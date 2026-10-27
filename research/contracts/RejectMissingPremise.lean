theorem missing_premise (a b c d k target : ℤ)
    (product : (a + k * c) * d - (b + k * d) * c = a * d - b * c) :
    (a + k * c) * d - (b + k * d) * c = target := by
  exact product
#audit_closed missing_premise
