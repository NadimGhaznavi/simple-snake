from enum import IntEnum, StrEnum
from typing import Final


class DAction(IntEnum):
    STRAIGHT = 0
    RIGHT = 1
    LEFT = 2


class DDirection(IntEnum):
    # Clockwise order makes relative turns independent of screen coordinates.
    RIGHT = 0
    DOWN = 1
    LEFT = 2
    UP = 3


class DMode(StrEnum):
    HUMAN = "human"
    TRAIN = "train"


class DGame:
    COLUMNS: Final[int] = 32
    ROWS: Final[int] = 24
    INITIAL_LENGTH: Final[int] = 3
    FOOD_REWARD: Final[int] = 10
    DEATH_REWARD: Final[int] = -10
    STEP_REWARD: Final[int] = 0
    STARVATION_FACTOR: Final[int] = 100
    OFFSETS: Final[tuple] = ((1, 0), (0, 1), (-1, 0), (0, -1))
