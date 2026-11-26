"""Exact breadth-first semantic enumeration for small Boolean functions."""
import json
from aig import input_tables, panel


def minimum(n, target, maximum, state_limit=250000):
    mask = (1 << (1 << n)) - 1

    def canonical(x):
        return min(x, x ^ mask)

    wanted = {canonical(x) for x in target}
    initial = frozenset(map(canonical, input_tables(n)))
    frontier = {initial}
    counts = []
    for depth in range(maximum + 1):
        counts.append(len(frontier))
        if any(wanted <= state for state in frontier):
            return dict(optimum=depth, lower_bound=depth, counts=counts)
        if depth == maximum:
            break
        following = set()
        for state in frontier:
            literals = sorted(state | {x ^ mask for x in state})
            for i, a in enumerate(literals):
                for b in literals[i:]:
                    c = canonical(a & b)
                    if c not in state:
                        following.add(state | {c})
                        if len(following) > state_limit:
                            return dict(optimum=None, lower_bound=depth + 1,
                                        counts=counts, reason="state limit")
        frontier = following
    return dict(optimum=None, lower_bound=maximum + 1, counts=counts)


if __name__ == "__main__":
    results = {}
    for task in panel():
        result = minimum(task["inputs"], task["target"], task["budget"])
        results[task["name"]] = result
        print(task["name"], result, flush=True)
    with open("optimality.json", "w") as f:
        json.dump(results, f, indent=2)
