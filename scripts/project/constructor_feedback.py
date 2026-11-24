"""Compare binary, concrete, and symbolic feedback on frozen failed constructors."""
import argparse
import ast
from collections import Counter
import itertools
import json
from pathlib import Path
import re
import time
import sympy as sp
import interface_discovery_pilot as lean
import run_policy_improvement as runtime
import universal_constructor as contracts

ARMS=['failure','counterexample','residual']


def polynomial(text, symbols):
    def visit(node):
        if isinstance(node,ast.Name) and node.id in symbols:return symbols[node.id]
        if isinstance(node,ast.Constant) and type(node.value) is int:return sp.Integer(node.value)
        if isinstance(node,ast.UnaryOp) and isinstance(node.op,(ast.USub,ast.UAdd)):
            return (-1 if isinstance(node.op,ast.USub) else 1)*visit(node.operand)
        if isinstance(node,ast.BinOp):
            a,b=visit(node.left),visit(node.right)
            if isinstance(node.op,ast.Add):return a+b
            if isinstance(node.op,ast.Sub):return a-b
            if isinstance(node.op,ast.Mult):return a*b
            if isinstance(node.op,ast.Pow) and b.is_Integer and 0<=b<=4:return a**b
        raise ValueError('Unsupported polynomial syntax')
    return visit(ast.parse(text.strip().replace('^','**'),mode='eval').body)


def prepare(a):
    a.out.mkdir(parents=True,exist_ok=False)
    old=a.bundle/'runs/universal-constructor-20261123-1399519/experiment'
    rows=lean.rows(old/'samples.jsonl');inputs=[];evidence=[];jobs=[];expected={}
    for ti,task in enumerate(contracts.panel()):
        family=[r for r in rows if r['task_id']==task['id']]
        text,count=Counter(r['text'] for r in family).most_common(1)[0]
        matches=list(re.finditer(r'fun ([a-z ]+) => \(([^(),\n]+),([^(),\n]+)\)',text))
        assert len(matches)==1
        m=matches[0];names=m[1].split();symbols={n:sp.Symbol(n) for n in names}
        f,g=polynomial(m[2],symbols),polynomial(m[3],symbols)
        if ti==0:
            assert names==['d','a','b','x','y'];d,aa,b,x,y=[symbols[n] for n in names]
            lhs=f**2-d*g**2;rhs=(aa**2-d*b**2)*(x**2-d*y**2)
            left=f'({m[2]})^2-d*({m[3]})^2';right='(a^2-d*b^2)*(x^2-d*y^2)'
        else:
            assert names==['x','y','u','v','k','l'];x,y,u,v,k,l=[symbols[n] for n in names]
            lhs=f*(x+k*y)+g*(l*x+(1+k*l)*y);rhs=u*x+v*y
            left=f'({m[2]})*(x+k*y)+({m[3]})*(l*x+(1+k*l)*y)';right='u*x+v*y'
        residual=sp.expand(lhs-rhs);assert residual!=0
        residual_text=str(residual).replace('**','^')
        for values in itertools.product([0,1,-1,2,-2],repeat=len(names)):
            assignment=dict(zip(names,values));subs={symbols[n]:v for n,v in assignment.items()}
            lv,rv=lhs.subs(subs),rhs.subs(subs)
            if lv!=rv:break
        else:raise AssertionError('No counterexample in frozen grid')
        numerical=f"Input {assignment} gives left side {lv}, right side {rv}; they differ."
        prefix=(f'-- Rejected candidate: {m[0]}\n'
            '-- This candidate does not satisfy the following contract.\n')
        for ai,arm in enumerate(ARMS):
            feedback={'failure':'No additional feedback.', 'counterexample':numerical,
                      'residual':f'For arbitrary integer inputs, left side minus right side of the first law is {residual_text}. It must be zero.'}[arm]
            comment=prefix+'-- Verification feedback: '+feedback+'\n-- Supply an implementation and proof satisfying every clause.\n'
            inputs.append(dict(id=task['id']+'/'+arm,task_id=task['id'],arm=arm,
                seed=20261125+1000*ti,prompt=lean.PREFIX+lean.HEADER+comment+task['statement']))
        residual_code=lean.HEADER+f"theorem target ({' '.join(names)} : ℤ) : ({left})-({right}) = {residual_text} := by ring\n#print axioms target\n"
        lets=''.join(f'  let {n} : ℤ := {v}\n' for n,v in assignment.items())
        numeric_code=lean.HEADER+'theorem target : True := by\n'+lets+f'  have h : ({left}) ≠ ({right}) := by norm_num [{", ".join(names)}]\n  trivial\n#print axioms target\n'
        for code in [residual_code,numeric_code]:
            j=contracts.job(a.bundle,code);jobs.append(j);expected[j['id']]=True
        for kind in ['witness','invalid']:
            code=lean.HEADER+task['statement']+task[kind]+'\n#print axioms target\n'
            j=contracts.job(a.bundle,code);jobs.append(j);expected[j['id']]=kind=='witness'
        evidence.append(dict(task_id=task['id'],selected_response=text,count=count,
            proposal_ids=[r['id'] for r in family if r['text']==text],function=m[0],
            lhs=str(lhs),rhs=str(rhs),residual=residual_text,assignment=assignment,
            lhs_value=int(lv),rhs_value=int(rv),feedback_source_sha256=[lean.sha(residual_code),lean.sha(numeric_code)]))
    lean.write(a.out/'inputs.json',inputs);lean.write(a.out/'feedback.json',evidence)
    lean.write(a.out/'fixture-sources.json',{j['id']:j['code'] for j in jobs})
    vs=lean.verify_jobs(jobs,a.out/'fixture-verdicts.jsonl',workers=2)
    assert all(not v.get('system_errors') and v['accepted']==expected[v['id']] for v in vs)
    lean.write(a.out/'ready.json',dict(passed=True,fixtures=len(vs),proposals=96,
        old_samples_sha256=lean.sha((old/'samples.jsonl').read_bytes()),
        inputs_sha256=lean.sha((a.out/'inputs.json').read_bytes()),feedback_sha256=lean.sha((a.out/'feedback.json').read_bytes())))


def run(a):
    ready=json.loads((a.out/'ready.json').read_text());assert ready['passed']
    assert ready['inputs_sha256']==lean.sha((a.out/'inputs.json').read_bytes())
    model,tok=runtime.load_model(a.bundle,a.bundle/'models/c1-final');start=time.time()
    with (a.out/'samples.jsonl').open('x',buffering=1) as stream:
        for inp in json.loads((a.out/'inputs.json').read_text()):
            rows=runtime.sample(model,tok,inp['prompt'],inp['seed'],768,False)
            for row in rows:
                stream.write(json.dumps(dict(**row,task_id=inp['task_id'],arm=inp['arm'],id=inp['id']+'/'+str(row['sample_index'])))+'\n')
            print(json.dumps(dict(completed=inp['id'],seconds=time.time()-start)),flush=True)
    lean.write(a.out/'generation-complete.json',dict(proposals=96,seconds=time.time()-start,samples_sha256=lean.sha((a.out/'samples.jsonl').read_bytes())))


def verify(a):
    tasks={t['id']:t for t in contracts.panel()};rows=lean.rows(a.out/'samples.jsonl');assert len(rows)==96
    jobs={};edges=[]
    for r in rows:
        body,error=lean.completion_code(r['text']);key=None
        if not error:
            # Feedback comments are not needed in the checked source; the contract is byte-identical.
            code=lean.HEADER+tasks[r['task_id']]['statement']+body+'\n#print axioms target\n'
            j=contracts.job(a.bundle,code);key=j['id'];jobs[key]=j
        edges.append(dict(id=r['id'],key=key,parse_error=error))
    lean.write(a.out/'edges.json',edges);lean.write(a.out/'sources.json',{k:j['code'] for k,j in jobs.items()})
    vs=lean.verify_jobs(list(jobs.values()),a.out/'verdicts.jsonl',workers=4);verdicts={v['id']:v for v in vs}
    cells={}
    for e in edges:
        name=e['id'].rsplit('/',1)[0];c=cells.setdefault(name,dict(proposals=0,accepted=0,parse_errors=0,unresolved=0))
        c['proposals']+=1;c['parse_errors']+=bool(e['parse_error'])
        if e['key']:c['accepted']+=bool(verdicts[e['key']]['accepted']);c['unresolved']+=bool(verdicts[e['key']].get('system_errors'))
    strong={arm:all(cells[t+'/'+arm]['accepted']>=4 and cells[t+'/failure']['accepted']<=1 for t in tasks)
        and all(not c['unresolved'] for c in cells.values()) for arm in ['counterexample','residual']}
    lean.write(a.out/'results.json',dict(cells=cells,proposals=96,unique_checks=len(vs),strong_feedback_effect=strong,
        scope='Feedback-conditioned inference on inspected contracts, no training or novel-algorithm claim'))


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('mode',choices=['prepare','run','verify'])
    p.add_argument('bundle',type=Path);p.add_argument('out',type=Path);a=p.parse_args();globals()[a.mode](a)
