import itertools
import random
import unittest
from environment import OPTIMUM, WITNESSES, case, execute, verify


class Tests(unittest.TestCase):
    def test_witnesses(self):
        for n, budget in OPTIMUM.items():
            self.assertEqual(verify(n, WITNESSES[n], budget)["reward"], 1)
            self.assertEqual(verify(n, WITNESSES[n], budget-1)["reward"], 0)

    def test_exact_state(self):
        rng = random.Random(42)
        for n in (3, 6, 9):
            comparators = list(itertools.combinations(range(n), 2))
            actions = [rng.choice(comparators) for _ in range(15)]
            rows = list(itertools.product((0, 1), repeat=n))
            for i, j in actions:
                rows = [row[:i] + (min(row[i], row[j]),) +
                        row[i+1:j] + (max(row[i], row[j]),) + row[j+1:] for row in rows]
            expected = sum(1 << int("".join(map(str, row)), 2) for row in set(rows))
            self.assertEqual(execute(n, actions), expected)

    def test_reset_controls(self):
        for n, budget in OPTIMUM.items():
            for condition in ("random", "known"):
                state, _ = case(n, condition)
                self.assertEqual(verify(n, [], budget, state)["reward"], 0)
                self.assertEqual(verify(n, WITNESSES[n], budget, state)["reward"], 1)
            state, _ = case(n, "known")
            self.assertEqual(verify(n, WITNESSES[n][-3:], 3, state)["reward"], 1)


if __name__ == "__main__":
    unittest.main()
