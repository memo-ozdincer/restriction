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

theorem mathd_algebra_215 (S : Finset ℝ) (h₀ : ∀ x : ℝ, x ∈ S ↔ (x + 3) ^ 2 = 121) :
    (∑ k in S, k) = -6 := by
  have h₁ : S = {8, -14} := by
    ext x; simp only [h₀, Finset.mem_insert, Finset.mem_singleton, sq]; constructor
    · intro h; match eq_or_eq_neg_of_sq_eq_sq (x + 3) 11 (by linarith) with
      | Or.inl h => left; linarith
      | Or.inr h => right; linarith
    · intro h; match h with
      | Or.inl h => rw [h]; norm_num
      | Or.inr h => rw [h]; norm_num
  rw [h₁]; norm_num
#print axioms mathd_algebra_215
