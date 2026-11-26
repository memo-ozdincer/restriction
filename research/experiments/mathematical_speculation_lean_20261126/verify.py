"""Fresh-process Lean kernel verifier for the separate CLI pilot."""
import os
from pathlib import Path
import re
import subprocess
import time

ROOT=Path(__file__).resolve().parent
REPO=ROOT.parents[2]
TOOLCHAIN=REPO/'artifacts/lean-cli-verifier/lean-4.9.0-rc1-darwin_aarch64'
MATHLIB=REPO/'artifacts/lean-cli-verifier/mathlib-subset'
HEADER="""import Mathlib.Data.Real.Basic
import Mathlib.Tactic.Ring
import Mathlib.Tactic.Linarith
import Mathlib.Tactic.NormNum
import Mathlib.Tactic.Positivity
import Mathlib.Tactic.FieldSimp
import Aesop
import Mathlib.Algebra.BigOperators.Group.Finset
import Mathlib.Algebra.BigOperators.Ring
import Mathlib.Data.Complex.Basic
import Mathlib.Data.Nat.Factorial.Basic
import Mathlib.Data.Nat.Prime
import Mathlib.Tactic.IntervalCases
import Mathlib.Tactic.Contrapose
import Mathlib.Tactic.PushNeg
import Mathlib.Tactic.LinearCombination
set_option maxHeartbeats 0
open BigOperators Real Nat Rat
"""
ALLOWED={'propext','Classical.choice','Quot.sound'}
FORBIDDEN=re.compile(r'(?m)\b(?:sorry|admit|axiom|unsafe)\b|^\s*(?:import|theorem|lemma|def|abbrev|namespace|section|end|set_option|#\w+)\s')


def indent(body,spaces=2):
    # Preserve relative indentation and avoid allowing new top-level commands.
    import textwrap
    body=textwrap.dedent(body).strip('\n')
    return '\n'.join(' '*spaces+l if l.strip() else '' for l in body.splitlines())


def verify(statement,name,body,out,local_fact=None):
    out.mkdir(parents=True,exist_ok=True)
    t=time.monotonic()
    if not body.strip() or FORBIDDEN.search(body) or chr(96)*3 in body:
        return dict(accepted=False,reason='lexical_or_empty',elapsed_seconds=time.monotonic()-t)
    content=HEADER+'\n'+statement.rstrip()+'\n'
    if local_fact:
        typ,proof=local_fact
        if FORBIDDEN.search(typ) or FORBIDDEN.search(proof) or not typ.strip() or not proof.strip():
            return dict(accepted=False,reason='invalid_fact_lexical',elapsed_seconds=time.monotonic()-t)
        content+=f'  have h_help : {typ.strip()} := by\n'+indent(proof,4)+'\n'
    content+=indent(body)+'\n#print axioms '+name+'\n'
    path=out/'candidate.lean';path.write_text(content)
    env=dict(os.environ,LEAN_PATH=str(MATHLIB))
    try:
        p=subprocess.run([str(TOOLCHAIN/'bin/lean'),str(path)],env=env,capture_output=True,text=True,timeout=60)
        output=p.stdout+p.stderr
        (out/'lean-output.txt').write_text(output)
        m=re.search(rf"'{re.escape(name)}' depends on axioms: \[([^\]]*)\]",output)
        n=re.search(rf"'{re.escape(name)}' does not depend on any axioms",output)
        axioms=set(x.strip() for x in m.group(1).split(',') if x.strip()) if m else set()
        ok=p.returncode==0 and (m is not None or n is not None) and axioms<=ALLOWED
        return dict(accepted=bool(ok),reason='verified' if ok else 'lean_rejected_or_axiom_audit',returncode=p.returncode,axioms=sorted(axioms),elapsed_seconds=time.monotonic()-t)
    except subprocess.TimeoutExpired:
        return dict(accepted=False,reason='timeout',elapsed_seconds=time.monotonic()-t)
