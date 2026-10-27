#!/usr/bin/env python3
"""Run the registered base continuation screen inside an allocated workspace.

Run this from an immutable git-archive snapshot on the assigned compute node.
It never submits Slurm jobs and never updates model weights.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import re
import signal
import socket
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[2]
MODEL_REVISION = "e9a6e6fbb67620d4e9c4944bc51ff7c435af12da"
# Authenticated base shards from the original bundle's MANIFEST.sha256.
BASE_MODEL_WEIGHTS = {
    "model-00001-of-000002.safetensors": "a8fc709546d75ee3440d402d6b2431d6b52e98d63befba1a99b3f230d859f649",
    "model-00002-of-000002.safetensors": "90602e9cb2983b429020f4186693872cad0fe3ea31690b45e94c49efa6688b89",
}
SOURCE_SUFFIXES = {".py", ".sh", ".yaml", ".yml", ".patch", ".toml", ".json",
                   ".c", ".cc", ".cpp", ".cu", ".h", ".hpp", ".sbatch"}


def sha256(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def write_json(path, value):
    path = Path(path)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")
    temporary.replace(path)


def validate_allocation(job_id, job_info, hostname, cgroup, nodes):
    """Fail closed if SSH did not enter the user's live Slurm allocation."""
    fields = dict(re.findall(r"(?:^|\s)(\w+)=([^\s]+)", job_info))
    if fields.get("JobId") != str(job_id) or fields.get("Account") != "def-zhijing":
        raise ValueError("not the requested def-zhijing allocation")
    if fields.get("JobState") != "RUNNING":
        raise ValueError("workspace is not running")
    if hostname.split(".")[0] not in {n.split(".")[0] for n in nodes}:
        raise ValueError("this host is not assigned to the workspace")
    if not re.search(rf"(?:^|[/_-])job[_-]?{int(job_id)}(?:[/_.\n-]|$)", cgroup):
        raise ValueError("process is not inside the allocated Slurm job cgroup")
    return fields


def validate_snapshot(snapshot, live_repo, commit):
    """Check every tracked runtime source and reject injected source modules."""
    snapshot, live_repo = Path(snapshot).resolve(), Path(live_repo).resolve()
    if snapshot == live_repo:
        raise ValueError("execute from a separate immutable git-archive snapshot")
    tree = subprocess.check_output(["git", "-C", str(live_repo), "ls-tree", "-r", "-z", commit])
    tracked = set()
    pinned = {}
    for entry in tree.split(b"\0"):
        if not entry:
            continue
        header, name = entry.split(b"\t", 1)
        mode, kind, object_id = header.decode().split()
        relative = name.decode()
        if Path(relative).suffix not in SOURCE_SUFFIXES:
            continue
        tracked.add(relative)
        source = snapshot / relative
        if kind != "blob" or mode not in ("100644", "100755") or source.is_symlink() or not source.is_file():
            raise ValueError(f"missing or unsupported pinned source: {relative}")
        content = source.read_bytes()
        actual = hashlib.sha1(b"blob " + str(len(content)).encode() + b"\0" + content).hexdigest()
        if actual != object_id:
            raise ValueError(f"source differs from pinned commit: {relative}")
        pinned[relative] = hashlib.sha256(content).hexdigest()
    if not pinned:
        raise ValueError("snapshot contains no pinned runtime source")
    # Additional Python/config/patch files could change imports or runtime setup.
    for source in snapshot.rglob("*"):
        if source.is_file() and source.suffix in SOURCE_SUFFIXES:
            if str(source.relative_to(snapshot)) not in tracked:
                raise ValueError(f"untracked runtime source in snapshot: {source.relative_to(snapshot)}")
    return pinned


def validate_panel(panel, expected_digest, bundle):
    panel, bundle = Path(panel), Path(bundle)
    manifest_path = panel / "manifest.json"
    if sha256(manifest_path) != expected_digest:
        raise ValueError("panel manifest differs from preregistered digest")
    manifest = json.loads(manifest_path.read_text())
    if manifest.get("schema_version") != 1 or manifest.get("model_revision") != MODEL_REVISION:
        raise ValueError("unsupported panel schema or base model revision")
    model = (bundle / "models/base").resolve()
    if Path(manifest["model_path"]).resolve() != model:
        raise ValueError("panel was prepared with a different model path")
    for filename in ("selection_bank.jsonl", "train_prefix.parquet", "diagnostic.parquet"):
        entry = manifest["files"][filename]
        expected = entry["sha256"] if isinstance(entry, dict) else entry
        if sha256(panel / filename) != expected:
            raise ValueError(f"panel checksum mismatch: {filename}")
    configuration = manifest.get("model_configuration_and_tokenizer_sha256", {})
    if not configuration:
        raise ValueError("model configuration/tokenizer digests are missing")
    for filename, expected in configuration.items():
        path = model / filename
        if Path(filename).is_absolute() or ".." in Path(filename).parts or sha256(path) != expected:
            raise ValueError(f"model configuration/tokenizer checksum mismatch: {filename}")
    return manifest


def validate_model_weights(model, expected=BASE_MODEL_WEIGHTS):
    """Hash complete base weight shards, not only a model name or config."""
    actual = {}
    for filename, digest in expected.items():
        actual[filename] = sha256(Path(model) / filename)
        if actual[filename] != digest:
            raise ValueError(f"base model weight checksum mismatch: {filename}")
    return actual


def command_for_panel(run, model, samples):
    """Fixed screen settings; no training, no model/reference substitution."""
    return [sys.executable, "-m", "verl.trainer.main_lean",
        f"data.train_files={run / 'train.parquet'}",
        f"data.val_files={run / 'train.parquet'}",
        "data.max_prompt_length=512", "+data.seed=42",
        f"actor_rollout_ref.model.path={model}",
        "actor_rollout_ref.actor.ppo_micro_batch_size_per_gpu=8",
        "actor_rollout_ref.rollout.log_prob_micro_batch_size_per_gpu=16",
        "actor_rollout_ref.rollout.tensor_model_parallel_size=2",
        "actor_rollout_ref.rollout.gpu_memory_utilization=0.5",
        "actor_rollout_ref.ref.log_prob_micro_batch_size_per_gpu=16",
        "critic.ppo_micro_batch_size=8", "trainer.default_hdfs_dir=null",
        f"trainer.default_local_dir={run / 'artifacts'}",
        "trainer.n_gpus_per_node=4", "trainer.nnodes=1",
        "trainer.logger=[console]", "actor_rollout_ref.rollout.name=vllm",
        "actor_rollout_ref.rollout.n=1", "actor_rollout_ref.rollout.response_length=512",
        "actor_rollout_ref.rollout.temperature=1.0", "actor_rollout_ref.rollout.top_p=1.0",
        "actor_rollout_ref.rollout.top_k=-1", "+actor_rollout_ref.model.trust_remote_code=True",
        "actor_rollout_ref.rollout.load_format=dummy_dtensor",
        f"trainer.experiment_name={run.name}", "trainer.save_freq=0",
        "trainer.save_proof_freq=1", "trainer.total_epochs=1",
        "+trainer.sample_only=True", "+trainer.resume=False",
        "algorithm.adv_estimator=grpo", "lean.prompt_key=deepseek-prover",
        f"lean.num_samples={samples}", "lean.problem_batch_size=16",
        "lean.rejection_sampling=False", "lean.advantage_threshold=False",
        "lean.max_workers=32", "+lean.penalize_extra_text=True",
        "lean.hard_blocking.enabled=False", f"hydra.run.dir={run / 'hydra'}"]


def run_bounded(command, log, *, cwd, env, seconds):
    """Preserve process status and terminate its process group on deadline."""
    if seconds <= 0:
        raise ValueError("process budget must be positive")
    started = time.time()
    clock_started = time.monotonic()
    with Path(log).open("x") as stream:
        child = subprocess.Popen(command, stdout=stream, stderr=subprocess.STDOUT,
                                 cwd=cwd, env=env, start_new_session=True)
        try:
            rc = child.wait(timeout=seconds)
            timed_out = False
        except subprocess.TimeoutExpired:
            timed_out = True
            try:
                os.killpg(child.pid, signal.SIGTERM)
            except ProcessLookupError:
                pass
            try:
                rc = child.wait(timeout=30)
            except subprocess.TimeoutExpired:
                try:
                    os.killpg(child.pid, signal.SIGKILL)
                except ProcessLookupError:
                    pass
                rc = child.wait()
        except BaseException:
            try:
                os.killpg(child.pid, signal.SIGTERM)
            except ProcessLookupError:
                pass
            try:
                child.wait(timeout=30)
            except subprocess.TimeoutExpired:
                try:
                    os.killpg(child.pid, signal.SIGKILL)
                except ProcessLookupError:
                    pass
                child.wait()
            raise
    return {"returncode": rc, "timed_out": timed_out,
            "started_unix": started, "elapsed_seconds": time.monotonic() - clock_started}


def verify_witnesses(bank, output, workers=32):
    """Recheck witnesses and reject solved or unverifiable partial tasks."""
    from verl.lean.verifier import verify_with_deepseek_verifier
    tasks = [json.loads(line) for line in Path(bank).read_text().splitlines() if line.strip()]
    tasks = [r for r in tasks if r["proof_prefix"]]
    if not tasks:
        raise ValueError("no continuation witnesses")
    checked = []
    submitted_candidates = 0
    for offset in range(0, len(tasks), 32):
        group = tasks[offset:offset + 32]
        proofs, statements, contexts = [], [], []
        for row in group:
            witness = row["witness_proof"]
            if hashlib.sha256(witness.encode()).hexdigest() != row["witness_sha256"]:
                raise ValueError("witness checksum mismatch")
            if not witness.startswith(row["proof_prefix"]):
                raise ValueError("prefix is not an exact witness start")
            proofs += [witness, row["proof_prefix"] + "\n```\n"]
            statements.append(row["theorem_statement"])
            contexts.append(row["src_context"])
        submitted_candidates += len(proofs)
        pending = {"complete": False, "checked": checked,
                   "submitted_candidates": submitted_candidates,
                   "physical_lean_calls": None,
                   "physical_lean_calls_lower_bound": 2 * len(checked)}
        write_json(output, pending)
        try:
            results = verify_with_deepseek_verifier(proofs, statements, contexts,
                max_workers=workers, penalize_extra_text=True)
        except Exception as error:
            write_json(output, {**pending, "error": repr(error)})
            raise
        if len(results) != len(group):
            raise ValueError("witness verifier returned an incorrect batch length")
        for row, result in zip(group, results):
            candidates = result["candidate_results"]
            if len(candidates) != 2:
                raise ValueError("witness verifier returned an incorrect candidate count")
            record = {"pilot_row_id": row["pilot_row_id"],
                      "witness": candidates[0], "prefix_only": candidates[1]}
            checked.append(record)
        write_json(output, {"complete": False, "checked": checked,
                            "physical_lean_calls": 2 * len(checked),
                            "submitted_candidates": submitted_candidates})
    invalid = []
    for row in checked:
        witness, prefix = row["witness"], row["prefix_only"]
        reasons = []
        if (witness.get("verdict") is not True or witness.get("lean_complete") is not True
                or witness.get("failure_class") is not None or witness.get("timed_out")
                or witness.get("verifier_error")):
            reasons.append("witness_not_verified")
        if (prefix.get("verdict") is not False or prefix.get("lean_complete") is not False
                or prefix.get("failure_class") != "lean_rejected" or prefix.get("timed_out")
                or prefix.get("verifier_error")):
            reasons.append("prefix_not_confirmed_incomplete")
        if reasons:
            row["invalid_reasons"] = reasons
            invalid.append(row["pilot_row_id"])
    write_json(output, {"complete": True, "checked": checked,
                       "physical_lean_calls": 2 * len(checked),
                       "submitted_candidates": submitted_candidates, "invalid_tasks": invalid})
    if invalid:
        raise ValueError(f"{len(invalid)} tasks fail witness/nonterminal checks; no generation launched")


def run(args):
    started = time.time()
    clock_started = time.monotonic()
    bundle = args.bundle.resolve()
    panel = args.panel.resolve()
    output = args.output.resolve()
    if output.exists():
        raise FileExistsError(f"refusing existing output: {output}")
    if not re.fullmatch(r"[0-9a-f]{40}", args.commit):
        raise ValueError("a full immutable source commit is required")
    live_repo = bundle / "repository"
    pinned_source = validate_snapshot(ROOT, live_repo, args.commit)
    info = subprocess.check_output(["scontrol", "show", "job", str(args.job_id), "-o"], text=True)
    fields = dict(re.findall(r"(?:^|\s)(\w+)=([^\s]+)", info))
    nodes = subprocess.check_output(["scontrol", "show", "hostnames", fields.get("NodeList", "")], text=True).splitlines()
    cgroup = Path("/proc/self/cgroup").read_text()
    validate_allocation(args.job_id, info, socket.gethostname(), cgroup, nodes)
    manifest = validate_panel(panel, args.panel_sha256, bundle)
    model_weight_sha256 = validate_model_weights(bundle / "models/base")
    # Preflight itself needs Git metadata, while experiment imports use ROOT.
    preflight_path = live_repo / "scripts/project/preflight.sh"
    if sha256(preflight_path) != pinned_source["scripts/project/preflight.sh"]:
        raise ValueError("live preflight script differs from the pinned snapshot")
    output.mkdir(parents=True)
    scratch = Path("/tmp") / f"memoozd-execution-{args.job_id}-{output.name}"
    scratch.mkdir(exist_ok=False)
    verifier = scratch / "verifier"
    env = os.environ.copy()
    system_gcc = "/cvmfs/soft.computecanada.ca/gentoo/2023/x86-64-v3/usr/bin"
    env.update({"RESTRICTION_BUNDLE_ROOT": str(bundle),
        "RESTRICTION_VENV": str(bundle / "environment/venv"),
        "ELAN_HOME": str(bundle / "lean/elan"),
        "HF_HOME": str(bundle / "runtime/huggingface"),
        "TRANSFORMERS_OFFLINE": "1", "HF_HUB_OFFLINE": "1",
        "PYTHONPATH": str(ROOT), "PYTHONDONTWRITEBYTECODE": "1", "PYTHONUNBUFFERED": "1",
        "DEEPSEEK_PROVER_ROOT": str(verifier), "DEEPSEEK_VERIFIER_MEMORY_LIMIT_GB": "32",
        "DMB_GIT_COMMIT": args.commit, "DMB_MODEL_REVISION": MODEL_REVISION,
        "VLLM_ATTENTION_BACKEND": "XFORMERS", "CC": system_gcc + "/gcc", "CXX": system_gcc + "/g++",
        "PATH": f"{bundle / 'environment/venv/bin'}:{bundle / 'lean/elan/bin'}:{system_gcc}:" + env["PATH"]})
    # Ray Unix sockets must be on an executable local filesystem with short paths.
    ray_tmp = Path("/dev/shm") / f"r{args.job_id}ep"
    ray_tmp.mkdir(exist_ok=False)
    env.update({"TMPDIR": str(ray_tmp), "TRITON_CACHE_DIR": str(ray_tmp / "triton"),
                "TORCHINDUCTOR_CACHE_DIR": str(ray_tmp / "torchinductor")})
    write_json(output / "provenance.json", {"source_commit": args.commit,
        "panel": str(panel), "panel_manifest_sha256": args.panel_sha256,
        "model_path": str(bundle / "models/base"), "model_revision": MODEL_REVISION,
        "model_weight_sha256": model_weight_sha256,
        "source_files_sha256": pinned_source,
        "job_info": info, "cgroup": cgroup, "hostname": socket.gethostname(),
        "gpu_info": subprocess.check_output(["nvidia-smi", "--query-gpu=name,memory.total,driver_version", "--format=csv,noheader"], text=True),
        "seed": 42, "hypothesis": "valid short starts expose repairable execution deficits",
        "started_unix": started, "maximum_seconds": 21600})
    stage = run_bounded(["bash", str(ROOT / "scripts/project/stage_deepseek_verifier.sh"),
        str(bundle / "verifier/DeepSeek-Prover-V1.5"), str(verifier)],
        output / "staging.log", cwd=ROOT, env=env, seconds=1800)
    write_json(output / "staging_status.json", stage)
    if stage["returncode"] != 0:
        raise RuntimeError("verifier staging failed")
    # Reuse the audited operational path patch; it selects the same pinned lake
    # binary through ELAN_HOME without changing the user's HOME or Lean logic.
    lake_patch = ROOT / "scripts/project/patches/benchmark_lake_path.patch"
    with lake_patch.open("rb") as patch_input, (output / "lake_path_patch.log").open("x") as patch_log:
        subprocess.run(["patch", "-d", str(verifier), "-p1"], stdin=patch_input,
                       stdout=patch_log, stderr=subprocess.STDOUT, check=True, env=env, timeout=60)
    write_json(output / "verifier_provenance.json", {
        "source_verifier_sha256": sha256(bundle / "verifier/DeepSeek-Prover-V1.5/prover/lean/verifier.py"),
        "staged_verifier_sha256": sha256(verifier / "prover/lean/verifier.py"),
        "lake_path_patch_sha256": sha256(lake_patch),
        "result_handoff_patch_sha256": sha256(ROOT / "scripts/project/patches/deepseek_verifier_compact_result.patch"),
        "lean_toolchain": (verifier / "mathlib4/lean-toolchain").read_text().strip()})
    preflight = run_bounded(["bash", str(preflight_path)],
        output / "preflight.log", cwd=live_repo, env=env, seconds=300)
    write_json(output / "preflight_status.json", preflight)
    if preflight["returncode"] != 0:
        raise RuntimeError("allocated-node preflight failed")
    witness = run_bounded([sys.executable, str(Path(__file__).resolve()), "--verify-bank",
        str(panel / "selection_bank.jsonl"), "--witness-output", str(output / "witness_checks.json")],
        output / "witness.log", cwd=verifier, env=env, seconds=3600)
    write_json(output / "witness_status.json", witness)
    if witness["returncode"] != 0:
        raise RuntimeError("witness validation failed")
    import pandas as pd
    for label, filename, samples in (("practice", "train_prefix.parquet", 16),
                                     ("diagnostic", "diagnostic.parquet", 32)):
        destination = output / label
        destination.mkdir()
        (destination / "train.parquet").write_bytes((panel / filename).read_bytes())
        rows = len(pd.read_parquet(destination / "train.parquet"))
        if not 0 < rows <= (512 if label == "practice" else 192):
            raise ValueError("panel exceeds registered screen budget")
        command = command_for_panel(destination, bundle / "models/base", samples)
        write_json(destination / "command.json", command)
        # Only this full-node allocation is touched; the keeper does not use Ray.
        ray_command = str(bundle / "environment/venv/bin/ray")
        with (destination / "ray_cleanup.log").open("x") as cleanup:
            subprocess.run([ray_command, "stop", "--force"], env=env, stdout=cleanup,
                           stderr=subprocess.STDOUT, timeout=90, check=False)
            try:
                # Reserve the timeout termination grace and final Ray cleanup
                # inside the prospective six-hour execution envelope.
                remaining = 21600 - math.ceil(time.monotonic() - clock_started) - 120
                if remaining < 900:
                    raise RuntimeError("insufficient remaining screen budget")
                result = run_bounded(command, destination / "run.log", cwd=verifier, env=env, seconds=remaining)
            finally:
                subprocess.run([ray_command, "stop", "--force"], env=env, stdout=cleanup,
                               stderr=subprocess.STDOUT, timeout=90, check=False)
        steps = math.ceil(rows / 16)
        proof_log = destination / "artifacts/proofs" / f"global_step_{steps}.jsonl"
        result.update({"expected_steps": steps, "registered_rows": rows,
                       "registered_proposals": rows * samples, "proof_log": str(proof_log)})
        # The historical trainer signals successful termination with Exception('Stop').
        # Preserve the true exit status and require final artifact + finish marker.
        log_text = (destination / "run.log").read_text(errors="replace")
        result["completion_candidate"] = bool(not result["timed_out"] and proof_log.is_file()
            and "[TRAINING] Training finished" in log_text
            and (result["returncode"] == 0 or "Exception: Stop" in log_text))
        if proof_log.exists():
            result["proof_log_sha256"] = sha256(proof_log)
        write_json(destination / "process_status.json", result)
        if not result["completion_candidate"]:
            raise RuntimeError(f"{label} screen did not finish; preserve partial evidence")
    write_json(output / "generation_complete.json", {"elapsed_seconds": time.monotonic() - clock_started,
        "status": "generation_complete_pending_independent_analysis", "trained_samples": 0})


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bundle", type=Path)
    parser.add_argument("--panel", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--job-id", type=int)
    parser.add_argument("--commit")
    parser.add_argument("--panel-sha256")
    parser.add_argument("--verify-bank", type=Path)
    parser.add_argument("--witness-output", type=Path)
    args = parser.parse_args()
    if args.verify_bank:
        if not args.witness_output:
            parser.error("--verify-bank requires --witness-output")
        verify_witnesses(args.verify_bank, args.witness_output)
    else:
        if any(getattr(args, key) is None for key in ("bundle", "panel", "output", "job_id", "commit", "panel_sha256")):
            parser.error("all workspace, panel, output, and provenance arguments are required")
        try:
            run(args)
        except Exception as error:
            if args.output.is_dir():
                write_json(args.output / "failure.json", {"error": repr(error), "time_unix": time.time()})
            raise


if __name__ == "__main__":
    main()
