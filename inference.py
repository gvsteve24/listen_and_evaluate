from dataclasses import dataclass

from sentence_transformers import SentenceTransformer, util
import nemo.collections.asr as nemo_asr

from util.encoder import AudioEncoder


@dataclass
class InferScore:
    score: int
    text: str


class Inferer:
    def __init__(self):
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

    def calculate_score(self, query: str, docs: [str]) -> [InferScore]:
        query_emb = self.sentence_bert.encode(query)
        doc_emb = self.sentence_bert.encode(docs)

        scores = util.dot_score(query_emb, doc_emb)[0].cpu().tolist()

        doc_score_pairs = list(zip(docs, scores))
        doc_score_pairs = sorted(doc_score_pairs, key=lambda x: x[1], reverse=True)
        doc_score_pairs = [InferScore(score, doc) for doc, score in doc_score_pairs]

        return doc_score_pairs


if __name__ == "__main__":
    pass
    # file_path = '/home/junghyun/Downloads/interview.webm'
    # load_dotenv()
    # url = os.getenv('DATABASE_URL')
