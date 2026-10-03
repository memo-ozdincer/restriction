#!/usr/bin/env python3
"""Run an unchanged training command for a bounded operational prefix."""

import argparse
import json
import os
from pathlib import Path
import re
import signal
import subprocess
import time


STEP = re.compile(r"\bstep:(\d+) - num_accepted:")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--log", required=True, type=Path)
    parser.add_argument("--status", required=True, type=Path)
    parser.add_argument("--stop-step", type=int, default=20)
    parser.add_argument("--max-seconds", type=int, default=6000)
    parser.add_argument("command", nargs=argparse.REMAINDER)
    args = parser.parse_args()
    if not args.command or args.command[0] != "--" or len(args.command) < 2:
        parser.error("pass the command after --")
    command = args.command[1:]
    if args.log.exists() or args.status.exists():
        parser.error("refusing to reuse log or status path")
    if args.stop_step < 1 or args.max_seconds < 1:
        parser.error("stop step and max seconds must be positive")

    started = time.monotonic()
    last_step = 0
    stop_reason = None
    with args.log.open("w", buffering=1) as output:
        process = subprocess.Popen(command, stdout=output, stderr=subprocess.STDOUT,
                                   start_new_session=True)
        with args.log.open("r") as reader:
            while True:
                for line in reader:
                    match = STEP.search(line)
                    if match:
                        last_step = max(last_step, int(match.group(1)))
                if last_step >= args.stop_step:
                    stop_reason = "completed_step_boundary"
                    break
                if process.poll() is not None:
                    break
                if time.monotonic() - started >= args.max_seconds:
                    stop_reason = "time_cap"
                    break
                time.sleep(2)
        if stop_reason is not None and process.poll() is None:
            os.killpg(process.pid, signal.SIGTERM)
            try:
                process.wait(timeout=30)
            except subprocess.TimeoutExpired:
                os.killpg(process.pid, signal.SIGKILL)
                process.wait()
        else:
            process.wait()
    status = {
        "classification": "operational_prefix_only_not_scientific_result",
        "stop_reason": stop_reason or "command_exited_before_boundary",
        "last_completed_step": last_step,
        "requested_stop_step": args.stop_step,
        "elapsed_seconds": round(time.monotonic() - started, 3),
        "child_returncode": process.returncode,
        "command": command,
    }
    args.status.write_text(json.dumps(status, indent=2) + "\n")
    return 0 if stop_reason == "completed_step_boundary" else 1


if __name__ == "__main__":
    raise SystemExit(main())
