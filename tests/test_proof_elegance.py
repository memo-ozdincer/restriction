import unittest

from scripts.project.analyze_proof_elegance import (
    concise_novel_candidates,
    directional_minimum_counts,
    pareto_dominates_all,
    qualifying_mode_relationship,
    recovery_at_floor,
)


def proof(mode, tokens, steps, exact=None):
    return {
        "mode_id": mode,
        "exact_proof_id": exact or f"exact-{mode}",
        "token_count": tokens,
        "tactic_heads": [f"tactic-{index}" for index in range(steps)],
    }


class ProofEleganceTests(unittest.TestCase):
    def test_pareto_dominance_requires_both_dimensions(self):
        comparators = [proof("a", 20, 3), proof("b", 30, 2)]
        self.assertTrue(pareto_dominates_all(proof("new", 19, 2), comparators))
        self.assertFalse(pareto_dominates_all(proof("new", 19, 4), comparators))
        self.assertFalse(pareto_dominates_all(proof("new", 31, 1), comparators))
        self.assertFalse(pareto_dominates_all(proof("new", 20, 3), comparators))
        self.assertFalse(pareto_dominates_all(proof("new", 1, 1), []))

    def test_concise_candidate_must_have_novel_mode(self):
        comparator = [proof("shared", 20, 3)]
        treatment = [proof("shared", 10, 1), proof("novel", 19, 2)]
        self.assertEqual(
            [item["mode_id"] for item in concise_novel_candidates(treatment, comparator)],
            ["novel"],
        )

    def test_directional_minima_report_both_directions_and_ties(self):
        treatment = {
            "win": [proof("a", 10, 1)],
            "loss": [proof("b", 10, 3)],
            "tie": [proof("c", 10, 2)],
            "only": [proof("d", 10, 1)],
        }
        comparator = {
            "win": [proof("e", 10, 2)],
            "loss": [proof("f", 10, 2)],
            "tie": [proof("g", 10, 2)],
            "only": [],
        }
        result = directional_minimum_counts(
            treatment, comparator, "parsed_tactic_heads"
        )
        self.assertEqual(result["common_solved_theorems"], 3)
        self.assertEqual(result["treatment_lower"], 1)
        self.assertEqual(result["comparator_lower"], 1)
        self.assertEqual(result["equal"], 1)
        self.assertEqual(result["two_sided_exact_sign_p"], 1.0)

    def test_qualifying_modes_split_new_from_recovered(self):
        treatment = {
            "x": [proof("new", 10, 1), proof("recovered", 10, 1)]
        }
        comparator = {"x": [proof("comparator", 20, 2)]}
        source = {"x": [proof("recovered", 30, 3), proof("recovered", 31, 3)]}
        result = qualifying_mode_relationship(treatment, comparator, source)
        self.assertEqual(result["qualifying_tactic_modes"], 2)
        self.assertEqual(result["modes_absent_from_base_sample"], 1)
        self.assertEqual(
            result["modes_present_in_base_but_absent_from_comparator"], 1
        )
        self.assertEqual(
            result["recovered_modes_by_minimum_base_observations"],
            {"2": 1, "4": 0, "8": 0},
        )

    def test_recovery_floor_uses_base_frequency_and_sampled_absence(self):
        base = {
            "x": [proof("recover", 1, 1), proof("recover", 2, 1), proof("lost", 3, 1)],
            "y": [proof("retained", 1, 1), proof("retained", 2, 1)],
        }
        grpo = {"x": [], "y": [proof("retained", 1, 1)]}
        restriction = {"x": [proof("recover", 1, 1)], "y": []}
        result = recovery_at_floor(
            base,
            grpo,
            restriction,
            identity_field="mode_id",
            floors=(1, 2),
        )
        self.assertEqual(result["1"]["base_identities_absent_from_grpo"], 2)
        self.assertEqual(result["1"]["recovered_by_restriction"], 1)
        self.assertEqual(result["2"]["base_identities_absent_from_grpo"], 1)
        self.assertEqual(result["2"]["recovered_by_restriction"], 1)


if __name__ == "__main__":
    unittest.main()
