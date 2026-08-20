#!/usr/bin/env python3
"""Analyze C1/C3 mode-collapse dynamics and C0 mode suppression."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from collections import Counter, defaultdict
from math import comb
from pathlib import Path

import pandas as pd


STEP_RE = re.compile(r":step-(\d+)$")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def latest_proof_log(run_dir: Path) -> Path:
    paths = list((run_dir / "artifacts/proofs").glob("global_step_*.jsonl"))
    if not paths:
        raise FileNotFoundError(f"no proof snapshot under {run_dir}")
    return max(paths, key=lambda path: int(path.stem.rsplit("_", 1)[1]))


def expected_rarefied_modes(counts: Counter[str], draws: int) -> float:
    total = sum(counts.values())
    if draws < 0 or draws > total:
        raise ValueError("rarefaction draws must be between zero and the sample size")
    if draws == 0:
        return 0.0
    denominator = comb(total, draws)
    return sum(
        1.0 - (comb(total - count, draws) / denominator if total - count >= draws else 0.0)
        for count in counts.values()
    )


def effective_modes(counts: Counter[str]) -> float:
    total = sum(counts.values())
    if total == 0:
        return 0.0
    return 1.0 / sum((count / total) ** 2 for count in counts.values())


def load_run(run_dir: Path) -> tuple[dict[str, dict], dict]:
    frame = pd.read_parquet(run_dir / "train.parquet")
    expected = [str(value) for value in frame["theorem_full_name"]]
    expected_set = set(expected)
    proof_log = latest_proof_log(run_dir)
    seen: Counter[str] = Counter()
    data: dict[str, dict] = {
        name: {
            "step": None,
            "correct": 0,
            "blocked": 0,
            "modes": Counter(),
            "exact": Counter(),
            "examples": {},
        }
        for name in expected
    }
    physical = 0
    with proof_log.open(encoding="utf-8") as stream:
        for line in stream:
            physical += 1
            item = json.loads(line)
            name = str(item["theorem_name"])
            if name not in expected_set or seen[name] >= 32:
                continue
            seen[name] += 1
            match = STEP_RE.search(str(item["batch_id"]))
            if match is None:
                raise ValueError(f"missing step in batch ID: {item['batch_id']}")
            step = int(match.group(1))
            if data[name]["step"] not in (None, step):
                raise ValueError(f"theorem {name} spans multiple training steps")
            data[name]["step"] = step
            data[name]["blocked"] += int(bool(item.get("blocked_correct", False)))
            if not item.get("correct", False):
                continue
            data[name]["correct"] += 1
            mode = str(item.get("tactic_prefix_signature") or item.get("mode_id"))
            exact = str(item["exact_proof_id"])
            data[name]["modes"][mode] += 1
            data[name]["exact"][exact] += 1
            data[name]["examples"].setdefault(
                mode,
                {
                    "proof": item["proof"],
                    "tactic_heads": item.get("tactic_heads", []),
                },
            )
    bad = {name: seen[name] for name in expected if seen[name] != 32}
    if bad:
        raise ValueError(f"{len(bad)} theorems do not have exactly 32 selected proposals")
    metadata = (run_dir / "RUN_METADATA.md").read_text(encoding="utf-8")
    commit_match = re.search(r"Git commit: `([0-9a-f]{40})`", metadata)
    if commit_match is None:
        raise ValueError(f"run metadata lacks a full Git commit: {run_dir}")
    metrics_path = run_dir / "metrics.json"
    metrics = json.loads(metrics_path.read_text(encoding="utf-8"))
    return data, {
        "run_dir": str(run_dir),
        "git_commit": commit_match.group(1),
        "model_revision": "e9a6e6fbb67620d4e9c4944bc51ff7c435af12da",
        "dataset_sha256": "56799bc5a19c4ccc0c671dd8631a16c0956786ae63ba5d4e30e9f30b7bbcc9eb",
        "seed": 42,
        "proof_log": str(proof_log),
        "proof_log_sha256": sha256(proof_log),
        "metrics_sha256": sha256(metrics_path),
        "hardware_record_sha256": metrics["hardware_record_sha256"],
        "wall_clock_seconds": metrics["wall_clock_seconds"],
        "registered_proposals": len(expected) * 32,
        "physical_proposals": physical,
        "excluded_padding_proposals": physical - len(expected) * 32,
    }


def summarize(theorems: list[dict]) -> dict:
    correct = sum(item["correct"] for item in theorems)
    modes = sum(len(item["modes"]) for item in theorems)
    exact = sum(len(item["exact"]) for item in theorems)
    solved = [item for item in theorems if item["correct"]]
    return {
        "theorems": len(theorems),
        "proposals": len(theorems) * 32,
        "correct": correct,
        "correct_rate": correct / (len(theorems) * 32),
        "blocked_correct": sum(item["blocked"] for item in theorems),
        "solved_theorems": len(solved),
        "correct_mode_coverage": modes,
        "modes_per_correct_rollout": modes / correct,
        "mean_modes_per_solved_theorem": modes / len(solved),
        "exact_proof_coverage": exact,
        "exact_proofs_per_correct_rollout": exact / correct,
        "mean_top_mode_share": sum(max(item["modes"].values()) / item["correct"] for item in solved)
        / len(solved),
        "mean_effective_modes": sum(effective_modes(item["modes"]) for item in solved) / len(solved),
    }


def windows(data: dict[str, dict], window_size: int) -> list[dict]:
    grouped: dict[int, list[dict]] = defaultdict(list)
    for item in data.values():
        grouped[(item["step"] - 1) // window_size].append(item)
    output = []
    for index, items in sorted(grouped.items()):
        summary = summarize(items)
        summary["step_start"] = index * window_size + 1
        summary["step_end"] = max(item["step"] for item in items)
        output.append(summary)
    return output


def rarefaction(data: dict[str, dict]) -> dict:
    output = {}
    for draws in (1, 2, 4, 8, 16):
        eligible = [item for item in data.values() if item["correct"] >= draws]
        output[str(draws)] = {
            "correct_draws": draws,
            "eligible_theorems": len(eligible),
            "mean_expected_modes": sum(
                expected_rarefied_modes(item["modes"], draws) for item in eligible
            )
            / len(eligible),
        }
    return output


def paired_rarefaction(c1: dict[str, dict], c3: dict[str, dict]) -> dict:
    output = {}
    for draws in (1, 2, 4, 8, 16):
        names = [name for name in c1 if c1[name]["correct"] >= draws and c3[name]["correct"] >= draws]
        c1_values = [expected_rarefied_modes(c1[name]["modes"], draws) for name in names]
        c3_values = [expected_rarefied_modes(c3[name]["modes"], draws) for name in names]
        deltas = [right - left for left, right in zip(c1_values, c3_values, strict=True)]
        deltas = [0.0 if abs(delta) < 1e-12 else delta for delta in deltas]
        output[str(draws)] = {
            "correct_draws": draws,
            "common_eligible_theorems": len(names),
            "c1_mean_expected_modes": sum(c1_values) / len(names),
            "c3_mean_expected_modes": sum(c3_values) / len(names),
            "mean_delta_c3_minus_c1": sum(deltas) / len(names),
            "theorems_c3_higher": sum(delta > 0 for delta in deltas),
            "theorems_equal": sum(delta == 0 for delta in deltas),
            "theorems_c1_higher": sum(delta < 0 for delta in deltas),
        }
    return output


def suppression(c0_counts: dict[str, dict[str, int]], c1: dict[str, dict], c3: dict[str, dict]) -> dict:
    floors = {}
    for floor in (1, 2, 4):
        base_total = suppressed = recovered = 0
        affected_theorems: set[str] = set()
        recovered_theorems: set[str] = set()
        for name, counts in c0_counts.items():
            base_modes = {mode for mode, count in counts.items() if count >= floor}
            c1_modes = set(c1[name]["modes"])
            c3_modes = set(c3[name]["modes"])
            lost = base_modes - c1_modes
            kept_by_c3 = lost & c3_modes
            base_total += len(base_modes)
            suppressed += len(lost)
            recovered += len(kept_by_c3)
            if lost:
                affected_theorems.add(name)
            if kept_by_c3:
                recovered_theorems.add(name)
        floors[str(floor)] = {
            "minimum_c0_observations": floor,
            "c0_modes": base_total,
            "c0_modes_absent_from_c1": suppressed,
            "suppressed_modes_present_in_c3": recovered,
            "recovery_fraction": recovered / suppressed if suppressed else None,
            "theorems_with_suppressed_mode": len(affected_theorems),
            "theorems_with_c3_recovery": len(recovered_theorems),
        }

    examples = []
    for name, counts in c0_counts.items():
        for mode, base_count in counts.items():
            if base_count < 2 or mode in c1[name]["modes"] or mode not in c3[name]["modes"]:
                continue
            example = c3[name]["examples"][mode]
            examples.append(
                {
                    "theorem": name,
                    "mode_id": mode,
                    "c0_count": base_count,
                    "c1_count": c1[name]["modes"].get(mode, 0),
                    "c3_count": c3[name]["modes"][mode],
                    "tactic_heads": example["tactic_heads"],
                    "c3_example_proof": example["proof"],
                }
            )
    examples.sort(key=lambda item: (-item["c3_count"], item["c0_count"], item["theorem"], item["mode_id"]))
    return {"by_c0_count_floor": floors, "top_recovered_examples": examples[:100]}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--c0-archive", type=Path, required=True)
    parser.add_argument("--c1-run", type=Path, required=True)
    parser.add_argument("--c3-run", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--window-size", type=int, default=100)
    args = parser.parse_args()

    c1, c1_source = load_run(args.c1_run.resolve())
    c3, c3_source = load_run(args.c3_run.resolve())
    if set(c1) != set(c3):
        parser.error("C1 and C3 theorem identities differ")
    archive_path = args.c0_archive.resolve()
    archive = json.loads(archive_path.read_text(encoding="utf-8"))
    c0_counts = archive["counts"]
    if set(c0_counts) - set(c1):
        parser.error("C0 archive contains theorem identities absent from C1/C3")

    result = {
        "analysis": "c1-c3-training-dynamics-and-c0-mode-suppression-v1",
        "sources": {
            "c0_archive": {"path": str(archive_path), "sha256": sha256(archive_path)},
            "c1": c1_source,
            "c3": c3_source,
        },
        "overall": {"c1": summarize(list(c1.values())), "c3": summarize(list(c3.values()))},
        "training_windows": {
            "window_size_steps": args.window_size,
            "c1": windows(c1, args.window_size),
            "c3": windows(c3, args.window_size),
        },
        "correct_rollout_rarefaction": {
            "c1": rarefaction(c1),
            "c3": rarefaction(c3),
            "paired_common_theorems": paired_rarefaction(c1, c3),
        },
        "c0_mode_suppression_and_c3_recovery": suppression(c0_counts, c1, c3),
        "claim_boundary": (
            "Mode absence or recovery is relative to finite 32-proposal samples and deterministic "
            "tactic signatures; it is not proof of semantic strategy loss or creation."
        ),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(args.output)


if __name__ == "__main__":
    main()
