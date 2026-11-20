#!/usr/bin/env python3
"""Run one frozen repaired-library composition test inside a bounded keeper."""
import argparse
from datetime import datetime
import hashlib
import json
import os
from pathlib import Path
import signal
import socket
import subprocess
import sys
import time


def write(path, data):
    temporary = path.with_suffix('.tmp')
    temporary.write_text(json.dumps(data, indent=2) + '\n')
    temporary.replace(path)


def digest(path):
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(8*1024**2), b''):
            h.update(chunk)
    return h.hexdigest()


def main():
    p = argparse.ArgumentParser(description=__doc__)
    for name in ('workspace', 'bundle', 'panel', 'validation', 'prior-workspace'):
        p.add_argument('--' + name, type=Path, required=True)
    p.add_argument('--panel-sha256', required=True)
    a = p.parse_args()
    w, b = a.workspace, a.bundle
    allocation = json.loads((w / 'allocation.json').read_text())
    job = allocation['SLURM_JOB_ID']
    if allocation['SLURM_JOB_ACCOUNT'] != 'def-zhijing' or socket.gethostname() != allocation['node']:
        raise RuntimeError('Wrong allocation account or node')
    if 'job_' + job not in Path('/proc/self/cgroup').read_text():
        raise RuntimeError('Not inside recorded allocation')
    info = subprocess.check_output(['scontrol', 'show', 'job', job, '-o'], text=True)
    if 'JobState=RUNNING' not in info or 'Account=def-zhijing' not in info:
        raise RuntimeError('Allocation no longer running under requested account')
    end = next(t.split('=', 1)[1] for t in info.split() if t.startswith('EndTime='))
    deadline = datetime.fromisoformat(end).timestamp() - 120
    if deadline - time.time() < 900:
        raise RuntimeError('Less than fifteen minutes remain')
    if digest(a.panel / 'manifest.json') != a.panel_sha256:
        raise RuntimeError('Panel manifest changed')
    import repaired_library
    repaired_library.authenticate(a.panel)
    out = w / 'repaired-library'
    out.mkdir(exist_ok=False)
    status = {'state': 'starting', 'started_unix': time.time(), 'job_id': job,
        'panel_sha256': a.panel_sha256, 'deadline_unix': deadline, 'phases': [],
        'driver_sha256': digest(Path(__file__)), 'parameter_updates': 0,
        'allocation': allocation, 'initial_slurm_job': info,
        'validation_sha256': digest(a.validation)}
    write(out / 'status.json', status)
    env = os.environ.copy()
    env.update(ELAN_HOME=str(b / 'lean/elan'), OMP_NUM_THREADS='1', OPENBLAS_NUM_THREADS='1',
        MKL_NUM_THREADS='1', TOKENIZERS_PARALLELISM='false', VLLM_WORKER_MULTIPROC_METHOD='spawn',
        CUDA_VISIBLE_DEVICES=allocation['CUDA_VISIBLE_DEVICES'], PYTHONDONTWRITEBYTECODE='1')

    def phase(name, command):
        remaining = deadline - time.time()
        if remaining < 60:
            raise TimeoutError('Screen allocation budget exhausted')
        entry = {'name': name, 'started_unix': time.time(), 'command': command}
        status.update(state='running', current_phase=name)
        status['phases'].append(entry)
        write(out / 'status.json', status)
        with (out / (name + '.log')).open('x') as log:
            proc = subprocess.Popen(command, env=env, stdout=log, stderr=subprocess.STDOUT,
                                    start_new_session=True)
            try:
                entry['returncode'] = proc.wait(timeout=remaining)
            finally:
                try: os.killpg(proc.pid, signal.SIGTERM)
                except ProcessLookupError: pass
                try: proc.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    os.killpg(proc.pid, signal.SIGKILL)
                    proc.wait()
                entry['ended_unix'] = time.time()
                write(out / 'status.json', status)
        if entry['returncode']:
            raise RuntimeError('Phase failed: ' + name)

    try:
        identity = {p.name: {'bytes': p.stat().st_size, 'sha256': digest(p)}
                    for p in sorted((b / 'models/base').iterdir())
                    if p.suffix in ('.json', '.safetensors')}
        prior = json.loads((a.prior_workspace / 'experiment/model-identities.json').read_text())
        if identity != prior['base']:
            raise RuntimeError('Pristine base/tokenizer differs from pinned original model')
        write(out / 'model-identity.json', identity)
        # Warm imports separately, before scientific candidates. This is logged
        # and charged, and cannot relax any candidate's 60-second timeout.
        warm = (
            'import sys,json; from pathlib import Path; '
            'b=Path(sys.argv[1]); sys.path.insert(0,str(b/"verifier/DeepSeek-Prover-V1.5")); '
            'from prover.lean.verifier import verify_lean4_file; '
            'r=verify_lean4_file("import Mathlib\\nimport Aesop\\ntheorem warmup : True := by trivial\\n", '
            'lake_path=str(b/"lean/elan/bin/lake"), '
            'lean_workspace=str(b/"verifier/DeepSeek-Prover-V1.5/mathlib4"),timeout=300); '
            'Path(sys.argv[2]).write_text(json.dumps(r,indent=2)); '
            'sys.exit(0 if r.get("complete") else 1)')
        phase('node-import-warmup', [sys.executable, '-c', warm, str(b), str(out / 'warmup.json')])
        common = [sys.executable, '-u', str(Path(__file__).parent / 'repaired_library.py')]
        phase('generate', common + ['generate', '--panel', str(a.panel), '--bundle', str(b),
            '--validation', str(a.validation), '--output', str(out / 'candidates.jsonl')])
        phase('verify', common + ['verify', '--panel', str(a.panel), '--bundle', str(b),
            '--input', str(out / 'candidates.jsonl'), '--output', str(out / 'matrix')])
        status['state'] = 'complete'
        status['analysis_sha256'] = digest(out / 'matrix/analysis.json')
    except Exception as error:
        status.update(state='incomplete', error=repr(error))
        raise
    finally:
        status['ended_unix'] = time.time()
        status['allocation_release_requested_unix'] = time.time()
        write(out / 'status.json', status)
        subprocess.run(['scancel', job], check=True)


if __name__ == '__main__':
    main()
