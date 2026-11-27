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
        # SnakeGame() calls __init__; self holds that particular game's attributes.
        # https://docs.python.org/3/tutorial/classes.html#class-objects
        if columns < 2 * DGame.INITIAL_LENGTH or rows < 2:
            raise ValueError("The board is too small for the initial snake")
        self.columns = columns
        self.rows = rows
        self.rng = rng if rng is not None else random.Random()
        self.reset()

    def reset(self):
        # // divides and rounds down, placing the head in a whole grid cell.
        head = Point(self.columns // 2, self.rows // 2)
        # A list comprehension builds the body from head to tail.
        # https://docs.python.org/3/tutorial/datastructures.html#list-comprehensions
        self.snake = [Point(head.x - offset, head.y)
                      for offset in range(DGame.INITIAL_LENGTH)]
        self.direction = DDirection.RIGHT
        self.score = 0
        self.steps = 0
        self.done = False
        self.won = False
        self.food = self._place_food()

    def snapshot(self):
        # Copy the mutable body list into a tuple so later moves cannot change it.
        return GameState(self.columns, self.rows, tuple(self.snake),
                         self.direction, self.food, self.score, self.done, self.won)

    def _place_food(self):
        # Set membership efficiently checks whether a cell already holds the snake.
        # https://docs.python.org/3/library/stdtypes.html#set-types-set-frozenset
        occupied = set(self.snake)
        free = [Point(x, y) for y in range(self.rows)
                for x in range(self.columns) if Point(x, y) not in occupied]
        # A full board is a win, rather than recursive food placement forever.
        return self.rng.choice(free) if free else None

    def next_point(self, direction):
        # Unpack the direction's (horizontal, vertical) movement into two variables.
        dx, dy = DGame.OFFSETS[direction]
        head = self.snake[0]
        return Point(head.x + dx, head.y + dy)

    def is_collision(self, point):
        # [1:] slices off the head; the remaining cells are the body and tail.
        return (not 0 <= point.x < self.columns
                or not 0 <= point.y < self.rows
                or point in self.snake[1:])

    def step(self, action=DAction.STRAIGHT, *, starvation=True):
        if self.done:
            raise RuntimeError("Reset the finished game before stepping again")
        action = DAction(action)
        turn = {DAction.STRAIGHT: 0, DAction.RIGHT: 1, DAction.LEFT: -1}[action]
        # % wraps clockwise direction numbers back into the range 0 to 3.
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
            # Removing the tail keeps the length fixed; eating skips this removal.
            self.snake.pop()
        return StepResult(reward, self.done, self.score)

    def steer(self, direction):
        """Resolve an absolute human direction; ignore immediate reversals."""
        turn = (direction - self.direction) % len(DDirection)
        return {0: DAction.STRAIGHT, 1: DAction.RIGHT,
                2: DAction.STRAIGHT, 3: DAction.LEFT}[turn]
