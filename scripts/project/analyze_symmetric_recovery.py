#!/usr/bin/env python3
"""Exploratory, symmetric sampled-support recovery on finalized held-out runs.

Absence is finite-sample non-observation, not demonstrated capability loss.
Tactic signatures are syntactic proxies, not semantic mathematical strategies.
"""

import argparse
import json
from pathlib import Path

from scripts.project.analyze_evaluation_accumulation import (
    full_counts, load_run, validate_finalized_metrics,
)


CONDITIONS = {
    "c0": "c0_base", "c1": "c1_grpo_default",
    "c2": "c2_unlikeliness_2", "c3": "c3_hardblock_restart",
}


def partition_recovery(base, grpo, soft, blocking, minimum):
    """Partition base-supported, GRPO-unobserved theorem-specific patterns."""
    if minimum < 1:
        raise ValueError("minimum must be positive")
    if not (set(base) == set(grpo) == set(soft) == set(blocking)):
        raise ValueError("theorem panels differ")
    buckets = {key: [] for key in ("c2_only", "c3_only", "both", "neither")}
    for name in sorted(base):
        for mode, count in sorted(base[name].items()):
            if count < minimum or grpo[name].get(mode, 0):
                continue
            left = soft[name].get(mode, 0)
            right = blocking[name].get(mode, 0)
            key = "both" if left and right else "c2_only" if left else "c3_only" if right else "neither"
            buckets[key].append({"theorem": name, "pattern": mode,
                                 "c0_count": count, "c2_count": left, "c3_count": right})
    return {
        "minimum_c0_count": minimum,
        "missing_c1_patterns": sum(map(len, buckets.values())),
        "buckets": {key: {"patterns": len(rows),
                          "theorems": len({row["theorem"] for row in rows}),
                          "entries": rows} for key, rows in buckets.items()},
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for key in CONDITIONS:
        parser.add_argument(f"--{key}-run", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError(args.output)
    runs, sources = {}, {}
    for key, condition in CONDITIONS.items():
        runs[key], sources[key] = load_run(getattr(args, f"{key}_run"), condition)
        validate_finalized_metrics(runs[key], sources[key], [1, 4, 8, 16, 32, 64, 128])
    reference = runs["c0"]
    if any(set(run) != set(reference) for run in runs.values()):
        raise ValueError("theorem panels differ")
    if len({src["evaluation_parquet_sha256"] for src in sources.values()}) != 1:
        raise ValueError("evaluation datasets differ")
    if {src["num_samples"] for src in sources.values()} != {128}:
        raise ValueError("all runs must use 128 samples")
    output = {"analysis": "exploratory-symmetric-heldout-recovery-v1", "sources": sources,
              "interpretation": "Finite-sample syntactic support, not semantic recovery or proven forgetting.",
              "splits": {}}
    for split in ["combined"] + sorted({item["dataset"] for item in reference.values()}):
        names = [name for name, item in reference.items()
                 if split == "combined" or item["dataset"] == split]
        panel = {"theorems": len(names), "attempts_per_condition": 128 * len(names)}
        for label, index in [("tactic_modes", 1), ("exact_proofs", 2)]:
            counts = {key: {name: full_counts(run[name])[index] for name in names}
                      for key, run in runs.items()}
            panel[label] = {str(floor): partition_recovery(
                counts["c0"], counts["c1"], counts["c2"], counts["c3"], floor)
                for floor in (1, 2, 4, 8)}
        output["splits"][split] = panel
    with args.output.open("x") as stream:
        json.dump(output, stream, indent=2, sort_keys=True)
        stream.write("\n")


if __name__ == "__main__":
    main()
