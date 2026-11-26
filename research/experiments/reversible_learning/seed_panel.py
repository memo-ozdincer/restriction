"""Reproduce the registered follow-up across paired initializations."""
import json
from pathlib import Path
from train import make_environment, train

env = make_environment()
rows = []
for seed in range(42, 50):
    for mode, exclude in [
        ("root", False), ("near", False), ("near-switch", False),
        ("near", True), ("near-switch", True),
    ]:
        rows.append(train(mode, 300, env, seed, exclude))
Path(__file__).with_name("seed_panel.json").write_text(json.dumps(rows, indent=2))
