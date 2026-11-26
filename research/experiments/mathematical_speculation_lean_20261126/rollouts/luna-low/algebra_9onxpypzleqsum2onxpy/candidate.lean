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
  have hxy : 0 < x + y := by linarith
  have hyz : 0 < y + z := by linarith
  have hzx : 0 < z + x := by linarith
  have hs : 0 < x + y + z := by linarith
  have h1 : 0 < (x + y) * (y + z) * (z + x) := mul_pos (mul_pos hxy hyz) hzx
  field_simp
  rw [div_le_iff₀ hs]
  rw [div_le_iff₀ h1]
  nlinarith [sq_nonneg (x - y), sq_nonneg (y - z), sq_nonneg (z - x)]
#print axioms algebra_9onxpypzleqsum2onxpy
