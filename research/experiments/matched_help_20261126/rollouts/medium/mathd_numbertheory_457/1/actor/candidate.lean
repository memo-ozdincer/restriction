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
  by_contra h
  have hn : n ≤ 16 := Nat.le_of_not_ge h
  have hfac : n ! ≤ 16 ! := Nat.factorial_le hn
  have hdiv : 80325 ∣ 16 ! := Nat.dvd_of_dvd_mul_left h₁ (by
    have : n ! ∣ 16 ! := Nat.dvd_factorial (by omega) (by omega)
    exact this)
  norm_num [Nat.factorial] at hdiv
#print axioms mathd_numbertheory_457
