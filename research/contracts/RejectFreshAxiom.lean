axiom fresh_untrusted_axiom : (0 : ℤ) = 1
theorem axiom_certificate : (0 : ℤ) = 1 := fresh_untrusted_axiom
#audit_closed axiom_certificate
