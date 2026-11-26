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
  have ha : (0 : ℝ) < (a : ℝ) := by
    exact_mod_cast h₀.2
  have hm : (0 : ℝ) < (m : ℝ) := by
    exact_mod_cast h₀.1
  have hratio : 4 * (m : ℝ) = 3 * (a : ℝ) := by
    have h := (div_eq_iff (ne_of_gt ha)).mp h₁
    linarith
  have hd : (m : ℝ) + (a : ℝ) ≠ 0 := ne_of_gt (add_pos hm ha)
  apply (div_eq_iff hd).2
  linarith
#print axioms amc12b_2021_p4
