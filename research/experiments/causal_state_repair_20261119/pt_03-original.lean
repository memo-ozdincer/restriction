import Mathlib
import Aesop

set_option maxHeartbeats 0

open BigOperators Real Nat Topology Rat

def op_03 : Nat → Int → Int → Int → Int → Int × Int × Int × Int
  | 0, a, b, c, d => (a,b,c,d)
  | n+1, a, b, c, d => op_03 n (a+5*c) (b+5*d) (c+2*(a+5*c)) (d+2*(b+5*d))

theorem pt_03 (n : Nat) (a b c d : Int) :
    (op_03 n a b c d).1*(op_03 n a b c d).2.2.2 - (op_03 n a b c d).2.1*(op_03 n a b c d).2.2.1 = a*d-b*c := by
  induction n with
  | zero =>
    simp [op_03]
  | succ n ih =>
    simp [op_03, ih, mul_add, mul_comm, mul_left_comm, mul_assoc]
    ring

#print axioms pt_03
