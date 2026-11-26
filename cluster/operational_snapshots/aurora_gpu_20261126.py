#!/usr/bin/env python3
"""Run one RCC command on one explicitly selected, currently unused GPU.

The advisory lock coordinates RCC launches only; it is not a scheduler reservation.
Never stop or change existing processes to make room for an experiment.
"""

import argparse
import csv
import fcntl
import json
import os
from pathlib import Path
import re
import subprocess
import sys
from datetime import datetime, timezone


def inventory():
    result = subprocess.run(
        ["nvidia-smi", "--query-gpu=uuid,memory.used,utilization.gpu", "--format=csv,noheader,nounits"],
        capture_output=True, text=True, check=True,
    )
    return {row[0].strip(): (int(row[1]), int(row[2])) for row in csv.reader(result.stdout.splitlines())}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--gpu", required=True, help="Full GPU UUID, never an implicit all-GPU launch")
    parser.add_argument("--run-id", required=True)
    parser.add_argument("command", nargs=argparse.REMAINDER)
    args = parser.parse_args()
    if not re.fullmatch(r"GPU-[a-f0-9-]{36}", args.gpu):
        parser.error("Use a full GPU UUID from nvidia-smi")
    if not re.fullmatch(r"[a-z0-9][a-z0-9_-]{0,90}", args.run_id):
        parser.error("Use a short lowercase run ID")
    command = args.command[1:] if args.command[:1] == ["--"] else args.command
    if not command:
        parser.error("A command is required after --")
    root = Path(os.environ["RCC_SCRATCH_ROOT"])
    locks = root / "locks"
    locks.mkdir(parents=True, exist_ok=True)
    with (locks / (args.gpu + ".lock")).open("a+") as lock:
        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            raise SystemExit("Another RCC launch holds this GPU lock") from None
        if inventory().get(args.gpu) != (0, 0):
            raise SystemExit("GPU is missing or not idle with zero allocated memory; nothing stopped")
        processes = subprocess.run(
            ["nvidia-smi", "--query-compute-apps=gpu_uuid", "--format=csv,noheader"],
            capture_output=True, text=True, check=True,
        ).stdout
        if args.gpu in processes:
            raise SystemExit("GPU has a compute process; nothing stopped")
        env = dict(os.environ, CUDA_VISIBLE_DEVICES=args.gpu, CUDA_DEVICE_ORDER="PCI_BUS_ID")
        record_path = locks / (args.run_id + ".json")
        record = {
            "run_id": args.run_id, "gpu_uuid": args.gpu, "uid": os.getuid(),
            "launcher_pid": os.getpid(), "started_utc": datetime.now(timezone.utc).isoformat(),
            "status": "starting", "command_executable": command[0],
        }
        # No environment or full command dump: either could contain credentials.
        with record_path.open("x") as out:
            json.dump(record, out, indent=2)
        child = subprocess.Popen(command, env=env)
        record.update(status="running", child_pid=child.pid)
        record_path.write_text(json.dumps(record, indent=2) + "\n")
        try:
            code = child.wait()
        except KeyboardInterrupt:
            # Only the exact child created here is eligible for termination.
            child.terminate()
            code = child.wait(timeout=30)
        record.update(status="finished", exit_code=code,
                      finished_utc=datetime.now(timezone.utc).isoformat())
        record_path.write_text(json.dumps(record, indent=2) + "\n")
        return code


if __name__ == "__main__":
    sys.exit(main())
