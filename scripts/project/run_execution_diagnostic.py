#!/usr/bin/env python3
"""Evaluate ONE certified step-64 actor on the frozen diagnostic panel.

Manual allocated-node execution only: no scheduling, training, resume, or retries.
The base-screen command is reused verbatim apart from paths to this run and its
certified actor. Observational telemetry independently attests sample-only use.
"""
from __future__ import annotations

import argparse
from collections import defaultdict
import hashlib
import json
import math
import os
from pathlib import Path
import re
import socket
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.project import analyze_execution_pilot as analysis
from scripts.project import prepare_execution_training as prepare
from scripts.project import run_execution_screen as screen
from scripts.project import run_execution_training as training
from scripts.project.execution_training_telemetry import validate_actor_checkpoint
from verl.lean.telemetry import telemetry_identity

require, sha256, write_json = prepare.require, screen.sha256, screen.write_json
ROWS, SAMPLES, STEPS = 168, 32, 11
MAXIMUM_SECONDS = 10800
FINALIZATION_SECONDS = 300


def expected_runtime_config(run, model):
    from omegaconf import OmegaConf
    overrides = [item.lstrip("+") for item in screen.command_for_panel(run, model, SAMPLES)[3:]
                 if not item.startswith("hydra.")]
    config = OmegaConf.merge(OmegaConf.load(ROOT / "verl/trainer/config/lean_trainer.yaml"),
                             OmegaConf.from_dotlist(overrides))
    config.actor_rollout_ref.actor.optim.total_training_steps = STEPS
    config.critic.optim.total_training_steps = STEPS
    return OmegaConf.to_container(config, resolve=True)


def authenticate_training(run, panel, manifest_digest, bundle, arm, commit, pinned, rows):
    """A saved success flag is insufficient: recertify logs, updates and weights."""
    run, panel, bundle = Path(run).resolve(), Path(panel).resolve(), Path(bundle).resolve()
    require(not (run / "failure.json").exists(), "training run has a failure certificate")
    saved = prepare.read_json(run / "training_complete.json")
    require(saved.get("schema_version") == 1 and saved.get("evaluation_eligible") is True and
            saved.get("status") == "complete_eligible_for_diagnostic_evaluation" and
            saved.get("global_steps") == prepare.STEPS and saved.get("arm") == arm and
            saved.get("source_commit") == commit and
            saved.get("training_manifest_sha256") == manifest_digest,
            "training certificate is partial or belongs to another arm/source/panel")
    provenance = prepare.read_json(run / "provenance.json")
    require(provenance.get("source_commit") == commit and provenance.get("source_files_sha256") == pinned,
            "training source inventory differs from pinned evaluation source")
    require(provenance.get("training_panel") == str(panel) and
            provenance.get("training_manifest_sha256") == manifest_digest and
            provenance.get("panel_manifest_sha256") == prepare.PANEL_SHA256 and
            provenance.get("model_path") == str(bundle / "models/base") and
            provenance.get("model_revision") == screen.MODEL_REVISION and
            provenance.get("model_weight_sha256") == screen.BASE_MODEL_WEIGHTS and
            provenance.get("arm") == arm and provenance.get("seed") == prepare.SEED,
            "training input/model provenance changed")
    hostname = provenance["hostname"]
    screen.validate_allocation(prepare.WORKSPACE_JOB, provenance["job_info"], hostname,
                               provenance["cgroup"], [hostname])
    require(provenance.get("maximum_seconds") == training.MAXIMUM_SECONDS,
            "training time budget changed")
    for name in ("staging", "preflight"):
        status = prepare.read_json(run / (name + "_status.json"))
        require(status.get("returncode") == 0 and status.get("timed_out") is False,
                f"training {name} did not complete")
    verifier = prepare.read_json(run / "verifier_provenance.json")
    validate_verifier_provenance(verifier, pinned, bundle)
    require(sha256(run / "train.parquet") == sha256(panel / arm / "train.parquet"),
            "training runtime dataset changed")
    actual = training.certify_completion(run, rows, prepare.read_json(run / "process_status.json"),
        bundle / "models/base", arm, manifest_digest, commit, persist=False)
    require(saved == actual, "saved training certificate differs from authenticated completed run")
    return saved


def validate_verifier_provenance(value, pinned, bundle):
    require(value.get("source_verifier_sha256") == prepare.SOURCE_VERIFIER_SHA256 and
            value.get("staged_verifier_sha256") == prepare.STAGED_VERIFIER_SHA256,
            "verifier differs from authenticated base screen")
    for key, filename in (("lake_path_patch_sha256", "benchmark_lake_path.patch"),
                          ("result_handoff_patch_sha256", "deepseek_verifier_compact_result.patch")):
        require(value.get(key) == pinned["scripts/project/patches/" + filename], "verifier patch changed")
    require(value.get("lean_toolchain") ==
            (Path(bundle) / "verifier/DeepSeek-Prover-V1.5/mathlib4/lean-toolchain").read_text().strip(),
            "Lean toolchain changed")


def diagnostic_bank(panel):
    manifest = prepare.read_json(Path(panel) / "manifest.json")
    bank = analysis.validate_bank(list(analysis.read_jsonl(Path(panel) / "selection_bank.jsonl")), manifest)
    bank = {key: row for key, row in bank.items() if row["pilot_split"] == "diagnostic"}
    require(len(bank) == ROWS and sum(not row["proof_prefix"] for row in bank.values()) == 64,
            "frozen diagnostic panel must contain 64 roots and 104 prefixes")
    return bank


def authenticate_evaluation_telemetry(run, model, commit, verifier):
    """Require the resolved runtime and every batch, and reject all update events."""
    paths = sorted((Path(run) / "telemetry").glob("*.jsonl"))
    require(len(paths) == 1 and not paths[0].is_symlink(),
            "evaluation must have exactly one driver telemetry file and no actor updates")
    records = list(analysis.read_jsonl(paths[0]))
    require(len(records) == STEPS + 1, "missing or extra evaluation telemetry events")
    require(all(row.get("schema_version") == 1 and row.get("role") == "driver" for row in records),
            "evaluation telemetry contains a non-driver event")
    require(len({(r.get("hostname"), r.get("pid"), r.get("rank")) for r in records}) == 1,
            "evaluation driver restarted or changed identity")
    require([r.get("sequence") for r in records] == list(range(1, STEPS + 2)),
            "evaluation telemetry sequence changed")
    runtime = records[0]
    require(runtime.get("event") == "runtime_config" and
            runtime.get("resolved_config") == expected_runtime_config(run, model),
            "evaluation resolved configuration differs from the frozen sample-only command")
    environment = {"git_commit": commit, "model_revision": screen.MODEL_REVISION,
                   "verifier_root": str(verifier), "verifier_memory_limit_gb": "32"}
    require(runtime.get("environment") == environment, "evaluation runtime environment changed")
    config_hash, environment_hash = telemetry_identity(
        json.dumps(runtime["resolved_config"], sort_keys=True, separators=(",", ":")), environment)
    require(runtime.get("config_hash") == config_hash and runtime.get("environment_hash") == environment_hash,
            "evaluation runtime identity hash mismatch")
    for step, row in enumerate(records[1:], 1):
        groups = 16 if step < STEPS else 8
        require(row.get("event") == "rollout_batch" and row.get("step") == step and
                row.get("groups") == groups and row.get("samples_per_group") == SAMPLES and
                row.get("admitted_groups") == groups and row.get("skipped_groups") == 0,
                "evaluation batch changed or an optimizer/checkpoint event appeared")
    return {"config_hash": config_hash, "environment_hash": environment_hash,
            "resolved_config": runtime["resolved_config"], "environment": environment,
            "files_sha256": {path.name: sha256(path) for path in paths},
            "rollout_batches": STEPS, "actor_updates": 0, "trained_samples": 0}


def certify_evaluation(run, bank, certificate, panel, commit, verifier, result):
    """Scientific counts and runtime/model authentication are separate checks."""
    run, panel = Path(run).resolve(), Path(panel).resolve()
    require(not (run / "failure.json").exists(), "evaluation has a failure certificate")
    log_text = (run / "run.log").read_text(errors="replace")
    require(result.get("timed_out") is False and "[TRAINING] Training finished" in log_text and
            (result.get("returncode") == 0 or "Exception: Stop" in log_text),
            "evaluation process did not complete")
    require(result.get("expected_steps") == STEPS and result.get("registered_rows") == ROWS and
            result.get("registered_proposals") == ROWS * SAMPLES and
            0 < result.get("elapsed_evaluation_seconds", 0) <= MAXIMUM_SECONDS,
            "evaluation process budget differs from registration")
    require(prepare.read_json(run / "process_status.json") == result, "evaluation process status changed")
    model = Path(certificate["checkpoint"])
    command = prepare.read_json(run / "command.json")
    require(command == screen.command_for_panel(run, model, SAMPLES), "evaluation command changed")
    require(sha256(run / "train.parquet") == sha256(panel / "diagnostic.parquet"),
            "evaluation dataset changed")
    telemetry = authenticate_evaluation_telemetry(run, model, commit, verifier)
    proof = run / "artifacts/proofs/global_step_11.jsonl"
    require(proof.is_file() and not proof.is_symlink(), "missing final diagnostic proof snapshot")
    records = list(analysis.read_jsonl(proof))
    batches = defaultdict(set)
    for row in records:
        require(row.get("config_hash") == telemetry["config_hash"] and
                row.get("environment_hash") == telemetry["environment_hash"],
                "diagnostic proposal runtime identity changed")
        require(row.get("pilot_padding") is False, "padding is not registered for the 168-row diagnostic")
        require(not row.get("blocked_correct"), "hard blocking appeared during diagnostic evaluation")
        batches[row.get("batch_id")].add(row["pilot_row_id"])
    require(set(batches) == {f"{run.name}:step-{step}" for step in range(1, STEPS + 1)} and
            all(len(batches[f"{run.name}:step-{step}"]) == (16 if step < STEPS else 8)
                for step in range(1, STEPS + 1)), "diagnostic proof batches differ from runtime telemetry")
    summary = analysis.summarize(bank, records)
    require(summary["registered"]["proposals"] == summary["physical"]["proposals"] == ROWS * SAMPLES and
            summary["panels"]["train_prefix"]["proposals"] == 0,
            "evaluation does not contain exactly 5376 diagnostic-only proposals")
    summary["classification"] = "trained_actor_frozen_diagnostic_not_compositional_OOD"
    summary.pop("gate")  # Diagnostic outcomes never define a training availability gate.
    summary["provenance"] = {"manifest": str(panel / "manifest.json"),
        "manifest_sha256": sha256(panel / "manifest.json"), "proof_log": str(proof),
        "proof_log_sha256": sha256(proof), "arm": certificate["arm"],
        "runtime_attestation": "separate evaluation_complete.json required; scientific counts alone do not establish model identity"}
    return summary, telemetry


def authenticate_checkpoint(certificate, base):
    actual = validate_actor_checkpoint(Path(certificate["checkpoint"]), base)
    require(actual == certificate["checkpoint_manifest"], "checkpoint bytes changed since training certification")
    return actual


def run(args):
    started, clock_started = time.time(), time.monotonic()
    bundle, output = args.bundle.resolve(), args.output.resolve()
    training_run, training_panel = args.training_run.resolve(), args.training_panel.resolve()
    require(args.job_id == prepare.WORKSPACE_JOB, "only the existing registered workspace is authorized")
    require(re.fullmatch(r"[0-9a-f]{40}", args.commit) is not None, "full immutable source commit required")
    require(re.fullmatch(r"[0-9a-f]{64}", args.training_sha256) is not None, "training manifest SHA-256 required")
    require(output.is_relative_to(bundle / "runs") and output != bundle / "runs", "output must be under bundle/runs")
    require(not output.exists(), "refusing existing diagnostic output")
    info = subprocess.check_output(["scontrol", "show", "job", str(args.job_id), "-o"], text=True)
    fields = dict(re.findall(r"(?:^|\s)(\w+)=([^\s]+)", info))
    nodes = subprocess.check_output(["scontrol", "show", "hostnames", fields.get("NodeList", "")], text=True).splitlines()
    cgroup, hostname = Path("/proc/self/cgroup").read_text(), socket.gethostname()
    screen.validate_allocation(args.job_id, info, hostname, cgroup, nodes)
    remaining = training.require_remaining_allocation(info, MAXIMUM_SECONDS)
    pinned = screen.validate_snapshot(ROOT, bundle / "repository", args.commit)
    preflight = bundle / "repository/scripts/project/preflight.sh"
    require(sha256(preflight) == pinned["scripts/project/preflight.sh"], "live preflight differs from snapshot")
    lock = bundle / "runs" / f".execution-training-{args.job_id}.active.json"
    with lock.open("x") as stream:
        json.dump({"operation": "diagnostic", "arm": args.arm, "pid": os.getpid(),
                   "hostname": hostname, "started_unix": started, "output": str(output)}, stream)
    output_created = False
    try:
        output.mkdir(parents=True, exist_ok=False)
        output_created = True
        manifest, arms = prepare.validate_training_panel(training_panel, args.training_sha256, bundle)
        panel = Path(manifest["panel"]).resolve()
        weights = screen.validate_model_weights(bundle / "models/base")
        certificate = authenticate_training(training_run, training_panel, args.training_sha256,
                                           bundle, args.arm, args.commit, pinned, arms[args.arm])
        certificate_hash = sha256(training_run / "training_complete.json")
        model = Path(certificate["checkpoint"])
        bank = diagnostic_bank(panel)
        (output / "train.parquet").write_bytes((panel / "diagnostic.parquet").read_bytes())
        scratch = Path("/tmp") / f"memoozd-execution-diagnostic-{args.job_id}-{output.name}"
        scratch.mkdir(exist_ok=False)
        verifier = scratch / "verifier"
        suffix = hashlib.sha256(str(output).encode()).hexdigest()[:8]
        ray_tmp = Path("/dev/shm") / f"r{args.job_id}ed{suffix}"
        ray_tmp.mkdir(exist_ok=False)
        (output / "telemetry").mkdir()
        system_gcc = "/cvmfs/soft.computecanada.ca/gentoo/2023/x86-64-v3/usr/bin"
        env = os.environ.copy()
        env.update({"RESTRICTION_BUNDLE_ROOT": str(bundle), "RESTRICTION_VENV": str(bundle / "environment/venv"),
            "ELAN_HOME": str(bundle / "lean/elan"), "HF_HOME": str(bundle / "runtime/huggingface"),
            "TRANSFORMERS_OFFLINE": "1", "HF_HUB_OFFLINE": "1", "PYTHONPATH": str(ROOT),
            "PYTHONDONTWRITEBYTECODE": "1", "PYTHONUNBUFFERED": "1", "DEEPSEEK_PROVER_ROOT": str(verifier),
            "DEEPSEEK_VERIFIER_MEMORY_LIMIT_GB": "32", "DMB_GIT_COMMIT": args.commit,
            "DMB_MODEL_REVISION": screen.MODEL_REVISION, "VLLM_ATTENTION_BACKEND": "XFORMERS",
            "EXECUTION_TRAINING_TELEMETRY": str(output / "telemetry"), "CC": system_gcc + "/gcc", "CXX": system_gcc + "/g++",
            "PATH": f"{bundle / 'environment/venv/bin'}:{bundle / 'lean/elan/bin'}:{system_gcc}:" + env["PATH"],
            "TMPDIR": str(ray_tmp), "TRITON_CACHE_DIR": str(ray_tmp / "triton"),
            "TORCHINDUCTOR_CACHE_DIR": str(ray_tmp / "torchinductor")})
        gpu_info = subprocess.check_output(["nvidia-smi", "--query-gpu=name,memory.total,driver_version", "--format=csv,noheader"], text=True)
        require(len(gpu_info.splitlines()) == 4 and all("H100" in line for line in gpu_info.splitlines()),
                "diagnostic requires the allocated four H100 GPUs")
        write_json(output / "provenance.json", {"source_commit": args.commit, "source_files_sha256": pinned,
            "source_kind": "separate git-archive snapshot; runtime source authenticated against commit",
            "live_repository_git_status": subprocess.check_output(
                ["git", "-C", str(bundle / "repository"), "status", "--short"], text=True).strip(),
            "training_run": str(training_run), "training_complete_sha256": certificate_hash,
            "training_manifest": str(training_panel / "manifest.json"), "training_manifest_sha256": args.training_sha256,
            "panel": str(panel), "panel_manifest_sha256": prepare.PANEL_SHA256,
            "model_path": str(model), "checkpoint_manifest": certificate["checkpoint_manifest"],
            "base_model_revision": screen.MODEL_REVISION, "base_model_weight_sha256": weights,
            "staged_verifier": str(verifier), "job_info": info, "cgroup": cgroup, "hostname": hostname,
            "gpu_info": gpu_info, "arm": args.arm, "seed": prepare.SEED, "started_unix": started,
            "maximum_seconds": MAXIMUM_SECONDS, "allocation_remaining_at_start": remaining,
            "hypothesis": "reserved practice improves held-out conditional execution and may transfer to unconditioned roots"})

        def budget(cap):
            seconds = min(cap, MAXIMUM_SECONDS - math.ceil(time.monotonic() - clock_started) - FINALIZATION_SECONDS)
            require(seconds > 0, "three-hour diagnostic budget exhausted")
            return seconds

        stage = screen.run_bounded(["bash", str(ROOT / "scripts/project/stage_deepseek_verifier.sh"),
            str(bundle / "verifier/DeepSeek-Prover-V1.5"), str(verifier)],
            output / "staging.log", cwd=ROOT, env=env, seconds=budget(1800))
        write_json(output / "staging_status.json", stage)
        require(stage["returncode"] == 0 and not stage["timed_out"], "verifier staging failed")
        patch_path = ROOT / "scripts/project/patches/benchmark_lake_path.patch"
        with patch_path.open("rb") as patch_input, (output / "lake_path_patch.log").open("x") as log:
            subprocess.run(["patch", "-d", str(verifier), "-p1"], stdin=patch_input, stdout=log,
                           stderr=subprocess.STDOUT, check=True, env=env, timeout=budget(60))
        verifier_provenance = {
            "source_verifier_sha256": sha256(bundle / "verifier/DeepSeek-Prover-V1.5/prover/lean/verifier.py"),
            "staged_verifier_sha256": sha256(verifier / "prover/lean/verifier.py"),
            "lake_path_patch_sha256": sha256(patch_path),
            "result_handoff_patch_sha256": sha256(ROOT / "scripts/project/patches/deepseek_verifier_compact_result.patch"),
            "lean_toolchain": (verifier / "mathlib4/lean-toolchain").read_text().strip()}
        validate_verifier_provenance(verifier_provenance, pinned, bundle)
        write_json(output / "verifier_provenance.json", verifier_provenance)
        status = screen.run_bounded(["bash", str(preflight)], output / "preflight.log",
                                    cwd=bundle / "repository", env=env, seconds=budget(300))
        write_json(output / "preflight_status.json", status)
        require(status["returncode"] == 0 and not status["timed_out"], "allocated-node preflight failed")
        command = screen.command_for_panel(output, model, SAMPLES)
        write_json(output / "command.json", command)
        ray = str(bundle / "environment/venv/bin/ray")
        with (output / "ray_cleanup.log").open("x") as cleanup:
            subprocess.run([ray, "stop", "--force"], env=env, stdout=cleanup, stderr=subprocess.STDOUT, timeout=90, check=False)
            try:
                seconds = budget(MAXIMUM_SECONDS)
                require(seconds >= 900, "insufficient remaining diagnostic budget")
                current = subprocess.check_output(["scontrol", "show", "job", str(args.job_id), "-o"], text=True)
                screen.validate_allocation(args.job_id, current, hostname, Path("/proc/self/cgroup").read_text(), nodes)
                training.require_remaining_allocation(current, seconds + FINALIZATION_SECONDS)
                result = screen.run_bounded(command, output / "run.log", cwd=verifier, env=env, seconds=seconds)
            finally:
                subprocess.run([ray, "stop", "--force"], env=env, stdout=cleanup, stderr=subprocess.STDOUT, timeout=90, check=False)
        result.update(expected_steps=STEPS, registered_rows=ROWS, registered_proposals=ROWS * SAMPLES,
                      elapsed_evaluation_seconds=time.monotonic() - clock_started)
        write_json(output / "process_status.json", result)
        summary, telemetry = certify_evaluation(output, bank, certificate, panel, args.commit, verifier, result)
        actual_checkpoint = authenticate_checkpoint(certificate, bundle / "models/base")
        require(sha256(training_run / "training_complete.json") == certificate_hash,
                "training certificate changed during evaluation")
        write_json(output / "resolved_config.json", telemetry["resolved_config"])
        write_json(output / "analysis.json", summary)
        elapsed = time.monotonic() - clock_started
        require(elapsed <= MAXIMUM_SECONDS, "diagnostic exceeded three-hour envelope")
        proof = output / "artifacts/proofs/global_step_11.jsonl"
        write_json(output / "evaluation_complete.json", {"schema_version": 1,
            "status": "complete_frozen_diagnostic_evaluation", "arm": args.arm,
            "source_commit": args.commit, "training_run": str(training_run),
            "training_complete_sha256": certificate_hash, "training_manifest_sha256": args.training_sha256,
            "panel_manifest_sha256": prepare.PANEL_SHA256, "model_path": str(model),
            "checkpoint_manifest": actual_checkpoint, "registered_rows": ROWS, "samples_per_row": SAMPLES,
            "registered_proposals": ROWS * SAMPLES, "trained_samples": 0, "actor_updates": 0,
            "proof_log": str(proof), "proof_log_sha256": sha256(proof),
            "telemetry": telemetry, "elapsed_seconds": elapsed, "maximum_seconds": MAXIMUM_SECONDS,
            "files_sha256": {name: sha256(output / name) for name in (
                "command.json", "process_status.json", "provenance.json", "verifier_provenance.json",
                "staging_status.json", "preflight_status.json", "train.parquet", "run.log",
                "resolved_config.json", "analysis.json")},
            "runtime_attestation": "certified final actor bytes, sample-only resolved runtime, zero update events, complete diagnostic outcomes"})
    except BaseException as error:
        if output_created:
            write_json(output / "failure.json", {"error": repr(error), "time_unix": time.time(),
                                                 "evaluation_complete": False, "automatic_retry": False})
        raise
    finally:
        lock.unlink()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for flag in ("bundle", "training-panel", "training-run", "output"):
        parser.add_argument("--" + flag, type=Path, required=True)
    parser.add_argument("--arm", choices=("root", "practice"), required=True)
    parser.add_argument("--commit", required=True)
    parser.add_argument("--training-sha256", required=True)
    parser.add_argument("--job-id", type=int, required=True)
    run(parser.parse_args())


if __name__ == "__main__":
    main()
