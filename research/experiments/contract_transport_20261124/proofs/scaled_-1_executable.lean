import Mathlib
import Aesop

set_option maxHeartbeats 0

open BigOperators Real Nat Topology Rat

theorem target :
    ∃ f : ℤ → ℤ → ℤ → ℤ → ℤ → ℤ × ℤ,
      (∀ d a b x y : ℤ,
        (f d a b x y).1 ^ 2 - (2*d) * (f d a b x y).2 ^ 2 =
          (a^2-(2*d)*b^2)*(x^2-(2*d)*y^2)) ∧
      (∀ d a b : ℤ, f d a b 1 0 = (a,b)) ∧
      (∀ d a b : ℤ, f d a b 0 1 = ((2*d)*b,a)) := by
  refine ⟨fun d a b x y => (fun d a b x y => (a * x - d * b * y, b * x + a * y)) (((-2)*(d))) a b x y, ?_⟩
  dsimp
  constructor
  · intros; ring
  constructor
  · intros; simp <;> ring
  · intros; simp <;> ring

#print axioms target
