from pathlib import Path

import torch
from torch import nn

from simplesnake.constants.DTraining import DTraining


class QNetwork(nn.Module):
    """Loeber's two-layer network, running on CPU on either desktop platform."""

    def __init__(self):
        super().__init__()
        self.linear1 = nn.Linear(DTraining.INPUT_SIZE, DTraining.HIDDEN_SIZE)
        self.linear2 = nn.Linear(DTraining.HIDDEN_SIZE, DTraining.ACTION_COUNT)

    def forward(self, values):
        return self.linear2(torch.relu(self.linear1(values)))

    def save(self, path: Path):
        path.parent.mkdir(parents=True, exist_ok=True)
        temporary = path.with_suffix(path.suffix + ".tmp")
        try:
            torch.save(self.state_dict(), temporary)
            temporary.replace(path)
        finally:
            temporary.unlink(missing_ok=True)
