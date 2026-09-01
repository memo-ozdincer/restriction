import unittest
from collections import Counter

from scripts.project.analyze_c5_training import (
    decision_classification,
    dominant_mode_panel,
    paired_metrics,
    validate_intervention_invariants,
)
from verl.lean.mode_archive import ModeArchive


def theorem(correct: int, modes: dict[str, int]) -> dict:
    return {
        "correct": correct,
        "blocked": 0,
        "modes": Counter(modes),
        "exact": Counter(modes),
        "examples": {},
    }


class C5TrainingAnalysisTests(unittest.TestCase):
    def test_paired_metrics_uses_c5_minus_c3_direction(self):
        c3 = {"x": theorem(4, {"a": 4})}
        c5 = {"x": theorem(4, {"a": 2, "b": 2})}
        result = paired_metrics(c3, c5, ["x"])
        self.assertEqual(result["mean_delta_c5_minus_c3"]["modes"], 1)
        self.assertLess(result["mean_delta_c5_minus_c3"]["top_mode_share"], 0)
        self.assertGreater(result["mean_delta_c5_minus_c3"]["effective_modes"], 0)

    def test_dominant_panel_measures_archived_mode_suppression(self):
        archive = ModeArchive(
            {**{"x": {"a": 3, "b": 1}}, **{f"pad-{i}": {"a": 3, "b": 1} for i in range(1013)}}
        )
        names = ["x", *(f"pad-{i}" for i in range(1013))]
        c3 = {name: theorem(4, {"a": 4}) for name in names}
        c5 = {name: theorem(4, {"a": 2, "b": 2}) for name in names}
        result = dominant_mode_panel(archive, c3, c5, names)
        self.assertAlmostEqual(
            result["paired_common_solved"][
                "mean_delta_archived_dominant_share_c5_minus_c3"
            ],
            -0.5,
        )

    def test_intervention_invariants_distinguish_c3_and_c5(self):
        common = {
            "archive_sha256": "archive",
            "proposals": 308_960,
            "physical_proposals": 308_992,
        }
        c3 = {
            **common,
            "condition": "c3_hardblock_restart",
            "classification": "registered_full_seed42",
            "blocked_correct_zero_advantage": 10,
        }
        c5 = {
            **common,
            "condition": "c5_reward_reject_restart",
            "classification": "exploratory_full_seed42_h100",
            "blocked_correct": 8,
            "blocked_correct_zero_advantage": 0,
            "blocked_correct_reward_rejected": 8,
            "physical_blocked_correct": 9,
            "physical_blocked_correct_reward_rejected": 9,
        }
        validate_intervention_invariants(c3, c5, "archive")
        with self.assertRaises(ValueError):
            validate_intervention_invariants(
                c3, {**c5, "blocked_correct_reward_rejected": 7}, "archive"
            )

    def test_material_decision_requires_diversity_suppression_and_safety(self):
        overall = {
            "c3": {"correct_rate": 0.70, "correct_mode_coverage": 100},
            "c5": {"correct_rate": 0.66, "correct_mode_coverage": 112},
        }
        rarefaction = {"16": {"relative_delta_c5_minus_c3": 0.06}}
        dominant = {
            "paired_common_solved": {
                "mean_delta_archived_dominant_share_c5_minus_c3": -0.06
            }
        }
        result = decision_classification(overall, rarefaction, dominant)
        self.assertEqual(
            result["classification"], "material_support_for_stronger_exploration"
        )
        unsafe = decision_classification(
            {**overall, "c5": {"correct_rate": 0.60, "correct_mode_coverage": 112}},
            rarefaction,
            dominant,
        )
        self.assertEqual(
            unsafe["classification"],
            "directional_support_with_tradeoffs_or_small_effect",
        )


if __name__ == "__main__":
    unittest.main()
