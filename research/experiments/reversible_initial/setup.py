"""Fetch benchmark files locally, retain copyright notices, verify all witnesses."""
from pathlib import Path
from urllib.request import urlretrieve
import json
from environment import load_benchmark, verify

ROOT = Path(__file__).resolve().parents[4] / "circuit-tools/reversible-benchmarks"
ROOT.mkdir(parents=True, exist_ok=True)
records = []
for index in range(1, 6):
    for ext in ("txt", "tfc"):
        name = f"4b15g_{index}.{ext}"
        path = ROOT / name
        if not path.exists():
            urlretrieve("https://reversiblebenchmarks.github.io/" + name, path)
    task = load_benchmark(ROOT, index)
    result = verify(4, task["target"], task["witness"], 15)
    records.append(dict(name=task["name"], published_optimum=15,
                        hashes=task["hashes"], verification=result))
Path(__file__).with_name("inventory.json").write_text(json.dumps(records, indent=2))
print(f"Verified {len(records)} benchmarks in {ROOT}")
