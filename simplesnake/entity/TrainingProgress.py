from dataclasses import dataclass

from simplesnake.entity.GameState import GameState


@dataclass(frozen=True)
class TrainingProgress:
    # A snapshot carries results from the learning thread to the window.
    game: GameState
    games: int
    record: int
    mean: float
    # Present only for the terminal frame, so the UI appends each result once.
    completed_score: int | None = None
