import unittest
from collections import Counter

from scripts.project.analyze_training_dynamics import effective_modes, expected_rarefied_modes


class TrainingDynamicsTests(unittest.TestCase):
    def test_rarefaction_for_one_mode(self):
        counts = Counter({"a": 4})
        self.assertEqual(expected_rarefied_modes(counts, 1), 1.0)
        self.assertEqual(expected_rarefied_modes(counts, 4), 1.0)

    def test_rarefaction_for_two_balanced_modes(self):
        counts = Counter({"a": 2, "b": 2})
        self.assertAlmostEqual(expected_rarefied_modes(counts, 2), 5 / 3)
        self.assertEqual(effective_modes(counts), 2.0)

    def test_rarefaction_rejects_too_many_draws(self):
        with self.assertRaises(ValueError):
            expected_rarefied_modes(Counter({"a": 1}), 2)


if __name__ == "__main__":
    unittest.main()
