from dataclasses import dataclass

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.sql.expression import func

from model import Question, InputFiles, Answer


@dataclass
class PathResultItem:
    id: int
    path: str


@dataclass
class QuestionItem:
    id: int
    content: str


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
                    .order_by(Question.content == question)
                    .first()
            )
        else:
            item = (
                session.query(Question)
                    .order_by(func.rand())
                    .first()
            )

        session.close()
        return QuestionItem(item.id, item.content)

    def save_one_path(self, path: str, q_id: int):
        session = self._connector.get_session()
        item = (
            session.query(InputFiles)
                .filter(InputFiles.path == path)
                .first()
        )
        if item is None:
            item = InputFiles(path=path, q_id=q_id)
            session.add(item)
        else:
            session.add(item)
        # session.expunge(item)
        session.commit()
        session.close()

    def retrieve_one_path(self, path) -> PathResultItem:
        session = self._connector.get_session()
        print(path)
        item = (
            session.query(InputFiles)
                .filter(InputFiles.path == path)
                .first()
        )
        session.close()
        return PathResultItem(item.id, item.path)

    def retrieve_path_by_question(self, question: str) -> [PathResultItem]:
        session = self._connector.get_session()
        result = []

        items = (
            session.query(InputFiles)
                .join(Question, Question.id == InputFiles.q_id)
                .filter(Question.content == question)
                .all()
        )

        for item in items:
            result.append(PathResultItem(item.id, item.path))
        session.close()
        return result

    def save_one_answer(self, q_id: int, text: str, path: str):
        session = self._connector.get_session()
        # getting input_id from q_id and text(?)
        item = (
            session.query(InputFiles)
                .filter(InputFiles.path == path)
                .first()
        )
        session.add(Answer(suggested=0, text=text, q_id=q_id, input_id=item.id))
        session.commit()
        session.close()

    def retrieve_suggested_answers(self, q_id: int) -> [str]:
        session = self._connector.get_session()
        items = (
            session.query(Answer.text)
                .filter(Answer.q_id == q_id)
                .where(Answer.suggested == 1)
                .all()
        )
        doc = [ans for row in items for ans in row]
        session.close()
        return doc



if __name__ == "__main__":
    # handler = DBHandler(url)
    # result = handler.retrieve_suggested_answers(q_id=22)
    pass