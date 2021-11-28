from dataclasses import dataclass


@dataclass
class PathResultItem:
    id: int
    path: str


@dataclass
class QuestionItem:
    id: int
    text: str


@dataclass
class InferScore:
    score: int
    text: str