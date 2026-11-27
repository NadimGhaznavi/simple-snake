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

- Internet access for the initial dependency download, sufficient free disk space for Python packages (including PyTorch), and a writable folder.
- The project source: open the [GitHub repository](https://github.com/{{ site.repository }}), select the desired branch or release, choose **Code → Download ZIP**, and extract it.

### Windows Prerequisites

- Install a supported 64-bit (x86-64) [Python](https://www.python.org/downloads/) build.
- Install the latest [Microsoft Visual C++ x64 Redistributable](https://aka.ms/vc14/vc_redist.x64.exe), required by PyTorch. If it is already installed, choose **Repair**. Restart Windows if the Microsoft installer requests it.

### Linux Prerequisites

On Linux, Qt may still require system-level graphical libraries, such as XCB dependencies. Install the library named in any Qt startup error through your distribution's package manager. Some Linux distributions also package Python's venv support separately.

## Windows

Open PowerShell in the source folder. Keep that folder separate from the installation destination.

Check the prerequisites, then install:

```powershell
py -3.15 scripts/install.py install --check
py -3.15 scripts/install.py install
```

The default destination is `%LOCALAPPDATA%\Programs\SimpleSnake`. Launch the installed game with:

```powershell
& "$env:LOCALAPPDATA\Programs\SimpleSnake\scripts\run.cmd"
```

Or double-click its `scripts\run.cmd` in File Explorer. Native Windows desktop validation remains pending.

### Recover from a PyTorch DLL error

If installation fails with `[WinError 126]` while loading `torch\lib\shm.dll` or one of its dependencies, a missing or damaged Visual C++ runtime is a common cause. Install or repair the x64 redistributable linked above, restart Windows if requested, then rerun the same `install` command from the source folder. A reboot alone does not install a missing runtime. The installer can reuse its owned environment and packages; you do not need to delete the installation folder.

The installer checks that the required C++ runtime DLLs load before copying application files or downloading packages, including with `--check`. This prerequisite check does not verify every PyTorch DLL; the full deployed import check still runs after dependency installation. If the error persists after repairing the runtime, retain the full error output for diagnosis.

### Upgrade or uninstall

To upgrade, obtain the new source and run the upgrade command from that source folder. To remove the installed copy, run uninstall instead. Close the game first.

```powershell
py -3.15 scripts/install.py upgrade
py -3.15 scripts/install.py uninstall
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

The interpreter running the installer creates the private environment on first installation. An upgrade reuses that environment and its original Python version. To move an installed copy to Python 3.15, uninstall it and install again using `py -3.15`; uninstall preserves per-user app data and checkpoints.

The installer uses BMForge's ownership manifest and readable version constants. It creates an isolated venv, installs the pinned dependencies, verifies imports and starts an offscreen Qt window before writing the successful-version marker. System and user-site PyPI packages are left unchanged.

Use the same `--destination` on later operations. Paths containing spaces are supported. The `install`, `upgrade` and `uninstall` wrappers in [scripts](https://github.com/{{ site.repository }}/tree/main/scripts) are also available as `.cmd` and `.sh` files; Windows wrappers use Python on PATH. The explicit commands above select the interpreter directly.

`--check` validates local prerequisites without installing packages or writing files, but cannot guarantee a later download. Upgrades preserve user files and checkpoints. Uninstall removes owned code and the owned venv, retaining unowned files and per-user app data. A failed upgrade retains the last-successful marker but does not roll back files already copied; retry the upgrade or uninstall from the separate source folder.

---

[Documentation index]({{ site.baseurl }}{% link index.md %})
