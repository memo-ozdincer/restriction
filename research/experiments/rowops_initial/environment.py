"""Exact small linear matrix synthesis over GF(3)."""
from collections import Counter, deque
from itertools import product
import random

N = 3
P = 3
IDENTITY = tuple(int(row == col) for row in range(N) for col in range(N))
# (destination, source, coefficient). The diagonal case negates a row.
ACTIONS = tuple(
    (i, j, k) for i, j, k in product(range(N), range(N), (1, 2)) if i != j
) + tuple((i, i, 2) for i in range(N))
TARGET = (0, 0, 1, 1, 0, 0, 0, 2, 0)
BUDGET = 7


def step(state, action):
    i, j, k = action
    if (i, j, k) not in ACTIONS:
        raise ValueError("invalid row action")
    result = list(state)
    for column in range(N):
        pos = N * i + column
        if i == j:
            result[pos] = state[pos] * k % P
        else:
            result[pos] = (state[pos] + k * state[N * j + column]) % P
    return tuple(result)


def execute(state, actions):
    for action in actions:
        state = step(state, tuple(action))
    return state


def distances(start=IDENTITY):
    """Exact BFS over the group; all transitions have legal inverses."""
    queue = deque([start])
    depths = {start: 0}
    parents = {}
    while queue:
        state = queue.popleft()
        for action in ACTIONS:
            nxt = step(state, action)
            if nxt not in depths:
                depths[nxt] = depths[state] + 1
                parents[nxt] = (state, action)
                queue.append(nxt)
    return depths, parents


def witness(start, goal, parents):
    actions = []
    while goal != start:
        goal, action = parents[goal]
        actions.append(action)
    return list(reversed(actions))


def verify(start, actions, goal=TARGET, budget=BUDGET):
    if not isinstance(actions, list):
        raise ValueError("actions must be a list")
    final = execute(start, actions)
    return {"correct": final == goal, "actions": len(actions),
            "reward": int(final == goal and len(actions) <= budget)}


def starts():
    """Fixed paired diagnostic starts, including genuine uniform state resets."""
    depth, _ = distances(TARGET)
    rng = random.Random(20261127)
    states = sorted(depth)
    for mode in ("root", "uniform", "near"):
        for index in range(4):
            if mode == "root":
                state = IDENTITY
            elif mode == "uniform":
                state = rng.choice(states)
            else:
                while True:
                    state = execute(TARGET, rng.choices(ACTIONS, k=index+1))
                    if state != TARGET:
                        break
            yield mode, index, state, depth[state]


if __name__ == "__main__":
    depth, parent = distances()
    assert len(depth) == 11232
    assert depth[TARGET] == max(depth.values()) == BUDGET
    assert verify(IDENTITY, witness(IDENTITY, TARGET, parent))["reward"]
    print(sorted(Counter(depth.values()).items()))
    print("target:", TARGET, depth[TARGET])
    for mode, index, state, distance in starts():
        print(mode, index, state, distance)
