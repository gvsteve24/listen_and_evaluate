from dataclasses import dataclass

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.sql.expression import func

from inference import InferScore
from model import Question, InputFile, Answer, BestAnswer, Score


@dataclass
class PathResultItem:
    id: int
    path: str


@dataclass
class QuestionItem:
    id: int
    text: str


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
            item = (
                session.query(Question)
                    .order_by(Question.text == question)
                    .first()
            )
        else:
            item = (
                session.query(Question)
                    .order_by(func.rand())
                    .first()
            )

        session.close()
        return QuestionItem(item.id, item.text)

    def save_one_path(self, path: str, q_id: int):
        session = self._connector.get_session()
        item = (
            session.query(InputFile)
                .filter(InputFile.path == path)
                .first()
        )
        if item is None:
            item = InputFile(path=path, q_id=q_id)
            session.add(item)
        else:
            session.add(item)
        # session.expunge(item)
        session.commit()
        session.close()

    def retrieve_one_path(self, path) -> PathResultItem:
        session = self._connector.get_session()
        item = (
            session.query(InputFile)
                .filter(InputFile.path == path)
                .first()
        )
        session.close()
        return PathResultItem(item.id, item.path)

    def retrieve_input_from_answer(self, answer: str) -> int:
        """
        :param answer: speech to text inference result
        :return: row id from input_file on corresponding answer
        """
        session = self._connector.get_session()
        id = (
            session.query(Answer.input_id)
                .filter_by(text=answer)
                .first()
        )
        return id

    def retrieve_path_by_question(self, question: str) -> [PathResultItem]:
        session = self._connector.get_session()
        result = []

        items = (
            session.query(InputFile)
                .join(Question, Question.id == InputFile.q_id)
                .filter(Question.content == question)
                .all()
        )

        for item in items:
            result.append(PathResultItem(item.id, item.path))
        session.close()
        return result

    def save_one_answer(self, q_id: int, text: str, path: str):
        session = self._connector.get_session()
        item = (
            session.query(InputFile)
                .filter(InputFile.path == path)
                .first()
        )
        session.add(Answer(text=text, q_id=q_id, input_id=item.id))
        session.commit()
        session.close()

    def retrieve_best_answer_id(self, text: str) -> int:
        session = self._connector.get_session()
        item = (session.query(BestAnswer.id).filter_by(text=text).first())
        return item

    def retrieve_suggested_answers(self, q_id: int, input_id: int) -> [str]:
        session = self._connector.get_session()
        # based on input_id on score table, it can retrieve only docs that never participated inference
        items_to_exclude = (
            session.query(BestAnswer, Score, InputFile)
                .filter(Score.best_id == BestAnswer.id)
                .filter(Score.input_id == InputFile.id)
                .filter(Score.input_id == input_id)
                .all()
        )
        items = (
            session.query(BestAnswer.text)
                .filter(BestAnswer.q_id == q_id)
                .all()
        )
        if items_to_exclude:
            print("exclude items.")
            exit()
        docs = [txt for doc in items for txt in doc]
        session.close()
        return docs

    def save_score(self, query_answer: str, result: [InferScore]):
        session = self._connector.get_session()
        # iterate result
        # retrieve input_id from answer table
        for item in result:
            score = item.score
            text = item.text
            input_id = self.retrieve_input_from_answer(answer=query_answer)
            b_id = self.retrieve_best_answer_id(text)
            session.add(Score(score=score, input_id=input_id, best_id=b_id))
        session.commit()
        session.close()


if __name__ == "__main__":
    RDS_URL = 'mysql+mysqlconnector://junghyun:2514876ec2a231800915a25aa023a3b6ea81e17a2bf20b21c5bb618378f9f1db@ml-mario.cluster-custom-cxdgkesqfuwz.ap-northeast-2.rds.amazonaws.com/junghyun'
    handler = DBHandler(RDS_URL)
    doc = handler.retrieve_suggested_answers(q_id=15, input_id=4)
    # doc = handler.retrieve_input_from_answer(answer="when i first started myn internshep the onboarding process was inpari parl and initial training for developers left a lot to be desired after sharing my concerns with my trainir i was able to help develop better resources for new equobies as well as in structure and the programme entirely i feel like the show both my initiative and problem solving abilities")
    print(*doc)