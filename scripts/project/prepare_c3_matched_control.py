#!/usr/bin/env python3
"""Prepare the full blocking-disabled control matched to C3."""

from __future__ import annotations

import argparse
import hashlib
import os
import subprocess
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[2]
MODEL = "deepseek-ai/DeepSeek-Prover-V1.5-SFT"
MODEL_PATH = os.environ.get(
    "RESTRICTION_BASE_MODEL_PATH", "/scratch/memoozd/models/DeepSeek-Prover-V1.5-SFT"
)
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
    parser.add_argument("run_dir", type=Path, help="new run directory; it must not exist")
    parser.add_argument("--source", type=Path, default=ROOT / "data/mff-lwb-10k-seen.parquet")
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    run_dir = args.run_dir.resolve()
    if run_dir.exists():
        parser.error(f"refusing to reuse existing run directory: {run_dir}")
    if not args.source.is_file():
        parser.error(f"source parquet does not exist: {args.source}")
    frame = pd.read_parquet(args.source)
    train = frame.loc[frame["split"] == "train"].copy()
    valid = frame.loc[frame["split"] == "valid"].copy()
    if len(train) != 9655 or len(valid) != 223:
        parser.error(f"unexpected registered split sizes: train={len(train)}, valid={len(valid)}")

    run_dir.mkdir(parents=True)
    train_path = run_dir / "train.parquet"
    valid_path = run_dir / "valid.parquet"
    train.to_parquet(train_path, index=False)
    valid.to_parquet(valid_path, index=False)
    status = git_output("status", "--short") or "clean"
    lines = [
        "# C3-Matched No-Blocking Full Control", "",
        "Status: prepared; no result exists yet.", "",
        f"- Git commit: `{git_output('rev-parse', 'HEAD')}`",
        f"- Dirty status: `{status}`",
        f"- Pristine actor and frozen reference: `{MODEL}`",
        f"- Runtime model path: `{MODEL_PATH}`",
        f"- Model revision: `{MODEL_REVISION}`",
        f"- Source data: `{args.source.resolve()}` (`{sha256(args.source)}`)",
        f"- Derived training data: {len(train)} rows (`{sha256(train_path)}`)",
        f"- Derived validation data: {len(valid)} rows (`{sha256(valid_path)}`)",
        "- Selection: complete registered train and validation splits in source order",
        f"- Seed: {args.seed}",
        "- Proposal budget: 32 per theorem; 308,960 registered training proposals",
        "- Expected dataloader steps: 604",
        "- PPO epochs: 2", "- KL loss coefficient: 0.10", "- Rank penalty: 0.0",
        "- Hard blocking: disabled; no archive is loaded or consulted",
        "- Matched condition: C3 HardBlock-Restart at seed 42",
        "- Only intended C3 launch difference: `lean.hard_blocking.enabled=False`",
        "- Resume: disabled; optimizer and rollout buffer start fresh",
        "- Classification: registered full C3-matched no-blocking control seed-42 run",
        "- Final actor checkpoint and proof snapshot frequency: step 604", "",
        "Append resolved config, environment, hardware, wall-clock, proposal,",
        "verified, correct, and trained counts after completion.",
    ]
    (run_dir / "RUN_METADATA.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(run_dir)


if __name__ == "__main__":
    main()
