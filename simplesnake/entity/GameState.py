from dataclasses import dataclass

from simplesnake.constants.DGame import DDirection
from simplesnake.entity.Point import Point


@dataclass(frozen=True)
class GameState:
    columns: int
    rows: int
    snake: tuple[Point, ...]
    direction: DDirection
    food: Point | None
    score: int
    done: bool
    won: bool
