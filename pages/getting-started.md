---
title: "Run from source"
lang: en
locale: en-US
language_name: English
translation_key: simple-snake-getting-started
classes: wide
author_profile: true
---

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

---

[Documentation index]({{ site.baseurl }}{% link index.md %})
