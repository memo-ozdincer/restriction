#!/usr/bin/env python3
"""Launch one approved execution screen when an existing Slurm workspace starts.

Never allocates, resubmits, retries a launch, trains, or cancels a Slurm job.
All source comes from a pinned commit, archived before the first polling wait.
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import pwd
import re
import shlex
import socket
import subprocess
import tarfile
import time


ROOT = Path(__file__).resolve().parents[2]
RUNNER = "scripts/project/run_execution_screen.py"
ANALYZER = "scripts/project/analyze_execution_pilot.py"
WAIT_STATES = {"PENDING", "CONFIGURING", "SUSPENDED", "RESIZING"}


def sha256(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def write_json(path, record):
    path = Path(path)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(record, sort_keys=True, indent=2) + "\n")
    temporary.replace(path)


def exclusive_record(path, record):
    """Durable fail-closed claim; an uncertain previous launch needs inspection."""
    with Path(path).open("x") as stream:
        json.dump(record, stream, sort_keys=True, indent=2)
        stream.write("\n")
        stream.flush()
        os.fsync(stream.fileno())


def validate_job(info, job_id, uid, username):
    fields = dict(re.findall(r"(?:^|\s)(\w+)=([^\s]+)", info))
    if fields.get("JobId") != str(job_id) or fields.get("Account") != "def-zhijing":
        raise ValueError("job does not match requested def-zhijing allocation")
    if fields.get("UserId") != f"{username}({uid})":
        raise ValueError("allocation is not owned by the current OS user")
    if fields.get("JobState") not in WAIT_STATES | {"RUNNING"}:
        raise ValueError(f"allocation cannot run the screen: {fields.get('JobState')}")
    return fields


def poll_until_running(query, update, *, max_wait_seconds=172800, poll_seconds=60,
                       monotonic=time.monotonic, sleep=time.sleep):
    deadline = monotonic() + max_wait_seconds
    while True:
        fields = query()
        if fields["JobState"] == "RUNNING":
            return fields
        remaining = deadline - monotonic()
        if remaining <= 0:
            raise TimeoutError("48-hour allocation wait expired; Slurm job was not cancelled")
        update("waiting", slurm_state=fields["JobState"], reason=fields.get("Reason"),
               estimated_start=fields.get("StartTime"), remaining_wait_seconds=remaining)
        sleep(min(poll_seconds, remaining))


def prepare_snapshot(repo, commit, watcher):
    if not re.fullmatch(r"[0-9a-f]{40}", commit):
        raise ValueError("commit must be a full 40-character SHA")
    subprocess.run(["git", "-C", str(repo), "cat-file", "-e", commit + "^{commit}"], check=True)
    for relative in (RUNNER, ANALYZER):
        subprocess.run(["git", "-C", str(repo), "cat-file", "-e", f"{commit}:{relative}"], check=True)
    archive = watcher / "source.tar"
    snapshot = watcher / "source"
    snapshot.mkdir(exist_ok=False)
    subprocess.run(["git", "-C", str(repo), "archive", "--format=tar", "--output", str(archive), commit], check=True)
    with tarfile.open(archive) as tar:
        for member in tar.getmembers():
            path = Path(member.name)
            if path.is_absolute() or ".." in path.parts or not (member.isfile() or member.isdir()):
                raise ValueError(f"unsupported source archive member: {member.name}")
        tar.extractall(snapshot, filter="data")
    for relative in (RUNNER, ANALYZER):
        expected = subprocess.check_output(["git", "-C", str(repo), "show", f"{commit}:{relative}"])
        if (snapshot / relative).read_bytes() != expected:
            raise ValueError(f"snapshot differs from pinned source: {relative}")
    for path in snapshot.rglob("*"):
        path.chmod(path.stat().st_mode & ~0o222)
    snapshot.chmod(snapshot.stat().st_mode & ~0o222)
    archive.chmod(0o444)
    return snapshot, sha256(archive)


def ssh_command(node, python, snapshot, args):
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9.-]*", node):
        raise ValueError("invalid Slurm-assigned hostname")
    remote = [str(python), "-B", "-u", str(snapshot / RUNNER),
              "--bundle", str(args.bundle), "--panel", str(args.panel_dir),
              "--output", str(args.output), "--job-id", str(args.job_id),
              "--commit", args.commit, "--panel-sha256", args.manifest_sha256]
    return ["ssh", "-n", "-T", "-o", "BatchMode=yes", "-o", "ConnectTimeout=15",
            "-o", "ServerAliveInterval=30", "-o", "ServerAliveCountMax=3",
            node, shlex.join(remote)]


def launch_once(command, marker, record, log, update, *, execute=subprocess.run):
    exclusive_record(marker, record | {"launch_attempted": True})
    update("starting", launch_attempted=True, node=record["node"], needs_inspection=False,
           pending_analysis=True)
    with Path(log).open("x") as stream:
        update("running", launch_attempted=True)
        # A transport failure can leave the remote process running. Never retry.
        result = execute(command, stdout=stream, stderr=subprocess.STDOUT, timeout=25200, check=False)
    if result.returncode != 0:
        raise RuntimeError(f"SSH/screen exited {result.returncode}; launch may have started; inspect durable logs before any retry")


def completed_logs(output):
    completion = output / "generation_complete.json"
    if not completion.is_file():
        raise ValueError("SSH exited successfully without generation completion certificate")
    generation = json.loads(completion.read_text())
    if (generation.get("trained_samples") != 0 or
            generation.get("status") != "generation_complete_pending_independent_analysis"):
        raise ValueError("unexpected generation completion certificate")
    witnesses = output / "witness_checks.json"
    checks = json.loads(witnesses.read_text())
    if checks.get("complete") is not True or checks.get("invalid_tasks") != []:
        raise ValueError("fresh witness/nonterminal certificate failed")
    logs = {}
    for label in ("practice", "diagnostic"):
        status_path = output / label / "process_status.json"
        status = json.loads(status_path.read_text())
        if status.get("completion_candidate") is not True or status.get("timed_out") is not False:
            raise ValueError(f"{label} process did not complete")
        log = Path(status["proof_log"]).resolve()
        if not log.is_relative_to(output.resolve()) or sha256(log) != status["proof_log_sha256"]:
            raise ValueError(f"{label} proof log is outside output or changed")
        logs[label] = log
    return logs, {str(path): sha256(path) for path in (
        completion, witnesses, output / "practice/process_status.json", output / "diagnostic/process_status.json")}


def run(args):
    for key in ("bundle", "panel_dir", "output", "watcher_output"):
        setattr(args, key, getattr(args, key).resolve())
    if args.job_id <= 0 or not re.fullmatch(r"[0-9a-f]{64}", args.manifest_sha256):
        raise ValueError("invalid job ID or manifest SHA-256")
    for path in (args.output, args.watcher_output):
        if not path.is_relative_to(args.bundle / "runs") or path == args.bundle / "runs":
            raise ValueError("output and watcher directory must be new shared bundle/runs paths")
        if path.exists():
            raise FileExistsError(f"refusing existing destination: {path}")
    if (args.output.is_relative_to(args.watcher_output) or args.watcher_output.is_relative_to(args.output)):
        raise ValueError("watcher and screen output must be separate, non-nested paths")
    manifest_path = args.panel_dir / "manifest.json"
    if sha256(manifest_path) != args.manifest_sha256:
        raise ValueError("panel manifest does not match pinned digest")
    manifest = json.loads(manifest_path.read_text())
    expected_logs = {}
    for split, label in (("train", "practice"), ("diagnostic", "diagnostic")):
        rows = sum(task["pilot_split"] == split and task["screen_samples"] > 0 for task in manifest["tasks"])
        expected_logs[label] = str(args.output / label / "artifacts/proofs" / f"global_step_{(rows + 15) // 16}.jsonl")
    args.watcher_output.mkdir(parents=True, exist_ok=False)
    state = {"job_id": args.job_id, "commit": args.commit, "panel": str(args.panel_dir),
             "panel_manifest_sha256": args.manifest_sha256, "output": str(args.output),
             "watcher_pid": os.getpid(), "watcher_host": socket.gethostname(),
             "watcher_script_sha256": sha256(__file__), "expected_proof_logs": expected_logs,
             "expected_analysis": str(args.output / "analysis.json"), "pending_analysis": False,
             "launch_attempted": False, "needs_inspection": False,
             "automatic_training": False, "automatic_job_submission": False}

    def update(status, **values):
        state.update(values, status=status, updated_utc=datetime.now(timezone.utc).isoformat())
        write_json(args.watcher_output / "status.json", state)

    uid = os.getuid()
    username = pwd.getpwuid(uid).pw_name

    def query():
        info = subprocess.check_output(["scontrol", "show", "job", str(args.job_id), "-o"], text=True, timeout=30)
        return validate_job(info, args.job_id, uid, username)

    try:
        update("preparing")
        query()  # Do not reserve or wait for a job owned by someone else.
        snapshot, archive_hash = prepare_snapshot(args.bundle / "repository", args.commit, args.watcher_output)
        state.update(snapshot=str(snapshot), source_archive_sha256=archive_hash)
        claim = args.bundle / "runs" / f"execution-screen-job-{args.job_id}.claim.json"
        exclusive_record(claim, state | {"watcher_output": str(args.watcher_output)})
        state["job_claim"] = str(claim)
        fields = poll_until_running(query, update)
        nodes = subprocess.check_output(["scontrol", "show", "hostnames", fields["NodeList"]], text=True, timeout=30).splitlines()
        if len(nodes) != 1:
            raise ValueError("expected exactly one assigned workspace node")
        current = query()  # Revalidate owner/account/state immediately before launch.
        if current["JobState"] != "RUNNING" or current["NodeList"] != fields["NodeList"]:
            raise ValueError("allocation changed immediately before launch")
        if args.output.exists() or sha256(manifest_path) != args.manifest_sha256:
            raise ValueError("screen output appeared or manifest changed while waiting")
        python = args.bundle / "environment/venv/bin/python"
        command = ssh_command(nodes[0], python, snapshot, args)
        write_json(args.watcher_output / "ssh_command.json", command)
        launch_once(command, args.watcher_output / "launch_attempt.json", state | {"node": nodes[0]},
                    args.watcher_output / "ssh.log", update)
        logs, certificates = completed_logs(args.output)
        analysis = args.output / "analysis.json"
        if analysis.exists():
            raise FileExistsError("refusing existing independent analysis")
        command = [str(python), "-B", str(snapshot / ANALYZER),
                   "--manifest", str(manifest_path), "--practice-log", str(logs["practice"]),
                   "--diagnostic-log", str(logs["diagnostic"]), "--output", str(analysis)]
        write_json(args.watcher_output / "analysis_command.json", command)
        update("running", pending_analysis=True, proof_logs={k: str(v) for k, v in logs.items()}, certificates=certificates)
        env = os.environ.copy()
        env.update(PYTHONPATH=str(snapshot), PYTHONDONTWRITEBYTECODE="1")
        with (args.watcher_output / "analysis.log").open("x") as stream:
            subprocess.run(command, stdout=stream, stderr=subprocess.STDOUT, env=env,
                           cwd=snapshot, timeout=1800, check=True)
        result = json.loads(analysis.read_text())
        update("complete", pending_analysis=False, analysis=str(analysis),
               analysis_sha256=sha256(analysis), gate=result["gate"], needs_inspection=False)
    except TimeoutError as error:
        update("timeout", error=repr(error), job_cancelled=False)
        raise
    except BaseException as error:
        update("failed", error=repr(error), needs_inspection=bool(state["launch_attempted"]),
               automatic_retry=False, pending_analysis=state.get("pending_analysis", False))
        raise


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bundle", type=Path, default=ROOT.parent)
    parser.add_argument("--job-id", type=int, required=True)
    parser.add_argument("--commit", required=True)
    parser.add_argument("--panel-dir", type=Path, required=True)
    parser.add_argument("--manifest-sha256", required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--watcher-output", type=Path, required=True)
    run(parser.parse_args())


if __name__ == "__main__":
    main()
