#!/usr/bin/env python3
"""Preserve both typed-composition attempts and exact component provenance."""
import argparse
import json
from pathlib import Path
import tarfile
from archive_policy_update_training import sha


def main():
    p = argparse.ArgumentParser(description=__doc__)
    for n in ['bundle', 'output']: p.add_argument('--' + n, type=Path, required=True)
    a = p.parse_args(); b = a.bundle
    run = b / 'runs/typed-procedure-composition-20261119-runtime-fixed'
    assert json.loads((run / 'independent-audit.json').read_text())['passed']
    paths = []
    for name in ['typed-procedure-composition-20261119', 'typed-procedure-composition-20261119-runtime-fixed']:
        paths += [p for p in (b / 'runs' / name).rglob('*') if p.is_file()]
    original = b / 'runs/interface-discovery-workspace-20261118-1373310/policy-improvement'
    paths += [original / n for n in ['traces.jsonl', 'matrix/edges.json', 'matrix/verdicts.jsonl']]
    paths += [b / 'runs/repaired-library-panel-20261119-final' / n for n in ['manifest.json', 'records.json']]
    paths += [b / 'repository/scripts/project' / n for n in ['typed_procedure_composition.py', 'audit_typed_procedure_composition.py', 'archive_typed_procedure_composition.py', 'interface_discovery_pilot.py', 'archive_policy_update_training.py']]
    paths = sorted(set(paths)); assert all(p.is_file() and not p.is_symlink() for p in paths)
    files = {str(p.relative_to(b)): dict(bytes=p.stat().st_size, sha256=sha(p)) for p in paths}
    a.output.mkdir(parents=True, exist_ok=False)
    archive = a.output / 'typed-procedure-composition-20261119.tar.gz'
    with tarfile.open(archive, 'w:gz', compresslevel=6) as t:
        for p in paths: t.add(p, arcname=str(p.relative_to(b)), recursive=False)
    for p in paths: assert sha(p) == files[str(p.relative_to(b))]['sha256']
    record = dict(files=files, file_count=len(paths), logical_bytes=sum(x['bytes'] for x in files.values()),
                  archive=archive.name, archive_bytes=archive.stat().st_size, archive_sha256=sha(archive))
    (a.output / 'inventory.json').write_text(json.dumps(record, indent=2) + '\n')
    print(json.dumps({k:v for k,v in record.items() if k != 'files'}))


if __name__ == '__main__': main()
