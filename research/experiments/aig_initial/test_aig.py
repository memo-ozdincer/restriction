import unittest
from aig import evaluate, panel, verify, random_prefix
import random


class Tests(unittest.TestCase):
    def test_witnesses(self):
        for task in panel():
            self.assertEqual(verify(task, **task["witness"])["reward"], 1, task["name"])

    def test_exhaustive(self):
        self.assertEqual(evaluate(2, [[2, 4]], [6, 7]), [8, 7])

    def test_forward_reference(self):
        with self.assertRaises(ValueError):
            evaluate(2, [[2, 6]], [6])

    def test_budget_and_prefix(self):
        task = panel()[0]
        witness = task["witness"]
        self.assertEqual(verify(task, witness["gates"][1:], witness["outputs"],
                                witness["gates"][:1])["reward"], 1)
        self.assertEqual(verify(dict(task, budget=2), **witness)["reward"], 0)

    def test_random(self):
        gates = random_prefix(4, 10, random.Random(42))
        self.assertEqual(len(evaluate(4, gates, [28])), 1)


if __name__ == "__main__":
    unittest.main()
