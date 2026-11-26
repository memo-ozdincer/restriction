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

theorem mathd_numbertheory_457 (n : ℕ) (h₀ : 0 < n) (h₁ : 80325 ∣ n !) : 17 ≤ n := by
  have hp : Nat.Prime 17 := by norm_num
  have h17 : 17 ∣ n ! := dvd_trans (by norm_num : 17 ∣ 80325) h₁
  by_contra h
  have hn : n < 17 := by omega
  have hnd : n ! < 17 := by
    calc
      n ! ≤ 16 ! := Nat.factorial_le hn.le
      _ < 17 := by norm_num
  have : n ! = 0 := Nat.eq_zero_of_dvd_of_lt h17 hnd
  have : 0 < n ! := Nat.factorial_pos n
  omega
#print axioms mathd_numbertheory_457
