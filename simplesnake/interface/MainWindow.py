from pathlib import Path

from PySide6.QtCore import QStandardPaths, QTimer, Qt, Slot
from PySide6.QtGui import QKeySequence, QShortcut
from PySide6.QtWidgets import (
    QComboBox, QHBoxLayout, QLabel, QMainWindow, QMessageBox, QPushButton,
    QSpinBox, QSplitter, QVBoxLayout, QWidget,
)

from simplesnake.activity.SnakeGame import SnakeGame
from simplesnake.constants.DDisplay import DDisplay
from simplesnake.constants.DGame import DDirection, DMode
from simplesnake.constants.DSimpleSnake import DSimpleSnake
from simplesnake.constants.DText import DText
from simplesnake.interface.GameBoard import GameBoard
from simplesnake.interface.TrainingChart import TrainingChart
from simplesnake.interface.TrainingWorker import TrainingWorker


class MainWindow(QMainWindow):
    """Present game state and delegate each mode to its own small scheduler."""

    def __init__(self, text):
        super().__init__()
        self.text = text
        self.game = SnakeGame()
        self.pending_direction = self.game.direction
        self.worker = None
        self.running = False
        self.record = 0
        self.model_path = Path(QStandardPaths.writableLocation(
            QStandardPaths.StandardLocation.AppDataLocation)) / DSimpleSnake.MODEL_FILE
        self.setWindowTitle(text(DText.APP_TITLE))
        self.resize(DDisplay.WINDOW_WIDTH, DDisplay.WINDOW_HEIGHT)

        self.mode = QComboBox()
        self.mode.addItem(text(DText.HUMAN), DMode.HUMAN)
        self.mode.addItem(text(DText.TRAIN), DMode.TRAIN)
        self.toggle = QPushButton(text(DText.START))
        self.reset = QPushButton(text(DText.RESET))
        self.speed = QSpinBox()
        self.speed.setRange(DDisplay.MIN_SPEED, DDisplay.MAX_SPEED)
        self.speed.setValue(DDisplay.DEFAULT_SPEED)
        self.speed.setSuffix(text(DText.SPEED_UNIT))
        self.speed.setKeyboardTracking(False)
        controls = QHBoxLayout()
        controls.addWidget(QLabel(text(DText.MODE)))
        controls.addWidget(self.mode)
        controls.addWidget(self.toggle)
        controls.addWidget(self.reset)
        controls.addStretch()
        controls.addWidget(QLabel(text(DText.SPEED)))
        controls.addWidget(self.speed)

        self.stats = [QLabel() for _ in range(4)]
        stats = QHBoxLayout()
        for label in self.stats:
            stats.addWidget(label)
        self.board = GameBoard(self.game.snapshot())
        self.chart = TrainingChart(text)
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.addWidget(self.board)
        splitter.addWidget(self.chart)
        splitter.setSizes([640, 460])
        model_label = QLabel(text(DText.MODEL_PATH, path=str(self.model_path)))
        model_label.setTextFormat(Qt.TextFormat.PlainText)
        model_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        layout = QVBoxLayout()
        layout.addLayout(controls)
        layout.addLayout(stats)
        layout.addWidget(splitter, 1)
        layout.addWidget(model_label)
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self._human_step)
        self.toggle.clicked.connect(self._toggle)
        self.reset.clicked.connect(self._reset)
        self.mode.currentIndexChanged.connect(self._reset)
        self.speed.valueChanged.connect(self._change_speed)
        for keys, direction in (
            (("Up", "W"), DDirection.UP), (("Right", "D"), DDirection.RIGHT),
            (("Down", "S"), DDirection.DOWN), (("Left", "A"), DDirection.LEFT),
        ):
            for key in keys:
                shortcut = QShortcut(QKeySequence(key), self)
                shortcut.activated.connect(lambda d=direction: self._steer(d))
        shortcut = QShortcut(QKeySequence("Space"), self)
        shortcut.setAutoRepeat(False)
        shortcut.activated.connect(self._toggle)
        self._show_stats(0, 0, 0, 0)
        self.statusBar().showMessage(text(DText.READY))

    def _show_stats(self, score, games, record, mean):
        values = (
            self.text(DText.SCORE, score=score), self.text(DText.GAMES, games=games),
            self.text(DText.RECORD, record=record), self.text(DText.MEAN, mean=f"{mean:.2f}"),
        )
        for label, value in zip(self.stats, values):
            label.setText(value)

    def _toggle(self):
        if self.running:
            self.running = False
            self.timer.stop()
            if self.worker is not None:
                self.worker.set_paused(True)
            self.toggle.setText(self.text(DText.RESUME))
            self.statusBar().showMessage(self.text(DText.PAUSED))
            return
        if self.mode.currentData() == DMode.TRAIN:
            if self.worker is None:
                self.chart.reset()
                self._show_stats(0, 0, 0, 0)
                self.worker = TrainingWorker(self.model_path, self.speed.value(), self)
                self.worker.progress.connect(self._training_progress)
                self.worker.failed.connect(self._training_failed)
                self.worker.start()
            else:
                self.worker.set_paused(False)
            status = DText.TRAINING
        else:
            if self.game.done:
                self.game.reset()
                self.pending_direction = self.game.direction
                self.board.show_state(self.game.snapshot())
            self.timer.start(self._interval())
            status = DText.PLAYING
        self.running = True
        self.toggle.setText(self.text(DText.PAUSE))
        self.statusBar().showMessage(self.text(status))
        self.board.setFocus()

    def _interval(self):
        return max(1, round(DDisplay.MILLISECONDS_PER_SECOND / self.speed.value()))

    def _change_speed(self):
        self.timer.setInterval(self._interval())
        if self.worker is not None:
            self.worker.set_speed(self.speed.value())

    def _steer(self, direction):
        if self.running and self.mode.currentData() == DMode.HUMAN:
            if (direction - self.game.direction) % len(DDirection) != 2:
                self.pending_direction = direction

    def _human_step(self):
        result = self.game.step(self.game.steer(self.pending_direction), starvation=False)
        self.pending_direction = self.game.direction
        self.record = max(self.record, result.score)
        self.board.show_state(self.game.snapshot())
        self._show_stats(result.score, 0, self.record, 0)
        if result.done:
            self.timer.stop()
            self.running = False
            self.toggle.setText(self.text(DText.START))
            self.statusBar().showMessage(self.text(
                DText.WON if self.game.won else DText.GAME_OVER, score=result.score))

    @Slot(object)
    def _training_progress(self, progress):
        # A stopped worker may have already queued a final signal.
        if self.sender() is not self.worker:
            return
        self.board.show_state(progress.game)
        self._show_stats(progress.game.score, progress.games, progress.record, progress.mean)
        if progress.completed_score is not None:
            self.chart.append(progress.completed_score, progress.mean)

    def _stop_training(self):
        worker, self.worker = self.worker, None
        if worker is not None:
            worker.stop()
            # Cooperative shutdown completes at most the current local move or
            # replay batch; no forced termination of Python/PyTorch state.
            worker.wait()
            worker.deleteLater()

    @Slot(str)
    def _training_failed(self, error):
        if self.sender() is not self.worker:
            return
        self._stop_training()
        self.running = False
        self.toggle.setText(self.text(DText.START))
        message = self.text(DText.TRAINING_ERROR, error=error)
        self.statusBar().showMessage(message)
        QMessageBox.critical(self, self.text(DText.ERROR_TITLE), message)

    def _reset(self):
        self.timer.stop()
        self._stop_training()
        self.running = False
        self.record = 0
        self.game.reset()
        self.pending_direction = self.game.direction
        self.board.show_state(self.game.snapshot())
        self.chart.reset()
        self._show_stats(0, 0, 0, 0)
        self.toggle.setText(self.text(DText.START))
        self.statusBar().showMessage(self.text(DText.READY))

    def closeEvent(self, event):
        self.timer.stop()
        self._stop_training()
        event.accept()
