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
        self.rng = rng if rng is not None else random.Random()
        self.games = 0
        self.memory = deque(maxlen=DTraining.MEMORY_SIZE)
        self.model = QNetwork()
        self.trainer = QTrainer(self.model)

    @staticmethod
    def observe(game):
        direction = game.direction
        danger = [game.is_collision(game.next_point(DDirection((direction + turn) % len(DDirection))))
                  for turn in (0, 1, -1)]
        head, food = game.snake[0], game.food
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
        epsilon = DTraining.EXPLORATION_GAMES - self.games
        if self.rng.randint(0, DTraining.EXPLORATION_RANGE) < epsilon:
            return DAction(self.rng.randrange(DTraining.ACTION_COUNT))
        with torch.no_grad():
            return DAction(self.model(torch.as_tensor(state)).argmax().item())

    def learn(self, state, action, result, next_state):
        transition = (state, int(action), result.reward, next_state, result.done)
        self.trainer.train(*[(value,) for value in transition])
        self.memory.append(transition)

    def finish_game(self):
        self.games += 1
        batch = self.rng.sample(list(self.memory), min(len(self.memory), DTraining.BATCH_SIZE))
        self.trainer.train(*zip(*batch))
