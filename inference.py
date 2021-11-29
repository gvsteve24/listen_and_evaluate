import os
import torch
import torch.utils.data.dataloader

import nemo.collections.asr as nemo_asr
from dotenv import load_dotenv
from transformers import AutoTokenizer, AutoModel

from util.encoder import AudioEncoder
from dataclass import InferScore, BestItem

os.environ["CUDA_VISIBLE_DEVICES"] = "-1"


class SentenceBert:
    def __init__(self, model_url="sentence-transformers/msmarco-distilbert-dot-v5"):
        self.tokenizer = AutoTokenizer.from_pretrained(model_url)
        self.model = AutoModel.from_pretrained(model_url)

    #Mean Pooling - Take attention mask into account for correct averaging
    def mean_pooling(self, model_output, attention_mask):
        token_embeddings = model_output.last_hidden_state
        input_mask_expanded = attention_mask.unsqueeze(-1).expand(token_embeddings.size()).float()
        return torch.sum(token_embeddings * input_mask_expanded, 1) / torch.clamp(input_mask_expanded.sum(1), min=1e-9)

    def encode(self, texts):
        # Tokenize sentences / input type : [str] / str
        encoded_input = self.tokenizer(texts, padding=True, truncation=True, return_tensors='pt')

        # Compute token embeddings
        with torch.no_grad():
            model_output = self.model(**encoded_input, return_dict=True)

        # Perform pooling
        embeddings = self.mean_pooling(model_output, encoded_input['attention_mask'])

        return embeddings

    def score(self, docs, query_emb, doc_emb):
        # Compute dot score between query and all document embeddings
        scores = torch.mm(query_emb, doc_emb.transpose(0, 1))[0].cpu().tolist()

        # Combine docs & scores
        doc_score_pairs = list(zip(docs, scores))

        # Sort by decreasing score
        doc_score_pairs = sorted(doc_score_pairs, key=lambda x: x[1], reverse=True)
        doc_score_pairs = [InferScore(score, doc) for doc, score in doc_score_pairs]
        return doc_score_pairs


class Inferer:
    def __init__(self, input_bert: SentenceBert):
        self.sentence_bert = input_bert
        if torch.cuda.is_available():
            self.quartznet = nemo_asr.models.ASRModel.from_pretrained(model_name="QuartzNet15x5Base-En").cuda()
            # self.sentence_bert = SentenceTransformer('sentence-transformers/msmarco-distilbert-dot-v5')
        else:
            self.quartznet = nemo_asr.models.ASRModel.from_pretrained(model_name="QuartzNet15x5Base-En")
            # self.sentence_bert = SentenceTransformer('sentence-transformers/msmarco-distilbert-dot-v5')

    def speech_to_text(self, audio_path: str) -> str:
        enc_path = AudioEncoder.encode(audio_path)
        if AudioEncoder.validate_audio(enc_path):
            text = self.quartznet.transcribe([enc_path])
            return text[0]
        else:
            output_path = AudioEncoder.cut_in_length(enc_path, 60)
            text = self.quartznet.transcribe([output_path])
            return text[0]

    def calculate_score(self, query: str, ans: [BestItem]) -> [InferScore]:
        query_emb = self.sentence_bert.encode(query)
        docs = []
        doc_embs = []
        for item in ans:
            if item.embed is None:
                doc_emb = self.sentence_bert.encode(item.text)
                item.embed = doc_emb
                # TODO: save it to db
            docs.append(item.text)
            doc_embs.append(item.embed)

        result = self.sentence_bert.score(docs, query_emb, doc_embs)[0].cpu().tolist()

        return result


if __name__ == "__main__":
    file_path = '/home/junghyun/Downloads/interview.webm'
    load_dotenv()
    url = os.getenv('DATABASE_URL')
    # query embedding dim check
    # query type check
    # query insert check (handdling logic)

