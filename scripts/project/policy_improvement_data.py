#!/usr/bin/env python3
"""Frozen data/configuration for the matched single-cycle policy update."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil

try:
    from . import interface_discovery_pilot as lean
except ImportError:
    import interface_discovery_pilot as lean

CONFIG = dict(seed=20261120, evaluation_seed=20261121, samples_per_task=16,
    collection_max_tokens=256, evaluation_max_tokens=512, max_prompt_tokens=1536,
    temperature=1., top_p=1., top_k=0, epochs=2, learning_rate=1e-4,
    weight_decay=0., gradient_clip=1., ppo_clip=.2, kl_coefficient=.02,
    lora_rank=8, lora_alpha=16, lora_dropout=0., lora_modules=['q_proj', 'v_proj'],
    arms=['local', 'cross', 'length', 'replay'], optimizer_steps_per_arm=40,
    behavior_reference_mean_abs_tolerance=.05, behavior_reference_max_abs_tolerance=.5,
    adapter_reload_tolerance=1e-4, maximum_allocation_seconds=7200,
    claim_scope='One shared fresh rollout batch, two proximal-update epochs; not a converged online RL campaign.')


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def fresh_evaluation():
    rows = []
    for arity in (2, 3):
        args = ['a', 'b', 'c'][:arity]
        children = ' '.join(args)
        child_types = ' → '.join(['ProbeTree'] * (arity + 1))
        hypotheses = ' → '.join(f'P {x} → Q {x}' for x in args)
        definition = f'inductive ProbeTree where\n  | tip : Int → ProbeTree\n  | node : {child_types}\n\n'
        statement = definition + f'''theorem target (P Q : ProbeTree → Prop)
    (hp : ∀ z, P (ProbeTree.tip z)) (hq : ∀ z, Q (ProbeTree.tip z))
    (sp : ∀ {children}, {hypotheses} → P (ProbeTree.node {children}))
    (sq : ∀ {children}, {hypotheses} → P (ProbeTree.node {children}) → Q (ProbeTree.node {children})) :
    ∀ t, P t ∧ Q t := by
'''
        rows.append(dict(id=f'fresh_tree_{arity}', family='fresh_tree_composition', theorem='target',
            statement=statement, witness='  intro t\n  induction t <;> aesop\n', split='composition'))
    rows.append(dict(id='fresh_nat_product', family='fresh_product_composition', theorem='target',
        statement='''theorem target (P : Nat → Nat → Prop) (h0 : P 0 0)
    (hs : ∀ i j, P i j → P (i+1) j) (ht : ∀ i j, P i j → P i (j+1)) :
    ∀ i j, P i j := by
''', witness='''  intro i
  induction i with
  | zero =>
    intro j
    induction j <;> aesop
  | succ i ih =>
    intro j
    exact hs i j (ih j)
''', split='composition'))
    rows.append(dict(id='fresh_list_nat_product', family='fresh_product_composition', theorem='target',
        statement='''theorem target (P : List Int → Nat → Prop) (h0 : P [] 0)
    (hs : ∀ a xs n, P xs n → P (a :: xs) n) (ht : ∀ xs n, P xs n → P xs (n+1)) :
    ∀ xs n, P xs n := by
''', witness='''  intro xs
  induction xs with
  | nil =>
    intro n
    induction n <;> aesop
  | cons a xs ih =>
    intro n
    exact hs a xs n (ih n)
''', split='composition'))
    return rows


def prepare(args):
    args.output.mkdir(parents=True, exist_ok=False)
    b = args.bundle
    training = b / 'runs/cross-context-panel-20261119'
    if sha(training / 'manifest.json') != '131818321e273d93c2bf687437cc4b6d814e24db72787dfe9b534fd107f029b0':
        raise RuntimeError('Training bank changed')
    tasks = json.loads((training / 'tasks.json').read_text())
    train = [dict(id=r['id'], family=r['family'], theorem='target', statement=r['statement'],
                  split='retention') for r in tasks]
    old = b / 'runs/procedure-transfer-panel-20261026'
    if sha(old / 'manifest.json') != '83ad8c87e356768e550839cc742a62c171558e312fbb92226caceaba6b01c15d':
        raise RuntimeError('Original composition panel changed')
    manifest = json.loads((old / 'manifest.json').read_text())
    for name, expected in manifest['files'].items():
        if sha(old / name) != expected: raise RuntimeError('Old composition input changed')
    witnesses = {r['task_id']: r for r in lean.rows(old / 'witnesses.jsonl')}
    override_path = b / 'runs/procedure-transfer-rational-diagnosis-20261026/witness_overlay.jsonl'
    if sha(override_path) != 'bd501bfededf2ada758dab6b52f2eda2b894f45334a6be2b882cfd50fbdf0f53':
        raise RuntimeError('Witness erratum changed')
    overrides = {r['task_id']: r for r in lean.rows(override_path)}
    evaluation = []
    for r in lean.rows(old / 'tasks.jsonl'):
        witness = witnesses[r['task_id']]['witness']
        if r['task_id'] in overrides:
            repair = overrides[r['task_id']]
            if repair['original_witness_sha256'] != lean.sha(witness) or repair['witness'] != witness.replace('ne_of_gt', '_root_.ne_of_gt'):
                raise RuntimeError('Witness-only repair is not exact')
            witness = repair['witness']
        evaluation.append(dict(id=r['task_id'], family=r['family'] + '/' + r['target_schema'],
            theorem=r['task_id'], statement=r['theorem_statement'], witness=witness, split='composition'))
    evaluation += fresh_evaluation()
    lean.write(args.output / 'train-tasks.json', train)
    lean.write(args.output / 'evaluation-tasks.json', [{k:v for k,v in r.items() if k != 'witness'} for r in evaluation])
    lean.write(args.output / 'evaluation-witnesses.json', evaluation)
    lean.write(args.output / 'config.json', CONFIG)
    sources = ['policy_improvement_data.py', 'policy_update_math.py', 'run_policy_improvement.py']
    lean.write(args.output / 'manifest.json', {'training_bank_manifest_sha256': sha(training / 'manifest.json'),
        'old_evaluation_manifest_sha256': sha(old / 'manifest.json'), 'witness_erratum_sha256': sha(override_path),
        'training_tasks': 20, 'composition_tasks': 20, 'evaluation_samples_per_policy': 640,
        'training_proposals': 320, 'policies': ['base'] + CONFIG['arms'],
        'source_sha256': {name:sha(Path(__file__).parent / name) for name in sources},
        'files': {p.name:sha(p) for p in sorted(args.output.iterdir())},
        'test_selection': 'All original sixteen roots plus four fresh multi-premise composition tasks; no model-score filtering',
        'scientific_parameter_updates': 0})


def authenticate(panel):
    m = json.loads((panel / 'manifest.json').read_text())
    for name, expected in m['files'].items():
        if sha(panel / name) != expected: raise RuntimeError('Panel changed: ' + name)
    for name, expected in m['source_sha256'].items():
        if sha(Path(__file__).parent / name) != expected: raise RuntimeError('Frozen source changed: ' + name)
    if json.loads((panel / 'config.json').read_text()) != CONFIG: raise RuntimeError('Configuration mismatch')
    return m


def validate(args):
    authenticate(args.panel)
    jobs = []
    for r in json.loads((args.panel / 'evaluation-witnesses.json').read_text()):
        for mode, suffix in [('witness', r['witness']), ('empty', '')]:
            jobs.append(dict(id=r['id'] + '/' + mode, code=lean.HEADER + r['statement'] + suffix +
                '\n#print axioms ' + r['theorem'] + '\n', verifier=str(args.bundle / 'verifier/DeepSeek-Prover-V1.5'),
                lake=str(args.bundle / 'lean/elan/bin/lake')))
    results = lean.verify_jobs(jobs, args.output, workers=8)
    passed = all(r['accepted'] == r['id'].endswith('/witness') and not r.get('system_errors') for r in results)
    lean.write(args.output.with_suffix('.summary.json'), {'passed':passed, 'checks':len(results)})
    if not passed: raise SystemExit('Composition instrument failed; no training allowed')


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('mode', choices=['prepare', 'validate'])
    for name in ('bundle', 'panel', 'output'): p.add_argument('--'+name, type=Path)
    a = p.parse_args()
    globals()[a.mode](a)


if __name__ == '__main__': main()
