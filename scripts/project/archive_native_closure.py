"""Archive native-learning adapters, crossover dependencies and full evidence."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import tarfile


def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('bundle',type=Path);p.add_argument('job');p.add_argument('output',type=Path);a=p.parse_args();b=a.bundle
    run=b/f'runs/native-closure-20261124-{a.job}';audit=json.loads((run/'experiment/independent-audit.json').read_text());assert audit['passed'] and audit['proposals']==960
    paths=[]
    for name in [f'native-closure-20261124-{a.job}',f'native-closure-launch-20261124-{a.job}',
                 'native-closure-token-preflight-20261124','contract-transport-20261124-v2','prompt-interface-audit-20261124']:
        root=b/'runs'/name;paths.extend(p for p in root.rglob('*') if p.is_file() and p.relative_to(root).parts[0]!='source')
    old=b/'runs/contract-closure-20261124-1400174/experiment'
    paths += [old/'train.json',old/'test.json',old/'hindsight/tokens.json',
              b/'runs/hindsight-contracts-mining-20261124/selected.json',
              b/'runs/universal-constructor-20261123-1399519/experiment/samples.jsonl',
              b/'runs/contract-closure-20261124-1400174/parent-model-identity.json',
              b/'repository/scripts/project/archive_native_closure.py',b/'repository/scripts/project/analyze_native_closure.py']
    for arm in ['executable','transport']:
        paths.extend(p for p in (old/arm).rglob('*') if p.is_file())
    paths.extend(p for p in (b/f'runs/interface-discovery-workspace-20261118-{a.job}').iterdir() if p.is_file())
    paths=sorted(set(paths));assert all(not p.is_symlink() for p in paths)
    pattern=re.compile(rb'-----BEGIN (?:RSA |OPENSSH |EC )?PRIVATE KEY-----|gh[pousr]_[A-Za-z0-9]{30,}|sk-[A-Za-z0-9]{32,}')
    assert all(not pattern.search(p.read_bytes()) for p in paths)
    members={str(p.relative_to(b)):dict(bytes=p.stat().st_size,sha256=sha(p)) for p in paths}
    for arm in ['hindsight','executable','transport']:
        adapter=run/'experiment'/arm/'adapter/adapter_model.safetensors';assert sha(adapter)==audit['training'][arm]['adapter_sha256'] and str(adapter.relative_to(b)) in members
    for arm in ['executable','transport']:assert sha(old/arm/'adapter/adapter_model.safetensors')==audit['reused_adapters']['legacy_'+arm]['adapter_sha256']
    a.output.mkdir(parents=True,exist_ok=False);arc=a.output/f'native-closure-{a.job}.tar.gz'
    with tarfile.open(arc,'w:gz',compresslevel=6) as t:
        for p in paths:t.add(p,arcname=str(p.relative_to(b)),recursive=False)
    assert all(sha(p)==members[str(p.relative_to(b))]['sha256'] for p in paths)
    result=dict(archive=arc.name,bytes=arc.stat().st_size,sha256=sha(arc),member_count=len(members),logical_bytes=sum(v['bytes'] for v in members.values()),members=members,
        execution_commit=(run/'commit').read_text().strip(),base_weights_included=False,optimizer_state_included=False,new_adapters=3,reused_adapters=2)
    (a.output/'inventory.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items() if k!='members'}))


if __name__=='__main__':main()
