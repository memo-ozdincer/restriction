#!/usr/bin/env python3
"""Evaluate the bounded C5 actor-loaded verifier diagnostic, never proof quality."""

import argparse
import hashlib
import json
from pathlib import Path
import re


STEP_RE = re.compile(r"\bstep:(\d+) - num_accepted:")
METRIC_RE = re.compile(r"(?:^|\s)([a-zA-Z][a-zA-Z0-9_/]*):(-?\d+(?:\.\d+)?)")
REQUIRED = (
    "num_accepted", "num_rejected", "num_blocked", "num_reward_rejected",
    "num_trained", "timing/verify_full_proof", "timing/step",
)
FATAL = re.compile(r"CUDA out of memory|RayOutOfMemoryError|OutOfMemoryError|worker.*killed", re.I)
REGISTERED_BASELINE_SHA256 = "dd9fb6552f0cc76db107d2c3a0cd3c68d8f0b843772b595e45ec13c005f4ad56"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def parse_steps(path: Path, through: int) -> tuple[dict[int, dict[str, float]], list[str]]:
    steps = {}
    fatal_lines = []
    with path.open(errors="replace") as stream:
        for line in stream:
            if FATAL.search(line):
                fatal_lines.append(line.strip()[:300])
            match = STEP_RE.search(line)
            if not match:
                continue
            step = int(match.group(1))
            if step > through:
                continue
            if step in steps:
                raise ValueError(f"duplicate step {step} in {path}")
            metrics = {key: float(value) for key, value in METRIC_RE.findall(line)}
            missing = [key for key in REQUIRED if key not in metrics]
            if missing:
                raise ValueError(f"step {step} missing metrics: {missing}")
            steps[step] = metrics
    return steps, fatal_lines


def parse_memory(path: Path) -> dict:
    samples = []
    with path.open() as stream:
        header = next(stream, "").rstrip("\n").split("\t")
        if header != ["timestamp", "mem_available_kib", "gpu_memory_used_mib", "repl_processes"]:
            raise ValueError("unexpected memory sample columns")
        for row in stream:
            cells = row.rstrip("\n").split("\t")
            if len(cells) != 4:
                raise ValueError("malformed memory sample")
            gpus = [int(value) for value in cells[2].split(";")]
            if len(gpus) != 4:
                raise ValueError("expected four GPU memory readings")
            samples.append((int(cells[1]), max(gpus), int(cells[3])))
    if not samples:
        raise ValueError("no memory samples")
    return {
        "samples": len(samples),
        "minimum_mem_available_gib": round(min(row[0] for row in samples) / 1024**2, 3),
        "peak_gpu_memory_mib": max(row[1] for row in samples),
        "peak_repl_processes": max(row[2] for row in samples),
    }


def evaluate(run: Path, baseline_log: Path, through: int = 20) -> dict:
    status_path = run / "stop_status.json"
    live_log = run / "run.log"
    memory_path = run / "memory.tsv"
    status = json.loads(status_path.read_text())
    live, fatal_lines = parse_steps(live_log, through)
    baseline, _ = parse_steps(baseline_log, through)
    expected = list(range(1, through + 1))
    errors = []
    if sorted(live) != expected:
        errors.append(f"live step sequence is {sorted(live)}, expected {expected}")
    if sorted(baseline) != expected:
        errors.append("historical baseline lacks the exact step sequence")
    if status.get("stop_reason") != "completed_step_boundary" or status.get("last_completed_step") != through:
        errors.append("diagnostic did not stop at the registered completed-step boundary")
    if status.get("classification") != "operational_prefix_only_not_scientific_result":
        errors.append("diagnostic classification mismatch")
    if fatal_lines:
        errors.append("fatal runtime pattern found in live log")
    for step, metrics in live.items():
        if metrics["num_accepted"] + metrics["num_rejected"] != 512:
            errors.append(f"step {step} does not account for 512 proposals")
        if metrics["num_blocked"] != metrics["num_reward_rejected"]:
            errors.append(f"step {step} blocked/reward-rejected counts differ")
        if metrics["num_accepted"] != metrics["num_trained"]:
            errors.append(f"step {step} accepted/trained counts differ")
    memory = parse_memory(memory_path)
    if memory["minimum_mem_available_gib"] < 128:
        errors.append("node available memory fell below the registered 128 GiB diagnostic floor")
    if memory["peak_gpu_memory_mib"] >= 81559:
        errors.append("sampled GPU memory reached the reported device capacity")

    baseline_verify = sum(row["timing/verify_full_proof"] for row in baseline.values())
    live_verify = sum(row["timing/verify_full_proof"] for row in live.values())
    speedup = baseline_verify / live_verify if live_verify > 0 else None
    # Amdahl-style planning calculation from the historical C5 steps 1-571.
    projected = ((23.708 - 17.958) + 17.958 / speedup) * 604 / 571 if speedup else None
    throughput_gate = speedup is not None and speedup >= 1.19 and projected <= 22.0
    return {
        "analysis": "c5_actorloaded64_operational_gate_v1",
        "classification": "operational_only_not_scientific_result",
        "run": str(run),
        "source_sha256": {"run_log": sha256(live_log), "baseline_log": sha256(baseline_log),
                          "memory": sha256(memory_path), "stop_status": sha256(status_path)},
        "registered_step_boundary": through,
        "last_completed_step": max(live, default=0),
        "memory": memory,
        "baseline_verify_seconds": round(baseline_verify, 3),
        "live_verify_seconds": round(live_verify, 3),
        "first_20_verify_speedup": round(speedup, 4) if speedup else None,
        "rough_604_logged_step_hours": round(projected, 3) if projected else None,
        "throughput_gate_1_19x_and_22h": throughput_gate,
        "operational_integrity_pass": not errors,
        "errors": errors,
        "fatal_lines": fatal_lines[:10],
        "limits": ["Different generated proofs and node conditions limit causal timing inference.",
                   "A 20-step prefix does not establish late-tail or checkpoint feasibility."],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run", type=Path, required=True)
    parser.add_argument("--baseline-log", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        parser.error("refusing to overwrite output")
    if sha256(args.baseline_log) != REGISTERED_BASELINE_SHA256:
        parser.error("historical C5 32-worker baseline log checksum mismatch")
    result = evaluate(args.run, args.baseline_log)
    args.output.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({key: result[key] for key in ("operational_integrity_pass",
          "throughput_gate_1_19x_and_22h", "first_20_verify_speedup", "errors")}, indent=2))
    return 0 if result["operational_integrity_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
