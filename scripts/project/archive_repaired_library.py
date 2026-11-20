#!/usr/bin/env python3
"""Archive the complete repaired-library experiment and its input provenance."""
import argparse
import json
from pathlib import Path
import tarfile
from archive_policy_update_training import sha


def main():
    p = argparse.ArgumentParser(description=__doc__)
    for name in ['bundle', 'output']:
        p.add_argument('--' + name, type=Path, required=True)
    a = p.parse_args(); b = a.bundle
    workspace = b / 'runs/interface-discovery-workspace-20261118-1373856'
    run = workspace / 'repaired-library'
    assert json.loads((run / 'status.json').read_text())['state'] == 'complete'
    assert json.loads((run / 'independent-audit.json').read_text())['passed']
    launch = b / 'runs/repaired-library-launch-20261119-1373856'
    paths = [p for p in run.rglob('*') if p.is_file()]
    paths += [launch / n for n in ['source.tar', 'launch.json', 'ssh-command.json', 'ssh-result.json', 'driver.log']]
    paths += [workspace / n for n in ['allocation.json', 'keeper.py']]
    paths += [p for p in (b / 'runs/repaired-library-panel-20261119-final').rglob('*') if p.is_file()]
    paths += [b / 'runs/causal-state-repair-20261119' / n for n in ['manifest.json', 'analysis.json', 'proposals.json', 'independent-audit.json']]
    paths += [b / 'runs/policy-improvement-panel-20261119-fp32' / n for n in ['manifest.json', 'evaluation-tasks.json']]
    paths += [b / 'repository/scripts/project' / n for n in ['audit_repaired_library.py', 'archive_repaired_library.py', 'archive_policy_update_training.py']]
    paths = sorted(set(paths))
    assert all(p.is_file() and not p.is_symlink() for p in paths)
    inventory = {str(p.relative_to(b)): dict(bytes=p.stat().st_size, sha256=sha(p)) for p in paths}
    a.output.mkdir(parents=True, exist_ok=False)
    archive = a.output / 'repaired-library-20261119.tar.gz'
    with tarfile.open(archive, 'w:gz', compresslevel=6) as t:
        for p in paths:
            t.add(p, arcname=str(p.relative_to(b)), recursive=False)
    for p in paths:
        assert sha(p) == inventory[str(p.relative_to(b))]['sha256']
    record = dict(files=inventory, file_count=len(paths), logical_bytes=sum(v['bytes'] for v in inventory.values()),
                  archive=archive.name, archive_bytes=archive.stat().st_size, archive_sha256=sha(archive))
    (a.output / 'inventory.json').write_text(json.dumps(record, indent=2) + '\n')
    print(json.dumps({k: v for k, v in record.items() if k != 'files'}))


if __name__ == '__main__':
    main()
