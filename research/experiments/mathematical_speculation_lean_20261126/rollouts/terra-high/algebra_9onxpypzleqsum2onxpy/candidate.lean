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
  have h₁ : 0 ≤ 2 / (x + y) - 6 / (x + y + z) +
      (9 / 2 : ℝ) * (x + y) / (x + y + z) ^ 2 := by
    have hp : 0 ≤ (x + y - 2 * z) ^ 2 /
        (2 * (x + y) * (x + y + z) ^ 2) := by positivity
    have heq : (x + y - 2 * z) ^ 2 /
        (2 * (x + y) * (x + y + z) ^ 2) =
        2 / (x + y) - 6 / (x + y + z) +
          (9 / 2 : ℝ) * (x + y) / (x + y + z) ^ 2 := by
      field_simp [ne_of_gt hxy, ne_of_gt hs] <;> ring
    rw [← heq]
    exact hp
  have h₂ : 0 ≤ 2 / (y + z) - 6 / (x + y + z) +
      (9 / 2 : ℝ) * (y + z) / (x + y + z) ^ 2 := by
    have hp : 0 ≤ (y + z - 2 * x) ^ 2 /
        (2 * (y + z) * (x + y + z) ^ 2) := by positivity
    have heq : (y + z - 2 * x) ^ 2 /
        (2 * (y + z) * (x + y + z) ^ 2) =
        2 / (y + z) - 6 / (x + y + z) +
          (9 / 2 : ℝ) * (y + z) / (x + y + z) ^ 2 := by
      field_simp [ne_of_gt hyz, ne_of_gt hs] <;> ring
    rw [← heq]
    exact hp
  have h₃ : 0 ≤ 2 / (z + x) - 6 / (x + y + z) +
      (9 / 2 : ℝ) * (z + x) / (x + y + z) ^ 2 := by
    have hp : 0 ≤ (z + x - 2 * y) ^ 2 /
        (2 * (z + x) * (x + y + z) ^ 2) := by positivity
    have heq : (z + x - 2 * y) ^ 2 /
        (2 * (z + x) * (x + y + z) ^ 2) =
        2 / (z + x) - 6 / (x + y + z) +
          (9 / 2 : ℝ) * (z + x) / (x + y + z) ^ 2 := by
      field_simp [ne_of_gt hzx, ne_of_gt hs] <;> ring
    rw [← heq]
    exact hp
  have hc : (9 / 2 : ℝ) * (x + y) / (x + y + z) ^ 2 +
      (9 / 2 : ℝ) * (y + z) / (x + y + z) ^ 2 +
      (9 / 2 : ℝ) * (z + x) / (x + y + z) ^ 2 =
      9 / (x + y + z) := by
    field_simp [ne_of_gt hs] <;> ring
  linarith
#print axioms algebra_9onxpypzleqsum2onxpy
