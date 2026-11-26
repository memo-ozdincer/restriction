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
  subst v z
  have hz : (2 : ℂ) - Complex.I ≠ 0 := by
    intro h
    have : Complex.I = 2 := sub_eq_zero.mp h
    have hI : Complex.I.re = (2 : ℂ).re := congrArg Complex.re this
    norm_num at hI
  have hi : i = (1 + Complex.I) / (2 - Complex.I) := by
    rw [h₁] at h₀
    rw [h₀]
    exact (eq_div_iff hz).2 rfl
  rw [hi]
  field_simp
  ring
#print axioms mathd_algebra_313
