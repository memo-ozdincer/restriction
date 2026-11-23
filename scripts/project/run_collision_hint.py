"""Pair unguided and hinted model proofs on an end-to-end theorem and its moment bridge."""
import argparse
import json
from pathlib import Path

import interface_discovery_pilot as lean
import run_policy_improvement as policy

HEADER = 'import Mathlib\nopen BigOperators Finset\nset_option maxRecDepth 8192\nset_option maxHeartbeats 2000000\n\n'
ROOT = '''theorem target (B : Finset ℕ) (hB : B.card = 42) (hI : B ⊆ Icc 1 2142) :
    ∃ X Y : Finset ℕ, X ⊆ B ∧ Y ⊆ B ∧ X.Nonempty ∧ Y.Nonempty ∧ Disjoint X Y ∧
      (∑ x in X, x) = ∑ y in Y, y ∧ (∑ x in X, x^2) = ∑ y in Y, y^2 := by
'''
BRIDGE = '''theorem target (U V : Finset ℕ) (hu : U ⊆ Icc 1 2142) (hv : V ⊆ Icc 1 2142)
    (hs : (∑ x in U, x) = ∑ x in V, x)
    (hw : (∑ x in U, x*(2142-x)) = ∑ x in V, x*(2142-x)) :
    (∑ x in U, x^2) = ∑ x in V, x^2 := by
'''
TASKS = [
    ('root', ROOT,'Use the pair of subset sums of x and x*(2142-x) as the pigeonhole key.', 2048),
    ('bridge', BRIDGE,'For each x in the interval, x*(2142-x) + x^2 = x*2142. Sum this identity.',512),
]


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('bundle',type=Path)
    p.add_argument('output',type=Path)
    a = p.parse_args()
    model, tokenizer = policy.load_model(a.bundle)
    adapter = a.bundle/'runs/recursive-grpo-20261123-1398215/recursive/adapter'
    model = policy.add_adapter(model, adapter)
    jobs = {}
    cells = {}
    for index,(name,statement,hint,limit) in enumerate(TASKS):
        for arm in ('plain','hint'):
            cell = name+'-'+arm
            prompt = lean.PREFIX+HEADER+('' if arm=='plain' else '-- '+hint+'\n')+statement
            rows = policy.sample(model,tokenizer,prompt,20261125+index,limit,False)
            lean.write(a.output/(cell+'.json'),dict(prompt=prompt,rows=rows))
            details = []
            for row in rows:
                body,error = lean.completion_code(row['text'])
                key = None
                if not error:
                    code = HEADER+statement+body+'\n#print axioms target\n'
                    key = lean.sha(code)
                    jobs[key] = dict(id=key,code=code,lake=str(a.bundle/'lean/elan/bin/lake'),
                                     verifier=str(a.bundle/'verifier/DeepSeek-Prover-V1.5'))
                details.append(dict(index=row['sample_index'],finish=row['finish_reason'],parse_error=error,key=key))
            cells[cell]=details
    lean.write(a.output/'sources.json',{k:v['code'] for k,v in jobs.items()})
    verdicts=lean.verify_jobs(list(jobs.values()),a.output/'verdicts.jsonl',workers=8)
    by_key={r['id']:r for r in verdicts}
    summary={}
    for cell,rows in cells.items():
        for r in rows:
            verdict=by_key.get(r['key'],{})
            r.update(accepted=bool(verdict.get('accepted')),unresolved=bool(verdict.get('system_errors')))
        summary[cell]=dict(samples=len(rows),accepted=sum(r['accepted'] for r in rows),
            parse_errors=sum(bool(r['parse_error']) for r in rows),length=sum(r['finish']=='length' for r in rows),
            unresolved=sum(r['unresolved'] for r in rows))
    lean.write(a.output/'cells.json',cells)
    lean.write(a.output/'summary.json',summary)


if __name__=='__main__':
    main()
