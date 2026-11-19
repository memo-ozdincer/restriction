#!/usr/bin/env python3
"""Post-hoc exact-byte transport of every successful local-context suffix."""
import argparse
import json
from pathlib import Path
import sys
from types import SimpleNamespace


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--workspace', type=Path, required=True)
    p.add_argument('--panel', type=Path, required=True)
    p.add_argument('--bundle', type=Path, required=True)
    a = p.parse_args()
    sys.path.insert(0, str(a.workspace))
    import pilot
    out = a.workspace / 'transport'
    out.mkdir(exist_ok=False)
    registration = (
        'Post-hoc hypothesis, recorded before transport verification: the exact '
        'two successful nonzero proof suffixes also solve the other recurrence '
        'when its invariant is instantiated as h. Transport every successful '
        'suffix, unchanged, to both original nonzero targets under both oracle '
        'and irrelevant helpers: eight Lean calls, no new model samples, no '
        'edits or search. The irrelevant control should fail. These targets '
        'have already been inspected; this is descriptive procedure reuse, '
        'not held-out transfer, a trained discovery, or a causal rate estimate.'
    )
    (out / 'registration.txt').write_text(registration + '\n')
    requests = pilot.generation_requests(SimpleNamespace(
        phase='consumer', panel=a.panel, artifacts=None))
    requests = [r for r in requests if r['target'].endswith('_nonzero')]
    jobs, provenance = [], []
    for model in ('base', 'grpo'):
        raw = pilot.rows(a.workspace / 'materialization' / (model + '-consumer.jsonl'))
        verdicts = {v['id']: v for v in pilot.rows(
            a.workspace / 'materialization' / (model + '-consumer-verified.jsonl'))}
        for row in raw:
            if not verdicts[row['id']]['accepted']:
                continue
            if not row['target'].endswith('_nonzero'):
                raise RuntimeError('Unexpected successful target outside registered transport scope')
            body, error = pilot.completion_code(row['text'])
            assert not error
            for request in requests:
                code = request['prompt'].removeprefix(pilot.PREFIX)
                code += '  have h := reusable_fact n\n' + body + '\n#print axioms target\n'
                identity = row['id'] + '/to/' + request['id']
                if request['id'] == row['target'] + '/' + row['condition']:
                    assert pilot.sha(code) == verdicts[row['id']]['code_sha256']
                jobs.append({'id': identity, 'code': code,
                    'verifier': str(a.bundle / 'verifier/DeepSeek-Prover-V1.5'),
                    'lake': str(a.bundle / 'lean/elan/bin/lake')})
                provenance.append({'id': identity, 'source_proposal': row['id'],
                    'source_target': row['target'], 'destination_target': request['target'],
                    'condition': request['condition'], 'suffix_sha256': pilot.sha(body),
                    'code_sha256': pilot.sha(code), 'model': model})
                (out / (identity.replace('/', '__') + '.lean')).write_text(code)
    if len(jobs) != 8:
        raise RuntimeError('Expected two successful suffixes and four destinations each')
    pilot.write(out / 'provenance.json', provenance)
    results = pilot.verify_jobs(jobs, out / 'verdicts.jsonl', workers=2)
    print(json.dumps({'checks': len(results), 'accepted': sum(r['accepted'] for r in results),
                      'system_errors': sum(bool(r.get('system_errors')) for r in results)}))


if __name__ == '__main__':
    main()
