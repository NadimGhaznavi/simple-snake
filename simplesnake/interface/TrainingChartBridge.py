from PySide6.QtCore import QObject, Signal, Slot


class TrainingChartBridge(QObject):
    """Receive completion and failure notifications from the local chart page."""

    ready = Signal()
    failed = Signal(str)

    @Slot()
    def rendered(self):
        self.ready.emit()

    @Slot(str)
    def render_failed(self, message):
        self.failed.emit(message)
