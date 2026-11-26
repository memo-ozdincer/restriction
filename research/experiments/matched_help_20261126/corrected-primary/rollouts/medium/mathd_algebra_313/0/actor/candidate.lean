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
  rw [h₁] at h₀
  have hz : (2 : ℂ) - Complex.I ≠ 0 := by
    norm_num [Complex.ext_iff]
  have hi : i = (1 + Complex.I) / (2 - Complex.I) := by
    rw [h₂] at h₀
    apply (eq_div_iff hz).2
    calc
      i * (2 - Complex.I) = 1 + Complex.I := h₀
      _ = (1 + Complex.I) := rfl
  rw [hi]
  field_simp
  <;> ring
#print axioms mathd_algebra_313
