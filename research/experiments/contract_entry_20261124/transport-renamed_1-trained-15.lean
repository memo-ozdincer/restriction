import Mathlib
import Aesop

set_option maxHeartbeats 0

open BigOperators Real Nat Topology Rat

theorem target :
    ∃ combine : (ℤ → ℤ) → ℤ → ℤ → ℤ → ℤ → ℤ → ℤ × ℤ,
      (∀ (metric : ℤ → ℤ) (rho u v p q : ℤ),
        (combine metric rho u v p q).1 ^ 2 + (metric rho) * (combine metric rho u v p q).2 ^ 2 =
          (u^2+(metric rho)*v^2)*(p^2+(metric rho)*q^2)) ∧
      (∀ (metric : ℤ → ℤ) (rho u v : ℤ), combine metric rho u v 1 0 = (u,v)) ∧
      (∀ (metric : ℤ → ℤ) (rho u v : ℤ), combine metric rho u v 0 1 = (-(metric rho)*v,u)) := by
  have source_contract :
    ∃ combine : (ℤ → ℤ) → ℤ → ℤ → ℤ → ℤ → ℤ → ℤ × ℤ,
      (∀ (metric : ℤ → ℤ) (rho u v p q : ℤ),
        (combine metric rho u v p q).1 ^ 2 + (metric rho) * (combine metric rho u v p q).2 ^ 2 =
          (u^2+(metric rho)*v^2)*(p^2+(metric rho)*q^2)) ∧
      (∀ (metric : ℤ → ℤ) (rho u v : ℤ), combine metric rho u v 1 0 = (u,v)) ∧
      (∀ (metric : ℤ → ℤ) (rho u v : ℤ), combine metric rho u v 0 1 = (-(metric rho)*v,u)) := by
    use fun metric rho u v p q => (u * p - metric rho * v * q, u * q + v * p)
    exact ⟨by
      intros
      ring_nf,
      by
      intros
      ring_nf,
      by
      intros
      ring_nf⟩
  aesop

#print axioms target
