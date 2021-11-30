import json
import ast
import time
from collections.abc import Iterable

import numpy as np
from sqlalchemy import create_engine
from sqlalchemy.pool import NullPool
from sqlalchemy.orm import sessionmaker, contains_eager
from sqlalchemy.sql.expression import func

from model import Question, InputFile, Answer, BestAnswer, Score
from dataclass import PathResultItem, QuestionItem, InferScore


# session time checker
def timeis(func):
    def wrap(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        print(func.__name__, "took ", end-start, "ms.")
        return result
    return wrap


class DBHandler:
    def __init__(self, url: str):
        self._engine = create_engine(url, poolclass=NullPool)
        self._Session = sessionmaker(bind=self._engine)

    @timeis
    def retrieve_one_question(self, random: bool = False, question: str = None) -> QuestionItem:
        session = self._Session()
        if not random:
            item = session.query(Question) \
                .order_by(Question.text == question) \
                .first()
        else:
            item = session.query(Question) \
                .order_by(func.rand()) \
                .first()

        session.close()
        return QuestionItem(item.id, item.text)

    @timeis
    def save_one_path(self, path: str, q_id: int):
        session = self._Session()
        item = session.query(InputFile) \
            .filter(InputFile.path == path) \
            .first()
        if item is None:
            item = InputFile(path=path, q_id=q_id)
            session.add(item)
        session.commit()
        session.close()

    @timeis
    def retrieve_one_path(self, path) -> PathResultItem:
        session = self._Session()
        item = session.query(InputFile) \
            .filter(InputFile.path == path) \
            .first()
        session.close()
        return PathResultItem(item.id, item.path)

    @timeis
    def retrieve_input_from_answer(self, answer: str) -> int:
        """
        :param answer: speech to text inference result
        :return: row id from input_file on corresponding answer
        """
        session = self._Session()
        id = session.query(Answer.input_id) \
            .filter_by(text=answer) \
            .first()
        session.close()
        return id[0]

    @timeis
    def retrieve_path_by_question(self, question: str) -> [PathResultItem]:
        session = self._Session()
        result = []

        items = session.query(InputFile) \
            .join(Question, Question.id == InputFile.q_id) \
            .filter(Question.content == question) \
            .all()

        for item in items:
            result.append(PathResultItem(item.id, item.path))
        session.close()
        return result

    @timeis
    def save_one_answer(self, q_id: int, text: str, path: str):
        session = self._Session()
        item = session.query(InputFile) \
            .filter(InputFile.path == path) \
            .first()
        session.add(Answer(text=text, q_id=q_id, input_id=item.id))
        session.commit()
        session.close()

    @timeis
    def retrieve_best_answer_id(self, text: str) -> int:
        session = self._Session()
        item = (session.query(BestAnswer.id).filter_by(text=text).first())
        session.close()
        return item[0]

    @timeis
    def retrieve_suggested_answers(self, q_id: int, input_id: int) -> [str]:
        session = self._Session()
        # based on input_id on score table, it can retrieve only docs that never participated inference
        subq1 = session.query(Score.best_id) \
            .filter(Score.input_id == input_id) \
            .subquery()

        items = session.query(BestAnswer) \
            .filter(BestAnswer.q_id == q_id) \
            .filter(BestAnswer.id.not_in(subq1)) \
            .all()

        docs = []
        for doc in items:
            if not isinstance(doc, Iterable):
                docs.append(doc.text)
            else:
                print("it's iterable.")
                docs.extend([txt for txt in doc])
        session.close()
        return docs

    @timeis
    def save_score(self, query_answer: str, result: [InferScore]):
        session = self._Session()
        # iterate result
        # retrieve input_id from answer table
        for item in result:
            score = item.score
            text = item.text if hasattr(item, "text") else item.best_answer.text
            input_id = self.retrieve_input_from_answer(answer=query_answer)
            b_id = self.retrieve_best_answer_id(text)
            session.add(Score(score=score, input_id=input_id, best_id=b_id))
        session.commit()
        session.close()

    @timeis
    def retrieve_score_and_best_by_input(self, input_id: int):
        # score: best_answer = N : 1
        session = self._Session()
        score = session.query(Score) \
            .join(Score.best_answer) \
            .filter(Score.input_id == input_id) \
            .options(contains_eager(Score.best_answer)) \
            .all()

        session.close()
        return [InferScore(s.score, s.best_answer.text) for s in score]

    @timeis
    def retrieve_best_answer_vector(self, docs: [str]) -> [np.ndarray]:
        v_list = []
        session = self._Session()
        for doc in docs:
            item = session.query(BestAnswer.vector) \
                .filter(BestAnswer.text == doc) \
                .first()
            v_list.append(ast.literal_eval(item[0]))
        session.close()
        return np.array(v_list, dtype=float)

    @timeis
    def save_vectors(self, doc, vec):
        session = self._Session()
        vecs = []
        for d, e in zip(doc, vec):
            ba = session.query(BestAnswer) \
                .filter_by(text=d) \
                .first()
            ba.vector = json.dumps(e.tolist())
            vecs.append(e)
            session.commit()
        session.close()
        return vecs


if __name__ == "__main__":
    pass