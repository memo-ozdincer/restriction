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
open BigOperators Real Nat Topology Rat

theorem mathd_algebra_158 (a : ℕ) (h₀ : Even a)
    (h₁ : ↑(∑ k in Finset.range 8, 2 * k + 1) - ↑(∑ k in Finset.range 5, a + 2 * k) = (4 : ℤ)) :
    a = 8 := by
  norm_num [Finset.sum_range_succ] at h₁ <;>
  simp_all only [Nat.even_iff, Finset.sum_range_succ, add_right_inj]
  omega
#print axioms mathd_algebra_158
