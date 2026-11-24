"""Archive the marker-placement experiment and authoritative native-format evidence."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import tarfile


def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('bundle',type=Path);p.add_argument('job');p.add_argument('output',type=Path);a=p.parse_args();b=a.bundle
    run=b/f'runs/prompt-boundary-20261124-{a.job}';audit=json.loads((run/'experiment/independent-audit.json').read_text());assert audit['passed'] and audit['proposals']==256
    paths=[]
    for name in [f'prompt-boundary-20261124-{a.job}',f'prompt-boundary-launch-20261124-{a.job}','prompt-interface-audit-20261124']:
        root=b/'runs'/name;paths.extend(p for p in root.rglob('*') if p.is_file() and p.relative_to(root).parts[0]!='source')
    old=b/'runs/c1-grpo-default-full-20260814-seed42-5ced4c3'
    paths += [old/'artifacts/train_batch_buffer/global_step_604',old/'RUN_METADATA.md',old/'hydra/.hydra/config.yaml']
    recent=b/'runs/contract-closure-20261124-1400174/experiment'
    paths += [recent/'train.json',recent/'transport/tokens.json',recent/'transport/reload-probes.json',b/'repository/scripts/project/archive_prompt_boundary.py']
    analysis=json.loads((run/'experiment/boundary-token-analysis.json').read_text())
    for relative,expected in analysis['input_sha256'].items():
        path=b/relative;assert sha(path)==expected;paths.append(path)
    paths.append(b/'repository/scripts/project/analyze_boundary_tokens.py')
    paths.extend(p for p in (b/'models/c1-final').iterdir() if p.is_file() and p.suffix=='.json' and 'safetensors' not in p.name)
    paths.extend(p for p in (b/f'runs/interface-discovery-workspace-20261118-{a.job}').iterdir() if p.is_file())
    paths=sorted(set(paths));assert all(not p.is_symlink() for p in paths)
    pattern=re.compile(rb'-----BEGIN (?:RSA |OPENSSH |EC )?PRIVATE KEY-----|gh[pousr]_[A-Za-z0-9]{30,}|sk-[A-Za-z0-9]{32,}')
    assert all(not pattern.search(p.read_bytes()) for p in paths)
    members={str(p.relative_to(b)):dict(bytes=p.stat().st_size,sha256=sha(p)) for p in paths}
    a.output.mkdir(parents=True,exist_ok=False);arc=a.output/f'prompt-boundary-{a.job}.tar.gz'
    with tarfile.open(arc,'w:gz',compresslevel=6) as t:
        for p in paths:t.add(p,arcname=str(p.relative_to(b)),recursive=False)
    assert all(sha(p)==members[str(p.relative_to(b))]['sha256'] for p in paths)
    result=dict(archive=arc.name,bytes=arc.stat().st_size,sha256=sha(arc),member_count=len(members),logical_bytes=sum(v['bytes'] for v in members.values()),members=members,
        execution_commit=(run/'commit').read_text().strip(),base_weights_included=False,new_training=False,training_prompt_tensor_evidence_included=True)
    (a.output/'inventory.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items() if k!='members'}))


if __name__=='__main__':main()
