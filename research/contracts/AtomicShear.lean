/- Training-permitted atom: one row shear only. No iteration, nonzero-row or
   Bezout target, frozen task, or multi-edge held-out dependency graph. -/
theorem atomic_shear (a b c d k : ℤ) :
    (a + k * c) * d - (b + k * d) * c = a * d - b * c := by
  ring

theorem atomic_shear_renamed (p q r s coefficient : ℤ) :
    (p + coefficient * r) * s - (q + coefficient * s) * r = p * s - q * r := by
  ring

-- Same atomic identity, but a genuinely different local type.
theorem atomic_shear_rational (a b c d k : ℚ) :
    (a + k * c) * d - (b + k * d) * c = a * d - b * c := by
  ring

-- Preserve local let values in the closed interface, not merely pretty goals.
theorem atomic_shear_value_one :
    let k : ℤ := 1
    ∀ a b c d : ℤ, (a + k * c) * d - (b + k * d) * c = a * d - b * c := by
  dsimp
  intros
  ring

theorem atomic_shear_value_two :
    let k : ℤ := 2
    ∀ a b c d : ℤ, (a + k * c) * d - (b + k * d) * c = a * d - b * c := by
  dsimp
  intros
  ring

-- The adapter consumes the checked product plus its explicit extra premise.
theorem shear_adapter (a b c d k target : ℤ)
    (product : (a + k * c) * d - (b + k * d) * c = a * d - b * c)
    (initial : a * d - b * c = target) :
    (a + k * c) * d - (b + k * d) * c = target := by
  exact product.trans initial

-- Counterexamples establish impossible interfaces, beyond a failed tactic.
theorem no_adapter_without_premise :
    ¬ (∀ a b c d k target : ℤ,
      (a + k * c) * d - (b + k * d) * c = a * d - b * c →
      (a + k * c) * d - (b + k * d) * c = target) := by
  intro h
  have bad := h 0 0 0 0 0 1 (by norm_num)
  norm_num at bad

theorem no_incompatible_adapter :
    ¬ (∀ a b c d k : ℤ,
      (a + k * c) * d - (b + k * d) * c = a * d - b * c →
      (a + k * c) * d - (b + k * d) * c = a * d - b * c + 1) := by
  intro h
  have bad := h 0 0 0 0 0 (by norm_num)
  norm_num at bad

#audit_closed atomic_shear
#audit_closed atomic_shear_renamed
#audit_closed atomic_shear_rational
#audit_closed atomic_shear_value_one
#audit_closed atomic_shear_value_two
#audit_closed shear_adapter
#audit_closed no_adapter_without_premise
#audit_closed no_incompatible_adapter
#compare_closed atomic_shear atomic_shear_renamed
#compare_closed atomic_shear atomic_shear_rational
#compare_closed atomic_shear_value_one atomic_shear_value_two
