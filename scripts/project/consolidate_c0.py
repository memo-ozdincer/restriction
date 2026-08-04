#!/usr/bin/env python3
"""Validate disjoint C0 snapshots and freeze their aggregate metrics/archive."""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter, defaultdict
from datetime import datetime, timezone
from math import comb
from pathlib import Path

import pandas as pd

from verl.lean.mode_archive import ModeArchive
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


def percentile(values: list[int], fraction: float) -> int | None:
    if not values:
        return None
    ordered = sorted(values)
    return ordered[min(len(ordered) - 1, int(fraction * len(ordered)))]


def distribution(values: list[int]) -> dict[str, float | int | None]:
    return {
        "mean": sum(values) / len(values) if values else None,
        "median": percentile(values, 0.5),
        "p90": percentile(values, 0.9),
        "max": max(values) if values else None,
    }


def load_counts(path: Path) -> tuple[Counter[str], int, int]:
    counts: Counter[str] = Counter()
    records = 0
    correct = 0
    with path.open(encoding="utf-8") as stream:
        for line_number, line in enumerate(stream, start=1):
            try:
                record = json.loads(line)
                theorem = str(record["theorem_name"])
                proof = record["proof"]
                verdict = record["correct"]
            except (json.JSONDecodeError, KeyError) as error:
                raise ValueError(f"{path}:{line_number}: invalid proof record: {error}") from error
            if not isinstance(proof, str) or not isinstance(verdict, bool):
                raise ValueError(f"{path}:{line_number}: proof/correct has invalid type")
            counts[theorem] += 1
            records += 1
            correct += int(verdict)
    return counts, records, correct


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--proofs", required=True, action="append", type=Path)
    parser.add_argument("--dataset", required=True, type=Path)
    parser.add_argument("--dataset-sha256", required=True)
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--model-revision", required=True)
    parser.add_argument("--seed", required=True, type=int)
    parser.add_argument("--samples-per-theorem", type=int, default=32)
    parser.add_argument("--expected-padding-proposals", type=int, default=0)
    args = parser.parse_args()

    proof_paths = [path.resolve() for path in args.proofs]
    dataset = args.dataset.resolve()
    output_dir = args.output_dir.resolve()
    if output_dir.exists():
        parser.error(f"refusing to overwrite output directory: {output_dir}")
    if not dataset.is_file() or sha256(dataset) != args.dataset_sha256:
        parser.error("dataset is missing or its SHA-256 does not match")
    if len(set(proof_paths)) != len(proof_paths):
        parser.error("the same proof snapshot was provided more than once")
    for path in proof_paths:
        if not path.is_file():
            parser.error(f"proof snapshot does not exist: {path}")

    frame = pd.read_parquet(dataset)
    if "split" not in frame or "theorem_full_name" not in frame:
        parser.error("dataset must contain split and theorem_full_name columns")
    train = frame.loc[frame["split"] == "train", "theorem_full_name"].astype(str)
    expected = set(train)
    if len(expected) != len(train):
        parser.error("training split theorem_full_name values are not unique")

    manifests = []
    seen_theorems: set[str] = set()
    raw_proposals = 0
    raw_correct = 0
    padding_by_theorem: dict[str, int] = {}
    counts_by_path: list[Counter[str]] = []
    for path in proof_paths:
        counts, records, correct = load_counts(path)
        overlap = seen_theorems.intersection(counts)
        if overlap:
            parser.error(f"proof snapshots are not theorem-disjoint; overlap includes {sorted(overlap)[:3]}")
        unknown = set(counts) - expected
        if unknown:
            parser.error(f"proof snapshot has theorems outside registered train split: {sorted(unknown)[:3]}")
        under = {name: count for name, count in counts.items() if count < args.samples_per_theorem}
        non_integral = {
            name: count for name, count in counts.items()
            if count % args.samples_per_theorem != 0
        }
        if under or non_integral:
            parser.error("a theorem lacks a whole registered proposal group")
        for name, count in counts.items():
            if count > args.samples_per_theorem:
                padding_by_theorem[name] = count - args.samples_per_theorem
        counts_by_path.append(counts)
        seen_theorems.update(counts)
        raw_proposals += records
        raw_correct += correct
        manifests.append({
            "path": str(path),
            "sha256": sha256(path),
            "raw_proposals": records,
            "raw_correct": correct,
            "unique_theorems": len(counts),
        })

    missing = expected - seen_theorems
    if missing:
        parser.error(f"C0 is incomplete; {len(missing)} registered train theorems are missing")
    padding = sum(padding_by_theorem.values())
    if padding != args.expected_padding_proposals:
        parser.error(
            f"observed {padding} padding proposals, expected {args.expected_padding_proposals}"
        )

    successes: Counter[str] = Counter()
    correct_modes: dict[str, Counter[str]] = defaultdict(Counter)
    exact_by_theorem: dict[str, set[str]] = defaultdict(set)
    selected_correct = 0
    selected_proposals = 0
    for path, path_counts in zip(proof_paths, counts_by_path, strict=True):
        accepted: Counter[str] = Counter()
        with path.open(encoding="utf-8") as stream:
            for line in stream:
                record = json.loads(line)
                theorem = str(record["theorem_name"])
                if accepted[theorem] >= args.samples_per_theorem:
                    continue
                accepted[theorem] += 1
                selected_proposals += 1
                if record["correct"]:
                    selected_correct += 1
                    successes[theorem] += 1
                    correct_modes[theorem][mode_id(record["proof"])] += 1
                    exact_by_theorem[theorem].add(exact_proof_id(record["proof"]))
        if set(accepted) != set(path_counts) or any(
            count != args.samples_per_theorem for count in accepted.values()
        ):
            raise RuntimeError(f"internal selection error while processing {path}")

    expected_selected = len(expected) * args.samples_per_theorem
    if selected_proposals != expected_selected:
        raise RuntimeError("registered proposal count does not match theorem budget")

    archive = ModeArchive(metadata={
        "signature_version": "mode_id_v1",
        "source_condition": "c0_base",
        "source_runs": [str(path.parents[2]) for path in proof_paths],
        "data_split": "train",
        "model_revision": args.model_revision,
        "dataset": str(dataset),
        "dataset_sha256": args.dataset_sha256,
        "seed": args.seed,
        "samples_per_theorem": args.samples_per_theorem,
        "proof_logs": manifests,
        "padding_selection": "first registered proposal group retained per theorem",
    })
    for theorem, modes in correct_modes.items():
        for mode, count in modes.items():
            archive.counts[theorem][mode] = count

    solved = set(successes)
    mode_counts = [len(correct_modes[name]) for name in solved]
    exact_counts = [len(exact_by_theorem[name]) for name in solved]
    dominant = {
        name: archive.dominant_mode(name, threshold=0.5, min_verified=4)
        for name in expected
    }
    dominant = {name: mode for name, mode in dominant.items() if mode is not None}
    dominant_with_alternative = sum(len(correct_modes[name]) >= 2 for name in dominant)
    dominant_blocked_correct = sum(correct_modes[name][mode] for name, mode in dominant.items())
    dominant_eligible_correct = sum(successes[name] for name in dominant)
    pass_metrics = {
        f"pass_at_{n}": sum(
            pass_at_n(successes[name], args.samples_per_theorem, n) for name in expected
        ) / len(expected)
        for n in (1, 4, 8, 16, 32)
    }

    output_dir.mkdir(parents=True)
    archive_path = output_dir / "mode_archive.json"
    archive_checksum = archive.save(archive_path)
    (output_dir / "mode_archive.json.sha256").write_text(archive_checksum + "\n", encoding="utf-8")
    validation = {
        "status": "valid",
        "expected_training_theorems": len(expected),
        "observed_training_theorems": len(seen_theorems),
        "samples_per_theorem": args.samples_per_theorem,
        "registered_proposals": selected_proposals,
        "raw_generated_and_verified_proposals": raw_proposals,
        "padding_proposals_excluded_from_scientific_sample": padding,
        "padding_by_theorem": dict(sorted(padding_by_theorem.items())),
        "proof_logs": manifests,
    }
    metrics = {
        "condition": "c0_base",
        "completed_at_utc": datetime.now(timezone.utc).isoformat(),
        "model_revision": args.model_revision,
        "dataset": str(dataset),
        "dataset_sha256": args.dataset_sha256,
        "seed": args.seed,
        "raw_proposals": raw_proposals,
        "raw_verified": raw_proposals,
        "raw_correct": raw_correct,
        "padding_proposals_excluded": padding,
        "proposals": selected_proposals,
        "verified": selected_proposals,
        "correct": selected_correct,
        "blocked": 0,
        "trained_samples": 0,
        "solved_theorems": len(solved),
        "expected_training_theorems": len(expected),
        "pass_at_n": pass_metrics,
        "correct_mode_coverage": sum(mode_counts),
        "exact_proof_coverage": sum(exact_counts),
        "correct_modes_per_solved_theorem": distribution(mode_counts),
        "exact_proofs_per_solved_theorem": distribution(exact_counts),
        "solved_with_at_least_2_modes": sum(value >= 2 for value in mode_counts),
        "solved_with_at_least_3_modes": sum(value >= 3 for value in mode_counts),
        "solved_with_at_least_4_modes": sum(value >= 4 for value in mode_counts),
        "solved_with_at_least_8_modes": sum(value >= 8 for value in mode_counts),
        "dominant_eligible_theorems": len(dominant),
        "dominant_eligible_with_alternative_modes": dominant_with_alternative,
        "dominant_blocked_correct_proposals": dominant_blocked_correct,
        "dominant_eligible_correct_proposals": dominant_eligible_correct,
        "archive": str(archive_path),
        "archive_sha256": archive_checksum,
    }
    (output_dir / "validation.json").write_text(
        json.dumps(validation, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    (output_dir / "metrics.json").write_text(
        json.dumps(metrics, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    metadata = [
        "# Complete C0 Aggregate", "", "Status: complete and validated.", "",
        f"- Completed: `{metrics['completed_at_utc']}`",
        f"- Model revision: `{args.model_revision}`",
        f"- Dataset: `{dataset}` (`{args.dataset_sha256}`)",
        f"- Seed: {args.seed}",
        f"- Registered sample: {len(expected)} train theorems x {args.samples_per_theorem} = {selected_proposals} proposals",
        f"- Physical compute: {raw_proposals} generated and verified proposals; {padding} padding proposals are reported and excluded from scientific metrics",
        f"- Correct: {selected_correct}; blocked: 0; trained: 0",
        f"- Archive: `mode_archive.json` (`{archive_checksum}`)",
        "- Validation: `validation.json`; metrics: `metrics.json`", "",
        "## Source snapshots", "",
    ]
    metadata.extend(f"- `{item['path']}` (`{item['sha256']}`)" for item in manifests)
    (output_dir / "RUN_METADATA.md").write_text("\n".join(metadata) + "\n", encoding="utf-8")
    print(json.dumps({"output_dir": str(output_dir), **metrics}, sort_keys=True))


if __name__ == "__main__":
    main()
