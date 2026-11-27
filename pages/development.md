---
title: "Development"
lang: en
locale: en-US
language_name: English
translation_key: simple-snake-development
classes: wide
author_profile: true
---

See [architecture]({{ site.baseurl }}{% link pages/architecture.md %}) for the module map and learning flow.
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
[third-party notices]({{ site.baseurl }}{% link pages/credits.md %}). This project retains its
[GPL license](https://github.com/{{ site.repository }}/blob/main/LICENSE).

---

[Documentation index]({{ site.baseurl }}{% link index.md %})
