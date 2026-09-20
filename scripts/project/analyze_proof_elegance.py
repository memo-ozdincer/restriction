#!/usr/bin/env python3
"""Exploratory concise-proof and sampled-recovery analysis for pass@128."""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
from scipy.stats import binomtest

from verl.lean.proof_modes import exact_proof_id, mode_id


CONDITIONS = {
    "c0": "c0_base",
    "c1": "c1_grpo_default",
    "c3": "c3_hardblock_restart",
}


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


def proof_dimensions(item: dict) -> tuple[int, int]:
    """Return generated tokens and parsed top-level tactic-head count."""
    return int(item["token_count"]), len(item["tactic_heads"])


def pareto_dominates_all(candidate: dict, comparators: list[dict]) -> bool:
    """Whether candidate strictly Pareto-dominates every comparator proof."""
    if not comparators:
        return False
    candidate_tokens, candidate_steps = proof_dimensions(candidate)
    for comparator in comparators:
        tokens, steps = proof_dimensions(comparator)
        if candidate_tokens > tokens or candidate_steps > steps:
            return False
        if candidate_tokens == tokens and candidate_steps == steps:
            return False
    return True


def concise_novel_candidates(
    treatment: list[dict], comparator: list[dict]
) -> list[dict]:
    """Return treatment proofs with a novel mode that dominate all comparator proofs."""
    comparator_modes = {item["mode_id"] for item in comparator}
    return [
        item
        for item in treatment
        if item["mode_id"] not in comparator_modes
        and pareto_dominates_all(item, comparator)
    ]


def qualifying_mode_relationship(
    treatment: dict[str, list[dict]],
    comparator: dict[str, list[dict]],
    source: dict[str, list[dict]],
) -> dict:
    """Split qualifying treatment modes into new and source-recovered modes."""
    qualifying: set[tuple[str, str]] = set()
    source_counts: dict[tuple[str, str], int] = {}
    for name in treatment:
        if not treatment[name] or not comparator.get(name, []):
            continue
        candidates = concise_novel_candidates(treatment[name], comparator[name])
        source_mode_counts = Counter(item["mode_id"] for item in source[name])
        for mode in {item["mode_id"] for item in candidates}:
            key = (name, mode)
            qualifying.add(key)
            source_counts[key] = source_mode_counts[mode]
    absent = sum(source_counts[key] == 0 for key in qualifying)
    present = len(qualifying) - absent
    return {
        "qualifying_tactic_modes": len(qualifying),
        "modes_absent_from_base_sample": absent,
        "modes_present_in_base_but_absent_from_comparator": present,
        "recovered_modes_by_minimum_base_observations": {
            str(floor): sum(source_counts[key] >= floor for key in qualifying)
            for floor in (2, 4, 8)
        },
    }


def directional_minimum_counts(
    treatment: dict[str, list[dict]], comparator: dict[str, list[dict]], field: str
) -> dict:
    common = [
        name for name in treatment if treatment[name] and comparator.get(name, [])
    ]
    if field == "tokens":
        measure = lambda item: int(item["token_count"])
    elif field == "parsed_tactic_heads":
        measure = lambda item: len(item["tactic_heads"])
    else:
        raise ValueError(f"unknown minimum-comparison field: {field}")
    deltas = [
        min(measure(item) for item in comparator[name])
        - min(measure(item) for item in treatment[name])
        for name in common
    ]
    wins = sum(delta > 0 for delta in deltas)
    losses = sum(delta < 0 for delta in deltas)
    discordant = wins + losses
    return {
        "common_solved_theorems": len(common),
        "treatment_lower": wins,
        "equal": len(common) - discordant,
        "comparator_lower": losses,
        "two_sided_exact_sign_p": (
            float(binomtest(wins, discordant, 0.5).pvalue) if discordant else 1.0
        ),
    }


def recovery_at_floor(
    base: dict[str, list[dict]],
    suppressed: dict[str, list[dict]],
    treatment: dict[str, list[dict]],
    *,
    identity_field: str,
    floors: tuple[int, ...],
) -> dict:
    output = {}
    for floor in floors:
        absent = recovered = recovered_theorems = 0
        for name in base:
            base_counts = Counter(item[identity_field] for item in base[name])
            suppressed_ids = {item[identity_field] for item in suppressed[name]}
            treatment_ids = {item[identity_field] for item in treatment[name]}
            eligible = {
                identity
                for identity, count in base_counts.items()
                if count >= floor and identity not in suppressed_ids
            }
            overlap = eligible & treatment_ids
            absent += len(eligible)
            recovered += len(overlap)
            recovered_theorems += bool(overlap)
        output[str(floor)] = {
            "minimum_base_observations": floor,
            "base_identities_absent_from_grpo": absent,
            "recovered_by_restriction": recovered,
            "recovery_rate": recovered / absent if absent else None,
            "theorems_with_recovery": recovered_theorems,
        }
    return output


def clean_proof(proof: str) -> str:
    lines = proof.rstrip().splitlines()
    if lines and lines[-1].strip() == "```":
        lines.pop()
    return "\n".join(lines).rstrip()


def compact_proof(item: dict) -> dict:
    return {
        "proof": clean_proof(item["proof"]),
        "token_count": int(item["token_count"]),
        "parsed_tactic_head_count": len(item["tactic_heads"]),
        "tactic_heads": item["tactic_heads"],
        "mode_id": item["mode_id"],
        "exact_proof_id": item["exact_proof_id"],
    }


def load_evaluation(run_dir: Path, expected_condition: str) -> tuple[dict, dict]:
    run_dir = run_dir.resolve()
    metrics_path = run_dir / "metrics.json"
    manifest_path = run_dir / "mode_manifest.json"
    metrics = json.loads(metrics_path.read_text(encoding="utf-8"))
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if metrics.get("condition") != expected_condition:
        raise ValueError(f"condition mismatch under {run_dir}")
    if metrics.get("classification") != "registered_evaluation_128":
        raise ValueError(f"run is not a registered pass@128 evaluation: {run_dir}")
    if metrics.get("completion_marker") != "upstream_post_completion_stop_sentinel":
        raise ValueError(f"run lacks the registered completion marker: {run_dir}")
    if manifest.get("condition") != expected_condition:
        raise ValueError(f"manifest condition mismatch under {run_dir}")
    if manifest.get("num_samples_per_theorem") != 128:
        raise ValueError(f"manifest is not pass@128 under {run_dir}")

    parquet_path = run_dir / "train.parquet"
    parquet_hash = sha256(parquet_path)
    if parquet_hash != metrics.get("evaluation_parquet_sha256"):
        raise ValueError(f"evaluation parquet hash mismatch under {run_dir}")
    if parquet_hash != manifest.get("evaluation_parquet_sha256"):
        raise ValueError(f"manifest parquet hash mismatch under {run_dir}")
    frame = pd.read_parquet(parquet_path)
    expected = [str(value) for value in frame["theorem_full_name"]]
    if len(expected) != len(set(expected)):
        raise ValueError("evaluation parquet contains duplicate theorem names")
    split_for = dict(
        zip(expected, frame["evaluation_dataset"].astype(str), strict=True)
    )

    proof_log = latest_proof_log(run_dir)
    proof_hash = sha256(proof_log)
    if proof_hash != metrics.get("proof_log_sha256"):
        raise ValueError(f"proof-log hash mismatch under {run_dir}")
    if sha256(manifest_path) != metrics.get("mode_manifest_sha256"):
        raise ValueError(f"mode-manifest hash mismatch under {run_dir}")

    grouped: dict[str, list[dict]] = defaultdict(list)
    physical = 0
    with proof_log.open(encoding="utf-8") as stream:
        for line in stream:
            physical += 1
            item = json.loads(line)
            grouped[str(item["theorem_name"])].append(item)
    if set(grouped) != set(expected):
        raise ValueError(f"proof theorem identities mismatch under {run_dir}")

    selected = {name: grouped[name][:128] for name in expected}
    if any(len(items) != 128 for items in selected.values()):
        raise ValueError(f"a theorem lacks 128 registered proposals under {run_dir}")
    if physical != metrics.get("physical_proposals"):
        raise ValueError(f"physical proposal count mismatch under {run_dir}")
    if len(expected) * 128 != metrics.get("registered_proposals"):
        raise ValueError(f"registered proposal count mismatch under {run_dir}")
    if physical - len(expected) * 128 != metrics.get("excluded_padding_proposals"):
        raise ValueError(f"excluded-padding count mismatch under {run_dir}")

    correct = {}
    for name, items in selected.items():
        correct[name] = []
        for item in items:
            if not item.get("correct", False):
                continue
            enriched = dict(item)
            enriched["mode_id"] = mode_id(item["proof"])
            enriched["exact_proof_id"] = exact_proof_id(item["proof"])
            correct[name].append(enriched)
        if {item["mode_id"] for item in correct[name]} != set(
            manifest["correct_modes_by_theorem"][name]
        ):
            raise ValueError(f"mode manifest does not reproduce theorem {name}")
        if {item["exact_proof_id"] for item in correct[name]} != set(
            manifest["exact_correct_proofs_by_theorem"][name]
        ):
            raise ValueError(f"exact-proof manifest does not reproduce theorem {name}")
    if sum(map(len, correct.values())) != metrics.get("correct"):
        raise ValueError(f"correct proposal count mismatch under {run_dir}")

    metadata = {
        "condition": expected_condition,
        "run_dir": str(run_dir),
        "metrics": str(metrics_path),
        "metrics_sha256": sha256(metrics_path),
        "proof_log": str(proof_log),
        "proof_log_sha256": proof_hash,
        "mode_manifest": str(manifest_path),
        "mode_manifest_sha256": sha256(manifest_path),
        "evaluation_parquet_sha256": parquet_hash,
        "registered_proposals": len(expected) * 128,
        "physical_proposals": physical,
    }
    return {
        "correct": correct,
        "split_for": split_for,
        "theorem_order": expected,
    }, metadata


def directional_cnp(
    treatment: dict[str, list[dict]],
    comparator: dict[str, list[dict]],
    source: dict[str, list[dict]],
    split_for: dict[str, str],
) -> tuple[dict, list[dict]]:
    rows = []
    for name in treatment:
        if not treatment[name] or not comparator[name]:
            continue
        candidates = concise_novel_candidates(treatment[name], comparator[name])
        if not candidates:
            continue
        representative = min(
            candidates, key=lambda item: (len(item["tactic_heads"]), item["token_count"])
        )
        comparator_best = min(
            comparator[name],
            key=lambda item: (len(item["tactic_heads"]), item["token_count"]),
        )
        source_modes = {item["mode_id"] for item in source[name]}
        source_exact = {item["exact_proof_id"] for item in source[name]}
        rows.append(
            {
                "theorem_name": name,
                "dataset": split_for[name],
                "informal_statement": representative["informal_statement"],
                "theorem_statement": representative["theorem_statement"],
                "treatment_proof": compact_proof(representative),
                "comparator_shortest_head_proof": compact_proof(comparator_best),
                "minimum_comparator_tokens": min(
                    item["token_count"] for item in comparator[name]
                ),
                "minimum_comparator_parsed_tactic_heads": min(
                    len(item["tactic_heads"]) for item in comparator[name]
                ),
                "treatment_mode_seen_in_base_sample": (
                    representative["mode_id"] in source_modes
                ),
                "treatment_exact_proof_seen_in_base_sample": (
                    representative["exact_proof_id"] in source_exact
                ),
            }
        )
    rows.sort(
        key=lambda row: (
            -(
                row["minimum_comparator_parsed_tactic_heads"]
                - row["treatment_proof"]["parsed_tactic_head_count"]
            ),
            -(
                row["minimum_comparator_tokens"]
                - row["treatment_proof"]["token_count"]
            ),
            row["theorem_name"],
        )
    )
    return {
        "theorems": len(rows),
        "by_dataset": dict(sorted(Counter(row["dataset"] for row in rows).items())),
        "qualifying_mode_relationship_to_base": qualifying_mode_relationship(
            treatment, comparator, source
        ),
    }, rows


def unique_solutions(
    treatment: dict[str, list[dict]],
    comparator: dict[str, list[dict]],
    source: dict[str, list[dict]],
    split_for: dict[str, str],
) -> list[dict]:
    rows = []
    for name in treatment:
        if not treatment[name] or comparator[name]:
            continue
        best = min(
            treatment[name],
            key=lambda item: (len(item["tactic_heads"]), item["token_count"]),
        )
        rows.append(
            {
                "theorem_name": name,
                "dataset": split_for[name],
                "informal_statement": best["informal_statement"],
                "theorem_statement": best["theorem_statement"],
                "treatment_correct_proposals": len(treatment[name]),
                "comparator_correct_proposals": 0,
                "base_correct_proposals": len(source[name]),
                "treatment_proof": compact_proof(best),
            }
        )
    return rows


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--c0-run", type=Path, required=True)
    parser.add_argument("--c1-run", type=Path, required=True)
    parser.add_argument("--c3-run", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    loaded = {}
    provenance = {}
    for short, run_dir in (("c0", args.c0_run), ("c1", args.c1_run), ("c3", args.c3_run)):
        loaded[short], provenance[short] = load_evaluation(
            run_dir, CONDITIONS[short]
        )
    parquet_hashes = {
        item["evaluation_parquet_sha256"] for item in provenance.values()
    }
    if len(parquet_hashes) != 1:
        parser.error("conditions do not use the same frozen evaluation parquet")
    theorem_orders = {tuple(item["theorem_order"]) for item in loaded.values()}
    if len(theorem_orders) != 1:
        parser.error("conditions do not use the same theorem order")

    c0 = loaded["c0"]["correct"]
    c1 = loaded["c1"]["correct"]
    c3 = loaded["c3"]["correct"]
    split_for = loaded["c0"]["split_for"]
    c3_cnp, c3_examples = directional_cnp(c3, c1, c0, split_for)
    c1_cnp, c1_examples = directional_cnp(c1, c3, c0, split_for)

    result = {
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "classification": "exploratory_posthoc_proof_concision_pass128",
        "interpretation_boundary": (
            "Lean correctness is definitive, but generated-token and parsed top-level "
            "tactic-head concision are syntactic proxies, not expert judgments of "
            "mathematical elegance. Sampled absence does not prove zero policy "
            "probability or literal forgetting."
        ),
        "metric_definition": {
            "name": "concise_novel_proof_yield_at_128",
            "abbreviation": "CNP@128",
            "unit": "theorems",
            "rule": (
                "Among theorems solved by both conditions, count a theorem when the "
                "treatment has a correct tactic mode absent from the comparator sample "
                "and at least one proof in that mode weakly improves both generated-token "
                "count and parsed top-level tactic-head count over every correct comparator "
                "proof, with a strict improvement for each comparison. Report both "
                "directions."
            ),
        },
        "provenance": provenance,
        "correctness": {
            short: {
                "correct_proposals": sum(map(len, loaded[short]["correct"].values())),
                "solved_theorems": sum(
                    bool(items) for items in loaded[short]["correct"].values()
                ),
            }
            for short in ("c0", "c1", "c3")
        },
        "restriction_vs_grpo": {
            "cnp_at_128": {
                "restriction_over_grpo": c3_cnp,
                "grpo_over_restriction": c1_cnp,
            },
            "minimum_parsed_tactic_heads": directional_minimum_counts(
                c3, c1, "parsed_tactic_heads"
            ),
            "minimum_generated_tokens": directional_minimum_counts(c3, c1, "tokens"),
            "restriction_only_solutions": unique_solutions(c3, c1, c0, split_for),
            "grpo_only_solutions": unique_solutions(c1, c3, c0, split_for),
        },
        "base_modes_sampled_absent_from_grpo": recovery_at_floor(
            c0, c1, c3, identity_field="mode_id", floors=(1, 2, 4, 8)
        ),
        "base_exact_proofs_sampled_absent_from_grpo": recovery_at_floor(
            c0, c1, c3, identity_field="exact_proof_id", floors=(1, 2, 4)
        ),
        "auditable_cnp_examples": {
            "restriction_over_grpo": c3_examples,
            "grpo_over_restriction": c1_examples,
        },
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    if args.output.exists():
        parser.error(f"refusing to overwrite {args.output}")
    args.output.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
