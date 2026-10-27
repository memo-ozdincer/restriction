"""Hypothesis: compiler-valid rational witness triggers production warning gate.
Read frozen evaluation-only witness; no training or model outputs are used.
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

tasks = [json.loads(line) for line in (PANEL / 'tasks.jsonl').read_text().splitlines()]
witnesses = [json.loads(line) for line in (PANEL / 'witnesses.jsonl').read_text().splitlines()]
task = tasks[12]
witness = witnesses[12]
assert task['task_id'] == witness['task_id'] == 'pt_12'
code = code_prefix + task['theorem_statement'] + witness['witness']
(OUT / 'pt_12_original.lean').write_text(code)
result = verify_lean4_file(code, lean_workspace=str(STAGED / 'mathlib4'), timeout=120)
(OUT / 'pt_12_original.raw.json').write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps({k: result.get(k) for k in ('pass', 'complete', 'sorries', 'errors', 'warnings', 'infos', 'system_errors', 'verify_time')}, indent=2))
