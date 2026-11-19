#!/usr/bin/env python3
"""Bounded same-allocation follow-up: instantiate the supplied lemma locally."""
import argparse
from datetime import datetime
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import signal
import socket
import subprocess
import sys
import time


def write(path, value):
    temporary = path.with_suffix('.tmp')
    temporary.write_text(json.dumps(value, indent=2) + '\n')
    temporary.replace(path)


def load_module(path):
    # Spawned verifier workers must be able to import the module by filename.
    spec = importlib.util.spec_from_file_location(path.stem, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--workspace', type=Path, required=True)
    p.add_argument('--panel', type=Path, required=True)
    p.add_argument('--bundle', type=Path, required=True)
    p.add_argument('--action', choices=['run', 'generate', 'verify'], default='run')
    p.add_argument('--model-label', choices=['base', 'grpo'])
    a = p.parse_args()
    w, b = a.workspace, a.bundle
    out = w / 'materialization'
    if a.action != 'run':
        pilot = load_module(w / 'pilot.py')
        if a.action == 'generate':
            original = pilot.generation_requests
            def requests(args):
                rows = original(args)
                for row in rows:
                    row['prompt'] += '  have h := reusable_fact n\n'
                return rows
            pilot.generation_requests = requests
            pilot.generate(argparse.Namespace(phase='consumer', panel=a.panel,
                artifacts=None, model=b / 'models' / ('base' if a.model_label == 'base' else 'c1-final'),
                tokenizer=b / 'models/base', model_label=a.model_label,
                output=out / (a.model_label + '-consumer.jsonl')))
        else:
            pilot.verify_generated(argparse.Namespace(input=out / (a.model_label + '-consumer.jsonl'),
                output=out / (a.model_label + '-consumer-verified.jsonl'),
                verifier=b / 'verifier/DeepSeek-Prover-V1.5', lake=b / 'lean/elan/bin/lake'))
        return
    allocation = json.loads((w / 'allocation.json').read_text())
    job = allocation['SLURM_JOB_ID']
    if allocation['SLURM_JOB_ACCOUNT'] != 'def-zhijing' or socket.gethostname() != allocation['node']:
        raise RuntimeError('Wrong allocation')
    if 'job_' + job not in Path('/proc/self/cgroup').read_text():
        raise RuntimeError('Outside allocation cgroup')
    info = subprocess.check_output(['scontrol', 'show', 'job', job, '-o'], text=True)
    if 'JobState=RUNNING' not in info:
        raise RuntimeError('Allocation not running')
    end = next(x.split('=', 1)[1] for x in info.split() if x.startswith('EndTime='))
    deadline = datetime.fromisoformat(end).timestamp() - 120
    if deadline - time.time() < 480:
        raise RuntimeError('Insufficient time for bounded follow-up')
    original_status = json.loads((w / 'experiment/status.json').read_text())
    if original_status['state'] != 'complete':
        raise RuntimeError('Original experiment must finish first')
    if hashlib.sha256((a.panel / 'manifest.json').read_bytes()).hexdigest() != original_status['panel_sha256']:
        raise RuntimeError('Original panel changed')
    if hashlib.sha256((w / 'pilot.py').read_bytes()).hexdigest() != original_status['pilot_sha256']:
        raise RuntimeError('Frozen pilot changed')
    manifest = json.loads((a.panel / 'manifest.json').read_text())
    for name, digest in manifest['files'].items():
        if hashlib.sha256((a.panel / name).read_bytes()).hexdigest() != digest:
            raise RuntimeError('Panel input changed: ' + name)
    out.mkdir(exist_ok=False)
    state = {'state': 'running', 'job_id': job, 'started_unix': time.time(),
             'deadline_unix': deadline, 'phases': [], 'new_training': False,
             'prefix_added': '  have h := reusable_fact n\n',
             'source_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
             'registration_sha256': hashlib.sha256((w / 'materialization-registration.md').read_bytes()).hexdigest()}
    env = os.environ.copy()
    env.update(ELAN_HOME=str(b / 'lean/elan'), OMP_NUM_THREADS='1', OPENBLAS_NUM_THREADS='1',
               MKL_NUM_THREADS='1', CUDA_VISIBLE_DEVICES=allocation['CUDA_VISIBLE_DEVICES'],
               VLLM_WORKER_MULTIPROC_METHOD='spawn', TOKENIZERS_PARALLELISM='false')
    try:
        for label in ('base', 'grpo'):
            for action in ('generate', 'verify'):
                entry = {'model': label, 'action': action, 'started_unix': time.time()}
                state['phases'].append(entry)
                write(out / 'status.json', state)
                if deadline - time.time() < 60:
                    raise TimeoutError('Follow-up deadline')
                command = [sys.executable, '-u', str(Path(__file__)), '--workspace', str(w),
                    '--panel', str(a.panel), '--bundle', str(b), '--action', action, '--model-label', label]
                with (out / f'{label}-{action}.log').open('x') as log:
                    proc = subprocess.Popen(command, env=env, stdout=log, stderr=subprocess.STDOUT,
                                            start_new_session=True)
                    try:
                        entry['returncode'] = proc.wait(timeout=deadline - time.time())
                    finally:
                        try: os.killpg(proc.pid, signal.SIGTERM)
                        except ProcessLookupError: pass
                        try: proc.wait(timeout=10)
                        except subprocess.TimeoutExpired:
                            os.killpg(proc.pid, signal.SIGKILL)
                            proc.wait()
                        entry['ended_unix'] = time.time()
                if entry['returncode']:
                    raise RuntimeError('Phase failed: ' + label + '/' + action)
        state['state'] = 'complete'
    except Exception as error:
        state.update(state='incomplete', error=repr(error))
        raise
    finally:
        state['ended_unix'] = time.time()
        write(out / 'status.json', state)
        load_module(w / 'driver.py').analyze(out)


if __name__ == '__main__':
    main()
