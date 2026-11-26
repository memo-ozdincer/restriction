import unittest
import numpy as np

from environment import (make_environment,tensor_value,tensor_neighbors,
                         sokoban_move,board_tiles)
from train import initial_weights,rollout,starts_for,transition_table,train


class Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tensor=make_environment("tensor")
        cls.sokoban=make_environment("sokoban")

    def test_tensor_invariant_and_cap(self):
        env=self.tensor
        target=env.metadata["target"]
        for i,s in enumerate(env.states):
            self.assertEqual(tensor_value(s),target)
            for j in env.transitions[i]:
                if j>=0:
                    self.assertLessEqual(len(env.states[j]),5)
                    self.assertEqual(tensor_value(env.states[j]),target)
        table=transition_table(env,"ordinary")
        reachable={env.root}
        while True:
            bigger=reachable|{int(j) for i in reachable for j in table[i] if j>=0}
            if bigger==reachable:break
            reachable=bigger
        self.assertEqual(len(reachable),env.metadata["cap4_states"])
        self.assertTrue(any(env.terminal[i] for i in reachable))

    def test_sokoban_transitions(self):
        env=self.sokoban
        tiles,ids,goals=board_tiles()
        for i,s in enumerate(env.states):
            for a,j in enumerate(env.transitions[i]):
                self.assertEqual(env.states[j],sokoban_move(s,a,tiles,ids))
            self.assertEqual(env.terminal[i],s[:2]==goals)
            if env.distances[i]>0:
                self.assertTrue(any(env.distances[j]==env.distances[i]-1 for j in env.transitions[i]))

    def test_same_group_starts(self):
        env=self.sokoban
        a=starts_for(env,"solvable",np.random.default_rng(42),40,8).reshape(-1,8)
        self.assertTrue(np.all(a==a[:,0,None]))
        self.assertTrue(np.all(env.distances[a]>0))

    def test_rollout_smoke_and_accounting(self):
        for env in (self.tensor,self.sokoban):
            row=train(env,"ordinary",42,updates=2,groups=2,group_size=2,eval_count=4)
            self.assertEqual(row["totals"]["slots"],2*2*2*env.horizon)
            self.assertEqual(row["totals"]["groups"],4)
            self.assertLessEqual(row["totals"]["active_steps"],row["totals"]["slots"])


if __name__=="__main__":
    unittest.main()
