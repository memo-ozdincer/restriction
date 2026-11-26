#!/usr/bin/env python3
"""Same-statement public RL cohort; preserve published verdicts and provenance."""
import argparse
import ast
import hashlib
import json
from collections import defaultdict
from pathlib import Path
import re
import sys

import pyarrow.parquet as pq

from track_near_misses import analyze, load

HEADER='import Mathlib\nimport Aesop\n\nset_option maxHeartbeats 0\n\nopen BigOperators Real Nat Topology Rat\n\n'


def load_canonicalizer():
    # Load only the two dependency-free functions without importing verl/PyTorch.
    ns = {}
    for path, name in [('verl/lean/utils.py','remove_comments'), ('verl/lean/proof_modes.py','canonicalize_proof')]:
        tree = ast.parse(Path(path).read_text())
        node = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == name)
        exec(compile(ast.Module(body=[node],type_ignores=[]),path,'exec'),ns)
    return ns['canonicalize_proof']


canonicalize_proof = load_canonicalizer()


def normalize(proof, sensitivity):
    proof=proof.rstrip('\n')+'\n'
    if sensitivity:
        return canonicalize_proof(proof)+'\n'
    return proof


def internal_body(raw):
    # Replicate the historical verifier's first closing fence.
    m=re.search(r'\n'+chr(96)*3,raw)
    return raw[:m.start()] if m else None


def prepare(data, public_path, sensitivity):
    # Do not alter or silently drop original rows (including unresolved).
    result={}
    for c, groups in data.items():
        result[c]={}
        for k, rows in groups.items():
            result[c][k]=[]
            for row in rows:
                r=dict(row)
                body=internal_body(r['proof'])
                if body is None:
                    assert not r['correct'] and r['failure_class']!='lean_rejected'
                    body=r['proof']
                r['proof']=normalize(body,sensitivity)
                result[c][k].append(r)
    keys={k[0]:k for k in data['c0']}
    external=defaultdict(list)
    for idx,r in enumerate(pq.read_table(public_path).to_pylist()):
        if r['problem_name'] not in keys: continue
        k=keys[r['problem_name']]
        assert r['formal_statement']==k[1]
        v=json.loads(r['result'])
        code=v.get('verified_code')
        prefix=HEADER+k[1]
        if not isinstance(code,str) or not code.startswith(prefix):
            # Unresolved or malformed external evidence: keep its slot.
            body=r['proof_code']
            correct=False
            fc='unresolved'
        else:
            body=code[len(prefix):]
            assert body==r['proof_code'], (k[0],idx)
            correct=r['status']=='success'
            assert correct==bool(v['complete'])
            fc='correct' if correct else 'unresolved' if v.get('system_errors') else 'lean_rejected'
        external[k].append(dict(proof=normalize(body,sensitivity),correct=correct,
            failure_class=fc,proposal_id=f'autores-row-{idx}'))
    assert set(external)==set(keys.values()) and all(len(v)==4 for v in external.values())
    result['public_v15rl']=external
    return result


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('root',type=Path);p.add_argument('public',type=Path);p.add_argument('output',type=Path)
    a=p.parse_args()
    sys.path.insert(0,str(Path.cwd()))
    data=load(a.root)
    inventory=json.loads(Path('research/experiments/failed_proof_corpus_20261125/external-inventory.json').read_text())
    expected=next(x['sha256'] for x in inventory if x['dataset']=='autores/DSP1.5RL-minif2f-sampling_4' and x['path'].endswith('.parquet'))
    assert hashlib.file_digest(a.public.open('rb'),'sha256').hexdigest()==expected
    all_results={}
    for tag,sens in [('literal',False),('canonical',True)]:
        prepared=prepare(data,a.public,sens)
        result=analyze(prepared,discovery_n=124,observation_n=4)
        all_results[tag]=result
        print(tag,len(result['records']),flush=True)
        for k,v in result['counts'].items():
            if k.endswith(('/all','/strict')):print(k,v,flush=True)
    with a.output.open('x') as f:json.dump(all_results,f,ensure_ascii=False,indent=2)
