# Simple Snake

A small PySide6/Qt port of Patrick Loeber's AI Snake game, with Matplotlib
training charts inside the application. Play yourself or watch a CPU-based
Q-learning agent train. The focus is readable code and a portable desktop app.

## Run from source

Use 64-bit Python 3.12–3.14 (tested here with Python 3.13 on Linux).
The pinned requirements use CPU PyTorch; no GPU or CUDA setup is needed.

Linux:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
./scripts/run.sh
```

Windows (PowerShell or Command Prompt, from the project root):

```powershell
py -3.13 -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt
.venv\Scripts\python.exe -m simplesnake
```

You can also use `scripts\run.cmd` after creating the virtual environment.
No activation is required. `--help`, `--version`, and `--language en` are
supported. English is the only published translation; UI messages use the
bundled catalogue so later translations do not require changing game code.

On Linux, Qt needs a graphical desktop and its platform libraries. If Qt
reports a missing `xcb` library, install the named system library through
your distribution. For automated tests without a display, use
`QT_QPA_PLATFORM=offscreen`.

## Controls and training

- Choose **Play yourself** or **Train AI**, then press **Start**.
- Steer with the arrow keys or WASD. An immediate reversal is ignored.
- **Pause** or Space pauses/resumes. Change **Speed** to control steps per second.
- **New session** or changing mode stops the worker and clears the board and chart.
- The chart shows each completed AI game's score and the cumulative mean.

Each AI session starts a fresh network and replay memory. A new positive
record saves model weights to the path displayed below the board. On Linux
this normally falls under `~/.local/share/BMForge/SimpleSnake`; on Windows it
uses Qt's per-user application-data location. A new session can replace the
previous session's checkpoint when it sets its first positive record.
Checkpoints contain weights only: loading/resuming a saved training session
is not implemented.

The port retains the reference's 11 observations, 11→256→3 network, relative
actions, epsilon schedule, replay limit/batch size, learning rate, discount,
rewards, and total-step starvation rule for AI games. Human games have no
starvation limit. Q-learning targets are detached from autograd, and a full
board ends as a win. Learning is stochastic; short runs are not evidence of
convergence. The GUI remains responsive while individual and replay training
steps run in a worker thread.

## Install, upgrade, uninstall

The BMForge source-file installer creates an owned installation with its own
virtual environment, manifest, readable version constants, and successful
version marker. It checks dependencies and starts an offscreen Qt window
before marking an installation successful. It does not create a service.

All application packages are installed into that venv. The system Python is
used only to create it; system and user-site PyPI packages are left unchanged.
The application launchers always use the venv's Python.

Run lifecycle commands from a separate checkout, outside the destination.
The default Linux destination is `/opt/prod/simplesnake` (normally requiring
administrator permissions); Windows defaults to
`%LOCALAPPDATA%\Programs\SimpleSnake`. Use `--destination` for a user-writable
directory or a disposable test installation. Always pass the same destination
on later upgrade/uninstall commands.

Linux example:

```bash
python3 scripts/install.py install --destination "$HOME/apps/SimpleSnake" --check
python3 scripts/install.py install --destination "$HOME/apps/SimpleSnake"
"$HOME/apps/SimpleSnake/scripts/run.sh"
python3 scripts/install.py upgrade --destination "$HOME/apps/SimpleSnake"
python3 scripts/install.py uninstall --destination "$HOME/apps/SimpleSnake"
```

Windows example:

```powershell
py -3.13 scripts/install.py install --check
py -3.13 scripts/install.py install
& "$env:LOCALAPPDATA\Programs\SimpleSnake\scripts\run.cmd"
py -3.13 scripts/install.py upgrade
py -3.13 scripts/install.py uninstall
```

Thin `install`, `upgrade`, and `uninstall` wrappers are available under
[scripts](scripts/) as `.sh` and `.cmd` files. The Windows wrappers use `python`
on PATH; the explicit `py -3.13` commands above select a specific interpreter.
Paths containing spaces are supported. `--check` validates local prerequisites
without writing files or installing packages; it cannot guarantee a future
package download will succeed.

Upgrades preserve user files and checkpoints. Uninstall removes owned code
and the owned virtual environment, retaining unowned files and per-user app
data. Failed upgrades retain the last-successful marker but do not roll back
files already copied; retry the upgrade or uninstall using the source checkout.

## Development

See [architecture](docs/architecture.md) for the module map and learning flow.
No application module imports BMForge or the reference project at runtime.
The ignored `loeber-snake` directory is **read-only reference material**.

Run the tests with the installed application dependencies (no separate test
framework is required):

```bash
QT_QPA_PLATFORM=offscreen .venv/bin/python -m unittest discover -v
```

Windows PowerShell:

```powershell
$env:QT_QPA_PLATFORM = "offscreen"
.venv\Scripts\python.exe -m unittest discover -v
```

Tests cover game rules, training math, model saves, localization, Qt controls,
pause/reset/shutdown, and install/upgrade/uninstall using real offline wheel
fixtures. Linux offscreen tests exercise Qt behavior, but native Windows
desktop validation remains to be done on the Windows VM.

The upstream attribution and MIT notice are preserved in
[THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md). This project retains its
[GPL license](LICENSE). The [project website](https://simplesnake.osoyalce.com)
is maintained separately.

