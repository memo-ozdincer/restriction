#!/usr/bin/env python3
"""Prepare the shared registered-valid plus miniF2F Lean evaluation set."""

from __future__ import annotations

import argparse
import hashlib
import subprocess
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[2]
SEEN_SHA = "56799bc5a19c4ccc0c671dd8631a16c0956786ae63ba5d4e30e9f30b7bbcc9eb"
MINIF2F_SHA = "c59790c596b02ff7213f2a810bb90dc37848a20ab8e830084533f88e3c8e40c6"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("run_dir", type=Path)
    parser.add_argument("--condition", required=True, choices=("c0_base", "c1_grpo_default", "c3_hardblock_restart"))
    parser.add_argument("--model-path", type=Path, required=True)
    parser.add_argument("--model-source-run", type=Path)
    parser.add_argument("--allow-pending-model", action="store_true")
    parser.add_argument("--num-samples", type=int, choices=(32, 128), default=32)
    args = parser.parse_args()
    run_dir = args.run_dir.resolve()
    if run_dir.exists(): parser.error(f"refusing existing run directory: {run_dir}")
    model_path = args.model_path.resolve()
    if not model_path.is_dir() and not args.allow_pending_model:
        parser.error(f"model path does not exist: {model_path}")
    seen_path = ROOT / "data/mff-lwb-10k-seen.parquet"
    mini_path = ROOT / "data/minif2f_test.parquet"
    if sha256(seen_path) != SEEN_SHA or sha256(mini_path) != MINIF2F_SHA:
        parser.error("registered evaluation source checksum mismatch")
    seen = pd.read_parquet(seen_path)
    valid = seen.loc[seen["split"] == "valid"].copy()
    valid["evaluation_dataset"] = "registered_valid"
    mini = pd.read_parquet(mini_path).copy()
    mini["evaluation_dataset"] = "minif2f_test"
    frame = pd.concat([valid, mini], ignore_index=True)
    if len(valid) != 223 or len(mini) != 244 or frame["theorem_full_name"].duplicated().any():
        parser.error("unexpected evaluation composition or overlapping theorem identity")
    run_dir.mkdir(parents=True)
    eval_path = run_dir / "train.parquet"
    frame.to_parquet(eval_path, index=False)
    (run_dir / "valid.parquet").write_bytes(eval_path.read_bytes())
    commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    status = subprocess.check_output(["git", "status", "--short"], cwd=ROOT, text=True).strip() or "clean"
    metadata = [
        f"# {args.condition} Registered Lean Evaluation", "", "Status: prepared; no result exists yet.", "",
        f"- Git commit: `{commit}`", f"- Dirty status: `{status}`",
        f"- Actor path: `{model_path}`", "- Model revision/base lineage: `e9a6e6fbb67620d4e9c4944bc51ff7c435af12da`",
        f"- Actor availability at preparation: `{'present' if model_path.is_dir() else 'pending dependency'}`",
        f"- Model source run: `{args.model_source_run.resolve()}`" if args.model_source_run else "- Model source run: pristine base",
        f"- Registered validation source: 223 rows (`{SEEN_SHA}`)",
        f"- miniF2F-test source: 244 rows (`{MINIF2F_SHA}`)",
        f"- Combined evaluation parquet: 467 rows (`{sha256(eval_path)}`)",
        "- Seed: 42",
        f"- Proposal budget: {args.num_samples} per theorem; "
        f"{len(frame) * args.num_samples:,} registered proposals",
        "- Training/update: disabled", "- Hard blocking during evaluation: disabled",
        "- Sampling: temperature 1.0, top-p 1.0, top-k disabled, response length 512", "",
    ]
    (run_dir / "RUN_METADATA.md").write_text("\n".join(metadata), encoding="utf-8")
    (run_dir / "model_path.txt").write_text(str(model_path) + "\n", encoding="utf-8")
    print(run_dir)


if __name__ == "__main__":
    main()
