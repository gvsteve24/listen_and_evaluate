from dataclasses import dataclass

import torch
from sentence_transformers import SentenceTransformer, util
import nemo.collections.asr as nemo_asr

from util.encoder import AudioEncoder


@dataclass
class InferScore:
    score: int
    text: str


class Inferer:
    def __init__(self):
        if torch.cuda.is_available():
            self.gpu_available = True
            self.quartznet = nemo_asr.models.ASRModel.from_pretrained(model_name="QuartzNet15x5Base-En").cuda()
            self.sentence_bert = SentenceTransformer('sentence-transformers/msmarco-distilbert-dot-v5')

    def speech_to_text(self, audio_path: str) -> str:
        enc_path = AudioEncoder.encode(audio_path)
        if AudioEncoder.validate_audio(enc_path):
            text = self.quartznet.transcribe([enc_path])
            return text[0]
        else:
            output_path = AudioEncoder.cut_in_length(enc_path, 60)
            text = self.quartznet.transcribe([output_path])
            return text[0]

    def calculate_score(self, query: str, docs: [str]) -> [InferScore]:
        query_emb = self.sentence_bert.encode(query)
        doc_emb = self.sentence_bert.encode(docs)

        scores = util.dot_score(query_emb, doc_emb)[0].cpu().tolist()

        doc_score_pairs = list(zip(docs, scores))
        doc_score_pairs = sorted(doc_score_pairs, key=lambda x: x[1], reverse=True)
        doc_score_pairs = [InferScore(score, doc) for doc, score in doc_score_pairs]

        return doc_score_pairs


if __name__ == "__main__":
    file_path = '/home/junghyun/Downloads/engineer_interview_questions.mp4'

    docs = [
        # "hire everybody in welcam my name is jen and a macurcoach and indeed with over ten years of experience working in carer services over the years i've worked with hundreds of job seekers to help them prepare for their next interviews by showing them how to create compelling talking points that they can apply to answering a variety of different questions today i'm going to share a little bit of that advice with you in this video we'll discuss five common intervie questions for each will discuss what employers are really looking for in an answer and break down how to craft a really strong response you'll also get examples of answers along the way at the end of the video will also cover a tricky question that's very common to pop up in an interview room it's a tough ine so be sure to stick around to learn how you can answer it with confidence let's start with our first question why do you want to work here now interpiewers often asks us question to determine whether or not you're going to be a good fit for the role and the company your answer will demonstrate whether or not you did your homework if hou can speak well to why you would be a good match for the team",
        # "hire somebody wecome my name is jen and consulting coach in indeed with over five years of experience3 working in career service over the years  I've worked with hundreds of job seekers to help them prepare for their next interviews by showing them how to achieve appealing breakpoints what the variousl answers and questions can combine. Today Im going to share littel bit of advice with you and really kno what is the strong pointwise answer and and the along the way at the end of the video will also cover a tricky question that's very common to pop up in an interview room it's tough and so make sure to stick around to learn how you can answer confidently. Let's start our first example question. Why do you want to work here? Now interviewrs often asks us question to determine whether or not you're going to be a good fit for the role and the company your answer will demonstrate whether or not you did your assignment if you can speak well to why you would be a good match for the team.",
        "hire everybody in welcome my name is Jan and a microcoach in indeed with over ten years of experience working in career services over the years i've worked with hundreds of job seekers to help them prepare for their next interviews by showing them how to create compelling talking points that they can apply to answering a variety of different questions today i'm going to share a little bit of that advice with you in this video we'll discuss five common interview questions for each will discuss what employers are really looking for in an answer and break down how to craft a really strong response you'll also get examples of answers along the way at the end of the video will also cover a tricky question that's very common to pop up in an interview room it's a tough so be sure to stick around to learn how you can answer it with confidence let's start with our first question why do you want to work here now interviewers often asks us question to determine whether or not you're going to be a good fit for the role and the company your answer will demonstrate whether or not you did your homework if who can speak well to why you would be a good match for the team"]

    infertool = Inferer()
    transcription = infertool.speech_to_text(file_path)
    result = infertool.calculate_score(transcription, docs)

    for doc, score in result:
        print(score, ': ', doc)
