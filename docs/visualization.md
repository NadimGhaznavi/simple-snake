# Desktop training chart specification

Specification: 0.1.0. Application: Simple Snake.

The user approved replacing Matplotlib with Plotly.js 4.1.1, embedding the
chart in Qt WebEngine, and bundling JavaScript for offline use on 2026-11-27.
This application-specific specification adapts BMForge visualization 0.1.0;
the pinned upstream skill remains unchanged.

## Approved adaptations

- Render inside the existing PySide6 desktop window using `QWebEngineView`,
  with `QWebChannel` for readiness and failure notifications. No HTTP server,
  frontend framework, Python plotting package or new Python dependency.
- Serve the application-owned HTML, JavaScript and Plotly distribution from
  local package files instead of the BMForge reference CDN at runtime.
- Keep score and mean computation in the existing training activities. The
  chart receives completed-game values and displays them as two line traces.

## Asset provenance

- Exact asset: [Plotly.js 4.1.1](https://cdn.plot.ly/plotly-4.1.1.min.js), copied
  unmodified to [plotly-4.1.1.min.js](../simplesnake/assets/plotly-4.1.1.min.js).
- SHA-256: `3b6e15d45dbb7fca5bd2094291e961ddc5472cd887009e6009a56dab668d721f`.
- License: [upstream v4.1.1 MIT license](https://github.com/plotly/plotly.js/blob/v4.1.1/LICENSE),
  included as [LICENSE-PLOTLY](../LICENSE-PLOTLY).
- Preserve the distribution's embedded third-party notices. Package the HTML,
  JavaScript and license in Python wheels and source-file deployments.

## Required behavior

1. Render localized title, axes and score/mean labels, escaping label content.
2. Retain games completed before browser initialization. Serialize appends and
   resets so asynchronous rendering preserves the current session's data.
3. Support hover values, zoom, pan and legend toggles. Preserve the view when
   appending games; restore automatic axes and both lines on session reset.
4. Resize with the desktop splitter and window. Operate entirely offline;
   prohibit remote page access and remote resource connections.
5. Display load/render failures in the chart area. Verify the browser's actual
   initial render in the install/upgrade startup probe.

Native Windows desktop verification remains pending. The full Plotly bundle
is about 4.6 MiB; Qt WebEngine adds browser processes supplied by PySide6.
