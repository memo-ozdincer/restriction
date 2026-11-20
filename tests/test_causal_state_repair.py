import unittest
from scripts.project.causal_state_repair import lift


class StateLiftTests(unittest.TestCase):
    def test_core_preserves_every_other_byte(self):
        body='  induction n with\n  | zero => simp [op]\n  | succ n ih => simp [op, ih]\n'
        fixed,reason=lift(body,['a','b'])
        self.assertIsNone(reason)
        self.assertEqual(fixed.replace(' generalizing a b','',1),body)
        self.assertIn('induction n generalizing a b with',fixed)

    def test_prime_places_clause_after_binders(self):
        body="  induction' n with n hn\n  simp_all\n"
        fixed,reason=lift(body,['x'])
        self.assertIsNone(reason)
        self.assertEqual(fixed,"  induction' n with n hn generalizing x\n  simp_all\n")
        self.assertEqual(lift(body,[]),(body,None))

    def test_ambiguous_or_already_lifted_proofs_are_not_rewritten(self):
        for body in ['induction n generalizing x\n','induction n\ninduction n\n',
                     '/-\ninduction n\n-/\n','induction n using other\n']:
            fixed,reason=lift(body,['x'])
            self.assertIsNone(fixed)
            self.assertIsNotNone(reason)


if __name__=='__main__':unittest.main()
