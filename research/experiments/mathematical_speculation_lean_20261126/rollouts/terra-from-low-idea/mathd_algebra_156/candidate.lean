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
  have hx : (x ^ 2 - 2) * (x ^ 2 - 3) = 0 := by
    rw [h₀, h₁] at h₂
    nlinarith [h₂]
  have hy : (y ^ 2 - 2) * (y ^ 2 - 3) = 0 := by
    rw [h₀, h₁] at h₃
    nlinarith [h₃]
  rcases mul_eq_zero.mp hx with hx | hx <;>
    rcases mul_eq_zero.mp hy with hy | hy <;>
    nlinarith [h₄]
#print axioms mathd_algebra_156
