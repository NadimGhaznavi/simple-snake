from dataclasses import dataclass

from simplesnake.constants.DGame import DDirection
from simplesnake.entity.Point import Point


@dataclass(frozen=True)
class GameState:
    # Type hints describe expected values; Python does not enforce them at runtime.
    # tuple[Point, ...] means any number of Points; Point | None allows missing food.
    # https://docs.python.org/3/library/typing.html
    columns: int
    rows: int
    snake: tuple[Point, ...]
    direction: DDirection
    food: Point | None
    score: int
    done: bool
    won: bool
