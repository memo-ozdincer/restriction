import Mathlib
import Aesop

set_option maxHeartbeats 0

open BigOperators Real Nat Topology Rat

def op_07 : Nat → Int → Int → Int → Int → Int × Int × Int × Int
  | 0, a, b, c, d => (a,b,c,d)
  | n+1, a, b, c, d => op_07 n (a+5*c) (b+5*d) (c+2*(a+5*c)) (d+2*(b+5*d))

theorem linked_contract (n : Nat) (a b c d : Int) :
    (op_07 n a b c d).1*(op_07 n a b c d).2.2.2 - (op_07 n a b c d).2.1*(op_07 n a b c d).2.2.1 = a*d-b*c := by
  induction n generalizing a b c d with
  | zero =>
    simp [op_07]
  | succ n ih =>
    simp [op_07, ih, mul_add, mul_comm, mul_left_comm, mul_assoc]
    ring

theorem pt_07 (n : Nat) (a b c d : Int) (h : a*d-b*c ≠ 0) :
    (op_07 n a b c d).1 ≠ 0 ∨ (op_07 n a b c d).2.1 ≠ 0 := by
  have hbridge : (op_07 n a b c d).1*(op_07 n a b c d).2.2.2 - (op_07 n a b c d).2.1*(op_07 n a b c d).2.2.1 = a*d-b*c := linked_contract n a b c d
  by_contra!
  aesop

#print axioms pt_07
