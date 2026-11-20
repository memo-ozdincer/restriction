#!/usr/bin/env python3
"""Prepare and measure exact-program credit across training-only contexts."""
import argparse
from collections import defaultdict
import hashlib
import json
from pathlib import Path
import sys

try:
    from . import interface_discovery_pilot as instrument
except ImportError:
    import interface_discovery_pilot as instrument

SEED = 20261119
SAMPLES = 16


def bank():
    result = []

    def add(family, statement, witness):
        index = sum(r['family'] == family for r in result)
        result.append({'id': f'{family}_{index}', 'family': family,
            'statement': 'theorem target ' + statement + ' := by\n',
            'witness': witness, 'scope': 'training_only'})

    for d in (2, 3, 5, 7):
        add('nonzero', f'(x y : Int) (h : x^2 - {d}*y^2 = 1) : x ≠ 0',
            '  intro heq\n  rw [heq] at h\n  nlinarith [sq_nonneg y]\n')
    for expression, u, v in [('x*z+y*w', 'z', 'w'), ('x*z-y*w', 'z', '-w'),
                              ('x*w-y*z', 'w', '-z'), ('x*w+y*z', 'w', 'z')]:
        add('witness', f'(x y z w : Int) (h : {expression} = 1) : '
            '∃ u v : Int, u*x+v*y = 1', f'  refine ⟨{u}, {v}, ?_⟩\n  nlinarith [h]\n')
    for expression in ['(x+k*z)*w-(y+k*w)*z', 'x*(w+k*y)-y*(z+k*x)',
                       '(x-k*z)*w-(y-k*w)*z', 'x*(w-k*y)-y*(z-k*x)']:
        add('shear', f'(x y z w k : Int) : {expression} = x*w-y*z', '  ring\n')
    for identity in ['x/(x*y) = 1/y', '(x*y)/x = y', '(x/y)*y = x', '(1/x)/(1/y) = y/x']:
        add('rational', f'(x y : Real) (hx : x ≠ 0) (hy : y ≠ 0) : {identity}',
            '  field_simp [hx, hy] <;> ring\n')
    add('induction', '(P : Nat → Prop) (h0 : P 0) (hs : ∀ n, P n → P (n+1)) : ∀ n, P n',
        '  intro n\n  induction n <;> aesop\n')
    add('induction', '(P : List Int → Prop) (h0 : P []) '
        '(hs : ∀ a xs, P xs → P (a :: xs)) : ∀ xs, P xs',
        '  intro xs\n  induction xs <;> aesop\n')
    add('induction', '(P : Option Int → Prop) (h0 : P none) '
        '(hs : ∀ a, P (some a)) : ∀ x, P x',
        '  intro x\n  cases x <;> aesop\n')
    add('induction', '(P : Nat → Prop) (n : Nat) (h0 : P 0) '
        '(hs : ∀ k, P k → P (k+1)) : P n',
        '  induction n <;> aesop\n')
    return result


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def prepare(args):
    args.output.mkdir(parents=True, exist_ok=False)
    records = bank()
    tasks = [{k: v for k, v in row.items() if k != 'witness'} for row in records]
    instrument.write(args.output / 'tasks.json', tasks)
    instrument.write(args.output / 'witnesses.json', records)
    instrument.write(args.output / 'manifest.json', {'scope': 'training_only',
        'task_count': len(tasks), 'families': 5, 'samples_per_task': SAMPLES,
        'generated_proposal_cap': len(tasks) * SAMPLES,
        'logical_candidate_context_checks_cap': len(tasks) * SAMPLES * 4,
        'source_sha256': sha(Path(__file__)),
        'instrument_sha256': sha(Path(instrument.__file__)),
        'seed': SEED, 'max_generated_tokens': 256, 'verifier_timeout_seconds': 60,
        'files': {p.name: sha(p) for p in sorted(args.output.iterdir())},
        'old_transfer_panel_read': False, 'model_inference_performed': False,
        'teacher_witnesses_visible_to_model': False})


def authenticate(panel):
    manifest = json.loads((panel / 'manifest.json').read_text())
    if manifest['source_sha256'] != sha(Path(__file__)):
        raise RuntimeError('Prepared source changed')
    if manifest['instrument_sha256'] != sha(Path(instrument.__file__)):
        raise RuntimeError('Prepared verifier/generation instrument changed')
    for name, expected in manifest['files'].items():
        if sha(panel / name) != expected:
            raise RuntimeError('Panel file changed: ' + name)
    return json.loads((panel / 'tasks.json').read_text())


def job(args, identity, code):
    return {'id': identity, 'code': code,
        'verifier': str(args.bundle / 'verifier/DeepSeek-Prover-V1.5'),
        'lake': str(args.bundle / 'lean/elan/bin/lake')}


def validate(args):
    authenticate(args.panel)
    records = json.loads((args.panel / 'witnesses.json').read_text())
    checks = []
    for row in records:
        for mode, suffix in [('witness', row['witness']), ('empty', '')]:
            checks.append(job(args, row['id'] + '/' + mode, instrument.HEADER +
                row['statement'] + suffix + '\n#print axioms target\n'))
    checks += [job(args, 'negative/sorry', instrument.HEADER +
        'theorem target : False := by sorry\n#print axioms target\n'),
        job(args, 'negative/axiom', instrument.HEADER +
        'axiom bad : False\ntheorem target : False := bad\n#print axioms target\n')]
    results = instrument.verify_jobs(checks, args.output, workers=8)
    passed = all(r['accepted'] == r['id'].endswith('/witness') and
                 not r.get('system_errors') for r in results)
    instrument.write(args.output.with_suffix('.summary.json'),
                     {'passed': passed, 'physical_lean_calls': len(checks)})
    if not passed:
        raise SystemExit('Bank validation failed; no generation authorized')


def requests(tasks):
    return [{'id': row['id'], 'world': row['family'], 'target': row['id'],
        'kind': 'consumer', 'condition': 'contract', 'samples': SAMPLES,
        'max_tokens': 256, 'prompt': instrument.PREFIX + instrument.HEADER + row['statement']}
        for row in tasks]


def generate(args):
    tasks = authenticate(args.panel)
    valid = json.loads(args.validation.with_suffix('.summary.json').read_text())
    if valid != {'passed': True, 'physical_lean_calls': 42}:
        raise RuntimeError('Need complete successful bank validation')
    checks = instrument.rows(args.validation)
    expected = {r['id'] + '/' + mode for r in tasks for mode in ('witness', 'empty')}
    expected |= {'negative/sorry', 'negative/axiom'}
    if len(checks) != 42 or {r['id'] for r in checks} != expected or any(
            r['accepted'] != r['id'].endswith('/witness') or r.get('system_errors') for r in checks):
        raise RuntimeError('Validation records do not support success summary')
    instrument.SEED = SEED
    instrument.generation_requests = lambda _: requests(tasks)
    args.phase = 'cross_context'
    args.model = args.bundle / 'models/base'
    args.tokenizer = args.model
    args.model_label = 'base'
    instrument.generate(args)


def rewards(local, peers):
    """A malformed/incorrect source never receives positive cross-context credit."""
    if len(peers) != 3 or any(type(v) is not bool for v in [local, *peers]):
        raise ValueError('Need one local and three resolved boolean kernel verdicts')
    return float(local), float(local) * sum(peers) / 3


def score(args):
    tasks = authenticate(args.panel)
    by_id = {r['id']: r for r in tasks}
    raw = instrument.rows(args.input)
    expected = {f"base/{row['id']}/{i}" for row in tasks for i in range(SAMPLES)}
    if len(raw) != len(expected) or {r['id'] for r in raw} != expected:
        raise RuntimeError('Incomplete/duplicate model proposals')
    # Deduplicate only byte-identical complete Lean sources, never tactic signatures.
    unique, edges = {}, []
    for row in raw:
        source = by_id[row['target']]
        request = next(r for r in requests(tasks) if r['id'] == source['id'])
        if any(row[k] != v for k, v in request.items() if k != 'id'):
            raise RuntimeError('Generated row differs from frozen request')
        body, error = instrument.completion_code(row['text'])
        for target in tasks:
            if target['family'] != source['family']:
                continue
            code = instrument.HEADER + target['statement'] + (body or '') + '\n#print axioms target\n'
            digest = instrument.sha(code) if not error else None
            if digest:
                unique.setdefault(digest, job(args, digest, code))
            edges.append({'proposal_id': row['id'], 'source': source['id'], 'target': target['id'],
                          'family': source['family'], 'code_sha256': digest, 'parse_error': error})
    args.output.mkdir(exist_ok=False)
    instrument.write(args.output / 'provenance.json', {
        'input_sha256': sha(args.input), 'panel_manifest_sha256': sha(args.panel / 'manifest.json'),
        'source_sha256': sha(Path(__file__)), 'instrument_sha256': sha(Path(instrument.__file__)),
        'candidate_transformations': 'Strip the closing Markdown fence only; preserve all proof-body bytes.',
        'cache_key': 'SHA-256 of the complete exact Lean source', 'training_updates': 0})
    instrument.write(args.output / 'edges.json', edges)
    instrument.write(args.output / 'unique-sources.json', list(unique.values()))
    instrument.verify_jobs(list(unique.values()), args.output / 'verdicts.jsonl', workers=8)
    summarize(args.output)


def summarize(output):
    edges = json.loads((output / 'edges.json').read_text())
    verdicts = {r['id']: r for r in instrument.rows(output / 'verdicts.jsonl')}
    grouped = defaultdict(list)
    for edge in edges:
        verdict = verdicts.get(edge['code_sha256']) if not edge['parse_error'] else None
        resolved = bool(edge['parse_error']) or (verdict is not None and not verdict.get('system_errors'))
        grouped[edge['proposal_id']].append({**edge, 'resolved': resolved,
            'accepted': bool(verdict and verdict['accepted']),
            'system_error': verdict.get('system_errors') if verdict else None})
    rows = []
    for proposal, checks in grouped.items():
        local = next(r for r in checks if r['source'] == r['target'])
        peers = [r for r in checks if r['source'] != r['target']]
        eligible = all(r['resolved'] for r in checks)
        credit = rewards(local['accepted'], [r['accepted'] for r in peers]) if eligible else (None, None)
        rows.append({'id': proposal, 'source': local['source'], 'family': local['family'],
                     'local_accepted': local['accepted'], 'peers_accepted': sum(r['accepted'] for r in peers),
                     'reward_eligible': eligible, 'local_reward': credit[0], 'cross_reward': credit[1]})
    separating = []
    for source in sorted({r['source'] for r in rows}):
        correct = [r for r in rows if r['source'] == source and r['reward_eligible'] and r['local_accepted']]
        if any(r['peers_accepted'] >= 2 for r in correct) and any(r['peers_accepted'] <= 1 for r in correct):
            separating.append(source)
    families = sorted({r['family'] for r in rows if r['source'] in separating})
    instrument.write(output / 'analysis.json', {'proposals': rows, 'separating_sources': separating,
        'separating_families': families, 'signal_gate_passed': len(families) >= 2,
        'logical_checks': len(edges), 'physical_lean_calls': len(verdicts),
        'unique_system_errors': sum(bool(r.get('system_errors')) for r in verdicts.values()),
        'generated_proposals': len(rows), 'parameter_updates': 0,
        'claim_boundary': 'Training-only reward-signal screen, not learned transfer or a training result.'})


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('mode', choices=['prepare', 'validate', 'generate', 'score', 'summarize'])
    for name in ('panel', 'output', 'input', 'validation', 'bundle'):
        p.add_argument('--' + name, type=Path)
    a = p.parse_args()
    if a.mode == 'summarize': summarize(a.output)
    else: globals()[a.mode](a)


if __name__ == '__main__':
    main()
