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
  have hmn : m = n + 2 := by
    have hle : n ≤ m := Nat.le_of_lt (Nat.sub_pos_iff_lt.mp (by simpa [h₂]))
    have ht : m - n + n = m := Nat.sub_add_cancel hle
    simpa [h₂, Nat.add_comm] using ht.symm
  by_cases ha : n ≤ 15
  · have hp := Nat.mul_le_mul_left n ha
    nlinarith
  · have hb : 16 ≤ n := Nat.succ_le_iff.mpr (Nat.lt_of_not_ge ha)
    by_cases hc : n ≤ 16
    · have hn : n = 16 := Nat.le_antisymm hc hb
      simpa [hn] using hmn
    · have hd : 17 ≤ n := Nat.succ_le_iff.mpr (Nat.lt_of_not_ge hc)
      have hp := Nat.mul_le_mul_left n hd
      nlinarith
#print axioms mathd_numbertheory_521
