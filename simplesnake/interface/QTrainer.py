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
        states = torch.as_tensor(np.asarray(states), dtype=torch.float32)
        next_states = torch.as_tensor(np.asarray(next_states), dtype=torch.float32)
        actions = torch.as_tensor(actions, dtype=torch.long)
        rewards = torch.as_tensor(rewards, dtype=torch.float32)
        dones = torch.as_tensor(dones, dtype=torch.bool)
        predictions = self.model(states)
        with torch.no_grad():
            targets = predictions.clone()
            future = self.model(next_states).max(dim=1).values
            values = rewards + DTraining.DISCOUNT * future * (~dones)
            targets[torch.arange(len(actions)), actions] = values
        self.optimizer.zero_grad()
        error = self.loss(predictions, targets)
        error.backward()
        self.optimizer.step()
        return error.item()
