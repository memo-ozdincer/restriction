#!/usr/bin/env python3
"""Verify every archived payload against the recovery inventory, without extraction."""
import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import subprocess
import tarfile


def verify(inventory, archive):
    expected = {r["archive_path"]: r for r in inventory["files"]
                if r["asset"] == archive.name}
    if not expected:
        raise ValueError(f"No inventory entries for {archive.name}")
    seen = {}
    process = subprocess.Popen(["zstd", "-dc", str(archive)], stdout=subprocess.PIPE)
    try:
        with tarfile.open(fileobj=process.stdout, mode="r|") as stream:
            for member in stream:
                name = member.name
                if PurePosixPath(name).is_absolute() or ".." in PurePosixPath(name).parts:
                    raise ValueError(f"Unsafe archive path: {name}")
                if name in seen or name not in expected:
                    raise ValueError(f"Unexpected or duplicate member: {name}")
                if member.islnk():
                    if member.linkname not in seen:
                        raise ValueError(f"Unresolved hard link: {name}")
                    size, digest = seen[member.linkname]
                elif member.isfile():
                    digest = hashlib.sha256()
                    size = 0
                    with stream.extractfile(member) as data:
                        for block in iter(lambda: data.read(4 * 1024**2), b""):
                            digest.update(block)
                            size += len(block)
                    digest = digest.hexdigest()
                else:
                    raise ValueError(f"Unexpected member type: {name}")
                record = expected[name]
                if size != record["size"] or digest != record["sha256"]:
                    raise ValueError(f"Payload checksum mismatch: {name}")
                seen[name] = size, digest
        # Drain tar padding before closing the decompressor's pipe.
        while process.stdout.read(1024 * 1024):
            pass
        if process.wait() != 0:
            raise ValueError(f"Decompression failed: {archive}")
        if set(seen) != set(expected):
            raise ValueError(f"Missing archive members: {sorted(set(expected) - set(seen))}")
        return {"archive": archive.name, "files_verified": len(seen),
                "payload_bytes_verified": sum(x[0] for x in seen.values())}
    finally:
        process.stdout.close()
        if process.poll() is None:
            process.terminate()
        process.wait()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("inventory", type=Path)
    parser.add_argument("archives", type=Path, nargs="+")
    args = parser.parse_args()
    inventory = json.loads(args.inventory.read_text())
    for archive in args.archives:
        print(json.dumps(verify(inventory, archive)), flush=True)


if __name__ == "__main__":
    main()
