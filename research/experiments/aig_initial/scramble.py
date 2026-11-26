"""Freeze a paired EPFL screen with target-independent random gate starts."""
import json
from pathlib import Path
import random
from aig import evaluate, input_tables, random_prefix, verify

ROOT = Path(__file__).parent
rng = random.Random(20261126)
tasks = []
starts = {}
for width in (4, 8):
    panel = json.loads((ROOT / f"epfl{width}.json").read_text())
    for index in (0, 24, 48, 72):
        task = dict(panel[index])
        task["name"] = f"w{width}-{task['name']}"
        task["budget"] += 2
        mask = (1 << (1 << width)) - 1
        # Reject only redundant or constant gates; do not inspect the target.
        while True:
            prefix = random_prefix(width, 2, rng)
            values = input_tables(width) + evaluate(width, prefix, [2*(width+1), 2*(width+2)])
            if len({min(v, v ^ mask) for v in values}) == len(values):
                break
        starts[task["name"]] = prefix
        # Shift the private feasible witness to prove the random start
        # can always be ignored within the common budget.
        def shift(literal):
            return literal + 4 if literal // 2 > width else literal
        witness = task["witness"]
        shifted = [[shift(x) for x in pair] for pair in witness["gates"]]
        assert verify(task, shifted, [shift(x) for x in witness["outputs"]], prefix)["reward"]
        tasks.append(task)
(ROOT / "scramble_panel.json").write_text(json.dumps(tasks, indent=2))
(ROOT / "scramble_starts.json").write_text(json.dumps(starts, indent=2))
