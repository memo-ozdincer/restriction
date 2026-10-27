"""Auditable proof continuation inputs; prefixes are context, never actions.

This module does not certify prefix validity or semantic strategy membership.
The experiment preparing the dataset owns those checks.
"""

from __future__ import annotations

import hashlib
import json
from collections.abc import Mapping, Sequence


def proof_prefixes(problem_infos: Mapping, count: int, prompt_key: str) -> list[str]:
    """Read optional continuation contexts without coercing missing data to code."""
    values = problem_infos.get("proof_prefix")
    if values is None:
        return [""] * count
    if len(values) != count:
        raise ValueError("proof_prefix length differs from the problem batch")
    prefixes = list(values)
    if any(not isinstance(prefix, str) for prefix in prefixes):
        raise ValueError("proof_prefix values must be strings; use an empty string for no prefix")
    if any(prefixes) and prompt_key not in ("deepseek-prover", "deepseek-prover-cot"):
        raise ValueError("proof_prefix requires a DeepSeek proof-continuation prompt")
    if any("```" in prefix or "<｜begin▁of▁sentence｜>" in prefix for prefix in prefixes):
        raise ValueError("proof_prefix must contain only unfinished Lean proof code")
    return prefixes


def assemble_proofs(suffixes: Sequence[str], prefixes: Sequence[str], num_samples: int) -> list[str]:
    """Reconstruct verifier inputs without changing generated response tensors."""
    if num_samples <= 0 or len(suffixes) != len(prefixes) * num_samples:
        raise ValueError("prefix/suffix rollout counts do not agree")
    return [prefixes[index // num_samples] + suffix for index, suffix in enumerate(suffixes)]


def conditioning_id(theorem_statement: str, context: str, prefix: str) -> str:
    payload = json.dumps([theorem_statement, context, prefix], ensure_ascii=False, separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def prefix_record(*, theorem_statement: str, context: str, prefix: str,
                  suffix: str, prompt_token_count: int) -> dict:
    """Return continuation provenance only for an active prefix."""
    if not prefix:
        return {}
    return {
        "proof_prefix": prefix,
        "proof_prefix_sha256": hashlib.sha256(prefix.encode("utf-8")).hexdigest(),
        "generated_suffix": suffix,
        "conditioning_id": conditioning_id(theorem_statement, context, prefix),
        "prompt_token_count": int(prompt_token_count),
    }


def pilot_record(problem_infos: Mapping, index: int, prompt_token_count: int) -> dict:
    """Preserve registered row identity, including explicitly marked padding."""
    if "pilot_row_id" not in problem_infos:
        return {}
    row_id = problem_infos["pilot_row_id"][index]
    split = problem_infos["pilot_split"][index]
    if not isinstance(row_id, str) or not row_id or not isinstance(split, str) or not split:
        raise ValueError("pilot_row_id and pilot_split must be nonempty strings")
    return {
        "pilot_row_id": row_id,
        "pilot_split": split,
        "pilot_padding": bool(problem_infos["pilot_padding"][index]),
        "prompt_token_count": int(prompt_token_count),
    }
