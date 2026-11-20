#!/usr/bin/env python3
"""Bound one manually launched, four-arm update/evaluation to its Slurm lease."""
import argparse
from datetime import datetime
import json
import os
from pathlib import Path
import signal
import socket
import subprocess
import sys
import time
from run_cross_context_screen import digest, write
import policy_improvement_data as data


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for name in ['bundle','workspace','panel','validation','prior-workspace']:
        p.add_argument('--'+name,type=Path,required=True)
    p.add_argument('--panel-sha256',required=True)
    a=p.parse_args()
    b,w=a.bundle,a.workspace
    allocation=json.loads((w/'allocation.json').read_text())
    job=allocation['SLURM_JOB_ID']
    if allocation['SLURM_JOB_ACCOUNT']!='def-zhijing' or socket.gethostname()!=allocation['node']:
        raise RuntimeError('Wrong allocated account/node')
    if 'job_'+job not in Path('/proc/self/cgroup').read_text(): raise RuntimeError('Outside job cgroup')
    info=subprocess.check_output(['scontrol','show','job',job,'-o'],text=True)
    if 'JobState=RUNNING' not in info or 'Account=def-zhijing' not in info: raise RuntimeError('Job not running')
    end=next(t.split('=',1)[1] for t in info.split() if t.startswith('EndTime='))
    deadline=datetime.fromisoformat(end).timestamp()-180
    if deadline-time.time()<5400: raise RuntimeError('Need ninety minutes remaining')
    if digest(a.panel/'manifest.json')!=a.panel_sha256: raise RuntimeError('Panel changed')
    data.authenticate(a.panel)
    validation=json.loads(a.validation.with_suffix('.summary.json').read_text())
    checks=data.lean.rows(a.validation)
    if validation!={'passed':True,'checks':40} or len(checks)!=40 or any(
        r['accepted']!=r['id'].endswith('/witness') or r.get('system_errors') for r in checks):
        raise RuntimeError('Composition instrument not validated')
    out=w/'policy-improvement'
    out.mkdir(exist_ok=False)
    status=dict(state='starting',started_unix=time.time(),job_id=job,allocation=allocation,
        initial_slurm_job=info,deadline_unix=deadline,panel_manifest_sha256=a.panel_sha256,
        validation_sha256=digest(a.validation),driver_sha256=digest(Path(__file__)),phases=[])
    write(out/'status.json',status)
    env=os.environ.copy()
    env.update(ELAN_HOME=str(b/'lean/elan'),OMP_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1',
        MKL_NUM_THREADS='1',TOKENIZERS_PARALLELISM='false',PYTHONDONTWRITEBYTECODE='1',
        PYTHONPATH=str(b/'environment/overlays/peft-0.10.0'),CUDA_VISIBLE_DEVICES=allocation['CUDA_VISIBLE_DEVICES'])
    source=Path(__file__).parent
    def phase(name,cmd):
        remaining=deadline-time.time()
        if remaining<60: raise TimeoutError('Lease budget exhausted')
        row=dict(name=name,command=cmd,started_unix=time.time())
        status.update(state='running',current_phase=name)
        status['phases'].append(row)
        write(out/'status.json',status)
        with (out/(name+'.log')).open('x') as log:
            proc=subprocess.Popen(cmd,env=env,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
            try: row['returncode']=proc.wait(timeout=remaining)
            finally:
                try: os.killpg(proc.pid,signal.SIGTERM)
                except ProcessLookupError: pass
                try: proc.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    os.killpg(proc.pid,signal.SIGKILL);proc.wait()
                row['ended_unix']=time.time()
                write(out/'status.json',status)
        if row['returncode']: raise RuntimeError('Phase failed: '+name)
    def scientific(mode,extra):
        return [sys.executable,'-u',str(source/'run_policy_improvement.py'),mode,
            '--bundle',str(b),'--panel',str(a.panel)]+extra
    try:
        identity={p.name:dict(bytes=p.stat().st_size,sha256=digest(p)) for p in sorted((b/'models/base').iterdir())
            if p.suffix in ('.json','.safetensors')}
        prior=json.loads((a.prior_workspace/'experiment/model-identities.json').read_text())
        if identity!=prior['base']: raise RuntimeError('Base model/tokenizer changed')
        write(out/'model-identity.json',identity)
        warm='import sys,json; from pathlib import Path; b=Path(sys.argv[1]); sys.path.insert(0,str(b/"verifier/DeepSeek-Prover-V1.5")); from prover.lean.verifier import verify_lean4_file; r=verify_lean4_file("import Mathlib\\nimport Aesop\\ntheorem warmup : True := by trivial\\n",lake_path=str(b/"lean/elan/bin/lake"),lean_workspace=str(b/"verifier/DeepSeek-Prover-V1.5/mathlib4"),timeout=300); Path(sys.argv[2]).write_text(json.dumps(r,indent=2)); sys.exit(0 if r.get("complete") else 1)'
        phase('warmup',[sys.executable,'-c',warm,str(b),str(out/'warmup.json')])
        phase('collect',scientific('collect',['--output',str(out/'traces.jsonl')]))
        phase('reward',[sys.executable,'-u',str(source/'cross_context_credit.py'),'score',
            '--bundle',str(b),'--panel',str(b/'runs/cross-context-panel-20261119'),
            '--input',str(out/'traces.jsonl'),'--output',str(out/'matrix')])
        for arm in data.CONFIG['arms']:
            phase('train-'+arm,scientific('train',['--input',str(out/'traces.jsonl'),'--matrix',str(out/'matrix'),
                '--arm',arm,'--output',str(out/arm)]))
        (out/'evaluation').mkdir()
        for arm in ['base']+data.CONFIG['arms']:
            phase('evaluate-'+arm,scientific('evaluate',['--arm',arm,'--adapter',str(out/arm),
                '--output',str(out/'evaluation'/(arm+'.jsonl'))]))
        phase('verify',scientific('verify',['--input',str(out/'evaluation'),'--output',str(out/'judgments')]))
        status.update(state='complete',analysis_sha256=digest(out/'judgments/analysis.json'))
    except BaseException as error:
        status.update(state='incomplete',error=repr(error))
        raise
    finally:
        status.update(ended_unix=time.time(),allocation_release_requested_unix=time.time())
        write(out/'status.json',status)
        subprocess.run(['scancel',job],check=True)


if __name__=='__main__': main()
