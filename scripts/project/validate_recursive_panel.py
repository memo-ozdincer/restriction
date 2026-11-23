"""Check training witnesses and positive/negative transfer fixtures in the pilot runtime."""
import argparse
import json
from pathlib import Path

import interface_discovery_pilot as lean
from run_recursive_grpo import TRANSFER

WITNESSES = {
    'square_transfer': '  nlinarith [sq_nonneg (4*a*b + (a-b))]',
    'weighted_cube_transfer': '  nlinarith [mul_nonneg (sq_nonneg (b-a)) (show 0 ≤ b+2*a by linarith)]',
    'abs_transfer': '  by_cases h : 0 ≤ t+1\n  · rw [abs_of_nonneg h]; nlinarith [sq_nonneg (t+1)]\n  · rw [abs_of_neg (lt_of_not_ge h)]; nlinarith [sq_nonneg (t+1)]',
    'finite_witness_transfer': '  exact ⟨∅, ∅, by simp⟩',
}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('bundle',type=Path)
    p.add_argument('panel',type=Path)
    p.add_argument('output',type=Path)
    a = p.parse_args()
    roots = {}
    for row in json.loads(a.panel.read_text())['panel']:
        proof = next(iter(row['held_examples'].values()))['proof'].split('```')[0]
        roots[row['theorem']] = row['statement'], proof
    for name, body in WITNESSES.items():
        roots[name] = f'theorem {name} {TRANSFER[name]} := by\n', body
    jobs = []
    for name,(statement,proof) in roots.items():
        for label,body in [('positive', proof), ('negative','  exact False.elim False.intro')]:
            jobs.append(dict(id=name+'/'+label,code=lean.HEADER+statement+body+'\n#print axioms '+name,
                             lake=str(a.bundle/'lean/elan/bin/lake'),verifier=str(a.bundle/'verifier/DeepSeek-Prover-V1.5')))
    results = lean.verify_jobs(jobs, a.output, workers=4)
    if any(r.get('system_errors') or r['accepted'] != r['id'].endswith('/positive') for r in results):
        raise RuntimeError('Panel check failed')


if __name__ == '__main__':
    main()
