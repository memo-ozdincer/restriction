#!/usr/bin/env python3
"""Check each frozen authored transfer witness through the production wrapper.

CPU-only instrument validation: no generation, training, task replacement, or
edits to the frozen panel. Uses the same two operational verifier patches as
the pending screen. Run only when no other long-lived REPL is active on this
host: the upstream scheduler has a process-name-based timeout monitor.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[2]
PANEL_SHA256 = "83ad8c87e356768e550839cc742a62c171558e312fbb92226caceaba6b01c15d"
SOURCE_VERIFIER_SHA256 = "ec9c2e9b5dae10634fd2661ca3ee7fb589b11d04cb471a47104c6eb9eea52532"
STAGED_VERIFIER_SHA256 = "d452842a8816e19f60c79a4cf4b7ddfa4fd026c44cd8e9e3d946bd3405a3f573"


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def digest(text):
    return hashlib.sha256(text.encode()).hexdigest()


def load_panel(panel):
    if sha(panel / "manifest.json") != PANEL_SHA256:
        raise ValueError("not the frozen transfer panel")
    manifest = json.loads((panel / "manifest.json").read_text())
    if manifest["training_allowed"] is not False:
        raise ValueError("transfer instrument must remain test-only")
    for name in ("tasks.jsonl", "witnesses.jsonl"):
        if sha(panel / name) != manifest["files"][name]:
            raise ValueError(f"changed {name}")
    tasks = [json.loads(line) for line in (panel / "tasks.jsonl").read_text().splitlines()]
    witnesses = [json.loads(line) for line in (panel / "witnesses.jsonl").read_text().splitlines()]
    if len(tasks) != 16 or len(witnesses) != 16:
        raise ValueError("expected exactly sixteen authored tasks and witnesses")
    by_id = {row["task_id"]: row for row in witnesses}
    if len(by_id) != 16 or set(by_id) != {row["task_id"] for row in tasks}:
        raise ValueError("duplicate or mismatched task identities")
    proofs = []
    for row in tasks:
        witness = by_id[row["task_id"]]
        if (row["proof_prefix"] or row["src_context"] or
                digest(row["theorem_statement"]) != row["statement_sha256"] or
                witness["statement_sha256"] != row["statement_sha256"] or
                digest(witness["witness"]) != witness["witness_sha256"]):
            raise ValueError(f"invalid frozen witness: {row['task_id']}")
        proofs.append(witness["witness"] + "\n```\n")
    return tasks, proofs


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bundle", type=Path, required=True)
    parser.add_argument("--panel", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--staged-verifier", type=Path, required=True)
    args = parser.parse_args()
    bundle, panel, output, staged = [path.resolve() for path in
        (args.bundle, args.panel, args.output, args.staged_verifier)]
    tasks, proofs = load_panel(panel)
    source = bundle / "verifier/DeepSeek-Prover-V1.5"
    if sha(source / "prover/lean/verifier.py") != SOURCE_VERIFIER_SHA256:
        raise ValueError("source verifier changed")
    if output.exists() or staged.exists():
        raise ValueError("refusing an existing output or staging directory")
    output.mkdir(parents=True)
    started = time.monotonic()
    env = os.environ.copy()
    env.update(ELAN_HOME=str(bundle / "lean/elan"), DEEPSEEK_PROVER_ROOT=str(staged),
               DEEPSEEK_VERIFIER_MEMORY_LIMIT_GB="10", PYTHONPATH=str(ROOT),
               PYTHONDONTWRITEBYTECODE="1")
    stage_script = ROOT / "scripts/project/stage_deepseek_verifier.sh"
    patch = ROOT / "scripts/project/patches/benchmark_lake_path.patch"
    command = ["bash", str(stage_script), str(source), str(staged)]
    (output / "staging_command.json").write_text(json.dumps(command) + "\n")
    with (output / "staging.log").open("x") as log:
        subprocess.run(command, env=env, stdout=log, stderr=subprocess.STDOUT,
                       check=True, timeout=1200)
    with patch.open("rb") as source_patch, (output / "lake_path_patch.log").open("x") as log:
        subprocess.run(["patch", "-d", str(staged), "-p1"], stdin=source_patch,
                       stdout=log, stderr=subprocess.STDOUT, check=True, timeout=60)
    if sha(staged / "prover/lean/verifier.py") != STAGED_VERIFIER_SHA256:
        raise ValueError("staged verifier differs from the screen verifier")
    os.environ.update({key: env[key] for key in
        ("ELAN_HOME", "DEEPSEEK_PROVER_ROOT", "DEEPSEEK_VERIFIER_MEMORY_LIMIT_GB")})
    sys.path.insert(0, str(ROOT))
    from verl.lean.verifier import verify_with_deepseek_verifier
    # Upstream verify_lean4_file supplies cwd="mathlib4/" itself.
    os.chdir(staged)
    # Each problem is a separate fresh REPL invocation. This catches accidental
    # dependence on another task's declaration in the earlier combined file.
    statements = [row["theorem_statement"] for row in tasks]
    statements.extend([
        "theorem contract_atomic_row_shear (a b c d k : Int) :\n"
        "    (a+k*c)*d-(b+k*d)*c = a*d-b*c := by\n",
        "theorem transfer_negative_sorry : False := by\n",
    ])
    proofs.extend(["  ring\n```\n", "  sorry\n```\n"])
    results = verify_with_deepseek_verifier(proofs, statements, [""] * 18,
                                          max_workers=1, penalize_extra_text=True)
    if len(results) != 18 or any(len(r["candidate_results"]) != 1 for r in results):
        raise ValueError("production wrapper returned wrong counts")
    records = [{"task_id": row["task_id"], **result["candidate_results"][0]}
               for row, result in zip(tasks + [{"task_id": "contract_atomic_row_shear"},
                                               {"task_id": "negative_sorry"}], results)]
    valid = all(r["verdict"] is True and r["lean_complete"] is True and
                r["failure_class"] is None for r in records[:17])
    negative = records[-1]
    valid = valid and negative["verdict"] is False and negative["failure_class"] == "lean_rejected"
    report = {
        "status": "passed" if valid else "failed", "model_inference_performed": False,
        "training_allowed": False, "authored_witnesses": 16,
        "atomic_contract_agreement_checks": 1, "negative_controls": 1,
        "physical_lean_calls": 18, "workers": 1, "elapsed_seconds": time.monotonic() - started,
        "panel": str(panel), "panel_manifest_sha256": PANEL_SHA256,
        "source_verifier_sha256": SOURCE_VERIFIER_SHA256,
        "staged_verifier_sha256": STAGED_VERIFIER_SHA256,
        "source_files": {str(path.relative_to(ROOT)): sha(path) for path in
                         (Path(__file__).resolve(), stage_script, patch, ROOT / "verl/lean/verifier.py")},
        "staged_verifier": str(staged), "records": records,
        "scope": "Independent authored-witness checks through unchanged production correctness; not model results.",
    }
    (output / "verification.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(json.dumps({key: report[key] for key in ("status", "physical_lean_calls", "elapsed_seconds")}))
    if not valid:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
