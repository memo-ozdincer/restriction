"""Synthesize polynomial argument bindings between verified quadratic contracts."""
import argparse
import json
from pathlib import Path
import re
import sympy as sp
import interface_discovery_pilot as lean
from constructor_certificates import extract,certificate
from constructor_feedback import polynomial
import universal_constructor as contracts


def specification(statement):
    bind=re.search(r'\(∀ ([A-Za-z0-9_ ]+) : ℤ,',statement);assert bind
    names=bind[1].split();assert len(names)==5
    match=re.search(r'\([^\n]+\)\.1 \^ 2 ([+-]) (.*?) \* \([^\n]+\)\.2 \^ 2 =',statement);assert match
    d=sp.Symbol('parameter')
    coefficient=polynomial(match[2],{names[0]:d})*(1 if match[1]=='+' else -1)
    return names,sp.expand(coefficient)


def binding(source_coefficient,target_coefficient):
    d=sp.Symbol('parameter');c0,c1,c2=sp.symbols('c0 c1 c2')
    candidate=c0+c1*d+c2*d*d
    residual=sp.expand(source_coefficient.subs(d,candidate)-target_coefficient)
    solutions=sp.solve(sp.Poly(residual,d).coeffs(),[c0,c1,c2],dict=True)
    assert len(solutions)==1 and all(c in solutions[0] and solutions[0][c].is_Integer for c in [c0,c1,c2])
    coefficients=[int(solutions[0][c]) for c in [c0,c1,c2]]
    answer=sp.expand(candidate.subs(solutions[0]));assert sp.expand(source_coefficient.subs(d,answer)-target_coefficient)==0
    return coefficients,answer


def lean_polynomial(coefficients,name):
    terms=[]
    for power,c in enumerate(coefficients):
        if c:
            terms.append(f'({c})'+('' if power==0 else f'*({name})' if power==1 else f'*({name}^{power})'))
    return '('+' + '.join(terms or ['0'])+')'


def logical_body(names,p):
    d,a,b,x,y=names
    return (f'  rcases source_contract with ⟨f, hNorm, hUnit, hBasis⟩\n'
        f'  refine ⟨fun {" ".join(names)} => f ({p}) {a} {b} {x} {y}, ?_⟩\n'
        '  constructor\n'
        f'  · intro {" ".join(names)}\n'
        f'    convert hNorm ({p}) {a} {b} {x} {y} using 1 <;> ring\n'
        '  constructor\n'
        f'  · intro {d} {a} {b}\n'
        f'    exact hUnit ({p}) {a} {b}\n'
        f'  · intro {d} {a} {b}\n'
        f'    convert hBasis ({p}) {a} {b} using 1 <;> simp <;> ring <;> simp\n')


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('bundle',type=Path);p.add_argument('out',type=Path)
    a=p.parse_args();a.out.mkdir(parents=True,exist_ok=False)
    selected=a.bundle/'runs/hindsight-contracts-mining-20261124/selected.json'
    target_file=a.bundle/'runs/hindsight-training-20261124-1399987/experiment/test.json'
    source=json.loads(selected.read_text())[0];assert source['id']=='quadratic-composition/0'
    body,error=lean.completion_code(source['response']);assert not error
    parsed=extract(source['response'],'quadratic-composition');assert not parsed['error']
    function=parsed['function'];source_names,source_coefficient=specification(source['positive'])
    assert source_coefficient==sp.Symbol('parameter')
    # Only statement fields enter synthesis; discard stored reference witnesses.
    tasks=[dict(id=t['id'],statement=t['statement']) for t in json.loads(target_file.read_text())];assert len(tasks)==8
    source_decl=source['positive'].replace('theorem target','theorem source_contract')+body+'\n'
    jobs={};edges=[];plans=[]
    def add(eid,code,expected):
        j=contracts.job(a.bundle,code);jobs[j['id']]=j;edges.append(dict(id=eid,key=j['id'],expected=expected))
    add('source/valid',lean.HEADER+source_decl+'\n#print axioms source_contract\n',True)
    add('source/invalid',lean.HEADER+source['positive']+'  refine ⟨fun _ _ _ _ _ => (0,0), ?_⟩\n  norm_num\n#print axioms target\n',False)
    for t in tasks:
        names,coefficient=specification(t['statement']);coefficients,p_expr=binding(source_coefficient,coefficient)
        p_lean=lean_polynomial(coefficients,names[0]);d,aa,b,x,y=names
        wrapper=f'fun {" ".join(names)} => ({function}) ({p_lean}) {aa} {b} {x} {y}'
        plans.append(dict(task=t['id'],names=names,target_coefficient=str(coefficient),coefficients=coefficients,
            synthesized_polynomial=str(p_expr),lean_binding=p_lean,original_function=function,executable_wrapper=wrapper))
        prefix=lean.HEADER+source_decl+'\n'+t['statement']
        add(t['id']+'/logical',prefix+logical_body(names,p_lean)+'\n#print axioms source_contract\n#print axioms target\n',True)
        add(t['id']+'/executable',certificate(dict(id='quadratic-composition',statement=t['statement']),wrapper),True)
        identity=sp.expand(source_coefficient-coefficient)==0
        add(t['id']+'/identity',prefix+logical_body(names,names[0])+'\n#print axioms source_contract\n#print axioms target\n',bool(identity))
        add(t['id']+'/wrong_sign',prefix+logical_body(names,f'-({p_lean})')+'\n#print axioms source_contract\n#print axioms target\n',False)
    lean.write(a.out/'inputs.json',dict(source=source,targets=tasks,function=function))
    lean.write(a.out/'provenance.json',dict(selection_path=str(selected),selection_sha256=lean.sha(selected.read_bytes()),
        targets_path=str(target_file),targets_sha256=lean.sha(target_file.read_bytes()),source_id=source['id']))
    lean.write(a.out/'plans.json',plans);lean.write(a.out/'edges.json',edges);lean.write(a.out/'sources.json',{k:j['code'] for k,j in jobs.items()})
    vs=lean.verify_jobs(list(jobs.values()),a.out/'verdicts.jsonl',workers=4);verdicts={v['id']:v for v in vs}
    failures=[e['id'] for e in edges if verdicts[e['key']]['accepted']!=e['expected']]
    unresolved=[v['id'] for v in vs if v.get('system_errors')]
    result=dict(logical_checks=len(edges),unique_checks=len(vs),unexpected_outcomes=failures,unresolved=unresolved,
        criterion_passed=not failures and not unresolved,counts={kind:sum(verdicts[e['key']]['accepted'] for e in edges if e['id'].endswith('/'+kind)) for kind in ['logical','executable','identity','wrong_sign']},
        scope='Compiler construction on inspected targets; no model sampling, parameter updates or changed historical pass rates')
    lean.write(a.out/'results.json',result);print(json.dumps(result,indent=2))


if __name__=='__main__':main()
