#!/usr/bin/env python3
"""Fail closed if a Restriction-RL transfer bundle is incomplete."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path


MODEL_REVISION = "e9a6e6fbb67620d4e9c4944bc51ff7c435af12da"
BASE_FILES = {
    "model-00001-of-000002.safetensors": "a8fc709546d75ee3440d402d6b2431d6b52e98d63befba1a99b3f230d859f649",
    "model-00002-of-000002.safetensors": "90602e9cb2983b429020f4186693872cad0fe3ea31690b45e94c49efa6688b89",
    "config.json": "9700b800d54caa843f1682982301e8e86ee26710b943d9c88ba9a7f257911ab5",
    "tokenizer.json": "41f3bf64213da8c012d8bd0871a58a1fdf70463e8f08f110ddbb1082f529f669",
}
DATA_SHA256 = "56799bc5a19c4ccc0c671dd8631a16c0956786ae63ba5d4e30e9f30b7bbcc9eb"
ARCHIVE_SHA256 = "fcffb4a3dc9baf837d4780ec30855308ebc7f0c5086d607162889938b5e426d3"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def require(path: Path) -> None:
    if not path.exists():
        raise FileNotFoundError(path)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("bundle", type=Path)
    parser.add_argument("--full-checksums", action="store_true")
    parser.add_argument(
        "--verify-manifest",
        action="store_true",
        help="verify every file recorded in MANIFEST.sha256",
    )
    args = parser.parse_args()
    root = args.bundle.resolve()

    required = [
        root / "repository/.git",
        root / "repository/data/mff-lwb-10k-seen.parquet",
        root / "models/base/model.safetensors.index.json",
        root / "models/c1-final/model.safetensors.index.json",
        root / "models/c3-final/model.safetensors.index.json",
        root / "verifier/DeepSeek-Prover-V1.5/mathlib4/.lake/build",
        root / "lean/elan/toolchains/leanprover--lean4---v4.9.0-rc1",
        root / "environment/venv/bin/python",
        root / "runs/c0-base-20260804-seed42-complete/mode_archive.json",
    ]
    for path in required:
        require(path)

    if sha256(root / "repository/data/mff-lwb-10k-seen.parquet") != DATA_SHA256:
        raise ValueError("registered dataset checksum mismatch")
    if sha256(root / "runs/c0-base-20260804-seed42-complete/mode_archive.json") != ARCHIVE_SHA256:
        raise ValueError("C0 archive checksum mismatch")
    if args.full_checksums:
        for name, expected in BASE_FILES.items():
            if sha256(root / "models/base" / name) != expected:
                raise ValueError(f"base-model checksum mismatch: {name}")

    if args.verify_manifest:
        manifest = root / "MANIFEST.sha256"
        require(manifest)
        for line_number, line in enumerate(manifest.read_text().splitlines(), 1):
            expected, separator, relative_text = line.partition("  ")
            if not separator:
                raise ValueError(f"malformed manifest line {line_number}")
            relative = Path(relative_text)
            if relative.is_absolute() or ".." in relative.parts:
                raise ValueError(f"unsafe manifest path on line {line_number}")
            path = root / relative
            require(path)
            if sha256(path) != expected:
                raise ValueError(f"bundle checksum mismatch: {relative}")

    env = os.environ.copy()
    env["PYTHONPATH"] = str(root / "repository")
    python = root / "environment/venv/bin/python"
    probe = subprocess.check_output(
        [
            str(python),
            "-c",
            (
                "import importlib.metadata as m, json, platform, torch; "
                "names=['torch','nvidia-cudnn-cu12','nvidia-nccl-cu12',"
                "'transformers','vllm','ray','tensordict','flash-attn',"
                "'xformers','triton']; "
                "versions={n:m.version(n) for n in names}; "
                "versions.update({'python': platform.python_version(), "
                "'torch_cuda': torch.version.cuda, "
                "'torch_cudnn': torch.backends.cudnn.version()}); "
                "print(json.dumps(versions, sort_keys=True))"
            ),
        ],
        env=env,
        text=True,
    )
    versions = json.loads(probe)
    expected_versions = {
        "python": "3.11.4",
        "torch": "2.3.0",
        "torch_cuda": "12.1",
        "torch_cudnn": 8902,
        "nvidia-cudnn-cu12": "8.9.2.26",
        "nvidia-nccl-cu12": "2.19.3",
        "transformers": "4.40.1",
        "vllm": "0.4.2",
        "ray": "2.38.0",
        "tensordict": "0.3.1",
        "flash-attn": "2.5.8",
        "xformers": "0.0.26.post1",
        "triton": "2.2.0",
    }
    if versions != expected_versions:
        raise ValueError(f"runtime version mismatch: {versions!r}")

    print(json.dumps({"bundle": str(root), "model_revision": MODEL_REVISION, "versions": versions}, indent=2))


if __name__ == "__main__":
    main()
