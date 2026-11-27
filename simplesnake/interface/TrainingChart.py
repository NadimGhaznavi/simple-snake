import json
from pathlib import Path

from PySide6.QtCore import QTimer, QUrl, Qt
from PySide6.QtWebChannel import QWebChannel
from PySide6.QtWebEngineCore import QWebEngineSettings
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget

from simplesnake.constants.DChart import DChart
from simplesnake.constants.DText import DText
from simplesnake.interface.TrainingChartBridge import TrainingChartBridge


class TrainingChart(QWidget):
    """An offline Plotly chart, updated only when a training game completes."""

    def __init__(self, text, parent=None):
        super().__init__(parent)
        self.text = text
        self.scores = []
        self.means = []
        self.ready = False
        self.error = None
        self._revision = 0
        assets = Path(__file__).resolve().parents[1] / DChart.ASSET_DIRECTORY
        for name in (DChart.PAGE_FILE, DChart.SCRIPT_FILE, DChart.PLOTLY_FILE):
            if not (assets / name).is_file():
                raise FileNotFoundError(assets / name)

        self.status = QLabel(text(DText.CHART_LOADING))
        self.status.setTextFormat(Qt.TextFormat.PlainText)
        self.status.setWordWrap(True)
        self.view = QWebEngineView(self)
        self.view.settings().setAttribute(
            QWebEngineSettings.WebAttribute.LocalContentCanAccessRemoteUrls, False)
        self.bridge = TrainingChartBridge(self)
        self.bridge.ready.connect(self._rendered)
        self.bridge.failed.connect(self._failed)
        self.channel = QWebChannel(self.view.page())
        self.channel.registerObject("chart", self.bridge)
        self.view.page().setWebChannel(self.channel)
        self.view.loadFinished.connect(self._loaded)
        self.view.renderProcessTerminated.connect(
            lambda status, code: self._failed(f"{status.name} ({code})"))
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.status)
        layout.addWidget(self.view, 1)
        self._load_timer = QTimer(self)
        self._load_timer.setSingleShot(True)
        self._load_timer.timeout.connect(
            lambda: self._failed(text(DText.CHART_TIMEOUT)))
        self._load_timer.start(DChart.READY_TIMEOUT_MS)
        self.view.load(QUrl.fromLocalFile(str(assets / DChart.PAGE_FILE)))

    def _loaded(self, success):
        if not success:
            self._failed(self.text(DText.CHART_LOAD_FAILED))
            return
        labels = {
            "title": self.text(DText.CHART_TITLE),
            "games": self.text(DText.CHART_GAMES),
            "score": self.text(DText.CHART_SCORE),
            "mean": self.text(DText.CHART_MEAN),
        }
        self._run("initialize", labels, DChart.PLOTLY_VERSION)

    def _rendered(self):
        if self.error is not None:
            return
        self._load_timer.stop()
        self.ready = True
        self.status.hide()
        # Games may finish before the browser has loaded. Send the current
        # session once, then append each subsequent completed game.
        self._run("replace", self.scores, self.means, self._revision)

    def _failed(self, message):
        self._load_timer.stop()
        self.ready = False
        self.error = message
        self.view.hide()
        self.status.setText(self.text(DText.CHART_ERROR, error=message))
        self.status.show()

    def reset(self):
        self.scores.clear()
        self.means.clear()
        self._revision += 1
        if self.ready:
            self._run("replace", self.scores, self.means, self._revision)

    def append(self, score, mean):
        self.scores.append(score)
        self.means.append(mean)
        if self.ready:
            self._run("append", score, mean)

    def _run(self, method, *arguments):
        values = ",".join(json.dumps(value, allow_nan=False) for value in arguments)
        self.view.page().runJavaScript(f"trainingChart.{method}({values})")
