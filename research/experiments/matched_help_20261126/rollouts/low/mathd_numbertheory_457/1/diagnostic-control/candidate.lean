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
  have hfac : 80325 = 3^2 * 5^2 * 7 * 17 := by norm_num
  have hdiv : 17 ∣ n ! := by
    have hmul : 17 ∣ 3^2 * 5^2 * 7 * 17 := ⟨3^2 * 5^2 * 7, by ring⟩
    rw [← hfac] at hmul
    exact dvd_trans hmul h₁
  by_contra h
  have hn : n ≤ 16 := by omega
  have hlt : n ! < 80325 := by
    calc
      n ! ≤ 16 ! := Nat.factorial_le hn
      _ < 80325 := by norm_num
  have hpos : 0 < n ! := Nat.factorial_pos n
  have hle : 80325 ≤ n ! := Nat.le_of_dvd hpos h₁
  omega
#print axioms mathd_numbertheory_457
