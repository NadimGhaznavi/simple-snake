from typing import Final


class DDisplay:
    WINDOW_WIDTH: Final[int] = 1120
    WINDOW_HEIGHT: Final[int] = 650
    BOARD_MIN_WIDTH: Final[int] = 320
    BOARD_MIN_HEIGHT: Final[int] = 240
    DEFAULT_SPEED: Final[int] = 40
    MIN_SPEED: Final[int] = 1
    MAX_SPEED: Final[int] = 120
    MILLISECONDS_PER_SECOND: Final[int] = 1000
    BACKGROUND: Final[str] = "#141c26"
    SNAKE: Final[str] = "#4096dc"
    HEAD: Final[str] = "#7cc6ff"
    FOOD: Final[str] = "#ed6565"
    CELL_INSET: Final[float] = 0.08
    CHART_DPI: Final[int] = 100
