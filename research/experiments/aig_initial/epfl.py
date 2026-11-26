"""Extract reproducible small single-output cuts from public EPFL arithmetic AIGs."""
import argparse
import hashlib
import json
from pathlib import Path
import random

from aig import evaluate, verify


def read_aig(path):
    with path.open("rb") as stream:
        kind, maximum, inputs, latches, outputs, gates = stream.readline().split()[:6]
        maximum, inputs, latches, outputs, gates = map(int, (maximum, inputs, latches, outputs, gates))
        if kind != b"aig" or latches or maximum != inputs + gates:
            raise ValueError("expected combinational binary AIGER")
        for _ in range(outputs):
            stream.readline()

        def delta():
            value = shift = 0
            while True:
                raw = stream.read(1)
                if not raw:
                    raise EOFError("truncated AIG")
                value |= (raw[0] & 127) << shift
                if raw[0] < 128:
                    return value
                shift += 7

        nodes = {}
        for node in range(inputs + 1, maximum + 1):
            first = 2 * node - delta()
            second = first - delta()
            if not 0 <= second <= first < 2 * node:
                raise ValueError("invalid AIG fanin")
            nodes[node] = (first, second)
    return nodes


def extract(nodes, root, width, rng):
    leaves = {root}
    expanded = set()
    while True:
        choices = []
        for node in sorted(leaves & nodes.keys()):
            replacement = (leaves - {node}) | {x // 2 for x in nodes[node] if x // 2}
            if len(replacement) <= width:
                choices.append((node, replacement))
        if not choices:
            break
        node, leaves = rng.choice(choices)
        expanded.add(node)
        # Bound cut construction cost, even for reconvergent cones.
        if len(expanded) >= 64:
            break
    # A leaf may become an internal node again through reconvergence.
    mapping = {node: 2 * (i + 1) for i, node in enumerate(sorted(leaves))}
    mapping[0] = 0
    gates = []

    def visit(node):
        if node not in mapping:
            pair = [visit(x // 2) ^ (x & 1) for x in nodes[node]]
            gates.append(pair)
            mapping[node] = 2 * (len(leaves) + len(gates))
        return mapping[node]

    output = visit(root)
    n = len(leaves)
    if n != width or not gates:
        return None
    target = evaluate(n, gates, [output])
    # Retain only functions genuinely depending on every cut input.
    for i in range(n):
        if all(((target[0] >> row) & 1) == ((target[0] >> (row ^ (1 << i))) & 1)
               for row in range(1 << n)):
            return None
    return dict(inputs=n, target=target, budget=len(gates),
                source_leaves=sorted(leaves),
                witness=dict(gates=gates, outputs=[output]))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--width", type=int, default=4, choices=[4, 6, 8])
    parser.add_argument("--per-circuit", type=int, default=8)
    args = parser.parse_args()
    rng = random.Random(42)
    tasks = []
    seen = set()
    for path in sorted((args.source / "arithmetic").glob("*.aig")):
        nodes = read_aig(path)
        roots = list(nodes)
        rng.shuffle(roots)
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        count = 0
        for root in roots:
            task = extract(nodes, root, args.width, rng)
            if task is None or tuple(task["target"]) in seen:
                continue
            seen.add(tuple(task["target"]))
            task.update(name=f"{path.stem}-{root}", source=path.name,
                        source_sha256=digest, root=root)
            assert verify(task, **task["witness"])["reward"] == 1
            tasks.append(task)
            count += 1
            if count == args.per_circuit:
                break
        print(path.name, count)
    args.out.write_text(json.dumps(tasks, indent=2))


if __name__ == "__main__":
    main()
