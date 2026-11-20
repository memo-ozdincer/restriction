import Mathlib
import Aesop

set_option maxHeartbeats 0

open BigOperators Real Nat Topology Rat

def op_00 : Nat → Int → Int → Int → Int → Int × Int × Int × Int
  | 0, a, b, c, d => (a,b,c,d)
  | n+1, a, b, c, d => op_00 n (a+2*c) (b+2*d) (c+3*(a+2*c)) (d+3*(b+2*d))

theorem pt_00 (n : Nat) (a b c d : Int) :
    (op_00 n a b c d).1*(op_00 n a b c d).2.2.2 - (op_00 n a b c d).2.1*(op_00 n a b c d).2.2.1 = a*d-b*c := by
  induction n generalizing a b c d <;> simp_all [op_00]
  <;> ring_nf
  <;> linarith

#print axioms pt_00
