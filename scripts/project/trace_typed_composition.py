#!/usr/bin/env python3
"""Observe one frozen unsuccessful composition search without changing its policy."""
import argparse
import hashlib
import json
from pathlib import Path
import sys


def main():
    p = argparse.ArgumentParser(description=__doc__)
    for n in ['bundle', 'output']: p.add_argument('--' + n, type=Path, required=True)
    a = p.parse_args(); b = a.bundle
    old = b / 'runs/typed-procedure-composition-20261119-runtime-fixed'
    audit = json.loads((old / 'independent-audit.json').read_text())
    assert audit['passed'] and audit['unresolved'] == 0 and audit['search_successes'] == 0
    row = next(x for x in json.loads((old / 'sources.json').read_text()) if x['id'] == 'pt_08/both')
    sha = lambda s: hashlib.sha256(s.encode()).hexdigest()
    assert sha(row['code']) == row['code_sha256']
    option = 'set_option trace.Meta.Tactic.solveByElim true\n'
    code = row['code'].replace('set_option maxHeartbeats 0\n', 'set_option maxHeartbeats 0\n' + option, 1)
    assert code.replace(option, '', 1) == row['code']
    a.output.mkdir(parents=True, exist_ok=False)
    (a.output / 'instrumented.lean').write_text(code)
    (a.output / 'manifest.json').write_text(json.dumps(dict(original_id=row['id'],
        original_code_sha256=row['code_sha256'], instrumented_code_sha256=sha(code),
        source_sha256=sha(Path(__file__).read_text()), change='Enable existing trace only',
        new_model_proposals=0, parameter_updates=0), indent=2) + '\n')
    sys.path.insert(0, str(b / 'verifier/DeepSeek-Prover-V1.5'))
    from prover.lean.verifier import verify_lean4_file
    result = verify_lean4_file(code, lake_path=str(b / 'lean/elan/bin/lake'),
        lean_workspace=str(b / 'verifier/DeepSeek-Prover-V1.5/mathlib4'), timeout=60)
    (a.output / 'verifier-output.json').write_text(json.dumps(result, indent=2) + '\n')
    assert not result.get('system_errors')
    assert not result['complete']
    print(json.dumps(dict(complete=result['complete'], info_messages=len(result['infos']),
                          seconds=result['verify_time'])))


if __name__ == '__main__': main()
