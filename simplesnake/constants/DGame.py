from enum import IntEnum, StrEnum
from typing import Final


# IntEnum gives readable names to numbers while supporting direction arithmetic.
# https://docs.python.org/3/library/enum.html#enum.IntEnum
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
    # StrEnum members also behave as strings, useful for stable UI option values.
    HUMAN = "human"
    TRAIN = "train"


class DGame:
    # Final marks constants for type checkers; it does not lock values at runtime.
    # https://docs.python.org/3/library/typing.html#typing.Final
    COLUMNS: Final[int] = 32
    ROWS: Final[int] = 24
    INITIAL_LENGTH: Final[int] = 3
    FOOD_REWARD: Final[int] = 10
    DEATH_REWARD: Final[int] = -10
    STEP_REWARD: Final[int] = 0
    STARVATION_FACTOR: Final[int] = 100
    # Match DDirection's order; screen y increases downward.
    OFFSETS: Final[tuple] = ((1, 0), (0, 1), (-1, 0), (0, -1))
