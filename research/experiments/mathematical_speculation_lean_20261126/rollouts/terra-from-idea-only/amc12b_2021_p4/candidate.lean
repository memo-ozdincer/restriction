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

theorem amc12b_2021_p4 (m a : ℕ) (h₀ : 0 < m ∧ 0 < a) (h₁ : ↑m / ↑a = (3 : ℝ) / 4) :
    (84 * ↑m + 70 * ↑a) / (↑m + ↑a) = (76 : ℝ) := by
  have ha : (a : ℝ) ≠ 0 := by
    exact_mod_cast (Nat.ne_of_gt h₀.2)
  have hm_pos : (0 : ℝ) < m := by
    exact_mod_cast h₀.1
  have ha_pos : (0 : ℝ) < a := by
    exact_mod_cast h₀.2
  have hrel : 4 * (m : ℝ) = 3 * (a : ℝ) := by
    have h := (div_eq_iff ha).mp h₁
    linarith
  have hden : (m : ℝ) + (a : ℝ) ≠ 0 :=
    ne_of_gt (add_pos hm_pos ha_pos)
  apply (div_eq_iff hden).2
  linarith
#print axioms amc12b_2021_p4
