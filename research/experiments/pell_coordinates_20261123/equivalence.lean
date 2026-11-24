import Mathlib

def Allowed (x : ℤ) := x.natAbs ≠ 1 ∧ x.natAbs ≠ 5

theorem forward_equiv :
    (∃ u v : ℤ, u^2 - 6*v^2 = 1 ∧ Allowed (5*u+12*v)) ↔
    (∃ x y : ℤ, x^2 - 6*y^2 = 1 ∧ Allowed x) := by
  constructor
  · rintro ⟨u,v,hn,ha⟩
    exact ⟨5*u+12*v, 5*v+2*u, by nlinarith [hn], ha⟩
  · rintro ⟨x,y,hn,ha⟩
    refine ⟨5*x-12*y, 5*y-2*x, by nlinarith [hn], ?_⟩
    convert ha using 1 <;> ring_nf

#print axioms forward_equiv

theorem inverse_equiv :
    (∃ u v : ℤ, u^2 - 6*v^2 = 1 ∧ Allowed (5*u-12*v)) ↔
    (∃ x y : ℤ, x^2 - 6*y^2 = 1 ∧ Allowed x) := by
  constructor
  · rintro ⟨u,v,hn,ha⟩
    exact ⟨5*u-12*v, 5*v-2*u, by nlinarith [hn], ha⟩
  · rintro ⟨x,y,hn,ha⟩
    refine ⟨5*x+12*y, 5*y+2*x, by nlinarith [hn], ?_⟩
    convert ha using 1 <;> ring_nf

#print axioms inverse_equiv
