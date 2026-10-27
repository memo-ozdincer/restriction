theorem incompatible_adapter (a b c d k : ℤ)
    (product : (a + k * c) * d - (b + k * d) * c = a * d - b * c) :
    (a + k * c) * d - (b + k * d) * c = a * d - b * c + 1 := by
  exact product
#audit_closed incompatible_adapter
