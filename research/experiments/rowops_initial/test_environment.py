import unittest
from collections import Counter
from environment import ACTIONS, IDENTITY, TARGET, BUDGET, step, execute, distances, witness, verify, starts


class Tests(unittest.TestCase):
    def test_calibration(self):
        depth, parents = distances()
        self.assertEqual(Counter(depth.values()), dict(enumerate([1, 15, 135, 787, 3000, 5522, 1764, 8])))
        self.assertEqual(depth[TARGET], BUDGET)
        self.assertEqual(verify(IDENTITY, witness(IDENTITY, TARGET, parents))["reward"], 1)

    def test_inverse_actions(self):
        for i, j, k in ACTIONS:
            inverse = (i, j, k if i == j else 3-k)
            self.assertEqual(execute(TARGET, [(i, j, k), inverse]), TARGET)

    def test_reset_feasible(self):
        self.assertEqual([d for m, _, _, d in starts() if m == "near"], [1,2,3,4])
        self.assertTrue(all(0 < d <= BUDGET for _, _, _, d in starts()))

    def test_invalid(self):
        with self.assertRaises(ValueError):
            step(IDENTITY, (0,0,1))
        with self.assertRaises(ValueError):
            step(IDENTITY, (3,0,1))

if __name__ == "__main__":
    unittest.main()
