from dataclasses import dataclass


@dataclass(frozen=True)
class StepResult:
    reward: int
    done: bool
    score: int
