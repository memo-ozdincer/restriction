"""Classical reversible circuits with positive-control generalized Toffoli gates."""
from collections import deque, Counter
from itertools import combinations
from pathlib import Path
import hashlib
import json
import random


def gate_library(n):
    return [(target, controls)
            for target in range(n)
            for size in range(n)
            for controls in combinations([i for i in range(n) if i != target], size)]


def gate_permutation(n, gate):
    target, controls = gate
    if not 0 <= target < n or len(set(controls)) != len(controls) or any(
            c == target or not 0 <= c < n for c in controls):
        raise ValueError("invalid gate")
    mask = sum(1 << c for c in controls)
    return tuple(x ^ (1 << target) if x & mask == mask else x
                 for x in range(1 << n))


def identity(n):
    return tuple(range(1 << n))


def compose(state, gate):
    return tuple(gate[x] for x in state)


def execute(n, actions, start=None):
    state = identity(n) if start is None else tuple(start)
    if sorted(state) != list(identity(n)):
        raise ValueError("invalid start permutation")
    for action in actions:
        state = compose(state, gate_permutation(n, action))
    return state


def verify(n, target, actions, budget, start=None):
    final = execute(n, actions, start)
    correct = final == tuple(target)
    return dict(correct=correct, gates=len(actions),
                reward=int(correct and len(actions) <= budget))


def random_start(n, rng):
    """Uniform permutation, reachable under the full generalized library."""
    values = list(identity(n))
    rng.shuffle(values)
    return tuple(values)


def distances(n, goal=None):
    if n > 3:
        raise ValueError("full enumeration limited to at most three wires")
    goal = identity(n) if goal is None else tuple(goal)
    generators = [gate_permutation(n, gate) for gate in gate_library(n)]
    depth = {goal: 0}
    queue = deque([goal])
    while queue:
        p = queue.popleft()
        for gate in generators:
            q = compose(p, gate)
            if q not in depth:
                depth[q] = depth[p] + 1
                queue.append(q)
    return depth


def load_benchmark(directory, index):
    name = f"4b15g_{index}"
    spec = directory / f"{name}.txt"
    circuit = directory / f"{name}.tfc"
    specification = tuple(int(line) for line in spec.read_text().splitlines()
                   if line.strip() and not line.startswith("#"))
    names = []
    actions = []
    inside = False
    for line in circuit.read_text().splitlines():
        line = line.strip()
        if line.startswith(".v "):
            names = line[3:].split(",")
        elif line == "BEGIN":
            inside = True
        elif line == "END":
            inside = False
        elif inside:
            op, wires = line.split()
            indices = [names.index(wire) for wire in wires.split(",")]
            if op != f"t{len(indices)}":
                raise ValueError("unsupported gate")
            actions.append((indices[-1], tuple(indices[:-1])))
    n = len(names)
    assert specification[0] == n
    target = specification[1:]
    assert sorted(target) == list(identity(n))
    assert len(actions) == 15
    if execute(n, actions) != target:
        actions = [(n-1-t, tuple(n-1-c for c in cs)) for t, cs in actions]
    assert execute(n, actions) == target, name
    return dict(name=name, inputs=n, target=target, published_optimum=15,
                witness=actions, hashes={p.name: hashlib.sha256(p.read_bytes()).hexdigest()
                                        for p in (spec, circuit)})


if __name__ == "__main__":
    root = Path(__file__).resolve().parents[4] / "circuit-tools/reversible-benchmarks"
    depth = distances(3)
    print("3-bit distribution:", sorted(Counter(depth.values()).items()))
    for index in range(1, 6):
        task = load_benchmark(root, index)
        print(task["name"], verify(4, task["target"], task["witness"], 15), task["hashes"])
