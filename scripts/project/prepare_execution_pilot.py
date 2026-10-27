#!/usr/bin/env python3
"""Freeze a train-only, hash-selected proof-prefix execution pilot panel.

Selection uses existing verified C0 proofs, never fresh model scores. Prefix
boundaries are conservative lexical tactic boundaries, not semantic strategies.
The original proof bytes (decoded UTF-8 text) are sliced without reconstruction.
"""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict, deque
import hashlib
import json
from pathlib import Path
import re
import subprocess


ROOT = Path(__file__).resolve().parents[2]
BUNDLE = ROOT.parent
MODEL = "deepseek-ai/DeepSeek-Prover-V1.5-SFT"
MODEL_REVISION = "e9a6e6fbb67620d4e9c4944bc51ff7c435af12da"
SOURCE_SHA256 = "56799bc5a19c4ccc0c671dd8631a16c0956786ae63ba5d4e30e9f30b7bbcc9eb"
VALIDATION_SHA256 = "afc65230ae2501cb668ec64031855054841ebd5818cdbaf6fda5254ec04ecdf3"
OLD_ROOT = "/scratch/memoozd/rl/restriction/"
HEAD = re.compile(r"([A-Za-z_][A-Za-z0-9_'.!?]*)")
CONTINUATION = re.compile(r"(?:\b(?:by|do|then|else|with)|:=|=>|<;>|[;,|=])\s*$")
NON_TACTICS = {"by", "case", "next", "end", "else", "then", "where", "in", "with"}


def sha256(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def text_hash(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def rank(seed, *parts):
    return text_hash(json.dumps([seed, *parts], ensure_ascii=False))


def mask_comments_and_strings(text):
    """Return equal-length lexical code mask; reject unfinished constructs."""
    result = list(text)
    depth = 0
    quoted = False
    i = 0
    while i < len(text):
        pair = text[i:i + 2]
        if depth:
            if pair == "/-":
                result[i:i + 2] = "  "
                depth += 1
                i += 2
                continue
            if pair == "-/":
                result[i:i + 2] = "  "
                depth -= 1
                i += 2
                continue
            if text[i] != "\n":
                result[i] = " "
        elif quoted:
            if text[i] == "\\" and i + 1 < len(text):
                result[i:i + 2] = "  "
                i += 2
                continue
            if text[i] == '"':
                quoted = False
            if text[i] != "\n":
                result[i] = " "
        elif pair == "/-":
            result[i:i + 2] = "  "
            depth = 1
            i += 2
            continue
        elif pair == "--":
            end = text.find("\n", i)
            end = len(text) if end < 0 else end
            result[i:end] = " " * (end - i)
            i = end
            continue
        elif text[i] == '"':
            quoted = True
            result[i] = " "
        i += 1
    if depth or quoted:
        raise ValueError("unfinished comment or string")
    return "".join(result)


def prefix_boundaries(proof):
    """Yield (exact prefix, step count, remaining steps, initial head).

Nested tactic blocks and balanced multiline expressions stay together. This
deliberately excludes nonstandard/ambiguous syntax instead of guessing where
it is safe to cut. The source full proof already has a successful Lean verdict;
the generated continuation must still be independently verified later.
"""
    body = proof.split("```", 1)[0]
    if not body or "\t" in body or "\r" in body:
        return []
    # Character literals need a real Lean lexer; do not guess their delimiters.
    if re.search(r"'(?:\\.|[^'\n])'", body):
        return []
    try:
        mask = mask_comments_and_strings(body)
    except ValueError:
        return []
    if re.search(r"\b(?:sorry|admit)\b", mask):
        return []
    lines = mask.splitlines(keepends=True)
    meaningful = [line for line in lines if line.strip()]
    if not meaningful:
        return []
    base_indent = len(meaningful[0]) - len(meaningful[0].lstrip(" "))
    first_match = HEAD.match(meaningful[0].lstrip())
    if not first_match or first_match.group(1) in NON_TACTICS:
        return []
    first_head = first_match.group(1)
    starts = []
    stack = []
    pairs = {")": "(", "]": "[", "}": "{", "⟩": "⟨"}
    offset = 0
    previous = ""
    pending_blank = None
    for line in lines:
        stripped = line.strip()
        if not stripped:
            if pending_blank is None:
                pending_blank = offset
            offset += len(line)
            continue
        indent = len(line) - len(line.lstrip(" "))
        if indent < base_indent:
            return []
        match = HEAD.match(line.lstrip())
        if (indent == base_indent and not stack and match
                and match.group(1) not in NON_TACTICS
                and not CONTINUATION.search(previous)):
            starts.append(pending_blank if pending_blank is not None else offset)
        pending_blank = None
        for char in line:
            if char in "([{⟨":
                stack.append(char)
            elif char in pairs:
                if not stack or stack.pop() != pairs[char]:
                    return []
        previous = stripped
        offset += len(line)
    if stack:
        return []
    return [(body[:starts[k]], k, len(starts) - k, first_head)
            for k in (1, 2) if len(starts) - k >= 2 and body[:starts[k]].endswith("\n")]


def eligible_prefixes(proof, prompt, token_count, max_prefix_tokens=128,
                      max_prompt_tokens=512, max_fraction=0.4):
    body = proof.split("```", 1)[0]
    boundaries = prefix_boundaries(proof)
    if not boundaries:
        return []
    total_tokens = token_count(body)
    accepted = []
    for prefix, steps, remaining, head in boundaries:
        tokens = token_count(prefix)
        prompt_tokens = token_count(prompt + prefix)
        if (tokens <= max_prefix_tokens and tokens <= max_fraction * total_tokens
                and prompt_tokens <= max_prompt_tokens):
            accepted.append({
                "proof_prefix": prefix, "prefix_steps": steps,
                "remaining_steps": remaining, "initial_tactic_head": head,
                "prefix_tokens": tokens, "source_body_tokens": total_tokens,
                "prompt_tokens": prompt_tokens, "prefix_char_end": len(prefix),
                "prefix_sha256": text_hash(prefix), "source_proof_sha256": text_hash(proof),
                "witness_proof": proof, "witness_sha256": text_hash(proof),
            })
    return accepted


def translated_path(original, bundle=BUNDLE):
    if not original.startswith(OLD_ROOT):
        raise ValueError(f"unrecognized historical source path: {original}")
    relative = Path(original[len(OLD_ROOT):])
    if relative.is_absolute() or ".." in relative.parts:
        raise ValueError("invalid historical relative path")
    return Path(bundle) / relative


def iter_registered_records(log_specs, train_rows, samples_per_theorem, counters):
    """Verify all hashes before reading, and retain only first registered group."""
    for spec in log_specs:
        if sha256(spec["local_path"]) != spec["sha256"]:
            raise ValueError(f"source log checksum mismatch: {spec['local_path']}")
    seen = Counter()
    for spec in log_specs:
        with Path(spec["local_path"]).open() as stream:
            for line_number, line in enumerate(stream, 1):
                record = json.loads(line)
                theorem = record["theorem_name"]
                if theorem not in train_rows:
                    raise ValueError(f"proof outside registered training split: {theorem}")
                row = train_rows[theorem]
                for saved, source in (("theorem_statement", "theorem_statement"),
                                      ("informal_statement", "informal_statement"),
                                      ("context", "src_context")):
                    if record.get(saved) != row[source]:
                        raise ValueError(f"source theorem metadata mismatch: {theorem}/{saved}")
                seen[theorem] += 1
                counters["raw_proposals"] += 1
                if seen[theorem] > samples_per_theorem:
                    counters["padding_excluded"] += 1
                    continue
                counters["registered_proposals"] += 1
                if record.get("correct") is not True:
                    continue
                counters["registered_correct"] += 1
                yield record, {"source_log": str(spec["local_path"]),
                               "source_log_sha256": spec["sha256"],
                               "source_line": line_number,
                               "source_proposal_index": seen[theorem] - 1}
    if set(seen) != set(train_rows) or any(count < samples_per_theorem for count in seen.values()):
        raise ValueError("C0 sources do not cover the complete registered sample")


def choose_routes(candidates, seed):
    """One exact-prefix choice per initial head, then up to two distinct heads."""
    routes = {}
    for theorem, choices in candidates.items():
        by_head = defaultdict(list)
        for candidate in choices.values():
            by_head[candidate["initial_tactic_head"]].append(candidate)
        heads = sorted(by_head, key=lambda head: rank(seed, theorem, head))[:2]
        routes[theorem] = [min(by_head[head], key=lambda c: rank(seed, theorem, c["proof_prefix"]))
                           for head in heads]
    return routes


def stratified_selection(routes, count, seed):
    """Round-robin initial-head strata with hash order; never score model outputs."""
    if len(routes) < count:
        raise ValueError(f"only {len(routes)} eligible theorems; need {count}; criteria unchanged")
    buckets = defaultdict(list)
    for theorem, choices in routes.items():
        buckets[choices[0]["initial_tactic_head"]].append(theorem)
    queues = {head: deque(sorted(values, key=lambda name: rank(seed, name)))
              for head, values in buckets.items()}
    heads = sorted(queues, key=lambda head: rank(seed, "stratum", head))
    selected = []
    while len(selected) < count:
        for head in heads:
            if queues[head]:
                selected.append(queues[head].popleft())
                if len(selected) == count:
                    break
    return selected


def make_panels(bank_rows):
    root = [row.copy() for row in bank_rows if row["condition"] == "root"]
    prefix = [row.copy() for row in bank_rows if row["condition"] == "prefix"]
    root_by_theorem = {row["theorem_full_name"]: row for row in root}
    mixed = []
    matched_root = []
    for candidate in prefix:
        repeated = root_by_theorem[candidate["theorem_full_name"]].copy()
        repeated["pilot_row_id"] += ":paired:" + candidate["prefix_sha256"]
        mixed.extend([repeated, candidate.copy()])
        for replicate in (0, 1):
            matched_root.append({**repeated, "pilot_row_id": repeated["pilot_row_id"] + f":{replicate}"})
    return {"root": matched_root, "prefix": prefix, "mixed": mixed}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("run_dir", type=Path)
    parser.add_argument("--source", type=Path, default=ROOT / "data/mff-lwb-10k-seen.parquet")
    parser.add_argument("--validation", type=Path, default=BUNDLE / "runs/c0-base-20260804-seed42-complete/validation.json")
    parser.add_argument("--model", type=Path, default=BUNDLE / "models/base")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--train-theorems", type=int, default=256)
    parser.add_argument("--diagnostic-theorems", type=int, default=64)
    parser.add_argument("--samples-per-row", type=int, default=32)
    args = parser.parse_args()
    if args.run_dir.exists():
        parser.error("refusing to overwrite existing destination")
    if min(args.train_theorems, args.diagnostic_theorems, args.samples_per_row) <= 0:
        parser.error("panel sizes and proposal count must be positive")
    if sha256(args.source) != SOURCE_SHA256 or sha256(args.validation) != VALIDATION_SHA256:
        parser.error("source dataset or C0 validation differs from frozen registered source")

    import pandas as pd
    from transformers import AutoTokenizer
    from verl.lean.prompts import prompt_fn_deepseek
    from verl.lean.proof_prefix import conditioning_id

    frame = pd.read_parquet(args.source)
    if frame.theorem_full_name.duplicated().any():
        parser.error("duplicate source theorem identity")
    train = frame.loc[frame["split"] == "train"]
    if len(train) != 9655:
        parser.error("unexpected registered train size")
    train_rows = {row["theorem_full_name"]: row for row in train.to_dict("records")}
    validation = json.loads(args.validation.read_text())
    if validation["status"] != "valid" or validation["samples_per_theorem"] != 32:
        parser.error("invalid C0 sample validation")
    specs = [{**spec, "local_path": str(translated_path(spec["path"]))}
             for spec in validation["proof_logs"]]
    tokenizer = AutoTokenizer.from_pretrained(str(args.model), local_files_only=True)
    from functools import lru_cache

    @lru_cache(maxsize=50000)
    def token_count(text):
        return len(tokenizer.encode(text, add_special_tokens=False))

    candidates = defaultdict(dict)
    counters = Counter()
    for record, provenance in iter_registered_records(specs, train_rows, 32, counters):
        theorem = record["theorem_name"]
        prompt = prompt_fn_deepseek(record["theorem_statement"], record["informal_statement"], None, None)
        for candidate in eligible_prefixes(record["proof"], prompt, token_count):
            # Stable first occurrence keeps the exact source verdict auditable.
            candidates[theorem].setdefault(candidate["proof_prefix"], {**candidate, **provenance})
    if counters["padding_excluded"] != validation["padding_proposals_excluded_from_scientific_sample"]:
        parser.error("C0 padding count differs from validation")
    if counters["registered_proposals"] != validation["registered_proposals"]:
        parser.error("registered proposal count differs from validation")
    routes = choose_routes(candidates, args.seed)
    feasibility = {**counters, "eligible_theorems": len(routes),
                   "eligible_exact_prefixes": sum(map(len, candidates.values())),
                   "theorems_with_two_initial_heads": sum(len(value) == 2 for value in routes.values()),
                   "candidate_initial_heads": dict(Counter(c["initial_tactic_head"]
                       for choices in candidates.values() for c in choices.values()))}
    print(json.dumps({"feasibility": feasibility}, sort_keys=True), flush=True)
    total = args.train_theorems + args.diagnostic_theorems
    selected = stratified_selection(routes, total, args.seed)
    # Stratify diagnostics from the selected set rather than taking its tail.
    diagnostic = set(stratified_selection({name: routes[name] for name in selected},
                                          args.diagnostic_theorems, args.seed + 1))
    bank = []
    for theorem in selected:
        row = train_rows[theorem]
        split = "diagnostic" if theorem in diagnostic else "train"
        shared = {**row, "pilot_split": split, "source_dataset_sha256": SOURCE_SHA256,
                  "source_model_revision": MODEL_REVISION,
                  "selection_seed": args.seed, "group_theorem_id": theorem}
        bank.append({**shared, "condition": "root", "proof_prefix": "",
                     "pilot_row_id": theorem + ":root", "prefix_sha256": text_hash(""),
                     "source_log": "", "source_log_sha256": "", "source_line": 0,
                     "source_proposal_index": -1, "source_proof_sha256": "",
                     "witness_proof": None, "witness_sha256": "",
                     "prefix_steps": 0, "remaining_steps": 0, "initial_tactic_head": "root",
                     "prefix_tokens": 0, "source_body_tokens": 0, "prefix_char_end": 0,
                     "prompt_tokens": token_count(prompt_fn_deepseek(
                         row["theorem_statement"], row["informal_statement"], None, None))})
        for candidate in routes[theorem]:
            bank.append({**shared, **candidate, "condition": "prefix",
                         "pilot_row_id": theorem + ":prefix:" + candidate["prefix_sha256"]})
    for row in bank:
        row["prefix_head"] = row["initial_tactic_head"]
        row["prefix_token_count"] = row["prefix_tokens"]
        row["prompt_token_count"] = row["prompt_tokens"]
        row["conditioning_id"] = conditioning_id(row["theorem_statement"], row["src_context"], row["proof_prefix"])
    panels = make_panels([row for row in bank if row["pilot_split"] == "train"])
    panels = {"train_" + name: rows for name, rows in panels.items()}
    panels["diagnostic"] = [row for row in bank if row["pilot_split"] == "diagnostic"]
    args.run_dir.mkdir(parents=True, exist_ok=False)
    # JSON conversion through pandas preserves original nested prompt/extra_info.
    pd.DataFrame(bank).to_json(args.run_dir / "selection_bank.jsonl", orient="records", lines=True,
                               force_ascii=False)
    witnesses = {}
    for row in bank:
        if row["condition"] == "prefix":
            key = (row["theorem_full_name"], row["witness_sha256"])
            witnesses.setdefault(key, {field: row[field] for field in (
                "theorem_full_name", "theorem_statement", "src_context", "informal_statement",
                "witness_proof", "witness_sha256", "source_log", "source_log_sha256", "source_line")})
    (args.run_dir / "witnesses.jsonl").write_text("".join(json.dumps(row, ensure_ascii=False) + "\n"
                                                       for row in witnesses.values()))
    for name, rows in panels.items():
        pd.DataFrame(rows).to_parquet(args.run_dir / f"{name}.parquet", index=False)
    histories = []
    for spec in specs:
        metadata = Path(spec["local_path"]).parents[2] / "RUN_METADATA.md"
        histories.append({"path": str(metadata), "sha256": sha256(metadata) if metadata.exists() else None})
    model_files = {str(path.relative_to(args.model)): sha256(path)
                   for path in sorted(args.model.glob("*.json"))}
    manifest = {
        "status": "prepared_unscored_requires_review_before_inference", "schema_version": 1,
        "model": MODEL, "model_revision": MODEL_REVISION, "model_path": str(args.model.resolve()),
        "model_configuration_and_tokenizer_sha256": model_files,
        "script_sha256": sha256(__file__),
        "git_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
        "git_status": subprocess.check_output(["git", "status", "--short"], cwd=ROOT, text=True).strip(),
        "source_dataset": {"path": str(args.source.resolve()), "sha256": SOURCE_SHA256},
        "c0_validation": {"path": str(args.validation.resolve()), "sha256": VALIDATION_SHA256},
        "source_logs": specs, "source_run_histories": histories, "feasibility": feasibility,
        "tasks": [{field: row[field] for field in (
            "pilot_row_id", "pilot_split", "condition", "theorem_full_name", "conditioning_id",
            "prefix_sha256", "prefix_head", "prefix_token_count", "prompt_token_count",
            "source_log_sha256", "source_line", "witness_sha256")}
            | {"screen_samples": 32 if row["pilot_split"] == "diagnostic" else
                                  (16 if row["condition"] == "prefix" else 0)} for row in bank],
        "selection": {"seed": args.seed, "train_theorems": args.train_theorems,
                      "diagnostic_theorems": args.diagnostic_theorems,
                      "max_prefixes_per_theorem": 2, "distinct_route_definition": "initial_tactic_head",
                      "prefix_steps": [1, 2], "minimum_remaining_steps": 2,
                      "max_prefix_tokens": 128, "max_prefix_fraction": 0.4,
                      "max_prompt_tokens": 512, "tokenizer_add_special_tokens": False,
                      "stratification": "round_robin_initial_head_then_sha256_order",
                      "diagnostic_seed": args.seed + 1,
                      "no_fresh_scores_used": True, "original_train_split_only": True,
                      "train_theorem_ids": [t for t in selected if t not in diagnostic],
                      "diagnostic_theorem_ids": [t for t in selected if t in diagnostic]},
        "budget": {"new_proposals_so_far": 0, "new_verifications_so_far": 0,
                   "samples_per_row_planned": args.samples_per_row,
                   "panels": {name: {"rows": len(rows), "proposals_per_single_pass": len(rows) * args.samples_per_row}
                              for name, rows in panels.items()},
                   "training_schedule": "not yet authorized by a frozen experiment design",
                   "historical_c0_generated_verified": validation["raw_generated_and_verified_proposals"]},
        "files": {path.name: sha256(path) for path in sorted(args.run_dir.iterdir())},
        "interpretation": "Prefixes expose parts of historically correct training proofs; diagnostic is held out from pilot training only, not untouched benchmark/OOD data. Initial tactic heads are operational routes, not semantic strategies.",
    }
    (args.run_dir / "manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"output": str(args.run_dir.resolve()), "rows": {name: len(rows) for name, rows in panels.items()}}, sort_keys=True))


if __name__ == "__main__":
    main()
