from PySide6.QtCore import QRectF, QSize, Qt
from PySide6.QtGui import QColor, QPainter
from PySide6.QtWidgets import QWidget

from simplesnake.constants.DDisplay import DDisplay


class GameBoard(QWidget):
    """Paint an immutable game snapshot, scaled to the available space."""

    def __init__(self, state, parent=None):
        super().__init__(parent)
        self.state = state
        self.setMinimumSize(DDisplay.BOARD_MIN_WIDTH, DDisplay.BOARD_MIN_HEIGHT)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

    def sizeHint(self):
        return QSize(640, 480)

    def show_state(self, state):
        self.state = state
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.fillRect(self.rect(), QColor(DDisplay.BACKGROUND))
        state = self.state
        cell = min(self.width() / state.columns, self.height() / state.rows)
        left = (self.width() - state.columns * cell) / 2
        top = (self.height() - state.rows * cell) / 2
        inset = cell * DDisplay.CELL_INSET

        def draw_cell(point, color):
            painter.fillRect(QRectF(left + point.x * cell + inset,
                                    top + point.y * cell + inset,
                                    cell - 2 * inset, cell - 2 * inset), QColor(color))

        if state.food is not None:
            draw_cell(state.food, DDisplay.FOOD)
        for point in state.snake[1:]:
            draw_cell(point, DDisplay.SNAKE)
        draw_cell(state.snake[0], DDisplay.HEAD)
