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

theorem mathd_algebra_484 : Real.log 27 / Real.log 3 = 3 := by
  rw [show Real.log 27 = 3 * Real.log 3 by
    rw [← Real.log_rpow (show (0 : ℝ) < 3 from by norm_num)]
    norm_num
    ]
  field_simp
#print axioms mathd_algebra_484
