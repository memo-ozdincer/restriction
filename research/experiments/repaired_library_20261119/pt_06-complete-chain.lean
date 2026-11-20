import Mathlib
import Aesop

set_option maxHeartbeats 0

open BigOperators Real Nat Topology Rat

def op_06 : Nat → Int → Int → Int → Int → Int × Int × Int × Int
  | 0, a, b, c, d => (a,b,c,d)
  | n+1, a, b, c, d => op_06 n (a+2*c) (b+2*d) (c+5*(a+2*c)) (d+5*(b+2*d))

theorem linked_contract (n : Nat) (a b c d : Int) :
    (op_06 n a b c d).1*(op_06 n a b c d).2.2.2 - (op_06 n a b c d).2.1*(op_06 n a b c d).2.2.1 = a*d-b*c := by
  induction n generalizing a b c d <;>
  simp_all [op_06]
  ring_nf

theorem pt_06 (n : Nat) (a b c d : Int) (h : a*d-b*c ≠ 0) :
    (op_06 n a b c d).1 ≠ 0 ∨ (op_06 n a b c d).2.1 ≠ 0 := by
  have hbridge : (op_06 n a b c d).1*(op_06 n a b c d).2.2.2 - (op_06 n a b c d).2.1*(op_06 n a b c d).2.2.1 = a*d-b*c := linked_contract n a b c d
  have h₁ : (op_06 n a b c d).1 ≠ 0 ∨ (op_06 n a b c d).2.1 ≠ 0 := by
    contrapose! h
    simp_all
  assumption

#print axioms pt_06
