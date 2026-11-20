#!/usr/bin/env python3
"""Independently reconstruct exact typed-composition sources and outcomes."""
import argparse
import hashlib
import json
from pathlib import Path


def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def digest(s): return hashlib.sha256(s.encode()).hexdigest()
def rows(p): return [json.loads(x) for x in p.read_text().splitlines() if x.strip()]


def main():
    p = argparse.ArgumentParser(description=__doc__)
    for n in ['bundle', 'run', 'output']: p.add_argument('--' + n, type=Path, required=True)
    a = p.parse_args(); b = a.bundle; r = a.run
    import interface_discovery_pilot as lean
    m = json.loads((r / 'manifest.json').read_text())
    assert sha(r / 'sources.json') == m['sources_sha256']
    assert sha(r / 'constructor-origin.json') == m['constructor_origin_sha256']
    for n, h in m['input_sha256'].items(): assert sha(b / n) == h
    original = b / 'runs/interface-discovery-workspace-20261118-1373310/policy-improvement'
    trace = json.loads((r / 'constructor-origin.json').read_text())
    assert trace == next(x for x in rows(original / 'traces.jsonl') if x['id'] == 'base/witness_2/15')
    edge = next(x for x in json.loads((original / 'matrix/edges.json').read_text())
                if x['proposal_id'] == trace['id'] and x['target'] == 'witness_2')
    oldcheck = next(x for x in rows(original / 'matrix/verdicts.jsonl') if x['id'] == edge['code_sha256'])
    assert oldcheck['accepted'] and oldcheck['lean_complete'] and not oldcheck.get('system_errors')
    body, error = lean.completion_code(trace['text']); assert error is None
    local = trace['prompt'].removeprefix(lean.PREFIX) + body + '\n#print axioms target\n'
    assert digest(local) == edge['code_sha256']
    constructor = ('theorem target' + trace['prompt'].split('theorem target', 1)[1]).replace(
        'theorem target', 'theorem witness_constructor', 1) + body + '\n'
    panel = {x['id']: x for x in json.loads((b / 'runs/repaired-library-panel-20261119-final/records.json').read_text())}
    sources = json.loads((r / 'sources.json').read_text())
    expected_ids = {f'pt_{i:02d}/{c}' for i in range(8, 12) for c in ['both', 'constructor_only', 'invariant_only', 'irrelevant', 'explicit']} | {'control/constructor', 'control/invalid'}
    assert len(sources) == 22 and {x['id'] for x in sources} == expected_ids
    for x in sources:
        assert digest(x['code']) == x['code_sha256']
        if x['id'].startswith('control/'):
            expected = lean.HEADER + (constructor + '\n#print axioms witness_constructor\n' if x['condition'] == 'constructor' else 'theorem target : False := by sorry\n#print axioms target\n')
        else:
            target, condition = x['id'].split('/'); rec = panel[target + '/linked']
            assert x['producer_id'] == rec['producer_id'] and x['constructor_id'] == trace['id']
            inv = panel[target + '/irrelevant']['library'] if condition == 'irrelevant' else rec['library']
            prefix = lean.HEADER + rec['definition']
            if condition != 'constructor_only': prefix += inv
            if condition != 'invariant_only': prefix += constructor
            names = []
            if condition != 'invariant_only': names.append('witness_constructor')
            names.append('Eq.trans')
            if condition != 'constructor_only': names.append('linked_contract')
            names.append('h')
            proof = '  solve_by_elim (config := {maxDepth := 4}) only [' + ', '.join(names) + ']\n'
            if condition == 'explicit': proof = '  exact witness_constructor _ _ _ _ (Eq.trans (linked_contract n a b c d) h)\n'
            expected = prefix + rec['target_theorem'] + proof + '\n#print axioms ' + target + '\n'
            assert 'hbridge' not in expected
        assert x['code'] == expected
        assert x['expected_accept'] == (x['condition'] in ['both', 'explicit', 'constructor'])
    verdicts = rows(r / 'verdicts.jsonl'); checked = {x['id']: x for x in verdicts}
    assert len(verdicts) == len(checked) == 22 and set(checked) == expected_ids
    for x in sources:
        v = checked[x['id']]; assert v['code_sha256'] == x['code_sha256']
        if v['accepted']: assert v['lean_complete'] and v['axiom_audit_found'] and set(v['axioms']) <= {'propext', 'Classical.choice', 'Quot.sound'}
    unresolved = sum(bool(v.get('system_errors')) for v in verdicts)
    outcome = not unresolved and all(checked[x['id']]['accepted'] == x['expected_accept'] for x in sources)
    analysis = json.loads((r / 'analysis.json').read_text())
    assert len(analysis['rows']) == 22 and {x['id'] for x in analysis['rows']} == expected_ids
    for x in analysis['rows']:
        v = checked[x['id']]
        assert x['accepted'] == v['accepted'] and x['unresolved'] == bool(v.get('system_errors')) and x['code_sha256'] == v['code_sha256']
    assert analysis['registered_outcome'] == outcome
    result = dict(passed=True, checks=22, unresolved=unresolved, registered_outcome=outcome,
        search_successes=sum(v['accepted'] for k,v in checked.items() if k.endswith('/both')),
        explicit_successes=sum(v['accepted'] for k,v in checked.items() if k.endswith('/explicit')),
        control_successes=sum(v['accepted'] for k,v in checked.items() if k.split('/')[-1] in ['constructor_only', 'invariant_only', 'irrelevant']),
        analysis_sha256=sha(r / 'analysis.json'), constructor_original_verified=True)
    with a.output.open('x') as f: json.dump(result, f, indent=2); f.write('\n')
    print(json.dumps(result))


if __name__ == '__main__': main()
