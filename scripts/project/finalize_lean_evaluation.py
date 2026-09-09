#!/usr/bin/env python3
"""Finalize a complete registered Lean evaluation and its mode manifest."""

from __future__ import annotations

import argparse
import hashlib
import json
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


def pass_at_n(successes: int, attempts: int, n: int) -> float:
    failures = attempts - successes
    return 1.0 if failures < n else 1.0 - comb(failures, n) / comb(attempts, n)


def latest_proof_log(run_dir: Path) -> Path:
    paths = sorted((run_dir / "artifacts/proofs").glob("global_step_*.jsonl"))
    if not paths:
        raise FileNotFoundError("no persisted proof snapshot exists")
    return max(paths, key=lambda path: int(path.stem.rsplit("_", 1)[1]))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("run_dir", type=Path)
    parser.add_argument(
        "--condition",
        required=True,
        choices=(
            "c0_base",
            "c1_grpo_default",
            "c2_unlikeliness_2",
            "c3_hardblock_restart",
            "c3_matched_control",
        ),
    )
    parser.add_argument("--num-samples", type=int, choices=(32, 128), default=32)
    args = parser.parse_args()
    run_dir = args.run_dir.resolve()
    metrics_path = run_dir / "metrics.json"
    manifest_path = run_dir / "mode_manifest.json"
    if metrics_path.exists() or manifest_path.exists():
        parser.error("refusing to overwrite finalized evaluation")
    proof_log = latest_proof_log(run_dir)
    log_path = run_dir / "run.log"
    config_path = run_dir / "hydra/.hydra/config.yaml"
    hardware_path = run_dir / "hardware.txt"
    for path in (log_path, config_path, hardware_path, run_dir / "exit_code.txt"):
        if not path.is_file(): parser.error(f"missing evaluation artifact: {path}")
    log = log_path.read_text(encoding="utf-8", errors="replace")
    if "[TRAINING] Training finished" not in log or "Exception: Stop" not in log:
        parser.error("evaluation did not reach the upstream completion sentinel")

    frame = pd.read_parquet(run_dir / "train.parquet")
    expected = [str(value) for value in frame["theorem_full_name"]]
    dataset_for = dict(zip(expected, frame["evaluation_dataset"], strict=True))
    physical = [json.loads(line) for line in proof_log.read_text(encoding="utf-8").splitlines()]
    grouped: dict[str, list[dict]] = defaultdict(list)
    for proof in physical: grouped[str(proof["theorem_name"])].append(proof)
    if set(grouped) != set(expected):
        parser.error("evaluation proof snapshot theorem identities do not match the frozen parquet")
    if any(len(grouped[name]) < args.num_samples for name in expected):
        parser.error(
            f"evaluation proof snapshot has fewer than {args.num_samples} proposals for a theorem"
        )
    selected_by_theorem = {name: grouped[name][:args.num_samples] for name in expected}
    selected = [proof for name in expected for proof in selected_by_theorem[name]]

    modes = {
        name: sorted({mode_id(item["proof"]) for item in items if item.get("correct", False)})
        for name, items in selected_by_theorem.items()
    }
    exact = {
        name: sorted({exact_proof_id(item["proof"]) for item in items if item.get("correct", False)})
        for name, items in selected_by_theorem.items()
    }
    manifest = {
        "condition": args.condition,
        "num_samples_per_theorem": args.num_samples,
        "evaluation_parquet_sha256": sha256(run_dir / "train.parquet"),
        "correct_modes_by_theorem": modes,
        "exact_correct_proofs_by_theorem": exact,
    }
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    datasets = {}
    for dataset in ("registered_valid", "minif2f_test"):
        names = [name for name in expected if dataset_for[name] == dataset]
        proofs = [item for name in names for item in selected_by_theorem[name]]
        successes = {name: sum(item.get("correct", False) for item in selected_by_theorem[name]) for name in names}
        datasets[dataset] = {
            "theorems": len(names),
            "proposals": len(proofs),
            "correct": sum(successes.values()),
            f"solved_at_{args.num_samples}": sum(value > 0 for value in successes.values()),
            "pass_at_n": {
                f"pass_at_{n}": sum(
                    pass_at_n(successes[name], args.num_samples, n) for name in names
                ) / len(names)
                for n in (1, 4, 8, 16, 32, 64, 128)
                if n <= args.num_samples
            },
            "correct_mode_coverage": sum(len(modes[name]) for name in names),
            "mean_correct_modes_per_theorem": sum(len(modes[name]) for name in names) / len(names),
            "exact_correct_proof_coverage": sum(len(exact[name]) for name in names),
        }
    verifier_failures = [item for item in selected if item.get("verifier_error")]
    metrics = {
        "condition": args.condition,
        "classification": f"registered_evaluation_{args.num_samples}",
        "completed_at_utc": datetime.now(timezone.utc).isoformat(),
        "completion_marker": "upstream_post_completion_stop_sentinel",
        "exit_code": int((run_dir / "exit_code.txt").read_text().strip()),
        "evaluation_parquet_sha256": sha256(run_dir / "train.parquet"),
        "proof_log": str(proof_log), "proof_log_sha256": sha256(proof_log),
        "resolved_config_sha256": sha256(config_path), "hardware_record_sha256": sha256(hardware_path),
        "mode_manifest": str(manifest_path), "mode_manifest_sha256": sha256(manifest_path),
        "registered_proposals": len(selected), "physical_proposals": len(physical),
        "excluded_padding_proposals": len(physical) - len(selected),
        "correct": sum(item.get("correct", False) for item in selected),
        "verifier_infrastructure_failures": len(verifier_failures),
        "failure_classes": dict(sorted(Counter(item.get("failure_class") or "none" for item in selected).items())),
        "datasets": datasets,
    }
    metrics_path.write_text(json.dumps(metrics, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    metadata_path = run_dir / "RUN_METADATA.md"
    metadata = metadata_path.read_text(encoding="utf-8").replace(
        "Status: prepared; no result exists yet.",
        "Status: complete; the nonzero process exit is the upstream post-completion sentinel.", 1,
    )
    metadata += (
        "\n## Completion\n\n"
        f"- Metrics: `metrics.json` (`{sha256(metrics_path)}`)\n"
        f"- Mode manifest: `mode_manifest.json` (`{metrics['mode_manifest_sha256']}`)\n"
        f"- Registered proposals: {len(selected)}; physical proposals: {len(physical)}; "
        f"excluded padding: {metrics['excluded_padding_proposals']}; correct: {metrics['correct']}\n"
    )
    metadata_path.write_text(metadata, encoding="utf-8")
    print(json.dumps(metrics, sort_keys=True))


if __name__ == "__main__":
    main()
