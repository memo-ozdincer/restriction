import unittest
import numpy as np
from run import TSP, Flip, DIST, ROOT, GOAL, MASKS, train


class TestEnvironment(unittest.TestCase):
    def test_flip_exact_component(self):
        self.assertEqual(len(DIST),512)
        self.assertEqual(DIST[ROOT],9)
        self.assertEqual(ROOT,GOAL ^ int(np.bitwise_xor.reduce(MASKS)))

    def test_flip_all_resets_solvable(self):
        env=Flip()
        rng=np.random.default_rng(42)
        for mode in ("root","uniform","near"):
            for _ in range(20):
                states,_=env.starts(mode,rng,8)
                self.assertTrue(np.all(states==states[0]))
                self.assertIn(int(states[0]),DIST)
                self.assertNotEqual(int(states[0]),GOAL)

    def test_tsp_legal_common_slots(self):
        env=TSP()
        rng=np.random.default_rng(45)
        w=np.zeros(env.dim,dtype=np.float32)
        s,_=env.starts("root",rng,4)
        root=env.rollout(w,s,rng,True)
        s,_=env.starts("subset",rng,4)
        sub=env.rollout(w,s,rng,True)
        self.assertEqual(root["padded_candidates"],sub["padded_candidates"])
        self.assertEqual(root["actions"],sub["actions"])
        self.assertGreater(root["candidates"],sub["candidates"])

    def test_root_reproducibility_and_replay(self):
        for domain in ("tsp","flip"):
            a=train(domain,"root",42,2,4,1,10.)
            b=train(domain,"root",42,2,4,1,10.)
            self.assertEqual(a["weights"],b["weights"])
            self.assertEqual(a["records"],b["records"])

    def test_common_prefix_identity_and_budget(self):
        for domain,variants in (("tsp",("subset","subset_switch")),("flip",("uniform","uniform_switch","near","near_switch"))):
            baseline=train(domain,"root",42,10,4,1,10.,True)
            for arm in variants:
                branch=train(domain,arm,42,10,4,1,10.,True)
                self.assertEqual(baseline["prefix_checkpoint"],branch["prefix_checkpoint"])
                self.assertEqual(branch["padded_slots"],baseline["padded_slots"])
                self.assertEqual(sum(v["updates"] for v in branch["by_mode"].values()),10)
                self.assertEqual(branch["by_mode"]["root"]["updates"],7 if arm.endswith("_switch") else 3)
                self.assertEqual(branch["by_mode"][arm.removesuffix("_switch")]["updates"],3 if arm.endswith("_switch") else 7)


if __name__=="__main__":
    unittest.main()
