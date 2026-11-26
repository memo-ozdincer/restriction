import unittest
from environment import GOAL, distances, move, verify, execute


class TestEnvironment(unittest.TestCase):
    def test_boundaries(self):
        with self.assertRaises(ValueError):
            move(GOAL, "D")
        with self.assertRaises(ValueError):
            move(GOAL, "R")

    def test_reverse(self):
        self.assertEqual(execute(GOAL, ["U", "L", "R", "D"]), GOAL)
        self.assertEqual(verify(move(GOAL, "U"), ["D"], 1)["reward"], 1)
        self.assertEqual(verify(move(GOAL, "U"), ["D"], 0)["reward"], 0)
        self.assertEqual(verify(move(GOAL, "U"), [], 1)["reward"], 0)

    def test_complete_distances(self):
        depth = distances()
        self.assertEqual(len(depth), 181440)
        self.assertEqual(max(depth.values()), 31)
        self.assertEqual(depth[GOAL], 0)


if __name__ == "__main__":
    unittest.main()
