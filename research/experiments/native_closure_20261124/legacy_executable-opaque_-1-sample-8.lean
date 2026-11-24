import Mathlib
import Aesop

set_option maxHeartbeats 0

open BigOperators Real Nat Topology Rat

theorem target :
    ∃ f : (ℤ → ℤ) → ℤ → ℤ → ℤ → ℤ → ℤ → ℤ × ℤ,
      (∀ (w : ℤ → ℤ) (d a b x y : ℤ),
        (f w d a b x y).1 ^ 2 + (-(w d)) * (f w d a b x y).2 ^ 2 =
          (a^2+(-(w d))*b^2)*(x^2+(-(w d))*y^2)) ∧
      (∀ (w : ℤ → ℤ) (d a b : ℤ), f w d a b 1 0 = (a,b)) ∧
      (∀ (w : ℤ → ℤ) (d a b : ℤ), f w d a b 0 1 = (-(-(w d))*b,a)) := by
  refine ⟨fun w d a b x y => (a * x - (-(w d)) * b * y, b * x + a * y), ?_⟩
  dsimp
  constructor
  · intros
    ring_nf
  · constructor
    · intros
      simp
    · intros
      simp

#print axioms target
