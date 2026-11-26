"""Exact shortest comparator continuation over the bitset state graph."""
from collections import deque
from itertools import combinations
import json
from environment import OPTIMUM, case, execute, goal, identity, step


def shortest(n, start, actions, limit=250_000):
    queue = deque([(start, 0)])
    seen = {start: None}
    while queue:
        state, depth = queue.popleft()
        if state == goal(n):
            path = []
            while seen[state] is not None:
                state, action = seen[state]
                path.append(action)
            path.reverse()
            assert execute(n, path, start) == goal(n)
            return dict(optimum=depth, witness=path, visited=len(seen))
        if len(seen) >= limit:
            return dict(optimum=None, lower_bound=depth, visited=len(seen))
        for action in actions:
            successor = step(n, state, action)
            if successor not in seen:
                seen[successor] = state, action
                queue.append((successor, depth + 1))
    raise ValueError("no reachable goal")


if __name__ == "__main__":
    rows = []
    for n in OPTIMUM:
        for condition in ("random", "known"):
            start, _ = case(n, condition)
            rows.append(dict(n=n, condition=condition,
                             **shortest(n, start, list(combinations(range(n), 2)))))
    n = 6
    restricted = [(i,i+1) for i in range(n-1)] + [(0,3),(1,4),(2,5)]
    rows.append(dict(n=n, condition="restricted_root", actions=restricted,
                     **shortest(n, identity(n), restricted)))
    print(json.dumps(rows, indent=2))
