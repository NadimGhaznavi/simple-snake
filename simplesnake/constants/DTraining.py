from typing import Final


class DTraining:
    INPUT_SIZE: Final[int] = 11
    HIDDEN_SIZE: Final[int] = 256
    ACTION_COUNT: Final[int] = 3
    MEMORY_SIZE: Final[int] = 100_000
    BATCH_SIZE: Final[int] = 1000
    LEARNING_RATE: Final[float] = 0.001
    DISCOUNT: Final[float] = 0.9
    EXPLORATION_GAMES: Final[int] = 80
    EXPLORATION_RANGE: Final[int] = 200
    CPU_THREADS: Final[int] = 1
