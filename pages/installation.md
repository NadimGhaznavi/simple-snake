---
title: "Install, upgrade, uninstall"
lang: en
locale: en-US
language_name: English
translation_key: simple-snake-installation
classes: wide
author_profile: true
---

Use the [source setup]({{ site.baseurl }}{% link pages/getting-started.md %}) to experiment with the code, or install a separate copy for everyday use. The installer manages its own application files and private Python environment.

## Prerequisites

- A Windows or Linux computer with a graphical desktop and a supported 64-bit Python environment.
- [Python](https://www.python.org/downloads/) 3.12–3.14 with pip and venv. The commands below use 3.13 on Windows; Python 3.13 has been tested on Linux. Check with `py -3.13 --version` on Windows or `python3 --version` on Linux.
- Internet access for the initial dependency download, sufficient free disk space for Python packages (including PyTorch), and a writable folder.
- The project source: open the [GitHub repository](https://github.com/{{ site.repository }}), select the desired branch or release, choose **Code → Download ZIP**, and extract it. Git is optional.

**Do I need to install Qt?** No. PySide6's pip wheels include the Qt binaries ([Qt for Python installation guide](https://doc.qt.io/qtforpython-6/gettingstarted.html)). The project's requirements install PySide6, Matplotlib, NumPy and CPU PyTorch into a private Python environment. You do not need a separate Qt SDK, Qt Creator, CUDA or a dedicated GPU.

On Linux, Qt may still require system-level graphical libraries, such as XCB dependencies. Install the library named in any Qt startup error through your distribution's package manager. Some Linux distributions also package Python's venv support separately.

The current installer is a source-file installer, not a frozen EXE, MSI or Start menu installer. It does not create a service.

## Windows

Open PowerShell in the source folder. Keep that folder separate from the installation destination.

Check the prerequisites, then install:

```powershell
py -3.13 scripts/install.py install --check
py -3.13 scripts/install.py install
```

The default destination is `%LOCALAPPDATA%\Programs\SimpleSnake`. Launch the installed game with:

```powershell
& "$env:LOCALAPPDATA\Programs\SimpleSnake\scripts\run.cmd"
```

Or double-click its `scripts\run.cmd` in File Explorer. Native Windows desktop validation remains pending.

To upgrade, obtain the new source and run the upgrade command from that source folder. To remove the installed copy, run uninstall instead. Close the game first.

```powershell
py -3.13 scripts/install.py upgrade
py -3.13 scripts/install.py uninstall
```

## Linux

The default destination is `/opt/prod/simplesnake`, which normally requires administrator access. For a personal installation, use a folder you own:

```bash
python3 scripts/install.py install --destination "$HOME/apps/SimpleSnake" --check
python3 scripts/install.py install --destination "$HOME/apps/SimpleSnake"
"$HOME/apps/SimpleSnake/scripts/run.sh"
```

To upgrade from new source or uninstall, run the appropriate command:

```bash
python3 scripts/install.py upgrade --destination "$HOME/apps/SimpleSnake"
python3 scripts/install.py uninstall --destination "$HOME/apps/SimpleSnake"
```

## What the installer does

The installer uses BMForge's ownership manifest and readable version constants. It creates an isolated venv, installs the pinned dependencies, verifies imports and starts an offscreen Qt window before writing the successful-version marker. System and user-site PyPI packages are left unchanged.

Use the same `--destination` on later operations. Paths containing spaces are supported. The `install`, `upgrade` and `uninstall` wrappers in [scripts](https://github.com/{{ site.repository }}/tree/main/scripts) are also available as `.cmd` and `.sh` files; Windows wrappers use Python on PATH. The explicit commands above select the interpreter directly.

`--check` validates local prerequisites without installing packages or writing files, but cannot guarantee a later download. Upgrades preserve user files and checkpoints. Uninstall removes owned code and the owned venv, retaining unowned files and per-user app data. A failed upgrade retains the last-successful marker but does not roll back files already copied; retry the upgrade or uninstall from the separate source folder.

---

[Documentation index]({{ site.baseurl }}{% link index.md %})
