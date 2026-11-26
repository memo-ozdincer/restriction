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
  have hxy : 0 < x + y := add_pos hx hy
  have hyz : 0 < y + z := add_pos hy hz
  have hzx : 0 < z + x := add_pos hz hx
  have hxyz : 0 < x + y + z := add_pos hxy hz
  have hden : 0 < (x + y + z) * (x + y) * (y + z) * (z + x) := by positivity
  field_simp
  nlinarith [mul_nonneg (sub_nonneg.mpr (le_of_lt hx)) (sq_nonneg (y - z)),
    mul_nonneg (sub_nonneg.mpr (le_of_lt hy)) (sq_nonneg (z - x)),
    mul_nonneg (sub_nonneg.mpr (le_of_lt hz)) (sq_nonneg (x - y))]
#print axioms algebra_9onxpypzleqsum2onxpy
