import Mathlib

theorem two_point_rigidity (a b c d : ℤ)
    (hs : a + b = c + d) (hq : a^2 + b^2 = c^2 + d^2) :
    (a = c ∧ b = d) ∨ (a = d ∧ b = c) := by
  have hb : b = c+d-a := by linarith
  rw [hb] at hq
  have h : (a-c)*(a-d) = 0 := by nlinarith [hq]
  rcases mul_eq_zero.mp h with h | h
  · left; constructor <;> linarith
  · right; constructor <;> linarith

#print axioms two_point_rigidity
