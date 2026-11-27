import random
import unittest

from simplesnake.activity.SnakeGame import SnakeGame
from simplesnake.constants.DGame import DAction, DDirection, DGame
from simplesnake.entity.Point import Point


class GameTests(unittest.TestCase):
    def setUp(self):
        self.game = SnakeGame(rng=random.Random(7))

    def test_reset_and_snapshot_are_independent(self):
        before = self.game.snapshot()
        self.game.food = Point(0, 0)
        self.game.step()
        self.assertEqual(before.snake[0], Point(16, 12))
        self.assertEqual(self.game.snake[0], Point(17, 12))
        self.assertEqual(len(before.snake), DGame.INITIAL_LENGTH)
        self.assertNotIn(before.food, before.snake)

    def test_relative_turns_for_all_directions(self):
        for direction in DDirection:
            for action, turn in ((DAction.STRAIGHT, 0), (DAction.RIGHT, 1), (DAction.LEFT, -1)):
                with self.subTest(direction=direction, action=action):
                    self.game.reset()
                    self.game.snake = [Point(10, 10)]
                    self.game.direction = direction
                    expected = DDirection((direction + turn) % len(DDirection))
                    point = self.game.next_point(expected)
                    self.game.step(action)
                    self.assertEqual(self.game.direction, expected)
                    self.assertEqual(self.game.snake[0], point)

    def test_food_grows_snake_and_rewards(self):
        self.game.food = self.game.next_point(self.game.direction)
        result = self.game.step()
        self.assertEqual(result.reward, DGame.FOOD_REWARD)
        self.assertEqual(result.score, 1)
        self.assertEqual(len(self.game.snake), DGame.INITIAL_LENGTH + 1)
        self.assertNotIn(self.game.food, self.game.snake)

    def test_wall_collision_and_finished_game_contract(self):
        self.game.snake = [Point(self.game.columns - 1, 0)]
        result = self.game.step()
        self.assertTrue(result.done)
        self.assertEqual(result.reward, DGame.DEATH_REWARD)
        with self.assertRaises(RuntimeError):
            self.game.step()
        self.game.reset()
        self.assertFalse(self.game.done)

    def test_tail_cell_counts_as_collision_like_reference(self):
        self.game.snake = [Point(2, 2), Point(2, 3), Point(3, 3), Point(3, 2)]
        self.assertTrue(self.game.step().done)

    def test_starvation_is_ai_only(self):
        for enabled in (True, False):
            self.game.reset()
            self.game.steps = DGame.STARVATION_FACTOR * (len(self.game.snake) + 1)
            self.assertEqual(self.game.step(starvation=enabled).done, enabled)

    def test_absolute_steering_ignores_reversal(self):
        self.assertEqual(self.game.steer(DDirection.UP), DAction.LEFT)
        self.assertEqual(self.game.steer(DDirection.DOWN), DAction.RIGHT)
        self.assertEqual(self.game.steer(DDirection.LEFT), DAction.STRAIGHT)

    def test_full_board_is_terminal_win(self):
        game = SnakeGame(6, 2)
        head, food = Point(4, 0), Point(5, 0)
        game.snake = [head] + [Point(x, y) for y in range(2) for x in range(6)
                               if Point(x, y) not in (head, food)]
        game.food = food
        result = game.step()
        self.assertTrue(result.done)
        self.assertTrue(game.won)
        self.assertIsNone(game.food)
        self.assertEqual(len(game.snake), 12)
        self.assertEqual(result.reward, DGame.FOOD_REWARD)

    def test_invalid_board_and_action_fail(self):
        with self.assertRaises(ValueError):
            SnakeGame(2, 2)
        with self.assertRaises(ValueError):
            self.game.step(100)
