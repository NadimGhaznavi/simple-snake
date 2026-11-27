import random

from simplesnake.constants.DGame import DAction, DDirection, DGame
from simplesnake.entity.GameState import GameState
from simplesnake.entity.Point import Point
from simplesnake.entity.StepResult import StepResult


class SnakeGame:
    """Grid-based Snake rules; coordinates are cells, not display pixels.

    As in Loeber's game, the tail still occupies its cell during collision
    checks, and the AI's time limit counts total steps in the episode.
    """

    def __init__(self, columns=DGame.COLUMNS, rows=DGame.ROWS, *, rng=None):
        if columns < 2 * DGame.INITIAL_LENGTH or rows < 2:
            raise ValueError("The board is too small for the initial snake")
        self.columns = columns
        self.rows = rows
        self.rng = rng if rng is not None else random.Random()
        self.reset()

    def reset(self):
        head = Point(self.columns // 2, self.rows // 2)
        self.snake = [Point(head.x - offset, head.y)
                      for offset in range(DGame.INITIAL_LENGTH)]
        self.direction = DDirection.RIGHT
        self.score = 0
        self.steps = 0
        self.done = False
        self.won = False
        self.food = self._place_food()

    def snapshot(self):
        return GameState(self.columns, self.rows, tuple(self.snake),
                         self.direction, self.food, self.score, self.done, self.won)

    def _place_food(self):
        occupied = set(self.snake)
        free = [Point(x, y) for y in range(self.rows)
                for x in range(self.columns) if Point(x, y) not in occupied]
        # A full board is a win, rather than recursive food placement forever.
        return self.rng.choice(free) if free else None

    def next_point(self, direction):
        dx, dy = DGame.OFFSETS[direction]
        head = self.snake[0]
        return Point(head.x + dx, head.y + dy)

    def is_collision(self, point):
        return (not 0 <= point.x < self.columns
                or not 0 <= point.y < self.rows
                or point in self.snake[1:])

    def step(self, action=DAction.STRAIGHT, *, starvation=True):
        if self.done:
            raise RuntimeError("Reset the finished game before stepping again")
        action = DAction(action)
        turn = {DAction.STRAIGHT: 0, DAction.RIGHT: 1, DAction.LEFT: -1}[action]
        self.direction = DDirection((self.direction + turn) % len(DDirection))
        head = self.next_point(self.direction)
        self.steps += 1
        collision = self.is_collision(head)
        self.snake.insert(0, head)
        if collision or (starvation and self.steps > DGame.STARVATION_FACTOR * len(self.snake)):
            self.done = True
            return StepResult(DGame.DEATH_REWARD, True, self.score)
        reward = DGame.STEP_REWARD
        if head == self.food:
            self.score += 1
            reward = DGame.FOOD_REWARD
            self.food = self._place_food()
            self.won = self.food is None
            self.done = self.won
        else:
            self.snake.pop()
        return StepResult(reward, self.done, self.score)

    def steer(self, direction):
        """Resolve an absolute human direction; ignore immediate reversals."""
        turn = (direction - self.direction) % len(DDirection)
        return {0: DAction.STRAIGHT, 1: DAction.RIGHT,
                2: DAction.STRAIGHT, 3: DAction.LEFT}[turn]
