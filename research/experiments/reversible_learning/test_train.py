import unittest
import numpy as np
from train import make_environment, sample_starts, rollout, HORIZON, ACTIONS, WIDTH
from environment import execute, gate_library, identity


class Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.env = make_environment()

    def test_transition(self):
        transitions, features, root, _, _ = self.env
        gates = gate_library(3)
        state = root
        actions = [0, 4, 9, 11]
        for a in actions:
            state = transitions[state, a]
        actual = tuple(features[state].reshape(WIDTH, WIDTH).argmax(axis=1))
        self.assertEqual(actual, execute(3, [gates[a] for a in actions], identity(3)))

    def test_reset(self):
        transitions, _, root, goal, _ = self.env
        rng = np.random.default_rng(42)
        states = sample_starts("near", rng, transitions, root, goal, 1000, True)
        self.assertFalse(np.any(states == goal))
        self.assertEqual(len(states), 1000)

    def test_terminal_only(self):
        transitions, features, root, goal, _ = self.env
        weights = np.zeros((WIDTH*WIDTH, ACTIONS), dtype=np.float32)
        hits, steps = rollout(weights, np.full(10, goal), transitions, features, goal,
                              np.random.default_rng(42))
        self.assertEqual((hits, steps), (10, 0))


if __name__ == "__main__":
    unittest.main()
