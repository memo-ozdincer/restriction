import Mathlib
import Aesop

set_option maxHeartbeats 0

open BigOperators Real Nat Topology Rat

def op_05 : Nat → Int → Int → Int → Int → Int × Int × Int × Int
  | 0, a, b, c, d => (a,b,c,d)
  | n+1, a, b, c, d => op_05 n (a+3*c) (b+3*d) (c+2*(a+3*c)) (d+2*(b+3*d))

theorem linked_contract (n : Nat) (a b c d : Int) :
    (op_05 n a b c d).1*(op_05 n a b c d).2.2.2 - (op_05 n a b c d).2.1*(op_05 n a b c d).2.2.1 = a*d-b*c := by
  induction n generalizing a b c d <;> simp_all [op_05]
  <;> ring_nf
  <;> linarith

theorem pt_05 (n : Nat) (a b c d : Int) (h : a*d-b*c ≠ 0) :
    (op_05 n a b c d).1 ≠ 0 ∨ (op_05 n a b c d).2.1 ≠ 0 := by
  have hbridge : (op_05 n a b c d).1*(op_05 n a b c d).2.2.2 - (op_05 n a b c d).2.1*(op_05 n a b c d).2.2.1 = a*d-b*c := linked_contract n a b c d
  by_contra!
  apply h
  aesop

#print axioms pt_05
