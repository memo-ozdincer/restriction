import unittest
from collections import Counter

from scripts.project.analyze_evaluation_accumulation import (
    expected_distinct_from_proposals,
    pass_at_n,
    representation_key,
    safe_wilcoxon,
    validate_finalized_evaluation_metrics,
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

    def test_finalized_evaluation_metrics_are_fail_closed(self):
        metrics = {
            "condition": "c3_matched_control",
            "classification": "registered_evaluation_128",
            "completion_marker": "upstream_post_completion_stop_sentinel",
            "registered_proposals": 256,
            "physical_proposals": 260,
            "excluded_padding_proposals": 4,
            "proof_log_sha256": "proof-hash",
            "evaluation_parquet_sha256": "parquet-hash",
        }
        kwargs = {
            "expected_condition": "c3_matched_control",
            "num_samples": 128,
            "expected_proposals": 256,
            "physical_proposals": 260,
            "proof_log_sha256": "proof-hash",
            "evaluation_parquet_sha256": "parquet-hash",
        }
        validate_finalized_evaluation_metrics(metrics, **kwargs)
        for key, bad_value in (
            ("condition", "c3_hardblock_restart"),
            ("classification", "registered_evaluation_32"),
            ("completion_marker", "incomplete"),
            ("registered_proposals", 255),
            ("physical_proposals", 259),
            ("proof_log_sha256", "wrong"),
            ("evaluation_parquet_sha256", "wrong"),
        ):
            with self.subTest(key=key), self.assertRaises(ValueError):
                validate_finalized_evaluation_metrics({**metrics, key: bad_value}, **kwargs)


if __name__ == "__main__":
    unittest.main()
