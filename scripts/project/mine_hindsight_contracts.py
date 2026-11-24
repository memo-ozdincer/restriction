"""Infer a signed quadratic contract and recheck unchanged failed responses."""
import argparse
import json
from pathlib import Path
import re
import sympy as sp
import interface_discovery_pilot as lean
from constructor_certificates import extract
from constructor_feedback import polynomial
import universal_constructor as contracts


def signed_statement(sign):
    s=contracts.panel()[0]['statement']
    if sign==-1:return s
    assert sign==1
    return s.replace(' - d *',' + d *').replace('a^2-d*b^2','a^2+d*b^2').replace('x^2-d*y^2','x^2+d*y^2').replace('(d*b,a)','(-d*b,a)')


def infer(function):
    names,rest=function[4:].split('=>',1);names=names.split();pair=rest.strip();assert pair[0]=='(' and pair[-1]==')'
    depth=0;commas=[]
    for i,c in enumerate(pair):
        if c=='(':depth+=1
        elif c==')':depth-=1
        elif c==',' and depth==1:commas.append(i)
    assert len(commas)==1
    d,a,b,x,y=sp.symbols('d a b x y');c=sp.Symbol('metricCoefficient')
    mapping=dict(zip(names,[d,a,b,x,y]));i=commas[0]
    f=polynomial(pair[1:i],mapping);g=polynomial(pair[i+1:-1],mapping)
    residual=sp.expand(f*f+c*d*g*g-(a*a+c*d*b*b)*(x*x+c*d*y*y))
    equations=sp.Poly(residual,d,a,b,x,y).coeffs();solutions=sp.solve(equations,[c],dict=True)
    if len(solutions)!=1 or c not in solutions[0] or solutions[0][c] not in [-1,1]:
        return dict(sign=None,solutions=str(solutions),error='no_unique_unit_metric')
    sign=int(solutions[0][c]);laws=[residual.subs(c,sign),f.subs({x:1,y:0})-a,g.subs({x:1,y:0})-b,
        f.subs({x:0,y:1})+sign*d*b,g.subs({x:0,y:1})-a]
    if any(sp.expand(v)!=0 for v in laws):return dict(sign=None,solutions=str(solutions),error='basis_law_failure')
    return dict(sign=sign,solutions=str(solutions),error=None)


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('bundle',type=Path);p.add_argument('out',type=Path)
    a=p.parse_args();a.out.mkdir(parents=True,exist_ok=False)
    src=a.bundle/'runs/universal-constructor-20261123-1399519/experiment/samples.jsonl'
    rows=[r for r in lean.rows(src) if r['task_id']=='quadratic-composition'];assert len(rows)==64
    jobs={};edges=[]
    for r in rows:
        e=dict(id=r['id'],response=r['text'],key=None);parsed=extract(r['text'],'quadratic-composition')
        e['extraction_error']=parsed['error']
        if not parsed['error']:
            e.update(inference=infer(parsed['function']),original_symbolic_valid=parsed['symbolic_valid'],function=parsed['function'])
            sign=e['inference']['sign']
            if sign is not None:
                body,error=lean.completion_code(r['text']);assert not error
                code=lean.HEADER+signed_statement(sign)+body+'\n#print axioms target\n'
                j=contracts.job(a.bundle,code);jobs[j['id']]=j;e['key']=j['id']
        edges.append(e)
    control=lean.HEADER+signed_statement(1)+'  refine ⟨fun _ _ _ _ _ => (0,0), ?_⟩\n  norm_num\n#print axioms target\n'
    cj=contracts.job(a.bundle,control);jobs[cj['id']]=cj
    lean.write(a.out/'edges.json',edges);lean.write(a.out/'sources.json',{k:j['code'] for k,j in jobs.items()})
    lean.write(a.out/'provenance.json',dict(input_path=str(src),input_sha256=lean.sha(src.read_bytes()),proposals=64,invalid_control=cj['id']))
    vs=lean.verify_jobs(list(jobs.values()),a.out/'verdicts.jsonl',workers=4);verdicts={v['id']:v for v in vs}
    unresolved=[v['id'] for v in vs if v.get('system_errors')]
    assert not verdicts[cj['id']]['accepted']
    chosen=[];seen=set()
    for e in edges:
        if e['key'] and verdicts[e['key']]['accepted'] and e['inference']['sign']==1 and not e['original_symbolic_valid']:
            if e['response'] not in seen and len(chosen)<8:
                chosen.append(dict(id=e['id'],response=e['response'],positive=signed_statement(1),negative=signed_statement(-1),source_key=e['key']))
                seen.add(e['response'])
    lean.write(a.out/'selected.json',chosen)
    result=dict(proposals=64,unique_checks=len(vs),hindsight_accepted=sum(bool(e['key'] and verdicts[e['key']]['accepted']) for e in edges),
        selected=len(chosen),unresolved=unresolved,ready=len(chosen)==8 and not unresolved,
        scope='Unchanged failed responses under inferred signed contracts; original-target acceptance stays zero')
    lean.write(a.out/'results.json',result);print(json.dumps(result,indent=2))


if __name__=='__main__':main()
