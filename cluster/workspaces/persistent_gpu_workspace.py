#!/usr/bin/env python3
"""Keep an authorized Slurm allocation alive for manually launched experiments."""

import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import signal
import socket
import subprocess
import threading


def timestamp():
    return datetime.now(timezone.utc).isoformat()


def command(args):
    result = subprocess.run(args, capture_output=True, text=True, timeout=20)
    return {"returncode": result.returncode, "stdout": result.stdout.strip(),
            "stderr": result.stderr.strip()}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-dir", type=Path, required=True)
    args = parser.parse_args()
    if not os.environ.get("SLURM_JOB_ID") or os.environ.get("SLURM_JOB_ACCOUNT") != "def-zhijing":
        parser.error("This keeper requires a live def-zhijing Slurm allocation.")
    stop = threading.Event()
    received = []

    def request_stop(signum, _frame):
        received.append(signum)
        stop.set()

    for signum in (signal.SIGTERM, signal.SIGINT, signal.SIGHUP):
        signal.signal(signum, request_stop)

    heartbeat = args.run_dir / "heartbeat.json"
    events = args.run_dir / "events.jsonl"
    with events.open("a", buffering=1) as stream:
        stream.write(json.dumps({"event": "keeper_started", "timestamp": timestamp(),
                                 "pid": os.getpid(), "node": socket.gethostname()}) + "\n")
        while not stop.is_set():
            sample = {
                "timestamp": timestamp(), "job_id": os.environ["SLURM_JOB_ID"],
                "account": os.environ["SLURM_JOB_ACCOUNT"], "node": socket.gethostname(),
                "pid": os.getpid(),
                "meminfo": Path("/proc/meminfo").read_text(),
            }
            try:
                sample["gpu"] = command([
                    "nvidia-smi", "--query-gpu=index,name,memory.used,memory.total,utilization.gpu",
                    "--format=csv,noheader,nounits",
                ])
            except (OSError, subprocess.TimeoutExpired) as exc:
                sample["gpu_error"] = str(exc)
            temporary = heartbeat.with_suffix(".tmp")
            temporary.write_text(json.dumps(sample, indent=2) + "\n")
            temporary.replace(heartbeat)
            # Interruptible equivalent of an infinite sleep, bounded by Slurm.
            stop.wait(60)
        stream.write(json.dumps({"event": "keeper_stopped", "timestamp": timestamp(),
                                 "signals": received}) + "\n")


if __name__ == "__main__":
    main()
