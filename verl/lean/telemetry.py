"""Deterministic observational telemetry for generated Lean proposals."""

from __future__ import annotations

import hashlib
import json
from typing import Any

from verl.lean.proof_modes import exact_proof_id, mode_id, tactic_heads


def _sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _sha256_json(value: Any) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return _sha256_text(payload)


def telemetry_identity(resolved_config: str, environment: dict[str, Any]) -> tuple[str, str]:
    """Hash the resolved run config and the execution identity that interprets it."""
    config_sha256 = _sha256_text(resolved_config)
    environment_sha256 = _sha256_json({
        "resolved_config_sha256": config_sha256,
        **environment,
    })
    return config_sha256, environment_sha256


def build_proposal_telemetry(
    *,
    run_id: str,
    batch_id: str,
    theorem_index: int,
    candidate_index: int,
    theorem_name: str,
    theorem_statement: str,
    context: str,
    proof: str,
    response_token_count: int,
    verifier_result: dict[str, Any],
    resolved_config_sha256: str,
    environment_sha256: str,
) -> dict[str, Any]:
    """Build auditable fields without altering generation or Lean acceptance.

    All persisted time values are elapsed seconds. ``parse_time`` measures
    wrapper code-fence extraction, not Lean tactic execution.
    """
    proposal_id = _sha256_json({
        "run_id": run_id,
        "batch_id": batch_id,
        "theorem_index": theorem_index,
        "candidate_index": candidate_index,
    })
    theorem_hash = _sha256_json({
        "theorem_name": theorem_name,
        "theorem_statement": theorem_statement,
        "context": context,
    })
    return {
        "proposal_id": proposal_id,
        "theorem_hash": theorem_hash,
        "proof_hash": _sha256_text(proof),
        "batch_id": batch_id,
        "theorem_index_in_batch": theorem_index,
        "candidate_index": candidate_index,
        "token_count": response_token_count,
        "parse_time": verifier_result.get("parse_time_seconds"),
        "queue_wait_time": verifier_result.get("queue_wait_time_seconds"),
        "verification_time": verifier_result.get("verification_time_seconds"),
        "verdict": bool(verifier_result.get("verdict", False)),
        "lean_complete": bool(verifier_result.get("lean_complete", False)),
        "failure_class": verifier_result.get("failure_class"),
        "timed_out": bool(verifier_result.get("timed_out", False)),
        "worker_id": verifier_result.get("worker_id"),
        "verifier_error": verifier_result.get("verifier_error"),
        "tactic_prefix_signature": mode_id(proof),
        "tactic_heads": list(tactic_heads(proof)),
        "exact_proof_id": exact_proof_id(proof),
        "config_hash": resolved_config_sha256,
        "environment_hash": environment_sha256,
    }
