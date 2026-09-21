#!/usr/bin/env python3
"""Counterfactual admission rules on finalized C2/C3 training proposal groups."""

import argparse
from collections import Counter
import json
from pathlib import Path

import yaml

from scripts.project.analyze_c2_unlikeliness import (
    EXPECTED_ARCHIVE_SHA256, validate_intervention_invariants, validate_mechanism_configs,
)
from scripts.project.analyze_training_dynamics import load_run, sha256
from verl.lean.mode_archive import ModeArchive


def classify(correct, blocked, proposals=32):
    if not all(type(value) is int for value in (correct, blocked, proposals)):
        raise ValueError("counts must be integers")
    if not 0 <= blocked <= correct <= proposals or proposals <= 1:
        raise ValueError("invalid group counts")
    alternatives = correct - blocked
    if correct == 0:
        stratum = "no_correct"
    elif alternatives == 0:
        stratum = "all_correct_blocked" if correct == proposals else "mixed_correctness_only_blocked"
    elif correct == proposals:
        stratum = "all_correct_mixed_modes" if blocked else "all_correct_no_blocked"
    else:
        stratum = "mixed_correctness_with_blocked_and_alternative" if blocked else "mixed_correctness_no_blocked"
    return {
        "stratum": stratum,
        "soft_admitted": 0 < correct < proposals,
        "zero_advantage_admitted": 0 < correct < proposals and alternatives > 0,
        "reward_reject_admitted": 0 < alternatives < proposals,
    }


def summarize(data, archive, *, check_blocked=False):
    panels = {key: {"groups": 0, "strata": Counter(), "admission": Counter()}
              for key in ("all", "archive_eligible", "archive_ineligible")}
    newly_admitted, lost_vs_soft = [], []
    blocked_total = 0
    for name, item in sorted(data.items()):
        correct = item["correct"]
        if sum(item["modes"].values()) != correct:
            raise ValueError(f"mode/correct mismatch for {name}")
        dominant = archive.dominant_mode(name, threshold=0.5, min_verified=4)
        blocked = item["modes"].get(dominant, 0) if dominant is not None else 0
        if check_blocked and blocked != item["blocked"]:
            raise ValueError(f"archive/telemetry blocked mismatch for {name}")
        blocked_total += blocked
        row = classify(correct, blocked)
        for key in ("all", "archive_eligible" if dominant is not None else "archive_ineligible"):
            panel = panels[key]
            panel["groups"] += 1
            panel["strata"][row["stratum"]] += 1
            for rule in ("soft_admitted", "zero_advantage_admitted", "reward_reject_admitted"):
                panel["admission"][rule] += int(row[rule])
        if row["reward_reject_admitted"] and not row["zero_advantage_admitted"]:
            newly_admitted.append({"theorem": name, "step": item["step"],
                                   "correct": correct, "blocked": blocked,
                                   "alternative": correct - blocked})
        if row["soft_admitted"] and not row["reward_reject_admitted"]:
            lost_vs_soft.append(name)
    return {"panels": panels, "archive_matching_correct_proposals": blocked_total,
            "newly_admitted_vs_zero_advantage": newly_admitted,
            "lost_vs_soft": lost_vs_soft}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-manifest", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError(args.output)
    manifest = json.loads(args.source_manifest.read_text())
    archive_source = manifest["sources"]["c0_archive"]
    archive_path = Path(archive_source["path"])
    if sha256(archive_path) != archive_source["sha256"] or archive_source["sha256"] != EXPECTED_ARCHIVE_SHA256:
        raise ValueError("archive differs from the frozen source")
    archive = ModeArchive.load(archive_path)
    runs = {key: Path(manifest["sources"][key]["run_dir"]) for key in ("c2", "c3")}
    validate_mechanism_configs(runs["c2"], runs["c3"])
    sources, summaries, names = {}, {}, {}
    for key, condition in (("c2", "c2_unlikeliness_2"), ("c3", "c3_hardblock_restart")):
        data, source = load_run(runs[key], condition)
        old = manifest["sources"][key]
        for field in ("proof_log_sha256", "metrics_sha256", "git_commit"):
            if source[field] != old[field]:
                raise ValueError(f"source mismatch: {key} {field}")
        if len(data) != 9655 or source["registered_proposals"] != 308960:
            raise ValueError("unexpected registered panel")
        if source["excluded_padding_proposals"] != 32:
            raise ValueError("unexpected padding count")
        metrics = json.loads(Path(source["metrics"]).read_text())
        if sum(item["correct"] for item in data.values()) != metrics["correct"]:
            raise ValueError("correct counts do not reproduce finalized metrics")
        config_path = runs[key] / "hydra/.hydra/config.yaml"
        source["resolved_config_sha256"] = sha256(config_path)
        if source["resolved_config_sha256"] != metrics["resolved_config_sha256"]:
            raise ValueError("resolved config differs from finalized metrics")
        config = yaml.safe_load(config_path.read_text())
        lean = config["lean"]
        if (lean["num_samples"] != 32 or not lean["advantage_threshold"]
                or lean["rejection_sampling"] or lean["max_samples"] < 32):
            raise ValueError("unsupported admission settings")
        if key == "c3" and (lean["hard_blocking"]["threshold"] != 0.5
                            or lean["hard_blocking"]["min_verified"] != 4):
            raise ValueError("unexpected archive rule")
        source["train_parquet_sha256"] = sha256(runs[key] / "train.parquet")
        summaries[key] = summarize(data, archive, check_blocked=key == "c3")
        if summaries[key]["panels"]["archive_eligible"]["groups"] != 1014:
            raise ValueError("unexpected archive eligibility")
        sources[key], names[key] = source, set(data)
    validate_intervention_invariants(sources["c2"], sources["c3"])
    if names["c2"] != names["c3"] or sources["c2"]["train_parquet_sha256"] != sources["c3"]["train_parquet_sha256"]:
        raise ValueError("training panels differ")
    if summaries["c3"]["archive_matching_correct_proposals"] != sources["c3"]["blocked_correct_zero_advantage"]:
        raise ValueError("C3 blocked counts differ from finalized metrics")
    output = {
        "analysis": "exploratory-saved-training-group-admission-v1",
        "scope": "same-sample admission counterfactuals; not a C5 training prediction",
        "source_manifest_sha256": sha256(args.source_manifest),
        "archive": archive_source, "sources": sources, "conditions": summaries,
        "notes": ["First 32 proposals per theorem; one padded group excluded per condition.",
                  "C2 archive matching is hypothetical; C2 used no blocking archive.",
                  "Admission counts are not optimizer-update counts or population performance estimates."],
    }
    with args.output.open("x") as stream:
        json.dump(output, stream, indent=2, sort_keys=True)
        stream.write("\n")


if __name__ == "__main__":
    main()
