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
  have hz : (2 : ℂ) - Complex.I ≠ 0 := by
    norm_num
  have hmul : i * (2 - Complex.I) = 1 + Complex.I := by
    calc
      i * (2 - Complex.I) = i * z := by rw [h₂]
      _ = v := h₀.symm
      _ = 1 + Complex.I := h₁
  have hquot : i = (1 + Complex.I) / (2 - Complex.I) := by
    apply (eq_div_iff hz).2
    simpa [mul_comm] using hmul
  rw [hquot]
  norm_num [div_eq_mul_inv]
  ring
#print axioms mathd_algebra_313
