from PySide6.QtCore import QObject, Signal, Slot


class TrainingChartBridge(QObject):
    """Receive completion and failure notifications from the local chart page."""

    ready = Signal()
    failed = Signal(str)

    @Slot()
    def rendered(self):
        # JavaScript calls this slot; the signal notifies the Python chart widget.
        self.ready.emit()

    @Slot(str)
    def render_failed(self, message):
        self.failed.emit(message)
