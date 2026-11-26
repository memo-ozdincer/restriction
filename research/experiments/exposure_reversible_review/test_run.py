import unittest
import numpy as np
from run import build, hits_by_horizon, ACTIONS, ARMS, GATES, TARGET, gate_value


class Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.env = build()

    def test_certificate(self):
        env = self.env
        self.assertEqual(len(env['graph']),40320)
        self.assertEqual((int(env['depths'][env['root']]),int(env['counts'][env['root']])),(8,6))
        self.assertEqual(len(GATES),12)

    def test_uniform_probability(self):
        env = self.env
        uniform = np.full((len(env['graph']),ACTIONS),1/ACTIONS)
        values = hits_by_horizon(uniform,env['graph'],env['goal'],(7,8,16,32))
        self.assertEqual(values[7][env['root']],0)
        self.assertAlmostEqual(values[8][env['root']],6/ACTIONS**8,places=15)
        self.assertGreater(values[16][env['root']],values[8][env['root']])
        self.assertGreater(values[32][env['root']],values[16][env['root']])

    def test_reset_distribution(self):
        env = self.env
        self.assertAlmostEqual(env['distribution'].sum(),1)
        self.assertEqual(env['distribution'][env['goal']],0)
        self.assertEqual(int(env['depths'][env['distribution']>0].max()),4)

    def test_arms(self):
        self.assertEqual(len(ARMS),11)
        self.assertEqual(len(set(ARMS)),11)


if __name__=='__main__':
    unittest.main()
