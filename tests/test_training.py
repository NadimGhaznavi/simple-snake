from pathlib import Path
import random
import tempfile
import unittest

import numpy as np
import torch

from simplesnake.activity.Agent import Agent
from simplesnake.activity.SnakeGame import SnakeGame
from simplesnake.activity.TrainingSession import TrainingSession
from simplesnake.constants.DGame import DAction, DDirection
from simplesnake.constants.DTraining import DTraining
from simplesnake.entity.Point import Point
from simplesnake.interface.QNetwork import QNetwork
from simplesnake.interface.QTrainer import QTrainer


torch.set_num_threads(DTraining.CPU_THREADS)


class TrainingTests(unittest.TestCase):
    def test_observation_matches_reference_order(self):
        game = SnakeGame()
        game.food = Point(0, 0)
        np.testing.assert_array_equal(Agent.observe(game),
                                     [0, 0, 0, 0, 1, 0, 0, 1, 0, 1, 0])
        game.snake = [Point(game.columns - 1, 5)]
        self.assertEqual(Agent.observe(game)[0], 1)
        game.direction = DDirection.UP
        self.assertEqual(Agent.observe(game)[1], 1)
        game.direction = DDirection.DOWN
        self.assertEqual(Agent.observe(game)[2], 1)

    def test_terminal_full_board_can_be_observed(self):
        game = SnakeGame()
        game.food = None
        observation = Agent.observe(game)
        self.assertEqual(len(observation), DTraining.INPUT_SIZE)
        np.testing.assert_array_equal(observation[-4:], [0, 0, 0, 0])

    def test_network_dimensions_and_greedy_action(self):
        agent = Agent(rng=random.Random(3))
        # Disable exploration so the action must match the network's highest value.
        agent.games = DTraining.EXPLORATION_GAMES
        state = Agent.observe(SnakeGame())
        self.assertEqual(agent.model(torch.as_tensor(state)).shape, (DTraining.ACTION_COUNT,))
        self.assertEqual(agent.choose_action(state), agent.model(torch.as_tensor(state)).argmax().item())

    def test_bellman_target_is_detached_for_terminal_and_live_batch(self):
        torch.manual_seed(2)
        model = QNetwork()
        trainer = QTrainer(model)
        states = np.ones((2, DTraining.INPUT_SIZE), dtype=np.float32)
        next_states = states * 2
        actions, rewards, dones = [0, 2], [10.0, -10.0], [False, True]
        with torch.no_grad():
            targets = model(torch.as_tensor(states)).clone()
            targets[0, 0] = rewards[0] + DTraining.DISCOUNT * model(torch.as_tensor(next_states))[0].max()
            targets[1, 2] = rewards[1]
        expected = torch.mean((model(torch.as_tensor(states)) - targets) ** 2)
        expected.backward()
        # Compare actual gradients to an independently calculated learning target.
        expected_gradients = [p.grad.clone() for p in model.parameters()]
        trainer.optimizer.zero_grad()
        loss = trainer.train(states, actions, rewards, next_states, dones)
        self.assertAlmostEqual(loss, expected.item(), places=5)
        for parameter, gradient in zip(model.parameters(), expected_gradients):
            torch.testing.assert_close(parameter.grad, gradient)

    def test_session_replay_checkpoint_and_next_episode(self):
        # TemporaryDirectory removes checkpoints automatically when the block exits.
        # https://docs.python.org/3/library/tempfile.html#tempfile.TemporaryDirectory
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'best-model.pth'
            session = TrainingSession(path)
            # Replace random/learned decisions with a predictable straight-line game.
            session.agent.choose_action = lambda state: DAction.STRAIGHT
            session.game.food = session.game.next_point(session.game.direction)
            first = session.step()
            self.assertEqual(first.game.score, 1)
            while not session.game.done:
                terminal = session.step()
            self.assertEqual(terminal.completed_score, 1)
            self.assertEqual(terminal.games, 1)
            self.assertEqual(terminal.record, 1)
            self.assertEqual(terminal.mean, 1)
            self.assertEqual(len(session.agent.memory), session.game.steps)
            restored = QNetwork()
            restored.load_state_dict(torch.load(path, weights_only=True))
            self.assertFalse(path.with_suffix('.pth.tmp').exists())
            next_frame = session.step()
            self.assertFalse(next_frame.game.done)
            self.assertIsNone(next_frame.completed_score)

    def test_checkpoint_failure_is_reported(self):
        with tempfile.TemporaryDirectory() as directory:
            blocked = Path(directory) / 'file'
            blocked.write_text('not a directory')
            with self.assertRaises(OSError):
                QNetwork().save(blocked / 'model.pth')
