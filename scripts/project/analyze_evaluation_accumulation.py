#!/usr/bin/env python3
"""Analyze pass@K and correct-mode accumulation in matched Lean evaluations."""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter, defaultdict
from datetime import datetime, timezone
from math import comb
from pathlib import Path

import pandas as pd
from scipy.stats import wilcoxon

from scripts.project.analyze_training_dynamics import effective_modes, expected_rarefied_modes
from verl.lean.proof_modes import exact_proof_id, mode_id, tactic_heads


CONDITIONS = ("c0_base", "c1_grpo_default", "c3_hardblock_restart")
DATASETS = ("combined", "registered_valid", "minif2f_test")


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


def expected_distinct_from_proposals(counts: Counter[str], total: int, draws: int) -> float:
    """Expected represented correct modes in draws without replacement."""
    if draws < 0 or draws > total:
        raise ValueError("draws must be between zero and the proposal total")
    if draws == 0:
        return 0.0
    denominator = comb(total, draws)
    return sum(
        1.0 - (comb(total - count, draws) / denominator if total - count >= draws else 0.0)
        for count in counts.values()
    )


def pass_at_n(successes: int, attempts: int, n: int) -> float:
    failures = attempts - successes
    return 1.0 if failures < n else 1.0 - comb(failures, n) / comb(attempts, n)


def safe_wilcoxon(values: list[float]) -> float:
    normalized = [0.0 if abs(value) < 1e-12 else value for value in values]
    if not normalized or all(value == 0.0 for value in normalized):
        return 1.0
    # Preserve zero-difference pairs using the Pratt convention used by the
    # registered pass@32 theorem-level analysis.
    return float(wilcoxon(normalized, zero_method="pratt", method="approx").pvalue)


def load_run(run_dir: Path, expected_condition: str) -> tuple[dict[str, dict], dict]:
    run_dir = run_dir.resolve()
    metrics_path = run_dir / "metrics.json"
    metrics = json.loads(metrics_path.read_text(encoding="utf-8"))
    if metrics["condition"] != expected_condition:
        raise ValueError(f"condition mismatch in {run_dir}")
    frame = pd.read_parquet(run_dir / "train.parquet")
    names = [str(value) for value in frame["theorem_full_name"]]
    dataset_for = dict(zip(names, frame["evaluation_dataset"], strict=True))
    if len(names) != len(set(names)):
        raise ValueError(f"duplicate theorem identity in {run_dir}")
    num_samples, remainder = divmod(metrics["registered_proposals"], len(names))
    if remainder or num_samples not in (32, 128):
        raise ValueError(f"unsupported proposal accounting in {run_dir}")

    proof_log = latest_proof_log(run_dir)
    grouped: dict[str, list[dict]] = defaultdict(list)
    with proof_log.open(encoding="utf-8") as stream:
        for line in stream:
            item = json.loads(line)
            grouped[str(item["theorem_name"])].append(item)
    if set(grouped) != set(names):
        raise ValueError(f"proof theorem identities differ from parquet in {run_dir}")

    data = {}
    for name in names:
        if len(grouped[name]) < num_samples:
            raise ValueError(f"{name} has fewer than {num_samples} proposals")
        proposals = []
        for item in grouped[name][:num_samples]:
            correct = bool(item.get("correct", False))
            proof = str(item.get("proof", ""))
            proposals.append(
                {
                    "correct": correct,
                    "mode": mode_id(proof) if correct else None,
                    "exact": exact_proof_id(proof) if correct else None,
                    "heads": tactic_heads(proof) if correct else (),
                }
            )
        data[name] = {"dataset": dataset_for[name], "proposals": proposals}

    source = {
        "run_dir": str(run_dir),
        "metrics": str(metrics_path),
        "metrics_sha256": sha256(metrics_path),
        "proof_log": str(proof_log),
        "proof_log_sha256": sha256(proof_log),
        "evaluation_parquet_sha256": sha256(run_dir / "train.parquet"),
        "num_samples": num_samples,
        "metrics_payload": metrics,
    }
    return data, source


def select_names(data: dict[str, dict], dataset: str) -> list[str]:
    if dataset == "combined":
        return list(data)
    return [name for name, item in data.items() if item["dataset"] == dataset]


def full_counts(item: dict) -> tuple[int, Counter[str], Counter[str]]:
    proposals = item["proposals"]
    return (
        sum(proposal["correct"] for proposal in proposals),
        Counter(proposal["mode"] for proposal in proposals if proposal["correct"]),
        Counter(proposal["exact"] for proposal in proposals if proposal["correct"]),
    )


def representation_key(proposal: dict, representation: str):
    heads = tuple(proposal["heads"])
    if representation == "first_head":
        return heads[:1]
    if representation == "first_two_heads":
        return heads[:2]
    if representation == "unordered_head_set":
        return tuple(sorted(set(heads)))
    if representation == "head_multiset":
        return tuple(sorted(Counter(heads).items()))
    if representation == "ordered_head_sequence":
        return heads
    if representation == "exact_proof":
        return proposal["exact"]
    raise ValueError(f"unknown representation: {representation}")


def representation_coverage(item: dict, representation: str) -> int:
    return len(
        {
            representation_key(proposal, representation)
            for proposal in item["proposals"]
            if proposal["correct"]
        }
    )


def accumulation_summary(data: dict[str, dict], names: list[str], draws: int) -> dict:
    total = len(next(iter(data.values()))["proposals"])
    observed_correct = observed_solved = observed_modes = observed_exact = 0
    expected_solved = expected_modes = expected_exact = 0.0
    for name in names:
        proposals = data[name]["proposals"]
        prefix = proposals[:draws]
        prefix_modes = {item["mode"] for item in prefix if item["correct"]}
        prefix_exact = {item["exact"] for item in prefix if item["correct"]}
        prefix_correct = sum(item["correct"] for item in prefix)
        observed_correct += prefix_correct
        observed_solved += int(prefix_correct > 0)
        observed_modes += len(prefix_modes)
        observed_exact += len(prefix_exact)

        correct, modes, exact = full_counts(data[name])
        expected_solved += pass_at_n(correct, total, draws)
        expected_modes += expected_distinct_from_proposals(modes, total, draws)
        expected_exact += expected_distinct_from_proposals(exact, total, draws)
    return {
        "theorems": len(names),
        "draws_per_theorem": draws,
        "observed_prefix": {
            "correct": observed_correct,
            "solved": observed_solved,
            "correct_mode_coverage": observed_modes,
            "mean_correct_modes_per_theorem": observed_modes / len(names),
            "exact_correct_proof_coverage": observed_exact,
        },
        "expected_from_full_sample": {
            "solved": expected_solved,
            "pass_at_n": expected_solved / len(names),
            "correct_mode_coverage": expected_modes,
            "mean_correct_modes_per_theorem": expected_modes / len(names),
            "exact_correct_proof_coverage": expected_exact,
        },
    }


def validate_finalized_metrics(data: dict[str, dict], source: dict, ks: list[int]) -> None:
    metrics = source["metrics_payload"]
    for dataset in ("registered_valid", "minif2f_test"):
        names = select_names(data, dataset)
        for k in ks:
            expected = accumulation_summary(data, names, k)["expected_from_full_sample"]["pass_at_n"]
            actual = metrics["datasets"][dataset]["pass_at_n"][f"pass_at_{k}"]
            if abs(expected - actual) > 1e-12:
                raise ValueError(f"pass@{k} does not reproduce finalized metrics for {dataset}")
        full = accumulation_summary(data, names, source["num_samples"])["observed_prefix"]
        finalized = metrics["datasets"][dataset]
        if full["correct"] != finalized["correct"]:
            raise ValueError(f"correct count does not reproduce finalized metrics for {dataset}")
        if full["correct_mode_coverage"] != finalized["correct_mode_coverage"]:
            raise ValueError(f"mode coverage does not reproduce finalized metrics for {dataset}")


def paired_full_sample(left: dict[str, dict], right: dict[str, dict], names: list[str]) -> dict:
    fields = {"correct": [], "modes": [], "exact": [], "top_mode_share": [], "effective_modes": []}
    direction = {"modes": [0, 0, 0], "correct": [0, 0, 0]}
    common_solved = 0
    for name in names:
        lcorrect, lmodes, lexact = full_counts(left[name])
        rcorrect, rmodes, rexact = full_counts(right[name])
        fields["correct"].append(rcorrect - lcorrect)
        fields["modes"].append(len(rmodes) - len(lmodes))
        fields["exact"].append(len(rexact) - len(lexact))
        for key, delta in (("modes", fields["modes"][-1]), ("correct", fields["correct"][-1])):
            direction[key][0 if delta < 0 else 1 if delta == 0 else 2] += 1
        if lcorrect and rcorrect:
            common_solved += 1
            fields["top_mode_share"].append(max(rmodes.values()) / rcorrect - max(lmodes.values()) / lcorrect)
            fields["effective_modes"].append(effective_modes(rmodes) - effective_modes(lmodes))
    return {
        "theorems": len(names),
        "common_solved_theorems": common_solved,
        "mean_delta_right_minus_left": {
            key: sum(values) / len(values) if values else None for key, values in fields.items()
        },
        "paired_wilcoxon_p": {
            key: safe_wilcoxon(values) if values else None for key, values in fields.items()
        },
        "direction_counts": {
            key: {"right_lower": values[0], "equal": values[1], "right_higher": values[2]}
            for key, values in direction.items()
        },
    }


def paired_correct_rarefaction(
    conditions: dict[str, dict[str, dict]], names: list[str], levels: tuple[int, ...]
) -> dict:
    output = {}
    for draws in levels:
        eligible = [
            name
            for name in names
            if all(full_counts(conditions[condition][name])[0] >= draws for condition in CONDITIONS)
        ]
        if not eligible:
            continue
        values = {
            condition: [
                expected_rarefied_modes(full_counts(conditions[condition][name])[1], draws)
                for name in eligible
            ]
            for condition in CONDITIONS
        }
        c3_c1 = [right - left for left, right in zip(values["c1_grpo_default"], values["c3_hardblock_restart"], strict=True)]
        output[str(draws)] = {
            "correct_draws": draws,
            "common_eligible_theorems": len(eligible),
            "mean_expected_modes": {
                condition: sum(condition_values) / len(condition_values)
                for condition, condition_values in values.items()
            },
            "c3_minus_c1": {
                "mean": sum(c3_c1) / len(c3_c1),
                "paired_wilcoxon_p": safe_wilcoxon(c3_c1),
                "c3_higher": sum(value > 1e-12 for value in c3_c1),
                "equal": sum(abs(value) <= 1e-12 for value in c3_c1),
                "c1_higher": sum(value < -1e-12 for value in c3_c1),
            },
        }
    return output


def c0_suppression_recovery(
    c0: dict[str, dict], c1: dict[str, dict], c3: dict[str, dict], names: list[str]
) -> dict:
    output = {}
    for floor in (1, 2, 4, 8):
        base = suppressed = recovered = 0
        affected = recovered_theorems = 0
        for name in names:
            c0_modes = {mode for mode, count in full_counts(c0[name])[1].items() if count >= floor}
            c1_modes = set(full_counts(c1[name])[1])
            c3_modes = set(full_counts(c3[name])[1])
            lost = c0_modes - c1_modes
            restored = lost & c3_modes
            base += len(c0_modes)
            suppressed += len(lost)
            recovered += len(restored)
            affected += int(bool(lost))
            recovered_theorems += int(bool(restored))
        output[str(floor)] = {
            "minimum_c0_observations": floor,
            "c0_modes": base,
            "c0_modes_absent_from_c1": suppressed,
            "suppressed_modes_present_in_c3": recovered,
            "recovery_fraction": recovered / suppressed if suppressed else None,
            "theorems_with_suppressed_mode": affected,
            "theorems_with_c3_recovery": recovered_theorems,
        }
    return output


def representation_robustness(conditions: dict[str, dict[str, dict]], names: list[str]) -> dict:
    output = {}
    for representation in (
        "first_head",
        "first_two_heads",
        "unordered_head_set",
        "head_multiset",
        "ordered_head_sequence",
        "exact_proof",
    ):
        coverage = {
            condition: [
                representation_coverage(conditions[condition][name], representation)
                for name in names
            ]
            for condition in CONDITIONS
        }
        deltas = [
            right - left
            for left, right in zip(
                coverage["c1_grpo_default"],
                coverage["c3_hardblock_restart"],
                strict=True,
            )
        ]
        output[representation] = {
            "coverage": {
                condition: sum(values) for condition, values in coverage.items()
            },
            "c3_minus_c1": {
                "mean_per_theorem": sum(deltas) / len(deltas),
                "paired_wilcoxon_p": safe_wilcoxon(deltas),
                "c3_higher": sum(delta > 0 for delta in deltas),
                "equal": sum(delta == 0 for delta in deltas),
                "c1_higher": sum(delta < 0 for delta in deltas),
            },
        }
    return output


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    for condition in CONDITIONS:
        parser.add_argument(f"--{condition.replace('_', '-')}-run", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    conditions = {}
    sources = {}
    for condition in CONDITIONS:
        conditions[condition], sources[condition] = load_run(
            getattr(args, f"{condition}_run"), condition
        )
    theorem_sets = {frozenset(data) for data in conditions.values()}
    sample_counts = {source["num_samples"] for source in sources.values()}
    parquet_hashes = {source["evaluation_parquet_sha256"] for source in sources.values()}
    if len(theorem_sets) != 1 or len(sample_counts) != 1 or len(parquet_hashes) != 1:
        parser.error("evaluation theorem sets, proposal budgets, or parquets differ")
    num_samples = sample_counts.pop()
    ks = [value for value in (1, 4, 8, 16, 32, 64, 128) if value <= num_samples]
    for condition in CONDITIONS:
        validate_finalized_metrics(conditions[condition], sources[condition], ks)

    accumulation = {}
    paired = {}
    rarefaction = {}
    suppression = {}
    robustness = {}
    reference = conditions["c0_base"]
    for dataset in DATASETS:
        names = select_names(reference, dataset)
        accumulation[dataset] = {
            condition: {
                str(k): accumulation_summary(conditions[condition], names, k) for k in ks
            }
            for condition in CONDITIONS
        }
        paired[dataset] = {
            "c3_minus_c1": paired_full_sample(
                conditions["c1_grpo_default"], conditions["c3_hardblock_restart"], names
            ),
            "c1_minus_c0": paired_full_sample(
                conditions["c0_base"], conditions["c1_grpo_default"], names
            ),
            "c3_minus_c0": paired_full_sample(
                conditions["c0_base"], conditions["c3_hardblock_restart"], names
            ),
        }
        rarefaction[dataset] = paired_correct_rarefaction(
            conditions, names, (1, 2, 4, 8, 16, 32, 64)
        )
        suppression[dataset] = c0_suppression_recovery(
            conditions["c0_base"], conditions["c1_grpo_default"],
            conditions["c3_hardblock_restart"], names,
        )
        robustness[dataset] = representation_robustness(conditions, names)

    serializable_sources = {
        condition: {key: value for key, value in source.items() if key != "metrics_payload"}
        for condition, source in sources.items()
    }
    result = {
        "analysis": "registered-evaluation-mode-accumulation-v1",
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "num_samples_per_theorem": num_samples,
        "evaluation_parquet_sha256": parquet_hashes.pop(),
        "sources": serializable_sources,
        "accumulation": accumulation,
        "paired_full_sample": paired,
        "correct_rollout_rarefaction": rarefaction,
        "c0_mode_suppression_and_c3_recovery": suppression,
        "representation_robustness": robustness,
        "claim_boundary": (
            "Modes are deterministic tactic signatures, not semantic proof strategies. "
            "Suppression and recovery denote absence and presence in finite matched samples."
        ),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    if args.output.exists():
        parser.error(f"refusing to overwrite {args.output}")
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(args.output)


if __name__ == "__main__":
    main()
