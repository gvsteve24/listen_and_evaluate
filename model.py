from sqlalchemy import Column, Integer, String, ForeignKey, Float, Boolean
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
    suggested = Column(Integer, default=0)
    text = Column(String)
    q_id = Column(Integer, ForeignKey("question.id"))
    input_id = Column(Integer, ForeignKey("input_files.id"))
