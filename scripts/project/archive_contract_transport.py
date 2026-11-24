"""Archive both transport attempts, immutable sources and original model provenance."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import tarfile


def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('bundle',type=Path);p.add_argument('output',type=Path)
    a=p.parse_args();b=a.bundle;first=b/'runs/contract-transport-20261124';second=b/'runs/contract-transport-20261124-v2'
    audit=json.loads((second/'independent-audit.json').read_text());assert audit['passed'] and audit['logical_checks']==34
    for name in ['inputs.json','plans.json','provenance.json']:assert (first/name).read_bytes()==(second/name).read_bytes()
    paths=[]
    for name in ['contract-transport-20261124','contract-transport-20261124-v2',
                 'contract-transport-launch-20261124','contract-transport-launch-20261124-v2']:
        root=b/'runs'/name
        paths += [p for p in root.rglob('*') if p.is_file() and p.relative_to(root).parts[0]!='source']
    paths += [b/'runs/hindsight-contracts-mining-20261124/selected.json',
              b/'runs/hindsight-training-20261124-1399987/experiment/test.json',
              b/'runs/universal-constructor-20261123-1399519/experiment/samples.jsonl',
              b/'runs/universal-constructor-20261123-1399519/parent-model-identity.json',
              b/'repository/scripts/project/archive_contract_transport.py']
    paths=sorted(set(paths));assert all(not p.is_symlink() for p in paths)
    secret=re.compile(rb'-----BEGIN (?:RSA |OPENSSH |EC )?PRIVATE KEY-----|gh[pousr]_[A-Za-z0-9]{30,}|sk-[A-Za-z0-9]{32,}')
    assert all(not secret.search(p.read_bytes()) for p in paths)
    members={str(p.relative_to(b)):dict(bytes=p.stat().st_size,sha256=sha(p)) for p in paths}
    a.output.mkdir(parents=True,exist_ok=False);arc=a.output/'contract-transport-20261124.tar.gz'
    with tarfile.open(arc,'w:gz',compresslevel=6) as t:
        for p in paths:t.add(p,arcname=str(p.relative_to(b)),recursive=False)
    assert all(sha(p)==members[str(p.relative_to(b))]['sha256'] for p in paths)
    record=dict(archive=arc.name,sha256=sha(arc),bytes=arc.stat().st_size,member_count=len(members),
        logical_bytes=sum(v['bytes'] for v in members.values()),members=members,
        execution_commits=[(b/'runs'/name/'commit').read_text().strip() for name in ['contract-transport-launch-20261124','contract-transport-launch-20261124-v2']],
        model_weights_included=False,gpu_allocations=0)
    (a.output/'transport-inventory.json').write_text(json.dumps(record,indent=2)+'\n')
    print(json.dumps({k:v for k,v in record.items() if k!='members'}))


if __name__=='__main__':main()
