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
    ∃ combine : ℤ → ℤ → ℤ → ℤ → ℤ → ℤ × ℤ,
      (∀ rho u v p q : ℤ,
        (combine rho u v p q).1 ^ 2 + rho * (combine rho u v p q).2 ^ 2 =
          (u^2+rho*v^2)*(p^2+rho*q^2)) ∧
      (∀ rho u v : ℤ, combine rho u v 1 0 = (u,v)) ∧
      (∀ rho u v : ℤ, combine rho u v 0 1 = (-rho*v,u)) := by
  rcases source_contract with ⟨f, hNorm, hUnit, hBasis⟩
  refine ⟨fun rho u v p q => f (((1)*(rho))) u v p q, ?_⟩
  constructor
  · intro rho u v p q
    convert hNorm (((1)*(rho))) u v p q using 1 <;> ring
  constructor
  · intro rho u v
    exact hUnit (((1)*(rho))) u v
  · intro rho u v
    convert hBasis (((1)*(rho))) u v using 1 <;> simp <;> ring <;> simp

#print axioms source_contract
#print axioms target
