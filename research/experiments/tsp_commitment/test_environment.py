import unittest
import itertools
import json
from environment import distances, cost, residual_solver, bound, construct, density, verify, ROOT


class Tests(unittest.TestCase):
    def test_exact_square(self):
        matrix=distances([(0,0),(0,3),(4,3),(4,0)])
        self.assertEqual(matrix[0][2],5)
        self.assertEqual(bound(matrix,[0],residual_solver(matrix)),14)
        self.assertEqual(cost(matrix,[0,1,2,3]),14)

    def test_prefix_bound_against_brute(self):
        matrix=distances([(0,0),(2,3),(9,4),(5,8),(6,1),(2,6)])
        for prefix in ([0],[0,4],[0,3,5]):
            remaining=set(range(len(matrix)))-set(prefix)
            exact=min(cost(matrix,prefix+list(p)) for p in itertools.permutations(remaining))
            self.assertEqual(bound(matrix,prefix,residual_solver(matrix)),exact)

    def test_frozen_case_and_density(self):
        case=json.loads((ROOT/"case.json").read_text())
        rebuilt=construct()
        self.assertEqual(case["seed"],rebuilt["seed"])
        self.assertEqual(case["prefix_bounds"],rebuilt["prefix_bounds"])
        for name,n in (("locked_density",5),("released_density",4)):
            self.assertEqual(case[name],density(case,case["greedy"][:n]))

    def test_verifier(self):
        case=json.loads((ROOT/"case.json").read_text())
        self.assertEqual(verify(case,[0]*12,[0])["reward"],0)
        self.assertEqual(verify(case,case["greedy"],case["greedy"][:5])["reward"],0)
        self.assertFalse(verify(case,case["greedy"],[0,1])["prefix_valid"])


if __name__=="__main__": unittest.main()
