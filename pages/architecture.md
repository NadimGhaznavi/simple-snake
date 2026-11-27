---
title: "Application structure"
lang: en
locale: en-US
language_name: English
translation_key: simple-snake-architecture
permalink: /docs/architecture.html
classes: wide
author_profile: true
---

## Overview

The AI has a surprisingly small brain: 11 inputs, one hidden layer of 256 neurons with a ReLU activation, and three outputs predicting the value of moving straight, turning right or turning left. It learns by updating those predictions using rewards and future value estimates. For an introduction to neural networks, have a look at this excellent [3Blue1Brown youtube video](https://www.youtube.com/watch?v=aircAruvnKk&list=PLZHQObOWTQDNU6R1_67000Dx_ZCJB-3pi), heads up it's 18:40 long.

### How the application starts

On Linux, launch the application from the project directory with:

```bash
./scripts/run.sh
```

The startup path connects the launcher to the Python classes:

1. [scripts/run.sh](https://github.com/{{ site.repository }}/blob/main/scripts/run.sh) changes to the project directory and runs `.venv/bin/python -B -m simplesnake`. It uses the virtual environment's Python directly, so a separate activation step is unnecessary.
2. `-m simplesnake` tells Python to run the `simplesnake` package through [simplesnake/__main__.py](https://github.com/{{ site.repository }}/blob/main/simplesnake/__main__.py). Its `main()` function creates the Qt application, shows the window, and starts the event loop that handles user input.
3. The window class, `MainWindow`, lives in [simplesnake/interface/MainWindow.py](https://github.com/{{ site.repository }}/blob/main/simplesnake/interface/MainWindow.py). It creates a `SnakeGame` instance from [simplesnake/activity/SnakeGame.py](https://github.com/{{ site.repository }}/blob/main/simplesnake/activity/SnakeGame.py), which contains the game rules. `simplesnake` is the package name; `SnakeGame` is the game class.

## Changing the brain

If you want to try changing the brain or its rewards first, start with [AI experiments]({{ site.baseurl }}{% link pages/experiments.md %}). The rest of this page explains the implementation.

## Python class organization

The application categorizes its classes into *Activity*, *Interface*, and *Entity* categories.

| Package | Owns |
| --- | --- |
| `simplesnake/activity` | Snake rules, agent decisions, and training-session orchestration |
| `simplesnake/interface` | Qt widgets/scheduling, PyTorch network/training, checkpoint files, and localization |
| `simplesnake/entity` | Immutable points, game snapshots, step results, and training progress |
| `simplesnake/constants` | Domain defaults, stable enum values, message keys, and literal application metadata |
| `simplesnake/locales` | English source messages |
| `scripts` | Platform launchers and the adapted BMForge install/upgrade/uninstall helper |

## A training step

1. `TrainingWorker` creates and owns one `TrainingSession` inside its thread.
2. `Agent.observe()` reads `SnakeGame` and produces the 11 reference features:
   danger straight/right/left, current direction left/right/up/down, and food
   left/right/up/down.
3. The agent explores or picks the largest predicted Q value. Actions are
   integer enums: straight, right, left. These replace one-hot vectors without
   changing their meaning or order.
4. `SnakeGame.step()` applies the relative move and returns reward/done/score.
   Grid coordinates replace pixel coordinates; the default board remains 32×24.
5. The agent learns from the transition and remembers it. At the end of a game
   it also trains on up to 1,000 replay transitions, increments its game count,
   and the session updates score statistics and saves a new record's weights.
6. The worker emits an immutable snapshot. `MainWindow` paints that snapshot;
   it appends to the embedded Plotly.js chart only on a completed game.

`QTrainer` computes reward + discount × max(next Q) for live transitions and
reward alone for terminal transitions. Its target is detached. The mean square
error includes all three outputs, as in the reference; only the selected
action's target differs from the current prediction.

## Thread ownership and shutdown

All widgets and browser bridge calls stay on the Qt GUI thread. Plotly renders
inside Qt WebEngine's browser process. The worker
owns its model, optimizer, replay memory, and game. Its condition variable
protects pause, speed, and stop flags; the UI never shares mutable learning
state. A pause may allow the move already in flight to finish. Speed is an
upper limit; slower learning steps reduce the actual rate.

Reset, mode changes, and close wake a paused worker, request cooperative stop,
and wait for its current local move/replay/save to finish before discarding it.
No thread is forcibly terminated. Frames already queued by an old worker are
ignored. A worker failure stops training and displays the error; the next
Start begins a fresh session.

Human play uses a GUI `QTimer` and the same rules. Only the latest legal
direction is applied per tick, so rapid keypresses cannot reverse into the
snake between ticks. The starvation cutoff is disabled in human mode.

## Training chart

The chart uses **Plotly.js 4.1.1**, following the pinned BMForge visualization
component 0.1.0. This project's approved desktop adaptation embeds the chart
in `QWebEngineView` rather than an HTTP display server and bundles the exact
JavaScript asset locally rather than loading BMForge's CDN URL. The application
has no HTTP listener and charts work offline. PySide6 already supplies Qt
WebEngine and Qt WebChannel; the Python `plotly` package is not used.

`TrainingChart` owns the score/mean history. Qt WebChannel reports browser
readiness and rendering failures; JSON transfers localized labels and data
to the page. Games completed before the initial render are retained, and
browser updates run in order so resets cannot race with earlier appends.
New points extend the two existing traces and preserve zoom and legend
choices. A new session clears the traces and restores automatic axes.
Labels are escaped before Plotly renders them. Load/render errors appear in
the chart area, and installation verifies the initial browser render.

The packaged assets and Plotly MIT license live in `simplesnake/assets`.
The project-specific specification in `docs/visualization.md` records asset
provenance and the approved adaptations without changing the pinned BMForge
skill snapshot.

## Portability and ownership

The board uses Qt painting and system fonts; the chart uses bundled browser
assets and system fonts. Resource paths derive from the
package directory; writable model paths come from `QStandardPaths`. The app
does not depend on the working directory, Pygame, IPython, a bundled font, or
anything in the ignored reference checkout.

`scripts/install.py` adapts the pinned BMForge installer, rather than adding a
second packaging framework. It selects `bin/python` or `Scripts/python.exe`,
uses the host interpreter to create an owned venv, validates real imports and
Qt startup, and writes the successful marker last. The portable desktop
requirement adds `sys` to the template imports to identify the host interpreter.
Windows uses a per-user destination instead of the Linux `/opt/prod` path;
the canonical CMDB constants remain readable in either deployment.

There are no services, listeners, databases, hidden production changes, or
automatic releases. The source-file installer is not a frozen executable or
MSI package. Native Windows desktop validation remains pending.

---

[Documentation index]({{ site.baseurl }}{% link index.md %})
