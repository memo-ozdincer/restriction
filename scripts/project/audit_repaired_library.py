#!/usr/bin/env python3
"""Independent provenance, closed-proof and dependency audit for library reuse."""
import argparse
from collections import defaultdict
import hashlib
import json
from pathlib import Path
import re


def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def digest(s):return hashlib.sha256(s.encode()).hexdigest()
def rows(p):return [json.loads(s) for s in p.read_text().splitlines() if s.strip()]


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for name in ['bundle','run','panel','output']:p.add_argument('--'+name,type=Path,required=True)
    a=p.parse_args();r=a.run;b=a.bundle
    import interface_discovery_pilot as lean
    status=json.loads((r/'status.json').read_text());assert status['state']=='complete'
    manifest=json.loads((a.panel/'manifest.json').read_text())
    assert sha(a.panel/'manifest.json')==status['panel_sha256']
    assert sha(a.panel/'records.json')==manifest['records_sha256']
    repair=b/'runs/causal-state-repair-20261119'
    assert sha(repair/'analysis.json')==manifest['repair_analysis_sha256']
    assert sha(repair/'proposals.json')==manifest['repair_proposals_sha256']
    props={x['id']:x for x in json.loads((repair/'proposals.json').read_text())}
    prior=json.loads((repair/'analysis.json').read_text())
    original_panel=b/'runs/policy-improvement-panel-20261119-fp32'
    assert sha(original_panel/'manifest.json')==manifest['source_panel_manifest_sha256']
    tasks={x['id']:x for x in json.loads((original_panel/'evaluation-tasks.json').read_text())}
    records={x['id']:x for x in json.loads((a.panel/'records.json').read_text())}
    assert len(records)==24
    for x in records.values():
        producer=props[x['producer_id']];target_number=int(x['target'].split('_')[1]);variant=target_number%4
        candidates=sorted([v['id'] for v in prior['rows'] if v['target']==f'pt_{variant:02d}' and v['accepted']],key=lambda z:int(z.rsplit('/',1)[1]))
        assert x['producer_id']==candidates[0]
        assert x['producer_original_body_sha256']==digest(producer['original_body'])
        assert x['producer_repaired_body_sha256']==digest(producer['repaired_body'])
        rename=lambda s:re.sub(r'\bop_'+f'{variant:02d}'+r'\b','op_'+f'{target_number:02d}',s)
        pd,pt=producer['statement'].split('theorem ',1)
        assert rename(pd)==x['definition']
        assert x['definition']+x['target_theorem']==tasks[x['target']]['statement']
        if x['condition']=='linked':
            expected='theorem '+rename(pt).replace(f'pt_{variant:02d} ','linked_contract ',1)+rename(producer['repaired_body'])+'\n'
            assert x['library']==expected
        assert rename(producer['repaired_body']) not in x['prompt']
        assert ' generalizing ' not in x['prompt']
        assert x['verifier_prefix']==lean.HEADER+x['definition']+x['library']+x['target_theorem']+x['prefix']
    raw=rows(r/'candidates.jsonl');rawby={x['id']:x for x in raw}
    assert len(rawby)==len(raw)==768 and set(rawby)=={key+'/'+str(i) for key in records for i in range(32)}
    assert json.loads((r/'candidates.complete.json').read_text())['sha256']==sha(r/'candidates.jsonl')
    sources={};checked={}
    for phase in ['', 'ablation-']:
        ss=json.loads((r/'matrix'/(phase+'sources.json')).read_text());vs=rows(r/'matrix'/(phase+'verdicts.jsonl'))
        assert len(ss)==len(vs)==len({v['id'] for v in vs})==len({s['id'] for s in ss})
        assert {s['id'] for s in ss}=={v['id'] for v in vs}
        for s in ss:assert digest(s['code'])==s['id'];sources[s['id']]=s['code']
        for v in vs:
            assert v['code_sha256']==v['id']
            if v['accepted']:
                assert v['lean_complete'] and v['axiom_audit_found'] and not v.get('system_errors')
                assert set(v['axioms'])<={'propext','Classical.choice','Quot.sound'}
            checked[v['id']]=v
    edges=json.loads((r/'matrix/edges.json').read_text());assert len(edges)==768 and {e['id'] for e in edges}==set(rawby)
    cells=defaultdict(lambda:[0,0,0]);expected_ablations={}
    for e in edges:
        rawrow=rawby[e['id']];x=records[rawrow['request_id']]
        assert rawrow['prompt']==x['prompt'] and rawrow['target']==x['target'] and rawrow['condition']==x['condition']
        assert rawrow['seed']==20261122+int(digest(x['target'])[:6],16)+(rawrow['sample_index']//16)*8192
        body,error=lean.completion_code(rawrow['text'])
        code=x['verifier_prefix']+(body or '')+'\n#print axioms '+x['target']+'\n';key=digest(code) if not error else None
        assert key==e['code_sha256'] and error==e['parse_error']
        if key:assert sources[key]==code
        v=checked.get(key);good=bool(v and v['accepted'])
        cell=cells[x['target'],x['condition']];cell[0]+=1;cell[1]+=int(good);cell[2]+=int(not error and (not v or bool(v.get('system_errors'))))
        if x['condition']=='linked' and good:
            for c in ['bare','irrelevant']:
                control=records[x['target']+'/'+c]
                code=control['verifier_prefix']+body+'\n#print axioms '+x['target']+'\n'
                expected_ablations[e['id'],c]=(digest(code),code)
    ablations=json.loads((r/'matrix/ablation-edges.json').read_text());assert len(ablations)==len(expected_ablations)
    dependency=defaultdict(list)
    for e in ablations:
        key,code=expected_ablations.pop((e['proposal_id'],e['condition']))
        assert key==e['code_sha256'] and sources[key]==code
        dependency[e['proposal_id']].append(checked[key])
    assert not expected_ablations
    dependent=sorted(key for key,vs in dependency.items() if len(vs)==2 and all(not v['accepted'] and not v.get('system_errors') for v in vs))
    result=json.loads((r/'matrix/analysis.json').read_text());assert len(result['cells'])==24
    assert {(x['target'],x['condition']) for x in result['cells']}==set(cells)
    for x in result['cells']:assert cells[x['target'],x['condition']]==[x['proposals'],x['accepted'],x['unresolved']]
    assert sorted(result['dependent_proposals'])==dependent
    dependent_roots={rawby[key]['target'] for key in dependent}
    qualifying=[t for t in {x['target'] for x in records.values()} if cells[t,'linked'][1]>=8
        and cells[t,'bare'][1]<=1 and cells[t,'irrelevant'][1]<=1 and t in dependent_roots]
    schemas={tasks[t]['family'] for t in qualifying};errors=sum(bool(v.get('system_errors')) for v in checked.values())
    assert sorted(qualifying)==sorted(result['qualifying_roots']) and sorted(schemas)==result['qualifying_schemas']
    assert result['exciting_result']==(len(schemas)==2 and errors==0)
    receipt=dict(passed=True,proposals=768,linked_successes=sum(v[1] for k,v in cells.items() if k[1]=='linked'),
        dependent_proposals=len(dependent),qualifying_roots=sorted(qualifying),qualifying_schemas=sorted(schemas),
        all_physical_checks=len(checked),system_errors=errors,exciting_result=result['exciting_result'],analysis_sha256=sha(r/'matrix/analysis.json'))
    with a.output.open('x') as f:json.dump(receipt,f,indent=2);f.write('\n')
    print(json.dumps(receipt))


if __name__=='__main__':main()
