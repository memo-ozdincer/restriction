#!/usr/bin/env python3
"""Compare C3 HardBlock-Restart with its matched no-blocking control."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

from verl.lean.mode_archive import ModeArchive

from scripts.project.analyze_evaluation_accumulation import safe_wilcoxon
from scripts.project.analyze_training_dynamics import (
    effective_modes,
    expected_rarefied_modes,
    load_run,
    sha256,
    summarize,
    suppression,
    windows,
)


def paired_metrics(control: dict[str, dict], c3: dict[str, dict], names: list[str]) -> dict:
    deltas: dict[str, list[float]] = {
        "correct": [],
        "modes": [],
        "exact": [],
        "top_mode_share": [],
        "effective_modes": [],
    }
    common_solved = 0
    for name in names:
        left = control[name]
        right = c3[name]
        deltas["correct"].append(right["correct"] - left["correct"])
        deltas["modes"].append(len(right["modes"]) - len(left["modes"]))
        deltas["exact"].append(len(right["exact"]) - len(left["exact"]))
        if left["correct"] and right["correct"]:
            common_solved += 1
            deltas["top_mode_share"].append(
                max(right["modes"].values()) / right["correct"]
                - max(left["modes"].values()) / left["correct"]
            )
            deltas["effective_modes"].append(
                effective_modes(right["modes"]) - effective_modes(left["modes"])
            )
    return {
        "theorems": len(names),
        "common_solved_theorems": common_solved,
        "mean_delta_c3_minus_control": {
            key: sum(values) / len(values) if values else None
            for key, values in deltas.items()
        },
        "paired_pratt_wilcoxon_p": {
            key: safe_wilcoxon(values) if values else None
            for key, values in deltas.items()
        },
        "direction_counts": {
            key: {
                "c3_lower": sum(value < 0 for value in values),
                "equal": sum(value == 0 for value in values),
                "c3_higher": sum(value > 0 for value in values),
            }
            for key, values in deltas.items()
        },
    }


def paired_rarefaction(
    control: dict[str, dict], c3: dict[str, dict], names: list[str]
) -> dict:
    output = {}
    for draws in (1, 2, 4, 8, 16):
        eligible = [
            name for name in names
            if control[name]["correct"] >= draws and c3[name]["correct"] >= draws
        ]
        if not eligible:
            continue
        control_values = [
            expected_rarefied_modes(control[name]["modes"], draws) for name in eligible
        ]
        c3_values = [expected_rarefied_modes(c3[name]["modes"], draws) for name in eligible]
        deltas = [right - left for left, right in zip(control_values, c3_values, strict=True)]
        output[str(draws)] = {
            "correct_draws": draws,
            "common_eligible_theorems": len(eligible),
            "control_mean_expected_modes": sum(control_values) / len(control_values),
            "c3_mean_expected_modes": sum(c3_values) / len(c3_values),
            "mean_delta_c3_minus_control": sum(deltas) / len(deltas),
            "paired_pratt_wilcoxon_p": safe_wilcoxon(deltas),
            "c3_higher": sum(value > 1e-12 for value in deltas),
            "equal": sum(abs(value) <= 1e-12 for value in deltas),
            "control_higher": sum(value < -1e-12 for value in deltas),
        }
    return output


def summarize_stratum(
    control: dict[str, dict], c3: dict[str, dict], names: list[str]
) -> dict:
    return {
        "control": summarize([control[name] for name in names]),
        "c3": summarize([c3[name] for name in names]),
        "paired": paired_metrics(control, c3, names),
        "correct_draw_rarefaction": paired_rarefaction(control, c3, names),
    }


def decision_classification(overall: dict) -> dict:
    control_modes = overall["control"]["correct_mode_coverage"]
    c3_modes = overall["c3"]["correct_mode_coverage"]
    relative_delta = (c3_modes - control_modes) / control_modes
    rarefied_16 = overall["correct_draw_rarefaction"].get("16")
    rarefaction_delta = (
        rarefied_16["mean_delta_c3_minus_control"] if rarefied_16 is not None else None
    )
    if relative_delta >= 0.10 and rarefaction_delta is not None and rarefaction_delta > 0:
        classification = "material_training_support_for_blocking"
    elif abs(relative_delta) <= 0.05:
        classification = "practically_null_training_mode_difference"
    elif relative_delta < 0:
        classification = "training_control_exceeds_c3"
    else:
        classification = "mixed_or_intermediate_training_result"
    if relative_delta <= 0:
        attribution_status = "not_supported_control_matches_or_exceeds_c3"
    elif classification == "material_training_support_for_blocking":
        attribution_status = "material_training_support_pending_heldout_control"
    else:
        attribution_status = "unresolved_pending_heldout_control"
    return {
        "classification": classification,
        "blocking_attribution_status": attribution_status,
        "c3_relative_correct_mode_delta": relative_delta,
        "paired_rarefaction_delta_at_16_correct_draws": rarefaction_delta,
        "material_support_rule": "mode delta >= 10% and rarefaction delta at 16 > 0",
        "practical_null_rule": "absolute mode delta <= 5%",
        "falsification_rule": "control mode coverage matches or exceeds C3",
        "held_out_claim_status": "requires matched final-checkpoint evaluation",
    }


def validate_intervention_invariants(
    control_source: dict, c3_source: dict, archive_sha256: str
) -> None:
    if control_source["condition"] != "c3_matched_control":
        raise ValueError("control source is not the registered C3-matched condition")
    if c3_source["condition"] != "c3_hardblock_restart":
        raise ValueError("C3 source is not the registered hard-block condition")
    for key in (
        "blocked_correct_zero_advantage",
        "physical_blocked_correct_zero_advantage",
        "skipped_all_blocked_prompts",
    ):
        if control_source[key] != 0:
            raise ValueError(f"matched control has nonzero {key}")
    if control_source["archive_sha256"] is not None:
        raise ValueError("matched control unexpectedly records a blocking archive")
    if c3_source["archive_sha256"] != archive_sha256:
        raise ValueError("C3 source does not use the supplied frozen C0 archive")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--c0-archive", type=Path, required=True)
    parser.add_argument("--control-run", type=Path, required=True)
    parser.add_argument("--c3-run", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--window-size", type=int, default=100)
    args = parser.parse_args()

    control, control_source = load_run(
        args.control_run.resolve(), "c3_matched_control"
    )
    c3, c3_source = load_run(args.c3_run.resolve(), "c3_hardblock_restart")
    if set(control) != set(c3):
        parser.error("control and C3 theorem identities differ")
    archive_path = args.c0_archive.resolve()
    archive = ModeArchive.load(archive_path)
    archive_sha256 = sha256(archive_path)
    validate_intervention_invariants(control_source, c3_source, archive_sha256)
    names = list(control)
    archive_eligible = [
        name for name in names
        if archive.dominant_mode(name, threshold=0.5, min_verified=4) is not None
    ]
    archive_eligible_set = set(archive_eligible)
    archive_ineligible = [name for name in names if name not in archive_eligible_set]
    if len(archive_eligible) != 1014:
        parser.error(f"expected 1,014 archive-eligible theorems, found {len(archive_eligible)}")

    overall = summarize_stratum(control, c3, names)
    result = {
        "analysis": "c3-versus-matched-control-training-v1",
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "sources": {
            "c0_archive": {"path": str(archive_path), "sha256": archive_sha256},
            "control": control_source,
            "c3": c3_source,
        },
        "overall": overall,
        "archive_eligibility_strata": {
            "eligible": summarize_stratum(control, c3, archive_eligible),
            "ineligible": summarize_stratum(control, c3, archive_ineligible),
        },
        "training_windows": {
            "window_size_steps": args.window_size,
            "control": windows(control, args.window_size),
            "c3": windows(c3, args.window_size),
        },
        "c0_mode_suppression_and_c3_recovery_relative_to_control": suppression(
            archive.counts, control, c3
        ),
        "registered_decision_rule": decision_classification(overall),
        "claim_boundary": (
            "Training rollouts are on-policy observations from evolving policies. The matched "
            "control isolates the training configuration, but blocking-specific held-out claims "
            "require matched final-checkpoint evaluation. Modes are tactic signatures, not "
            "semantic mathematical strategies."
        ),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    if args.output.exists():
        parser.error(f"refusing to overwrite {args.output}")
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(args.output)


if __name__ == "__main__":
    main()
