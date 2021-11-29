from inference import Inferer
from db_handler import DBHandler

from dataclass import InferScore

class TestTool:
    def __init__(self, db_handler: DBHandler, infer_tool: Inferer):
        self.db_handler = db_handler
        self.infer_tool = infer_tool

    def run_stt(self, path: str) -> [InferScore]:
        item = self.db_handler.retrieve_one_path(path)
        text_result = self.infer_tool.speech_to_text(item.path)
        return text_result

    def run_sentence_score(self, q_id: int, target_text: str) -> ([InferScore], bool):
        """
        :param q_id: question_id
        :param target_text: normal answer
        :return: InferScore dataclass with score and text, bool to provide flag whether to save result
        """
        input_id = self.db_handler.retrieve_input_from_answer(target_text)
        docs = self.db_handler.retrieve_suggested_answers(q_id=q_id, input_id=input_id)
        if not docs:
            result = self.db_handler.retrieve_score_and_best_by_input(input_id=input_id)
        else:
            # answers -> [BestItem]
            answers = self.db_handler.find_embedding_vector(docs)
            result = self.infer_tool.calculate_score(target_text, answers)
        return result, bool(docs)
