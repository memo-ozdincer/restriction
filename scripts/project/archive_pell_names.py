"""Preserve the terminal Pell interface experiment and its frozen execution code."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import tarfile


def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('bundle',type=Path);p.add_argument('output',type=Path)
    a=p.parse_args();b=a.bundle;r=b/'runs/pell-names-20261123-1399296'
    assert json.loads((r/'independent-audit.json').read_text())['passed']
    a.output.mkdir(parents=True,exist_ok=False)
    commit=(r/'commit').read_text().strip()
    frozen=a.output/'execution-source.tar'
    with frozen.open('wb') as f:
        subprocess.run(['git','-C',str(b/'repository'),'archive',commit,'scripts/project','cluster/workspaces'],stdout=f,check=True)
    paths=[p for p in r.rglob('*') if p.is_file()]
    workspace=b/'runs/interface-discovery-workspace-20261118-1399296'
    paths += [p for p in workspace.rglob('*') if p.is_file()]
    paths += [b/'repository/scripts/project'/n for n in ['audit_pell_names.py','archive_pell_names.py']]
    paths.append(frozen)
    assert all(not p.is_symlink() for p in paths)
    members={str(p.relative_to(b)):dict(sha256=sha(p),bytes=p.stat().st_size) for p in paths}
    archive=a.output/'pell-names-1399296.tar.gz'
    with tarfile.open(archive,'w:gz',compresslevel=6) as t:
        for p in paths:t.add(p,arcname=str(p.relative_to(b)),recursive=False)
    for p in paths:assert sha(p)==members[str(p.relative_to(b))]['sha256']
    inventory=dict(archive=archive.name,sha256=sha(archive),bytes=archive.stat().st_size,
        execution_commit=commit,members=members,
        parent_release='https://github.com/memo-ozdincer/restriction/releases/tag/pell-training-2026-11-23',
        parent_expression_adapter_sha256='8917953dfa3574cef4d4f8024a476d27d9671e135b817fc945f47328475e87fd')
    (a.output/'names-inventory.json').write_text(json.dumps(inventory,indent=2)+'\n')
    print(json.dumps({k:v for k,v in inventory.items() if k!='members'}))


if __name__=='__main__':main()
