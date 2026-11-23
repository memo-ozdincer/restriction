"""Check a nonempty witness construction and replay frozen on-policy outputs."""
import argparse
import json
from pathlib import Path

import interface_discovery_pilot as lean


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('bundle', type=Path)
    p.add_argument('experiment', type=Path)
    p.add_argument('output', type=Path)
    a = p.parse_args()
    target = 'lean_workbook_plus_11649'
    run = a.bundle/'runs/recursive-grpo-20261123-1398215'
    panel = json.loads((a.experiment.parent/'recursive_blocking_20261123/panel.json').read_text())
    original = next(r['statement'] for r in panel['panel'] if r['theorem']==target)
    strict = original.replace('(X ∩ Y', 'X.Nonempty ∧ Y.Nonempty ∧ (X ∩ Y')
    assert strict != original
    jobs = {}
    def add(statement, body):
        code = lean.HEADER + statement + body + '\n#print axioms ' + target
        key = lean.sha(code)
        jobs[key] = dict(id=key, code=code, verifier=str(a.bundle/'verifier/DeepSeek-Prover-V1.5'),
                         lake=str(a.bundle/'lean/elan/bin/lake'))
        return key
    fixture = add(strict, (a.experiment/'construction.txt').read_text())
    rows = []
    for arm in ['discovery','control','recursive']:
        for group in lean.rows(run/arm/'groups.jsonl'):
            if group['name'] != target:
                continue
            directory = run/arm/(group['phase']+'-'+target)
            samples = json.loads((directory/'samples.json').read_text())
            for s, mode in zip(samples, group['correct_modes'], strict=True):
                body,error = lean.completion_code(s['text'])
                key = None if error else add(strict, body)
                rows.append(dict(arm=arm,phase=group['phase'],index=s['sample_index'],
                                 original_accepted=mode is not None,strict_source=key))
    a.output.mkdir()
    lean.write(a.output/'sources.json', {k:v['code'] for k,v in jobs.items()})
    verdicts = lean.verify_jobs(list(jobs.values()), a.output/'verdicts.jsonl',workers=4)
    assert all(not v.get('system_errors') for v in verdicts)
    accepted = {v['id'] for v in verdicts if v['accepted']}
    for row in rows:
        row['strict_accepted'] = row['strict_source'] in accepted
    lean.write(a.output/'replay.json',rows)
    lean.write(a.output/'summary.json',dict(proposals=len(rows),original_accepted=sum(r['original_accepted'] for r in rows),
        strict_accepted=sum(r['strict_accepted'] for r in rows),fixture=fixture,fixture_accepted=fixture in accepted,
        physical_checks=len(jobs),parse_errors=sum(r['strict_source'] is None for r in rows)))


if __name__=='__main__':
    main()
