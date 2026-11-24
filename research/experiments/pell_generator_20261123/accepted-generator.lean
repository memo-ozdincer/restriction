import Mathlib
import Aesop

set_option maxHeartbeats 0

open BigOperators Real Nat Topology Rat

-- A verified starting solution is (2, 1).
theorem target : ∃ x y : ℤ, x^2 - 3*y^2 = 1 ∧ 362 < x ∧ x ≤ 1448 := by
  let step (p : ℤ × ℤ) : ℤ × ℤ :=
    if 362 < p.1 then p else (2*p.1+3*p.2, 1*p.1+2*p.2)
  let q := Nat.rec (motive := fun _ => ℤ × ℤ) ((2, 1) : ℤ × ℤ) (fun _ p => step p) 8
  use q.1, q.2
  norm_num [q, step] <;> decide

#print axioms target