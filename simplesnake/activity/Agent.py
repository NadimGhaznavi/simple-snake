from collections import deque
import random

import numpy as np
import torch

from simplesnake.constants.DGame import DAction, DDirection
from simplesnake.constants.DTraining import DTraining
from simplesnake.interface.QNetwork import QNetwork
from simplesnake.interface.QTrainer import QTrainer


class Agent:
    """Observe, explore, and learn from individual moves and replay memory."""

    def __init__(self, *, rng=None):
        # The * makes rng keyword-only; injecting it lets tests repeat random choices.
        # https://docs.python.org/3/tutorial/controlflow.html#keyword-only-arguments
        self.rng = rng if rng is not None else random.Random()
        self.games = 0
        # A bounded deque discards the oldest move when memory fills up.
        # https://docs.python.org/3/library/collections.html#collections.deque
        self.memory = deque(maxlen=DTraining.MEMORY_SIZE)
        self.model = QNetwork()
        self.trainer = QTrainer(self.model)

    @staticmethod
    def observe(game):
        # A static method needs no Agent instance (self); it only reads the game.
        # https://docs.python.org/3/library/functions.html#staticmethod
        direction = game.direction
        danger = [game.is_collision(game.next_point(DDirection((direction + turn) % len(DDirection))))
                  for turn in (0, 1, -1)]
        head, food = game.snake[0], game.food
        # The network receives 11 numbers: danger, heading, then food direction.
        # *danger expands the three danger flags into separate list elements.
        return np.array([
            *danger,
            direction == DDirection.LEFT, direction == DDirection.RIGHT,
            direction == DDirection.UP, direction == DDirection.DOWN,
            food is not None and food.x < head.x,
            food is not None and food.x > head.x,
            food is not None and food.y < head.y,
            food is not None and food.y > head.y,
        ], dtype=np.float32)

    def choose_action(self, state):
        # Random moves explore early; later, choose the highest predicted reward.
        epsilon = DTraining.EXPLORATION_GAMES - self.games
        if self.rng.randint(0, DTraining.EXPLORATION_RANGE) < epsilon:
            return DAction(self.rng.randrange(DTraining.ACTION_COUNT))
        # PyTorch need not record calculations for learning while choosing a move.
        # https://docs.pytorch.org/docs/stable/generated/torch.no_grad.html
        with torch.no_grad():
            # argmax finds the best action's index; item() returns a Python number.
            return DAction(self.model(torch.as_tensor(state)).argmax().item())

    def learn(self, state, action, result, next_state):
        transition = (state, int(action), result.reward, next_state, result.done)
        # Wrap each value as a one-item batch; * passes the five batches separately.
        self.trainer.train(*[(value,) for value in transition])
        self.memory.append(transition)

    def finish_game(self):
        self.games += 1
        batch = self.rng.sample(list(self.memory), min(len(self.memory), DTraining.BATCH_SIZE))
        # zip(*batch) groups past moves by field: all states, all actions, etc.
        # https://docs.python.org/3/library/functions.html#zip
        self.trainer.train(*zip(*batch))
