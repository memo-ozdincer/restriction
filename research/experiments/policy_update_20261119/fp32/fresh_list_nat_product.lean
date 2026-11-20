import Mathlib
import Aesop

set_option maxHeartbeats 0

open BigOperators Real Nat Topology Rat

theorem target (P : List Int → Nat → Prop) (h0 : P [] 0)
    (hs : ∀ a xs n, P xs n → P (a :: xs) n) (ht : ∀ xs n, P xs n → P xs (n+1)) :
    ∀ xs n, P xs n := by
  intro xs n
  induction xs <;> induction n <;> simp_all

#print axioms target
