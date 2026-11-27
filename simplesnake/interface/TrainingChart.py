from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure

from simplesnake.constants.DDisplay import DDisplay
from simplesnake.constants.DText import DText


class TrainingChart(FigureCanvasQTAgg):
    """One embedded figure, updated only when a training game completes."""

    def __init__(self, text, parent=None):
        figure = Figure(figsize=(4, 4), dpi=DDisplay.CHART_DPI, layout="constrained")
        super().__init__(figure)
        self.setParent(parent)
        self.axes = figure.add_subplot()
        self.axes.set_title(text(DText.CHART_TITLE))
        self.axes.set_xlabel(text(DText.CHART_GAMES))
        self.axes.set_ylabel(text(DText.CHART_SCORE))
        self.score_line, = self.axes.plot([], [], label=text(DText.CHART_SCORE), alpha=0.6)
        self.mean_line, = self.axes.plot([], [], label=text(DText.CHART_MEAN), linewidth=2)
        self.axes.legend(loc="upper left")
        self.axes.grid(alpha=0.2)
        self.scores = []
        self.means = []
        self.reset()

    def reset(self):
        self.scores.clear()
        self.means.clear()
        self._redraw()

    def append(self, score, mean):
        self.scores.append(score)
        self.means.append(mean)
        self._redraw()

    def _redraw(self):
        games = range(1, len(self.scores) + 1)
        self.score_line.set_data(games, self.scores)
        self.mean_line.set_data(games, self.means)
        self.axes.relim()
        self.axes.autoscale_view()
        self.axes.set_xlim(0, max(1, len(self.scores)))
        self.axes.set_ylim(bottom=0, top=max(1, max(self.scores, default=0) * 1.1))
        self.draw_idle()
