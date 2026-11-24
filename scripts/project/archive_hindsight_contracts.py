"""Preserve both hindsight adapters, original inputs, mining and full evaluation."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
import tarfile


def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('bundle',type=Path);p.add_argument('output',type=Path)
    a=p.parse_args();b=a.bundle;r=b/'runs/hindsight-training-20261124-1399987'
    audit=json.loads((r/'experiment/independent-audit.json').read_text());assert audit['passed'] and audit['proposals']==384
    paths=[p for p in r.rglob('*') if p.is_file() and p.relative_to(r).parts[0]!='source']
    for name in ['hindsight-contracts-mining-20261124','hindsight-mining-launch-20261124',
                 'hindsight-training-panel-20261124','hindsight-training-launch-20261124-1399987',
                 'interface-discovery-workspace-20261118-1399987']:
        root=b/'runs'/name
        paths += [p for p in root.rglob('*') if p.is_file() and p.relative_to(root).parts[0]!='source']
    paths.append(b/'runs/universal-constructor-20261123-1399519/experiment/samples.jsonl')
    paths.append(b/'repository/scripts/project/archive_hindsight_contracts.py')
    for arm in ['replay','contrast']:
        assert sha(r/'experiment'/arm/'adapter/adapter_model.safetensors')==audit['training'][arm]['adapter_sha256']
    a.output.mkdir(parents=True,exist_ok=False);wrapper=a.output/'frozen-workspace.sh'
    wrapper.write_bytes(subprocess.check_output(['git','-C',str(b/'repository'),'show',
        (r/'commit').read_text().strip()+':cluster/workspaces/hindsight_training_20261124.sh']))
    paths=sorted(set(paths+[wrapper]));assert all(not p.is_symlink() for p in paths)
    secret=re.compile(rb'-----BEGIN (?:RSA |OPENSSH |EC )?PRIVATE KEY-----|gh[pousr]_[A-Za-z0-9]{30,}|sk-[A-Za-z0-9]{32,}')
    assert all(not secret.search(p.read_bytes()) for p in paths)
    members={str(p.relative_to(b)):dict(bytes=p.stat().st_size,sha256=sha(p)) for p in paths}
    arc=a.output/'hindsight-contracts-1399987.tar.gz'
    with tarfile.open(arc,'w:gz',compresslevel=6) as t:
        for p in paths:t.add(p,arcname=str(p.relative_to(b)),recursive=False)
    assert all(sha(p)==members[str(p.relative_to(b))]['sha256'] for p in paths)
    report=dict(archive=arc.name,sha256=sha(arc),bytes=arc.stat().st_size,member_count=len(members),
        logical_bytes=sum(x['bytes'] for x in members.values()),members=members,
        execution_commit=(r/'commit').read_text().strip(),base_weights_included=False,optimizer_state_included=False)
    (a.output/'inventory.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({k:v for k,v in report.items() if k!='members'}))


if __name__=='__main__':main()
