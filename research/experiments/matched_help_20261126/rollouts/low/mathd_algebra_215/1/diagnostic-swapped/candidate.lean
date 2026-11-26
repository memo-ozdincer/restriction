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

theorem mathd_algebra_215 (S : Finset ℝ) (h₀ : ∀ x : ℝ, x ∈ S ↔ (x + 3) ^ 2 = 121) :
    (∑ k in S, k) = -6 := by
  have hS : S = ({8, -14} : Finset ℝ) := by
    ext x
    simp only [Finset.mem_insert, Finset.mem_singleton]
    rw [h₀ x]
    constructor
    · intro h
      have hf : (x + 3 - 11) * (x + 3 + 11) = 0 := by
        nlinarith
      rcases mul_eq_zero.mp hf with h | h
      · left
        linarith
      · right
        linarith
    · rintro (rfl | rfl) <;> norm_num
  rw [hS]
  norm_num
#print axioms mathd_algebra_215
