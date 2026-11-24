import Mathlib
import Aesop

set_option maxHeartbeats 0

open BigOperators Real Nat Topology Rat

theorem target :
    ∃ combine : ℤ → ℤ → ℤ → ℤ → ℤ → ℤ × ℤ,
      (∀ rho u v p q : ℤ,
        (combine rho u v p q).1 ^ 2 + rho * (combine rho u v p q).2 ^ 2 =
          (u^2+rho*v^2)*(p^2+rho*q^2)) ∧
      (∀ rho u v : ℤ, combine rho u v 1 0 = (u,v)) ∧
      (∀ rho u v : ℤ, combine rho u v 0 1 = (-rho*v,u)) := by
  refine ⟨fun rho u v p q => (fun d a b x y => (a * x - d * b * y, b * x + a * y)) (((1)*(rho))) u v p q, ?_⟩
  dsimp
  constructor
  · intros; ring
  constructor
  · intros; simp <;> ring
  · intros; simp <;> ring

#print axioms target
