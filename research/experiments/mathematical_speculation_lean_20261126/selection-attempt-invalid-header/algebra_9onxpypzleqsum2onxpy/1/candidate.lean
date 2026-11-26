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
open BigOperators Real Nat Topology Rat

theorem algebra_9onxpypzleqsum2onxpy (x y z : ℝ) (h₀ : 0 < x ∧ 0 < y ∧ 0 < z) :
    9 / (x + y + z) ≤ 2 / (x + y) + 2 / (y + z) + 2 / (z + x) := by
  have : 0 < x + y + z := add_pos (add_pos h₀.1 h₀.2.1) h₀.2.2
  have h₁ : 0 < x + y := add_pos h₀.1 h₀.2.1
  have h₂ : 0 < y + z := add_pos h₀.2.1 h₀.2.2
  have h₃ : 0 < z + x := add_pos h₀.2.2 h₀.1
  field_simp
  rw [div_le_div_iff this (by positivity)]
  nlinarith [sq_nonneg (x - y), sq_nonneg (y - z), sq_nonneg (z - x)]
#print axioms algebra_9onxpypzleqsum2onxpy
