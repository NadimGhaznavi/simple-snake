from simplesnake.activity.Agent import Agent
from simplesnake.activity.SnakeGame import SnakeGame
from simplesnake.entity.TrainingProgress import TrainingProgress


class TrainingSession:
    """Advance one move at a time; Qt owns scheduling, not the training loop."""

    def __init__(self, model_path):
        self.game = SnakeGame()
        self.agent = Agent()
        self.model_path = model_path
        self.record = 0
        self.total = 0

    def step(self):
        if self.game.done:
            self.game.reset()
        state = self.agent.observe(self.game)
        action = self.agent.choose_action(state)
        result = self.game.step(action)
        self.agent.learn(state, action, result, self.agent.observe(self.game))
        if result.done:
            self.agent.finish_game()
            self.total += result.score
            if result.score > self.record:
                self.agent.model.save(self.model_path)
                self.record = result.score
        return TrainingProgress(
            self.game.snapshot(), self.agent.games, self.record,
            self.total / self.agent.games if self.agent.games else 0.0,
            result.score if result.done else None,
        )
