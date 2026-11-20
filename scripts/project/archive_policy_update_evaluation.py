#!/usr/bin/env python3
"""Package terminal evaluation and audit evidence, without duplicating adapters."""
import argparse
import json
from pathlib import Path
import subprocess
import tarfile
from archive_policy_update_training import sha


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--bundle',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();b=a.bundle
    r=b/'runs/interface-discovery-workspace-20261118-1373310/policy-improvement'
    assert json.loads((r/'status.json').read_text())['state']=='complete'
    assert json.loads((r/'independent-audit.json').read_text())['passed']
    (r/'scheduler-accounting.txt').write_text(subprocess.check_output(['sacct','-j','1373078,1373310',
        '--format=JobID,Account,State,Elapsed,ExitCode','-P'],text=True))
    paths=list((r/'evaluation').rglob('*'))+list((r/'judgments').rglob('*'))
    paths+=[r/name for name in ['status.json','independent-audit.json','training-reward-contrast.json','scheduler-accounting.txt','verify.log']]
    paths+=list(r.glob('evaluate-*.log'))
    paths+=[b/'runs/policy-update-launch-20261119-1373310/driver.log',
            b/'repository/scripts/project/audit_policy_improvement.py',Path(__file__).resolve()]
    paths=sorted(set(p for p in paths if p.is_file()))
    assert all(not p.is_symlink() for p in paths)
    a.output.mkdir(exist_ok=False,parents=True)
    inventory={str(p.relative_to(b)):dict(bytes=p.stat().st_size,sha256=sha(p)) for p in paths}
    archive=a.output/'policy-update-evaluation-20261119.tar.gz'
    with tarfile.open(archive,'w:gz',compresslevel=6) as t:
        for p in paths:t.add(p,arcname=str(p.relative_to(b)),recursive=False)
    for p in paths:assert sha(p)==inventory[str(p.relative_to(b))]['sha256']
    record=dict(files=inventory,file_count=len(inventory),logical_bytes=sum(v['bytes'] for v in inventory.values()),
        archive=archive.name,archive_bytes=archive.stat().st_size,archive_sha256=sha(archive),
        companion_training_archive_sha256='10aa1cd65623c6296741e9415467570b59ee0e43a1432f184dfd7cae1a13c356')
    (a.output/'evaluation-inventory.json').write_text(json.dumps(record,indent=2)+'\n')
    print(json.dumps({k:v for k,v in record.items() if k!='files'}))


if __name__=='__main__':main()
