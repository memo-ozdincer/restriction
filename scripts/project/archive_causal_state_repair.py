#!/usr/bin/env python3
"""Package the completed causal repair and its original comparison evidence."""
import argparse
import json
from pathlib import Path
import tarfile
from archive_policy_update_training import sha


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for name in ['bundle','output']:p.add_argument('--'+name,type=Path,required=True)
    a=p.parse_args();b=a.bundle;r=b/'runs/causal-state-repair-20261119'
    m=json.loads((r/'manifest.json').read_text())
    assert json.loads((r/'independent-audit.json').read_text())['passed']
    original=b/'runs/interface-discovery-workspace-20261118-1373310/policy-improvement'
    paths=list(r.rglob('*'))+[original/name for name in m['input_sha256']]
    paths+=[b/'repository/scripts/project'/name for name in ['causal_state_repair.py',
        'audit_causal_state_repair.py','interface_discovery_pilot.py','archive_causal_state_repair.py',
        'archive_policy_update_training.py']]
    assert sha(b/'repository/scripts/project/causal_state_repair.py')==m['source_sha256']
    paths=sorted(set(p for p in paths if p.is_file()));assert all(not p.is_symlink() for p in paths)
    inventory={str(p.relative_to(b)):dict(bytes=p.stat().st_size,sha256=sha(p)) for p in paths}
    a.output.mkdir(parents=True,exist_ok=False);archive=a.output/'causal-state-repair-20261119.tar.gz'
    with tarfile.open(archive,'w:gz',compresslevel=6) as t:
        for p in paths:t.add(p,arcname=str(p.relative_to(b)),recursive=False)
    for p in paths:assert sha(p)==inventory[str(p.relative_to(b))]['sha256']
    record=dict(files=inventory,file_count=len(paths),logical_bytes=sum(v['bytes'] for v in inventory.values()),
        archive=archive.name,archive_bytes=archive.stat().st_size,archive_sha256=sha(archive))
    (a.output/'inventory.json').write_text(json.dumps(record,indent=2)+'\n')
    print(json.dumps({k:v for k,v in record.items() if k!='files'}))


if __name__=='__main__':main()
