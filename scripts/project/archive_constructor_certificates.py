"""Archive the fixed-certificate replay and both authenticated input banks."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import tarfile


def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('bundle',type=Path);p.add_argument('output',type=Path)
    a=p.parse_args();b=a.bundle;r=b/'runs/constructor-certificates-20261124'
    audit=json.loads((r/'independent-audit.json').read_text());assert audit['passed'] and audit['proposals']==224
    paths=[p for p in r.rglob('*') if p.is_file()]
    launch=b/'runs/constructor-certificate-launch-20261124'
    paths += [p for p in launch.rglob('*') if p.is_file() and p.relative_to(launch).parts[0]!='source']
    for name in ['universal-constructor-20261123-1399519','constructor-feedback-20261124-1399674']:
        paths.append(b/'runs'/name/'experiment/samples.jsonl')
    paths += [b/'repository/scripts/project'/name for name in
        ['archive_constructor_certificates.py','audit_constructor_certificates.py']]
    paths=sorted(set(paths));assert all(not p.is_symlink() for p in paths)
    secret=re.compile(rb'-----BEGIN (?:RSA |OPENSSH |EC )?PRIVATE KEY-----|gh[pousr]_[A-Za-z0-9]{30,}|sk-[A-Za-z0-9]{32,}')
    assert all(not secret.search(p.read_bytes()) for p in paths)
    members={str(p.relative_to(b)):dict(bytes=p.stat().st_size,sha256=sha(p)) for p in paths}
    a.output.mkdir(parents=True,exist_ok=False);arc=a.output/'certificate-audit-20261124.tar.gz'
    with tarfile.open(arc,'w:gz',compresslevel=6) as t:
        for p in paths:t.add(p,arcname=str(p.relative_to(b)),recursive=False)
    assert all(sha(p)==members[str(p.relative_to(b))]['sha256'] for p in paths)
    record=dict(archive=arc.name,sha256=sha(arc),bytes=arc.stat().st_size,member_count=len(members),
        logical_bytes=sum(x['bytes'] for x in members.values()),members=members,
        execution_commit=(launch/'commit').read_text().strip(),model_weights_included=False)
    (a.output/'certificate-inventory.json').write_text(json.dumps(record,indent=2)+'\n')
    print(json.dumps({k:v for k,v in record.items() if k!='members'}))


if __name__=='__main__':main()
