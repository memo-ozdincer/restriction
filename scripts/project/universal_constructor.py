"""Screen universally verified executable constructors, without supplying implementations."""
import argparse
import json
from pathlib import Path
import time
import interface_discovery_pilot as lean
import run_policy_improvement as runtime


def panel():
    return [dict(id='quadratic-composition', statement='''theorem target :
    ∃ f : ℤ → ℤ → ℤ → ℤ → ℤ → ℤ × ℤ,
      (∀ d a b x y : ℤ,
        (f d a b x y).1 ^ 2 - d * (f d a b x y).2 ^ 2 =
          (a^2-d*b^2)*(x^2-d*y^2)) ∧
      (∀ d a b : ℤ, f d a b 1 0 = (a,b)) ∧
      (∀ d a b : ℤ, f d a b 0 1 = (d*b,a)) := by
''', witness='''  refine ⟨fun d a b x y => (a*x+d*b*y, b*x+a*y), ?_⟩
  dsimp
  constructor
  · intros; ring
  constructor
  · intros; simp
  · intros; simp
''', invalid='''  refine ⟨fun _ _ _ _ _ => (0,0), ?_⟩
  norm_num
'''), dict(id='bezout-transport', statement='''theorem target :
    ∃ f : ℤ → ℤ → ℤ → ℤ → ℤ → ℤ → ℤ × ℤ,
      (∀ x y u v k l : ℤ,
        (f x y u v k l).1 * (x+k*y) +
          (f x y u v k l).2 * (l*x+(1+k*l)*y) = u*x+v*y) ∧
      (∀ x y u v : ℤ, f x y u v 0 0 = (u,v)) := by
''', witness='''  refine ⟨fun x y u v k l => (u*(1+k*l)-v*l, v-u*k), ?_⟩
  dsimp
  constructor
  · intros; ring
  · intros; simp
''', invalid='''  refine ⟨fun _ _ _ _ _ _ => (0,0), ?_⟩
  norm_num
''')]


def job(bundle, code):
    key=lean.sha(code)
    return dict(id=key, code=code, lake=str(bundle/'lean/elan/bin/lake'),
        verifier=str(bundle/'verifier/DeepSeek-Prover-V1.5'))


def prepare(a):
    a.out.mkdir(parents=True,exist_ok=False)
    tasks=panel();lean.write(a.out/'panel.json',tasks)
    lean.write(a.out/'model-inputs.json',[dict(id=t['id'],prompt=lean.PREFIX+lean.HEADER+t['statement']) for t in tasks])
    jobs=[];expected={}
    for task in tasks:
        for kind in ['witness','invalid']:
            code=lean.HEADER+task['statement']+task[kind]+'\n#print axioms target\n'
            j=job(a.bundle,code);jobs.append(j);expected[j['id']]=kind=='witness'
    lean.write(a.out/'fixture-sources.json',{j['id']:j['code'] for j in jobs})
    vs=lean.verify_jobs(jobs,a.out/'fixture-verdicts.jsonl',workers=2)
    assert all(not v.get('system_errors') and v['accepted']==expected[v['id']] for v in vs)
    lean.write(a.out/'ready.json',dict(passed=True,fixtures=len(vs),proposals=128,
        panel_sha256=lean.sha((a.out/'panel.json').read_bytes()),
        inputs_sha256=lean.sha((a.out/'model-inputs.json').read_bytes()),
        seed=20261124,max_tokens=768,groups_per_task=4,samples_per_group=16,
        scope='Inference feasibility for universal-contract reward; no parameter updates'))


def run(a):
    ready=json.loads((a.out/'ready.json').read_text());assert ready['passed']
    assert ready['inputs_sha256']==lean.sha((a.out/'model-inputs.json').read_bytes())
    inputs=json.loads((a.out/'model-inputs.json').read_text())
    model,tok=runtime.load_model(a.bundle,a.bundle/'models/c1-final')
    start=time.time()
    with (a.out/'samples.jsonl').open('x',buffering=1) as stream:
        for ti,task in enumerate(inputs):
            for batch in range(4):
                seed=20261124+ti*1000+batch
                rows=runtime.sample(model,tok,task['prompt'],seed,768,False)
                for row in rows:
                    stream.write(json.dumps(dict(**row,task_id=task['id'],batch=batch,
                        id=f"{task['id']}/{batch*16+row['sample_index']}"))+'\n')
                print(json.dumps(dict(task=task['id'],batch=batch,seconds=time.time()-start)),flush=True)
    lean.write(a.out/'generation-complete.json',dict(proposals=128,seconds=time.time()-start,
        samples_sha256=lean.sha((a.out/'samples.jsonl').read_bytes())))


def verify(a):
    tasks={t['id']:t for t in panel()};rows=lean.rows(a.out/'samples.jsonl')
    assert len(rows)==128 and len({r['id'] for r in rows})==128
    jobs={};edges=[]
    for row in rows:
        body,error=lean.completion_code(row['text']);key=None
        if not error:
            code=lean.HEADER+tasks[row['task_id']]['statement']+body+'\n#print axioms target\n'
            j=job(a.bundle,code);key=j['id'];jobs[key]=j
        edges.append(dict(id=row['id'],task_id=row['task_id'],key=key,parse_error=error))
    lean.write(a.out/'edges.json',edges);lean.write(a.out/'sources.json',{k:j['code'] for k,j in jobs.items()})
    vs=lean.verify_jobs(list(jobs.values()),a.out/'verdicts.jsonl',workers=4)
    verdicts={v['id']:v for v in vs};cells={}
    for tid in tasks:
        es=[e for e in edges if e['task_id']==tid]
        cells[tid]=dict(proposals=len(es),accepted=sum(bool(e['key'] and verdicts[e['key']]['accepted']) for e in es),
            parse_errors=sum(bool(e['parse_error']) for e in es),
            unresolved=sum(bool(e['key'] and verdicts[e['key']].get('system_errors')) for e in es))
    lean.write(a.out/'results.json',dict(cells=cells,unique_checks=len(vs),proposals=len(rows),
        reward_support_gate=all(0<c['accepted']<c['proposals'] and not c['unresolved'] for c in cells.values()),
        scope='Universal contracts are authored; implementations are sampled without demonstrations. No learning result.'))


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('mode',choices=['prepare','run','verify']);p.add_argument('bundle',type=Path);p.add_argument('out',type=Path)
    a=p.parse_args();globals()[a.mode](a)
