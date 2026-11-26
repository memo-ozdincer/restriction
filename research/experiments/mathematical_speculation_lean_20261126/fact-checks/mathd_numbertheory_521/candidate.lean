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

theorem mathd_numbertheory_521 (m n : ℕ) (h₀ : Even m) (h₁ : Even n) (h₂ : m - n = 2)
    (h₃ : m * n = 288) : m = 18 := by
  have h_help : m = n + 2 := by
    have hle : n ≤ m := by
      by_contra h
      have h' : m ≤ n := Nat.le_of_lt (Nat.lt_of_not_ge h)
      have hz : m - n = 0 := Nat.sub_eq_zero_of_le h'
      rw [h₂] at hz
      norm_num at hz
    have hcancel := Nat.sub_add_cancel hle
    rw [h₂] at hcancel
    linarith
  clear h_help
  have h₄ : m * n = 288 := by assumption
  have h₅ : m = n + 2 := by omega
  have h₆ : m * n = 288 := by omega
  have h₇ : m = 18 := by nlinarith
  exact h₇
#print axioms mathd_numbertheory_521
