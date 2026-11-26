import Mathlib.Data.Real.Basic
import Mathlib.Tactic.Ring
import Mathlib.Tactic.Linarith
import Mathlib.Tactic.NormNum
import Mathlib.Tactic.Positivity
import Mathlib.Tactic.FieldSimp
import Aesop
import Mathlib.Algebra.BigOperators.Group.Finset
import Mathlib.Algebra.BigOperators.Ring
import Mathlib.Data.Complex.Basic
import Mathlib.Data.Nat.Factorial.Basic
import Mathlib.Data.Nat.Prime
import Mathlib.Tactic.IntervalCases
import Mathlib.Tactic.Contrapose
import Mathlib.Tactic.PushNeg
import Mathlib.Tactic.LinearCombination
set_option maxHeartbeats 0
open BigOperators Real Nat Rat

theorem mathd_algebra_156 (x y : ℝ) (f g : ℝ → ℝ) (h₀ : ∀ t, f t = t ^ 4)
    (h₁ : ∀ t, g t = 5 * t ^ 2 - 6) (h₂ : f x = g x) (h₃ : f y = g y) (h₄ : x ^ 2 < y ^ 2) :
    y ^ 2 - x ^ 2 = 1 := by
  have h_help : x ^ 2 + y ^ 2 = 5 := by
    have hx : x ^ 4 = 5 * x ^ 2 - 6 := by
      simpa only [h₀, h₁] using h₂
    have hy : y ^ 4 = 5 * y ^ 2 - 6 := by
      simpa only [h₀, h₁] using h₃
    have hf : (y ^ 2 - x ^ 2) * (x ^ 2 + y ^ 2 - 5) = 0 := by
      nlinarith [hx, hy]
    rcases mul_eq_zero.mp hf with h | h
    · linarith
    · linarith
  clear h_help
  rw [h₀] at h₂ h₃
  simp_all only [h₀, h₁, mul_one, mul_zero, sub_zero, sub_eq_zero]
  ring_nf
  apply mul_left_cancel₀ (sub_ne_zero.mpr h₄.ne)
  ring_nf
  nlinarith
#print axioms mathd_algebra_156
