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
  rcases h₀ with ⟨hx, hy, hz⟩
  have hs : 0 < x + y + z := by positivity
  have hxy : 0 < x + y := by positivity
  have hyz : 0 < y + z := by positivity
  have hzx : 0 < z + x := by positivity
  have hd : 0 < (x + y) * (y + z) * (z + x) := by positivity
  have h1 : 0 ≤ (x + y) * (y - x)^2 :=
    mul_nonneg (le_of_lt hxy) (sq_nonneg (y - x))
  have h2 : 0 ≤ (y + z) * (z - y)^2 :=
    mul_nonneg (le_of_lt hyz) (sq_nonneg (z - y))
  have h3 : 0 ≤ (z + x) * (x - z)^2 :=
    mul_nonneg (le_of_lt hzx) (sq_nonneg (x - z))
  have hp :
      9 * ((x + y) * (y + z) * (z + x)) ≤
        2 * ((y + z) * (z + x) + (z + x) * (x + y) +
          (x + y) * (y + z)) * (x + y + z) := by
    nlinarith only [h1, h2, h3]
  apply (div_le_iff₀ hs).2
  calc
    (9 : ℝ) ≤
        (2 * ((y + z) * (z + x) + (z + x) * (x + y) +
          (x + y) * (y + z)) * (x + y + z)) /
          ((x + y) * (y + z) * (z + x)) :=
      (le_div_iff₀ hd).2 hp
    _ = (2 / (x + y) + 2 / (y + z) + 2 / (z + x)) *
        (x + y + z) := by
      field_simp
      <;> ring
#print axioms algebra_9onxpypzleqsum2onxpy
