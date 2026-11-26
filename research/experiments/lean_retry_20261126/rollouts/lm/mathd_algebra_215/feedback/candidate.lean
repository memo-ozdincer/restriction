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
  have hroots : ∀ x : ℝ, (x + 3) ^ 2 = 121 ↔ x = -14 ∨ x = 8 := by
    intro x
    constructor
    · intro h
      have hf : (x + 14) * (x - 8) = 0 := by nlinarith [h]
      rcases mul_eq_zero.mp hf with h' | h'
      · left
        linarith
      · right
        linarith
    · rintro (rfl | rfl) <;> norm_num
  have hs : S = ({-14, 8} : Finset ℝ) := by
    ext x
    rw [h₀, hroots]
    simp
  rw [hs]
  norm_num
#print axioms mathd_algebra_215
