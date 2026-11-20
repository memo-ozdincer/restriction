import Mathlib
import Aesop

set_option maxHeartbeats 0

open BigOperators Real Nat Topology Rat

theorem target (P : Nat → Nat → Prop) (h0 : P 0 0)
    (hs : ∀ i j, P i j → P (i+1) j) (ht : ∀ i j, P i j → P i (j+1)) :
    ∀ i j, P i j := by
  intro i j
  induction i <;> induction j <;> simp_all

#print axioms target
