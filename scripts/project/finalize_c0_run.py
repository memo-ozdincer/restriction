#!/usr/bin/env python3
"""Create auditable C0 metrics from a completed persisted proof snapshot."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

from verl.lean.proof_modes import exact_proof_id, mode_id


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def pass_at_n(successes: int, attempts: int, n: int) -> float | None:
    if attempts == 0:
        return None
    if attempts < n:
        return float(successes > 0)
    from math import comb
    failures = attempts - successes
    return 1.0 if failures < n else 1.0 - comb(failures, n) / comb(attempts, n)


def latest_proof_log(run_dir: Path) -> Path:
    proofs = sorted((run_dir / "artifacts" / "proofs").glob("global_step_*.jsonl"))
    if not proofs:
        raise FileNotFoundError("no persisted proof snapshot exists")
    return max(proofs, key=lambda path: int(path.stem.rsplit("_", 1)[1]))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("run_dir", type=Path)
    parser.add_argument("--proof-log", type=Path, help="defaults to latest saved snapshot")
    args = parser.parse_args()
    run_dir = args.run_dir.resolve()
    proof_log = args.proof_log or latest_proof_log(run_dir)
    if not proof_log.is_file():
        parser.error(f"proof log does not exist: {proof_log}")

    proofs = [json.loads(line) for line in proof_log.read_text(encoding="utf-8").splitlines()]
    by_theorem: dict[str, list[dict]] = defaultdict(list)
    for proof in proofs:
        by_theorem[proof["theorem_name"]].append(proof)
    correct = [proof for proof in proofs if proof.get("correct", False)]
    correct_modes = {(proof["theorem_name"], mode_id(proof["proof"])) for proof in correct}
    exact_proofs = {(proof["theorem_name"], exact_proof_id(proof["proof"])) for proof in correct}
    source = pd.read_parquet(run_dir / "train.parquet")
    expected_theorems = set(source["theorem_full_name"])
    pass_metrics = {}
    for n in (1, 4, 8, 16, 32):
        values = [pass_at_n(sum(p.get("correct", False) for p in by_theorem[name]), len(by_theorem[name]), n)
                  for name in expected_theorems]
        pass_metrics[f"pass_at_{n}"] = sum(value for value in values if value is not None) / len(expected_theorems)

    error_counts = [int(value) for value in re.findall(r"'num_errors': ([0-9]+)", (run_dir / "run.log").read_text(encoding="utf-8"))]
    metrics = {
        "condition": "c0_base",
        "completed_at_utc": datetime.now(timezone.utc).isoformat(),
        "proof_log": str(proof_log),
        "proof_log_sha256": sha256(proof_log),
        "proposals": len(proofs),
        "verified": len(proofs) - sum(error_counts),
        "verifier_errors": sum(error_counts),
        "correct": len(correct),
        "blocked": 0,
        "trained_samples": 0,
        "correct_mode_coverage": len(correct_modes),
        "exact_proof_coverage": len(exact_proofs),
        "theorems_with_rollouts": len(by_theorem),
        "expected_training_theorems": len(expected_theorems),
        "pass_at_n": pass_metrics,
    }
    (run_dir / "metrics.json").write_text(json.dumps(metrics, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    with (run_dir / "RUN_METADATA.md").open("a", encoding="utf-8") as metadata:
        metadata.write("\n## Completion\n\n")
        metadata.write(f"- Metrics: `metrics.json` (proof log SHA-256 `{metrics['proof_log_sha256']}`)\n")
        metadata.write(f"- Proposals: {metrics['proposals']}; verified: {metrics['verified']}; correct: {metrics['correct']}; blocked: 0; trained: 0\n")
    print(json.dumps(metrics, sort_keys=True))


if __name__ == "__main__":
    main()
