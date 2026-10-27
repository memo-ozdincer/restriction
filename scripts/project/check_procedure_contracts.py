#!/usr/bin/env python3
"""CPU-only closed atomic-contract checks; leaves production verification alone.

Hypothesis: a closed one-row shear certificate and an explicit-premise adapter
can be accepted while renamed binders preserve the elaborated interface and
changed types/let values, missing premises, admissions and new axioms do not.
This is an instrument test, not model evidence or a frozen training bank.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import platform
import signal
import subprocess
import time


REPO = Path(__file__).resolve().parents[2]
FIXTURES = REPO / "research" / "contracts"
ALLOWLIST = {"propext", "Classical.choice", "Quot.sound"}
CASES = {
    "AtomicShear": None,
    "RejectMissingPremise": "type mismatch",
    "RejectIncompatibleAdapter": "type mismatch",
    "RejectSorry": "CONTRACT_AUDIT_FORBIDDEN_AXIOM: sorryAx",
    "RejectFreshAxiom": "CONTRACT_AUDIT_FORBIDDEN_AXIOM: fresh_untrusted_axiom",
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def parse_records(stdout: str) -> list[dict]:
    """Parse instrument JSON only; never parse binders or infer Lean acceptance."""
    marker = "CONTRACT_JSON:"
    return [json.loads(line.split(marker, 1)[1]) for line in stdout.splitlines()
            if marker in line]


def validate_records(records: list[dict]) -> dict:
    certificates = {r["name"]: r for r in records if r["kind"] == "closed_certificate"}
    expected = {"atomic_shear", "atomic_shear_renamed", "atomic_shear_rational",
                "atomic_shear_value_one", "atomic_shear_value_two", "shear_adapter",
                "no_adapter_without_premise", "no_incompatible_adapter"}
    if set(certificates) != expected or len(records) != 11:
        raise ValueError("missing, duplicate, or unexpected closed certificate/comparison")
    for cert in certificates.values():
        if set(cert["axioms"]) - ALLOWLIST:
            raise ValueError("untrusted axiom in certificate")
        encoded = json.dumps(cert["interface"], sort_keys=True, separators=(",", ":"))
        if "UNSUPPORTED_" in encoded:
            raise ValueError("interface contains unresolved/open state")
        cert["alpha_interface_sha256"] = hashlib.sha256(encoded.encode()).hexdigest()
    comparisons = {(r["lhs"], r["rhs"]): r for r in records
                   if r["kind"] == "interface_comparison"}
    for pair, expected_equal in [
        (("atomic_shear", "atomic_shear_renamed"), True),
        (("atomic_shear", "atomic_shear_rational"), False),
        (("atomic_shear_value_one", "atomic_shear_value_two"), False),
    ]:
        comparison = comparisons[pair]
        if any(comparison[key] != expected_equal for key in
               ("kernel_definitionally_equal", "alpha_canonical_equal")):
            raise ValueError(f"unexpected elaborated interface comparison: {pair}")
    usage = {r["binder_index"]: r["used_in_body"]
             for r in certificates["shear_adapter"]["proof_binder_usage"]}
    if not usage.get(6) or not usage.get(7):
        raise ValueError("adapter witness does not use both recorded input facts")
    return {"certificates": certificates, "comparisons": list(comparisons.values()),
            "adapter_premise_binder_indices": [6, 7]}


def command_output(command: list[str], cwd: Path, env: dict) -> str:
    return subprocess.check_output(command, cwd=cwd, env=env, text=True,
                                   stderr=subprocess.STDOUT, timeout=30).strip()


def run_checks(output: Path, bundle: Path, timeout: float) -> dict:
    output.mkdir(parents=True, exist_ok=False)
    started = time.monotonic()
    mathlib = bundle / "verifier" / "DeepSeek-Prover-V1.5" / "mathlib4"
    elan = bundle / "lean" / "elan"
    lake = elan / "bin" / "lake"
    env = dict(os.environ, ELAN_HOME=str(elan),
               PATH=str(elan / "bin") + os.pathsep + os.environ.get("PATH", ""))
    metadata = {
        "hypothesis": __doc__.split("Hypothesis: ", 1)[1].strip(),
        "scope": "training-permitted one-row shear atom and adapter only",
        "model_revision": None, "dataset_path": None, "seed": None,
        "model_proposals": 0, "training_examples": 0, "gpu_jobs": 0,
        "hardware": {"host": platform.node(), "machine": platform.machine(),
                     "processor": platform.processor(), "cpu_count": os.cpu_count()},
        "git_commit": command_output(["git", "rev-parse", "HEAD"], REPO, env),
        "git_status": command_output(["git", "status", "--short"], REPO, env),
        "mathlib_commit": command_output(["git", "rev-parse", "HEAD"], mathlib, env),
        "mathlib_status": command_output(["git", "status", "--short"], mathlib, env),
        "lean_version": command_output([str(lake), "env", "lean", "--version"], mathlib, env),
        "toolchain": (mathlib / "lean-toolchain").read_text().strip(),
        "lake_manifest_sha256": sha256(mathlib / "lake-manifest.json"),
        "checker_sha256": sha256(Path(__file__).resolve()),
        "lean_binary_sha256": sha256(elan / "toolchains" / "leanprover--lean4---v4.9.0-rc1" / "bin" / "lean"),
        "toolchain_file_sha256": sha256(mathlib / "lean-toolchain"),
        "allowed_axioms": sorted(ALLOWLIST), "timeout_seconds_per_case": timeout,
        "bundle": str(bundle), "fixture_hashes": {},
        "environment_fingerprint_limit": "Provenance is not a hash of every transitive olean; "
            "interface hashes are scoped to this pinned runtime and are not semantic IDs.",
    }
    (output / "config.json").write_text(json.dumps(metadata, indent=2) + "\n")
    if metadata["toolchain"] != "leanprover/lean4:v4.9.0-rc1" or "4.9.0-rc1" not in metadata["lean_version"]:
        raise ValueError("wrong Lean environment: require pinned v4.9.0-rc1")
    prelude = (FIXTURES / "ClosedAudit.lean").read_text()
    results = []
    positive = None
    for name, expected_error in CASES.items():
        fixture = FIXTURES / f"{name}.lean"
        source = output / f"{name}.lean"
        source.write_text(prelude + "\n" + fixture.read_text())
        metadata["fixture_hashes"][fixture.name] = sha256(fixture)
        case_start = time.monotonic()
        command = [str(lake), "env", "lean", f"--root={output}",
                   "-o", str(output / f"{name}.olean"), str(source)]
        timed_out = False
        proc = subprocess.Popen(command, cwd=mathlib, env=env, text=True,
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                start_new_session=True)
        try:
            stdout, stderr = proc.communicate(timeout=timeout)
            returncode = proc.returncode
        except subprocess.TimeoutExpired:
            # lake launches Lean as a child: kill the process group, not just lake.
            os.killpg(proc.pid, signal.SIGKILL)
            stdout, stderr = proc.communicate()
            returncode, timed_out = None, True
        (output / f"{name}.stdout.log").write_text(stdout)
        (output / f"{name}.stderr.log").write_text(stderr)
        result = {"case": name, "command": command, "source_sha256": sha256(source),
                  "exit_code": returncode, "timed_out": timed_out,
                  "wall_seconds": time.monotonic() - case_start,
                  "expected_error": expected_error, "passed": False}
        if expected_error is None:
            try:
                if returncode != 0 or timed_out:
                    raise ValueError("positive Lean compilation failed")
                positive = validate_records(parse_records(stdout))
                result["passed"] = True
                result["olean_sha256"] = sha256(output / f"{name}.olean")
            except (ValueError, KeyError) as exc:
                result["validation_error"] = str(exc)
        else:
            result["passed"] = (positive is not None and returncode is not None and returncode != 0
                                and expected_error in stdout + stderr and not timed_out)
        results.append(result)
        print(f"{name}: {'PASS' if result['passed'] else 'FAIL'} "
              f"(Lean exit={returncode}, {result['wall_seconds']:.2f}s)", flush=True)
    metadata["fixture_hashes"]["ClosedAudit.lean"] = sha256(FIXTURES / "ClosedAudit.lean")
    (output / "config.json").write_text(json.dumps(metadata, indent=2) + "\n")
    report = {"complete": all(r["passed"] for r in results), "cases": results,
              "closed_interfaces": positive, "physical_lean_calls": len(results) + 1,
              "wall_seconds": time.monotonic() - started,
              "unsupported": ["arbitrary tactic-state extraction", "shared metavariable cuts",
                              "multiple focused goals", "polymorphic interface comparison",
                              "general semantic equivalence", "model or training claims"]}
    (output / "report.json").write_text(json.dumps(report, indent=2) + "\n")
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--bundle", type=Path, default=REPO.parent)
    parser.add_argument("--timeout", type=float, default=120.0)
    args = parser.parse_args()
    report = run_checks(args.output.resolve(), args.bundle.resolve(), args.timeout)
    raise SystemExit(0 if report["complete"] else 1)


if __name__ == "__main__":
    main()
