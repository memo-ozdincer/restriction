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
  have hz : (2 - Complex.I : ℂ) ≠ 0 := by
    norm_num
  rw [h₁] at h₀
  rw [h₂] at h₀
  have hi : i = (1 + Complex.I) / (2 - Complex.I) := by
    apply (mul_right_cancel₀ hz)
    simpa [div_eq_mul_inv, mul_comm] using h₀.symm
  rw [hi]
   have hden : (2 - Complex.I : ℂ) * (2 + Complex.I) = 5 := by
    norm_num [Complex.I_mul_I]
  field_simp [hden]
  ring
#print axioms mathd_algebra_313
