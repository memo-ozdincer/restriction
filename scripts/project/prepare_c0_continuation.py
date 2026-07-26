#!/usr/bin/env python3
"""Prepare the uncompleted theorem rows of an interrupted sample-only C0."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from collections import Counter
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
MODEL = "deepseek-ai/DeepSeek-Prover-V1.5-SFT"
MODEL_REVISION = "e9a6e6fbb67620d4e9c4944bc51ff7c435af12da"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def git_output(*args: str) -> str:
    return subprocess.check_output(["git", *args], cwd=ROOT, text=True).strip()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("run_dir", type=Path, help="new continuation directory")
    parser.add_argument("--previous-run", required=True, type=Path)
    parser.add_argument("--proof-log", required=True, type=Path,
                        help="latest cumulative proof snapshot from --previous-run")
    parser.add_argument("--samples", type=int, default=32)
    args = parser.parse_args()
    run_dir = args.run_dir.resolve()
    previous_run = args.previous_run.resolve()
    proof_log = args.proof_log.resolve()
    if run_dir.exists():
        parser.error(f"refusing to reuse existing run directory: {run_dir}")
    if not proof_log.is_file():
        parser.error(f"proof log does not exist: {proof_log}")

    records = [json.loads(line) for line in proof_log.read_text(encoding="utf-8").splitlines()]
    completed_counts = Counter(record["theorem_name"] for record in records)
    invalid = {name: count for name, count in completed_counts.items() if count != args.samples}
    if invalid:
        parser.error(f"proof log does not contain exactly {args.samples} samples per completed theorem")

    previous_train = previous_run / "train.parquet"
    previous_valid = previous_run / "valid.parquet"
    if not previous_train.is_file() or not previous_valid.is_file():
        parser.error("previous run lacks immutable derived train/valid parquet files")
    train = pd.read_parquet(previous_train)
    if train["theorem_full_name"].nunique() != len(train):
        parser.error("previous train split has non-unique theorem_full_name values")
    completed = set(completed_counts)
    unknown = completed - set(train["theorem_full_name"])
    if unknown:
        parser.error("proof log contains theorem names absent from previous train split")
    remaining = train.loc[~train["theorem_full_name"].isin(completed)].copy()
    if remaining.empty:
        parser.error("no uncompleted theorem rows remain")

    run_dir.mkdir(parents=True)
    train_path, valid_path = run_dir / "train.parquet", run_dir / "valid.parquet"
    remaining.to_parquet(train_path, index=False)
    pd.read_parquet(previous_valid).to_parquet(valid_path, index=False)
    status = git_output("status", "--short") or "clean"
    metadata = [
        "# C0 Continuation Metadata", "", "Status: prepared; no result exists yet.", "",
        f"- Git commit: `{git_output('rev-parse', 'HEAD')}`", f"- Dirty status: `{status}`",
        f"- Base model and frozen reference: `{MODEL}`", f"- Model revision: `{MODEL_REVISION}`",
        f"- Previous interrupted run: `{previous_run}`",
        f"- Previous cumulative proof log: `{proof_log}` (`{sha256(proof_log)}`)",
        f"- Completed theorem rows retained from prior snapshot: {len(completed)}",
        f"- Remaining theorem rows in this run: {len(remaining)} (`{sha256(train_path)}`)",
        f"- Validation rows copied unchanged: {len(pd.read_parquet(valid_path))} (`{sha256(valid_path)}`)",
        "- Seed: 42", f"- Proposal budget: {args.samples} per theorem",
        "- DeepSeek verifier memory cap: 32 GB per worker",
        "- DeepSeek verifier result handoff: compact Boolean verdict patch",
        "- Hard blocking: disabled", "- Archive: none", "",
        "The final C0 archive must merge this run's final proof log with the listed prior cumulative proof log; theorem sets are disjoint.",
    ]
    (run_dir / "RUN_METADATA.md").write_text("\n".join(metadata) + "\n", encoding="utf-8")
    print(run_dir)


if __name__ == "__main__":
    main()
