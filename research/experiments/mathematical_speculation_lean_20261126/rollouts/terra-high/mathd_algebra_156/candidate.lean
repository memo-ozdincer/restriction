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
  have hx : x ^ 4 = 5 * x ^ 2 - 6 := by
    simpa only [h₀, h₁] using h₂
  have hy : y ^ 4 = 5 * y ^ 2 - 6 := by
    simpa only [h₀, h₁] using h₃
  have hs : x ^ 2 + y ^ 2 = 5 := by
    have hf : (y ^ 2 - x ^ 2) * (x ^ 2 + y ^ 2 - 5) = 0 := by
      nlinarith [hx, hy]
    rcases mul_eq_zero.mp hf with h | h
    · linarith
    · linarith
  have hp : x ^ 2 * y ^ 2 = 6 := by
    have hm : x ^ 2 * (x ^ 2 + y ^ 2 - 5) = 0 := by
      rw [show x ^ 2 + y ^ 2 - 5 = 0 by linarith]
      ring
    nlinarith [hx, hm]
  have hf : (y ^ 2 - x ^ 2 - 1) * (y ^ 2 - x ^ 2 + 1) = 0 := by
    nlinarith [hx, hy, hp]
  rcases mul_eq_zero.mp hf with h | h
  · linarith
  · linarith
#print axioms mathd_algebra_156
