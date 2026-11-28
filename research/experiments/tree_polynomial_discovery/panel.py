"""Registered CPU pilot; each run has exactly 131072 training verifier calls."""
import concurrent.futures as cf
import gzip
import itertools
import json
import os
import pathlib
import subprocess
import sys

TASKS = [
    ("i26-13", "independence", 26, 13, 1),
    ("i56-28", "independence", 56, 28, 1),
    ("i56-27", "independence", 56, 27, 1),
    ("i70-double", "independence", 70, None, 2),
    ("d101-double", "domination", 101, None, 2),
]
BASE = [
    ("random", "normalized", "ordinary"),
    ("hill", "normalized", "ordinary"),
    ("anneal", "normalized", "ordinary"),
    ("pg", "raw", "ordinary"),
    ("pg", "normalized", "ordinary"),
    ("pg", "binary", "ordinary"),
    ("cem", "raw", "ordinary"),
    ("cem", "normalized", "ordinary"),
    ("pattern-lite", "normalized", "ordinary"),
]
EXTRA = [
    ("pg", "normalized", "balanced"),
    ("pg", "normalized", "matched"),
    ("cem", "normalized", "crossover"),
    ("cem", "normalized", "random-donor"),
    ("cem", "normalized", "edit"),
]
SEEDS = [42, 43, 44]
BATCH = 128
BUDGET = 131072

def specs():
    for task in TASKS:
        name, fam, n, index, required = task
        arms = list(BASE)
        if name in ("i26-13", "i56-27"):
            arms.append(("pattern-lite", "raw", "ordinary"))
        if name in ("i56-27", "i70-double", "d101-double"):
            arms += EXTRA
        for (method, score, variant), seed in itertools.product(arms, SEEDS):
            steps = BUDGET // BATCH
            if method in ("hill", "anneal"):
                steps -= 1
            elif method == "pattern-lite":
                steps //= 4
            key = f"{name}-{method}-{score}-{variant}-{seed}"
            args = ["--n", str(n), "--family", fam, "--required", str(required),
                    "--method", method, "--score", score, "--variant", variant,
                    "--steps", str(steps), "--batch", str(BATCH), "--seed", str(seed),
                    "--local-steps", "3", "--eval-batch", "256",
                    "--eval-every", str(32 if method == "pattern-lite" else 128)]
            if index is not None:
                args += ["--index", str(index)]
            yield key, args

def run(spec):
    key, args = spec
    root = pathlib.Path("results")
    path = root / (key + ".json")
    with (root / (key + ".log")).open("w") as log:
        subprocess.run([sys.executable, "train.py", *args, "--output", str(path)],
                       stdout=log, stderr=subprocess.STDOUT, check=True)
    data = json.loads(path.read_text())
    assert data["train"]["calls"] == BUDGET, (key, data["train"]["calls"])
    with gzip.open(str(path) + ".gz", "wt", compresslevel=6) as f:
        json.dump(data, f, separators=(",", ":"))
    path.unlink()
    return {"key": key, "config": data["config"],
            "train": {k:v for k,v in data["train"].items() if k != "witnesses"},
            "final": data["evaluation"]["checkpoints"][-1],
            "counters": data["counters"], "elapsed": data["elapsed_seconds"],
            "queries_per_second": data["queries_per_second"]}

if __name__ == "__main__":
    root = pathlib.Path("results")
    root.mkdir(exist_ok=False)
    panel = list(specs())
    (root / "registered_specs.json").write_text(json.dumps(panel,indent=2))
    completed = []
    failed = []
    with cf.ThreadPoolExecutor(max_workers=min(len(panel),int(os.environ.get("SLURM_CPUS_PER_TASK", "2")))) as ex:
        futures = {ex.submit(run,s):s[0] for s in panel}
        for f in cf.as_completed(futures):
            key = futures[f]
            try:
                result = f.result()
                completed.append(result)
                print(key, result["train"]["successes"], result["final"]["successes"], flush=True)
            except Exception as e:
                failed.append({"key":key,"error":repr(e)})
                print("FAILED",key,repr(e),flush=True)
            (root / "summary.json").write_text(json.dumps({"runs":completed,"failed":failed},indent=2))
    if failed:
        sys.exit(1)
