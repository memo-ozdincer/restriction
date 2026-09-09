#!/usr/bin/env python3
"""Compare C2 soft unlikeliness and C3 hard blocking on frozen pass@128 data."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

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


CONDITIONS = ("c0_base", "c2_unlikeliness_2", "c3_hardblock_restart")
DATASETS = ("combined", "registered_valid", "minif2f_test")


def paired_correct_rarefaction(
    c2: dict[str, dict], c3: dict[str, dict], names: list[str]
) -> dict:
    output = {}
    for draws in (1, 2, 4, 8, 16, 32, 64):
        eligible = [
            name for name in names
            if full_counts(c2[name])[0] >= draws and full_counts(c3[name])[0] >= draws
        ]
        if not eligible:
            continue
        c2_values = [
            expected_rarefied_modes(full_counts(c2[name])[1], draws) for name in eligible
        ]
        c3_values = [
            expected_rarefied_modes(full_counts(c3[name])[1], draws) for name in eligible
        ]
        deltas = [right - left for left, right in zip(c2_values, c3_values, strict=True)]
        c2_mean = sum(c2_values) / len(c2_values)
        c3_mean = sum(c3_values) / len(c3_values)
        output[str(draws)] = {
            "correct_draws": draws,
            "common_eligible_theorems": len(eligible),
            "c2_mean_expected_modes": c2_mean,
            "c3_mean_expected_modes": c3_mean,
            "mean_delta_c3_minus_c2": sum(deltas) / len(deltas),
            "relative_delta_c3_minus_c2": (c3_mean - c2_mean) / c2_mean,
            "paired_pratt_wilcoxon_p": safe_wilcoxon(deltas),
            "c3_higher": sum(delta > 1e-12 for delta in deltas),
            "equal": sum(abs(delta) <= 1e-12 for delta in deltas),
            "c2_higher": sum(delta < -1e-12 for delta in deltas),
        }
    return output


def representation_robustness(
    c2: dict[str, dict], c3: dict[str, dict], names: list[str]
) -> dict:
    output = {}
    for representation in (
        "first_head",
        "first_two_heads",
        "unordered_head_set",
        "head_multiset",
        "ordered_head_sequence",
        "exact_proof",
    ):
        c2_values = [representation_coverage(c2[name], representation) for name in names]
        c3_values = [representation_coverage(c3[name], representation) for name in names]
        deltas = [right - left for left, right in zip(c2_values, c3_values, strict=True)]
        output[representation] = {
            "c2_coverage": sum(c2_values),
            "c3_coverage": sum(c3_values),
            "relative_delta_c3_minus_c2": (
                (sum(c3_values) - sum(c2_values)) / sum(c2_values)
            ),
            "mean_delta_c3_minus_c2_per_theorem": sum(deltas) / len(deltas),
            "paired_pratt_wilcoxon_p": safe_wilcoxon(deltas),
            "c3_higher": sum(delta > 0 for delta in deltas),
            "equal": sum(delta == 0 for delta in deltas),
            "c2_higher": sum(delta < 0 for delta in deltas),
        }
    return output


def c0_suppression_recovery(
    c0: dict[str, dict], c2: dict[str, dict], c3: dict[str, dict], names: list[str]
) -> dict:
    output = {}
    for floor in (1, 2, 4, 8):
        base = absent = recovered = 0
        affected = recovered_theorems = 0
        for name in names:
            c0_modes = {
                mode for mode, count in full_counts(c0[name])[1].items() if count >= floor
            }
            c2_modes = set(full_counts(c2[name])[1])
            c3_modes = set(full_counts(c3[name])[1])
            suppressed = c0_modes - c2_modes
            restored = suppressed & c3_modes
            base += len(c0_modes)
            absent += len(suppressed)
            recovered += len(restored)
            affected += int(bool(suppressed))
            recovered_theorems += int(bool(restored))
        output[str(floor)] = {
            "minimum_c0_observations": floor,
            "c0_modes": base,
            "c0_modes_absent_from_c2": absent,
            "c2_absent_modes_present_in_c3": recovered,
            "recovery_fraction": recovered / absent if absent else None,
            "theorems_with_c2_absent_mode": affected,
            "theorems_with_c3_recovery": recovered_theorems,
        }
    return output


def decision_classification(
    accumulation: dict, rarefaction: dict, representation: dict
) -> dict:
    c2_full = accumulation["c2_unlikeliness_2"]["128"]["observed_prefix"]
    c3_full = accumulation["c3_hardblock_restart"]["128"]["observed_prefix"]
    raw_relative = (
        c3_full["correct_mode_coverage"] - c2_full["correct_mode_coverage"]
    ) / c2_full["correct_mode_coverage"]
    correctness_delta = (
        c3_full["correct"] - c2_full["correct"]
    ) / (accumulation["c2_unlikeliness_2"]["128"]["theorems"] * 128)
    rare_16 = rarefaction.get("16")
    rare_relative = rare_16["relative_delta_c3_minus_c2"] if rare_16 else None
    directions = [
        payload["relative_delta_c3_minus_c2"] for payload in representation.values()
    ]

    if (
        raw_relative >= 0.05
        and rare_relative is not None
        and rare_relative >= 0.05
        and correctness_delta >= -0.05
        and all(delta > 0 for delta in directions)
    ):
        classification = "material_heldout_support_for_hard_over_soft_exploration"
    elif (
        abs(raw_relative) <= 0.05
        and rare_relative is not None
        and abs(rare_relative) <= 0.05
    ):
        classification = "practically_null_heldout_hard_versus_soft_difference"
    elif raw_relative <= -0.05 and rare_relative is not None and rare_relative <= 0:
        classification = "heldout_soft_unlikeliness_outperforms_hard_blocking"
    else:
        classification = "mixed_or_representation_sensitive_heldout_result"
    return {
        "classification": classification,
        "c3_relative_raw_mode_delta_at_128": raw_relative,
        "c3_relative_rarefied_mode_delta_at_16_correct_draws": rare_relative,
        "c3_minus_c2_correctness_rate": correctness_delta,
        "representation_directions": directions,
        "material_support_rule": (
            "at least +5% raw and 16-correct-draw tactic-mode coverage, no more than a "
            "five-point correctness loss, and positive direction at all six frozen representations"
        ),
        "practical_null_rule": "both raw and 16-draw relative mode differences are within +/-5%",
        "claim_boundary": "syntactic exploration under one registered seed; not semantic strategy diversity",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--c0-run", type=Path, required=True)
    parser.add_argument("--c2-run", type=Path, required=True)
    parser.add_argument("--c3-run", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    run_args = {
        "c0_base": args.c0_run,
        "c2_unlikeliness_2": args.c2_run,
        "c3_hardblock_restart": args.c3_run,
    }
    conditions = {}
    sources = {}
    for condition, path in run_args.items():
        conditions[condition], sources[condition] = load_run(path.resolve(), condition)
    theorem_sets = {frozenset(data) for data in conditions.values()}
    sample_counts = {source["num_samples"] for source in sources.values()}
    parquet_hashes = {source["evaluation_parquet_sha256"] for source in sources.values()}
    if len(theorem_sets) != 1 or sample_counts != {128} or len(parquet_hashes) != 1:
        parser.error("C0/C2/C3 must use the same frozen 128-proposal evaluation panel")
    ks = [1, 4, 8, 16, 32, 64, 128]
    for condition in CONDITIONS:
        validate_finalized_metrics(conditions[condition], sources[condition], ks)

    accumulation = {}
    paired = {}
    rarefaction = {}
    robustness = {}
    recovery = {}
    reference = conditions["c0_base"]
    for dataset in DATASETS:
        names = select_names(reference, dataset)
        accumulation[dataset] = {
            condition: {
                str(k): accumulation_summary(conditions[condition], names, k) for k in ks
            }
            for condition in CONDITIONS
        }
        paired[dataset] = paired_full_sample(
            conditions["c2_unlikeliness_2"],
            conditions["c3_hardblock_restart"],
            names,
        )
        rarefaction[dataset] = paired_correct_rarefaction(
            conditions["c2_unlikeliness_2"],
            conditions["c3_hardblock_restart"],
            names,
        )
        robustness[dataset] = representation_robustness(
            conditions["c2_unlikeliness_2"],
            conditions["c3_hardblock_restart"],
            names,
        )
        recovery[dataset] = c0_suppression_recovery(
            conditions["c0_base"],
            conditions["c2_unlikeliness_2"],
            conditions["c3_hardblock_restart"],
            names,
        )

    serializable_sources = {
        condition: {key: value for key, value in source.items() if key != "metrics_payload"}
        for condition, source in sources.items()
    }
    decision = decision_classification(
        accumulation["combined"], rarefaction["combined"], robustness["combined"]
    )
    result = {
        "analysis": "c2-soft-unlikeliness-versus-c3-hard-blocking-pass128-v1",
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "hypothesis": (
            "Persistent hard exclusion preserves a broader useful correct tail than soft "
            "within-batch likelihood reweighting under matched training and evaluation budgets."
        ),
        "evaluation_parquet_sha256": parquet_hashes.pop(),
        "sources": serializable_sources,
        "accumulation": accumulation,
        "paired_full_sample_c3_minus_c2": paired,
        "correct_draw_rarefaction_c3_minus_c2": rarefaction,
        "representation_robustness_c3_minus_c2": robustness,
        "c0_modes_absent_from_c2_and_recovered_by_c3": recovery,
        "registered_decision_rule": decision,
        "claim_boundary": (
            "All differences are finite-sample syntactic proof-distribution comparisons at seed 42. "
            "They do not establish semantic mathematical-strategy diversity."
        ),
    }
    if args.output.exists():
        parser.error(f"refusing to overwrite {args.output}")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(args.output)


if __name__ == "__main__":
    main()
