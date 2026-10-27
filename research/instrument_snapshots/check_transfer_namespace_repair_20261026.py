"""Hypothesis: qualifying ne_of_gt resolves production-prefix Nat ambiguity.
Writes a separate evaluation-only witness overlay; never mutates frozen panel.
"""
import hashlib
import json
import os
from pathlib import Path
import sys

BUNDLE = Path('/scratch/memoozd/rrl/restriction-rl')
REPO = BUNDLE / 'repository'
STAGED = Path('/tmp/memoozd-procedure-transfer-verifier-20261026')
OUT = Path(__file__).resolve().parent
PANEL = BUNDLE / 'runs/procedure-transfer-panel-20261026'
os.environ['ELAN_HOME'] = str(BUNDLE / 'lean/elan')
os.environ['DEEPSEEK_PROVER_ROOT'] = str(STAGED)
sys.path.insert(0, str(REPO))
from verl.lean.verifier import code_prefix
from prover.lean.verifier import verify_lean4_file

sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
digest = lambda s: hashlib.sha256(s.encode()).hexdigest()
frozen_hashes = {p.name: sha(p) for p in PANEL.iterdir() if p.is_file()}
tasks = [json.loads(line) for line in (PANEL / 'tasks.jsonl').read_text().splitlines()]
witnesses = {row['task_id']: row for row in map(json.loads, (PANEL / 'witnesses.jsonl').read_text().splitlines())}
overlay = []
checks = []
for task in tasks[12:16]:
    original = witnesses[task['task_id']]
    assert digest(original['witness']) == original['witness_sha256']
    assert digest(task['theorem_statement']) == original['statement_sha256'] == task['statement_sha256']
    assert original['witness'].count('ne_of_gt') == 3
    repaired = original['witness'].replace('ne_of_gt', '_root_.ne_of_gt')
    overlay.append({'task_id':task['task_id'], 'statement_sha256':task['statement_sha256'],
        'original_witness_sha256':original['witness_sha256'], 'witness':repaired,
        'witness_sha256':digest(repaired)})
    code = code_prefix + task['theorem_statement'] + repaired
    (OUT / f"{task['task_id']}_candidate.lean").write_text(code)
    result = verify_lean4_file(code, lean_workspace=str(STAGED/'mathlib4'), timeout=120)
    (OUT / f"{task['task_id']}_candidate.raw.json").write_text(json.dumps(result,indent=2)+'\n')
    checks.append({'task_id':task['task_id'], 'source_sha256':digest(code),
        **{k:result.get(k) for k in ('pass','complete','sorries','errors','warnings','infos','system_errors','verify_time')}})
    print(task['task_id'],json.dumps(checks[-1]),flush=True)
(OUT/'witness_overlay.jsonl').write_text(''.join(json.dumps(row)+'\n' for row in overlay))
assert frozen_hashes == {p.name:sha(p) for p in PANEL.iterdir() if p.is_file()}
report = {'status':'passed' if all(r['complete'] for r in checks) else 'failed',
    'hypothesis':__doc__, 'training_allowed':False, 'model_inference_performed':False,
    'physical_lean_calls':5, 'calls':'one raw original pt12 + four candidate raw production checks',
    'root_cause':'Production code_prefix opens Nat; unqualified ne_of_gt is ambiguous between _root_.ne_of_gt and Nat.ne_of_gt in field_simp. Original raw result has three errors, no warnings, no sorries.',
    'repair':'Exactly three ne_of_gt identifiers per witness become _root_.ne_of_gt. No other proof, statement, model-input, or verifier changes.',
    'original_panel_unchanged':True, 'original_panel_hashes':frozen_hashes,
    'production_wrapper_sha256':sha(REPO/'verl/lean/verifier.py'),
    'staged_verifier_sha256':sha(STAGED/'prover/lean/verifier.py'),
    'overlay_sha256':sha(OUT/'witness_overlay.jsonl'), 'checks':checks}
(OUT/'diagnosis.json').write_text(json.dumps(report,indent=2)+'\n')
assert report['status'] == 'passed'
