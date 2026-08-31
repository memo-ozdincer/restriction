import unittest

from scripts.project.analyze_c3_matched_control import decision_classification


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
        result = decision_classification(overall(100, 111, 0.2))
        self.assertEqual(result["classification"], "material_training_support_for_blocking")
        result = decision_classification(overall(100, 111, -0.1))
        self.assertEqual(result["classification"], "mixed_or_intermediate_training_result")

    def test_practical_null_uses_registered_five_percent_band(self):
        result = decision_classification(overall(100, 105, 0.2))
        self.assertEqual(result["classification"], "practically_null_training_mode_difference")


if __name__ == "__main__":
    unittest.main()
