"""Exact bounded TSP diagnostic using rounded Euclidean costs."""
from functools import lru_cache
import json
import math
from pathlib import Path
import random
from itertools import permutations

ROOT = Path(__file__).resolve().parent


def distances(points):
    return [[math.isqrt((x-u)**2+(y-v)**2) +
             int(((x-u)**2+(y-v)**2) * 4 >= (2*math.isqrt((x-u)**2+(y-v)**2)+1)**2)
             for u, v in points] for x, y in points]


def cost(matrix, tour):
    return sum(matrix[a][b] for a, b in zip(tour, tour[1:] + tour[:1]))


def residual_solver(matrix):
    @lru_cache(None)
    def solve(last, mask):
        if not mask:
            return matrix[last][0]
        return min(matrix[last][j] + solve(j, mask ^ (1 << j))
                   for j in range(1, len(matrix)) if mask & (1 << j))
    return solve


def bound(matrix, prefix, solve):
    mask = ((1 << len(matrix)) - 1) ^ sum(1 << j for j in prefix)
    return sum(matrix[a][b] for a,b in zip(prefix, prefix[1:])) + solve(prefix[-1], mask)


def nearest_neighbor(matrix):
    tour = [0]
    remaining = set(range(1, len(matrix)))
    while remaining:
        j = min(remaining, key=lambda x: (matrix[tour[-1]][x], x))
        tour.append(j)
        remaining.remove(j)
    return tour


def construct():
    n = 12
    for seed in range(200):
        rng = random.Random(seed)
        pts = rng.sample([(x,y) for x in range(100) for y in range(100)], n)
        matrix = distances(pts)
        solve = residual_solver(matrix)
        optimum = bound(matrix, [0], solve)
        greedy = nearest_neighbor(matrix)
        trace = [bound(matrix, greedy[:k], solve) for k in range(1, n+1)]
        threshold = optimum*103//100
        if trace[4] <= threshold and trace[4] > trace[3]:
            return dict(seed=seed, points=pts, matrix=matrix, optimum=optimum,
                        threshold=threshold, greedy=greedy, prefix_bounds=trace)
    raise RuntimeError("no registered instance found")


def verify(case, tour, prefix):
    n = len(case["points"])
    valid = (isinstance(tour, list) and all(type(i) is int for i in tour)
             and len(tour)==n and sorted(tour)==list(range(n)) and tour[0]==0)
    prefix_valid = valid and tour[:len(prefix)] == prefix
    length = cost(case["matrix"], tour) if valid else None
    return dict(valid=valid, prefix_valid=prefix_valid, length=length,
                terminal_reward=int(valid and length <= case["threshold"]),
                reward=int(prefix_valid and length <= case["threshold"]))


def density(case, prefix):
    rest = sorted(set(range(len(case["points"]))) - set(prefix))
    success = 0
    total = 0
    for suffix in permutations(rest):
        tour = prefix + list(suffix)
        success += cost(case["matrix"], tour) <= case["threshold"]
        total += 1
    return dict(solutions=success, completions=total)


if __name__ == "__main__":
    case = construct()
    case["locked_density"] = density(case, case["greedy"][:5])
    case["released_density"] = density(case, case["greedy"][:4])
    (ROOT/"case.json").write_text(json.dumps(case, indent=2))
    print({k:v for k,v in case.items() if k != "matrix"})
