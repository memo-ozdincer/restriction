"""Deterministic, dependency-free proof-mode identities.

These identities are operational tactic-head signatures, not claims about
semantic mathematical strategy.
"""

from __future__ import annotations

import hashlib
import json
import re

from verl.lean.utils import parse_proof_steps, remove_comments

def canonicalize_proof(proof: str) -> str:
    """Normalize a proof so comments, blank lines, and whitespace are ignored."""
    text = remove_comments(proof).strip()
    return "\n".join(" ".join(line.split()) for line in text.splitlines() if line.strip())


def tactic_heads(proof: str) -> tuple[str, ...]:
    """Return the top-level tactic head for each parsed proof step."""
    canonical = canonicalize_proof(proof)
    steps = parse_proof_steps(canonical, retain_comments=False)
    heads: list[str] = []
    for step in steps:
        line = step.strip()
        if line == "by":
            continue
        match = re.match(r"([A-Za-z_][A-Za-z0-9_'.]*)", line)
        if match:
            heads.append(match.group(1))
    return tuple(heads)


def mode_id(proof: str) -> str:
    """Hash the deterministic tactic-head signature."""
    payload = json.dumps(tactic_heads(proof), separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def exact_proof_id(proof: str) -> str:
    """Secondary identity for a normalized exact proof string."""
    return hashlib.sha256(canonicalize_proof(proof).encode("utf-8")).hexdigest()
