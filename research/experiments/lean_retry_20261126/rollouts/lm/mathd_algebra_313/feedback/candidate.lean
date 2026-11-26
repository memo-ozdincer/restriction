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
  rw [h₁, h₂] at h₀
  have hz : (2 : ℂ) - Complex.I ≠ 0 := by
    intro h
    have hre := congrArg Complex.re h
    norm_num at hre
  have heq : i * (2 - Complex.I) = (1 / 5 + 3 / 5 * Complex.I) * (2 - Complex.I) := by
    calc
      i * (2 - Complex.I) = 1 + Complex.I := h₀.symm
      _ = (1 / 5 + 3 / 5 * Complex.I) * (2 - Complex.I) := by
        norm_num [Complex.I_sq]
  exact mul_right_cancel₀ hz heq
#print axioms mathd_algebra_313
