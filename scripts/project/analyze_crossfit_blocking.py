#!/usr/bin/env python3
"""Measure cross-fitted safety gates for stronger C0-derived mode blocking."""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import hashlib
import json
from pathlib import Path
from typing import Any

from verl.lean.proof_modes import mode_id


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_VALIDATION = ROOT / "runs/c0-base-20260804-seed42-complete/validation.json"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def unique_top(counts: Counter[str]) -> str | None:
    if not counts:
        return None
    largest = max(counts.values())
    winners = [mode for mode, count in counts.items() if count == largest]
    return winners[0] if len(winners) == 1 else None


def load_registered(validation_path: Path) -> dict[str, list[dict[str, Any]]]:
    validation = json.loads(validation_path.read_text(encoding="utf-8"))
    if validation.get("status") != "valid" or validation.get("samples_per_theorem") != 32:
        raise ValueError("validation is not the frozen complete 32-proposal C0 aggregate")

    by_theorem: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for item in validation["proof_logs"]:
        path = Path(item["path"])
        if not path.is_file() or sha256(path) != item["sha256"]:
            raise ValueError(f"snapshot checksum mismatch: {path}")
        with path.open(encoding="utf-8") as stream:
            for line_number, line in enumerate(stream, start=1):
                record = json.loads(line)
                try:
                    theorem = str(record["theorem_name"])
                    proof = record["proof"]
                    correct = record["correct"]
                except KeyError as error:
                    raise ValueError(f"{path}:{line_number} lacks {error.args[0]}") from error
                if not isinstance(proof, str) or not isinstance(correct, bool):
                    raise ValueError(f"{path}:{line_number} has invalid proof or verdict")
                if len(by_theorem[theorem]) < 32:
                    by_theorem[theorem].append(record)

    expected_theorems = int(validation["expected_training_theorems"])
    if len(by_theorem) != expected_theorems:
        raise ValueError(f"expected {expected_theorems} theorems, found {len(by_theorem)}")
    bad = {name: len(rows) for name, rows in by_theorem.items() if len(rows) != 32}
    if bad:
        raise ValueError(f"registered proposal groups are incomplete: {dict(list(bad.items())[:5])}")
    return by_theorem


def correct_counts(rows: list[dict[str, Any]]) -> Counter[str]:
    return Counter(mode_id(row["proof"]) for row in rows if row["correct"])


def analyze(by_theorem: dict[str, list[dict[str, Any]]]) -> dict[str, Any]:
    stable: list[dict[str, Any]] = []
    correct_total = 0
    solved = 0
    for theorem, rows in by_theorem.items():
        first = correct_counts(rows[:16])
        second = correct_counts(rows[16:])
        full = first + second
        correct_total += full.total()
        solved += int(bool(full))
        first_top = unique_top(first)
        second_top = unique_top(second)
        if first_top is None or first_top != second_top or full.total() < 4:
            continue
        blocked_mode = first_top
        stable.append({
            "theorem_name": theorem,
            "mode_id": blocked_mode,
            "correct": full.total(),
            "blocked_correct": full[blocked_mode],
            "first_alternatives": first.total() - first[blocked_mode],
            "second_alternatives": second.total() - second[blocked_mode],
        })

    floors: dict[str, Any] = {}
    for floor in (1, 2, 4):
        eligible = [
            row for row in stable
            if row["first_alternatives"] >= floor
            and row["second_alternatives"] >= floor
        ]
        blocked = sum(row["blocked_correct"] for row in eligible)
        retained = sum(row["correct"] - row["blocked_correct"] for row in eligible)
        floors[str(floor)] = {
            "eligible_theorems": len(eligible),
            "share_all_training_theorems": len(eligible) / len(by_theorem),
            "blocked_correct_proposals": blocked,
            "retained_alternative_correct_proposals": retained,
            "mean_retained_alternatives_per_eligible_theorem": (
                retained / len(eligible) if eligible else None
            ),
        }

    return {
        "analysis": "c0-crossfit-stable-top-blocking-v1",
        "status": "valid",
        "split": {
            "selection_a": "registered candidate indices 0-15",
            "validation_b": "registered candidate indices 16-31",
            "symmetric_requirement": "same unique top correct mode in both halves",
        },
        "theorems": len(by_theorem),
        "solved_theorems": solved,
        "correct_proposals": correct_total,
        "stable_top_theorems_minimum_four_correct": len(stable),
        "alternative_support_floors_per_half": floors,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--validation", type=Path, default=DEFAULT_VALIDATION)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        parser.error(f"refusing to overwrite output: {args.output}")
    report = analyze(load_registered(args.validation.resolve()))
    report["source_validation"] = {
        "path": str(args.validation.resolve()),
        "sha256": sha256(args.validation.resolve()),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    rendered = json.dumps(report, indent=2, sort_keys=True) + "\n"
    args.output.write_text(rendered, encoding="utf-8")
    print(rendered, end="")


if __name__ == "__main__":
    main()
