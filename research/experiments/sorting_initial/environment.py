"""Classical comparison-network synthesis, exact zero-one verifier."""
import random
from itertools import combinations
from functools import lru_cache

OPTIMUM = {6: 12, 9: 25}
# Published optimal-size witnesses from Bert Dobbelaere's SorterHunter catalogue.
WITNESSES = {
    6: [(0,5),(1,3),(2,4),(1,2),(3,4),(0,3),(2,5),(0,1),(2,3),(4,5),(1,2),(3,4)],
    9: [(0,3),(1,7),(2,5),(4,8),(0,7),(2,4),(3,8),(5,6),(0,2),(1,3),(4,5),(7,8),(1,4),(3,6),(5,7),(0,1),(2,4),(3,5),(6,8),(2,3),(4,5),(6,7),(1,2),(3,4),(5,6)],
}


def identity(n):
    return (1 << (1 << n)) - 1


def goal(n):
    return sum(1 << ((1 << k) - 1) for k in range(n + 1))


@lru_cache(maxsize=None)
def comparator(n, i, j):
    if not 0 <= i < j < n:
        raise ValueError("invalid comparator")
    hi, lo = 1 << (n - 1 - i), 1 << (n - 1 - j)
    moved = sum(1 << r for r in range(1 << n) if r & hi and not r & lo)
    return moved, hi - lo


def step(n, state, action):
    moved, shift = comparator(n, *action)
    return (state & ~moved) | ((state & moved) >> shift)


def execute(n, actions, start=None):
    state = identity(n) if start is None else start
    if state & ~identity(n) or state & goal(n) != goal(n):
        raise ValueError("invalid reachable state invariant")
    for action in actions:
        state = step(n, state, action)
    return state


def verify(n, actions, budget, start=None):
    final = execute(n, actions, start)
    correct = final == goal(n)
    return dict(correct=correct, comparators=len(actions),
                reward=int(correct and len(actions) <= budget),
                remaining_rows=(final & ~goal(n)).bit_count())


def unresolved(n, state):
    return [format(r, f"0{n}b") for r in range(1 << n)
            if (state & ~goal(n)) >> r & 1]


def case(n, condition):
    budget = OPTIMUM[n]
    if condition == "root":
        return identity(n), []
    if condition == "known":
        prefix = WITNESSES[n][:-3]
    elif condition == "random":
        # Uniform comparator draws, independent of solution; reject only
        # already-terminal states. Prefix cost is excluded from reset budget.
        rng = random.Random(20261127 + n)
        gates = list(combinations(range(n), 2))
        while True:
            prefix = [rng.choice(gates) for _ in range(2 * budget)]
            if execute(n, prefix) != goal(n):
                break
    else:
        raise ValueError(condition)
    state = execute(n, prefix)
    assert state != identity(n) and state != goal(n)
    assert verify(n, WITNESSES[n], budget, state)["reward"]
    return state, prefix


if __name__ == "__main__":
    for n, budget in OPTIMUM.items():
        print(n, verify(n, WITNESSES[n], budget))
        for condition in ("root", "random", "known"):
            state, prefix = case(n, condition)
            print(n, condition, "prefix", len(prefix), "unresolved", len(unresolved(n, state)))
