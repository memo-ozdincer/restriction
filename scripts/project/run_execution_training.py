#!/usr/bin/env python3
"""Manually run ONE conditional-training arm inside workspace job 1176227.

Run from a reviewed immutable git-archive snapshot, through SSH on the assigned
compute node. No submission, waiting, automatic arm chaining, or resume exists.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from datetime import datetime
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

from scripts.project import prepare_execution_training as prepare
from scripts.project import run_execution_screen as screen
from scripts.project.analyze_execution_pilot import read_jsonl, text_hash

require = prepare.require
sha256 = screen.sha256
write_json = screen.write_json
MAXIMUM_SECONDS = 21600
ALLOCATION_MARGIN = 900


def require_remaining_allocation(job_info, seconds, now=None):
    fields = dict(re.findall(r"(?:^|\s)(\w+)=([^\s]+)", job_info))
    try:
        end = datetime.fromisoformat(fields["EndTime"]).timestamp()
    except (KeyError, ValueError):
        raise ValueError("allocation has no finite parseable EndTime") from None
    remaining = end - (time.time() if now is None else now)
    require(remaining >= seconds + ALLOCATION_MARGIN, "insufficient remaining allocation time")
    return remaining


def command_for_arm(run, model):
    """Both arms differ only through the initial-state values in their parquet."""
    return [sys.executable, "-m", "verl.trainer.main_lean",
        f"data.train_files={run / 'train.parquet'}", f"data.val_files={run / 'train.parquet'}",
        "data.max_prompt_length=512", "+data.seed=42",
        f"actor_rollout_ref.model.path={model}",
        "actor_rollout_ref.actor.optim.lr=1e-6", "actor_rollout_ref.actor.optim.lr_warmup_steps=0",
        "actor_rollout_ref.actor.optim.weight_decay=0.01", "actor_rollout_ref.actor.ppo_mini_batch_size=256",
        "actor_rollout_ref.actor.ppo_micro_batch_size_per_gpu=8",
        "actor_rollout_ref.rollout.log_prob_micro_batch_size_per_gpu=16",
        "actor_rollout_ref.rollout.tensor_model_parallel_size=2", "actor_rollout_ref.rollout.gpu_memory_utilization=0.5",
        "actor_rollout_ref.ref.log_prob_micro_batch_size_per_gpu=16", "critic.ppo_micro_batch_size=8",
        "trainer.default_hdfs_dir=null", f"trainer.default_local_dir={run / 'artifacts'}",
        "trainer.n_gpus_per_node=4", "trainer.nnodes=1", "trainer.logger=[console]",
        "actor_rollout_ref.rollout.name=vllm", "actor_rollout_ref.rollout.n=1",
        "actor_rollout_ref.rollout.response_length=512", "actor_rollout_ref.rollout.temperature=1.0",
        "actor_rollout_ref.rollout.top_p=1.0", "actor_rollout_ref.rollout.top_k=-1",
        "actor_rollout_ref.actor.use_kl_loss=True", "actor_rollout_ref.actor.kl_loss_coef=0.10",
        "actor_rollout_ref.actor.ppo_epochs=2", "algorithm.adv_estimator=grpo",
        "+actor_rollout_ref.model.trust_remote_code=True", "actor_rollout_ref.rollout.load_format=dummy_dtensor",
        "actor_rollout_ref.actor.update_rule=ppo", "actor_rollout_ref.actor.entropy_coeff=0.0",
        "actor_rollout_ref.actor.grad_skip_thresh=20.0", f"trainer.experiment_name={run.name}",
        "trainer.save_freq=16", "trainer.save_limit=2", "trainer.save_proof_freq=1",
        "trainer.total_epochs=1", "trainer.total_training_steps=64", "trainer.train_batch_size=256",
        "trainer.dynamic_update=True", "+trainer.resume=False", "+trainer.sample_only=False",
        "lean.prompt_key=deepseek-prover", "lean.num_samples=32", "lean.problem_batch_size=16",
        "lean.rejection_sampling=False", "lean.advantage_threshold=True", "lean.max_workers=64",
        "+lean.penalize_extra_text=True", "+lean.rank_penalty=0.25", "lean.hard_blocking.enabled=False",
        f"hydra.run.dir={run / 'hydra'}"]


def expected_runtime_config(run, model):
    """Resolve the fixed command and the trainer's documented step injection."""
    from omegaconf import OmegaConf
    overrides = [item.lstrip("+") for item in command_for_arm(run, model)[3:]
                 if not item.startswith("hydra.")]
    config = OmegaConf.merge(OmegaConf.load(ROOT / "verl/trainer/config/lean_trainer.yaml"),
                             OmegaConf.from_dotlist(overrides))
    config.actor_rollout_ref.actor.optim.total_training_steps = prepare.STEPS
    config.critic.optim.total_training_steps = prepare.STEPS
    return OmegaConf.to_container(config, resolve=True)


def validate_training_proofs(path, rows, expected_identity=None):
    """Count all 32,768 fresh proposals, including failed and rejected attempts."""
    by_id = {row["pilot_row_id"]: row for row in rows}
    require(len(by_id) == prepare.ROWS, "training rows are not unique")
    grouped, proposal_ids, batches = defaultdict(list), set(), defaultdict(set)
    physical, failures = Counter(), Counter()
    for record in read_jsonl(path):
        key = record.get("pilot_row_id")
        require(key in by_id, "unknown training proposal row")
        row = by_id[key]
        require(record.get("pilot_padding") is False and record.get("pilot_split") == "train",
                "training padding or diagnostic leakage")
        for logged, frozen in (("theorem_name", "theorem_full_name"), ("theorem_statement", "theorem_statement"),
                                ("context", "src_context")):
            require(record.get(logged) == row[frozen], "training theorem metadata changed")
        prefix = row["proof_prefix"]
        require(record.get("proof_prefix", "") == prefix, "training prefix changed")
        if prefix:
            require(record.get("proof_prefix_sha256") == row["prefix_sha256"] and
                    record.get("conditioning_id") == row["conditioning_id"] and
                    isinstance(record.get("generated_suffix"), str) and
                    record["proof"] == prefix + record["generated_suffix"], "training suffix provenance changed")
        require(record.get("proof_hash") == text_hash(record["proof"]), "training proof checksum changed")
        if expected_identity is not None:
            require(record.get("config_hash") == expected_identity["config_hash"] and
                    record.get("environment_hash") == expected_identity["environment_hash"],
                    "training proposal runtime identity changed")
        proposal = record.get("proposal_id")
        require(isinstance(proposal, str) and proposal and proposal not in proposal_ids,
                "missing or repeated fresh proposal identity")
        proposal_ids.add(proposal)
        candidate = record.get("candidate_index")
        require(type(candidate) is int and 0 <= candidate < prepare.SAMPLES, "candidate outside proposal budget")
        require(type(record.get("correct")) is bool and type(record.get("verdict")) is bool and
                record["correct"] == record["verdict"], "training correctness invalid")
        require(type(record.get("lean_complete")) is bool and type(record.get("timed_out")) is bool and
                (not record["correct"] or (record["lean_complete"] and not record["timed_out"] and
                                           not record.get("verifier_error"))), "invalid correct verifier result")
        require(record.get("prompt_token_count") == row["prompt_token_count"], "training prompt tokens changed")
        require(type(record.get("token_count")) is int and record["token_count"] >= 0, "invalid generated tokens")
        require(not record.get("blocked_correct"), "hard blocking appeared in conditional training")
        for timing_key in ("parse_time", "queue_wait_time", "verification_time"):
            value = record.get(timing_key)
            require(value is None or (type(value) in (int, float) and math.isfinite(value) and value >= 0),
                    "invalid verifier timing")
            physical[timing_key + ("_missing" if value is None else "_seconds_sum")] += 1 if value is None else value
        failures[record.get("failure_class") or "none"] += 1
        batch = record.get("batch_id")
        require(isinstance(batch, str) and batch, "training batch identity missing")
        batches[batch].add(key)
        grouped[key].append(candidate)
        physical.update(proposals=1, generated_tokens=record["token_count"],
                        prompt_tokens=row["prompt_token_count"], supplied_prefix_tokens=row["prefix_token_count"],
                        correct=int(record["correct"]), timed_out=int(record["timed_out"]),
                        verifier_errors=int(bool(record.get("verifier_error"))))
    require(set(grouped) == set(by_id), "missing fresh training tasks")
    require(all(len(values) == prepare.SAMPLES and set(values) == set(range(prepare.SAMPLES))
                for values in grouped.values()), "training proposal count/index mismatch")
    require(len(batches) == prepare.STEPS and all(len(ids) == 16 for ids in batches.values()),
            "training did not produce exactly 64 fresh batches of 16")
    require(sum(map(len, batches.values())) == prepare.ROWS, "training row repeated across batches")
    physical["verification_attempts"] = physical["proposals"]
    return dict(physical, blocked=0, failure_classes=dict(failures))


def certify_completion(run, rows, result, model, arm, manifest_digest, commit, *, persist=True):
    from scripts.project.execution_training_telemetry import summarize_telemetry, validate_actor_checkpoint
    run = Path(run)
    require(not (run / "failure.json").exists(), "training arm has a failure certificate")
    require(prepare.read_json(run / "process_status.json") == result, "process status differs from saved runtime")
    require(result.get("arm") == arm and result.get("expected_steps") == prepare.STEPS and
            result.get("registered_rows") == prepare.ROWS and result.get("registered_proposals") == prepare.ROWS * prepare.SAMPLES and
            0 < result.get("elapsed_arm_seconds", 0) <= MAXIMUM_SECONDS, "training process budget certificate changed")
    command = prepare.read_json(run / "command.json")
    require(command[1:] == command_for_arm(run, model)[1:], "training runtime command changed")
    log_text = (run / "run.log").read_text(errors="replace")
    require(result.get("timed_out") is False and "[TRAINING] Training finished" in log_text and
            (result.get("returncode") == 0 or "Exception: Stop" in log_text), "training process did not complete")
    proof_files = {f"global_step_{step}.jsonl" for step in range(1, prepare.STEPS + 1)}
    require(proof_files <= {path.name for path in (run / "artifacts/proofs").glob("*.jsonl")},
            "a per-step proof snapshot is missing")
    proof = run / "artifacts/proofs/global_step_64.jsonl"
    telemetry = summarize_telemetry(run / "telemetry", expected_ranks=4)
    require(telemetry["resolved_config"] == expected_runtime_config(run, model),
            "resolved training configuration differs from registered command")
    provenance = prepare.read_json(run / "provenance.json")
    require(provenance.get("source_commit") == commit and provenance.get("training_manifest_sha256") == manifest_digest and
            provenance.get("arm") == arm and provenance.get("model_weight_sha256") == screen.BASE_MODEL_WEIGHTS and
            Path(provenance.get("model_path", "")).resolve() == Path(model).resolve(), "training provenance changed")
    require(telemetry["environment"] == {"git_commit": commit, "model_revision": screen.MODEL_REVISION,
            "verifier_root": provenance["staged_verifier"], "verifier_memory_limit_gb": "32"},
            "training environment differs from registered runtime")
    costs = validate_training_proofs(proof, rows, telemetry)
    require(telemetry["actual_optimizer_steps"] > 0 and telemetry["final_checkpoint_saved"] is True,
            "no demonstrated actor optimizer updates or final checkpoint save")
    checkpoint = run / "artifacts/actor/global_step_64"
    checkpoint_manifest = validate_actor_checkpoint(checkpoint, model)
    if persist:
        write_json(run / "resolved_config.json", telemetry["resolved_config"])
    else:
        require(prepare.read_json(run / "resolved_config.json") == telemetry["resolved_config"],
                "saved resolved configuration differs from attested runtime")
    complete = {"schema_version": 1, "status": "complete_eligible_for_diagnostic_evaluation",
        "evaluation_eligible": True, "arm": arm, "global_steps": prepare.STEPS,
        "proposals": costs["proposals"], "costs": costs, "checkpoint": str(checkpoint.resolve()),
        "checkpoint_manifest": checkpoint_manifest, "telemetry": telemetry, "telemetry_valid": True,
        "proof_log": str(proof.resolve()), "proof_log_sha256": sha256(proof),
        "training_manifest_sha256": manifest_digest, "source_commit": commit,
        "command_sha256": sha256(run / "command.json"),
        "process_status_sha256": sha256(run / "process_status.json"),
        "resume_supported": False, "checkpoint_contents": "actor weights and tokenizer; no exact optimizer/RNG resume"}
    if persist:
        write_json(run / "training_complete.json", complete)
    return complete


def run(args):
    started, clock_started = time.time(), time.monotonic()
    bundle, panel, comparison = args.bundle.resolve(), args.training_panel.resolve(), args.output.resolve()
    require(args.job_id == prepare.WORKSPACE_JOB, "only the existing registered workspace is authorized")
    require(re.fullmatch(r"[0-9a-f]{40}", args.commit) is not None, "full immutable source commit required")
    require(re.fullmatch(r"[0-9a-f]{64}", args.training_sha256) is not None, "training manifest SHA-256 required")
    require(comparison.is_relative_to(bundle / "runs") and comparison != bundle / "runs", "output must be under bundle/runs")
    output = comparison / args.arm
    require(not output.exists(), "refusing reused arm output; exact resume is unsupported")
    info = subprocess.check_output(["scontrol", "show", "job", str(args.job_id), "-o"], text=True)
    fields = dict(re.findall(r"(?:^|\s)(\w+)=([^\s]+)", info))
    nodes = subprocess.check_output(["scontrol", "show", "hostnames", fields.get("NodeList", "")], text=True).splitlines()
    cgroup, hostname = Path("/proc/self/cgroup").read_text(), socket.gethostname()
    screen.validate_allocation(args.job_id, info, hostname, cgroup, nodes)
    other = comparison / ("practice" if args.arm == "root" else "root")
    if other.exists():
        sibling = prepare.read_json(other / "training_complete.json")
        require(sibling.get("evaluation_eligible") is True and
                sibling.get("training_manifest_sha256") == args.training_sha256 and
                sibling.get("source_commit") == args.commit, "other arm incomplete or from another comparison")
    remaining = require_remaining_allocation(info, MAXIMUM_SECONDS if other.exists() else 2 * MAXIMUM_SECONDS)
    pinned = screen.validate_snapshot(ROOT, bundle / "repository", args.commit)
    manifest, arms = prepare.validate_training_panel(panel, args.training_sha256, bundle)
    model = bundle / "models/base"
    weights = screen.validate_model_weights(model)
    preflight = bundle / "repository/scripts/project/preflight.sh"
    require(sha256(preflight) == pinned["scripts/project/preflight.sh"], "live preflight differs from snapshot")
    comparison.mkdir(parents=True, exist_ok=True)
    # Never race two model processes inside this full-node workspace.
    lock = bundle / "runs" / f".execution-training-{args.job_id}.active.json"
    with lock.open("x") as stream:
        json.dump({"arm": args.arm, "pid": os.getpid(), "hostname": hostname, "started_unix": started}, stream)
    output.mkdir()
    try:
        (output / "train.parquet").write_bytes((panel / args.arm / "train.parquet").read_bytes())
        scratch = Path("/tmp") / f"memoozd-execution-training-{args.job_id}-{args.arm}-{comparison.name}"
        scratch.mkdir(exist_ok=False)
        verifier = scratch / "verifier"
        ray_tmp = Path("/dev/shm") / f"r{args.job_id}et{args.arm[0]}"
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
        write_json(output / "provenance.json", {"source_commit": args.commit, "source_files_sha256": pinned,
            "training_panel": str(panel), "training_manifest_sha256": args.training_sha256,
            "screen_analysis": str(Path(manifest["screen_run"]) / "analysis.json"),
            "panel_manifest_sha256": prepare.PANEL_SHA256, "model_path": str(model),
            "staged_verifier": str(verifier),
            "model_revision": screen.MODEL_REVISION, "model_weight_sha256": weights,
            "job_info": info, "cgroup": cgroup, "hostname": hostname, "arm": args.arm, "seed": prepare.SEED,
            "gpu_info": subprocess.check_output(["nvidia-smi", "--query-gpu=name,memory.total,driver_version", "--format=csv,noheader"], text=True),
            "started_unix": started, "maximum_seconds": MAXIMUM_SECONDS, "allocation_remaining_at_start": remaining,
            "hypothesis": "reserved practice of partially competent verified starts improves held-out conditional execution"})
        stage = screen.run_bounded(["bash", str(ROOT / "scripts/project/stage_deepseek_verifier.sh"),
                                   str(bundle / "verifier/DeepSeek-Prover-V1.5"), str(verifier)],
                                  output / "staging.log", cwd=ROOT, env=env, seconds=1800)
        write_json(output / "staging_status.json", stage)
        require(stage["returncode"] == 0 and not stage["timed_out"], "verifier staging failed")
        patch_path = ROOT / "scripts/project/patches/benchmark_lake_path.patch"
        with patch_path.open("rb") as patch_input, (output / "lake_path_patch.log").open("x") as log:
            subprocess.run(["patch", "-d", str(verifier), "-p1"], stdin=patch_input, stdout=log,
                           stderr=subprocess.STDOUT, check=True, env=env, timeout=60)
        verifier_provenance = {
            "source_verifier_sha256": sha256(bundle / "verifier/DeepSeek-Prover-V1.5/prover/lean/verifier.py"),
            "staged_verifier_sha256": sha256(verifier / "prover/lean/verifier.py"),
            "lake_path_patch_sha256": sha256(patch_path),
            "result_handoff_patch_sha256": sha256(ROOT / "scripts/project/patches/deepseek_verifier_compact_result.patch"),
            "lean_toolchain": (verifier / "mathlib4/lean-toolchain").read_text().strip()}
        require(verifier_provenance["source_verifier_sha256"] == prepare.SOURCE_VERIFIER_SHA256 and
                verifier_provenance["staged_verifier_sha256"] == prepare.STAGED_VERIFIER_SHA256,
                "training verifier differs from authenticated screen verifier")
        write_json(output / "verifier_provenance.json", verifier_provenance)
        status = screen.run_bounded(["bash", str(preflight)], output / "preflight.log",
                                    cwd=bundle / "repository", env=env, seconds=300)
        write_json(output / "preflight_status.json", status)
        require(status["returncode"] == 0 and not status["timed_out"], "allocated-node preflight failed")
        command = command_for_arm(output, model)
        write_json(output / "command.json", command)
        ray = str(bundle / "environment/venv/bin/ray")
        with (output / "ray_cleanup.log").open("x") as cleanup:
            subprocess.run([ray, "stop", "--force"], env=env, stdout=cleanup, stderr=subprocess.STDOUT, timeout=90, check=False)
            try:
                budget = MAXIMUM_SECONDS - math.ceil(time.monotonic() - clock_started) - 120
                require(budget >= 900, "insufficient remaining arm budget")
                current = subprocess.check_output(["scontrol", "show", "job", str(args.job_id), "-o"], text=True)
                screen.validate_allocation(args.job_id, current, hostname, cgroup, nodes)
                require_remaining_allocation(current, budget)
                result = screen.run_bounded(command, output / "run.log", cwd=verifier, env=env, seconds=budget)
            finally:
                subprocess.run([ray, "stop", "--force"], env=env, stdout=cleanup, stderr=subprocess.STDOUT, timeout=90, check=False)
        result.update(arm=args.arm, expected_steps=prepare.STEPS, registered_rows=prepare.ROWS,
                      registered_proposals=prepare.ROWS * prepare.SAMPLES,
                      elapsed_arm_seconds=time.monotonic() - clock_started)
        write_json(output / "process_status.json", result)
        require(result["elapsed_arm_seconds"] <= MAXIMUM_SECONDS, "arm exceeded six-hour execution envelope")
        certify_completion(output, arms[args.arm], result, model, args.arm, args.training_sha256, args.commit)
    except BaseException as error:
        write_json(output / "failure.json", {"error": repr(error), "time_unix": time.time(),
                                             "evaluation_eligible": False, "automatic_retry": False})
        raise
    finally:
        lock.unlink()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for flag in ("bundle", "training-panel", "output"):
        parser.add_argument("--" + flag, type=Path, required=True)
    parser.add_argument("--arm", choices=("root", "practice"), required=True)
    parser.add_argument("--commit", required=True)
    parser.add_argument("--training-sha256", required=True)
    parser.add_argument("--job-id", type=int, required=True)
    run(parser.parse_args())


if __name__ == "__main__":
    main()
