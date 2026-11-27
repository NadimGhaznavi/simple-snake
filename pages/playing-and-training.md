---
title: "Play and train"
lang: en
locale: en-US
language_name: English
translation_key: simple-snake-playing-and-training
classes: wide
author_profile: true
---

## Play yourself

Choose **Play yourself**, press **Start**, and guide the snake towards the food. Each piece of food adds one point and makes the snake longer. Hitting a wall or your own body ends the game; filling the board wins.

| Control | What it does |
| --- | --- |
| Arrow keys or WASD | Steer in human mode. Immediate reversal is ignored. |
| Start / Pause / Resume | Start or pause the current game or AI training. |
| Space | Start, pause or resume. |
| Speed | Limit moves per second (1–120; default 40). Lower it for easier human play. |
| New session | Stop and reset the current game or training, including chart and statistics. |
| Mode | Switch between human play and AI training; switching resets the session. |

## Train the AI

1. Choose **Train AI** and press **Start**.
2. Watch the snake play. It automatically begins another game after each game ends.
3. Increase Speed to spend less time watching individual moves or lower it to study the snake's choices.
4. Let it play many games before judging it. Early games can be short, and even after training it can still make mistakes.

Speed changes the pace of the simulation, not the neural network's learning rate. Actual speed depends on your computer.

## Read the chart

**Score** is the number of food items collected in a game. **Games** counts completed AI games. **Record** is the best completed AI score in this session (or the current best score in human mode). **Mean** is the average score over all completed AI games.

The chart plots individual completed-game scores and their cumulative mean. A single spike may be luck; a rising mean across many games suggests improving performance. The cumulative mean includes early games and may react slowly to later changes. The chart does not plot training loss or rewards.

## What is it learning?

The AI gets a reward of +10 for food, -10 for a collision or exceeding its move budget, and 0 for a normal move. It tries to predict the future value of each possible action using a neural network. At first it sometimes chooses randomly; that exploration decreases as the number of completed games rises. The AI also learns from remembered moves.

Each AI session begins with a fresh network and replay memory. Pause preserves them; **New session** and mode changes discard them. When a positive record is set, the app saves network weights at the path shown below the board (normally under `~/.local/share/BMForge/SimpleSnake` on Linux and Qt's per-user application-data directory on Windows).

The first positive record in a new session can overwrite a previous session's weights. Checkpoints contain weights only, and loading or resuming them is not implemented. Save screenshots or copy the checkpoint separately if you want to preserve an interesting result.

AI games also have a total-move cutoff that grows with snake length; human games do not.

Ready to change the rules of learning? See [AI experiments]({{ site.baseurl }}{% link pages/experiments.md %}).

---

[Documentation index]({{ site.baseurl }}{% link index.md %})
