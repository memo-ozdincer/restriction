import unittest
from collections import Counter

from scripts.project.analyze_evaluation_accumulation import (
    expected_distinct_from_proposals,
    pass_at_n,
    representation_key,
    safe_wilcoxon,
)


class EvaluationAccumulationTests(unittest.TestCase):
    def test_expected_distinct_at_full_budget_is_observed_coverage(self):
        self.assertEqual(expected_distinct_from_proposals(Counter({"a": 3, "b": 1}), 8, 8), 2.0)

    def test_expected_distinct_counts_incorrect_proposals_in_denominator(self):
        self.assertAlmostEqual(
            expected_distinct_from_proposals(Counter({"a": 2}), 4, 1),
            0.5,
        )

    def test_expected_distinct_rejects_excess_draws(self):
        with self.assertRaises(ValueError):
            expected_distinct_from_proposals(Counter({"a": 1}), 2, 3)

    def test_pass_at_n_boundaries(self):
        self.assertEqual(pass_at_n(0, 8, 8), 0.0)
        self.assertEqual(pass_at_n(1, 8, 8), 1.0)
        self.assertAlmostEqual(pass_at_n(2, 8, 1), 0.25)

    def test_all_zero_wilcoxon_is_one(self):
        self.assertEqual(safe_wilcoxon([0.0, 0.0]), 1.0)

    def test_wilcoxon_preserves_zero_pairs_with_pratt_convention(self):
        self.assertAlmostEqual(safe_wilcoxon([-1.0, 0.0, 1.0, 1.0]), 0.5637028616507731)

    def test_coarse_representations_discard_only_their_registered_structure(self):
        proposal = {"heads": ("have", "norm_num", "have"), "exact": "proof-id"}
        self.assertEqual(representation_key(proposal, "first_head"), ("have",))
        self.assertEqual(
            representation_key(proposal, "unordered_head_set"),
            ("have", "norm_num"),
        )
        self.assertEqual(
            representation_key(proposal, "head_multiset"),
            (("have", 2), ("norm_num", 1)),
        )
        self.assertEqual(representation_key(proposal, "exact_proof"), "proof-id")


if __name__ == "__main__":
    unittest.main()
