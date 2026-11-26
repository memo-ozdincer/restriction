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
    rw [hfac] at h₁
    exact (Nat.dvd_of_mul_dvd_mul_left (by norm_num : 0 < 3^2 * 5^2 * 7) h₁)
  by_contra hn
  have hn' : n < 17 := by omega
  have hlt : n ! < 17 := by
    calc
      n ! ≤ 16 ! := Nat.factorial_le hn'.le
      _ < 17 := by norm_num
  have : 17 ≤ n ! := Nat.le_of_dvd (by positivity) hdiv
  omega
#print axioms mathd_numbertheory_457
