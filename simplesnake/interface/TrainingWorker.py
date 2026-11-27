from threading import Condition
from time import monotonic

from PySide6.QtCore import QThread, Signal

from simplesnake.activity.TrainingSession import TrainingSession


class TrainingWorker(QThread):
    """Own all learning state in one thread; send immutable values to the UI.

    The condition protects only scheduling flags. Widgets never touch the
    session or model. Stop wakes a paused worker and finishes its current step.
    """

    progress = Signal(object)
    failed = Signal(str)

    def __init__(self, model_path, speed, parent=None):
        super().__init__(parent)
        self.model_path = model_path
        self._speed = speed
        self._paused = False
        self._stopping = False
        self._condition = Condition()

    def set_paused(self, paused):
        # with acquires the condition's lock and releases it even if an error occurs.
        # https://docs.python.org/3/library/threading.html#condition-objects
        with self._condition:
            self._paused = paused
            self._condition.notify_all()

    def set_speed(self, speed):
        with self._condition:
            self._speed = speed
            self._condition.notify_all()

    def stop(self):
        with self._condition:
            self._stopping = True
            self._condition.notify_all()

    def run(self):
        try:
            session = TrainingSession(self.model_path)
            while True:
                with self._condition:
                    # wait releases the lock while asleep; recheck flags on each wakeup.
                    while self._paused and not self._stopping:
                        self._condition.wait()
                    if self._stopping:
                        return
                    interval = 1 / self._speed
                # A monotonic clock measures elapsed time even if the wall clock changes.
                # https://docs.python.org/3/library/time.html#time.monotonic
                started = monotonic()
                self.progress.emit(session.step())
                with self._condition:
                    if not self._stopping:
                        # Subtract learning time; notifications can interrupt this delay.
                        self._condition.wait(timeout=max(0, interval - (monotonic() - started)))
        except Exception as error:
            # The thread boundary reports failures to the window and stops.
            # Continuing here would display a training run that is not running.
            self.failed.emit(f"{type(error).__name__}: {error}")
