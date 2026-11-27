---
title: "Get started"
lang: en
locale: en-US
language_name: English
translation_key: simple-snake-getting-started
classes: wide
author_profile: true
---

Run Simple Snake from its source folder if you want to play, watch the AI or experiment with its learning settings.

## Prerequisites

- A Windows or Linux computer with a graphical desktop and a supported 64-bit Python environment.
- [Python](https://www.python.org/downloads/) 3.12–3.15 with pip and venv. On Windows, use the standard 64-bit (x86-64) build; the commands below use 3.15. Python 3.13 has been tested on Linux. Check with `py -3.15 --version` on Windows or `python3 --version` on Linux.
- On Windows, the latest [Microsoft Visual C++ x64 Redistributable](https://aka.ms/vc14/vc_redist.x64.exe), required by PyTorch. Install it or choose **Repair**, and restart Windows if requested. For a PyTorch DLL error such as `[WinError 126]` loading `shm.dll`, see [installation recovery]({{ site.baseurl }}{% link pages/installation.md %}#recover-from-a-pytorch-dll-error).
- Internet access for the initial dependency download, sufficient free disk space for Python packages (including PyTorch), and a writable folder.
- The project source: open the [GitHub repository](https://github.com/{{ site.repository }}), select the desired branch or release, choose **Code → Download ZIP**, and extract it. Git is optional.

**Do I need to install Qt?** No. PySide6's pip wheels include Qt and Qt WebEngine ([Qt for Python installation guide](https://doc.qt.io/qtforpython-6/gettingstarted.html)). The project's requirements install PySide6, NumPy and CPU PyTorch into a private Python environment. Plotly.js is bundled with the application, so the chart works offline. You do not need a separate Qt SDK, Qt Creator, CUDA or a dedicated GPU.

On Linux, Qt may still require system-level graphical libraries, such as XCB dependencies. Install the library named in any Qt startup error through your distribution's package manager. Some Linux distributions also package Python's venv support separately.

## Windows: your first launch

Open PowerShell or Command Prompt in the extracted project folder (the one containing `requirements.txt`) and run:

```powershell
py -3.15 -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt
.venv\Scripts\python.exe -m simplesnake
```

The first command creates a private Python environment, the second installs dependencies, and the third opens the game.

For subsequent launches, double-click `scripts\run.cmd` in File Explorer or run the final command again. You do not need to activate the environment. If the Python launcher cannot find 3.15, install it or explicitly select another supported interpreter. An existing virtual environment keeps its original Python version; to switch to 3.15, rename the old environment and repeat the setup commands.

Native Windows desktop validation is still pending.

## Linux: your first launch

Open a terminal in the project folder, using a supported Python version:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
./scripts/run.sh
```

For subsequent launches, run `./scripts/run.sh` again.

## Your first game

Choose **Play yourself**, reduce **Speed** if necessary, and press **Start**. Collect food using the arrow keys or WASD. Then choose **Train AI** and press **Start** to watch the computer take over.

Next: [Controls and training]({{ site.baseurl }}{% link pages/playing-and-training.md %}) or [experiment with the AI]({{ site.baseurl }}{% link pages/experiments.md %}).

If you want a separate installed copy instead, see the [installation guide]({{ site.baseurl }}{% link pages/installation.md %}).

The launch command also supports `--help`, `--version` and `--language en`. English is currently the only included translation. For display-free tests, see [Development and testing]({{ site.baseurl }}{% link pages/development.md %}).

---

[Documentation index]({{ site.baseurl }}{% link index.md %})
