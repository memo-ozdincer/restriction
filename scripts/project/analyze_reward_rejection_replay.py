#!/usr/bin/env python3
"""Replay frozen C3 rollouts through the proposed reward-rejection rule."""

from __future__ import annotations

import argparse
from collections import defaultdict
import hashlib
import json
import math
from pathlib import Path
from typing import Any

import pandas as pd


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_RUN = ROOT.parent / "runs/c3-hardblock-restart-full-20260814-seed42-265aecd"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def latest_proof_log(run_dir: Path) -> Path:
    paths = sorted((run_dir / "artifacts/proofs").glob("global_step_*.jsonl"))
    if not paths:
        raise ValueError("run has no proof snapshot")
    return paths[-1]


def standardized_binary_advantages(successes: int, total: int) -> tuple[float, float]:
    """Match the trainer's sample-standard-deviation GRPO normalization."""
    if not 0 < successes < total:
        raise ValueError("group must contain both accepted and rejected outcomes")
    mean = successes / total
    variance_numerator = successes * (1.0 - mean) ** 2 + (total - successes) * mean ** 2
    sample_std = math.sqrt(variance_numerator / (total - 1))
    return (0.0 - mean) / (sample_std + 1e-6), (1.0 - mean) / (sample_std + 1e-6)


def analyze(run_dir: Path) -> dict[str, Any]:
    metrics_path = run_dir / "metrics.json"
    train_path = run_dir / "train.parquet"
    proof_path = latest_proof_log(run_dir)
    metrics = json.loads(metrics_path.read_text(encoding="utf-8"))
    if metrics.get("condition") != "c3_hardblock_restart":
        raise ValueError("source is not the finalized C3 hard-block run")
    if metrics.get("proposals") != 308_960:
        raise ValueError("source does not have the registered proposal budget")
    if metrics.get("proof_log_sha256") != sha256(proof_path):
        raise ValueError("proof snapshot checksum differs from finalized C3 metrics")

    expected_names = [str(value) for value in pd.read_parquet(train_path)["theorem_full_name"]]
    if len(expected_names) != 9_655:
        raise ValueError("source training split does not contain 9,655 theorems")
    by_theorem: dict[str, list[dict[str, Any]]] = defaultdict(list)
    with proof_path.open(encoding="utf-8") as stream:
        for line in stream:
            record = json.loads(line)
            by_theorem[str(record["theorem_name"])].append(record)

    groups: list[tuple[int, int, int]] = []
    for name in expected_names:
        rows = by_theorem[name][:32]
        if len(rows) != 32:
            raise ValueError(f"{name!r} does not have 32 registered proposals")
        correct = sum(bool(row.get("correct")) for row in rows)
        blocked = sum(bool(row.get("blocked_correct")) for row in rows)
        groups.append((correct, blocked, correct - blocked))

    affected = [group for group in groups if group[1] > 0]
    active = [group for group in affected if group[2] > 0]
    all_blocked = [group for group in affected if group[2] == 0]
    newly_trainable = [group for group in active if group[0] == 32]

    blocked_advantage_sum = 0.0
    alternative_advantage_sum = 0.0
    incorrect_advantage_sum = 0.0
    blocked_count = 0
    alternative_count = 0
    incorrect_count = 0
    for correct, blocked, alternative in active:
        rejected_advantage, accepted_advantage = standardized_binary_advantages(alternative, 32)
        incorrect = 32 - correct
        blocked_advantage_sum += blocked * rejected_advantage
        alternative_advantage_sum += alternative * accepted_advantage
        incorrect_advantage_sum += incorrect * rejected_advantage
        blocked_count += blocked
        alternative_count += alternative
        incorrect_count += incorrect

    return {
        "analysis": "c3-frozen-rollout-reward-rejection-replay-v1",
        "status": "valid_counterfactual_replay_not_c5_result",
        "interpretation": (
            "Measures whether frozen C3 groups contain usable alternative support and the immediate "
            "advantages C5 would assign. It does not predict C5's on-policy distribution or final result."
        ),
        "source": {
            "run_dir": str(run_dir),
            "metrics_sha256": sha256(metrics_path),
            "train_sha256": sha256(train_path),
            "proof_log": str(proof_path),
            "proof_log_sha256": sha256(proof_path),
        },
        "registered_training_theorems": len(groups),
        "theorems_with_blocked_dominant_rollouts": len(affected),
        "theorems_with_blocked_and_alternative_correct": len(active),
        "theorems_all_correct_but_newly_trainable_under_rejection": len(newly_trainable),
        "theorems_with_only_blocked_correct_to_skip": len(all_blocked),
        "blocked_correct_rollouts_total": sum(group[1] for group in groups),
        "active_rejection_groups": {
            "blocked_correct_rollouts": blocked_count,
            "alternative_correct_rollouts": alternative_count,
            "incorrect_rollouts": incorrect_count,
            "mean_standardized_advantage": {
                "blocked_correct": blocked_advantage_sum / blocked_count,
                "alternative_correct": alternative_advantage_sum / alternative_count,
                "incorrect": incorrect_advantage_sum / incorrect_count,
            },
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-dir", type=Path, default=DEFAULT_RUN)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    output = args.output.resolve()
    if output.exists():
        parser.error(f"refusing to overwrite output: {output}")
    report = analyze(args.run_dir.resolve())
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
