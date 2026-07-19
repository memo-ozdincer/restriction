#!/usr/bin/env python3
"""Freeze a dominance archive from persisted, verified C0 training proofs."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from verl.lean.mode_archive import ModeArchive
from verl.lean.proof_modes import mode_id


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def build_archive(proof_paths: list[Path], metadata: dict) -> ModeArchive:
    archive = ModeArchive(metadata=metadata)
    for path in proof_paths:
        with path.open(encoding="utf-8") as stream:
            for line_number, line in enumerate(stream, start=1):
                record = json.loads(line)
                if not record.get("correct", False):
                    continue
                try:
                    archive.add(record["theorem_name"], mode_id(record["proof"]))
                except KeyError as error:
                    raise ValueError(f"{path}:{line_number} lacks {error.args[0]!r}") from error
    return archive


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--proofs", required=True, action="append", type=Path,
                        help="C0 training proof JSONL (repeat for multiple snapshots)")
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--model-revision", required=True)
    parser.add_argument("--dataset", required=True, type=Path)
    parser.add_argument("--dataset-sha256", required=True)
    parser.add_argument("--seed", required=True, type=int)
    parser.add_argument("--source-run", required=True)
    args = parser.parse_args()

    for path in args.proofs:
        if not path.is_file():
            parser.error(f"proof log does not exist: {path}")
    if sha256(args.dataset) != args.dataset_sha256:
        parser.error("dataset SHA-256 does not match --dataset-sha256")

    archive = build_archive(args.proofs, {
        "signature_version": "mode_id_v1",
        "source_condition": "c0_base",
        "source_run": args.source_run,
        "data_split": "train",
        "model_revision": args.model_revision,
        "dataset": str(args.dataset),
        "dataset_sha256": args.dataset_sha256,
        "seed": args.seed,
        "proof_logs": [str(path) for path in args.proofs],
    })
    checksum = archive.save(args.output)
    args.output.with_suffix(args.output.suffix + ".sha256").write_text(checksum + "\n", encoding="utf-8")
    print(json.dumps({"archive": str(args.output), "sha256": checksum, "theorems": len(archive.counts)}, sort_keys=True))


if __name__ == "__main__":
    main()
