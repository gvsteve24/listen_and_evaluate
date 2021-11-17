import os
from dataclasses import dataclass

import torch
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer, util
import nemo.collections.asr as nemo_asr

from db_handler import DBHandler
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
    file_path = '/home/junghyun/Downloads/interview.webm'
    load_dotenv()
    url = os.getenv('DATABASE_URL')
    handler = DBHandler(url)
    doc = handler.retrieve_suggested_answers(q_id=22)
    infertool = Inferer()
    transcription = infertool.speech_to_text(file_path)
    result = infertool.calculate_score(transcription, doc)

    # print(result)
    for obj in result:
        print(obj.score, ', when compare to the answer "', obj.text, '"')
