/* Application-owned Plotly presentation. Training statistics come from Python. */
(() => {
  "use strict";
  const channel = new Promise(resolve => {
    new QWebChannel(qt.webChannelTransport, value => resolve(value.objects.chart));
  });
  const chart = () => document.getElementById("chart");
  const escape = value => value.replace(/[&<>]/g, character => ({
    "&": "&amp;", "<": "&lt;", ">": "&gt;"
  })[character]);
  let labels;
  let pending = Promise.resolve();
  let failed = false;

  // Serialize browser operations so a reset cannot be overtaken by an older
  // append or a render still in flight.
  function enqueue(operation) {
    pending = pending.then(() => failed ? undefined : operation()).catch(error => {
      failed = true;
      return channel.then(bridge => bridge.render_failed(String(error)));
    });
  }

  function traces(scores, means) {
    const games = scores.map((_, index) => index + 1);
    return [
      {type: "scatter", mode: "lines", x: games, y: scores,
        name: labels.score, line: {color: "#4096dc", width: 1}, opacity: 0.6},
      {type: "scatter", mode: "lines", x: games, y: means,
        name: labels.mean, line: {color: "#edb965", width: 2}}
    ];
  }

  function layout(revision) {
    return {
      title: {text: labels.title, x: 0.5},
      paper_bgcolor: "#141c26", plot_bgcolor: "#141c26",
      font: {family: "system-ui, sans-serif", color: "#e4edf7", size: 12},
      margin: {l: 60, r: 20, t: 90, b: 60},
      xaxis: {title: {text: labels.games}, rangemode: "tozero",
        minallowed: 0, gridcolor: "#2d3947", tickformat: "d"},
      yaxis: {title: {text: labels.score}, rangemode: "tozero",
        minallowed: 0, gridcolor: "#2d3947"},
      legend: {orientation: "h", x: 0, y: 1.12},
      hovermode: "x unified", uirevision: revision
    };
  }

  const config = {
    responsive: true, displaylogo: false, scrollZoom: true,
    // Avoid a browser download prompt inside the desktop widget.
    modeBarButtonsToRemove: ["toImage", "select2d", "lasso2d"]
  };

  window.trainingChart = {
    initialize(rawLabels, version) {
      enqueue(async () => {
        const bridge = await channel;
        if (Plotly.version !== version) {
          throw new Error(`Plotly.js ${version} required; found ${Plotly.version}`);
        }
        labels = Object.fromEntries(Object.entries(rawLabels).map(
          ([key, value]) => [key, escape(value)]));
        await Plotly.newPlot(chart(), traces([], []), layout(0), config);
        bridge.rendered();
      });
    },
    replace(scores, means, revision) {
      enqueue(() => Plotly.react(chart(), traces(scores, means), layout(revision), config));
    },
    append(score, mean) {
      enqueue(() => {
        const game = chart().data[0].y.length + 1;
        return Plotly.extendTraces(chart(), {x: [[game], [game]], y: [[score], [mean]]}, [0, 1]);
      });
    }
  };
})();
