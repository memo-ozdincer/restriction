"""Package the complete universal-constructor screen for portable recovery."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
import tarfile


def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('bundle',type=Path);p.add_argument('output',type=Path);a=p.parse_args();b=a.bundle
    run=b/'runs/universal-constructor-20261123-1399519'
    audit=json.loads((run/'experiment/independent-audit.json').read_text())
    assert audit['passed'] and audit['proposals']==128
    paths=[p for p in run.rglob('*') if p.is_file() and p.relative_to(run).parts[0]!='source']
    for name in ['universal-constructor-panel-20261123','universal-constructor-launch-20261123-1399519',
                 'interface-discovery-workspace-20261118-1399519']:
        paths += [p for p in (b/'runs'/name).rglob('*') if p.is_file()]
    paths.append(b/'repository/scripts/project/archive_universal_constructor.py')
    a.output.mkdir(parents=True,exist_ok=False)
    wrapper=a.output/'frozen-workspace.sh'
    wrapper.write_bytes(subprocess.check_output(['git','-C',str(b/'repository'),'show',
        (run/'commit').read_text().strip()+':cluster/workspaces/universal_constructor_20261123.sh']))
    paths=sorted(set(paths+[wrapper]));assert all(not p.is_symlink() for p in paths)
    secret=re.compile(rb'-----BEGIN (?:RSA |OPENSSH |EC )?PRIVATE KEY-----|gh[pousr]_[A-Za-z0-9]{30,}|sk-[A-Za-z0-9]{32,}')
    assert all(not secret.search(p.read_bytes()) for p in paths)
    members={str(p.relative_to(b)):dict(bytes=p.stat().st_size,sha256=sha(p)) for p in paths}
    arc=a.output/'universal-constructor-1399519.tar.gz'
    with tarfile.open(arc,'w:gz',compresslevel=6) as t:
        for p in paths:t.add(p,arcname=str(p.relative_to(b)),recursive=False)
    assert all(sha(p)==members[str(p.relative_to(b))]['sha256'] for p in paths)
    inventory=dict(archive=arc.name,sha256=sha(arc),bytes=arc.stat().st_size,member_count=len(members),
        logical_bytes=sum(v['bytes'] for v in members.values()),members=members,
        execution_commit=(run/'commit').read_text().strip(),model_weights_included=False)
    (a.output/'inventory.json').write_text(json.dumps(inventory,indent=2)+'\n')
    print(json.dumps({k:v for k,v in inventory.items() if k!='members'}))


if __name__=='__main__':main()
