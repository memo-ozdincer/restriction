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
  have hnm : n ≤ m := by
    by_contra h
    have hz : m - n = 0 := Nat.sub_eq_zero_of_le (Nat.le_of_not_ge h)
    rw [hz] at h₂
    norm_num at h₂
  have heq : m = n + 2 := by
    simpa [h₂, Nat.add_comm] using (Nat.sub_add_cancel hnm).symm
  have hn : n = 16 := by
    have hlo : 16 ≤ n := by
      by_contra h
      have hn' : n ≤ 15 := Nat.lt_succ_iff.mp (Nat.lt_of_not_ge h)
      have hm' : m ≤ 17 := by
        rw [heq]
        simpa using Nat.add_le_add_right hn' 2
      have hp : m * n ≤ 255 := by
        simpa using Nat.mul_le_mul hm' hn'
      linarith
    have hhi : n ≤ 16 := by
      by_contra h
      have hn' : 17 ≤ n := Nat.succ_le_of_lt (Nat.lt_of_not_ge h)
      have hm' : 19 ≤ m := by
        rw [heq]
        simpa using Nat.add_le_add_right hn' 2
      have hp : 323 ≤ m * n := by
        simpa using Nat.mul_le_mul hm' hn'
      linarith
    exact Nat.le_antisymm hhi hlo
  simpa [hn] using heq
#print axioms mathd_numbertheory_521
