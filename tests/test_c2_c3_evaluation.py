import unittest

from scripts.project.analyze_c2_c3_evaluation import decision_classification


def accumulation(c2_modes=100, c3_modes=106, c2_correct=500, c3_correct=490):
    return {
        "c2_unlikeliness_2": {
            "128": {"theorems": 10, "observed_prefix": {"correct_mode_coverage": c2_modes, "correct": c2_correct}}
        },
        "c3_hardblock_restart": {
            "128": {"theorems": 10, "observed_prefix": {"correct_mode_coverage": c3_modes, "correct": c3_correct}}
        },
    }


def representations(delta=0.01):
    return {name: {"relative_delta_c3_minus_c2": delta} for name in (
        "first_head", "first_two_heads", "unordered_head_set", "head_multiset",
        "ordered_head_sequence", "exact_proof",
    )}


class C2C3EvaluationTests(unittest.TestCase):
    def test_material_support_requires_representation_robustness(self):
        result = decision_classification(
            accumulation(), {"16": {"relative_delta_c3_minus_c2": 0.06}}, representations()
        )
        self.assertEqual(
            result["classification"],
            "material_heldout_support_for_hard_over_soft_exploration",
        )
        mixed = representations()
        mixed["exact_proof"]["relative_delta_c3_minus_c2"] = -0.01
        result = decision_classification(
            accumulation(), {"16": {"relative_delta_c3_minus_c2": 0.06}}, mixed
        )
        self.assertEqual(result["classification"], "mixed_or_representation_sensitive_heldout_result")

    def test_null_and_soft_superiority_are_explicit(self):
        result = decision_classification(
            accumulation(c3_modes=103),
            {"16": {"relative_delta_c3_minus_c2": 0.02}},
            representations(),
        )
        self.assertEqual(result["classification"], "practically_null_heldout_hard_versus_soft_difference")
        result = decision_classification(
            accumulation(c3_modes=90),
            {"16": {"relative_delta_c3_minus_c2": -0.02}},
            representations(-0.01),
        )
        self.assertEqual(result["classification"], "heldout_soft_unlikeliness_outperforms_hard_blocking")


if __name__ == "__main__":
    unittest.main()
