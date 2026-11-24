"""Frozen, byte-preserving joins of failed C0 training attempts; no new model calls."""
import argparse
from collections import Counter, defaultdict
from concurrent.futures import ProcessPoolExecutor
import hashlib
import json
import multiprocessing
import os
from pathlib import Path
import queue
import re
import signal
import subprocess
import threading
import time

import interface_discovery_pilot as lean
from prepare_execution_pilot import prefix_boundaries, sha256, SOURCE_SHA256, VALIDATION_SHA256

SELECTION = 'failed-experience-join-20261124/'
CONFIG = dict(roots=32, samples=32, joins_per_root=128, workers=4,
              command_timeout_seconds=60, root_timeout_seconds=300,
              gate_roots=4, gate_joined_bodies=8)


def cuts(body):
    return [len(p) for p, _, _, _ in prefix_boundaries(body)]


def candidates(rows):
    """No new bytes in a candidate body. Hash ranking precedes all new checks."""
    bodies = [r['body'] for r in rows]
    splits = [(i, k) for i, b in enumerate(bodies) for k in cuts(b)]
    control = defaultdict(list)
    for i, body in enumerate(bodies): control[body].append(dict(kind='original', sample=i))
    for i, k in splits:
        control[bodies[i][:k]].append(dict(kind='prefix', sample=i, cut=k))
        control[bodies[i][k:]].append(dict(kind='suffix', sample=i, cut=k))
    for i, body in enumerate(bodies):
        for a in cuts(body):
            for b in cuts(body):
                if a < b: control[body[:a]+body[b:]].append(dict(kind='deletion', sample=i, left=a, right=b))
    joins = defaultdict(list)
    for i, a in splits:
        for j, b in splits:
            if i == j or bodies[i] == bodies[j]: continue
            body = bodies[i][:a] + bodies[j][b:]
            if body in bodies: continue
            joins[body].append(dict(prefix_sample=i, prefix_cut=a, suffix_sample=j, suffix_cut=b))
    name = rows[0]['record']['theorem_name']
    chosen = sorted(joins, key=lambda b: lean.sha(name+'\n'+b))[:CONFIG['joins_per_root']]
    items = {}
    for body, origins in control.items(): items[lean.sha(body)] = dict(body=body, controls=origins, joins=[])
    for body in chosen:
        key = lean.sha(body)
        items.setdefault(key,dict(body=body, controls=[], joins=[]))['joins'] = joins[body]
    return items


def prepare(bundle, output):
    output.mkdir(parents=True,exist_ok=False)
    repo=bundle/'repository';data=repo/'data/mff-lwb-10k-seen.parquet';vpath=bundle/'runs/c0-base-20260804-seed42-complete/validation.json'
    assert sha256(data)==SOURCE_SHA256 and sha256(vpath)==VALIDATION_SHA256
    import pandas as pd
    frame=pd.read_parquet(data);train={r['theorem_full_name']:r for r in frame.to_dict('records') if r['split']=='train'}
    assert len(train)==9655
    validation=json.loads(vpath.read_text());assert validation['status']=='valid' and validation['samples_per_theorem']==32
    specs=[]
    for s in validation['proof_logs']:
        path=bundle/s['path'].removeprefix('/scratch/memoozd/rl/restriction/')
        assert sha256(path)==s['sha256'];specs.append(dict(path=str(path),sha256=s['sha256']))
    counts=Counter();statistics={};eligible_bodies=defaultdict(set);raw_count=0
    for spec in specs:
        for line in Path(spec['path']).open():
            r=json.loads(line);name=r['theorem_name'];assert name in train
            for a,b in [('theorem_statement','theorem_statement'),('informal_statement','informal_statement'),('context','src_context')]:assert r[a]==train[name][b]
            raw_count+=1;counts[name]+=1
            if counts[name]>32:continue
            s=statistics.setdefault(name,dict(correct=0,parse_errors=0))
            s['correct']+=r['correct'] is True
            body,error=lean.completion_code(r['proof']);s['parse_errors']+=bool(error)
            if not error and cuts(body):eligible_bodies[name].add(body)
    assert raw_count==validation['raw_generated_and_verified_proposals'] and len(counts)==9655 and all(n>=32 for n in counts.values())
    eligible=[n for n,s in statistics.items() if s==dict(correct=0,parse_errors=0) and len(eligible_bodies[n])>=4
              and re.match(r'^theorem '+re.escape(n)+r'\b',train[n]['theorem_statement']) and re.search(r':=\s*by\s*$',train[n]['theorem_statement'])]
    selected=sorted(eligible,key=lambda n:lean.sha(SELECTION+n))[:32];assert len(selected)==32
    bank={n:[] for n in selected};seen=Counter()
    for spec in specs:
        for line_number,line in enumerate(Path(spec['path']).open(),1):
            r=json.loads(line);n=r['theorem_name']
            if n not in bank:continue
            index=seen[n];seen[n]+=1
            if index>=32:continue
            body,error=lean.completion_code(r['proof']);assert not error and r['correct'] is False
            bank[n].append(dict(record=r,sample_index=index,body=body,cuts=cuts(body),source=spec,source_line=line_number))
    panel=[]
    for index,name in enumerate(selected):
        rows=bank[name];assert len(rows)==32
        panel.append(dict(index=index,name=name,statement=rows[0]['record']['theorem_statement'],rows=rows,candidates=candidates(rows)))
    lean.write(output/'panel.json',panel)
    lean.write(output/'manifest.json',dict(config=CONFIG,panel_sha256=sha256(output/'panel.json'),eligible_roots=len(eligible),source_logs=specs,
        dataset_sha256=SOURCE_SHA256,validation_sha256=VALIDATION_SHA256,raw_proposals=raw_count,registered_proposals=9655*32,
        selected=selected,selection=SELECTION,model='deepseek-ai/DeepSeek-Prover-V1.5-SFT',model_revision='e9a6e6fbb67620d4e9c4944bc51ff7c435af12da',
        unique_controls=sum(sum(bool(x['controls']) for x in p['candidates'].values()) for p in panel),
        unique_joins=sum(sum(bool(x['joins']) for x in p['candidates'].values()) for p in panel)))
    print(json.dumps({k:v for k,v in json.loads((output/'manifest.json').read_text()).items() if k not in ['selected','source_logs']},indent=2))


class Session:
    """Retain errors as observations; every command starts from the import env."""
    def __init__(self,bundle,output):
        self.output=output;output.mkdir(parents=True,exist_ok=False);self.requests=0;self.q=queue.Queue()
        self.stderr=(output/'stderr.log').open('wb');project=bundle/'verifier/DeepSeek-Prover-V1.5/mathlib4'
        env={**os.environ,'ELAN_HOME':str(bundle/'lean/elan'),'PATH':str(bundle/'lean/elan/bin')+os.pathsep+os.environ.get('PATH','')}
        lake=str(bundle/'lean/elan/bin/lake')
        lean_path=subprocess.check_output([lake,'env','printenv','LEAN_PATH'],cwd=project,env=env,text=True,stderr=subprocess.PIPE).strip()
        env['LEAN_PATH']=lean_path
        repl=project/'.lake/packages/REPL/.lake/build/bin/repl'
        lean.write(output/'runtime.json',dict(lean_path=lean_path,repl=str(repl),repl_sha256=sha256(repl),header_sha256=lean.sha(lean.HEADER),lean_toolchain=(project/'lean-toolchain').read_text(),lake_manifest_sha256=sha256(project/'lake-manifest.json')))
        self.p=subprocess.Popen(['/usr/bin/stdbuf','-oL',str(repl)],cwd=project,env=env,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=self.stderr,start_new_session=True)
        def read():
            for line in iter(self.p.stdout.readline,b''):self.q.put(line)
            self.q.put(None)
        self.reader=threading.Thread(target=read,daemon=True);self.reader.start()
    def ask(self,request,timeout=60):
        i=self.requests;self.requests+=1;lean.write(self.output/f'request-{i:04d}.json',request)
        start=time.monotonic();raw=b'';status='complete'
        try:
            self.p.stdin.write((json.dumps(request,ensure_ascii=False)+'\n\n').encode());self.p.stdin.flush()
            while True:
                remaining=timeout-(time.monotonic()-start)
                if remaining<=0:raise queue.Empty
                line=self.q.get(timeout=remaining)
                if line is None:raise RuntimeError('REPL exited')
                raw+=line
                if raw.strip() and not line.strip():break
            result=json.loads(raw);assert isinstance(result,dict)
            return i,result
        except queue.Empty:
            status='timeout';raise TimeoutError('REPL timeout')
        except Exception:
            status='error';raise
        finally:
            (self.output/f'response-{i:04d}.raw').write_bytes(raw)
            lean.write(self.output/f'exchange-{i:04d}.json',dict(seconds=time.monotonic()-start,status=status,request_sha256=sha256(self.output/f'request-{i:04d}.json'),response_sha256=lean.sha(raw)))
    def close(self):
        if self.p.poll() is None:os.killpg(self.p.pid,signal.SIGKILL)
        self.p.wait();self.reader.join(timeout=2);self.p.stdin.close();self.p.stdout.close();self.stderr.close()


def accepted(response,name):
    if response.get('message') or response.get('sorries') or any(m.get('severity')=='error' for m in response.get('messages',[])):return False
    if any(m.get('severity')=='warning' and ("declaration uses 'sorry'" in m.get('data','') or 'failed' in m.get('data','')) for m in response.get('messages',[])):return False
    for m in response.get('messages',[]):
        if m.get('severity')!='info':continue
        data=m.get('data','')
        match=re.fullmatch(re.escape("'"+name+"'")+r' depends on axioms: \[([^]]*)\]',data.strip())
        if match:return set(x.strip() for x in match[1].split(',') if x.strip())<=lean.ALLOWED_AXIOMS
        if data.strip()=="'"+name+"' does not depend on any axioms":return True
    return False


def code(root,body,imports=False):
    return (lean.HEADER if imports else '')+root['statement']+body+'\n#print axioms '+root['name']+'\n'


def execute_root(args):
    bundle,output,root=args;directory=output/f"root-{root['index']:02d}";directory.mkdir(exist_ok=False)
    start=time.monotonic();records=[];error=None;session=Session(bundle,directory/'protocol')
    try:
        _,boot=session.ask(dict(cmd=lean.HEADER),timeout=60)
        assert not boot.get('message') and not any(m.get('severity')=='error' for m in boot.get('messages',[]))
        env=boot['env'];ordered=sorted(root['candidates'],key=lambda k:(not bool(root['candidates'][k]['controls']),k))
        with (directory/'checks.jsonl').open('x',buffering=1) as stream:
            for key in ordered:
                remaining=CONFIG['root_timeout_seconds']-(time.monotonic()-start)
                if remaining<=0:error='root_time_limit';break
                body=root['candidates'][key]['body'];source=code(root,body)
                request,response=session.ask(dict(cmd=source,env=env),timeout=min(60,remaining))
                if 'message' in response or not isinstance(response.get('env'),int):raise RuntimeError('REPL command protocol error: '+json.dumps(response))
                row=dict(key=key,request=request,code_sha256=lean.sha(source),accepted=accepted(response,root['name']))
                records.append(row);stream.write(json.dumps(row)+'\n')
    except Exception as exc:error=type(exc).__name__+': '+str(exc)
    finally:session.close()
    result=dict(index=root['index'],name=root['name'],checked=len(records),expected=len(root['candidates']),complete=error is None and len(records)==len(root['candidates']),error=error,seconds=time.monotonic()-start,accepted=[r['key'] for r in records if r['accepted']])
    lean.write(directory/'complete.json',result);return result


def execute(bundle,output):
    manifest=json.loads((output/'manifest.json').read_text());assert manifest['config']==CONFIG and sha256(output/'panel.json')==manifest['panel_sha256']
    panel=json.loads((output/'panel.json').read_text());assert all(candidates(p['rows'])==p['candidates'] for p in panel)
    start=time.monotonic()
    with ProcessPoolExecutor(max_workers=4,mp_context=multiprocessing.get_context('spawn'),initializer=lean.limit_verifier_worker) as pool:
        results=list(pool.map(execute_root,[(bundle,output,p) for p in panel]))
    jobs={};edges=[]
    for p,r in zip(panel,results):
        for key in r['accepted']:
            source=code(p,p['candidates'][key]['body'],True);digest=lean.sha(source)
            jobs[digest]=dict(id=digest,code=source,lake=str(bundle/'lean/elan/bin/lake'),verifier=str(bundle/'verifier/DeepSeek-Prover-V1.5'))
            edges.append(dict(root=p['index'],key=key,source_sha256=digest))
    lean.write(output/'positive-sources.json',{k:j['code'] for k,j in jobs.items()});lean.write(output/'positive-edges.json',edges)
    if jobs:lean.verify_jobs(list(jobs.values()),output/'positive-verdicts.jsonl',workers=4)
    else:(output/'positive-verdicts.jsonl').write_text('')
    lean.write(output/'execution.json',dict(roots=results,seconds=time.monotonic()-start,model_proposals=0,updates=0))
    print(json.dumps(dict(roots=len(results),resolved=sum(r['complete'] for r in results),positive_sources=len(jobs)),indent=2))


def fixture(bundle,output):
    output.mkdir(parents=True,exist_ok=False);session=Session(bundle,output/'protocol')
    name='join_fixture';root=dict(name=name,statement='theorem join_fixture (a b : Nat) (h : a = b) : b = a := by\n')
    a='  have ha : a = b := h\n  skip\n  exact h\n';b='  have ha : a = b := by rfl\n  skip\n  exact ha.symm\n'
    pa=cuts(a)[0];pb=cuts(b)[0];bodies=dict(first=a,second=b,joined=a[:pa]+b[pb:],prefix=a[:pa],suffix=b[pb:])
    expected=dict(first=False,second=False,joined=True,prefix=False,suffix=False)
    results={}
    try:
        _,boot=session.ask(dict(cmd=lean.HEADER));env=boot['env']
        for label,body in bodies.items():
            _,response=session.ask(dict(cmd=code(root,body),env=env));results[label]=accepted(response,name)
        assert results==expected,(results,expected)
        _,isolated=session.ask(dict(cmd='theorem isolation_fixture (a b : Nat) (h : a = b) : b = a := by\n  exact join_fixture a b h\n#print axioms isolation_fixture\n',env=env))
        assert any(m.get('severity')=='error' and 'join_fixture' in m.get('data','') for m in isolated.get('messages',[])),isolated
        results['prior_declaration_unavailable']=True
        expected['prior_declaration_unavailable']=True
        # Full-command rejection is required even if a failed local declaration
        # leaves a later proof that appears closed through an inserted sorry.
        assert not accepted(dict(messages=[dict(severity='info',data="'join_fixture' depends on axioms: [sorryAx]")]),name)
        assert not accepted(dict(messages=[dict(severity='info',data="'different' depends on axioms: []")]),name)
        assert not accepted(dict(goals=[]),name)
    finally:session.close()
    source=code(root,bodies['joined'],True);verdict=lean.verify_one(dict(id=lean.sha(source),code=source,lake=str(bundle/'lean/elan/bin/lake'),verifier=str(bundle/'verifier/DeepSeek-Prover-V1.5')))
    lean.write(output/'fresh-verdict.json',verdict);assert verdict['accepted']
    lean.write(output/'fixture.json',dict(passed=True,expected=expected,observed=results,source=source,source_sha256=lean.sha(source)))
    print(json.dumps(results))


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('mode',choices=['prepare','execute','fixture']);p.add_argument('bundle',type=Path);p.add_argument('output',type=Path);a=p.parse_args();globals()[a.mode](a.bundle,a.output)
