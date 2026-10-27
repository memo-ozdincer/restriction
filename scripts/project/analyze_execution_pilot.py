#!/usr/bin/env python3
"""Validate and summarize the registered base-policy continuation screen.

Use one complete proof snapshot for each panel, not all cumulative snapshots.
Scientific tasks are (theorem, exact prefix), never theorem identity alone.
Only explicitly marked, bounded world-size padding is excluded from the gate;
all such proposals remain in physical compute accounting.
"""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import hashlib
import json
import math
from pathlib import Path

from verl.lean.proof_prefix import conditioning_id


def sha256(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def text_hash(value):
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def require(condition, message):
    if not condition:
        raise ValueError(message)


def integer(value, label, minimum=0):
    require(type(value) is int and value >= minimum, f"invalid {label}: {value!r}")
    return value


def read_jsonl(path):
    with Path(path).open(encoding="utf-8") as stream:
        for line_number, line in enumerate(stream, 1):
            require(bool(line.strip()), f"blank record at {path}:{line_number}")
            row = json.loads(line)
            require(isinstance(row, dict), f"non-object record at {path}:{line_number}")
            yield row


def screen_samples(row):
    if row["pilot_split"] == "diagnostic":
        return 32
    return 16 if row["condition"] == "prefix" else 0


def validate_bank(bank, manifest):
    """Check identities and independence without consulting generated outcomes."""
    by_id = {}
    identities = set()
    split_theorems = defaultdict(set)
    by_theorem = defaultdict(list)
    for row in bank:
        row_id = row["pilot_row_id"]
        theorem = row["theorem_full_name"]
        prefix = row["proof_prefix"]
        require(isinstance(row_id, str) and row_id, "invalid pilot_row_id")
        require(row_id not in by_id, f"duplicate bank row: {row_id}")
        require(isinstance(prefix, str), f"invalid bank prefix: {row_id}")
        require(row["pilot_split"] in ("train", "diagnostic"), f"invalid split: {row_id}")
        require(row["condition"] == ("prefix" if prefix else "root"), f"condition mismatch: {row_id}")
        require(row["prefix_sha256"] == text_hash(prefix), f"prefix hash mismatch: {row_id}")
        cid = conditioning_id(row["theorem_statement"], row["src_context"], prefix)
        require(row["conditioning_id"] == cid, f"conditioning hash mismatch: {row_id}")
        require((theorem, prefix) not in identities, f"duplicate theorem/prefix: {row_id}")
        identities.add((theorem, prefix))
        integer(row["prefix_token_count"], "prefix_token_count")
        integer(row["prompt_token_count"], "prompt_token_count", 1)
        require(row["prompt_token_count"] <= 512, f"oversized prompt: {row_id}")
        if prefix:
            require(row["initial_tactic_head"] not in ("", "root"), f"missing first head: {row_id}")
            require(row["witness_sha256"] == text_hash(row["witness_proof"]), f"witness hash mismatch: {row_id}")
            require(row["witness_proof"].startswith(prefix), f"prefix is not exact witness slice: {row_id}")
        else:
            require(row["prefix_token_count"] == 0, f"root has prefix tokens: {row_id}")
        split_theorems[row["pilot_split"]].add(theorem)
        by_theorem[theorem].append(row)
        by_id[row_id] = row
    require(not split_theorems["train"] & split_theorems["diagnostic"], "train/diagnostic theorem leakage")
    for theorem, rows in by_theorem.items():
        prefixes = [row for row in rows if row["condition"] == "prefix"]
        require(sum(row["condition"] == "root" for row in rows) == 1, f"missing/duplicate root: {theorem}")
        require(1 <= len(prefixes) <= 2, f"wrong prefix count: {theorem}")
        require(len({row["initial_tactic_head"] for row in prefixes}) == len(prefixes),
                f"duplicate first-head routes: {theorem}")
    selection = manifest["selection"]
    for split, key in (("train", "train_theorem_ids"), ("diagnostic", "diagnostic_theorem_ids")):
        ids = selection[key]
        require(len(ids) == len(set(ids)) and set(ids) == split_theorems[split], f"selection identity mismatch: {split}")
        require(selection[f"{split}_theorems"] == len(ids), f"selection count mismatch: {split}")
    tasks = manifest["tasks"]
    require(len(tasks) == len(by_id) and {task["pilot_row_id"] for task in tasks} == set(by_id),
            "manifest task identities differ from bank")
    for task in tasks:
        row = by_id[task["pilot_row_id"]]
        require(task["conditioning_id"] == row["conditioning_id"], "manifest conditioning mismatch")
        require(type(task["screen_samples"]) is int and task["screen_samples"] == screen_samples(row),
                "manifest screen sample count changed")
    return by_id


def load_manifest(path):
    """Rehash source inputs and frozen panel artifacts; authenticate witnesses."""
    path = Path(path).resolve()
    manifest = json.loads(path.read_text(encoding="utf-8"))
    require(manifest["schema_version"] == 1, "unsupported manifest schema")
    verified = {}

    def check(file_path, digest):
        file_path = Path(file_path)
        if not file_path.is_absolute():
            file_path = path.parent / file_path
        file_path = file_path.resolve()
        if str(file_path) not in verified:
            verified[str(file_path)] = sha256(file_path)
        require(verified[str(file_path)] == digest, f"source checksum mismatch: {file_path}")
        return file_path

    require("selection_bank.jsonl" in manifest["files"], "bank checksum missing")
    for filename, digest in manifest["files"].items():
        check(path.parent / filename, digest)
    for key in ("source_dataset", "c0_validation"):
        spec = manifest[key]
        check(spec["path"], spec["sha256"])
    sources = {str(check(spec.get("local_path") or spec["path"], spec["sha256"])): spec["sha256"]
               for spec in manifest["source_logs"]}
    require(bool(sources), "source logs missing")
    for spec in manifest.get("source_run_histories", []):
        if spec["sha256"] is not None:
            check(spec["path"], spec["sha256"])
    for filename, digest in manifest.get("model_configuration_and_tokenizer_sha256", {}).items():
        check(Path(manifest["model_path"]) / filename, digest)
    bank = list(read_jsonl(path.parent / "selection_bank.jsonl"))
    by_id = validate_bank(bank, manifest)
    requested = defaultdict(lambda: defaultdict(list))
    for row in bank:
        if row["condition"] != "prefix":
            continue
        source = str(Path(row["source_log"]).resolve())
        require(source in sources and row["source_log_sha256"] == sources[source], "witness source not in manifest")
        requested[source][integer(row["source_line"], "source_line", 1)].append(row)
    for source, wanted in requested.items():
        remaining = set(wanted)
        for line_number, record in enumerate(read_jsonl(source), 1):
            if line_number not in wanted:
                continue
            for row in wanted[line_number]:
                require(record.get("correct") is True, "source witness was not verified correct")
                for saved, expected in (("theorem_name", "theorem_full_name"),
                                        ("theorem_statement", "theorem_statement"),
                                        ("context", "src_context"),
                                        ("informal_statement", "informal_statement"),
                                        ("proof", "witness_proof")):
                    require(record.get(saved) == row[expected], f"witness source mismatch: {row['pilot_row_id']}/{saved}")
            remaining.remove(line_number)
            if not remaining:
                break
        require(not remaining, f"missing source witness lines: {source}")
    return manifest, by_id, verified


def summarize(by_id, records):
    """Apply the fixed practice-only gate, preserving every physical cost."""
    expected = {key: row for key, row in by_id.items() if screen_samples(row)}
    grouped = defaultdict(list)
    padding_groups = defaultdict(list)
    proposal_ids = set()
    physical = []
    for record in records:
        row_id = record["pilot_row_id"]
        require(row_id in expected, f"unexpected task: {row_id}")
        row = expected[row_id]
        n = screen_samples(row)
        require(record.get("pilot_split") == row["pilot_split"], f"record split mismatch: {row_id}")
        require(type(record.get("pilot_padding")) is bool, f"missing explicit padding marker: {row_id}")
        for saved, bank_key in (("theorem_name", "theorem_full_name"),
                                ("theorem_statement", "theorem_statement"), ("context", "src_context")):
            require(record.get(saved) == row[bank_key], f"record theorem metadata mismatch: {row_id}/{saved}")
        prefix = record.get("proof_prefix", "")
        require(prefix == row["proof_prefix"], f"record prefix mismatch: {row_id}")
        if prefix:
            require(record.get("proof_prefix_sha256") == row["prefix_sha256"], f"record prefix hash mismatch: {row_id}")
            require(isinstance(record.get("generated_suffix"), str) and
                    record["proof"] == prefix + record["generated_suffix"], f"assembled proof mismatch: {row_id}")
            require(record.get("conditioning_id") == row["conditioning_id"], f"record conditioning mismatch: {row_id}")
        elif "conditioning_id" in record:
            require(record["conditioning_id"] == row["conditioning_id"], f"root conditioning mismatch: {row_id}")
        if "prompt_token_count" in record:
            require(record["prompt_token_count"] == row["prompt_token_count"], f"prompt token mismatch: {row_id}")
        require(record.get("proof_hash") == text_hash(record["proof"]), f"record proof hash mismatch: {row_id}")
        proposal_id = record.get("proposal_id")
        require(isinstance(proposal_id, str) and proposal_id, "missing proposal id")
        require(proposal_id not in proposal_ids, f"duplicate physical proposal id: {proposal_id}")
        proposal_ids.add(proposal_id)
        candidate = integer(record.get("candidate_index"), "candidate_index")
        require(candidate < n, f"candidate index outside registered budget: {row_id}")
        require(type(record.get("correct")) is bool and type(record.get("verdict")) is bool,
                f"non-boolean correctness: {row_id}")
        require(record["correct"] == record["verdict"], f"verdict disagreement: {row_id}")
        require(type(record.get("lean_complete")) is bool and
                (not record["correct"] or record["lean_complete"]), f"uncompleted correct proof: {row_id}")
        integer(record.get("token_count"), "token_count")
        require(type(record.get("timed_out")) is bool, f"missing timeout flag: {row_id}")
        require(not record["correct"] or (not record["timed_out"] and not record.get("verifier_error")),
                f"correct proof has verifier failure: {row_id}")
        for key in ("parse_time", "queue_wait_time", "verification_time"):
            value = record.get(key)
            require(value is None or (type(value) in (int, float) and math.isfinite(value) and value >= 0),
                    f"invalid timing: {row_id}/{key}")
        if record["pilot_padding"]:
            require(isinstance(record.get("batch_id"), str) and record["batch_id"], "padding batch id missing")
            index = integer(record.get("theorem_index_in_batch"), "theorem_index_in_batch")
            padding_groups[(row["pilot_split"], record["batch_id"], index, row_id)].append(record)
        else:
            grouped[row_id].append(record)
        physical.append(record)
    require(set(grouped) == set(expected), "missing registered tasks")
    for row_id, items in grouped.items():
        n = screen_samples(expected[row_id])
        require(len(items) == n and {item["candidate_index"] for item in items} == set(range(n)),
                f"exact scientific proposal count/index mismatch: {row_id}")
    padding_counts = Counter()
    for (split, _, _, row_id), items in padding_groups.items():
        n = screen_samples(expected[row_id])
        require(len(items) == n and {item["candidate_index"] for item in items} == set(range(n)),
                f"incomplete or duplicated padding group: {row_id}")
        padding_counts[split] += 1
    require(all(count <= 3 for count in padding_counts.values()), "padding exceeds three rows per panel")

    summaries = []
    eligible = set()
    eligible_by_head = defaultdict(set)
    eligible_prefixes = []
    for row_id in sorted(expected):
        row = expected[row_id]
        items = grouped[row_id]
        successes = sum(item["correct"] for item in items)
        result = {
            "pilot_row_id": row_id, "theorem": row["theorem_full_name"],
            "conditioning_id": row["conditioning_id"], "prefix_sha256": row["prefix_sha256"],
            "split": row["pilot_split"], "condition": row["condition"],
            "initial_tactic_head": row["initial_tactic_head"],
            "proposals": len(items), "correct": successes, "correctness": successes / len(items),
            "timed_out": sum(item["timed_out"] for item in items),
            "verifier_errors": sum(bool(item.get("verifier_error")) for item in items),
        }
        summaries.append(result)
        if row["pilot_split"] == "train" and row["condition"] == "prefix" and 1 <= successes <= 8:
            eligible.add(row["theorem_full_name"])
            eligible_by_head[row["initial_tactic_head"]].add(row["theorem_full_name"])
            eligible_prefixes.append(row_id)
    qualifying_heads = sorted(head for head, names in eligible_by_head.items() if len(names) >= 8)
    gate = {
        "advance": len(eligible) >= 48 and len(qualifying_heads) >= 4,
        "minimum_practice_theorems": 48, "successes_in_16_inclusive": [1, 8],
        "minimum_head_strata": 4, "minimum_theorems_per_head": 8,
        "eligible_theorems": sorted(eligible), "eligible_prefix_rows": eligible_prefixes,
        "eligible_theorems_by_head": {head: sorted(names) for head, names in sorted(eligible_by_head.items())},
        "qualifying_heads": qualifying_heads, "diagnostics_used_for_gate": False,
    }
    panels = {}
    for split, condition in (("train", "prefix"), ("diagnostic", "root"), ("diagnostic", "prefix")):
        rows = [row for row in summaries if row["split"] == split and row["condition"] == condition]
        per_theorem = defaultdict(list)
        for row in rows:
            per_theorem[row["theorem"]].append(row["correctness"])
        means = {name: sum(values) / len(values) for name, values in per_theorem.items()}
        panels[f"{split}_{condition}"] = {
            "tasks": len(rows), "theorems": len(means), "proposals": sum(row["proposals"] for row in rows),
            "correct": sum(row["correct"] for row in rows),
            "theorem_balanced_correctness": sum(means.values()) / len(means) if means else None,
            "correctness_by_theorem": dict(sorted(means.items())),
        }

    def costs(items):
        result = {
            "proposals": len(items), "verification_attempts": len(items),
            "generated_tokens": sum(item["token_count"] for item in items),
            "supplied_prefix_tokens": sum(expected[item["pilot_row_id"]]["prefix_token_count"] for item in items),
            "prompt_tokens": sum(expected[item["pilot_row_id"]]["prompt_token_count"] for item in items),
            "prompt_token_source": "frozen tokenizer counts, checked against logged counts when present",
            "timed_out": sum(item["timed_out"] for item in items),
            "verifier_errors": sum(bool(item.get("verifier_error")) for item in items),
            "failure_classes": dict(sorted(Counter(item.get("failure_class") or "none" for item in items).items())),
        }
        for key in ("parse_time", "queue_wait_time", "verification_time"):
            result[key + "_seconds_sum"] = sum(item[key] for item in items if item.get(key) is not None)
            result[key + "_missing"] = sum(item.get(key) is None for item in items)
        return result

    return {
        "classification": "base_continuation_signal_screen_not_capability_result",
        "gate": gate, "tasks": summaries, "panels": panels,
        "physical": costs(physical),
        "registered": costs([item for item in physical if not item["pilot_padding"]]),
        "explicit_padding": costs([item for item in physical if item["pilot_padding"]]),
        "padding_rows_by_panel": dict(sorted(padding_counts.items())),
        "wall_time": "not inferred from parallel verifier-duration sums; retain runtime logs",
    }


def analyze(manifest_path, practice_log, diagnostic_log):
    manifest, bank, verified = load_manifest(manifest_path)
    records = []
    logs = []
    for split, path in (("train", practice_log), ("diagnostic", diagnostic_log)):
        path = Path(path).resolve()
        rows = list(read_jsonl(path))
        require(all(row.get("pilot_split") == split for row in rows), f"wrong panel in {path}")
        records.extend(rows)
        logs.append({"split": split, "path": str(path), "sha256": sha256(path), "records": len(rows)})
    result = summarize(bank, records)
    result["provenance"] = {
        "manifest": str(Path(manifest_path).resolve()), "manifest_sha256": sha256(manifest_path),
        "registered_model_revision": manifest["model_revision"], "proof_logs": logs, "verified_source_sha256": verified,
        "runtime_attestation": "requires launcher completion, fresh-prefix validation, and model/config provenance; exact record counts alone do not certify these",
    }
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--practice-log", type=Path, required=True)
    parser.add_argument("--diagnostic-log", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        parser.error("refusing to overwrite frozen analysis")
    result = analyze(args.manifest, args.practice_log, args.diagnostic_log)
    with args.output.open("x", encoding="utf-8") as stream:
        json.dump(result, stream, indent=2, sort_keys=True)
        stream.write("\n")
    print(json.dumps({"output": str(args.output), "gate": result["gate"],
                      "physical_proposals": result["physical"]["proposals"]}, sort_keys=True))


if __name__ == "__main__":
    main()
