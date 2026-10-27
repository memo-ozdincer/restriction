#!/usr/bin/env python3
"""Compare common held-out continuation tasks without pooling their prefixes.

This validates proof records and estimates effects. Runtime/model attestation
must additionally come from the associated training/evaluation certificates;
passing this statistical analysis alone never makes a checkpoint eligible.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np

from scripts.project.analyze_execution_pilot import load_manifest, read_jsonl, sha256, summarize


def paired_effect(left, right, *, seed=20261026, draws=10000):
    """Right-minus-left effect with paired theorem bootstrap uncertainty."""
    if not left or set(left) != set(right):
        raise ValueError("effects require the same nonempty theorem population")
    names = sorted(left)
    difference = np.array([right[name] - left[name] for name in names], dtype=float)
    if not np.isfinite(difference).all():
        raise ValueError("nonfinite theorem-level correctness")
    if draws < 1:
        raise ValueError("bootstrap draws must be positive")
    random = np.random.default_rng(seed)
    bootstrap = np.mean(difference[random.integers(0, len(names), (draws, len(names)))], axis=1)
    return {
        "right_minus_left": float(difference.mean()),
        "paired_theorems": len(names),
        "percentile_interval_95": np.quantile(bootstrap, [0.025, 0.975]).tolist(),
        "bootstrap_seed": seed, "bootstrap_draws": draws,
        "unit": "theorem; all prefixes of a theorem remain together",
        "difference_by_theorem": dict(zip(names, difference.tolist())),
        "uncertainty_scope": "theorem resampling only; no training-seed uncertainty",
    }


def compare(bank, records_by_arm):
    """Apply already-registered practical thresholds; no test-based selection."""
    if set(records_by_arm) != {"base", "root", "practice"}:
        raise ValueError("exactly base, root and practice diagnostic logs are required")
    diagnostic = {key: row for key, row in bank.items() if row["pilot_split"] == "diagnostic"}
    if not diagnostic:
        raise ValueError("no registered diagnostic tasks")
    results = {arm: summarize(diagnostic, records) for arm, records in records_by_arm.items()}
    effects = {}
    for condition in ("root", "prefix"):
        panels = {arm: result["panels"][f"diagnostic_{condition}"]["correctness_by_theorem"]
                  for arm, result in results.items()}
        effects[condition] = {
            f"{right}_minus_{left}": paired_effect(panels[left], panels[right])
            for left, right in (("root", "practice"), ("base", "root"), ("base", "practice"))
        }
    conditional = effects["prefix"]["practice_minus_root"]["right_minus_left"]
    unconditioned = effects["root"]["practice_minus_root"]["right_minus_left"]
    material = conditional >= 0.10 - 1e-12
    retained = unconditioned >= -0.02 - 1e-12
    summaries = {}
    for arm, result in results.items():
        roots = [r for r in result["tasks"] if r["condition"] == "root"]
        prefixes = [r for r in result["tasks"] if r["condition"] == "prefix"]
        summaries[arm] = {
            "panels": result["panels"], "physical": result["physical"],
            "registered": result["registered"], "explicit_padding": result["explicit_padding"],
            "root_theorems_solved_at_32": sum(row["correct"] > 0 for row in roots),
            "root_theorems": len(roots),
            "prefix_tasks_solved_at_32": sum(row["correct"] > 0 for row in prefixes),
            "prefix_tasks": len(prefixes), "tasks": result["tasks"],
        }
    return {
        "classification": "held_out_pilot_theorem_execution_comparison_not_compositional_OOD",
        "arms": summaries, "effects": effects,
        "preregistered_material_screen": {
            "conditional_gain_at_least_10_percentage_points": material,
            "root_loss_no_more_than_2_percentage_points": retained,
            "pass": material and retained,
            "thresholds_are": "practical decision rules, not significance tests or a breakthrough definition",
            "positive_unconditioned_point_effect": unconditioned > 0,
        },
        "interpretation": {
            "conditioning": "All checkpoints receive exactly the same registered starts at evaluation.",
            "scope": "Diagnostic identities are excluded from this pilot's training; their source proofs were in the historical C0 training archive.",
            "limitations": [
                "Conditional gains can reflect repair of unfamiliar supplied contexts.",
                "First-tactic labels do not certify semantic method identity or adherence.",
                "The practical screen does not establish unseen-composition transfer.",
                "Matched proposal budgets do not imply matched admitted groups, optimized tokens or elapsed time.",
                "This analysis does not authenticate which model produced a log; inspect linked run certificates.",
            ],
        },
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--base-log", type=Path, required=True)
    parser.add_argument("--root-log", type=Path, required=True)
    parser.add_argument("--practice-log", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        parser.error("refusing existing comparison output")
    _, bank, verified = load_manifest(args.manifest)
    paths = {arm: getattr(args, f"{arm}_log").resolve() for arm in ("base", "root", "practice")}
    result = compare(bank, {arm: list(read_jsonl(path)) for arm, path in paths.items()})
    result["provenance"] = {
        "manifest": str(args.manifest.resolve()), "manifest_sha256": sha256(args.manifest),
        "authenticated_input_files": verified,
        "proof_logs": {arm: {"path": str(path), "sha256": sha256(path)} for arm, path in paths.items()},
        "runtime_attestation": "required separately; not inferred from registered model revision",
    }
    with args.output.open("x") as stream:
        json.dump(result, stream, indent=2, sort_keys=True)
        stream.write("\n")
    print(json.dumps({"output": str(args.output), "material_screen": result["preregistered_material_screen"]}))


if __name__ == "__main__":
    main()
