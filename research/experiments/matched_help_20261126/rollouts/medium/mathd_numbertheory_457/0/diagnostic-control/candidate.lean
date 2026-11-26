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
  have hn : n ≤ 16 := by omega
  have hfactor : 80325 ∣ (16 : ℕ)! := by
    have hle : n ! ∣ (16 : ℕ)! := Nat.factorial_dvd_factorial hn
    exact dvd_trans h₁ hle
  have h17 : 17 ∣ 80325 := by norm_num
  have h17factor : 17 ∣ (16 : ℕ)! := dvd_trans h17 hfactor
  have h17prime : Nat.Prime 17 := by norm_num
  have h17le : 17 ≤ 16 := (Nat.Prime.dvd_factorial h17prime).1 h17factor
  omega
#print axioms mathd_numbertheory_457
