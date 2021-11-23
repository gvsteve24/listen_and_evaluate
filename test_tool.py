from dataclasses import dataclass

from inference import Inferer
from db_handler import DBHandler


@dataclass
class InferScore:
    score: int
    text: str


class TestTool:
    def __init__(self, db_handler: DBHandler, infer_tool: Inferer):
        self.db_handler = db_handler
        self.infer_tool = infer_tool

    def run_stt(self, path: str) -> [InferScore]:
        item = self.db_handler.retrieve_one_path(path)
        text_result = self.infer_tool.speech_to_text(item.path)
        return text_result

    def run_sentence_score(self, q_id: int, target_text: str):
        # input_id is available
        input_id = self.db_handler.retrieve_input_from_answer(target_text)
        docs = self.db_handler.retrieve_suggested_answers(q_id=q_id, input_id=input_id)
        result = self.infer_tool.calculate_score(target_text, docs)
        return result
