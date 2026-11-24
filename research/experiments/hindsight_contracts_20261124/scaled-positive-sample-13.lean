import Mathlib
import Aesop

set_option maxHeartbeats 0

open BigOperators Real Nat Topology Rat

theorem target :
    ∃ f : ℤ → ℤ → ℤ → ℤ → ℤ → ℤ × ℤ,
      (∀ d a b x y : ℤ,
        (f d a b x y).1 ^ 2 + (2*d) * (f d a b x y).2 ^ 2 =
          (a^2+(2*d)*b^2)*(x^2+(2*d)*y^2)) ∧
      (∀ d a b : ℤ, f d a b 1 0 = (a,b)) ∧
      (∀ d a b : ℤ, f d a b 0 1 = (-(2*d)*b,a)) := by
  refine' ⟨fun d a b x y => (a*x - (2*d)*b*y, a*y + b*x), _, _, _⟩
  <;> intros <;> simp_all only [mul_comm, mul_left_comm, mul_assoc, Int.negSucc_coe,
    Int.ofNat_eq_coe, Int.neg_mul, Int.mul_neg, Int.neg_neg, Int.neg_zero, Int.mul_zero,
    Int.zero_mul, Int.add_zero, Int.zero_add, Int.sub_eq_add_neg]
  <;> ring_nf
  <;> aesop

#print axioms target
