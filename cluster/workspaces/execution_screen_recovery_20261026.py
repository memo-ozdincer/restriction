#!/usr/bin/env python3
"""One explicit recovery of the pre-output SSH PATH failure on job1176227.

No allocation, retry loop, training, or mutation of the original failed record.
The scientific source/panel/output are the same frozen screen. The only launch
change is obtaining the cluster environment with /bin/bash -lc.
"""
import hashlib
import json
import os
from pathlib import Path
import shlex
import subprocess
import sys
import time

BUNDLE = Path('/scratch/memoozd/rrl/restriction-rl')
REPO = BUNDLE / 'repository'
PRIOR = BUNDLE / 'runs/execution-workspace-watch-20261026-1176227'
RECOVERY = BUNDLE / 'runs/execution-screen-recovery-20261026-1176227'
OUTPUT = BUNDLE / 'runs/execution-base-screen-20261026-1176227'
COMMIT = '57b2d3013e6888dee4a4ad7520252ae4c47791e2'
DIGEST = 'c5513992dc40cda4f62896c2b53b5c4509f2d5934b245b2477da71b2a17fc0b8'


def write(name, value):
    path = RECOVERY / name
    temporary = path.with_suffix(path.suffix + '.tmp')
    temporary.write_text(json.dumps(value, indent=2, sort_keys=True) + '\n')
    temporary.replace(path)


def main():
    RECOVERY.mkdir(exist_ok=False)
    (RECOVERY / 'launcher_source.py').write_bytes(Path(__file__).read_bytes())
    prior = json.loads((PRIOR / 'status.json').read_text())
    if prior['status'] != 'failed' or OUTPUT.exists():
        raise RuntimeError('expected preserved failed launch and absent screen output')
    if "No such file or directory: 'scontrol'" not in (PRIOR / 'ssh.log').read_text():
        raise RuntimeError('different prior failure requires a new diagnosis')
    try:
        os.kill(prior['watcher_pid'], 0)
    except ProcessLookupError:
        pass
    else:
        raise RuntimeError('original launcher is still live; do not overlap')
    sys.path.insert(0, str(REPO))
    from scripts.project.wait_execution_workspace import validate_job, completed_logs
    import pwd
    info = subprocess.check_output(['scontrol', 'show', 'job', '1176227', '-o'], text=True)
    job = validate_job(info, 1176227, os.getuid(), pwd.getpwuid(os.getuid()).pw_name)
    if job['JobState'] != 'RUNNING' or job['NodeList'] != 'trig0025':
        raise RuntimeError('allocation changed')
    remote = [str(BUNDLE / 'environment/venv/bin/python'), '-B', '-u',
              str(PRIOR / 'source/scripts/project/run_execution_screen.py'),
              '--bundle', str(BUNDLE), '--panel', str(BUNDLE / 'runs/execution-pilot-panel-20261026'),
              '--output', str(OUTPUT), '--job-id', '1176227', '--commit', COMMIT,
              '--panel-sha256', DIGEST]
    command = ['ssh', '-n', '-T', '-o', 'BatchMode=yes', '-o', 'ConnectTimeout=15',
               '-o', 'ServerAliveInterval=30', '-o', 'ServerAliveCountMax=3', 'trig0025',
               shlex.join(['/bin/bash', '-lc', shlex.join(remote)])]
    write('command.json', command)
    state = {'status': 'starting', 'pid': os.getpid(), 'started_unix': time.time(),
             'job_id': 1176227, 'node': 'trig0025', 'scientific_commit': COMMIT,
             'panel_sha256': DIGEST, 'original_failure': str(PRIOR / 'ssh.log'),
             'launcher_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
             'output': str(OUTPUT), 'automatic_retry': False, 'automatic_training': False,
             'recovery_reason': 'non-login SSH PATH lacked scontrol; no screen output was created',
             'prelaunch_job_info': info}
    write('status.json', state)
    try:
        with (RECOVERY / 'ssh.log').open('x') as log:
            result = subprocess.run(command, stdout=log, stderr=subprocess.STDOUT,
                                    timeout=25200, check=False)
        state['returncode'] = result.returncode
        if result.returncode:
            raise RuntimeError('recovery transport/screen failed; inspect before any further launch')
        logs, certificates = completed_logs(OUTPUT)
        state.update(status='complete_pending_analysis', proof_logs={k:str(v) for k,v in logs.items()},
                     certificates=certificates)
    except Exception as error:
        state.update(status='failed_needs_inspection', error=repr(error))
        raise
    finally:
        state['ended_unix'] = time.time()
        write('status.json', state)


if __name__ == '__main__':
    main()
