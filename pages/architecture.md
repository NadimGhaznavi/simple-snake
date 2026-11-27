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

The application uses BMForge's Activity / Interface / Entity responsibilities.
Each substantial class has its own module. There is no runtime framework
beyond Qt, Matplotlib, NumPy, and PyTorch.

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
   it appends to the Matplotlib chart only on a completed game.

`QTrainer` computes reward + discount × max(next Q) for live transitions and
reward alone for terminal transitions. Its target is detached. The mean square
error includes all three outputs, as in the reference; only the selected
action's target differs from the current prediction.

## Thread ownership and shutdown

All widgets and Matplotlib operations stay on the Qt GUI thread. The worker
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

## Portability and ownership

UI assets use Qt painting and system fonts. Resource paths derive from the
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
MSI package. Native Windows platform integration will be validated in the VM.

---

[Documentation index]({{ site.baseurl }}{% link index.md %})
