"""Preserve closure-learning adapters, all raw evidence and source dependencies."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import tarfile


def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('bundle',type=Path);p.add_argument('job');p.add_argument('output',type=Path);a=p.parse_args();b=a.bundle
    run=b/f'runs/contract-closure-20261124-{a.job}';audit=json.loads((run/'experiment/independent-audit.json').read_text());assert audit['passed'] and audit['proposals']==640
    paths=[]
    for name in [f'contract-closure-20261124-{a.job}',f'contract-closure-launch-20261124-{a.job}',
                 'contract-closure-panel-20261124','contract-closure-panel-launch-20261124','contract-transport-20261124-v2']:
        root=b/'runs'/name;assert root.is_dir()
        paths.extend(p for p in root.rglob('*') if p.is_file() and p.relative_to(root).parts[0]!='source')
    paths += [b/'runs/hindsight-contracts-mining-20261124/selected.json',
              b/'runs/universal-constructor-20261123-1399519/experiment/samples.jsonl',
              b/'repository/scripts/project/archive_contract_closure.py']
    keeper=b/f'runs/interface-discovery-workspace-20261118-{a.job}'
    paths.extend(p for p in keeper.iterdir() if p.is_file())
    paths=sorted(set(paths));assert all(not p.is_symlink() for p in paths)
    pattern=re.compile(rb'-----BEGIN (?:RSA |OPENSSH |EC )?PRIVATE KEY-----|gh[pousr]_[A-Za-z0-9]{30,}|sk-[A-Za-z0-9]{32,}')
    assert all(not pattern.search(p.read_bytes()) for p in paths)
    members={str(p.relative_to(b)):dict(bytes=p.stat().st_size,sha256=sha(p)) for p in paths}
    for arm in ['hindsight','executable','transport']:
        adapter=run/'experiment'/arm/'adapter/adapter_model.safetensors'
        assert sha(adapter)==audit['training'][arm]['adapter_sha256'] and str(adapter.relative_to(b)) in members
    a.output.mkdir(parents=True,exist_ok=False);arc=a.output/f'contract-closure-{a.job}.tar.gz'
    with tarfile.open(arc,'w:gz',compresslevel=6) as t:
        for p in paths:t.add(p,arcname=str(p.relative_to(b)),recursive=False)
    assert all(sha(p)==members[str(p.relative_to(b))]['sha256'] for p in paths)
    result=dict(archive=arc.name,bytes=arc.stat().st_size,sha256=sha(arc),member_count=len(members),
        logical_bytes=sum(v['bytes'] for v in members.values()),members=members,execution_commit=(run/'commit').read_text().strip(),
        base_weights_included=False,optimizer_state_included=False,adapter_arms=['hindsight','executable','transport'])
    (a.output/'inventory.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items() if k!='members'}))


if __name__=='__main__':main()
