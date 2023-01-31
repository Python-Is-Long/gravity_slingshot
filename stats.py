# 2023-1-23
from dataclasses import dataclass


@dataclass
class GameStats():
    time_taken: float = 0
    moves: int = 0
    score: int = 0
