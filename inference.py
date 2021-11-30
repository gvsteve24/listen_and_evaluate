import os

import numpy as np
import torch
import torch.utils.data.dataloader

import nemo.collections.asr as nemo_asr
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer, util

from db_handler import DBHandler
from util.encoder import AudioEncoder
from dataclass import InferScore

os.environ["CUDA_VISIBLE_DEVICES"] = "-1"


class Inferer:
    def __init__(self):
        if torch.cuda.is_available():
            self.quartznet = nemo_asr.models.ASRModel.from_pretrained(model_name="QuartzNet15x5Base-En").cuda()
        else:
            self.quartznet = nemo_asr.models.ASRModel.from_pretrained(model_name="QuartzNet15x5Base-En")
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

    def calculate_score(self, query: str, docs: [str], doc_emb: [np.ndarray]) -> [InferScore]:
        query_emb = self.sentence_bert.encode(query)
        if any(elem is None for elem in doc_emb):
            doc_emb = self.sentence_bert.encode(doc_emb)
        else:
            doc_emb = torch.tensor(doc_emb).float()

        scores = util.dot_score(query_emb, doc_emb)[0].cpu().tolist()
        doc_score_pairs = list(zip(docs, scores))
        doc_score_pairs = sorted(doc_score_pairs, key=lambda x: x[1], reverse=True)
        doc_score_pairs = [InferScore(score, doc) for doc, score in doc_score_pairs]
        return doc_score_pairs


if __name__ == "__main__":
    file_path = '/home/junghyun/Downloads/interview.webm'
    load_dotenv()
    url = os.getenv('DATABASE_URL')
    # query embedding dim check
    # query type check
    # query insert check (handdling logic)

