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
  have h : i * (2 - Complex.I) = 1 + Complex.I := by
    rw [← h₁, h₂, ← h₀]
  have hmul : (i * (2 - Complex.I)) * (2 + Complex.I) = (1 + Complex.I) * (2 + Complex.I) := by
    rw [h]
  have hden : (2 - Complex.I) * (2 + Complex.I) = 5 := by
    norm_num [Complex.I_mul_I]
  have hnum : (1 + Complex.I) * (2 + Complex.I) = 1 + 3 * Complex.I := by
    norm_num [Complex.I_mul_I]
  rw [mul_assoc, hden, hnum] at hmul
  have hi : i * 5 = 1 + 3 * Complex.I := by
    simpa [mul_comm] using hmul
  have hfive : (5 : ℂ) ≠ 0 := by norm_num
  apply (mul_right_cancel₀ hfive)
  calc
    (i * 5) * (1 / 5 : ℂ) = i := by
      field_simp
    _ = (1 + 3 * Complex.I) * (1 / 5 : ℂ) := by rw [hi]
    _ = 1 / 5 + 3 / 5 * Complex.I := by ring
#print axioms mathd_algebra_313
