#!/usr/bin/env python3
"""Compare held-out C3 and matched-control proof distributions through pass@K."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

from scipy.stats import binomtest

from scripts.project.analyze_evaluation_accumulation import (
    accumulation_summary,
    full_counts,
    load_run,
    paired_full_sample,
    representation_coverage,
    safe_wilcoxon,
    select_names,
    validate_finalized_metrics,
)
from scripts.project.analyze_training_dynamics import expected_rarefied_modes


DATASETS = ("combined", "registered_valid", "minif2f_test")
REPRESENTATIONS = (
    "first_head",
    "first_two_heads",
    "unordered_head_set",
    "head_multiset",
    "ordered_head_sequence",
    "exact_proof",
)


def mcnemar_exact(control_solved: list[bool], c3_solved: list[bool]) -> dict:
    control_only = sum(left and not right for left, right in zip(control_solved, c3_solved, strict=True))
    c3_only = sum(right and not left for left, right in zip(control_solved, c3_solved, strict=True))
    discordant = control_only + c3_only
    p = float(binomtest(c3_only, discordant, 0.5).pvalue) if discordant else 1.0
    return {"control_only": control_only, "c3_only": c3_only, "exact_p": p}


def paired_rarefaction(control: dict[str, dict], c3: dict[str, dict], names: list[str]) -> dict:
    output = {}
    for draws in (1, 2, 4, 8, 16, 32, 64):
        eligible = [
            name for name in names
            if full_counts(control[name])[0] >= draws and full_counts(c3[name])[0] >= draws
        ]
        if not eligible:
            continue
        control_values = [
            expected_rarefied_modes(full_counts(control[name])[1], draws) for name in eligible
        ]
        c3_values = [
            expected_rarefied_modes(full_counts(c3[name])[1], draws) for name in eligible
        ]
        deltas = [right - left for left, right in zip(control_values, c3_values, strict=True)]
        output[str(draws)] = {
            "correct_draws": draws,
            "common_eligible_theorems": len(eligible),
            "control_mean_expected_modes": sum(control_values) / len(control_values),
            "c3_mean_expected_modes": sum(c3_values) / len(c3_values),
            "mean_delta_c3_minus_control": sum(deltas) / len(deltas),
            "paired_pratt_wilcoxon_p": safe_wilcoxon(deltas),
            "c3_higher": sum(delta > 1e-12 for delta in deltas),
            "equal": sum(abs(delta) <= 1e-12 for delta in deltas),
            "control_higher": sum(delta < -1e-12 for delta in deltas),
        }
    return output


def representation_panel(control: dict[str, dict], c3: dict[str, dict], names: list[str]) -> dict:
    output = {}
    for representation in REPRESENTATIONS:
        control_values = [representation_coverage(control[name], representation) for name in names]
        c3_values = [representation_coverage(c3[name], representation) for name in names]
        deltas = [right - left for left, right in zip(control_values, c3_values, strict=True)]
        output[representation] = {
            "control_coverage": sum(control_values),
            "c3_coverage": sum(c3_values),
            "relative_delta": (
                (sum(c3_values) - sum(control_values)) / sum(control_values)
                if sum(control_values) else None
            ),
            "mean_delta_per_theorem": sum(deltas) / len(deltas),
            "paired_pratt_wilcoxon_p": safe_wilcoxon(deltas),
            "c3_higher": sum(delta > 0 for delta in deltas),
            "equal": sum(delta == 0 for delta in deltas),
            "control_higher": sum(delta < 0 for delta in deltas),
        }
    return output


def dataset_analysis(
    control: dict[str, dict], c3: dict[str, dict], names: list[str], ks: list[int]
) -> dict:
    accumulation = {
        "control": {str(k): accumulation_summary(control, names, k) for k in ks},
        "c3": {str(k): accumulation_summary(c3, names, k) for k in ks},
    }
    curve_delta = {}
    for k in ks:
        left = accumulation["control"][str(k)]["expected_from_full_sample"]
        right = accumulation["c3"][str(k)]["expected_from_full_sample"]
        curve_delta[str(k)] = {
            "pass_at_n": right["pass_at_n"] - left["pass_at_n"],
            "correct_mode_coverage": right["correct_mode_coverage"] - left["correct_mode_coverage"],
            "mean_correct_modes_per_theorem": (
                right["mean_correct_modes_per_theorem"]
                - left["mean_correct_modes_per_theorem"]
            ),
            "exact_correct_proof_coverage": (
                right["exact_correct_proof_coverage"]
                - left["exact_correct_proof_coverage"]
            ),
        }
    control_solved = [full_counts(control[name])[0] > 0 for name in names]
    c3_solved = [full_counts(c3[name])[0] > 0 for name in names]
    return {
        "accumulation": accumulation,
        "expected_curve_delta_c3_minus_control": curve_delta,
        "paired_full_sample": paired_full_sample(control, c3, names),
        "paired_correct_draw_rarefaction": paired_rarefaction(control, c3, names),
        "representation_robustness": representation_panel(control, c3, names),
        "solved_theorem_mcnemar": mcnemar_exact(control_solved, c3_solved),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--control-run", type=Path, required=True)
    parser.add_argument("--c3-run", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    control, control_source = load_run(args.control_run, "c3_matched_control")
    c3, c3_source = load_run(args.c3_run, "c3_hardblock_restart")
    if set(control) != set(c3):
        parser.error("control and C3 evaluation theorem identities differ")
    if control_source["num_samples"] != c3_source["num_samples"]:
        parser.error("control and C3 proposal budgets differ")
    if control_source["evaluation_parquet_sha256"] != c3_source["evaluation_parquet_sha256"]:
        parser.error("control and C3 evaluation parquets differ")
    num_samples = control_source["num_samples"]
    ks = [k for k in (1, 4, 8, 16, 32, 64, 128) if k <= num_samples]
    validate_finalized_metrics(control, control_source, ks)
    validate_finalized_metrics(c3, c3_source, ks)

    result = {
        "analysis": "c3-versus-matched-control-heldout-accumulation-v1",
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "num_samples_per_theorem": num_samples,
        "evaluation_parquet_sha256": control_source["evaluation_parquet_sha256"],
        "sources": {
            "control": {k: v for k, v in control_source.items() if k != "metrics_payload"},
            "c3": {k: v for k, v in c3_source.items() if k != "metrics_payload"},
        },
        "datasets": {
            dataset: dataset_analysis(control, c3, select_names(control, dataset), ks)
            for dataset in DATASETS
        },
        "claim_boundary": (
            "This matched held-out contrast identifies the effect of hard blocking within the "
            "seed-42 C3 training configuration. It is one training seed. Modes are deterministic "
            "tactic signatures, not semantic mathematical strategies."
        ),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    if args.output.exists():
        parser.error(f"refusing to overwrite {args.output}")
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(args.output)


if __name__ == "__main__":
    main()
