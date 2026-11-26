"""Paired useful-prefix and perturbed-prefix diagnostic."""
import json
from pathlib import Path
import random
from aig import evaluate, input_tables, verify

root = Path(__file__).parent
tasks = json.loads((root / "scramble_panel.json").read_text())
rng = random.Random(20261127)
clean, perturbed = {}, {}
for task in tasks:
    n = task["inputs"]
    witness = task["witness"]
    k = max(1, len(witness["gates"]) * 2 // 3)
    prefix = witness["gates"][:k]
    clean[task["name"]] = prefix
    assert verify(task, witness["gates"][k:], witness["outputs"], prefix)["reward"]
    # Alter the last supplied gate; the original gate can always be recreated.
    last = n + k
    mask = (1 << (1 << n)) - 1
    previous = prefix[:-1]
    old = evaluate(n, prefix, [2*last])[0]
    existing = input_tables(n) + evaluate(n, previous, [2*(n+i+1) for i in range(k-1)])
    forbidden = {min(x, x ^ mask) for x in existing + [old]}
    while True:
        pair = [rng.randrange(2*last), rng.randrange(2*last)]
        value = evaluate(n, previous + [pair], [2*last])[0]
        if min(value, value ^ mask) not in forbidden:
            break
    damaged = previous + [pair]
    perturbed[task["name"]] = damaged

    def shift(x):
        return x + 2 if x // 2 >= last else x

    continuation = [prefix[-1]] + [[shift(x) for x in g] for g in witness["gates"][k:]]
    assert verify(task, continuation, [shift(x) for x in witness["outputs"]], damaged)["reward"]
for name, starts in [("solution_prefix", clean), ("perturbed_prefix", perturbed)]:
    (root / f"{name}.json").write_text(json.dumps(starts, indent=2))
