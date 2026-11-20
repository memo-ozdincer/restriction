#!/usr/bin/env python3
"""Link repaired model prerequisites into controlled consumer generation."""
import argparse
from collections import defaultdict
import hashlib
import json
from pathlib import Path
import re
import time
import interface_discovery_pilot as lean

SEED=20261122
CONDITIONS=['bare','linked','irrelevant']


def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def rename(s,old,new):return re.sub(r'\b'+re.escape(old)+r'\b',new,s)
def split_statement(s):
    i=s.index('theorem ')
    return s[:i],s[i:]


def prepare(a):
    a.output.mkdir(parents=True,exist_ok=False)
    repair=a.bundle/'runs/causal-state-repair-20261119'
    audit=json.loads((repair/'independent-audit.json').read_text())
    assert audit['passed'] and audit['analysis_sha256']==sha(repair/'analysis.json')
    summary=json.loads((repair/'analysis.json').read_text())
    props={x['id']:x for x in json.loads((repair/'proposals.json').read_text())}
    panel=a.bundle/'runs/policy-improvement-panel-20261119-fp32'
    assert sha(panel/'manifest.json')=='dd2250492190e9d12f2d45e7026b731a967c6a1994795be2c279adafa76e95b0'
    tasks={x['id']:x for x in json.loads((panel/'evaluation-tasks.json').read_text())}
    records=[]
    for i in range(4):
        source=f'pt_{i:02d}'
        successes=sorted([x for x in summary['rows'] if x['target']==source and x['accepted']],
            key=lambda x:int(x['id'].rsplit('/',1)[1]))
        selected=props[successes[0]['id']]
        definition,theorem=split_statement(selected['statement'])
        for offset in [4,8]:
            target=f'pt_{i+offset:02d}';task=tasks[target]
            td,tt=split_statement(task['statement'])
            oldop=f'op_{i:02d}';newop=f'op_{i+offset:02d}'
            assert rename(definition,oldop,newop)==td
            transferred=rename(theorem,oldop,newop).replace('theorem '+source+' ','theorem linked_contract ',1)
            body=rename(selected['repaired_body'],oldop,newop)
            signature=transferred.removesuffix(' := by\n')
            equality=signature.split(' :\n',1)[1].strip()
            lhs=equality.split(' = ',1)[0]
            irrelevant=lhs+' = '+lhs
            common='theorem linked_contract (n : Nat) (a b c d : Int) :\n    '
            for condition in CONDITIONS:
                if condition=='bare':
                    library='';prefix='';comment='';contract=None
                else:
                    contract=equality if condition=='linked' else irrelevant
                    library=(transferred+body if condition=='linked' else common+contract+' := by\n  rfl\n')+'\n'
                    prefix='  have hbridge : '+contract+' := linked_contract n a b c d\n'
                    comment='-- External checked declaration (proof body hidden):\n-- linked_contract (n : Nat) (a b c d : Int) : '+contract+'\n'
                records.append(dict(id=target+'/'+condition,target=target,family=task['family'],condition=condition,
                    producer_id=selected['id'],producer_original_body_sha256=lean.sha(selected['original_body']),
                    producer_repaired_body_sha256=lean.sha(selected['repaired_body']),
                    definition=td,target_theorem=tt,library=library,contract=contract,prefix=prefix,
                    prompt=lean.PREFIX+lean.HEADER+td+comment+tt+prefix,
                    verifier_prefix=lean.HEADER+td+library+tt+prefix))
    lean.write(a.output/'records.json',records)
    names=['repaired_library.py','interface_discovery_pilot.py','run_policy_improvement.py',
           'policy_improvement_data.py','policy_update_math.py','cross_context_credit.py']
    lean.write(a.output/'manifest.json',dict(seed=SEED,conditions=CONDITIONS,tasks=8,samples_per_cell=32,
        proposal_cap=768,max_response_tokens=256,max_prompt_tokens=1536,parameter_updates=0,
        source_sha256={n:sha(Path(__file__).parent/n) for n in names},records_sha256=sha(a.output/'records.json'),
        repair_analysis_sha256=sha(repair/'analysis.json'),repair_proposals_sha256=sha(repair/'proposals.json'),
        source_panel_manifest_sha256=sha(panel/'manifest.json'),
        claim_scope='Inspected-root inference composition; no model learning or held-out claim'))


def authenticate(panel):
    m=json.loads((panel/'manifest.json').read_text())
    assert m['seed']==SEED and m['conditions']==CONDITIONS
    assert sha(panel/'records.json')==m['records_sha256']
    for n,h in m['source_sha256'].items():assert sha(Path(__file__).parent/n)==h
    return json.loads((panel/'records.json').read_text())


def job(a,identity,code):return dict(id=identity,code=code,
    verifier=str(a.bundle/'verifier/DeepSeek-Prover-V1.5'),lake=str(a.bundle/'lean/elan/bin/lake'))


def validate(a):
    records=authenticate(a.panel);jobs=[]
    for r in records:
        if r['library']:
            jobs.append(job(a,r['id']+'/library',lean.HEADER+r['definition']+r['library']+'\n#print axioms linked_contract\n'))
        jobs.append(job(a,r['id']+'/empty',r['verifier_prefix']+'\n#print axioms '+r['target']+'\n'))
    jobs += [job(a,'negative/sorry',lean.HEADER+'theorem target : False := by sorry\n#print axioms target\n'),
             job(a,'negative/axiom',lean.HEADER+'axiom bad : False\ntheorem target : False := bad\n#print axioms target\n')]
    checked=lean.verify_jobs(jobs,a.output,workers=8)
    passed=len(checked)==42 and all(r['accepted']==r['id'].endswith('/library') and not r.get('system_errors') for r in checked)
    lean.write(a.output.with_suffix('.summary.json'),dict(passed=passed,checks=len(checked)))
    if not passed:raise RuntimeError('Library/prefix validation failed')


def generate(a):
    records=authenticate(a.panel)
    checks=lean.rows(a.validation)
    expected={r['id']+'/empty' for r in records}|{r['id']+'/library' for r in records if r['library']}|{'negative/sorry','negative/axiom'}
    assert len(checks)==42 and {r['id'] for r in checks}==expected
    assert all(r['accepted']==r['id'].endswith('/library') and not r.get('system_errors') for r in checks)
    import run_policy_improvement as runtime
    model,tokenizer=runtime.load_model(a.bundle)
    start=time.time()
    with a.output.open('x') as f:
        for r in records:
            for batch in range(2):
                seed=SEED+int(lean.sha(r['target'])[:6],16)+batch*8192
                for row in runtime.sample(model,tokenizer,r['prompt'],seed,256,False):
                    index=batch*16+row['sample_index']
                    runtime.append(f,{**row,'id':r['id']+'/'+str(index),'request_id':r['id'],
                        'sample_index':index,'condition':r['condition'],'target':r['target'],'prompt':r['prompt']})
            print(json.dumps(dict(generated=r['id'],samples=32,seconds=time.time()-start)),flush=True)
    lean.write(a.output.with_suffix('.complete.json'),dict(proposals=768,sha256=sha(a.output),seconds=time.time()-start))


def verify(a):
    records={r['id']:r for r in authenticate(a.panel)};raw=lean.rows(a.input)
    expected={key+'/'+str(i) for key in records for i in range(32)}
    assert len(raw)==768 and {r['id'] for r in raw}==expected
    unique={};edges=[]
    for row in raw:
        r=records[row['request_id']];assert row['prompt']==r['prompt'] and row['condition']==r['condition'] and row['target']==r['target']
        body,error=lean.completion_code(row['text'])
        source=r['verifier_prefix']+(body or '')+'\n#print axioms '+r['target']+'\n'
        key=lean.sha(source) if not error else None
        if key:unique.setdefault(key,job(a,key,source))
        edges.append(dict(id=row['id'],target=r['target'],family=r['family'],condition=r['condition'],code_sha256=key,parse_error=error))
    a.output.mkdir(exist_ok=False)
    lean.write(a.output/'edges.json',edges);lean.write(a.output/'sources.json',list(unique.values()))
    checks={r['id']:r for r in lean.verify_jobs(list(unique.values()),a.output/'verdicts.jsonl',workers=8)}
    raw_by={r['id']:r for r in raw};ablations=[];extra={}
    for e in edges:
        if e['condition']!='linked' or not e['code_sha256'] or not checks[e['code_sha256']]['accepted']:continue
        body,error=lean.completion_code(raw_by[e['id']]['text']);assert error is None
        for condition in ['bare','irrelevant']:
            control=records[e['target']+'/'+condition]
            source=control['verifier_prefix']+body+'\n#print axioms '+e['target']+'\n'
            key=lean.sha(source)
            if key not in checks:extra.setdefault(key,job(a,key,source))
            ablations.append(dict(proposal_id=e['id'],target=e['target'],condition=condition,code_sha256=key))
    lean.write(a.output/'ablation-edges.json',ablations);lean.write(a.output/'ablation-sources.json',list(extra.values()))
    extra_checks={r['id']:r for r in lean.verify_jobs(list(extra.values()),a.output/'ablation-verdicts.jsonl',workers=8)}
    all_checks=checks|extra_checks
    dependency=defaultdict(list)
    for e in ablations:dependency[e['proposal_id']].append(all_checks[e['code_sha256']])
    dependent=[key for key,vs in dependency.items() if len(vs)==2 and all(not v['accepted'] and not v.get('system_errors') for v in vs)]
    dependent_roots=sorted({raw_by[key]['target'] for key in dependent})
    cells=defaultdict(lambda:dict(proposals=0,accepted=0,unresolved=0))
    for e in edges:
        v=checks.get(e['code_sha256']);c=cells[e['target'],e['family'],e['condition']]
        c['proposals']+=1;c['accepted']+=int(bool(v and v['accepted']))
        c['unresolved']+=int(not e['parse_error'] and (not v or bool(v.get('system_errors'))))
    rows=[dict(target=k[0],family=k[1],condition=k[2],**v) for k,v in sorted(cells.items())]
    by={(r['target'],r['condition']):r for r in rows};qualifying=[]
    for r in rows:
        if r['condition']=='linked' and r['accepted']>=8 and r['target'] in dependent_roots and all(by[r['target'],c]['accepted']<=1 for c in ['bare','irrelevant']):qualifying.append(r)
    unresolved=sum(r['unresolved'] for r in rows)
    lean.write(a.output/'analysis.json',dict(cells=rows,qualifying_roots=[r['target'] for r in qualifying],
        qualifying_schemas=sorted({r['family'] for r in qualifying}),unresolved=unresolved,
        exciting_result=len({r['family'] for r in qualifying})==2 and not any(v.get('system_errors') for v in all_checks.values()),
        dependent_proposals=dependent,dependent_roots=dependent_roots,ablation_logical_checks=len(ablations),
        ablation_physical_checks=len(extra_checks),all_unique_system_errors=sum(bool(v.get('system_errors')) for v in all_checks.values()),
        physical_checks=len(checks),proposals=len(raw),parameter_updates=0))


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('mode',choices=['prepare','validate','generate','verify'])
    for name in ['bundle','panel','output','input','validation']:p.add_argument('--'+name,type=Path)
    a=p.parse_args();globals()[a.mode](a)


if __name__=='__main__':main()
