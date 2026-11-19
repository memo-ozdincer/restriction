import Mathlib
import Aesop

set_option maxHeartbeats 0

open BigOperators Real Nat Topology Rat

def orbit : Nat → Int × Int
  | 0 => (1, 0)
  | n+1 => let s := orbit n; (2*s.1 + 3*s.2, 1*s.1 + 2*s.2)

theorem reusable_fact (n : Nat) :
    (orbit n).1 ^ 2 - 3 * (orbit n).2 ^ 2 = 1 := by
  induction n with
  | zero => norm_num [orbit]
  | succ n ih =>
    change (2*(orbit n).1 + 3*(orbit n).2)^2 -
      3*(1*(orbit n).1 + 2*(orbit n).2)^2 = 1
    nlinarith [ih]

theorem target (n : Nat) : (orbit n).1 ≠ 0 := by
  have h := reusable_fact n
  intro heq
  simp only [heq, mul_zero, zero_mul, sub_zero, zero_add, zero_pow two_ne_zero] at h
  nlinarith

#print axioms target
