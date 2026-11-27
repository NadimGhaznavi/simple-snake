import os
os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')

from pathlib import Path
import tempfile
from time import monotonic
import unittest
from unittest.mock import patch

from PySide6.QtCore import QEventLoop, QTimer, Qt
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication

from simplesnake.constants.DGame import DAction, DDirection
from simplesnake.interface.Localizer import Localizer
from simplesnake.interface.MainWindow import MainWindow
from simplesnake.interface.TrainingWorker import TrainingWorker


APP = QApplication.instance() or QApplication([])


def process_events(milliseconds):
    # A real Qt event loop releases the GIL while waiting, like app.exec().
    loop = QEventLoop()
    QTimer.singleShot(milliseconds, loop.quit)
    loop.exec()


def wait_until(predicate, timeout=10000):
    deadline = monotonic() + timeout / 1000
    while not predicate() and monotonic() < deadline:
        process_events(10)
    return predicate()


class QtTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        localizer = Localizer(Path(__file__).resolve().parents[1] / 'simplesnake/locales')
        self.window = MainWindow(localizer.text)
        self.window.model_path = Path(self.directory.name) / 'best.pth'
        self.window.show()
        APP.processEvents()

    def tearDown(self):
        self.window.close()
        APP.processEvents()
        self.directory.cleanup()

    def test_human_controls_pause_reversal_and_resize(self):
        self.window.speed.setValue(1)
        QTest.mouseClick(self.window.toggle, Qt.MouseButton.LeftButton)
        self.assertTrue(self.window.running)
        QTest.keyClick(self.window.board, Qt.Key.Key_Left)
        self.assertEqual(self.window.pending_direction, DDirection.RIGHT)
        QTest.keyClick(self.window.board, Qt.Key.Key_Up)
        self.window._human_step()
        self.assertEqual(self.window.game.direction, DDirection.UP)
        QTest.keyClick(self.window.board, Qt.Key.Key_Space)
        self.assertFalse(self.window.timer.isActive())
        self.assertFalse(self.window.running)
        QTest.keyClick(self.window.board, Qt.Key.Key_Space)
        self.assertTrue(self.window.timer.isActive())
        self.window.resize(900, 550)
        APP.processEvents()
        self.assertFalse(self.window.grab().isNull())

    def test_human_game_over_can_restart(self):
        self.window._toggle()
        self.window.timer.stop()
        while not self.window.game.done:
            self.window._human_step()
        self.assertFalse(self.window.running)
        self.window._toggle()
        self.assertTrue(self.window.running)
        self.assertFalse(self.window.game.done)

    @patch('simplesnake.activity.Agent.Agent.choose_action', return_value=DAction.STRAIGHT)
    def test_training_chart_pause_resume_reset_and_shutdown(self, choose_action):
        self.window.mode.setCurrentIndex(1)
        self.window.speed.setValue(120)
        self.window._toggle()
        self.assertTrue(wait_until(lambda: len(self.window.chart.scores) >= 1))
        worker = self.window.worker
        self.window._toggle()
        process_events(100)  # Drain the one move already in flight at pause.
        head = self.window.board.state
        process_events(100)
        self.assertEqual(self.window.board.state, head)
        self.window._toggle()
        self.assertTrue(self.window.running)
        self.window._toggle()  # Shutdown must also wake a paused worker.
        self.window._reset()
        self.assertFalse(worker.isRunning())
        self.assertIsNone(self.window.worker)
        APP.processEvents()
        self.assertEqual(self.window.chart.scores, [])
        self.assertEqual(self.window.board.state.score, 0)

    def test_mode_change_discards_old_worker_frames(self):
        self.window.mode.setCurrentIndex(1)
        self.window._toggle()
        worker = self.window.worker
        self.window.mode.setCurrentIndex(0)
        APP.processEvents()
        self.assertFalse(worker.isRunning())
        self.assertEqual(self.window.board.state, self.window.game.snapshot())
        self.assertFalse(self.window.running)

    def test_worker_errors_are_signalled_and_stop(self):
        messages = []
        worker = TrainingWorker(Path(self.directory.name) / 'model.pth', 40)
        worker.failed.connect(messages.append)
        with patch('simplesnake.interface.TrainingWorker.TrainingSession',
                   side_effect=OSError('test storage failure')):
            worker.start()
            self.assertTrue(wait_until(lambda: bool(messages)))
            self.assertTrue(worker.wait(2000))
        self.assertIn('test storage failure', messages[0])
