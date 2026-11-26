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
  have h_help : i = (1 + Complex.I) / (2 - Complex.I) := by
    have hn : (2 - Complex.I : ℂ) ≠ 0 := by
      intro hz
      have hr := congrArg Complex.re hz
      norm_num at hr
    apply (eq_div_iff hn).2
    rw [← h₂, ← h₀, h₁]
  rw [h_help]
  apply (div_eq_iff (by norm_num : (2 - Complex.I : ℂ) ≠ 0)).2
    norm_num [Complex.ext_iff]
    <;> ring
#print axioms mathd_algebra_313
