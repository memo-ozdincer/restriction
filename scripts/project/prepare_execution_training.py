#!/usr/bin/env python3
"""Freeze the conditional training comparison after an authenticated base gate.

This command does CPU preparation only. It does not launch training or submit jobs.
The gate and all runtime evidence are rechecked; a hand-written advance flag is
not authorization to manufacture a training panel.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from copy import deepcopy
import json
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.project import analyze_execution_pilot as analysis
from scripts.project import run_execution_screen as screen
from scripts.project.prepare_execution_pilot import rank

SCREEN_COMMIT = "57b2d3013e6888dee4a4ad7520252ae4c47791e2"
PANEL_SHA256 = "c5513992dc40cda4f62896c2b53b5c4509f2d5934b245b2477da71b2a17fc0b8"
WORKSPACE_JOB = 1176227
SOURCE_VERIFIER_SHA256 = "ec9c2e9b5dae10634fd2661ca3ee7fb589b11d04cb471a47104c6eb9eea52532"
STAGED_VERIFIER_SHA256 = "d452842a8816e19f60c79a4cf4b7ddfa4fd026c44cd8e9e3d946bd3405a3f573"
SEED = 42
PAIRS = 512
ROWS = 1024
SAMPLES = 32
STEPS = 64
BUDGET = {"rows_per_arm": ROWS, "prefix_rows_practice": PAIRS, "root_rows_practice": PAIRS,
          "samples_per_row": SAMPLES, "proposals_per_arm": ROWS * SAMPLES,
          "problem_batch_size": 16, "batches_per_arm": STEPS, "padding_permitted": False,
          "maximum_seconds_per_arm": 21600}
require = analysis.require
sha256 = screen.sha256
write_json = screen.write_json


def read_json(path):
    return json.loads(Path(path).read_text())


def authenticate_runtime(run, panel, manifest, bank, source_files, bundle):
    """Authenticate runtime certificates against pinned inputs and actual logs."""
    run, panel, bundle = Path(run).resolve(), Path(panel).resolve(), Path(bundle).resolve()
    require(not (run / "failure.json").exists(), "screen has a failure certificate")
    certificates = {}

    def certificate(relative):
        path = run / relative
        value = read_json(path)
        certificates[str(path)] = sha256(path)
        return value

    provenance = certificate("provenance.json")
    require(provenance.get("source_commit") == SCREEN_COMMIT, "screen source commit changed")
    require(provenance.get("source_files_sha256") == source_files, "screen runtime source inventory changed")
    require(provenance.get("panel") == str(panel) and provenance.get("panel_manifest_sha256") == PANEL_SHA256,
            "screen used another frozen panel")
    require(provenance.get("model_revision") == screen.MODEL_REVISION and
            Path(provenance.get("model_path", "")).resolve() == (bundle / "models/base").resolve() and
            provenance.get("model_weight_sha256") == screen.BASE_MODEL_WEIGHTS,
            "screen did not attest the pristine base weights")
    require(provenance.get("seed") == SEED and provenance.get("maximum_seconds") == 21600,
            "screen seed or time budget changed")
    hostname = provenance["hostname"]
    screen.validate_allocation(WORKSPACE_JOB, provenance["job_info"], hostname,
                               provenance["cgroup"], [hostname])
    node_list = dict(re.findall(r"(?:^|\s)(\w+)=([^\s]+)", provenance["job_info"])).get("NodeList")
    require(node_list == hostname.split(".")[0], "recorded screen node differs from allocation")
    for name in ("staging", "preflight", "witness"):
        status = certificate(name + "_status.json")
        require(status.get("returncode") == 0 and status.get("timed_out") is False,
                f"screen {name} did not complete")
    verifier = certificate("verifier_provenance.json")
    source_verifier = bundle / "verifier/DeepSeek-Prover-V1.5/prover/lean/verifier.py"
    require(verifier.get("source_verifier_sha256") == sha256(source_verifier) == SOURCE_VERIFIER_SHA256,
            "verifier source changed")
    require(verifier.get("staged_verifier_sha256") == STAGED_VERIFIER_SHA256, "staged screen verifier changed")
    for key, relative in (("lake_path_patch_sha256", "scripts/project/patches/benchmark_lake_path.patch"),
                          ("result_handoff_patch_sha256", "scripts/project/patches/deepseek_verifier_compact_result.patch")):
        require(verifier.get(key) == source_files[relative], f"screen verifier patch changed: {key}")
    require(verifier.get("lean_toolchain") ==
            (bundle / "verifier/DeepSeek-Prover-V1.5/mathlib4/lean-toolchain").read_text().strip(),
            "screen Lean toolchain changed")
    checks = certificate("witness_checks.json")
    expected = {key for key, row in bank.items() if row["proof_prefix"]}
    checked = checks.get("checked", [])
    require(checks.get("complete") is True and checks.get("invalid_tasks") == [],
            "fresh witness certificate failed")
    require(len(checked) == len(expected) and {r["pilot_row_id"] for r in checked} == expected,
            "fresh witness certificate omitted or duplicated a task")
    require(checks.get("physical_lean_calls") == checks.get("submitted_candidates") == 2 * len(expected),
            "fresh witness accounting mismatch")
    for row in checked:
        for field, verdict, failure in (("witness", True, None), ("prefix_only", False, "lean_rejected")):
            record = row[field]
            require(record.get("verdict") is verdict and record.get("lean_complete") is verdict and
                    record.get("failure_class") == failure and not record.get("timed_out") and
                    not record.get("verifier_error"), f"invalid fresh {field}: {row['pilot_row_id']}")
    generation = certificate("generation_complete.json")
    require(generation.get("status") == "generation_complete_pending_independent_analysis" and
            generation.get("trained_samples") == 0 and
            0 < generation.get("elapsed_seconds", 0) <= 21600,
            "screen generation completion certificate invalid")
    logs = {}
    for label, filename, samples in (("practice", "train_prefix.parquet", 16),
                                      ("diagnostic", "diagnostic.parquet", 32)):
        destination = run / label
        count = sum(analysis.screen_samples(row) == samples and
                    row["pilot_split"] == ("train" if label == "practice" else "diagnostic")
                    for row in bank.values())
        steps = (count + 15) // 16
        status = certificate(label + "/process_status.json")
        log = destination / "artifacts/proofs" / f"global_step_{steps}.jsonl"
        require(status.get("completion_candidate") is True and status.get("timed_out") is False and
                status.get("expected_steps") == steps and status.get("registered_rows") == count and
                status.get("registered_proposals") == count * samples and
                Path(status.get("proof_log", "")).resolve() == log and
                status.get("proof_log_sha256") == sha256(log), f"{label} completion/proof certificate changed")
        text = (destination / "run.log").read_text(errors="replace")
        require("[TRAINING] Training finished" in text and
                (status.get("returncode") == 0 or "Exception: Stop" in text), f"{label} finish marker missing")
        require(sha256(destination / "train.parquet") == sha256(panel / filename),
                f"{label} runtime dataset changed")
        command = certificate(label + "/command.json")
        expected_command = screen.command_for_panel(destination, bundle / "models/base", samples)
        require(command[1:] == expected_command[1:] and
                Path(command[0]).resolve() == (bundle / "environment/venv/bin/python").resolve(),
                f"{label} runtime command changed")
        for path in (destination / "run.log", destination / "train.parquet", log):
            certificates[str(path)] = sha256(path)
        logs[label] = log
    return logs, certificates


def authenticate_screen(bundle, panel, screen_run, screen_source):
    """Recompute the saved analysis; source hashes and certificates must agree."""
    bundle, panel, screen_run = Path(bundle).resolve(), Path(panel).resolve(), Path(screen_run).resolve()
    source_files = screen.validate_snapshot(screen_source, bundle / "repository", SCREEN_COMMIT)
    screen.validate_panel(panel, PANEL_SHA256, bundle)
    manifest, bank, verified = analysis.load_manifest(panel / "manifest.json")
    logs, certificates = authenticate_runtime(screen_run, panel, manifest, bank, source_files, bundle)
    records, proof_logs = [], []
    for split, label in (("train", "practice"), ("diagnostic", "diagnostic")):
        path = logs[label]
        rows = list(analysis.read_jsonl(path))
        require(all(row.get("pilot_split") == split for row in rows), f"wrong panel in {path}")
        records.extend(rows)
        proof_logs.append({"split": split, "path": str(path), "sha256": sha256(path), "records": len(rows)})
    computed = analysis.summarize(bank, records)
    computed["provenance"] = {
        "manifest": str(panel / "manifest.json"), "manifest_sha256": sha256(panel / "manifest.json"),
        "registered_model_revision": manifest["model_revision"], "proof_logs": proof_logs,
        "verified_source_sha256": verified,
        "runtime_attestation": "requires launcher completion, fresh-prefix validation, and model/config provenance; exact record counts alone do not certify these",
    }
    saved = read_json(screen_run / "analysis.json")
    require(saved == computed, "saved screen analysis differs from authenticated raw outcomes")
    require(computed["gate"].get("advance") is True, "base screen gate did not advance")
    certificates[str(screen_run / "analysis.json")] = sha256(screen_run / "analysis.json")
    return bank, computed, certificates


def eligible_rows(bank, result):
    """Recompute practice eligibility independently; diagnostics cannot select rows."""
    require(result["gate"].get("advance") is True, "base screen gate did not advance")
    require(result["gate"].get("diagnostics_used_for_gate") is False, "diagnostic selection forbidden")
    practice = {key for key, row in bank.items() if row["pilot_split"] == "train" and row["proof_prefix"]}
    seen, eligible, by_head = set(), [], defaultdict(set)
    for task in result["tasks"]:
        key = task["pilot_row_id"]
        require(key in bank and key not in seen, "unknown or duplicate analysis task")
        seen.add(key)
        row = bank[key]
        if row["pilot_split"] != "train":
            continue
        require(key in practice and task["split"] == "train" and task["condition"] == "prefix" and
                task["proposals"] == 16 and type(task["correct"]) is int and 0 <= task["correct"] <= 16,
                "invalid practice eligibility evidence")
        require(task["theorem"] == row["theorem_full_name"] and
                task["prefix_sha256"] == row["prefix_sha256"] and
                task["conditioning_id"] == row["conditioning_id"] and
                task["initial_tactic_head"] == row["initial_tactic_head"], "practice identity changed")
        if 1 <= task["correct"] <= 8:
            eligible.append(key)
            by_head[row["initial_tactic_head"]].add(row["theorem_full_name"])
    require(practice <= seen, "practice tasks omitted from analysis")
    theorems = {bank[key]["theorem_full_name"] for key in eligible}
    qualifying = sorted(head for head, names in by_head.items() if len(names) >= 8)
    require(len(theorems) >= 48 and len(qualifying) >= 4, "recomputed practice gate did not advance")
    gate = result["gate"]
    require(sorted(eligible) == sorted(gate["eligible_prefix_rows"]) and
            sorted(theorems) == gate["eligible_theorems"] and qualifying == gate["qualifying_heads"],
            "eligible rows differ from frozen practice gate")
    return eligible


def build_schedule(bank, result):
    """512 balanced prefix/root pairs, then identical row ordering in both arms."""
    eligible = eligible_rows(bank, result)
    by_theorem = defaultdict(list)
    roots = {}
    for key, row in bank.items():
        if row["pilot_split"] == "train" and not row["proof_prefix"]:
            require(row["theorem_full_name"] not in roots, "duplicate practice root")
            roots[row["theorem_full_name"]] = key
    for key in eligible:
        by_theorem[bank[key]["theorem_full_name"]].append(key)
    theorems = sorted(by_theorem, key=lambda name: rank(SEED, "theorem", name))
    require(len(theorems) <= PAIRS, "more eligible theorems than prefix slots")
    pairs = []
    quotas = {}
    for index, theorem in enumerate(theorems):
        require(theorem in roots, "eligible theorem lacks its frozen root")
        quota = PAIRS // len(theorems) + (index < PAIRS % len(theorems))
        routes = sorted(by_theorem[theorem], key=lambda key: rank(SEED, "route", theorem, key))
        quotas[theorem] = {"prefix_rows": quota, "root_rows_practice": quota,
                           "total_rows_per_arm": 2 * quota,
                           "prefix_routes": dict(Counter(routes[i % len(routes)] for i in range(quota)))}
        for index_in_theorem in range(quota):
            pairs.append((theorem, routes[index_in_theorem % len(routes)], index_in_theorem))
    pairs.sort(key=lambda item: rank(SEED, "pair-order", *item))
    arms = {"root": [], "practice": []}
    for pair_index, (theorem, route, repeat) in enumerate(pairs):
        for half in (0, 1):
            slot = pair_index * 2 + half
            for arm in arms:
                source_id = route if arm == "practice" and half else roots[theorem]
                row = deepcopy(bank[source_id])
                row.update(pilot_row_id=f"execution-training:{arm}:{slot:04d}", pilot_padding=False,
                           source_pilot_row_id=source_id, training_arm=arm, training_slot=slot,
                           matched_route_id=route, route_repeat=repeat)
                arms[arm].append(row)
    require(len(arms["root"]) == len(arms["practice"]) == ROWS, "training row budget mismatch")
    require(sum(bool(r["proof_prefix"]) for r in arms["practice"]) == PAIRS, "practice split mismatch")
    require(not any(r["proof_prefix"] for r in arms["root"]), "root arm contains a prefix")
    for left, right in zip(arms["root"], arms["practice"]):
        require(left["theorem_full_name"] == right["theorem_full_name"], "theorem slot mismatch")
    return arms, quotas


def prepare(args):
    output = args.output.resolve()
    require(not output.exists(), "refusing existing training panel")
    bank, result, certificates = authenticate_screen(args.bundle, args.panel, args.screen_run, args.screen_source)
    arms, quotas = build_schedule(bank, result)
    import pandas as pd
    output.mkdir(parents=True, exist_ok=False)
    for arm, rows in arms.items():
        (output / arm).mkdir()
        (output / arm / "rows.jsonl").write_text("".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows))
        pd.DataFrame(rows).to_parquet(output / arm / "train.parquet", index=False)
    files = {str(path.relative_to(output)): sha256(path) for path in output.rglob("*") if path.is_file()}
    manifest = {"schema_version": 1, "status": "prepared_requires_manual_allocated_node_launch",
        "screen_commit": SCREEN_COMMIT, "panel_manifest_sha256": PANEL_SHA256,
        "model_revision": screen.MODEL_REVISION, "model_weight_sha256": screen.BASE_MODEL_WEIGHTS,
        "panel": str(args.panel.resolve()), "screen_run": str(args.screen_run.resolve()),
        "screen_source": str(args.screen_source.resolve()), "runtime_certificates_sha256": certificates,
        "seed": SEED, "gate": result["gate"], "diagnostics_used_for_selection": False,
        "theorem_quotas": quotas, "files": files,
        "budget": BUDGET,
        "quota_order": "sha256([42, theorem, id]); balanced theorems, then hashed routes within theorem",
        "script_sha256": sha256(__file__),
        "git_commit": subprocess.check_output(["git", "-C", str(ROOT), "rev-parse", "HEAD"], text=True).strip(),
        "git_status": subprocess.check_output(["git", "-C", str(ROOT), "status", "--short"], text=True).strip(),
        "resume": "unsupported; every arm starts from pristine base; checkpoints are weights only"}
    write_json(output / "manifest.json", manifest)
    return manifest


def validate_training_panel(path, expected_digest, bundle):
    """Reauthenticate source screen and independently reproduce every training slot."""
    path = Path(path).resolve()
    require(sha256(path / "manifest.json") == expected_digest, "training manifest changed")
    manifest = read_json(path / "manifest.json")
    require(manifest["schema_version"] == 1 and manifest["seed"] == SEED and
            manifest["panel_manifest_sha256"] == PANEL_SHA256 and manifest["screen_commit"] == SCREEN_COMMIT,
            "unsupported training panel provenance")
    require(manifest.get("diagnostics_used_for_selection") is False, "diagnostic selection forbidden")
    require(manifest.get("budget") == BUDGET and manifest.get("model_revision") == screen.MODEL_REVISION and
            manifest.get("model_weight_sha256") == screen.BASE_MODEL_WEIGHTS, "training budget or base model changed")
    expected_files = {f"{arm}/{name}" for arm in ("root", "practice") for name in ("rows.jsonl", "train.parquet")}
    require(set(manifest["files"]) == expected_files, "unexpected training panel files")
    for relative, digest in manifest["files"].items():
        require(sha256(path / relative) == digest, f"training panel checksum mismatch: {relative}")
    bank, result, certificates = authenticate_screen(bundle, manifest["panel"], manifest["screen_run"], manifest["screen_source"])
    require(manifest["runtime_certificates_sha256"] == certificates and manifest["gate"] == result["gate"],
            "training panel source evidence changed")
    arms, quotas = build_schedule(bank, result)
    require(manifest["theorem_quotas"] == quotas, "training quotas changed")
    import pandas as pd
    for arm, rows in arms.items():
        saved = list(analysis.read_jsonl(path / arm / "rows.jsonl"))
        require(saved == rows, f"training rows differ from reproducible schedule: {arm}")
        # A JSON normalization preserves nested array/struct parquet values.
        parquet_rows = json.loads(pd.read_parquet(path / arm / "train.parquet").to_json(orient="records"))
        expected_rows = json.loads(pd.DataFrame(rows).to_json(orient="records"))
        require(parquet_rows == expected_rows, f"training parquet differs from frozen rows: {arm}")
    return manifest, arms


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for flag in ("bundle", "panel", "screen-run", "screen-source", "output"):
        parser.add_argument("--" + flag, required=True, type=Path)
    args = parser.parse_args()
    result = prepare(args)
    print(json.dumps({"output": str(args.output.resolve()), "manifest_sha256": sha256(args.output / "manifest.json"),
                      "theorems": len(result["theorem_quotas"]), "rows_per_arm": ROWS}))


if __name__ == "__main__":
    main()
