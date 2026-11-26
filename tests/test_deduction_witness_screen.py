import unittest

from scripts.project.screen_deduction_witness import category, form


class DeductionWitnessScreenTest(unittest.TestCase):
    def test_outer_goal(self):
        self.assertEqual(category("theorem test (x : ℕ) : ∃ y : ℕ, y = x := by"), "explicit_existential")
        self.assertEqual(category("theorem test (h : ∃ x, P x) : Q := by"), "other_statement")
        self.assertEqual(category("theorem test : ∀ x, ∃ y, R x y := by"), "nested_existential")

    def test_lexical_candidates(self):
        self.assertEqual(form("  use 5, 2\n  norm_num"), "explicit_candidate_syntax")
        self.assertEqual(form("  refine' ⟨0, _⟩\n  simp"), "explicit_candidate_syntax")
        self.assertEqual(form("  exact ⟨h₁, h₂⟩"), "explicit_candidate_syntax")
        self.assertEqual(form("  -- use 5\n  simp"), "other_syntax")
