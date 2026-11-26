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
  have hn : n ≤ 16 := by omega
  have hfac : n ! ≤ 16 ! := Nat.factorial_le hn
  have hsmall : 16 ! < 80325 := by norm_num
  rcases h₁ with ⟨k, hk⟩
  have hdiv : 80325 ≤ n ! := Nat.le_of_dvd (Nat.factorial_pos n) ⟨k, hk⟩
  omega
#print axioms mathd_numbertheory_457
