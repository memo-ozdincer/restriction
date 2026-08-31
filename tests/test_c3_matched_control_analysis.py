import unittest

from scripts.project.analyze_c3_matched_control import (
    decision_classification,
    validate_intervention_invariants,
)


def overall(control_modes, c3_modes, rarefaction_delta):
    return {
        "control": {"correct_mode_coverage": control_modes},
        "c3": {"correct_mode_coverage": c3_modes},
        "correct_draw_rarefaction": {
            "16": {"mean_delta_c3_minus_control": rarefaction_delta}
        },
    }


class C3MatchedControlAnalysisTests(unittest.TestCase):
    def test_material_support_requires_coverage_and_rarefaction(self):
        result = decision_classification(overall(100, 110, 0.2))
        self.assertEqual(result["classification"], "material_training_support_for_blocking")
        self.assertEqual(
            result["blocking_attribution_status"],
            "material_training_support_pending_heldout_control",
        )
        result = decision_classification(overall(100, 111, -0.1))
        self.assertEqual(result["classification"], "mixed_or_intermediate_training_result")

    def test_practical_null_uses_registered_five_percent_band(self):
        result = decision_classification(overall(100, 105, 0.2))
        self.assertEqual(result["classification"], "practically_null_training_mode_difference")

    def test_control_matching_or_exceeding_c3_is_explicit(self):
        for c3_modes, classification in (
            (100, "practically_null_training_mode_difference"),
            (96, "practically_null_training_mode_difference"),
            (94, "training_control_exceeds_c3"),
        ):
            with self.subTest(c3_modes=c3_modes):
                result = decision_classification(overall(100, c3_modes, 0.2))
                self.assertEqual(result["classification"], classification)
                self.assertEqual(
                    result["blocking_attribution_status"],
                    "not_supported_control_matches_or_exceeds_c3",
                )

    def test_intervention_invariants_reject_contaminated_control(self):
        control = {
            "condition": "c3_matched_control",
            "blocked_correct_zero_advantage": 0,
            "physical_blocked_correct_zero_advantage": 0,
            "skipped_all_blocked_prompts": 0,
            "archive_sha256": None,
        }
        c3 = {"condition": "c3_hardblock_restart", "archive_sha256": "archive-hash"}
        validate_intervention_invariants(control, c3, "archive-hash")
        for key, bad_value in (
            ("blocked_correct_zero_advantage", 1),
            ("physical_blocked_correct_zero_advantage", 1),
            ("skipped_all_blocked_prompts", 1),
            ("archive_sha256", "archive-hash"),
        ):
            with self.subTest(key=key), self.assertRaises(ValueError):
                validate_intervention_invariants(
                    {**control, key: bad_value}, c3, "archive-hash"
                )


if __name__ == "__main__":
    unittest.main()
