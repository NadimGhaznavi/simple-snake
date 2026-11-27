---
title: "AI experiments"
lang: en
locale: en-US
language_name: English
translation_key: simple-snake-experiments
classes: wide
author_profile: true
---

What makes a good AI snake? There is no magic setting. The fun is finding out what happens when you change one thing and watch the results.

## Before you start

Run from a source folder using the [getting-started guide]({{ site.baseurl }}{% link pages/getting-started.md %}). The current game window does not have controls for training hyperparameters. Instead, open two small Python files in a text editor:

- `simplesnake/constants/DTraining.py` — neural network, learning, memory and exploration.
- `simplesnake/constants/DGame.py` — rewards and game rules.

You do not need to rewrite the game. Change the number after an equals sign, save the file, close the application and relaunch from the same source folder. Starting a new session inside the old process will not reload the edited constants. Keep a copy of the original files so you can restore them.

## The AI's settings

| Setting | Default | What you are changing |
| --- | ---: | --- |
| `HIDDEN_SIZE` | 256 | Number of hidden neurons in the network. |
| `LEARNING_RATE` | 0.001 | Size of the optimizer's learning updates. |
| `DISCOUNT` | 0.9 | How much predicted future reward matters. |
| `MEMORY_SIZE` | 100,000 | Maximum remembered transitions. |
| `BATCH_SIZE` | 1,000 | Maximum transitions sampled for replay at the end of a game. |
| `EXPLORATION_GAMES` | 80 | Exploration schedule intercept; random moves stop after this many completed games. |
| `EXPLORATION_RANGE` | 200 | Upper inclusive bound of the random draw used in exploration. |

With the defaults, the initial random-action probability is 80/201 (about 40%). It falls as games finish and reaches zero after 80 games. Random actions may include the same action the model would have chosen.

Leave `INPUT_SIZE` (11) and `ACTION_COUNT` (3) unchanged: they match the actual observation and action interfaces.

## The snake's rewards

| Setting | Default | What you are changing |
| --- | ---: | --- |
| `FOOD_REWARD` | +10 | Reward for eating food. |
| `DEATH_REWARD` | -10 | Penalty for a collision or exceeding the move budget. |
| `STEP_REWARD` | 0 | Reward for ordinary movement. |
| `STARVATION_FACTOR` | 100 | Multiplier for the total-move budget relative to snake length. |

The score remains the number of food items collected. Changing a reward does not change the score awarded for food. The AI learns from the rewards, not directly from the score chart.

## Four challenges

| Challenge | Change one setting | Question to investigate |
| --- | --- | --- |
| A bigger brain | `HIDDEN_SIZE`: 256 → 128, or 512 | Does a larger or smaller network learn more effectively? |
| Fast learner | `LEARNING_RATE`: 0.001 → 0.0005, or 0.002 | Does a different update size help or destabilize learning? |
| Long-term thinker | `DISCOUNT`: 0.9 → 0.95, or 0.8 | Does valuing future rewards change how well the snake survives? |
| Extra-curious snake | `EXPLORATION_GAMES`: 80 → 120 | Does a longer and initially stronger exploration schedule help it find better strategies? |

Bonus: try increasing `FOOD_REWARD` from 10 to 15 or changing `STEP_REWARD` from 0 to -1. Does the snake learn to find food more efficiently, or does a new reward have an unintended effect?

## Run a fair experiment

1. Train with the original settings for a chosen number of completed games (for example, 150). Record the final mean, record and a screenshot of the chart.
2. Change just one setting and relaunch the app.
3. Train for the same number of completed games, and record the same results. Keep the board and other settings fixed.
4. Repeat both settings several times. The network initialization, food placement and random moves vary from run to run; the current app does not offer seed controls.
5. Compare typical mean scores and records across runs. Ask whether the change helped consistently, rather than selecting the luckiest game.

Try to predict what will happen before starting. Unexpected results are often the most interesting ones.

| Run | Changed setting | Games | Mean score | Record | What did you notice? |
| --- | --- | --- | --- | --- | --- |
| Baseline | Defaults | | | | |
| Experiment 1 | | | | | |
| Experiment 2 | | | | | |

## Want to see the code that does the learning?

The [application structure guide]({{ site.baseurl }}{% link pages/architecture.md %}) explains how the 11 observations enter the neural network, how it chooses among three moves, and how feedback updates its predictions. The [development guide]({{ site.baseurl }}{% link pages/development.md %}) shows how to run the tests.

---

[Documentation index]({{ site.baseurl }}{% link index.md %})
