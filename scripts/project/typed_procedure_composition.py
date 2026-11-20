#!/usr/bin/env python3
"""Fixed bounded type-directed composition of two saved model procedures."""
import argparse
import json
from pathlib import Path
import sys
import time
import interface_discovery_pilot as lean
from archive_policy_update_training import sha


def prepare(a):
    b = a.bundle
    panel = b / 'runs/repaired-library-panel-20261119-final'
    assert sha(panel / 'manifest.json') == 'a2130075a8b0dd7bf6728fa0be9865722755c5504f1a79e4ac2d83aa5a4f4cf6'
    manifest = json.loads((panel / 'manifest.json').read_text())
    assert sha(panel / 'records.json') == manifest['records_sha256']
    previous = b / 'runs/interface-discovery-workspace-20261118-1373310/policy-improvement'
    trace = next(x for x in lean.rows(previous / 'traces.jsonl') if x['id'] == 'base/witness_2/15')
    body, error = lean.completion_code(trace['text']); assert error is None
    assert body.strip() == 'exact ⟨w, -z, by linarith⟩'
    statement = trace['prompt'].split('theorem target', 1)[1]
    constructor = 'theorem witness_constructor' + statement + body + '\n'
    records = {x['id']: x for x in json.loads((panel / 'records.json').read_text())}
    rows = []
    for i in range(8, 12):
        target = f'pt_{i:02d}'; r = records[target + '/linked']
        for condition in ['both', 'constructor_only', 'invariant_only', 'irrelevant', 'explicit']:
            with_constructor = condition != 'invariant_only'
            with_invariant = condition != 'constructor_only'
            inv = records[target + '/irrelevant']['library'] if condition == 'irrelevant' else r['library']
            library = (inv if with_invariant else '') + (constructor if with_constructor else '')
            names = (['witness_constructor'] if with_constructor else []) + ['Eq.trans'] + (['linked_contract'] if with_invariant else []) + ['h']
            proof = '  solve_by_elim (maxDepth := 4) only [' + ', '.join(names) + ']\n'
            if condition == 'explicit':
                proof = '  exact witness_constructor _ _ _ _ (Eq.trans (linked_contract n a b c d) h)\n'
            code = lean.HEADER + r['definition'] + library + r['target_theorem'] + proof + '\n#print axioms ' + target + '\n'
            rows.append(dict(id=target + '/' + condition, target=target, condition=condition,
                expected_accept=condition in ['both', 'explicit'], code=code, code_sha256=lean.sha(code),
                producer_id=r['producer_id'], constructor_id=trace['id']))
    for name, code, expected in [
        ('constructor', lean.HEADER + constructor + '\n#print axioms witness_constructor\n', True),
        ('invalid', lean.HEADER + 'theorem target : False := by sorry\n#print axioms target\n', False),
    ]:
        rows.append(dict(id='control/' + name, condition=name, expected_accept=expected, code=code, code_sha256=lean.sha(code)))
    a.output.mkdir(parents=True, exist_ok=False)
    lean.write(a.output / 'sources.json', rows)
    lean.write(a.output / 'constructor-origin.json', trace)
    inputs = [panel / 'manifest.json', panel / 'records.json', previous / 'traces.jsonl']
    lean.write(a.output / 'manifest.json', dict(checks=22, source_sha256=sha(Path(__file__)),
        sources_sha256=sha(a.output / 'sources.json'), constructor_origin_sha256=sha(a.output / 'constructor-origin.json'),
        input_sha256={str(p.relative_to(b)): sha(p) for p in inputs}, max_depth=4,
        parameter_updates=0, new_model_proposals=0, scope='Inspected-root compiler composition; no learning claim'))


def execute(a):
    m = json.loads((a.output / 'manifest.json').read_text())
    assert sha(Path(__file__)) == m['source_sha256']
    assert sha(a.output / 'sources.json') == m['sources_sha256']
    assert sha(a.output / 'constructor-origin.json') == m['constructor_origin_sha256']
    for name, digest in m['input_sha256'].items(): assert sha(a.bundle / name) == digest
    rows = json.loads((a.output / 'sources.json').read_text()); assert len(rows) == 22
    sys.path.insert(0, str(a.bundle / 'verifier/DeepSeek-Prover-V1.5'))
    from prover.lean.verifier import verify_lean4_file
    warm = verify_lean4_file('import Mathlib\nimport Aesop\ntheorem warmup : True := by trivial\n',
        lake_path=str(a.bundle / 'lean/elan/bin/lake'), lean_workspace=str(a.bundle / 'verifier/DeepSeek-Prover-V1.5/mathlib4'), timeout=300)
    lean.write(a.output / 'warmup.json', warm)
    assert warm.get('complete')
    start = time.time()
    jobs = [dict(id=r['id'], code=r['code'], verifier=str(a.bundle / 'verifier/DeepSeek-Prover-V1.5'),
                 lake=str(a.bundle / 'lean/elan/bin/lake')) for r in rows]
    checked = {v['id']: v for v in lean.verify_jobs(jobs, a.output / 'verdicts.jsonl', workers=8)}
    results = [dict(id=r['id'], condition=r['condition'], expected_accept=r['expected_accept'],
                    accepted=checked[r['id']]['accepted'], unresolved=bool(checked[r['id']].get('system_errors')),
                    code_sha256=r['code_sha256']) for r in rows]
    outcome = all(r['accepted'] == r['expected_accept'] and not r['unresolved'] for r in results)
    lean.write(a.output / 'analysis.json', dict(rows=results, registered_outcome=outcome,
        checks=len(results), seconds=time.time()-start, new_model_proposals=0, parameter_updates=0))
    print(json.dumps(dict(registered_outcome=outcome, checks=len(results))))


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('mode', choices=['prepare', 'execute'])
    for n in ['bundle', 'output']: p.add_argument('--' + n, type=Path, required=True)
    a = p.parse_args(); globals()[a.mode](a)
