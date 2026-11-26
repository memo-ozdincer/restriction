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
  have h₁ : S = {8, -14} := by
    ext1 x
    simp only [h₀, Finset.mem_insert, Finset.mem_singleton, true_and_iff, and_true_iff]
    constructor
    · intro hx
      have hx' : (x + 3) ^ 2 = 121 := hx
      have hx'' : x + 3 = 11 ∨ x + 3 = -11 := by
        apply eq_or_eq_neg_of_sq_eq_sq
        rw [hx']
        norm_num
      cases' hx'' with hx'' hx''
      · left
        linarith
      · right
        linarith
    · intro hx
      cases' hx with hx hx
      · rw [hx]
        norm_num
      · rw [hx]
        norm_num
  rw [h₁]
  norm_num
#print axioms mathd_algebra_215
