---
title: "Development"
lang: en
locale: en-US
language_name: English
translation_key: simple-snake-development
classes: wide
author_profile: true
---

First set up a source environment using the [getting-started guide]({{ site.baseurl }}{% link pages/getting-started.md %}). You can experiment with learning constants using the [AI experiments guide]({{ site.baseurl }}{% link pages/experiments.md %}), or explore the implementation and tests below.

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
offline browser chart rendering, zoom/legend persistence, chart reset/resize,
pause/reset/shutdown, and install/upgrade/uninstall using real offline wheel
fixtures. Linux offscreen tests exercise Qt behavior, but native Windows
desktop validation remains to be done on the Windows VM.

The Python compatibility workflow runs these tests on Windows x86-64 with
Python 3.15. It also installs the package metadata, checks the Windows
launcher, and exercises a deployed install, upgrade, and uninstall with the
real application dependencies. These offscreen checks complement manual
Windows desktop testing.

The Qt tests select software rendering for headless execution. Qt WebEngine
still starts Chromium's sandboxed renderer processes, so run them on a host
that permits those subprocesses and their IPC.

The upstream attribution and MIT notice are preserved in
[third-party notices]({{ site.baseurl }}{% link pages/credits.md %}). This project retains its
[GPL license](https://github.com/{{ site.repository }}/blob/main/LICENSE).

---

[Documentation index]({{ site.baseurl }}{% link index.md %})
