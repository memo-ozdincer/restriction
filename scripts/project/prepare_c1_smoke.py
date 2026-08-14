#!/usr/bin/env python3
"""Create a fresh, immutable one-update C1 GRPO-Default smoke run."""

from __future__ import annotations

import argparse
import hashlib
import subprocess
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[2]
MODEL = "deepseek-ai/DeepSeek-Prover-V1.5-SFT"
MODEL_REVISION = "e9a6e6fbb67620d4e9c4944bc51ff7c435af12da"
TRAIN_ROWS = 16
VALID_ROWS = 16


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
    parser.add_argument(
        "--source", type=Path, default=ROOT / "data/mff-lwb-10k-seen.parquet"
    )
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument(
        "--verifier-root", type=Path,
        help="record an explicitly staged DeepSeek verifier workspace",
    )
    args = parser.parse_args()

    run_dir = args.run_dir.resolve()
    if run_dir.exists():
        parser.error(f"refusing to reuse existing run directory: {run_dir}")
    if not args.source.is_file():
        parser.error(f"source parquet does not exist: {args.source}")

    frame = pd.read_parquet(args.source)
    if "split" not in frame.columns:
        parser.error("registered source has no split column")
    registered_train = frame.loc[frame["split"] == "train"]
    registered_valid = frame.loc[frame["split"] == "valid"]
    if len(registered_train) != 9655 or len(registered_valid) != 223:
        parser.error(
            "unexpected registered split sizes: "
            f"train={len(registered_train)}, valid={len(registered_valid)}"
        )

    train = registered_train.iloc[:TRAIN_ROWS].copy()
    valid = registered_valid.iloc[:VALID_ROWS].copy()
    run_dir.mkdir(parents=True)
    train_path = run_dir / "train.parquet"
    valid_path = run_dir / "valid.parquet"
    train.to_parquet(train_path, index=False)
    valid.to_parquet(valid_path, index=False)

    status = git_output("status", "--short") or "clean"
    lines = [
        "# C1 GRPO-Default Smoke Metadata",
        "",
        "Status: prepared; no result exists yet.",
        "",
        f"- Git commit: `{git_output('rev-parse', 'HEAD')}`",
        f"- Dirty status: `{status}`",
        f"- Base actor and frozen reference: `{MODEL}`",
        f"- Model revision: `{MODEL_REVISION}`",
        f"- Source data: `{args.source}` (`{sha256(args.source)}`)",
        f"- Derived training smoke data: {len(train)} rows (`{sha256(train_path)}`)",
        f"- Derived validation smoke data: {len(valid)} rows (`{sha256(valid_path)}`)",
        "- Selection: first 16 rows of each registered split in source order",
        f"- Seed: {args.seed}",
        "- Proposal budget: 32 per theorem; 512 total training proposals",
        "- Expected optimizer updates: 1",
        "- PPO epochs: 1",
        "- KL loss coefficient: 0.02",
        "- Rank penalty: 0.0",
        "- Hard blocking: disabled",
        "- Resume: disabled; optimizer and rollout buffer start fresh",
        "- Classification: engineering smoke, not a scientific C1 result",
    ]
    if args.verifier_root:
        lines.append(f"- DeepSeek verifier workspace: `{args.verifier_root.resolve()}`")
    lines.extend([
        "",
        "Append resolved config, environment, hardware, wall-clock, proposal, ",
        "verified, correct, blocked, and trained counts after completion.",
    ])
    (run_dir / "RUN_METADATA.md").write_text(
        "\n".join(lines) + "\n", encoding="utf-8"
    )
    print(run_dir)


if __name__ == "__main__":
    main()
