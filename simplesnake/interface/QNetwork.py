from pathlib import Path

import torch
from torch import nn

from simplesnake.constants.DTraining import DTraining


class QNetwork(nn.Module):
    """Loeber's two-layer network, running on CPU on either desktop platform."""

    def __init__(self):
        super().__init__()
        # Assigning layers to self registers their trainable weights with nn.Module.
        # https://docs.pytorch.org/docs/stable/generated/torch.nn.Module.html
        self.linear1 = nn.Linear(DTraining.INPUT_SIZE, DTraining.HIDDEN_SIZE)
        self.linear2 = nn.Linear(DTraining.HIDDEN_SIZE, DTraining.ACTION_COUNT)

    def forward(self, values):
        # model(values) calls forward: features -> hidden layer -> three action values.
        # ReLU replaces negative hidden values with zero.
        # https://docs.pytorch.org/docs/stable/generated/torch.nn.ReLU.html
        return self.linear2(torch.relu(self.linear1(values)))

    def save(self, path: Path):
        path.parent.mkdir(parents=True, exist_ok=True)
        temporary = path.with_suffix(path.suffix + ".tmp")
        try:
            # Save learned weights, then replace the checkpoint only after writing succeeds.
            # https://docs.pytorch.org/tutorials/beginner/saving_loading_models.html
            torch.save(self.state_dict(), temporary)
            temporary.replace(path)
        finally:
            # finally runs on success or failure, cleaning up any unfinished file.
            # https://docs.python.org/3/tutorial/errors.html#defining-clean-up-actions
            temporary.unlink(missing_ok=True)
