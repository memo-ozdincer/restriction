import Mathlib
import Aesop

set_option maxHeartbeats 0

open BigOperators Real Nat Topology Rat

theorem translated_witness_family (k m : ℕ) (hm : 0 < m) (S : Finset ℕ) (hS : S = Finset.Icc 1 (51 * m)) (A : Finset ℕ) (hA : A ⊆ S) (hA' : A.card = 50 * m) : let n := 51*m+1; let X : Finset ℕ := {n,n+k+4,n+2*k+5}; let Y : Finset ℕ := {n+1,n+k+2,n+2*k+6}; X.Nonempty ∧ Y.Nonempty ∧ (X ∩ Y = ∅ ∧ Y ∩ A = ∅ ∧ A ∩ X = ∅ ∧ (∑ x in X, x = ∑ y in Y, y ∧ ∑ x in X, x ^ 2 = ∑ y in Y, y ^ 2))   := by
  dsimp only
  generalize hn : 51*m+1 = n
  have bound (z : ℕ) (hz : z ∈ A) : z ≤ 51*m := by
    have h := hA hz
    rw [hS] at h
    exact (Finset.mem_Icc.mp h).2
  change ({n,n+k+4,n+2*k+5} : Finset ℕ).Nonempty ∧ _
  refine ⟨?_, ?_, ?_, ?_, ?_, ?_, ?_⟩
  · exact ⟨n, by simp⟩
  · exact ⟨n+1, by simp⟩
  · ext z
    simp only [Finset.mem_inter, Finset.mem_insert, Finset.mem_singleton, Finset.not_mem_empty, iff_false]
    omega
  · ext z
    simp only [Finset.mem_inter, Finset.mem_insert, Finset.mem_singleton, Finset.not_mem_empty, iff_false]
    intro ⟨hz, ha⟩
    have := bound z ha
    omega
  · ext z
    simp only [Finset.mem_inter, Finset.mem_insert, Finset.mem_singleton, Finset.not_mem_empty, iff_false]
    intro ⟨ha, hz⟩
    have := bound z ha
    omega
  · simp [Finset.sum_insert, show n ≠ n+k+4 by omega, show n ≠ n+2*k+5 by omega,
      show n+k+4 ≠ n+2*k+5 by omega, show n+1 ≠ n+k+2 by omega, show n+1 ≠ n+2*k+6 by omega,
      show n+k+2 ≠ n+2*k+6 by omega] <;> ring
  · simp [Finset.sum_insert, show n ≠ n+k+4 by omega, show n ≠ n+2*k+5 by omega,
      show n+k+4 ≠ n+2*k+5 by omega, show n+1 ≠ n+k+2 by omega, show n+1 ≠ n+2*k+6 by omega,
      show n+k+2 ≠ n+2*k+6 by omega] <;> ring

#print axioms translated_witness_family
