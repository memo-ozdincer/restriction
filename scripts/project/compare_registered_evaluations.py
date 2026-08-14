#!/usr/bin/env python3
"""Compare finalized C0/C1/C3 registered Lean evaluations."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path


CONDITIONS = ("c0_base", "c1_grpo_default", "c3_hardblock_restart")


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def training_counts(condition: str, metrics: dict) -> dict:
    if condition == "c0_base":
        return {
            "proposals": metrics["proposals"], "correct": metrics["correct"],
            "blocked": metrics.get("blocked", 0), "trained": metrics.get("trained_samples", 0), "skipped": 0,
        }
    return {
        "proposals": metrics["proposals"], "correct": metrics["correct"],
        "blocked": metrics["blocked_correct_zero_advantage"],
        "trained": metrics["update_batch_samples"], "skipped": metrics["skipped_all_blocked_prompts"],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    for condition in CONDITIONS:
        parser.add_argument(f"--{condition.replace('_', '-')}-eval", type=Path, required=True)
        parser.add_argument(f"--{condition.replace('_', '-')}-training", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    evaluations = {}
    manifests = {}
    training = {}
    for condition in CONDITIONS:
        key = condition.replace("_", "-")
        eval_metrics = load_json(getattr(args, f"{condition}_eval"))
        if eval_metrics["condition"] != condition: parser.error(f"condition mismatch for {condition} evaluation")
        evaluations[condition] = eval_metrics
        manifests[condition] = load_json(Path(eval_metrics["mode_manifest"]))
        training[condition] = training_counts(condition, load_json(getattr(args, f"{condition}_training")))
    hashes = {metrics["evaluation_parquet_sha256"] for metrics in evaluations.values()}
    proposals = {metrics["registered_proposals"] for metrics in evaluations.values()}
    if len(hashes) != 1 or len(proposals) != 1:
        parser.error("evaluation datasets or proposal budgets differ across conditions")

    comparisons = {}
    for left, right in (("c1_grpo_default", "c0_base"), ("c3_hardblock_restart", "c0_base"), ("c3_hardblock_restart", "c1_grpo_default")):
        label = f"{left}_minus_{right}"
        comparisons[label] = {}
        for dataset in ("registered_valid", "minif2f_test"):
            ldata = evaluations[left]["datasets"][dataset]
            rdata = evaluations[right]["datasets"][dataset]
            names = [name for name in manifests[left]["correct_modes_by_theorem"] if name in manifests[right]["correct_modes_by_theorem"]]
            dataset_names = [
                name for name in names
                if any(name in manifest["correct_modes_by_theorem"] for manifest in (manifests[left], manifests[right]))
            ]
            comparisons[label][dataset] = {
                "pass_at_n_delta": {key: ldata["pass_at_n"][key] - rdata["pass_at_n"][key] for key in ldata["pass_at_n"]},
                "correct_mode_coverage_delta": ldata["correct_mode_coverage"] - rdata["correct_mode_coverage"],
                "mean_correct_modes_per_theorem_delta": ldata["mean_correct_modes_per_theorem"] - rdata["mean_correct_modes_per_theorem"],
            }
        comparisons[label]["theorems_with_new_correct_mode_vs_comparator"] = sum(
            bool(set(manifests[left]["correct_modes_by_theorem"][name]) - set(manifests[right]["correct_modes_by_theorem"][name]))
            for name in manifests[left]["correct_modes_by_theorem"]
        )
    result = {
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "classification": "registered_c0_c1_c3_comparison",
        "evaluation_parquet_sha256": hashes.pop(), "registered_proposals_per_condition": proposals.pop(),
        "training_counts": training,
        "evaluation": {condition: evaluations[condition]["datasets"] for condition in CONDITIONS},
        "comparisons": comparisons,
        "c4_status": "exploratory_not_included",
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    if args.output.exists(): parser.error(f"refusing to overwrite {args.output}")
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
