"""Persistent dominance counts for verified proof modes."""

from __future__ import annotations

import hashlib
import json
import os
from collections import Counter, defaultdict
from pathlib import Path
from typing import Iterable


ARCHIVE_SCHEMA_VERSION = 1


class ModeArchive:
    def __init__(self, counts: dict[str, dict[str, int]] | None = None, metadata: dict | None = None):
        self.counts: dict[str, Counter[str]] = defaultdict(Counter)
        self.metadata = dict(metadata or {})
        for theorem, modes in (counts or {}).items():
            self.counts[theorem].update({str(k): int(v) for k, v in modes.items()})

    def add(self, theorem_id: str, mode: str, *, correct: bool = True) -> None:
        if correct:
            self.counts[str(theorem_id)][str(mode)] += 1

    def dominant_mode(self, theorem_id: str, threshold: float = 0.5, min_verified: int = 4) -> str | None:
        modes = self.counts.get(str(theorem_id), Counter())
        total = sum(modes.values())
        if total < min_verified or not modes:
            return None
        mode, count = modes.most_common(1)[0]
        return mode if count / total > threshold else None

    def is_blocked(self, theorem_id: str, mode: str, threshold: float = 0.5, min_verified: int = 4) -> bool:
        return mode == self.dominant_mode(theorem_id, threshold, min_verified)

    def to_dict(self) -> dict[str, dict[str, int]]:
        return {k: dict(sorted(v.items())) for k, v in sorted(self.counts.items())}

    def payload(self) -> dict:
        return {
            "schema_version": ARCHIVE_SCHEMA_VERSION,
            "metadata": self.metadata,
            "counts": self.to_dict(),
        }

    def save(self, path: str | os.PathLike[str]) -> str:
        target = Path(path)
        target.parent.mkdir(parents=True, exist_ok=True)
        payload = json.dumps(self.payload(), sort_keys=True, indent=2) + "\n"
        target.write_text(payload, encoding="utf-8")
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()

    @classmethod
    def load(cls, path: str | os.PathLike[str]) -> "ModeArchive":
        payload = json.loads(Path(path).read_text(encoding="utf-8"))
        # No archive has been published yet, but accepting the prototype format
        # keeps local development artifacts readable.
        if "counts" not in payload:
            return cls(payload)
        if payload.get("schema_version") != ARCHIVE_SCHEMA_VERSION:
            raise ValueError(f"unsupported mode archive schema: {payload.get('schema_version')}")
        return cls(payload["counts"], payload.get("metadata"))
