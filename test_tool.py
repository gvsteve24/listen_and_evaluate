import numpy as np

from inference import Inferer
from db_handler import DBHandler

from dataclass import InferScore

class TestTool:
    def __init__(self, db_handler: DBHandler, infer_tool: Inferer):
        self.db_handler = db_handler
        self.infer_tool = infer_tool

    def run_stt(self, path: str) -> [InferScore]:
        text_result = self.infer_tool.speech_to_text(path)
        return text_result

    def run_sentence_score(self, target_text: str, doc: [str], embedding: np.ndarray) -> [InferScore]:
        """
        :param doc:
        :param target_text: query text
        :param embedding: best_answer embedding vector
        :return: InferScore dataclass with score and text, bool to provide flag whether to save result
        """
        result = self.infer_tool.calculate_score(query=target_text, docs=doc, doc_emb=embedding)
        return result
