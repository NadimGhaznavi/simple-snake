from dataclasses import dataclass


@dataclass(frozen=True)
class StepResult:
    # One move's feedback: the AI's reward, whether play ended, and the score.
    reward: int
    done: bool
    score: int
