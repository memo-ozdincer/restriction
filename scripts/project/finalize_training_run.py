#!/usr/bin/env python3
"""Finalize a completed C1/C3 training run from its durable artifacts."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from collections import Counter, defaultdict
from datetime import datetime, timezone
from math import comb
from pathlib import Path

import pandas as pd

from verl.lean.proof_modes import exact_proof_id, mode_id


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def latest_proof_log(run_dir: Path) -> Path:
    proofs = sorted((run_dir / "artifacts/proofs").glob("global_step_*.jsonl"))
    if not proofs:
        raise FileNotFoundError("no persisted proof snapshot exists")
    return max(proofs, key=lambda path: int(path.stem.rsplit("_", 1)[1]))


def latest_actor_checkpoint(run_dir: Path) -> Path:
    checkpoints = sorted((run_dir / "artifacts/actor").glob("global_step_*"))
    if not checkpoints:
        raise FileNotFoundError("no persisted actor checkpoint exists")
    return max(checkpoints, key=lambda path: int(path.name.rsplit("_", 1)[1]))


def last_int(log: str, key: str, default: int | None = None) -> int:
    values = re.findall(rf"'{re.escape(key)}': (\d+)", log)
    if values:
        return int(values[-1])
    if default is None:
        raise ValueError(f"completed log lacks {key}")
    return default


def sum_ints(log: str, key: str, default: int = 0) -> int:
    values = re.findall(rf"'{re.escape(key)}': (\d+)", log)
    return sum(map(int, values)) if values else default


def pass_at_n(successes: int, attempts: int, n: int) -> float | None:
    if attempts == 0:
        return None
    if attempts < n:
        return float(successes > 0)
    failures = attempts - successes
    return 1.0 if failures < n else 1.0 - comb(failures, n) / comb(attempts, n)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("run_dir", type=Path)
    parser.add_argument("--condition", required=True, choices=("c1_grpo_default", "c3_hardblock_restart"))
    parser.add_argument("--classification", default="engineering_smoke")
    args = parser.parse_args()

    run_dir = args.run_dir.resolve()
    metrics_path = run_dir / "metrics.json"
    if metrics_path.exists():
        parser.error(f"refusing to overwrite existing metrics: {metrics_path}")
    proof_log = latest_proof_log(run_dir)
    run_log_path = run_dir / "run.log"
    config_path = run_dir / "hydra/.hydra/config.yaml"
    hardware_path = run_dir / "hardware.txt"
    checkpoint = latest_actor_checkpoint(run_dir)
    required = (run_log_path, config_path, hardware_path, checkpoint)
    if any(not path.exists() for path in required):
        parser.error("run lacks a log, resolved config, hardware record, or step-1 checkpoint")

    log = run_log_path.read_text(encoding="utf-8", errors="replace")
    if "[TRAINING] Training finished" not in log or 'Exception: Stop' not in log:
        parser.error("run did not reach the upstream post-completion sentinel")
    physical_proofs = [json.loads(line) for line in proof_log.read_text(encoding="utf-8").splitlines()]
    source = pd.read_parquet(run_dir / "train.parquet")
    expected_theorems = [str(name) for name in source["theorem_full_name"]]
    expected_set = set(expected_theorems)
    physical_by_theorem: dict[str, list[dict]] = defaultdict(list)
    for proof in physical_proofs:
        physical_by_theorem[str(proof["theorem_name"])].append(proof)
    unexpected = set(physical_by_theorem) - expected_set
    missing = expected_set - set(physical_by_theorem)
    if unexpected or missing:
        parser.error(f"proof snapshot theorem mismatch: missing={len(missing)}, unexpected={len(unexpected)}")
    short = {name: len(items) for name, items in physical_by_theorem.items() if len(items) < 32}
    if short:
        parser.error(f"proof snapshot has {len(short)} theorems below the registered 32 proposals")
    by_theorem = {name: physical_by_theorem[name][:32] for name in expected_theorems}
    proofs = [proof for name in expected_theorems for proof in by_theorem[name]]

    correct = [proof for proof in proofs if proof.get("correct", False)]
    blocked = [proof for proof in proofs if proof.get("blocked_correct", False)]
    verifier_failures = [proof for proof in proofs if proof.get("verifier_error")]
    correct_modes = {(proof["theorem_name"], mode_id(proof["proof"])) for proof in correct}
    exact_proofs = {(proof["theorem_name"], exact_proof_id(proof["proof"])) for proof in correct}
    pass_metrics = {}
    for n in (1, 4, 8, 16, 32):
        values = [
            pass_at_n(sum(item.get("correct", False) for item in by_theorem[name]), len(by_theorem[name]), n)
            for name in expected_theorems
        ]
        pass_metrics[f"pass_at_{n}"] = sum(value for value in values if value is not None) / len(expected_theorems)

    hardware_lines = hardware_path.read_text(encoding="utf-8").splitlines()
    try:
        start = datetime.fromisoformat(hardware_lines[0])
        wall_clock_source = "hardware_record_iso_timestamp_to_run_log_mtime"
    except ValueError:
        start = datetime.fromtimestamp(hardware_path.stat().st_mtime, timezone.utc)
        wall_clock_source = "hardware_record_mtime_to_run_log_mtime"
    end = datetime.fromtimestamp(run_log_path.stat().st_mtime, timezone.utc)
    archive_path = run_dir / "block_archive.json"
    trained = sum_ints(log, "num_trained", default=sum_ints(log, "num_accepted"))
    metrics = {
        "condition": args.condition,
        "classification": args.classification,
        "actor_checkpoint": str(checkpoint),
        "completed_at_utc": datetime.now(timezone.utc).isoformat(),
        "completion_marker": "upstream_post_completion_stop_sentinel",
        "exit_code": int((run_dir / "exit_code.txt").read_text().strip()),
        "wall_clock_seconds": (end - start.astimezone(timezone.utc)).total_seconds(),
        "wall_clock_source": wall_clock_source,
        "proof_log": str(proof_log),
        "proof_log_sha256": sha256(proof_log),
        "resolved_config": str(config_path),
        "resolved_config_sha256": sha256(config_path),
        "hardware_record_sha256": sha256(hardware_path),
        "archive_sha256": sha256(archive_path) if archive_path.exists() else None,
        "proposals": len(proofs),
        "physical_proposals": len(physical_proofs),
        "excluded_padding_proposals": len(physical_proofs) - len(proofs),
        "expected_registered_proposals": len(expected_theorems) * 32,
        "lean_verifier_attempts": len(proofs),
        "verifier_infrastructure_failures": len(verifier_failures),
        "correct": len(correct),
        "lean_rejected": len(proofs) - len(correct) - len(verifier_failures),
        "blocked_correct_zero_advantage": len(blocked),
        "update_batch_samples": trained,
        "physical_blocked_correct_zero_advantage": sum(
            bool(proof.get("blocked_correct", False)) for proof in physical_proofs
        ),
        "skipped_all_blocked_prompts": sum_ints(log, "num_skipped_all_blocked_prompts"),
        "correct_mode_coverage": len(correct_modes),
        "exact_proof_coverage": len(exact_proofs),
        "theorems_with_rollouts": len(by_theorem),
        "expected_training_theorems": len(expected_theorems),
        "failure_classes": dict(sorted(Counter(proof.get("failure_class") or "none" for proof in proofs).items())),
        "config_hashes": sorted({proof.get("config_hash") for proof in proofs if proof.get("config_hash")}),
        "environment_hashes": sorted({proof.get("environment_hash") for proof in proofs if proof.get("environment_hash")}),
        "pass_at_n": pass_metrics,
    }
    metrics_path.write_text(json.dumps(metrics, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    metadata_path = run_dir / "RUN_METADATA.md"
    metadata = metadata_path.read_text(encoding="utf-8").replace(
        "Status: prepared; no result exists yet.",
        "Status: complete; the nonzero process exit is the upstream post-completion sentinel.",
        1,
    )
    metadata += (
        "\n## Completion\n\n"
        f"- Metrics: `metrics.json` (proof log SHA-256 `{metrics['proof_log_sha256']}`)\n"
        f"- Resolved config: `hydra/.hydra/config.yaml` (`{metrics['resolved_config_sha256']}`)\n"
        f"- Wall clock: {metrics['wall_clock_seconds']:.3f} seconds\n"
        f"- Proposals/verifier attempts: {metrics['proposals']}; correct: {metrics['correct']}; "
        f"blocked correct: {metrics['blocked_correct_zero_advantage']}; update batch: {metrics['update_batch_samples']}\n"
        f"- All-blocked prompts skipped: {metrics['skipped_all_blocked_prompts']}\n"
    )
    metadata_path.write_text(metadata, encoding="utf-8")
    print(json.dumps(metrics, sort_keys=True))


if __name__ == "__main__":
    main()
