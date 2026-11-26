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
  have hroots : ∀ x : ℝ, (x + 3) ^ 2 = 121 → x = 8 ∨ x = -14 := by
    intro x hx
    have hprod : (x - 8) * (x + 14) = 0 := by
      nlinarith [hx]
    rcases mul_eq_zero.mp hprod with h | h
    · left
      linarith
    · right
      linarith
  have hS : S = ({8, -14} : Finset ℝ) := by
    ext x
    rw [h₀ x]
    simp only [Finset.mem_insert, Finset.mem_singleton]
    constructor
    · exact hroots x
    · rintro (rfl | rfl) <;> norm_num
  rw [hS]
  norm_num
#print axioms mathd_algebra_215
