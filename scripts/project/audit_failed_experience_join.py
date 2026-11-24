"""Reconstruct frozen joins, protocol judgments and the failure-only acquisition gate."""
import argparse
import json
from pathlib import Path
from failed_experience_join import CONFIG, candidates, code, accepted, cuts, sha256, lean


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('run',type=Path);a=p.parse_args();r=a.run
    m=json.loads((r/'manifest.json').read_text());panel=json.loads((r/'panel.json').read_text());execution=json.loads((r/'execution.json').read_text())
    assert sha256(r/'panel.json')==m['panel_sha256'] and m['config']==CONFIG
    assert len(panel)==32 and [x['name'] for x in panel]==m['selected']
    positive_sources=json.loads((r/'positive-sources.json').read_text());positive_edges=json.loads((r/'positive-edges.json').read_text());fresh=lean.rows(r/'positive-verdicts.jsonl')
    assert len(fresh)==len({x['id'] for x in fresh})==len(positive_sources)
    fv={x['id']:x for x in fresh}
    for k,source in positive_sources.items():
        v=fv[k];assert k==lean.sha(source)==v['code_sha256']
        assert v['accepted']==bool(v['lean_complete'] and v['axiom_audit_found'] and set(v['axioms'])<=lean.ALLOWED_AXIOMS)
    positives={(e['root'],e['key']):e['source_sha256'] for e in positive_edges};assert len(positives)==len(positive_edges)
    roots=[];accepted_examples=[];total_checks=0;total_requests=0;confirmed=set();discrepancies=[]
    for root,saved in zip(panel,execution['roots']):
        assert len(root['rows'])==32 and all(x['record']['correct'] is False and x['record']['theorem_name']==root['name'] and x['record']['theorem_statement']==root['statement'] for x in root['rows'])
        assert candidates(root['rows'])==root['candidates']
        for i,row in enumerate(root['rows']):
            assert row['sample_index']==i and lean.completion_code(row['record']['proof'])==(row['body'],None) and row['cuts']==cuts(row['body'])
        d=r/f"root-{root['index']:02d}";protocol=d/'protocol';done=json.loads((d/'complete.json').read_text());assert done==saved
        checks=lean.rows(d/'checks.jsonl') if (d/'checks.jsonl').exists() else []
        assert len(checks)==done['checked'] and len(root['candidates'])==done['expected']
        assert done['complete']==(done['error'] is None and len(checks)==len(root['candidates']))
        order=sorted(root['candidates'],key=lambda k:(not bool(root['candidates'][k]['controls']),k));assert [x['key'] for x in checks]==order[:len(checks)]
        requests=sorted(protocol.glob('request-*.json'));total_requests+=len(requests)
        assert json.loads((protocol/'request-0000.json').read_text())==dict(cmd=lean.HEADER)
        if checks:
            boot=json.loads((protocol/'response-0000.raw').read_text());env=boot['env']
        for check in checks:
            k=check['key'];item=root['candidates'][k];assert lean.sha(item['body'])==k
            req=protocol/f"request-{check['request']:04d}.json";raw=protocol/f"response-{check['request']:04d}.raw";exchange=json.loads((protocol/f"exchange-{check['request']:04d}.json").read_text())
            assert json.loads(req.read_text())==dict(cmd=code(root,item['body']),env=env)
            assert exchange['status']=='complete' and exchange['request_sha256']==sha256(req) and exchange['response_sha256']==sha256(raw)
            response=json.loads(raw.read_text());assert check['accepted']==accepted(response,root['name']) and check['code_sha256']==lean.sha(code(root,item['body']))
            if check['accepted']:
                full=code(root,item['body'],True);digest=lean.sha(full)
                assert positives[root['index'],k]==digest and positive_sources[digest]==full;confirmed.add((root['index'],k))
                if not fv[digest]['accepted']:discrepancies.append(dict(root=root['name'],key=k,unresolved=bool(fv[digest].get('system_errors'))))
                else:accepted_examples.append(dict(root=root['name'],index=root['index'],key=k,source_sha256=digest,controls=item['controls'],donors=item['joins']))
        assert done['accepted']==[x['key'] for x in checks if x['accepted']]
        control_hits=[x for x in checks if x['accepted'] and root['candidates'][x['key']]['controls']]
        join_hits=[x for x in checks if x['accepted'] and root['candidates'][x['key']]['joins']]
        original_hits=[x for x in control_hits if any(c['kind']=='original' for c in root['candidates'][x['key']]['controls'])]
        positive_confirmed=all(fv[positives[root['index'],x['key']]]['accepted'] for x in checks if x['accepted'])
        qualified=done['complete'] and not control_hits and positive_confirmed
        roots.append(dict(index=root['index'],name=root['name'],complete=done['complete'],error=done['error'],checked=len(checks),expected=done['expected'],
            control_accepted=len(control_hits),original_accepted=len(original_hits),joined_accepted=len(join_hits),
            qualified_joined_bodies=len(join_hits) if qualified else 0,qualifying_root=qualified and bool(join_hits),seconds=done['seconds']))
        total_checks+=len(checks)
    assert confirmed==set(positives)
    root_count=sum(x['qualifying_root'] for x in roots);body_count=sum(x['qualified_joined_bodies'] for x in roots)
    result=dict(passed=True,roots=roots,roots_complete=sum(x['complete'] for x in roots),roots_total=32,original_proposals=1024,
        selected_join_bodies=m['unique_joins'],selected_control_bodies=m['unique_controls'],executed_command_checks=total_checks,
        physical_repl_requests=total_requests,fresh_positive_checks=len(fresh),positive_discrepancies=discrepancies,
        qualifying_roots=root_count,qualifying_joined_bodies=body_count,acquisition_gate=root_count>=4 and body_count>=8 and not discrepancies,
        model_proposals=0,updates=0,seconds=execution['seconds'])
    lean.write(r/'accepted-examples.json',accepted_examples);lean.write(r/'independent-audit.json',result)
    print(json.dumps({k:v for k,v in result.items() if k!='roots'},indent=2))


if __name__=='__main__':main()
