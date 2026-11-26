import json
from pathlib import Path
import unittest
from environment import apply,cost,descend,held_karp,moves,distance_matrix
from screen import verify,HORIZON

class TestEnvironment(unittest.TestCase):
    def setUp(self):
        self.task=json.loads(Path(__file__).with_name('instance.json').read_text())

    def test_exact_square(self):
        matrix=distance_matrix([(0,0),(3,0),(3,4),(0,4)])
        self.assertEqual(held_karp(matrix),14)
        self.assertEqual(cost(matrix,(0,1,2,3)),14)

    def test_frozen_plateau(self):
        task=self.task; root=tuple(task['plateau'])
        self.assertEqual(held_karp(task['matrix']),334)
        self.assertEqual(cost(task['matrix'],root),341)
        self.assertTrue(all(cost(task['matrix'],apply(root,m))>341 for m in moves(11)))
        self.assertEqual(descend(task['matrix'],tuple(task['descent'][0]))[-1],root)

    def test_all_kicks_reversible(self):
        task=self.task; root=tuple(task['plateau'])
        for m in moves(11):self.assertEqual(apply(apply(root,m),m),root)
        for state in task['states'][1:]:self.assertEqual(apply(root,tuple(state['kick'])),tuple(state['tour']))

    def test_zero_and_illegal(self):
        task=self.task; state=task['states'][0]
        self.assertEqual(verify(task,state,{'actions':[]})['reward'],0)
        with self.assertRaises(ValueError): verify(task,state,{'actions':[{'i':0,'j':2}]})

if __name__=='__main__':unittest.main()
