"""Audit fixed-certificate closure of unchanged sampled polynomial constructors."""
import argparse
import json
from pathlib import Path
import re
import sympy as sp
import interface_discovery_pilot as lean
from constructor_feedback import polynomial
import universal_constructor as contracts

BANKS={'original':'universal-constructor-20261123-1399519',
       'feedback':'constructor-feedback-20261124-1399674'}
NAMES={'quadratic-composition':['d','a','b','x','y'],
       'bezout-transport':['x','y','u','v','k','l']}


def extract(text,task):
    body,error=lean.completion_code(text)
    if error:return dict(error='original_parse:'+error)
    pattern=r"^\s*(?:use\s+|(?:refine'?|exact)\s*⟨\s*)(fun\s+([A-Za-z_][A-Za-z_0-9]*(?:\s+[A-Za-z_][A-Za-z_0-9]*)*)\s*=>\s*\()"
    m=re.search(pattern,body)
    if not m:return dict(error='not_direct_polynomial_lambda')
    # Later proof lambdas are permitted; the witness itself must be the first
    # direct tuple lambda. Its component syntax cannot contain nested lambdas.
    names=m[2].split()
    if len(names)!=len(NAMES[task]) or len(set(n for n in names if n!='_'))!=sum(n!='_' for n in names):
        return dict(error='unsupported_binders')
    start=m.start(1);opening=m.end()-1;depth=0;comma=None;end=None
    for i in range(opening,len(body)):
        c=body[i]
        if c=='(':depth+=1
        elif c==')':
            depth-=1
            if depth==0:end=i+1;break
        elif c==',' and depth==1:
            if comma is not None:return dict(error='not_pair')
            comma=i
    if end is None or comma is None:return dict(error='unclosed_pair')
    if body[end:].lstrip()[:1] not in [',','⟩','\n',''] and not body[end:].startswith('\n'):
        return dict(error='unsupported_lambda_suffix')
    canonical={n:sp.Symbol(n) for n in NAMES[task]}
    mapping={src:canonical[dst] for src,dst in zip(names,NAMES[task]) if src!='_'}
    try:
        f=polynomial(body[opening+1:comma],mapping);g=polynomial(body[comma+1:end-1],mapping)
    except (ValueError,SyntaxError,TypeError):return dict(error='unsupported_polynomial')
    if task=='quadratic-composition':
        d,a,b,x,y=[canonical[n] for n in NAMES[task]]
        residuals=[f*f-d*g*g-(a*a-d*b*b)*(x*x-d*y*y),
            f.subs({x:1,y:0})-a,g.subs({x:1,y:0})-b,
            f.subs({x:0,y:1})-d*b,g.subs({x:0,y:1})-a]
    else:
        x,y,u,v,k,l=[canonical[n] for n in NAMES[task]]
        residuals=[f*(x+k*y)+g*(l*x+(1+k*l)*y)-u*x-v*y,
            f.subs({k:0,l:0})-u,g.subs({k:0,l:0})-v]
    residuals=[sp.expand(e) for e in residuals]
    return dict(error=None,start=start,end=end,function=body[start:end],
        residuals=[str(e) for e in residuals],symbolic_valid=all(e==0 for e in residuals))


def certificate(task,function):
    proof=f'  refine ⟨{function}, ?_⟩\n  dsimp\n  constructor\n  · intros; ring\n'
    if task['id']=='quadratic-composition':proof+='  constructor\n'
    proof+='  · intros; simp <;> ring\n'
    if task['id']=='quadratic-composition':proof+='  · intros; simp <;> ring\n'
    return lean.HEADER+task['statement']+proof+'\n#print axioms target\n'


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('bundle',type=Path);p.add_argument('out',type=Path)
    a=p.parse_args();a.out.mkdir(parents=True,exist_ok=False)
    tasks={t['id']:t for t in contracts.panel()};edges=[];jobs={};provenance={};fixtures=[]
    for bank,name in BANKS.items():
        path=a.bundle/'runs'/name/'experiment/samples.jsonl';rs=lean.rows(path)
        assert len(rs)=={'original':128,'feedback':96}[bank]
        provenance[bank]=dict(path=str(path),sha256=lean.sha(path.read_bytes()),proposals=len(rs))
        for row in rs:
            e=dict(id=bank+'/'+row['id'],task_id=row['task_id'],**extract(row['text'],row['task_id']))
            e['key']=None
            if not e['error']:
                code=certificate(tasks[e['task_id']],e['function']);j=contracts.job(a.bundle,code);jobs[j['id']]=j;e['key']=j['id']
            edges.append(e)
    for t in tasks.values():
        for kind in ['witness','invalid']:
            body=t[kind]+'```';e=extract(body,t['id']);assert not e['error']
            code=certificate(t,e['function']);j=contracts.job(a.bundle,code);jobs[j['id']]=j
            fixtures.append(dict(task=t['id'],kind=kind,key=j['id'],expected=kind=='witness'))
    lean.write(a.out/'provenance.json',provenance);lean.write(a.out/'edges.json',edges);lean.write(a.out/'fixtures.json',fixtures)
    lean.write(a.out/'sources.json',{k:j['code'] for k,j in jobs.items()})
    vs=lean.verify_jobs(list(jobs.values()),a.out/'verdicts.jsonl',workers=4);verdicts={v['id']:v for v in vs}
    assert all(not verdicts[f['key']].get('system_errors') and verdicts[f['key']]['accepted']==f['expected'] for f in fixtures)
    cells={};disagreements=[]
    for e in edges:
        group=e['id'].rsplit('/',1)[0];c=cells.setdefault(group,dict(proposals=0,unclassified=0,compiled_valid=0,unresolved=0))
        c['proposals']+=1
        if e['error']:c['unclassified']+=1;continue
        v=verdicts[e['key']];c['compiled_valid']+=bool(v['accepted']);c['unresolved']+=bool(v.get('system_errors'))
        if not v.get('system_errors') and v['accepted']!=e['symbolic_valid']:disagreements.append(e['id'])
    lean.write(a.out/'results.json',dict(proposals=len(edges),unique_checks=len(vs),fixtures=len(fixtures),cells=cells,
        semantic_certificate_disagreements=disagreements,
        accepted_ids=[e['id'] for e in edges if e['key'] and verdicts[e['key']]['accepted']],
        scope='Unchanged extracted functions plus a fixed external certificate, not original whole-proof acceptance'))


if __name__=='__main__':main()
