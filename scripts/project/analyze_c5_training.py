#!/usr/bin/env python3
"""Compare complete C5 RewardReject-Restart training with complete C3."""

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
    windows,
)


ARCHIVE_SHA256 = "fcffb4a3dc9baf837d4780ec30855308ebc7f0c5086d607162889938b5e426d3"
C5_CLASSIFICATION = "exploratory_full_seed42_h100"


def paired_metrics(c3: dict[str, dict], c5: dict[str, dict], names: list[str]) -> dict:
    deltas: dict[str, list[float]] = {
        "correct": [],
        "modes": [],
        "exact": [],
        "top_mode_share": [],
        "effective_modes": [],
    }
    common_solved = 0
    for name in names:
        left = c3[name]
        right = c5[name]
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
        "mean_delta_c5_minus_c3": {
            key: sum(values) / len(values) if values else None
            for key, values in deltas.items()
        },
        "paired_pratt_wilcoxon_p": {
            key: safe_wilcoxon(values) if values else None
            for key, values in deltas.items()
        },
        "direction_counts": {
            key: {
                "c5_lower": sum(value < 0 for value in values),
                "equal": sum(value == 0 for value in values),
                "c5_higher": sum(value > 0 for value in values),
            }
            for key, values in deltas.items()
        },
    }


def paired_rarefaction(c3: dict[str, dict], c5: dict[str, dict], names: list[str]) -> dict:
    output = {}
    for draws in (1, 2, 4, 8, 16):
        eligible = [
            name
            for name in names
            if c3[name]["correct"] >= draws and c5[name]["correct"] >= draws
        ]
        if not eligible:
            continue
        c3_values = [
            expected_rarefied_modes(c3[name]["modes"], draws) for name in eligible
        ]
        c5_values = [
            expected_rarefied_modes(c5[name]["modes"], draws) for name in eligible
        ]
        deltas = [right - left for left, right in zip(c3_values, c5_values, strict=True)]
        output[str(draws)] = {
            "correct_draws": draws,
            "common_eligible_theorems": len(eligible),
            "c3_mean_expected_modes": sum(c3_values) / len(c3_values),
            "c5_mean_expected_modes": sum(c5_values) / len(c5_values),
            "mean_delta_c5_minus_c3": sum(deltas) / len(deltas),
            "relative_delta_c5_minus_c3": (
                (sum(c5_values) - sum(c3_values)) / sum(c3_values)
            ),
            "paired_pratt_wilcoxon_p": safe_wilcoxon(deltas),
            "c5_higher": sum(value > 1e-12 for value in deltas),
            "equal": sum(abs(value) <= 1e-12 for value in deltas),
            "c3_higher": sum(value < -1e-12 for value in deltas),
        }
    return output


def dominant_mode_panel(
    archive: ModeArchive,
    c3: dict[str, dict],
    c5: dict[str, dict],
    names: list[str],
) -> dict:
    dominant = {
        name: archive.dominant_mode(name, threshold=0.5, min_verified=4)
        for name in names
    }
    eligible = [name for name in names if dominant[name] is not None]
    if len(eligible) != 1_014:
        raise ValueError(f"expected 1,014 archive-eligible theorems, found {len(eligible)}")

    def condition_summary(data: dict[str, dict]) -> dict:
        solved = [name for name in eligible if data[name]["correct"]]
        dominant_counts = {
            name: data[name]["modes"].get(dominant[name], 0) for name in eligible
        }
        correct = sum(data[name]["correct"] for name in eligible)
        observed = sum(dominant_counts.values())
        return {
            "eligible_theorems": len(eligible),
            "solved_eligible_theorems": len(solved),
            "eligible_correct_rollouts": correct,
            "archived_dominant_correct_rollouts": observed,
            "aggregate_archived_dominant_share": observed / correct if correct else None,
            "theorems_with_archived_dominant_observed": sum(
                dominant_counts[name] > 0 for name in eligible
            ),
            "mean_archived_dominant_share_on_solved": (
                sum(dominant_counts[name] / data[name]["correct"] for name in solved)
                / len(solved)
                if solved
                else None
            ),
        }

    common_solved = [
        name for name in eligible if c3[name]["correct"] and c5[name]["correct"]
    ]
    share_deltas = [
        c5[name]["modes"].get(dominant[name], 0) / c5[name]["correct"]
        - c3[name]["modes"].get(dominant[name], 0) / c3[name]["correct"]
        for name in common_solved
    ]
    count_deltas = [
        c5[name]["modes"].get(dominant[name], 0)
        - c3[name]["modes"].get(dominant[name], 0)
        for name in eligible
    ]
    return {
        "eligible_theorems": len(eligible),
        "c3": condition_summary(c3),
        "c5": condition_summary(c5),
        "paired_common_solved": {
            "theorems": len(common_solved),
            "mean_delta_archived_dominant_share_c5_minus_c3": (
                sum(share_deltas) / len(share_deltas) if share_deltas else None
            ),
            "paired_pratt_wilcoxon_p": safe_wilcoxon(share_deltas),
            "c5_lower": sum(value < -1e-12 for value in share_deltas),
            "equal": sum(abs(value) <= 1e-12 for value in share_deltas),
            "c5_higher": sum(value > 1e-12 for value in share_deltas),
        },
        "paired_dominant_count": {
            "mean_delta_c5_minus_c3": sum(count_deltas) / len(count_deltas),
            "paired_pratt_wilcoxon_p": safe_wilcoxon(count_deltas),
            "c5_lower": sum(value < 0 for value in count_deltas),
            "equal": sum(value == 0 for value in count_deltas),
            "c5_higher": sum(value > 0 for value in count_deltas),
        },
        "eligible_names": eligible,
    }


def c0_recovery_relative_to_c3(
    archive: ModeArchive,
    c3: dict[str, dict],
    c5: dict[str, dict],
    names: list[str],
) -> dict:
    output = {}
    for floor in (1, 2, 4):
        base_total = absent_from_c3 = present_in_c5 = 0
        affected = recovered_theorems = 0
        for name in names:
            base_modes = {
                mode for mode, count in archive.counts[name].items() if count >= floor
            }
            missing = base_modes - set(c3[name]["modes"])
            recovered = missing & set(c5[name]["modes"])
            base_total += len(base_modes)
            absent_from_c3 += len(missing)
            present_in_c5 += len(recovered)
            affected += int(bool(missing))
            recovered_theorems += int(bool(recovered))
        output[str(floor)] = {
            "minimum_c0_observations": floor,
            "c0_modes": base_total,
            "c0_modes_absent_from_c3": absent_from_c3,
            "c3_absent_modes_present_in_c5": present_in_c5,
            "recovery_fraction": (
                present_in_c5 / absent_from_c3 if absent_from_c3 else None
            ),
            "theorems_with_c3_absent_mode": affected,
            "theorems_with_c5_recovery": recovered_theorems,
        }
    return output


def validate_intervention_invariants(
    c3_metrics: dict, c5_metrics: dict, archive_sha256: str
) -> None:
    if c3_metrics.get("condition") != "c3_hardblock_restart":
        raise ValueError("C3 source is not the hard-block restart condition")
    if c3_metrics.get("classification") != "registered_full_seed42":
        raise ValueError("C3 source is not the registered full seed-42 run")
    if c5_metrics.get("condition") != "c5_reward_reject_restart":
        raise ValueError("C5 source is not the reward-rejection restart condition")
    if c5_metrics.get("classification") != C5_CLASSIFICATION:
        raise ValueError("C5 source has the wrong exploratory classification")
    for label, metrics in (("C3", c3_metrics), ("C5", c5_metrics)):
        if metrics.get("archive_sha256") != archive_sha256:
            raise ValueError(f"{label} source does not use the frozen C0 archive")
        if metrics.get("proposals") != 308_960:
            raise ValueError(f"{label} source has the wrong registered proposal count")
        if metrics.get("physical_proposals") != 308_992:
            raise ValueError(f"{label} source has the wrong physical proposal count")
    if c3_metrics.get("blocked_correct_zero_advantage", 0) <= 0:
        raise ValueError("C3 source has no zero-advantage blocking")
    if c3_metrics.get("blocked_correct_reward_rejected", 0) not in (None, 0):
        raise ValueError("C3 source unexpectedly uses reward rejection")
    if c5_metrics.get("blocked_correct", 0) <= 0:
        raise ValueError("C5 source has no blocked correct proofs")
    if c5_metrics.get("blocked_correct_zero_advantage") != 0:
        raise ValueError("C5 source unexpectedly uses zero-advantage blocking")
    if c5_metrics.get("blocked_correct_reward_rejected") != c5_metrics.get(
        "blocked_correct"
    ):
        raise ValueError("C5 blocked proofs are not all reward-rejected")
    if c5_metrics.get("physical_blocked_correct_reward_rejected") != c5_metrics.get(
        "physical_blocked_correct"
    ):
        raise ValueError("C5 physical blocked-proof accounting is inconsistent")


def decision_classification(
    overall: dict, rarefaction: dict, dominant: dict
) -> dict:
    c3 = overall["c3"]
    c5 = overall["c5"]
    correct_rate_delta = c5["correct_rate"] - c3["correct_rate"]
    mode_relative_delta = (
        c5["correct_mode_coverage"] - c3["correct_mode_coverage"]
    ) / c3["correct_mode_coverage"]
    rarefied_16 = rarefaction.get("16")
    rarefied_relative_delta = (
        rarefied_16["relative_delta_c5_minus_c3"] if rarefied_16 else None
    )
    dominant_share_delta = dominant["paired_common_solved"][
        "mean_delta_archived_dominant_share_c5_minus_c3"
    ]
    if (
        rarefied_relative_delta is not None
        and rarefied_relative_delta >= 0.05
        and dominant_share_delta is not None
        and dominant_share_delta <= -0.05
        and correct_rate_delta >= -0.05
    ):
        classification = "material_support_for_stronger_exploration"
    elif (
        rarefied_relative_delta is not None
        and rarefied_relative_delta > 0
        and dominant_share_delta is not None
        and dominant_share_delta < 0
    ):
        classification = "directional_support_with_tradeoffs_or_small_effect"
    elif (
        rarefied_relative_delta is not None
        and dominant_share_delta is not None
        and (rarefied_relative_delta <= 0 or dominant_share_delta >= 0)
    ):
        classification = "stronger_exploration_not_supported"
    else:
        classification = "mixed_or_insufficient_training_result"
    return {
        "classification": classification,
        "correct_rate_delta_c5_minus_c3": correct_rate_delta,
        "raw_mode_coverage_relative_delta_c5_minus_c3": mode_relative_delta,
        "rarefied_16_correct_draw_relative_delta_c5_minus_c3": rarefied_relative_delta,
        "paired_archived_dominant_share_delta_c5_minus_c3": dominant_share_delta,
        "material_rule": (
            "rarefied 16-correct-draw mode coverage >=5%, paired archived-dominant "
            "share <=-0.05, and correct-rate loss no worse than 0.05"
        ),
        "directional_rule": (
            "positive rarefied 16-correct-draw delta and negative archived-dominant "
            "share delta"
        ),
        "held_out_claim_status": "requires fresh final-checkpoint evaluation",
    }


def load_metrics(run_dir: Path) -> dict:
    return json.loads((run_dir / "metrics.json").read_text(encoding="utf-8"))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--c0-archive", type=Path, required=True)
    parser.add_argument("--c3-run", type=Path, required=True)
    parser.add_argument("--c5-run", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--window-size", type=int, default=100)
    args = parser.parse_args()

    c3_run = args.c3_run.resolve()
    c5_run = args.c5_run.resolve()
    c3, c3_source = load_run(c3_run, "c3_hardblock_restart")
    c5, c5_source = load_run(
        c5_run,
        "c5_reward_reject_restart",
        expected_classification=C5_CLASSIFICATION,
    )
    if set(c3) != set(c5):
        parser.error("C3 and C5 theorem identities differ")
    names = list(c3)
    archive_path = args.c0_archive.resolve()
    archive_sha256 = sha256(archive_path)
    if archive_sha256 != ARCHIVE_SHA256:
        parser.error("C0 archive is not the frozen registered archive")
    archive = ModeArchive.load(archive_path)
    c3_metrics = load_metrics(c3_run)
    c5_metrics = load_metrics(c5_run)
    validate_intervention_invariants(c3_metrics, c5_metrics, archive_sha256)

    eligible = [
        name
        for name in names
        if archive.dominant_mode(name, threshold=0.5, min_verified=4) is not None
    ]
    eligible_set = set(eligible)
    ineligible = [name for name in names if name not in eligible_set]
    overall = {"c3": summarize(list(c3.values())), "c5": summarize(list(c5.values()))}
    paired = paired_metrics(c3, c5, names)
    rarefaction = paired_rarefaction(c3, c5, names)
    dominant = dominant_mode_panel(archive, c3, c5, names)
    dominant.pop("eligible_names")
    result = {
        "analysis": "c5-versus-c3-full-training-v1",
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "sources": {
            "c0_archive": {"path": str(archive_path), "sha256": archive_sha256},
            "c3": c3_source,
            "c5": c5_source,
        },
        "overall": overall,
        "paired_full_sample": paired,
        "paired_correct_draw_rarefaction": rarefaction,
        "archived_dominant_mode_concentration": dominant,
        "archive_eligibility_strata": {
            "eligible": {
                "c3": summarize([c3[name] for name in eligible]),
                "c5": summarize([c5[name] for name in eligible]),
                "paired": paired_metrics(c3, c5, eligible),
                "paired_correct_draw_rarefaction": paired_rarefaction(
                    c3, c5, eligible
                ),
            },
            "ineligible": {
                "c3": summarize([c3[name] for name in ineligible]),
                "c5": summarize([c5[name] for name in ineligible]),
                "paired": paired_metrics(c3, c5, ineligible),
                "paired_correct_draw_rarefaction": paired_rarefaction(
                    c3, c5, ineligible
                ),
            },
        },
        "training_windows": {
            "window_size_steps": args.window_size,
            "c3": windows(c3, args.window_size),
            "c5": windows(c5, args.window_size),
        },
        "c0_mode_recovery_relative_to_c3": c0_recovery_relative_to_c3(
            archive, c3, c5, names
        ),
        "training_acceptance": {
            "c3": {
                "blocked_correct_zero_advantage": c3_metrics.get(
                    "blocked_correct_zero_advantage"
                ),
                "blocked_correct_reward_rejected": c3_metrics.get(
                    "blocked_correct_reward_rejected", 0
                ),
                "skipped_all_blocked_prompts": c3_metrics.get(
                    "skipped_all_blocked_prompts"
                ),
                "update_batch_samples": c3_metrics.get("update_batch_samples"),
            },
            "c5": {
                "blocked_correct": c5_metrics.get("blocked_correct"),
                "blocked_correct_zero_advantage": c5_metrics.get(
                    "blocked_correct_zero_advantage"
                ),
                "blocked_correct_reward_rejected": c5_metrics.get(
                    "blocked_correct_reward_rejected"
                ),
                "skipped_all_blocked_prompts": c5_metrics.get(
                    "skipped_all_blocked_prompts"
                ),
                "update_batch_samples": c5_metrics.get("update_batch_samples"),
            },
        },
        "frozen_decision_rule": decision_classification(
            overall, rarefaction, dominant
        ),
        "claim_boundary": (
            "This is a one-seed comparison of on-policy training rollouts. C3 and C5 "
            "use the same H100 accelerator class but were executed in different cluster "
            "sessions. Equal-correct-draw rarefaction controls observed correctness, not "
            "all policy-distribution differences. Modes are ordered tactic-head signatures, "
            "not semantic mathematical strategies. Held-out claims require a fresh C5 "
            "final-checkpoint evaluation with blocking disabled."
        ),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    if args.output.exists():
        parser.error(f"refusing to overwrite {args.output}")
    args.output.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(args.output)


if __name__ == "__main__":
    main()
