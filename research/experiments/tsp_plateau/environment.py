"""Exact small geometric TSP and standard symmetric 2-opt descent."""
from itertools import combinations
from math import isqrt
import random


def distance_matrix(points):
    # Integer rounded Euclidean metric, same as TSPLIB EUC_2D.
    def dist(a,b):
        squared = sum((x-y)**2 for x,y in zip(a,b))
        base = isqrt(squared)
        return base + (4*squared >= (2*base+1)**2)
    return [[dist(a,b) for b in points] for a in points]


def cost(matrix, tour):
    if sorted(tour) != list(range(len(matrix))):
        raise ValueError('tour must contain every city exactly once')
    return sum(matrix[a][b] for a,b in zip(tour,tour[1:]+tour[:1]))


def moves(n):
    return [(i,j) for i,j in combinations(range(1,n),2) if (i,j)!=(1,n-1)]


def apply(tour, move):
    i,j=move
    if not all(type(x) is int for x in (i,j)) or (i,j) not in moves(len(tour)):
        raise ValueError('invalid anchored 2-opt reversal')
    return tour[:i]+tuple(reversed(tour[i:j+1]))+tour[j+1:]


def descend(matrix,tour):
    history=[tour]
    while True:
        candidate=min((apply(tour,m) for m in moves(len(tour))),key=lambda t:cost(matrix,t))
        if cost(matrix,candidate)>=cost(matrix,tour):return history
        tour=candidate
        history.append(tour)


def held_karp(matrix):
    n=len(matrix)
    table={(1<<(j-1),j):matrix[0][j] for j in range(1,n)}
    for mask in range(1,1<<(n-1)):
        for j in range(1,n):
            bit=1<<(j-1)
            if mask & bit and mask != bit:
                table[mask,j]=min(table[mask^bit,k]+matrix[k][j] for k in range(1,n) if (mask^bit)&(1<<(k-1)))
    full=(1<<(n-1))-1
    return min(table[full,j]+matrix[j][0] for j in range(1,n))


def find_instance():
    """First seeded 11-city instance with a strictly suboptimal local optimum."""
    rng=random.Random(20261127)
    for seed_index in range(100):
        points=[(rng.randrange(100),rng.randrange(100)) for _ in range(11)]
        if len(set(points))!=len(points):continue
        matrix=distance_matrix(points); optimal=held_karp(matrix)
        for _ in range(100):
            raw=list(range(1,len(points))); rng.shuffle(raw)
            history=descend(matrix,(0,*raw)); plateau=history[-1]; plateau_cost=cost(matrix,plateau)
            if plateau_cost>optimal and all(cost(matrix,apply(plateau,m))>plateau_cost for m in moves(len(points))):
                # Need a feasible improvement within the ordinary three-action horizon.
                if any(cost(matrix,apply(apply(plateau,m),k))<plateau_cost for m in moves(len(points)) for k in moves(len(points))):
                    return dict(points=points,matrix=matrix,optimum=optimal,plateau=list(plateau),threshold=plateau_cost-1,descent=[list(t) for t in history],source_index=seed_index)
    raise RuntimeError('no instance')
