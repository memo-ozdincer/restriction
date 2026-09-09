#!/usr/bin/env python3
"""Compare C2 soft unlikeliness with C3 persistent hard blocking."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

import yaml

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


EXPECTED_ARCHIVE_SHA256 = "fcffb4a3dc9baf837d4780ec30855308ebc7f0c5086d607162889938b5e426d3"


def _resolved_config(run_dir: Path) -> dict:
    path = run_dir / "hydra/.hydra/config.yaml"
    payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"resolved config is not a mapping: {path}")
    return payload


def validate_mechanism_configs(c2_run: Path, c3_run: Path) -> None:
    c2 = _resolved_config(c2_run)
    c3 = _resolved_config(c3_run)
    c2_lean = c2["lean"]
    c3_lean = c3["lean"]
    c2_actor = c2["actor_rollout_ref"]["actor"]
    c3_actor = c3["actor_rollout_ref"]["actor"]

    if c2_lean["rank_penalty"] != 0.25 or c2_lean["hard_blocking"]["enabled"]:
        raise ValueError("C2 config is not soft rank-penalty unlikeliness")
    if c3_lean["rank_penalty"] != 0.0 or not c3_lean["hard_blocking"]["enabled"]:
        raise ValueError("C3 config is not persistent hard blocking")
    for label, left, right in (
        ("PPO epochs", c2_actor["ppo_epochs"], c3_actor["ppo_epochs"]),
        ("KL coefficient", c2_actor["kl_loss_coef"], c3_actor["kl_loss_coef"]),
        ("training data", c2["data"]["train_files"], c3["data"]["train_files"]),
        ("response length", c2["actor_rollout_ref"]["rollout"]["response_length"],
         c3["actor_rollout_ref"]["rollout"]["response_length"]),
        ("samples per theorem", c2_lean["num_samples"], c3_lean["num_samples"]),
    ):
        if label == "training data":
            # Run-local paths differ; their content is checked independently by load_run.
            continue
        if left != right:
            raise ValueError(f"C2/C3 mismatch in {label}: {left!r} != {right!r}")
    if c2_actor["ppo_epochs"] != 2 or c2_actor["kl_loss_coef"] != 0.10:
        raise ValueError("C2 does not use the registered two-epoch, KL=0.10 recipe")


def validate_intervention_invariants(c2_source: dict, c3_source: dict) -> None:
    if c2_source["condition"] != "c2_unlikeliness_2":
        raise ValueError("C2 source has the wrong condition")
    if c3_source["condition"] != "c3_hardblock_restart":
        raise ValueError("C3 source has the wrong condition")
    for key in (
        "blocked_correct_zero_advantage",
        "physical_blocked_correct_zero_advantage",
        "skipped_all_blocked_prompts",
    ):
        if c2_source[key] != 0:
            raise ValueError(f"C2 unexpectedly has nonzero {key}")
    if c2_source["archive_sha256"] is not None:
        raise ValueError("C2 unexpectedly records a blocking archive")
    if c3_source["archive_sha256"] != EXPECTED_ARCHIVE_SHA256:
        raise ValueError("C3 does not use the frozen registered C0 archive")


def paired_metrics(c2: dict[str, dict], c3: dict[str, dict], names: list[str]) -> dict:
    deltas: dict[str, list[float]] = {
        "correct": [],
        "modes": [],
        "exact": [],
        "top_mode_share": [],
        "effective_modes": [],
    }
    for name in names:
        left = c2[name]
        right = c3[name]
        deltas["correct"].append(right["correct"] - left["correct"])
        deltas["modes"].append(len(right["modes"]) - len(left["modes"]))
        deltas["exact"].append(len(right["exact"]) - len(left["exact"]))
        if left["correct"] and right["correct"]:
            deltas["top_mode_share"].append(
                max(right["modes"].values()) / right["correct"]
                - max(left["modes"].values()) / left["correct"]
            )
            deltas["effective_modes"].append(
                effective_modes(right["modes"]) - effective_modes(left["modes"])
            )
    return {
        "theorems": len(names),
        "mean_delta_c3_minus_c2": {
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


def paired_rarefaction(c2: dict[str, dict], c3: dict[str, dict], names: list[str]) -> dict:
    output = {}
    for draws in (1, 2, 4, 8, 16, 32):
        eligible = [
            name for name in names
            if c2[name]["correct"] >= draws and c3[name]["correct"] >= draws
        ]
        if not eligible:
            continue
        c2_values = [expected_rarefied_modes(c2[name]["modes"], draws) for name in eligible]
        c3_values = [expected_rarefied_modes(c3[name]["modes"], draws) for name in eligible]
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
            "c3_higher": sum(value > 1e-12 for value in deltas),
            "equal": sum(abs(value) <= 1e-12 for value in deltas),
            "c2_higher": sum(value < -1e-12 for value in deltas),
        }
    return output


def summarize_stratum(c2: dict[str, dict], c3: dict[str, dict], names: list[str]) -> dict:
    return {
        "c2": summarize([c2[name] for name in names]),
        "c3": summarize([c3[name] for name in names]),
        "paired": paired_metrics(c2, c3, names),
        "correct_draw_rarefaction": paired_rarefaction(c2, c3, names),
    }


def c0_suppression_recovery(
    c0_counts: dict[str, dict[str, int]], c2: dict[str, dict], c3: dict[str, dict]
) -> dict:
    floors = {}
    for floor in (1, 2, 4):
        base_total = absent = recovered = 0
        affected_theorems: set[str] = set()
        recovered_theorems: set[str] = set()
        for name, counts in c0_counts.items():
            base_modes = {mode for mode, count in counts.items() if count >= floor}
            c2_modes = set(c2[name]["modes"])
            c3_modes = set(c3[name]["modes"])
            lost = base_modes - c2_modes
            restored = lost & c3_modes
            base_total += len(base_modes)
            absent += len(lost)
            recovered += len(restored)
            if lost:
                affected_theorems.add(name)
            if restored:
                recovered_theorems.add(name)
        floors[str(floor)] = {
            "minimum_c0_observations": floor,
            "c0_modes": base_total,
            "c0_modes_absent_from_c2": absent,
            "c2_absent_modes_present_in_c3": recovered,
            "recovery_fraction": recovered / absent if absent else None,
            "theorems_with_c2_absent_mode": len(affected_theorems),
            "theorems_with_c3_recovery": len(recovered_theorems),
        }

    examples = []
    for name, counts in c0_counts.items():
        for mode, base_count in counts.items():
            if base_count < 2 or mode in c2[name]["modes"] or mode not in c3[name]["modes"]:
                continue
            example = c3[name]["examples"][mode]
            examples.append(
                {
                    "theorem": name,
                    "mode_id": mode,
                    "c0_count": base_count,
                    "c2_count": c2[name]["modes"].get(mode, 0),
                    "c3_count": c3[name]["modes"][mode],
                    "tactic_heads": example["tactic_heads"],
                    "c3_example_proof": example["proof"],
                }
            )
    examples.sort(
        key=lambda item: (-item["c3_count"], item["c0_count"], item["theorem"], item["mode_id"])
    )
    return {"by_c0_count_floor": floors, "top_recovered_examples": examples[:100]}


def decision_classification(overall: dict, proposals: int) -> dict:
    c2_modes = overall["c2"]["correct_mode_coverage"]
    c3_modes = overall["c3"]["correct_mode_coverage"]
    raw_relative = (c3_modes - c2_modes) / c2_modes
    rarefied = overall["correct_draw_rarefaction"].get("16")
    rarefied_relative = rarefied["relative_delta_c3_minus_c2"] if rarefied else None
    correctness_delta = (overall["c3"]["correct"] - overall["c2"]["correct"]) / proposals

    if (
        raw_relative >= 0.05
        and rarefied_relative is not None
        and rarefied_relative >= 0.05
        and correctness_delta >= -0.05
    ):
        classification = "material_training_support_for_hard_over_soft_exploration"
    elif (
        abs(raw_relative) <= 0.05
        and rarefied_relative is not None
        and abs(rarefied_relative) <= 0.05
    ):
        classification = "practically_null_hard_versus_soft_difference"
    elif raw_relative <= -0.05 and rarefied_relative is not None and rarefied_relative <= 0:
        classification = "soft_unlikeliness_outperforms_hard_blocking"
    else:
        classification = "mixed_or_intermediate_hard_versus_soft_result"
    return {
        "classification": classification,
        "c3_relative_raw_mode_delta": raw_relative,
        "c3_relative_rarefied_mode_delta_at_16_correct_draws": rarefied_relative,
        "c3_minus_c2_correctness_rate": correctness_delta,
        "material_support_rule": (
            "raw mode coverage and 16-correct-draw expected coverage each improve by at least "
            "5%, with no more than a five-point correctness-rate loss"
        ),
        "practical_null_rule": "both raw and 16-draw relative mode differences are within +/-5%",
        "soft_superiority_rule": (
            "C2 raw mode coverage exceeds C3 by at least 5% and C2 does not lose at 16 draws"
        ),
        "held_out_claim_status": "requires frozen C2 pass@128 final-checkpoint evaluation",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--c0-archive", type=Path, required=True)
    parser.add_argument("--c2-run", type=Path, required=True)
    parser.add_argument("--c3-run", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--window-size", type=int, default=100)
    args = parser.parse_args()

    c2_run = args.c2_run.resolve()
    c3_run = args.c3_run.resolve()
    c2, c2_source = load_run(c2_run, "c2_unlikeliness_2")
    c3, c3_source = load_run(c3_run, "c3_hardblock_restart")
    if set(c2) != set(c3):
        parser.error("C2 and C3 theorem identities differ")
    validate_mechanism_configs(c2_run, c3_run)
    validate_intervention_invariants(c2_source, c3_source)

    archive_path = args.c0_archive.resolve()
    if sha256(archive_path) != EXPECTED_ARCHIVE_SHA256:
        parser.error("C0 archive does not match the frozen registered archive")
    archive = ModeArchive.load(archive_path)
    names = list(c2)
    eligible = [
        name for name in names
        if archive.dominant_mode(name, threshold=0.5, min_verified=4) is not None
    ]
    eligible_set = set(eligible)
    ineligible = [name for name in names if name not in eligible_set]
    if len(eligible) != 1014:
        parser.error(f"expected 1,014 archive-eligible theorems, found {len(eligible)}")

    overall = summarize_stratum(c2, c3, names)
    result = {
        "analysis": "c2-soft-unlikeliness-versus-c3-hard-blocking-training-v1",
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "hypothesis": (
            "Persistent theorem-level hard exclusion preserves a broader correct proof tail "
            "than within-batch likelihood-rank reweighting at the same optimizer and proposal budget."
        ),
        "sources": {
            "c0_archive": {"path": str(archive_path), "sha256": sha256(archive_path)},
            "c2": c2_source,
            "c3": c3_source,
        },
        "overall": overall,
        "archive_eligibility_strata": {
            "eligible": summarize_stratum(c2, c3, eligible),
            "ineligible": summarize_stratum(c2, c3, ineligible),
        },
        "training_windows": {
            "window_size_steps": args.window_size,
            "c2": windows(c2, args.window_size),
            "c3": windows(c3, args.window_size),
        },
        "c0_mode_suppression_and_c3_recovery_relative_to_c2": c0_suppression_recovery(
            archive.counts, c2, c3
        ),
        "registered_decision_rule": decision_classification(overall, len(names) * 32),
        "claim_boundary": (
            "This isolates the registered exploration mechanism because C2 and C3 share the "
            "two-epoch, KL=0.10 recipe. Training rollouts remain on-policy observations; final-policy "
            "claims require the frozen pass@128 evaluation. Modes are tactic signatures, not semantic strategies."
        ),
    }
    if args.output.exists():
        parser.error(f"refusing to overwrite {args.output}")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(args.output)


if __name__ == "__main__":
    main()
