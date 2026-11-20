#!/usr/bin/env python3
"""Read-only reconstruction of a completed candidate/context matrix."""
import argparse
from collections import Counter, defaultdict
import json
from pathlib import Path

import cross_context_credit as screen


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--workspace', type=Path, required=True)
    p.add_argument('--panel', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    a = p.parse_args()
    run = a.workspace / 'cross-context'
    status = json.loads((run / 'status.json').read_text())
    if status['state'] != 'complete':
        raise RuntimeError('Incomplete execution cannot receive a completed audit')
    if screen.sha(a.panel / 'manifest.json') != status['panel_sha256']:
        raise RuntimeError('Panel changed')
    tasks = screen.authenticate(a.panel)
    requests = {r['id']: r for r in screen.requests(tasks)}
    raw = screen.instrument.rows(run / 'candidates.jsonl')
    expected_ids = {f'base/{t["id"]}/{i}' for t in tasks for i in range(screen.SAMPLES)}
    if len(raw) != 320 or {r['id'] for r in raw} != expected_ids:
        raise RuntimeError('Candidate identity/count mismatch')
    matrix = run / 'matrix'
    provenance = json.loads((matrix / 'provenance.json').read_text())
    if provenance['input_sha256'] != screen.sha(run / 'candidates.jsonl'):
        raise RuntimeError('Raw candidates changed after checking')
    sources = json.loads((matrix / 'unique-sources.json').read_text())
    source_by_hash = {s['id']: s for s in sources}
    verdicts = screen.instrument.rows(matrix / 'verdicts.jsonl')
    checked = {v['id']: v for v in verdicts}
    if len(checked) != len(verdicts) or len(source_by_hash) != len(sources) or checked.keys() != source_by_hash.keys():
        raise RuntimeError('Duplicate/missing physical checks')
    for key, source in source_by_hash.items():
        verdict = checked[key]
        if screen.instrument.sha(source['code']) != key or verdict['code_sha256'] != key:
            raise RuntimeError('Checked source hash mismatch')
        if verdict['accepted'] and (not verdict['lean_complete'] or not verdict['axiom_audit_found'] or
                not set(verdict['axioms']) <= screen.instrument.ALLOWED_AXIOMS or verdict.get('system_errors')):
            raise RuntimeError('Acceptance audit failed')
    edges = []
    for row in raw:
        request = requests[row['target']]
        if any(row[k] != v for k, v in request.items() if k != 'id') or row['model'] != 'base':
            raise RuntimeError('Frozen request mismatch')
        if row['id'] != f"base/{row['target']}/{row['sample_index']}":
            raise RuntimeError('Sample ordinal mismatch')
        body, error = screen.instrument.completion_code(row['text'])
        for target in tasks:
            if target['family'] != row['world']:
                continue
            code = screen.instrument.HEADER + target['statement'] + (body or '') + '\n#print axioms target\n'
            key = screen.instrument.sha(code) if not error else None
            edges.append({'proposal_id': row['id'], 'source': row['target'], 'target': target['id'],
                'family': row['world'], 'code_sha256': key, 'parse_error': error})
            if key is not None and source_by_hash[key]['code'] != code:
                raise RuntimeError('Cross-context source differs from unchanged candidate')
    if edges != json.loads((matrix / 'edges.json').read_text()) or len(edges) != 1280:
        raise RuntimeError('Cross-execution matrix changed')
    saved = json.loads((matrix / 'analysis.json').read_text())
    by_proposal = defaultdict(list)
    for edge in edges:
        by_proposal[edge['proposal_id']].append(edge)
    groups = defaultdict(list)
    for row in saved['proposals']:
        related = by_proposal[row['id']]
        local = next(e for e in related if e['source'] == e['target'])
        good = lambda e: bool(e['code_sha256'] and checked[e['code_sha256']]['accepted'])
        peers = sum(good(e) for e in related if e != local)
        eligible = all(not e['code_sha256'] or not checked[e['code_sha256']].get('system_errors') for e in related)
        if (row['local_accepted'], row['peers_accepted'], row['reward_eligible']) != (good(local), peers, eligible):
            raise RuntimeError('Derived rewards differ from physical verdicts')
        expected = (float(good(local)), float(good(local))*peers/3) if eligible else (None, None)
        if (row['local_reward'], row['cross_reward']) != expected:
            raise RuntimeError('Incorrect reward')
        groups[row['source']].append(row)
    if len(saved['proposals']) != 320 or {r['id'] for r in saved['proposals']} != expected_ids:
        raise RuntimeError('Missing/duplicate analyzed candidates')
    new_signal = [k for k, rows in groups.items() if len({r['local_reward'] for r in rows}) == 1
                  and all(r['reward_eligible'] for r in rows) and len({r['cross_reward'] for r in rows}) > 1]
    separating = [k for k, rows in groups.items() if
        any(r['local_accepted'] and r['reward_eligible'] and r['peers_accepted'] >= 2 for r in rows) and
        any(r['local_accepted'] and r['reward_eligible'] and r['peers_accepted'] <= 1 for r in rows)]
    families = sorted({r['family'] for r in saved['proposals'] if r['source'] in separating})
    if sorted(separating) != saved['separating_sources'] or families != saved['separating_families'] or (
            len(families) >= 2) != saved['signal_gate_passed']:
        raise RuntimeError('Signal-gate reconstruction failed')
    result = {'complete_audit': True, 'job_id': status['job_id'], 'generated_proposals': len(raw),
        'logical_checks': len(edges), 'physical_checks': len(verdicts),
        'system_errors': sum(bool(v.get('system_errors')) for v in verdicts),
        'local_correct': sum(r['local_accepted'] for r in saved['proposals']),
        'new_reward_variance_sources': sorted(new_signal), 'separating_families': families,
        'signal_gate_passed': saved['signal_gate_passed'], 'parameter_updates': 0,
        'generated_tokens': sum(r['generated_tokens'] for r in raw),
        'supplied_tokens': sum(r['prompt_tokens'] for r in raw),
        'analysis_sha256': screen.sha(matrix / 'analysis.json')}
    with a.output.open('x') as f:
        json.dump(result, f, indent=2)
        f.write('\n')
    print(json.dumps(result))


if __name__ == '__main__':
    main()
