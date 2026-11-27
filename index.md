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

**Can you teach a computer to beat your high score at Snake?**

Simple Snake is the classic game with a twist: play it yourself, or put a little AI in charge and watch it learn from its own mistakes. It starts with a fresh neural network, tries moves, collects food and crashes into walls. A live chart shows its progress, one game at a time.

The AI runs on your computer. No cloud account, API key or dedicated graphics card is required.

## Get playing

- [Get started on Windows or Linux]({{ site.baseurl }}{% link pages/getting-started.md %}) — prerequisites and running from source.
- [Install the desktop app]({{ site.baseurl }}{% link pages/installation.md %}) — set up a separate local copy.
- [Play and train]({{ site.baseurl }}{% link pages/playing-and-training.md %}) — controls, scores and your first AI session.

## Give your snake a different brain

What happens if you reward food more generously? Does a bigger neural network make a better player? Should the snake spend more time trying random moves?

[Try some AI experiments]({{ site.baseurl }}{% link pages/experiments.md %}) and find out. For now, training settings live in two small Python files rather than in the game window. You can play and watch the AI without changing any code.

This is reinforcement learning: the snake receives feedback for what it does, and a neural network learns to estimate which moves are worth taking. Simple Snake adapts Patrick Loeber's Snake AI into a Qt desktop application with an embedded training chart.

## Under the hood

- [How the AI and app work]({{ site.baseurl }}{% link pages/architecture.md %}) — the learning loop and application structure.
- [Development and testing]({{ site.baseurl }}{% link pages/development.md %}) — work on the code and run the tests.
- [Changelog]({{ site.baseurl }}{% link CHANGELOG.md %}) — what's changed.
- [License and credits]({{ site.baseurl }}{% link pages/credits.md %}) — upstream project and licensing.

[Browse the source code](https://github.com/{{ site.repository }}).

**Development status:** Windows scripts are included, but native Windows desktop validation remains pending. The application has been tested on Linux. Training is stochastic, so improvement is not guaranteed.
