import numpy as np
import torch
from torch import nn

from simplesnake.constants.DTraining import DTraining


class QTrainer:
    """One-step Q-learning, with detached Bellman targets and batched replay."""

    def __init__(self, model):
        self.model = model
        self.optimizer = torch.optim.Adam(model.parameters(), lr=DTraining.LEARNING_RATE)
        self.loss = nn.MSELoss()

    def train(self, states, actions, rewards, next_states, dones):
        # Tensors are numeric arrays; each row represents one remembered move.
        # https://docs.pytorch.org/docs/stable/generated/torch.as_tensor.html
        states = torch.as_tensor(np.asarray(states), dtype=torch.float32)
        next_states = torch.as_tensor(np.asarray(next_states), dtype=torch.float32)
        actions = torch.as_tensor(actions, dtype=torch.long)
        rewards = torch.as_tensor(rewards, dtype=torch.float32)
        dones = torch.as_tensor(dones, dtype=torch.bool)
        predictions = self.model(states)
        # Targets are fixed answers for this update; only predictions track gradients.
        with torch.no_grad():
            targets = predictions.clone()
            # dim=1 finds the best action within each row of next-state predictions.
            future = self.model(next_states).max(dim=1).values
            # ~ flips boolean dones: a finished game has no future reward.
            values = rewards + DTraining.DISCOUNT * future * (~dones)
            # Pair row and action indices to update only the action actually taken.
            targets[torch.arange(len(actions)), actions] = values
        # Clear old gradients, measure error, compute new gradients, then adjust weights.
        # https://docs.pytorch.org/tutorials/beginner/basics/optimization_tutorial.html
        self.optimizer.zero_grad()
        error = self.loss(predictions, targets)
        error.backward()
        self.optimizer.step()
        return error.item()
