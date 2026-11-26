import unittest
import numpy as np
from graph_coloring import make_graph, count_colorings, exact_reward, sample, settings, N


class TestGraphColoring(unittest.TestCase):
    def test_graph_calibration(self):
        edges=make_graph()
        self.assertEqual(len(edges),49)
        self.assertEqual(count_colorings(edges,2),0)
        self.assertEqual(count_colorings(edges,3),6)

    def test_exact_predicate(self):
        rng=np.random.default_rng(42)
        edges=make_graph()
        labels=rng.integers(3,size=(200,N))
        mask=rng.random((200,len(edges)))<.45
        expected=[all(not keep or row[i]!=row[j] for (i,j),keep in zip(edges,m))
                  for row,m in zip(labels,mask)]
        np.testing.assert_array_equal(exact_reward(labels,edges,mask),expected)
        shared=mask[0]
        np.testing.assert_array_equal(exact_reward(labels,edges,shared),
                                      [all(not keep or row[i]!=row[j] for (i,j),keep in zip(edges,shared))
                                       for row in labels])

    def test_capacity_and_switch(self):
        weights=np.zeros((N,5))
        _,labels=sample(weights,3,np.random.default_rng(42),1000)
        self.assertTrue((labels<3).all())
        self.assertEqual(settings("colors5-switch",149),(5,1.,False))
        self.assertEqual(settings("colors5-switch",150),(3,1.,False))
        self.assertEqual(settings("mask55-switch400",399),(3,.55,False))
        self.assertEqual(settings("mask55-switch400",400),(3,1.,False))


if __name__=="__main__":
    unittest.main()
