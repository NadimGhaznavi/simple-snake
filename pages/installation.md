---
title: "Install, upgrade, uninstall"
lang: en
locale: en-US
language_name: English
translation_key: simple-snake-installation
classes: wide
author_profile: true
---

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
[scripts](https://github.com/{{ site.repository }}/tree/main/scripts) as `.sh` and `.cmd` files. The Windows wrappers use `python`
on PATH; the explicit `py -3.13` commands above select a specific interpreter.
Paths containing spaces are supported. `--check` validates local prerequisites
without writing files or installing packages; it cannot guarantee a future
package download will succeed.

Upgrades preserve user files and checkpoints. Uninstall removes owned code
and the owned virtual environment, retaining unowned files and per-user app
data. Failed upgrades retain the last-successful marker but do not roll back
files already copied; retry the upgrade or uninstall using the source checkout.

---

[Documentation index]({{ site.baseurl }}{% link index.md %})
