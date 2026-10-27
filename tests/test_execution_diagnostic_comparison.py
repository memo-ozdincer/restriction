import unittest

from scripts.project.compare_execution_diagnostics import compare, paired_effect
from tests.test_execution_pilot_analysis import bank_rows, records_for


class ExecutionDiagnosticComparisonTests(unittest.TestCase):
    def setUp(self):
        self.bank = [row for row in bank_rows(1, 4, two_prefixes=True)
                     if row["pilot_split"] == "diagnostic"]
        self.by_id = {row["pilot_row_id"]: row for row in self.bank}

    def records(self, root_successes, prefix_successes):
        records = records_for(self.bank)
        for record in records:
            row = self.by_id[record["pilot_row_id"]]
            successes = root_successes if row["condition"] == "root" else prefix_successes
            valid = record["candidate_index"] < successes
            record.update(correct=valid, verdict=valid, lean_complete=valid)
        return records

    def test_large_conditional_gain_with_root_retention_passes_material_screen(self):
        result = compare(self.by_id, {
            "base": self.records(16, 8), "root": self.records(20, 8),
            "practice": self.records(20, 12)})
        screen = result["preregistered_material_screen"]
        self.assertTrue(screen["pass"])
        self.assertFalse(screen["positive_unconditioned_point_effect"])
        self.assertEqual(result["effects"]["prefix"]["practice_minus_root"]["right_minus_left"], 0.125)
        self.assertEqual(result["arms"]["practice"]["registered"]["proposals"], 4 * 3 * 32)
        self.assertIn("not_compositional_OOD", result["classification"])

    def test_conditional_gain_does_not_hide_unconditioned_regression(self):
        result = compare(self.by_id, {
            "base": self.records(16, 8), "root": self.records(20, 8),
            "practice": self.records(19, 24)})
        self.assertFalse(result["preregistered_material_screen"]["pass"])
        self.assertTrue(result["preregistered_material_screen"]["conditional_gain_at_least_10_percentage_points"])

    def test_small_gain_does_not_pass_even_with_root_improvement(self):
        result = compare(self.by_id, {
            "base": self.records(16, 8), "root": self.records(20, 8),
            "practice": self.records(21, 11)})
        self.assertFalse(result["preregistered_material_screen"]["pass"])
        self.assertTrue(result["preregistered_material_screen"]["positive_unconditioned_point_effect"])

    def test_every_condition_requires_exact_common_registered_tasks(self):
        arms = {arm: self.records(16, 8) for arm in ("base", "root", "practice")}
        arms["practice"] = arms["practice"][:-1]
        with self.assertRaisesRegex(ValueError, "proposal count"):
            compare(self.by_id, arms)
        del arms["practice"]
        with self.assertRaisesRegex(ValueError, "exactly"):
            compare(self.by_id, arms)

    def test_uncertainty_is_paired_by_theorem_not_by_generated_sample(self):
        left = {"a": 0.0, "b": 1.0}
        right = {"a": 1.0, "b": 0.0}
        effect = paired_effect(left, right)
        self.assertEqual(effect["right_minus_left"], 0.0)
        self.assertEqual(effect["paired_theorems"], 2)
        self.assertEqual(effect["percentile_interval_95"], [-1.0, 1.0])
        self.assertEqual(effect, paired_effect(left, right))
        with self.assertRaises(ValueError):
            paired_effect(left, {"c": 0.5})


if __name__ == "__main__":
    unittest.main()
