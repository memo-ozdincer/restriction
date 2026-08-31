import unittest
from collections import Counter

from scripts.project.analyze_training_dynamics import (
    effective_modes,
    expected_rarefied_modes,
    validate_finalized_training_metrics,
)


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

    def test_finalized_training_metrics_are_fail_closed(self):
        metrics = {
            "condition": "c3_matched_control",
            "classification": "registered_full_seed42",
            "completion_marker": "upstream_post_completion_stop_sentinel",
            "proposals": 32,
            "expected_registered_proposals": 32,
            "physical_proposals": 34,
            "excluded_padding_proposals": 2,
            "proof_log_sha256": "proof-hash",
        }
        validate_finalized_training_metrics(
            metrics,
            expected_condition="c3_matched_control",
            expected_proposals=32,
            physical_proposals=34,
            proof_log_sha256="proof-hash",
        )
        for key, bad_value in (
            ("condition", "c1_grpo_default"),
            ("classification", "engineering_smoke"),
            ("completion_marker", "incomplete"),
            ("proposals", 31),
            ("physical_proposals", 33),
            ("proof_log_sha256", "wrong"),
        ):
            with self.subTest(key=key), self.assertRaises(ValueError):
                validate_finalized_training_metrics(
                    {**metrics, key: bad_value},
                    expected_condition="c3_matched_control",
                    expected_proposals=32,
                    physical_proposals=34,
                    proof_log_sha256="proof-hash",
                )


if __name__ == "__main__":
    unittest.main()
