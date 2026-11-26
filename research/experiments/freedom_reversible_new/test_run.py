import unittest
import numpy as np
from run import make_environment, build_distributions, hitting_probability, rollout, ACTIONS, WIDTH


class TestExperiment(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.env = make_environment()
        cls.p, cls.gd, cls.rd = build_distributions(cls.env[0], cls.env[2], cls.env[3])

    def test_reset_distributions_and_same_distance(self):
        goal = self.env[3]
        for p in self.p.values():
            self.assertAlmostEqual(p.sum(), 1.0)
            self.assertEqual(p[goal], 0)
        self.assertEqual(np.count_nonzero(self.p["equal_distance"]), 577)
        self.assertTrue(np.all(self.gd[self.p["equal_distance"] > 0] == 8))
        for d in range(1, 9):
            self.assertAlmostEqual(self.p["balanced_shell"][self.gd == d].sum(), 1/8)

    def test_exact_random_goal_probability(self):
        transitions, _, root, goal, _ = self.env
        probs = np.full((len(transitions), ACTIONS), 1/ACTIONS)
        hit = hitting_probability(probs, transitions, goal, 8)
        self.assertAlmostEqual(hit[root], 0.0000014466, places=10)
        self.assertAlmostEqual(float(self.p["goal_walk4"] @ hit), .03651645, places=8)

    def test_horizon_and_no_already_solved_reward(self):
        transitions, features, root, goal, _ = self.env
        weights = np.zeros((WIDTH*WIDTH, ACTIONS), dtype=np.float32)
        starts = np.full(128, root)
        hit, count = rollout(weights, starts, transitions, features, goal,
                             np.random.default_rng(42), 7)
        self.assertEqual(hit, 0)
        self.assertEqual(count, 128*7)


if __name__ == "__main__":
    unittest.main()
