import itertools
import math
import random
import unittest

from environment import (
    adjacency, prufer_to_edges, edges_to_prufer, tree_id, path_tree,
    independence_polynomial, domination_polynomial, defect, score,
    violations, kadrawi_26_trees, galvin_tree, bautista_ramos_tree,
    domination_witness_tree,
)


def brute(n, edges):
    """Independent direct subset predicates, not the dynamic program."""
    adjmask = [1<<v for v in range(n)]
    for u,v in edges:
        adjmask[u] |= 1<<v
        adjmask[v] |= 1<<u
    edgemasks = [(1<<u)|(1<<v) for u,v in edges]
    ip, dp = [0]*(n+1), [0]*(n+1)
    for subset in range(1<<n):
        k = subset.bit_count()
        if all((subset & m) != m for m in edgemasks):
            ip[k] += 1
        if all(subset & m for m in adjmask):
            dp[k] += 1
    return ip,dp


class TestEnvironment(unittest.TestCase):
    def test_exhaustive_small(self):
        for n in range(1,6):
            for code in itertools.product(range(n),repeat=max(0,n-2)):
                edges = prufer_to_edges(code,n)
                self.assertEqual(edges_to_prufer(n,edges),code)
                i,d = brute(n,edges)
                self.assertEqual(independence_polynomial(n,edges),i)
                self.assertEqual(domination_polynomial(n,edges),d)

    def test_random_brute_root_and_label_invariance(self):
        rng = random.Random(421)
        for n in [6,8,10,12,14,16]:
            for _ in range(5):
                edges = prufer_to_edges([rng.randrange(n) for v in range(n-2)])
                i,d = brute(n,edges)
                p = list(range(n));rng.shuffle(p)
                relabel = [(p[v],p[u]) for u,v in reversed(edges)]
                self.assertEqual(independence_polynomial(n,edges,root=n-1),i)
                self.assertEqual(domination_polynomial(n,edges,root=n-1),d)
                self.assertEqual(independence_polynomial(n,relabel),i)
                self.assertEqual(domination_polynomial(n,relabel),d)
                self.assertEqual(tree_id(n,edges),tree_id(n,relabel))

    def test_canonical_counts(self):
        # A000055 enumeration of unlabeled trees n=1..6, not reward equivalence.
        for n,expected in enumerate([1,1,1,2,3,6],start=1):
            ids = {tree_id(n,prufer_to_edges(code,n)) for code in itertools.product(range(n),repeat=max(0,n-2))}
            self.assertEqual(len(ids),expected)
        for n in [4,5,26,56,101]:
            self.assertNotEqual(tree_id(*path_tree(n)),tree_id(n,[(0,j) for j in range(1,n)]))

    def test_invalid(self):
        for n,edges in [(3,[(0,1),(0,1)]),(3,[(0,0),(1,2)]),(3,[(0,1),(1,3)]),(4,[(0,1),(1,2),(2,0)]),(2,[])]:
            with self.assertRaises(ValueError): adjacency(n,edges)
        for code,n in [((3,),3),((0,0),3),((-1,),3),((0,),1)]:
            with self.assertRaises(ValueError): prufer_to_edges(code,n)

    def test_witnesses(self):
        anchors = [(independence_polynomial, n, edges, [13], [expect]) for (n,edges),expect in zip(kadrawi_26_trees(),[378,68])]
        anchors.extend([(fn, *builder, indices, margins) for fn,builder,indices,margins in [
            (independence_polynomial,galvin_tree(5,5),[27],[332324762280]),
            (independence_polynomial,bautista_ramos_tree(2,5),[34,36],[59961497473247,17791]),
            (domination_polynomial,domination_witness_tree(2,5),[34,36],[405489,365508484889154]),
        ]])
        for fn,n,edges,ips,mar in anchors:
            co = fn(n,edges)
            self.assertEqual(violations(co),ips)
            self.assertEqual([defect(co,i) for i in ips],mar)
            self.assertEqual(score(co,required=len(ips),mode='binary'),1)
            self.assertEqual(score(co,required=len(ips)+1,mode='binary'),0)
            self.assertGreater(score(co,required=len(ips),mode='normalized'),0)
            for i,v in zip(ips,mar):
                self.assertEqual(score(co,index=i,mode='raw'),v)
                self.assertEqual(score(co,index=i,mode='binary'),1)

    def test_large_coefficients(self):
        n=101
        edges=[(0,j) for j in range(1,n)]
        ip=independence_polynomial(n,edges)
        dp=domination_polynomial(n,edges)
        self.assertGreater(ip[50],2**64)
        self.assertEqual(ip[50],math.comb(100,50))
        self.assertEqual(ip[1],101)
        self.assertEqual(sum(ip),2**100+1)
        self.assertEqual(dp[51],math.comb(100,50))
        self.assertEqual(sum(dp),2**100+1)

    def test_invalid_support(self):
        p=[1,5,2,0,0]
        self.assertEqual(score(p,index=3,mode='raw'),0)
        self.assertEqual(score(p,index=3,mode='binary'),0)
        self.assertEqual(score(p,index=3,mode='normalized'),-1)
        self.assertEqual(violations(p),[])
        self.assertEqual(score(p,required=2,mode='binary'),0)
        self.assertEqual(score(p,required=2,mode='normalized'),-1)
        self.assertLess(score(p,index=1,mode='normalized'),0)

if __name__ == '__main__':
    unittest.main()
