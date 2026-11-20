#!/usr/bin/env python3
"""Archive only completed training phases while evaluation continues separately."""
import argparse
import hashlib
import json
from pathlib import Path
import tarfile


def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--bundle',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();b=a.bundle
    a.output.mkdir(exist_ok=False,parents=True)
    run=b/'runs/interface-discovery-workspace-20261118-1373310/policy-improvement'
    paths=[]
    for arm in ['local','cross','length','replay']:
        cert=json.loads((run/arm/'complete.json').read_text())
        assert cert['optimizer_steps']==40 and cert['frozen_reference_bitwise_unchanged']
        assert sha(run/arm/'adapter/adapter_model.safetensors')==cert['adapter_sha256']
        paths+=list((run/arm).rglob('*'))+[run/('train-'+arm+'.log')]
    paths+=list((run/'matrix').rglob('*'))
    paths+=[run/name for name in ['traces.jsonl','traces.complete.json','model-identity.json','warmup.json','warmup.log','collect.log','reward.log']]
    for job in ['1373078','1373310']:
        launch=b/('runs/policy-update-launch-20261119-'+job)
        paths+=[launch/name for name in ['source.tar','launch.json','ssh-command.json','ssh-result.json']]
        workspace=b/('runs/interface-discovery-workspace-20261118-'+job)
        paths+=[workspace/'allocation.json',workspace/'keeper.py']
    paths+=list((b/'runs/interface-discovery-workspace-20261118-1373078/policy-improvement').rglob('*'))
    paths+=[b/'runs/policy-update-launch-20261119-1373078/driver.log']
    for name in ['policy-improvement-panel-20261119','policy-improvement-panel-20261119-fp32','cross-context-panel-20261119']:
        paths+=list((b/'runs'/name).rglob('*'))
    paths += [b/'archives/training-runtime-20261119/peft-0.10.0-py3-none-any.whl']
    paths=sorted(set(p for p in paths if p.is_file()))
    assert all(not p.is_symlink() for p in paths)
    inventory={str(p.relative_to(b)):dict(bytes=p.stat().st_size,sha256=sha(p)) for p in paths}
    archive=a.output/'policy-update-training-20261119.tar.gz'
    with tarfile.open(archive,'w:gz',compresslevel=6) as t:
        for p in paths:t.add(p,arcname=str(p.relative_to(b)),recursive=False)
    for p in paths:assert sha(p)==inventory[str(p.relative_to(b))]['sha256'],'File changed during snapshot'
    record=dict(scope='Four completed adapters, exact traces, rewards, sources and failed attempt; evaluation still separate',
        files=inventory,file_count=len(inventory),logical_bytes=sum(r['bytes'] for r in inventory.values()),
        archive=archive.name,archive_bytes=archive.stat().st_size,archive_sha256=sha(archive))
    (a.output/'training-inventory.json').write_text(json.dumps(record,indent=2)+'\n')
    print(json.dumps({k:v for k,v in record.items() if k!='files'}))


if __name__=='__main__':main()
