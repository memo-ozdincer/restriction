#!/usr/bin/env python3
"""Check pooled versus equal-theorem observed base-support overlap."""
import argparse
import json
from pathlib import Path
from statistics import mean

from scripts.project.analyze_evaluation_accumulation import (
    full_counts, load_run, sha256, validate_finalized_metrics,
)
from scripts.project.analyze_symmetric_recovery import CONDITIONS


def summarize(rows):
    """Rows map theorem to condition to (overlap count, correct count)."""
    common = [name for name, row in rows.items()
              if all(row[key][1] > 0 for key in ("c1", "c2", "c3"))]
    output = {"theorems": len(rows), "common_solved_theorems": len(common),
              "conditions": {}, "paired": {}}
    for key in ("c1", "c2", "c3"):
        solved = [name for name, row in rows.items() if row[key][1] > 0]
        def pooled(names):
            total = sum(rows[name][key][1] for name in names)
            return sum(rows[name][key][0] for name in names) / total if total else None
        output["conditions"][key] = {
            "solved_theorems": len(solved),
            "excluded_unsolved_theorems": len(rows) - len(solved),
            "pooled_all_solved": pooled(solved),
            "pooled_common": pooled(common),
            "macro_common": mean(rows[n][key][0] / rows[n][key][1] for n in common) if common else None,
        }
    for left, right in (("c3", "c2"), ("c1", "c3")):
        differences = [rows[n][left][0] / rows[n][left][1]
                       - rows[n][right][0] / rows[n][right][1] for n in common]
        output["paired"][f"{left}_minus_{right}"] = {
            "mean_difference": mean(differences) if differences else None,
            "positive": sum(d > 1e-12 for d in differences),
            "negative": sum(d < -1e-12 for d in differences),
            "tied": sum(abs(d) <= 1e-12 for d in differences),
        }
    output["per_theorem_counts"] = rows
    return output


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-manifest", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError(args.output)
    manifest = json.loads(args.source_manifest.read_text())
    runs, sources = {}, {}
    for key, condition in CONDITIONS.items():
        original = manifest["sources"][key]
        runs[key], sources[key] = load_run(Path(original["run_dir"]), condition)
        for field in ("metrics_sha256", "proof_log_sha256", "evaluation_parquet_sha256"):
            if sources[key][field] != original[field]:
                raise ValueError(f"source changed: {key} {field}")
        validate_finalized_metrics(runs[key], sources[key], [1, 4, 8, 16, 32, 64, 128])
    if any(set(run) != set(runs["c0"]) for run in runs.values()):
        raise ValueError("theorem panels differ")
    if {src["num_samples"] for src in sources.values()} != {128}:
        raise ValueError("expected 128 attempts per theorem")
    if len({src["evaluation_parquet_sha256"] for src in sources.values()}) != 1:
        raise ValueError("datasets differ")
    counts = {key: {name: full_counts(item) for name, item in run.items()}
              for key, run in runs.items()}
    output = {"analysis": "exploratory-base-overlap-weighting-v1", "sources": sources,
              "source_manifest_sha256": sha256(args.source_manifest), "splits": {}}
    for split in ["combined"] + sorted({item["dataset"] for item in runs["c0"].values()}):
        panel = {}
        for label, index in (("tactic_modes", 1), ("exact_proofs", 2)):
            rows = {}
            for name, item in runs["c0"].items():
                if split != "combined" and item["dataset"] != split:
                    continue
                base = counts["c0"][name][index]
                rows[name] = {key: (sum(n for mode, n in counts[key][name][index].items() if mode in base),
                                   counts[key][name][0]) for key in ("c1", "c2", "c3")}
            panel[label] = summarize(rows)
        output["splits"][split] = panel
    with args.output.open("x") as stream:
        json.dump(output, stream, indent=2, sort_keys=True)
        stream.write("\n")


if __name__ == "__main__":
    main()
