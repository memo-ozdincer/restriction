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

theorem mathd_algebra_313 (v i z : ℂ) (h₀ : v = i * z) (h₁ : v = 1 + Complex.I)
    (h₂ : z = 2 - Complex.I) : i = 1 / 5 + 3 / 5 * Complex.I := by
  have hn : (2 - Complex.I : ℂ) ≠ 0 := by
    intro h
    have hr := congrArg Complex.re h
    norm_num at hr
  have hp : i * (2 - Complex.I) = 1 + Complex.I := by
    rw [← h₂, ← h₀, h₁]
  apply mul_right_cancel₀ hn
  calc
    i * (2 - Complex.I) = 1 + Complex.I := hp
    _ = (1 / 5 + 3 / 5 * Complex.I) * (2 - Complex.I) := by
      linear_combination (3 / 5 : ℂ) * Complex.I_sq
#print axioms mathd_algebra_313
