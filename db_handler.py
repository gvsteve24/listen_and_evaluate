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
        # def retrieve_one_question(self, question: str) -> QuestionItem:
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

    def save_one_path(self, path):
        files = (
            self._session.query(InputFiles)
                .filter(InputFiles.path == path)
                .first()
        )
        if files is None:
            files = InputFiles(path=path)
            self._session.add(files)
        self._session.add(files)
        self._session.commit()
        self._session.close()

    def retrieve_one_path(self, path) -> PathResultItem:
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

    def save_transcript(self, q_id: int, text: str):
        item = (
            self._session.query(Answer)
                .filter(Answer.q_id == q_id)
                .first()
        )
        if not item:
            self._session.add(Answer(q_id=q_id, text=text))
        else:
            self._session.execute("UPDATE answer SET text = (:text) where q_id =(:q_id)", {"text": text, "q_id": q_id})
            print("Answer stt has been updated.")

        self._session.commit()
        self._session.close()

    def add_answer_content(self, q_id: int, score: int):
        """
        TO-DO: save score to existing row or newly save
        """
        item = (
            self._session.query(Answer)
                .filter(Answer.q_id == q_id)
                .first()
        )
        if not item:
            self._session.add(Answer(q_id=q_id, score=score))
        else:
            self._session.execute("UPDATE answer SET score = (:score) where q_id =(:q_id)", {"score": score, "q_id": q_id})
            print("Answer score has been updated.")

        self._session.commit()
        self._session.close()


if __name__ == "__main__":
    load_dotenv()
    url = os.getenv('DATABASE_URL')
    handler = DBHandler(url)
    result = handler.retrieve_one_question(random=True)
    print(result.id, result.content)
    # handler.add_questions(csv_path='sample/questions_developer_chegg_out.csv')
    # handler.add_answers(csv_path='sample/answers_developer_chegg_out.csv')
    # print(*handler.retrieve_path_by_question('q1'), sep='\n')
    # item = handler.retrieve_one_path('/home/junghyun/hdd/Fox News/CNN drops Rick Santorum fails to punish Chris Cuomo.3gpp')
    # print(item.id)