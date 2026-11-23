import Mathlib

theorem pell_next (x y : ℤ) (h : x^2 - 6*y^2 = 1) :
    (5*x+12*y)^2 - 6*(2*x+5*y)^2 = 1 := by
  nlinarith [h]

theorem pell_two_exclusions :
    ∃ x y : ℤ, x^2 - 6*y^2 = 1 ∧ x.natAbs ≠ 1 ∧ x.natAbs ≠ 5 := by
  exact ⟨49,20, by norm_num⟩

#print axioms pell_next
#print axioms pell_two_exclusions
