from sqlalchemy import Column, Integer, String, ForeignKey, Float, Boolean, LargeBinary
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class Question(Base):
    __tablename__ = 'question'

    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False, unique=True)
    text = Column(String, nullable=False)
    job_type = Column(Integer, nullable=True)
    user_id = Column(Integer, nullable=True)


class InputFile(Base):
    __tablename__ = 'input_file'

    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False, unique=True)
    path = Column(String, nullable=False)
    q_id = Column(Integer, ForeignKey("question.id"))
    user_id = Column(Integer, nullable=True)


class Answer(Base):
    __tablename__ = 'answer'

    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False, unique=True)
    text = Column(String)
    q_id = Column(Integer, ForeignKey("question.id"), nullable=True)
    input_id = Column(Integer, ForeignKey("input_file.id"), nullable=False)


class BestAnswer(Base):
    __tablename__ = 'best_answer'

    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False, unique=True)
    text = Column(String)
    q_id = Column(Integer, ForeignKey("question.id"), nullable=True)
    vector = Column(String, nullable=True)
    score = relationship("Score", back_populates="best_answer")


class Score(Base):
    __tablename__ = 'score'

    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False, unique=True)
    score = Column(Float, nullable=False)
    input_id = Column(Integer, ForeignKey("input_file.id"), nullable=False)
    best_id = Column(Integer, ForeignKey("best_answer.id"), nullable=False)
    best_answer = relationship("BestAnswer", back_populates="score")