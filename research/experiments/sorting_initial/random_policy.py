"""Calibrate sparse outcome frequency before interpreting frozen model results."""
import json
import random
from itertools import combinations
from environment import OPTIMUM, case, execute, goal, identity


def measure(n, condition, rng, count=2000):
    actions = list(combinations(range(n), 2))
    budget = OPTIMUM[n]
    successes = 0
    for _ in range(count):
        if condition == "fresh_random":
            while True:
                start = execute(n, [rng.choice(actions) for _ in range(2 * budget)])
                if start != goal(n):
                    break
        else:
            start, _ = case(n, condition)
        final = execute(n, [rng.choice(actions) for _ in range(budget)], start)
        successes += final == goal(n)
    return dict(n=n, condition=condition, trials=count, hits=successes)


if __name__ == "__main__":
    rng = random.Random(42)
    rows = [measure(n, condition, rng) for n in OPTIMUM
            for condition in ("root", "random", "known", "fresh_random")]
    print(json.dumps(rows, indent=2))
