"""Deterministic unit/smoke tests for CPU learner and intervention semantics."""
import tempfile
import unittest
from pathlib import Path
import numpy as np
from train import Policy, random_edge_edit, crossover, select_mask, pg_weights, cem_weights, run, parse_args
from environment import prufer_to_edges, edges_to_prufer, tree_id


class TrainTests(unittest.TestCase):
    def test_valid_tree_edits(self):
        rng=np.random.default_rng(4)
        for n in (3,8,26):
            for _ in range(20):
                a,b=rng.integers(n,size=(2,n-2))
                for c in (random_edge_edit(n,a,rng),crossover(n,a,b,rng)[0]):
                    self.assertEqual(tuple(c),edges_to_prufer(n,prufer_to_edges(c,n)))
                    self.assertEqual(len(prufer_to_edges(c,n)),n-1)

    def test_uniform_policy_reproducibility(self):
        p=Policy(8); q=Policy(8)
        a=p.sample(12,np.random.default_rng(55)); b=q.sample(12,np.random.default_rng(55))
        np.testing.assert_array_equal(a,b)
        self.assertFalse(p.update(a,np.zeros(12),.01))
        self.assertEqual(p.t,0)
        for x in p.params:self.assertFalse(np.any(x))

    def test_binary_no_signal(self):
        for fn in (pg_weights,lambda *x:cem_weights(*x,.25)):
            for value in (0,1):
                w,count=fn([value]*4,[value]*4,['a']*4,'balanced','binary',np.random.default_rng(8))
                self.assertFalse(np.any(w));self.assertEqual(count,0)

    def test_constant_normalized_pg_has_no_signal(self):
        # The exact same float is repeated, yet NumPy's rounded mean on
        # this batch can differ from the value, producing a tiny std.
        for variant in ('ordinary','balanced','matched'):
            vals=[-.1]*128
            w,count=pg_weights(vals,[0]*128,['same']*128,variant,'normalized',np.random.default_rng(8))
            self.assertFalse(np.any(w));self.assertEqual(count,0)

    def test_correct_mask_not_failure(self):
        vals=[0,0,1,1,1,1]; ids=['bad','bad','a','a','a','b'];hits=vals
        ordinary,_=pg_weights(vals,hits,ids,'ordinary','binary',np.random.default_rng(5))
        for variant in ('balanced','matched'):
            w,blocked=pg_weights(vals,hits,ids,variant,'binary',np.random.default_rng(5))
            self.assertEqual(blocked,2); np.testing.assert_array_equal(w[:2],ordinary[:2])
            self.assertEqual(np.count_nonzero(w[2:]),2)
        w,_=pg_weights(vals,hits,ids,'balanced','binary',np.random.default_rng(5))
        self.assertEqual(np.count_nonzero(w[2:5]),1);self.assertGreater(w[5],0)

    def test_dense_balance(self):
        vals=[-1,-1,-2,-2];ids=['a','a','b','c'];hits=[0]*4
        for variant in ('balanced','matched'):
            w,count=cem_weights(vals,hits,ids,variant,'raw',np.random.default_rng(6),.5)
            self.assertEqual(count,1); self.assertEqual(np.count_nonzero(w),1)

    def test_queries_and_repeatability(self):
        with tempfile.TemporaryDirectory() as d:
            for method,variant,calls in [('random','ordinary',16),('pg','balanced',16),
                    ('cem','crossover',16),('pattern-lite','edit',48),('hill','ordinary',24)]:
                cfg=['--n','8','--index','3','--steps','2','--batch','8','--eval-batch','4','--eval-every','1',
                    '--method',method,'--variant',variant,'--local-steps','2','--output',str(Path(d)/'o.json')]
                a=run(parse_args(cfg));b=run(parse_args(cfg))
                self.assertEqual(a['train']['calls'],calls);self.assertEqual(a['evaluation']['calls'],12)
                self.assertEqual(a['train'],b['train']);self.assertEqual(a['history'],b['history'])
                self.assertEqual(a['policy'],b['policy'])


if __name__=='__main__':unittest.main()
