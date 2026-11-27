---
title: "Controls and training"
lang: en
locale: en-US
language_name: English
translation_key: simple-snake-playing-and-training
classes: wide
author_profile: true
---

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

---

[Documentation index]({{ site.baseurl }}{% link index.md %})
