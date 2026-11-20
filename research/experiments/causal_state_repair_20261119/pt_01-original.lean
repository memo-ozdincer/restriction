import Mathlib
import Aesop

set_option maxHeartbeats 0

open BigOperators Real Nat Topology Rat

def op_01 : Nat → Int → Int → Int → Int → Int × Int × Int × Int
  | 0, a, b, c, d => (a,b,c,d)
  | n+1, a, b, c, d => op_01 n (a+3*c) (b+3*d) (c+2*(a+3*c)) (d+2*(b+3*d))

theorem pt_01 (n : Nat) (a b c d : Int) :
    (op_01 n a b c d).1*(op_01 n a b c d).2.2.2 - (op_01 n a b c d).2.1*(op_01 n a b c d).2.2.1 = a*d-b*c := by
  induction n <;> simp_all [op_01]
  <;> ring_nf
  <;> linarith

#print axioms pt_01
