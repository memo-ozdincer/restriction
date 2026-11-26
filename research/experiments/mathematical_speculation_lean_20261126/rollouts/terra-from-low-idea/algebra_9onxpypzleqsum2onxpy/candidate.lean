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

theorem algebra_9onxpypzleqsum2onxpy (x y z : ℝ) (h₀ : 0 < x ∧ 0 < y ∧ 0 < z) :
    9 / (x + y + z) ≤ 2 / (x + y) + 2 / (y + z) + 2 / (z + x) := by
  have hs : 0 < x + y + z := by positivity
  have hxy : 0 < x + y := by positivity
  have hyz : 0 < y + z := by positivity
  have hzx : 0 < z + x := by positivity
  have hpoly :
      9 * ((x + y) * (y + z) * (z + x)) ≤
        2 * (x + y + z) *
          ((x + y) * (y + z) + (y + z) * (z + x) + (z + x) * (x + y)) := by
    have h1 : 0 ≤ (x + y) * (y - x) ^ 2 := mul_nonneg (le_of_lt hxy) (sq_nonneg _)
    have h2 : 0 ≤ (y + z) * (z - y) ^ 2 := mul_nonneg (le_of_lt hyz) (sq_nonneg _)
    have h3 : 0 ≤ (z + x) * (x - z) ^ 2 := mul_nonneg (le_of_lt hzx) (sq_nonneg _)
    nlinarith
  have hd : 0 < (x + y + z) * (x + y) * (y + z) * (z + x) := by positivity
  apply (mul_le_mul_right hd).mp
  field_simp [ne_of_gt hs, ne_of_gt hxy, ne_of_gt hyz, ne_of_gt hzx]
  nlinarith [hpoly]
#print axioms algebra_9onxpypzleqsum2onxpy
