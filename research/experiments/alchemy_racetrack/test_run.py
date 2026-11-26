"""Sanity-check physical transitions and replay saved official evaluations."""
import json
from pathlib import Path
import unittest
import numpy as np
import run as r

class EnvironmentTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):r.initialize()
    def test_collision_and_crossing(self):
        t,c,f=r.ENV; a=int(np.flatnonzero((r.A==[0,0]).all(1))[0])
        q=r.encode(11,1,2,0)
        self.assertEqual(t[3,q,a],r.encode(11,1,0,0))
        self.assertTrue(c[3,q,a])
        s=r.encode(11,6,2,0)
        self.assertEqual(t[3,s,a],r.encode(13,6,2,0))
        self.assertFalse(c[3,s,a])
    def test_prefix_reachable(self):
        t,c,f=r.ENV
        maps=np.repeat(r.TRAIN-1,10);length=np.tile(np.arange(1,9),5)
        x=r.reset('random',maps,length,np.random.default_rng(1),None)
        self.assertFalse(r.GOAL[x].any())
        states={r.ROOT}
        for i in range(1,9):
            states=set(t[0,list(states)].ravel())
            # Separate reachability check on a single geometry.
            m=np.array([0]);q=r.reset('random',m,np.array([i]),np.random.default_rng(i),None)
            self.assertIn(int(q[0]),states)

def audit(path):
    r.initialize();t,c,f=r.ENV
    data=json.loads(Path(path).read_text())
    assert sorted(x["seed"] for x in data["rows"])==list(r.SEEDS)
    for row in data["rows"]:
        for eval in [row["baseline"]]+[v[k] for v in row["arms"].values() for k in ("mid","final")]:
            states=np.array(eval["path"])[:,0,:];maps=np.array(eval["maps"]);prev=np.full(len(maps),r.ROOT);hit=np.full(len(maps),r.T+1)
            for i,q in enumerate(states,1):
                alive=hit>r.T
                assert np.all((t[maps[alive],prev[alive]]==q[alive,None]).any(1))
                assert np.array_equal(prev[~alive],q[~alive])
                hit=np.where(alive&r.GOAL[q],i,hit)
                prev=q
            assert np.array_equal(hit,eval["finish_times"])
            assert np.isclose(np.where(hit<=r.T,1+(r.T-hit)/r.T,0.).mean(),eval["score"])
    print("All saved official-root trajectories verified by replay")

if __name__=='__main__':
    import sys
    if len(sys.argv)==2:audit(sys.argv[1])
    else:unittest.main()
