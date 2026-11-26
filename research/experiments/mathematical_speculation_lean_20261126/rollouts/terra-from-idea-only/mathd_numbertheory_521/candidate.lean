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
  have hle : n ≤ m := by
    by_contra h
    have hlt : m < n := Nat.lt_of_not_ge h
    have hz : m - n = 0 := Nat.sub_eq_zero_of_le (Nat.le_of_lt hlt)
    rw [hz] at h₂
    norm_num at h₂
  have hm : m = n + 2 := by
    have ht := Nat.sub_add_cancel hle
    rw [h₂] at ht
    nlinarith
  by_cases hn : n ≤ 16
  · by_cases he : n = 16
    · nlinarith
    · have hn15 : n ≤ 15 := Nat.lt_succ_iff.mp (lt_of_le_of_ne hn he)
      have hp : n * n ≤ 15 * 15 := Nat.mul_le_mul hn15 hn15
      nlinarith
  · have hn17 : 17 ≤ n := Nat.lt_of_not_ge hn
    have hp : 17 * 17 ≤ n * n := Nat.mul_le_mul hn17 hn17
    nlinarith
#print axioms mathd_numbertheory_521
