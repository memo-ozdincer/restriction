#!/usr/bin/env python3
"""Validate a finalized C5 reward-rejection training run."""

from __future__ import annotations

import argparse
import json
import os
import re
import tempfile
from pathlib import Path


ARCHIVE_SHA256 = "fcffb4a3dc9baf837d4780ec30855308ebc7f0c5086d607162889938b5e426d3"


def fail(message: str) -> None:
    raise ValueError(message)


def training_accounting(log: str) -> dict:
    """Reconstruct retained, optimized, and residual samples from log events."""
    step_sizes: list[int] = []
    update_sizes: list[int] = []
    summaries: list[dict] = []
    pending = 0

    for line in log.splitlines():
        step_match = re.search(r"\[TRAINING\] Step train batch size: (\d+)", line)
        if step_match:
            size = int(step_match.group(1))
            step_sizes.append(size)
            pending += size

        update_match = re.search(r"\[TRAINING\] Update train batch size: (\d+)", line)
        if update_match:
            size = int(update_match.group(1))
            if size != pending:
                fail(f"optimizer update size {size} does not match buffered size {pending}")
            update_sizes.append(size)
            pending = 0

        summary_match = re.search(r"\[HARD_BLOCKING\] (\{.*\})", line)
        if summary_match:
            summaries.append(json.loads(summary_match.group(1)))

    if len(summaries) != len(update_sizes):
        fail(
            f"found {len(summaries)} hard-blocking summaries for "
            f"{len(update_sizes)} optimizer updates"
        )

    for index, (summary, update_size) in enumerate(zip(summaries, update_sizes), 1):
        categorized = sum(
            int(summary[key])
            for key in (
                "blocked_correct_count",
                "alternative_correct_count",
                "incorrect_count",
            )
        )
        if categorized != update_size:
            fail(
                f"update {index} categorizes {categorized} samples but optimized "
                f"{update_size}"
            )

    return {
        "step_sizes": step_sizes,
        "update_sizes": update_sizes,
        "summaries": summaries,
        "retained_samples": sum(step_sizes),
        "optimized_samples": sum(update_sizes),
        "residual_buffer_samples": pending,
    }


def weighted_mean(summaries: list[dict], category: str) -> float:
    count_key = f"{category}_count"
    mean_key = f"{category}_advantage_mean"
    weighted = [
        (int(item[count_key]), item[mean_key])
        for item in summaries
        if item[count_key] and item[mean_key] is not None
    ]
    if not weighted:
        fail(f"no nonempty {category} telemetry exists")
    return sum(count * mean for count, mean in weighted) / sum(
        count for count, _ in weighted
    )


def validate(run_dir: Path, expected_steps: int, max_residual: int) -> dict:
    metrics_path = run_dir / "metrics.json"
    log_path = run_dir / "run.log"
    metrics = json.loads(metrics_path.read_text(encoding="utf-8"))
    log = log_path.read_text(encoding="utf-8", errors="replace")

    expected = {
        "condition": "c5_reward_reject_restart",
        "classification": "exploratory_full_seed42_h100",
        "proposals": 308_960,
        "physical_proposals": 308_992,
        "excluded_padding_proposals": 32,
        "expected_registered_proposals": 308_960,
        "theorems_with_rollouts": 9_655,
        "expected_training_theorems": 9_655,
        "archive_sha256": ARCHIVE_SHA256,
    }
    for key, value in expected.items():
        if metrics.get(key) != value:
            fail(f"{key}={metrics.get(key)!r}, expected {value!r}")

    if metrics["blocked_correct"] <= 0:
        fail("no blocked-correct proposal was observed")
    if metrics["blocked_correct_zero_advantage"] != 0:
        fail("C5 unexpectedly retained zero-advantage blocked proofs")
    if metrics["blocked_correct_reward_rejected"] != metrics["blocked_correct"]:
        fail("not every registered blocked-correct proof was reward-rejected")
    if (
        metrics["physical_blocked_correct_reward_rejected"]
        != metrics["physical_blocked_correct"]
    ):
        fail("not every physical blocked-correct proof was reward-rejected")
    if metrics["physical_blocked_correct_zero_advantage"] != 0:
        fail("physical proof log contains zero-advantage blocked proofs")

    checkpoint = Path(metrics["actor_checkpoint"])
    if not checkpoint.is_dir() or checkpoint.name != f"global_step_{expected_steps}":
        fail(f"missing final actor checkpoint global_step_{expected_steps}")

    accounting = training_accounting(log)
    if len(accounting["step_sizes"]) != expected_steps:
        fail(
            f"found {len(accounting['step_sizes'])} retained-sample steps, "
            f"expected {expected_steps}"
        )
    if not accounting["update_sizes"]:
        fail("no optimizer update was recorded")
    if accounting["retained_samples"] != metrics["update_batch_samples"]:
        fail(
            f"retained log samples {accounting['retained_samples']} do not match "
            f"finalized count {metrics['update_batch_samples']}"
        )
    if accounting["residual_buffer_samples"] > max_residual:
        fail(
            f"final residual buffer {accounting['residual_buffer_samples']} exceeds "
            f"registered sub-threshold maximum {max_residual}"
        )

    summaries = accounting["summaries"]
    if any(item["intervention"] != "reject_reward" for item in summaries):
        fail("telemetry contains a non-C5 intervention")
    for category in ("blocked_correct", "alternative_correct", "incorrect"):
        if sum(int(item[f"{category}_count"]) for item in summaries) <= 0:
            fail(f"no optimized {category} sample was observed")

    advantages = {
        category: weighted_mean(summaries, category)
        for category in ("blocked_correct", "alternative_correct", "incorrect")
    }
    if advantages["blocked_correct"] >= 0:
        fail("blocked-correct mean advantage is not negative")
    if advantages["alternative_correct"] <= 0:
        fail("alternative-correct mean advantage is not positive")
    if advantages["incorrect"] >= 0:
        fail("incorrect mean advantage is not negative")

    return {
        "validation": "c5-reward-rejection-finalized-v2",
        "run_dir": str(run_dir.resolve()),
        "correct": metrics["correct"],
        "correct_mode_coverage": metrics["correct_mode_coverage"],
        "blocked_correct_reward_rejected": metrics[
            "blocked_correct_reward_rejected"
        ],
        "dataloader_steps": len(accounting["step_sizes"]),
        "optimizer_updates": len(accounting["update_sizes"]),
        "retained_samples": accounting["retained_samples"],
        "optimized_samples": accounting["optimized_samples"],
        "residual_buffer_samples": accounting["residual_buffer_samples"],
        "mean_advantage": advantages,
    }


def write_new_json(path: Path, payload: dict) -> None:
    if path.exists():
        fail(f"refusing to overwrite validation output: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as stream:
            json.dump(payload, stream, indent=2, sort_keys=True)
            stream.write("\n")
        os.replace(temporary, path)
    except BaseException:
        Path(temporary).unlink(missing_ok=True)
        raise


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("run_dir", type=Path)
    parser.add_argument("--expected-steps", type=int, default=604)
    parser.add_argument("--max-residual", type=int, default=255)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    try:
        result = validate(args.run_dir.resolve(), args.expected_steps, args.max_residual)
        if args.output:
            write_new_json(args.output.resolve(), result)
        print(json.dumps(result, sort_keys=True))
    except (FileNotFoundError, KeyError, TypeError, ValueError, json.JSONDecodeError) as error:
        parser.error(str(error))


if __name__ == "__main__":
    main()
