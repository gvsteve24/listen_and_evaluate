import os
import csv
from dataclasses import dataclass
from dotenv import load_dotenv

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.sql.expression import func, select

from model import Question, InputFiles, Answer


@dataclass
class PathResultItem:
    id: int
    path: str


@dataclass
class QuestionItem:
    id: int
    content: str


class DBHandler:
    def __init__(self, url):
        self._engine = create_engine(url)
        self._session = scoped_session(sessionmaker(bind=self._engine))

    def add_questions(self, csv_path: str):
        """
        :param csv_path: csv is provided for sample data
        :return: None
        """
        f = open(csv_path)
        reader = csv.reader(f)
        for i, question in reader:
            self._session.execute("INSERT INTO question (content) VALUES (:content)",
                                  {"content": question})
            print(f"Added {question} in question table.")
        self._session.commit()
        self._session.close()

    def add_answers(self, csv_path: str):
        """
        :param csv_path: csv is provided for sample data
        :return:
        """
        f = open(csv_path)
        reader = csv.reader(f)

        for i, suggested, answer in reader:
            self._session.execute("INSERT INTO answer (q_id, suggested, text) VALUES (:q_id, :suggested, :text)",
                                  {"q_id": int(i),
                                   "suggested": bool(suggested),
                                   "text": answer.strip('"')})
            print(f"{answer} is created on q_id: {int(i)}")
        self._session.commit()
        self._session.close()

    def retrieve_one_question(self, random: bool = False, question: str = None) -> QuestionItem:
        if not random:
            item = (
                self._session.query(Question)
                    .order_by(Question.content == question)
                    .first()
            )
        else:
            item = (
                self._session.query(Question)
                    .order_by(func.rand())
                    .first()
            )

        self._session.close()
        return QuestionItem(item.id, item.content)

    def save_one_path(self, path: str, q_id: int) -> int:
        item = (
            self._session.query(InputFiles)
                .filter(InputFiles.path == path)
                .first()
        )
        if item is None:
            item = InputFiles(path=path, q_id=q_id)
            self._session.add(item)
        else:
            self._session.add(item)
        self._session.expunge(item)
        self._session.commit()
        self._session.close()
        return item.id

    def retrieve_one_path(self, path) -> PathResultItem:
        print(path)
        item = (
            self._session.query(InputFiles)
                .filter(InputFiles.path == path)
                .first()
        )
        self._session.close()
        return PathResultItem(item.id, item.path)

    def retrieve_path_by_question(self, question: str) -> [PathResultItem]:
        result = []

        items = (
            self._session.query(InputFiles)
                .join(Question, Question.id == InputFiles.q_id)
                .filter(Question.content == question)
                .all()
        )

        for item in items:
            result.append(PathResultItem(item.id, item.path))
        self._session.close()
        return result

    def save_one_answer(self, q_id: int, text: str, input_id: int):
        self._session.add(Answer(suggested=0, text=text, q_id=q_id, input_id=input_id))
        self._session.commit()
        self._session.close()

    def retrieve_suggested_answers(self, q_id: int) -> [str]:
        items = (
            self._session.query(Answer.text)
                .filter(Answer.q_id == q_id)
                .where(Answer.suggested == 1)
                .all()
        )
        doc = [ans for row in items for ans in row]
        return doc



if __name__ == "__main__":
    # load_dotenv()
    # url = os.getenv('DATABASE_URL')
    # handler = DBHandler(url)
    # result = handler.retrieve_suggested_answers(q_id=22)
    pass