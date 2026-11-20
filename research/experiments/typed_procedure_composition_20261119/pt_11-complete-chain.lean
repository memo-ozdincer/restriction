import Mathlib
import Aesop

set_option maxHeartbeats 0

open BigOperators Real Nat Topology Rat

def op_11 : Nat → Int → Int → Int → Int → Int × Int × Int × Int
  | 0, a, b, c, d => (a,b,c,d)
  | n+1, a, b, c, d => op_11 n (a+5*c) (b+5*d) (c+2*(a+5*c)) (d+2*(b+5*d))

theorem linked_contract (n : Nat) (a b c d : Int) :
    (op_11 n a b c d).1*(op_11 n a b c d).2.2.2 - (op_11 n a b c d).2.1*(op_11 n a b c d).2.2.1 = a*d-b*c := by
  induction n generalizing a b c d with
  | zero =>
    simp [op_11]
  | succ n ih =>
    simp [op_11, ih, mul_add, mul_comm, mul_left_comm, mul_assoc]
    ring

theorem witness_constructor (x y z w : Int) (h : x*w-y*z = 1) : ∃ u v : Int, u*x+v*y = 1 := by
  exact ⟨w, -z, by linarith⟩

theorem pt_11 (n : Nat) (a b c d : Int) (h : a*d-b*c = 1) :
    ∃ u v : Int, u*(op_11 n a b c d).1 + v*(op_11 n a b c d).2.1 = 1 := by
  exact witness_constructor _ _ _ _ (Eq.trans (linked_contract n a b c d) h)

#print axioms pt_11
