"""Archive both generator adapters, all outcomes, and rejected authoring attempts."""
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
    a=p.parse_args();b=a.bundle;r=b/'runs/pell-generator-20261123-1399388'
    audit=json.loads((r/'independent-audit.json').read_text());assert audit['passed'] and audit['proposals']==384
    paths=[p for p in r.rglob('*') if p.is_file() and p.relative_to(r).parts[0]!='source']
    for name in ['pell-generator-panel-20261123','pell-generator-panel-20261123-v2','pell-generator-panel-20261123-v3',
                 'pell-generator-launch-20261123-1399388','interface-discovery-workspace-20261118-1399388']:
        paths += [p for p in (b/'runs'/name).rglob('*') if p.is_file()]
    paths += [b/'repository/scripts/project/archive_pell_generator.py']
    for arm in ['literal','expression']:
        assert sha(r/arm/'adapter/adapter_model.safetensors')==audit['training'][arm]['adapter_sha256']
    a.output.mkdir(parents=True,exist_ok=False)
    wrapper=a.output/'frozen-workspace.sh'
    wrapper.write_bytes(subprocess.check_output(['git','-C',str(b/'repository'),'show',
        (r/'commit').read_text().strip()+':cluster/workspaces/pell_generator_20261123.sh']))
    paths.append(wrapper);paths=sorted(set(paths));assert all(not p.is_symlink() for p in paths)
    members={str(p.relative_to(b)):dict(bytes=p.stat().st_size,sha256=sha(p)) for p in paths}
    archive=a.output/'pell-generator-1399388.tar.gz'
    with tarfile.open(archive,'w:gz',compresslevel=6) as t:
        for p in paths:t.add(p,arcname=str(p.relative_to(b)),recursive=False)
    for p in paths:assert sha(p)==members[str(p.relative_to(b))]['sha256']
    record=dict(archive=archive.name,sha256=sha(archive),bytes=archive.stat().st_size,members=members,
        logical_bytes=sum(x['bytes'] for x in members.values()),member_count=len(members),
        execution_commit=(r/'commit').read_text().strip(),base_weights_included=False,optimizer_state_included=False)
    (a.output/'inventory.json').write_text(json.dumps(record,indent=2)+'\n')
    print(json.dumps({k:v for k,v in record.items() if k!='members'}))


if __name__=='__main__':main()
