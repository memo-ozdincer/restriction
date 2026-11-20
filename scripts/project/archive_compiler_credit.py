#!/usr/bin/env python3
"""Back up completed compiler-credit phases; never snapshot live evaluation files."""
import argparse
import json
from pathlib import Path
import tarfile
from archive_policy_update_training import sha


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for n in ['bundle','workspace','launch','output']:p.add_argument('--'+n,type=Path,required=True)
    p.add_argument('--stage',choices=['training','evaluation'],required=True)
    a=p.parse_args();b=a.bundle;r=a.workspace/'compiler-credit';paths=[]
    if a.stage=='training':
        for arm in ['full','mapped','rotated']:
            cert=json.loads((r/arm/'complete.json').read_text())
            assert cert['optimizer_steps']==80 and cert['frozen_reference_bitwise_unchanged']
            assert sha(r/arm/'adapter/adapter_model.safetensors')==cert['adapter_sha256']
            paths += [p for p in (r/arm).rglob('*') if p.is_file()]+[r/('train-'+arm+'.log')]
        for name in ['compiler-credit-panel-20261119','compiler-credit-tokens-20261119','typed-composition-trace-20261119']:
            paths += [p for p in (b/'runs'/name).rglob('*') if p.is_file()]
        paths += [a.launch/n for n in ['source.tar','launch.json','ssh-command.json','ssh-result.json']]
        paths += [a.workspace/n for n in ['allocation.json','keeper.py']]
        paths += [r/n for n in ['model-identity.json','warmup.json','node-import-warmup.log']]
    else:
        assert json.loads((r/'status.json').read_text())['state']=='complete'
        assert json.loads((r/'independent-audit.json').read_text())['passed']
        for name in ['matrix','evaluation']:
            paths += [p for p in (r/name).rglob('*') if p.is_file()]
        paths += [r/n for n in ['status.json','independent-audit.json','verify.log','scheduler-accounting.txt']]
        paths += [r/('evaluate-'+arm+'.log') for arm in ['base','full','mapped','rotated']]
        paths += [a.launch/'driver.log', b/'repository/scripts/project/audit_compiler_credit.py']
    paths += [b/'repository/scripts/project/archive_compiler_credit.py',b/'repository/scripts/project/archive_policy_update_training.py']
    paths=sorted(set(paths));assert all(p.is_file() and not p.is_symlink() for p in paths)
    files={str(p.relative_to(b)):dict(bytes=p.stat().st_size,sha256=sha(p)) for p in paths}
    a.output.mkdir(parents=True,exist_ok=False);archive=a.output/('compiler-credit-'+a.stage+'-20261119.tar.gz')
    with tarfile.open(archive,'w:gz',compresslevel=6) as t:
        for p in paths:t.add(p,arcname=str(p.relative_to(b)),recursive=False)
    for p in paths:assert sha(p)==files[str(p.relative_to(b))]['sha256']
    record=dict(stage=a.stage,files=files,file_count=len(paths),logical_bytes=sum(v['bytes'] for v in files.values()),
        archive=archive.name,archive_bytes=archive.stat().st_size,archive_sha256=sha(archive))
    (a.output/(a.stage+'-inventory.json')).write_text(json.dumps(record,indent=2)+'\n')
    print(json.dumps({k:v for k,v in record.items() if k!='files'}))


if __name__=='__main__':main()
