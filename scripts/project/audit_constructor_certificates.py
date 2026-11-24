"""Reconstruct certificate replay counts and exact unchanged function provenance."""
import argparse
from collections import Counter
import json
from pathlib import Path
import interface_discovery_pilot as lean
from constructor_certificates import BANKS,extract,certificate
from universal_constructor import panel


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('bundle',type=Path);p.add_argument('run',type=Path)
    a=p.parse_args();r=a.run;tasks={t['id']:t for t in panel()}
    edges=json.loads((r/'edges.json').read_text());by_edge={e['id']:e for e in edges};assert len(edges)==len(by_edge)==224
    prov=json.loads((r/'provenance.json').read_text());sources=json.loads((r/'sources.json').read_text())
    vs=lean.rows(r/'verdicts.jsonl');verdicts={v['id']:v for v in vs}
    assert len(vs)==len(verdicts)==len(sources) and set(verdicts)==set(sources)
    for v in vs:
        assert v['id']==v['code_sha256']==lean.sha(sources[v['id']])
        assert v['accepted']==bool(v['lean_complete'] and v['axiom_audit_found'] and set(v['axioms'])<=lean.ALLOWED_AXIOMS)
    ids=set();used=set();cells={};families={};unclassified=Counter();disagreements=[]
    for bank,path in BANKS.items():
        file=a.bundle/'runs'/path/'experiment/samples.jsonl';rs=lean.rows(file)
        assert lean.sha(file.read_bytes())==prov[bank]['sha256'] and len(rs)==prov[bank]['proposals']
        for row in rs:
            eid=bank+'/'+row['id'];assert eid not in ids;ids.add(eid)
            e=by_edge[eid];parsed=extract(row['text'],row['task_id']);key=None
            if not parsed['error']:
                body,_=lean.completion_code(row['text']);assert body[parsed['start']:parsed['end']]==parsed['function']
                # A newline must not hide a continuation of the tuple expression.
                assert body[parsed['end']:].lstrip()[:1] not in ['+','-','*','/','^','.']
                code=certificate(tasks[row['task_id']],parsed['function']);key=lean.sha(code)
                assert sources[key]==code;used.add(key)
            assert e==dict(id=eid,task_id=row['task_id'],**parsed,key=key)
            group=eid.rsplit('/',1)[0]
            c=cells.setdefault(group,dict(proposals=0,unclassified=0,compiled_valid=0,unresolved=0))
            f=families.setdefault(row['task_id'],dict(proposals=0,supported=0,compiled_valid=0,unresolved=0))
            c['proposals']+=1;f['proposals']+=1
            if e['error']:
                c['unclassified']+=1;unclassified[e['error']]+=1;continue
            f['supported']+=1;v=verdicts[key]
            for item in [c,f]:
                item['compiled_valid']+=bool(v['accepted']);item['unresolved']+=bool(v.get('system_errors'))
            if not v.get('system_errors') and v['accepted']!=e['symbolic_valid']:disagreements.append(eid)
    assert ids==set(by_edge)
    fixtures=json.loads((r/'fixtures.json').read_text());assert len(fixtures)==4
    for f in fixtures:
        e=extract(tasks[f['task']][f['kind']]+'```',f['task']);assert not e['error']
        code=certificate(tasks[f['task']],e['function']);key=lean.sha(code);assert key==f['key']
        assert sources[key]==code and f['expected']==(f['kind']=='witness');used.add(key)
        assert verdicts[key]['accepted']==f['expected'] and not verdicts[key].get('system_errors')
    assert used==set(sources)
    result=json.loads((r/'results.json').read_text())
    accepted=[e['id'] for e in edges if e['key'] and verdicts[e['key']]['accepted']]
    assert result['cells']==cells and result['accepted_ids']==accepted and result['semantic_certificate_disagreements']==disagreements
    assert result['proposals']==224 and result['unique_checks']==len(vs) and result['fixtures']==4
    report=dict(passed=True,proposals=224,unique_checks=len(vs),fixtures=4,cells=cells,families=families,
        unclassified_reasons=dict(unclassified),accepted_ids=accepted,semantic_certificate_disagreements=disagreements,
        both_family_support=all(f['compiled_valid']>0 and f['unresolved']==0 for f in families.values()) and not disagreements)
    lean.write(r/'independent-audit.json',report);print(json.dumps(report,indent=2))


if __name__=='__main__':main()
