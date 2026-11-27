---
title: "Simple Snake"
layout: single
classes: wide
author_profile: true
lang: en
locale: en-US
language_name: English
translation_key: simple-snake-home
permalink: /
---

![{{ site.title }} logo]({{ site.logo | relative_url }})

A small PySide6/Qt port of Patrick Loeber's AI Snake game, with Matplotlib
training charts inside the application. Play yourself or watch a CPU-based
Q-learning agent train. The focus is readable code and a portable desktop app.

## Documentation

- [Run from source]({{ site.baseurl }}{% link pages/getting-started.md %}) — Python requirements and Linux/Windows setup.
- [Controls and training]({{ site.baseurl }}{% link pages/playing-and-training.md %}) — human play, AI sessions, charts, and checkpoints.
- [Install, upgrade, uninstall]({{ site.baseurl }}{% link pages/installation.md %}) — owned installations and platform lifecycle commands.
- [Development]({{ site.baseurl }}{% link pages/development.md %}) — test commands and portability checks.
- [Application structure]({{ site.baseurl }}{% link pages/architecture.md %}) — modules, learning flow, and thread ownership.
- [Changelog]({{ site.baseurl }}{% link CHANGELOG.md %}) — project changes.
- [License and credits]({{ site.baseurl }}{% link pages/credits.md %}) — project license and upstream attribution.

[Source code](https://github.com/{{ site.repository }})
