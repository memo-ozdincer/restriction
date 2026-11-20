import Mathlib
import Aesop

set_option maxHeartbeats 0

open BigOperators Real Nat Topology Rat

def op_09 : Nat → Int → Int → Int → Int → Int × Int × Int × Int
  | 0, a, b, c, d => (a,b,c,d)
  | n+1, a, b, c, d => op_09 n (a+3*c) (b+3*d) (c+2*(a+3*c)) (d+2*(b+3*d))

theorem linked_contract (n : Nat) (a b c d : Int) :
    (op_09 n a b c d).1*(op_09 n a b c d).2.2.2 - (op_09 n a b c d).2.1*(op_09 n a b c d).2.2.1 = a*d-b*c := by
  induction n generalizing a b c d <;> simp_all [op_09]
  <;> ring_nf
  <;> linarith

theorem witness_constructor (x y z w : Int) (h : x*w-y*z = 1) : ∃ u v : Int, u*x+v*y = 1 := by
  exact ⟨w, -z, by linarith⟩

theorem pt_09 (n : Nat) (a b c d : Int) (h : a*d-b*c = 1) :
    ∃ u v : Int, u*(op_09 n a b c d).1 + v*(op_09 n a b c d).2.1 = 1 := by
  exact witness_constructor _ _ _ _ (Eq.trans (linked_contract n a b c d) h)

#print axioms pt_09
