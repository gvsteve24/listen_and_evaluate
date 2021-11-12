from sqlalchemy import Column, Integer, String, ForeignKey, Float
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class Question(Base):
    __tablename__ = 'question'

    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False, unique=True)
    content = Column(String, nullable=False)


class InputFiles(Base):
    __tablename__ = 'input_files'

    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False, unique=True)
    path = Column(String, nullable=False)
    q_id = Column(Integer, ForeignKey("question.id"))


class Answer(Base):
    __tablename__ = 'answer'

    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False, unique=True)
    text = Column(String)
    score = Column(Float, default=0)
    q_id = Column(Integer, ForeignKey("question.id"))
