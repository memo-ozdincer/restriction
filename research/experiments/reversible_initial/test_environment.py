import unittest
from collections import Counter
import random
from environment import (
    identity, gate_library, gate_permutation, execute, verify, distances, random_start,
)


class Tests(unittest.TestCase):
    def test_gates(self):
        self.assertEqual(len(gate_library(3)), 12)
        self.assertEqual(len(gate_library(4)), 32)
        for gate in gate_library(4):
            p = gate_permutation(4, gate)
            self.assertEqual(sorted(p), list(identity(4)))
            self.assertEqual(execute(4, [gate, gate]), identity(4))

    def test_all_three_bit_distances(self):
        self.assertEqual(Counter(distances(3).values()),
                         dict(enumerate([1, 12, 102, 625, 2780, 8921, 17049, 10253, 577])))

    def test_start_changes_task(self):
        rng = random.Random(42)
        start = random_start(4, rng)
        self.assertNotEqual(start, identity(4))
        actions = [(2, (0, 1))]
        target = execute(4, actions, start)
        self.assertEqual(verify(4, target, actions, 1, start)["reward"], 1)
        self.assertEqual(verify(4, target, actions, 1)["reward"], 0)
        self.assertEqual(verify(4, target, actions, 0, start)["reward"], 0)

    def test_invalid(self):
        with self.assertRaises(ValueError):
            execute(4, [(1, (1,))])
        with self.assertRaises(ValueError):
            execute(4, [], [0]*16)


if __name__ == "__main__":
    unittest.main()
