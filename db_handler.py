import os
from collections.abc import Iterable

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session, contains_eager
from sqlalchemy.sql.expression import func

from model import Question, InputFile, Answer, BestAnswer, Score, BestEmbed
from dataclass import PathResultItem, QuestionItem, InferScore, BestItem


class DBConnectionHandler:
    def __init__(self, url):
        self._engine = create_engine(url)
        self._Session = sessionmaker(bind=self._engine)

    def get_session(self) -> Session:
        return self._Session()


class DBHandler:
    def __init__(self, url: str):
        self._connector = DBConnectionHandler(url)
        self._session = None

    def retrieve_one_question(self, random: bool = False, question: str = None) -> QuestionItem:
        session = self._connector.get_session()
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

    def save_one_path(self, path: str, q_id: int):
        session = self._connector.get_session()
        item = session.query(InputFile) \
            .filter(InputFile.path == path) \
            .first()
        if item is None:
            item = InputFile(path=path, q_id=q_id)
            session.add(item)
        session.commit()
        session.close()

    def retrieve_one_path(self, path) -> PathResultItem:
        session = self._connector.get_session()
        item = session.query(InputFile) \
            .filter(InputFile.path == path) \
            .first()
        session.close()
        return PathResultItem(item.id, item.path)

    def retrieve_input_from_answer(self, answer: str) -> int:
        """
        :param answer: speech to text inference result
        :return: row id from input_file on corresponding answer
        """
        session = self._connector.get_session()
        id = session.query(Answer.input_id) \
            .filter_by(text=answer) \
            .first()
        return id[0]

    def retrieve_path_by_question(self, question: str) -> [PathResultItem]:
        session = self._connector.get_session()
        result = []

        items = session.query(InputFile) \
            .join(Question, Question.id == InputFile.q_id) \
            .filter(Question.content == question) \
            .all()

        for item in items:
            result.append(PathResultItem(item.id, item.path))
        session.close()
        return result

    def save_one_answer(self, q_id: int, text: str, path: str):
        session = self._connector.get_session()
        item = session.query(InputFile) \
            .filter(InputFile.path == path) \
            .first()
        session.add(Answer(text=text, q_id=q_id, input_id=item.id))
        session.commit()
        session.close()

    def retrieve_best_answer_id(self, text: str) -> int:
        session = self._connector.get_session()
        item = (session.query(BestAnswer.id).filter_by(text=text).first())
        return item[0]

    def retrieve_suggested_answers(self, q_id: int, input_id: int) -> [str]:
        session = self._connector.get_session()
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

    def save_score(self, query_answer: str, result: [InferScore]):
        session = self._connector.get_session()
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

    def retrieve_score_and_best_by_input(self, input_id: int):
        # score: best_answer = N : 1
        session = self._connector.get_session()
        score = session.query(Score) \
            .join(Score.best_answer) \
            .filter(Score.input_id == input_id) \
            .options(contains_eager(Score.best_answer)) \
            .all()

        session.close()
        return [InferScore(s.score, s.best_answer.text) for s in score]

    def find_embedding_vector(self, docs:[str]) -> [BestItem]:
        # best_answer : vector = 1 : 1 (upsert)
        session = self._connector.get_session()
        results = []
        for doc in docs:
            best = BestItem()
            item = session.query(BestEmbed) \
                .join(BestEmbed.best_answer) \
                .filter(BestAnswer.text == doc) \
                .first()
            if item:
                best.embed = item.embed # needs to be transform
            else:
                best.text = doc
            results.append(best)
        session.close()
        return results

if __name__ == "__main__":
    RDS_URL = os.environ.get("RDS_URL")
    handler = DBHandler(RDS_URL)
    score = handler.retrieve_score_and_best_by_input(input_id=5)
    for elem in score:
        print(elem.score, elem.best_answer.text)
    # doc = handler.retrieve_suggested_answers(q_id=3, input_id=5)
    # doc = handler.retrieve_input_from_answer(answer="when i first started myn internshep the onboarding process was inpari parl and initial training for developers left a lot to be desired after sharing my concerns with my trainir i was able to help develop better resources for new equobies as well as in structure and the programme entirely i feel like the show both my initiative and problem solving abilities")
    # print(doc)