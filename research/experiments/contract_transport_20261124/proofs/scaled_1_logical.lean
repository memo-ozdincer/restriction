import Mathlib
import Aesop

set_option maxHeartbeats 0

open BigOperators Real Nat Topology Rat

theorem source_contract :
    ∃ f : ℤ → ℤ → ℤ → ℤ → ℤ → ℤ × ℤ,
      (∀ d a b x y : ℤ,
        (f d a b x y).1 ^ 2 + d * (f d a b x y).2 ^ 2 =
          (a^2+d*b^2)*(x^2+d*y^2)) ∧
      (∀ d a b : ℤ, f d a b 1 0 = (a,b)) ∧
      (∀ d a b : ℤ, f d a b 0 1 = (-d*b,a)) := by
  use fun d a b x y => (a * x - d * b * y, b * x + a * y)
  exact ⟨fun d a b x y => by ring, fun d a b => by simp, fun d a b => by simp⟩


theorem target :
    ∃ f : ℤ → ℤ → ℤ → ℤ → ℤ → ℤ × ℤ,
      (∀ d a b x y : ℤ,
        (f d a b x y).1 ^ 2 + (2*d) * (f d a b x y).2 ^ 2 =
          (a^2+(2*d)*b^2)*(x^2+(2*d)*y^2)) ∧
      (∀ d a b : ℤ, f d a b 1 0 = (a,b)) ∧
      (∀ d a b : ℤ, f d a b 0 1 = (-(2*d)*b,a)) := by
  rcases source_contract with ⟨f, hNorm, hUnit, hBasis⟩
  refine ⟨fun d a b x y => f (((2)*(d))) a b x y, ?_⟩
  constructor
  · intro d a b x y
    convert hNorm (((2)*(d))) a b x y using 1 <;> ring
  constructor
  · intro d a b
    exact hUnit (((2)*(d))) a b
  · intro d a b
    convert hBasis (((2)*(d))) a b using 1 <;> simp <;> ring <;> simp

#print axioms source_contract
#print axioms target
