import argparse
import tempfile
import unittest
from pathlib import Path
import numpy as np
from environment import prufer_to_edges, edges_to_prufer, independence_polynomial, score
from local_search import norm_edge, tree_path, cycle_neighbors, optimize, run, parse_args
from train import Evaluator


class LocalTests(unittest.TestCase):
    def test_each_cycle_deletion_is_tree_and_original_cache(self):
        e={norm_edge(a,b) for a,b in prufer_to_edges([0,1,2,3],6)}
        a=(0,5); path=tree_path(6,e,*a)
        ns=cycle_neighbors(6,e,a);self.assertEqual(len(ns),len(path))
        self.assertEqual({x[0] for x in ns},set(path))
        for rem,tree in ns:
            self.assertEqual(tree,(e|{a})-{rem})
            code=edges_to_prufer(6,tree);self.assertEqual(tree,{norm_edge(a,b) for a,b in prufer_to_edges(code,6)})

    def test_budget_and_greedy_monotonicity(self):
        for strategy in ('single','cycle'):
            ev=Evaluator(argparse.Namespace(n=12,family='independence',index=6,required=1,score='raw'))
            rng=np.random.default_rng(23);code=rng.integers(12,size=10)
            out=optimize(code,ev,rng,max_swaps=10,budget=40,strategy=strategy)
            self.assertEqual(out['calls'],ev.calls);self.assertLessEqual(ev.calls,40)
            self.assertGreaterEqual(out['record'][0],out['initial'][0]);self.assertLessEqual(out['swaps'],10)
            self.assertEqual(out['record'][0],score(independence_polynomial(12,prufer_to_edges(out['code'],12)),6))

    def test_cycle_budget_rejects_partial(self):
        ev=Evaluator(argparse.Namespace(n=6,family='independence',index=3,required=1,score='raw'))
        out=optimize([0,1,2,3],ev,np.random.default_rng(1),budget=2)
        self.assertEqual(ev.calls,1);self.assertEqual(out['stop_reason'],'query_budget')

    def test_query_budget_and_determinism(self):
        with tempfile.TemporaryDirectory() as d:
            argv=['--n','8','--index','4','--queries','100','--max-swaps','3','--starts','cem','--batch','5','--eval-batch','4','--output',str(Path(d)/'out.json')]
            a=run(parse_args(argv));b=run(parse_args(argv))
            self.assertEqual(a['train']['calls'],100);self.assertEqual(a['train'],b['train']);self.assertEqual(a['history'],b['history']);self.assertEqual(a['policy'],b['policy'])


if __name__=='__main__':unittest.main()
