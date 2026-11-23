"""Test which explicit certificates are needed on the two changed inequality proofs."""
import argparse
import json
from pathlib import Path
from run_recursive_grpo import TRANSFER, lean


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('bundle',type=Path)
    p.add_argument('panel',type=Path)
    p.add_argument('output',type=Path)
    a = p.parse_args()
    quartic = 'lean_workbook_plus_78550'
    cube = 'weighted_cube_transfer'
    statements = {r['theorem']:r['statement'] for r in json.loads(a.panel.read_text())['panel']}
    statements[cube] = f'theorem {cube} {TRANSFER[cube]} := by\n'
    jobs = []
    for name, prefix, terms in [
        (cube, '', ['sq_nonneg (a - b)', 'mul_self_nonneg (a + b)']),
        (quartic,'intro a b\n  simp [add_comm]\n  ', ['sq_nonneg (a ^ 2 - a * b)', 'sq_nonneg (b ^ 2 - a * b)']),
    ]:
        for i in range(4):
            selected = [term for j,term in enumerate(terms) if i & (1<<j)]
            hint = ' ['+', '.join(selected)+']' if selected else ''
            code = lean.HEADER + statements[name] + '  ' + prefix + 'nlinarith' + hint + '\n#print axioms ' + name
            jobs.append(dict(id=f'{name}/{i}',code=code,lake=str(a.bundle/'lean/elan/bin/lake'),
                             verifier=str(a.bundle/'verifier/DeepSeek-Prover-V1.5')))
    verdicts = lean.verify_jobs(jobs,a.output,workers=2)
    assert all(not v.get('system_errors') for v in verdicts)


if __name__=='__main__':
    main()
