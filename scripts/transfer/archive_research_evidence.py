#!/usr/bin/env python3
"""Archive project evidence without weights, environments, or private sessions.

Writes three zstd tarballs, an exact SHA-256 inventory, and explicit omissions.
Run against a quiescent bundle. Existing output files are never overwritten.
No upload or scheduler action is performed. Git history is backed up separately.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import tempfile


SECRET_PATTERNS = [
    rb"gh[pousr]_[A-Za-z0-9]{20,}",
    rb"github_pat_[A-Za-z0-9_]{20,}",
    rb"sk-(?:proj-)?[A-Za-z0-9_-]{24,}",
    rb"AKIA[0-9A-Z]{16}",
    rb"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----",
    rb"(?i)authorization:\s*bearer\s+[A-Za-z0-9_.-]{20,}",
]
SECRET = re.compile(b"|".join(b"(?:" + p + b")" for p in SECRET_PATTERNS)
                    .replace(b"(?i)", b""), re.IGNORECASE)
SECRET_MARKERS = (b"ghp_", b"gho_", b"ghu_", b"ghs_", b"ghr_", b"github_pat_",
                  b"sk-", b"akia", b"private key", b"authorization:")
WEIGHTS = {".safetensors", ".pt", ".pth", ".ckpt", ".bin", ".so"}
PRUNE = {".git", "__pycache__", "source", ".lake", "wandb", "ray_tmp"}


def inspect_file(path):
    before = path.stat()
    digest = hashlib.sha256()
    tail = b""
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(4 * 1024 * 1024), b""):
            window = tail + block
            lower = window.lower()
            if any(marker in lower for marker in SECRET_MARKERS) and SECRET.search(window):
                raise ValueError(f"Possible credential; inspect privately before publication: {path}")
            digest.update(block)
            tail = block[-512:]
    after = path.stat()
    if (before.st_size, before.st_mtime_ns) != (after.st_size, after.st_mtime_ns):
        raise ValueError(f"File changed during inventory: {path}")
    return {"size": after.st_size, "mtime_ns": after.st_mtime_ns,
            "sha256": digest.hexdigest()}


def collect(workspace, extra):
    bundle = workspace / "restriction-rl"
    candidates, omitted = [], []

    def add(path):
        if path.is_symlink():
            omitted.append({"path": str(path), "reason": "symlink; not followed",
                            "target": os.readlink(path)})
        elif path.is_file():
            if path.suffix in WEIGHTS or path.name.startswith((".env", "core.")):
                omitted.append({"path": str(path), "size": path.stat().st_size,
                                "reason": "weights, compiled output, or environment secrets"})
            else:
                candidates.append((path, path.relative_to(workspace).as_posix()))

    for path in workspace.iterdir():
        if path.is_file() and path.suffix in {".sh", ".py", ".sbatch", ".log", ".out", ".tsv"}:
            add(path)
    for path in (bundle / "repository").iterdir():
        if path.is_file() and path.suffix in {".log", ".out"}:
            add(path)
    for name in ["runs", "archives", "models", "publication-audit-20260920"]:
        for directory, dirs, files in os.walk(bundle / name, followlinks=False):
            for name in dirs[:]:
                path = Path(directory) / name
                if name in PRUNE or path.is_symlink():
                    dirs.remove(name)
                    omitted.append({"path": str(path), "reason": "rebuildable source/cache tree or symlink"})
            for name in files:
                add(Path(directory) / name)
    for path in bundle.iterdir():
        if path.is_file():
            add(path)
    for name in ["requirements.installed.txt", "requirements.lock.txt"]:
        add(bundle / "environment" / name)
    for name in ["environment", "lean", "runtime", "verifier"]:
        omitted.append({"path": str(bundle / name), "reason": "installed runtime/toolchain; selected environment locks included separately"})
    for path in sorted(extra.rglob("*")):
        if path.is_symlink():
            raise ValueError(f"Symlink in reviewed extras: {path}")
        if path.is_file():
            candidates.append((path, "recovered-session-evidence/" + path.relative_to(extra).as_posix()))
    return sorted(set(candidates)), omitted


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workspace", type=Path, required=True)
    parser.add_argument("--extra", type=Path, required=True,
                        help="Reviewed public project extracts, never a raw Codex directory")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=False)
    candidates, omitted = collect(args.workspace.resolve(), args.extra.resolve())
    entries = []
    for index, (source, archive_path) in enumerate(candidates):
        info = inspect_file(source)
        group = "large-proof-records" if info["size"] > 25 * 1024**2 and source.suffix in {".jsonl", ".json", ".log"} else "research-evidence"
        if source.suffix == ".olean" or source.parent == args.workspace.resolve() / "restriction-rl/repository":
            group = "historical-supplement"
        entries.append({"source": str(source), "archive_path": archive_path,
                        "asset": group + ".tar.zst", **info})
        if index % 100 == 0:
            print(f"Inventoried {index + 1}/{len(candidates)} files", flush=True)
    manifest = {"schema_version": 1, "date": "2026-11-18", "files": entries,
                "omissions": omitted, "credential_scan": "known-token and private-key patterns; not a guarantee"}
    (args.output / "evidence-inventory.json").write_text(json.dumps(manifest, indent=2) + "\n")
    # Hard links avoid copying GB of evidence. Preserve original bytes and names
    # in the tar; refuse source mutation after hashing and after archiving.
    with tempfile.TemporaryDirectory(prefix="rrl-evidence-stage-", dir=args.output.parent) as temporary:
        stage = Path(temporary)
        for entry in entries:
            dst = stage / entry["archive_path"]
            dst.parent.mkdir(parents=True, exist_ok=True)
            os.link(entry["source"], dst)
        for asset in sorted({e["asset"] for e in entries}):
            listing = args.output / (asset + ".files")
            listing.write_bytes(b"".join(e["archive_path"].encode() + b"\0" for e in entries if e["asset"] == asset))
            subprocess.run(["tar", "-I", "zstd -T2 -3", "-cf", str(args.output / asset),
                            "-C", str(stage), "--null", "-T", str(listing)], check=True)
            print(f"Created {asset}: {(args.output / asset).stat().st_size} bytes", flush=True)
    for entry in entries:
        stat = Path(entry["source"]).stat()
        if (stat.st_size, stat.st_mtime_ns) != (entry["size"], entry["mtime_ns"]):
            raise ValueError(f"Source changed; do not publish archive: {entry['source']}")
    print(f"Archived {len(entries)} files; omissions are explicit in evidence-inventory.json", flush=True)


if __name__ == "__main__":
    main()
