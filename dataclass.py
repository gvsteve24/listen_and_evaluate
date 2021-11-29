from dataclasses import dataclass

import numpy as np


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


@dataclass
class BestItem:
    text: str
    embed: np.ndarray

    def __init__(self, text="", vector=None):
        self.text = text
        self.embed = vector