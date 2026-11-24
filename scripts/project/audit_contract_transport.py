"""Audit inferred substitutions, opaque-contract proofs and executable provenance."""
import argparse
import json
from pathlib import Path
import sympy as sp
import interface_discovery_pilot as lean
from constructor_certificates import extract,certificate
from compile_contract_transport import specification,binding,lean_polynomial,logical_body


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('bundle',type=Path);p.add_argument('run',type=Path);a=p.parse_args();b=a.bundle;r=a.run
    selection=b/'runs/hindsight-contracts-mining-20261124/selected.json';target_file=b/'runs/hindsight-training-20261124-1399987/experiment/test.json'
    prov=json.loads((r/'provenance.json').read_text());assert prov['selection_sha256']==lean.sha(selection.read_bytes()) and prov['targets_sha256']==lean.sha(target_file.read_bytes())
    source=json.loads(selection.read_text())[0];assert source['id']==prov['source_id']=='quadratic-composition/0'
    original_bank=b/'runs/universal-constructor-20261123-1399519/experiment/samples.jsonl'
    original=[row for row in lean.rows(original_bank) if row['id']==source['id']]
    assert len(original)==1 and original[0]['text']==source['response']
    tasks=[dict(id=t['id'],statement=t['statement']) for t in json.loads(target_file.read_text())]
    parsed=extract(source['response'],'quadratic-composition');assert not parsed['error'];function=parsed['function']
    body,error=lean.completion_code(source['response']);assert not error and body[parsed['start']:parsed['end']]==function
    assert json.loads((r/'inputs.json').read_text())==dict(source=source,targets=tasks,function=function)
    source_decl=source['positive'].replace('theorem target','theorem source_contract')+body+'\n'
    _,sc=specification(source['positive']);parameter=sp.Symbol('parameter');assert sc==parameter
    sources=json.loads((r/'sources.json').read_text());vs=lean.rows(r/'verdicts.jsonl');verdicts={v['id']:v for v in vs}
    assert len(vs)==len(verdicts)==len(sources) and set(sources)==set(verdicts)
    for v in vs:
        assert v['id']==v['code_sha256']==lean.sha(sources[v['id']])
        assert v['accepted']==bool(v['lean_complete'] and v['axiom_audit_found'] and set(v['axioms'])<=lean.ALLOWED_AXIOMS)
    expected_edges=[];used=set();expected_plans=[]
    def check(eid,code,expected):
        key=lean.sha(code);assert sources[key]==code;used.add(key);expected_edges.append(dict(id=eid,key=key,expected=expected))
    check('source/valid',lean.HEADER+source_decl+'\n#print axioms source_contract\n',True)
    check('source/invalid',lean.HEADER+source['positive']+'  refine ⟨fun _ _ _ _ _ => (0,0), ?_⟩\n  norm_num\n#print axioms target\n',False)
    for t in tasks:
        names,tc=specification(t['statement']);coeff,p=binding(sc,tc);p_lean=lean_polynomial(coeff,names[0]);d,aa,bb,x,y=names
        # Independently check the explicit coefficient vector and full identity.
        reconstructed=sum(sp.Integer(c)*parameter**i for i,c in enumerate(coeff))
        assert sp.expand(reconstructed-p)==0 and sp.expand(sc.subs(parameter,reconstructed)-tc)==0
        wrapper=f'fun {" ".join(names)} => ({function}) ({p_lean}) {aa} {bb} {x} {y}'
        expected_plans.append(dict(task=t['id'],names=names,target_coefficient=str(tc),coefficients=coeff,
            synthesized_polynomial=str(p),lean_binding=p_lean,original_function=function,executable_wrapper=wrapper))
        consumer=logical_body(names,p_lean)
        assert function not in consumer and 'unfold' not in consumer and 'source_contract' in consumer
        prefix=lean.HEADER+source_decl+'\n'+t['statement']
        check(t['id']+'/logical',prefix+consumer+'\n#print axioms source_contract\n#print axioms target\n',True)
        check(t['id']+'/executable',certificate(dict(id='quadratic-composition',statement=t['statement']),wrapper),True)
        check(t['id']+'/identity',prefix+logical_body(names,names[0])+'\n#print axioms source_contract\n#print axioms target\n',bool(sp.expand(sc-tc)==0))
        check(t['id']+'/wrong_sign',prefix+logical_body(names,f'-({p_lean})')+'\n#print axioms source_contract\n#print axioms target\n',False)
    assert expected_plans==json.loads((r/'plans.json').read_text())
    edges=json.loads((r/'edges.json').read_text());assert edges==expected_edges and len(edges)==34 and used==set(sources)
    failures=[e['id'] for e in edges if verdicts[e['key']]['accepted']!=e['expected']]
    unresolved=[v['id'] for v in vs if v.get('system_errors')]
    counts={kind:sum(verdicts[e['key']]['accepted'] for e in edges if e['id'].endswith('/'+kind)) for kind in ['logical','executable','identity','wrong_sign']}
    result=json.loads((r/'results.json').read_text());assert result['logical_checks']==34 and result['unique_checks']==len(vs)
    assert result['unexpected_outcomes']==failures and result['unresolved']==unresolved and result['counts']==counts
    assert result['criterion_passed']==(not failures and not unresolved)
    report=dict(passed=True,logical_checks=34,unique_checks=len(vs),counts=counts,unexpected_outcomes=failures,unresolved=unresolved,
        criterion_passed=not failures and not unresolved,source_id=source['id'],original_function_sha256=lean.sha(function),
        original_bank_sha256=lean.sha(original_bank.read_bytes()),
        scope='Compiler-assisted construction from an unchanged sampled program; no model capability/pass-rate claim')
    lean.write(r/'independent-audit.json',report);print(json.dumps(report,indent=2))


if __name__=='__main__':main()
