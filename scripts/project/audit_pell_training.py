"""Reconcile the paired updates, evaluation token traces, sources, and Lean outcomes."""
import argparse
import hashlib
import json
from pathlib import Path
from train_pell_construction import lean, panel


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('run',type=Path)
    p.add_argument('output',type=Path)
    args=p.parse_args()
    r=args.run
    train,test=panel()
    assert train==json.loads((r/'train.json').read_text()) and test==json.loads((r/'test.json').read_text())
    checks={v['id']:v for v in lean.rows(r/'panel-checks.jsonl')}
    for t in train+test:
        for name,body in [('literal',t['literal']),('expression',t['expression']),('invalid','  exact ⟨1,0, by norm_num⟩')]:
            if body is not None:
                v=checks[t['id']+'/'+name]
                assert v['code_sha256']==lean.sha(lean.HEADER+t['statement']+body+'\n#print axioms target')
                assert v['accepted']==(name!='invalid') and not v['system_errors']
    training={}
    for arm in ('literal','expression'):
        tokens=json.loads((r/arm/'tokens.json').read_text())
        assert [x['id'] for x in tokens]==[t['id'] for t in train]
        steps=lean.rows(r/arm/'metrics.jsonl')
        assert len(steps)==32
        for i,step in enumerate(steps):
            item=tokens[i%8]
            assert step['step']==i+1 and step['id']==item['id'] and step['tokens']==len(item['response_token_ids'])
        weights=r/arm/'adapter/adapter_model.safetensors'
        training[arm]=dict(steps=len(steps),supervised_tokens=sum(s['tokens'] for s in steps),
            first_epoch_mean_nll=sum(s['nll'] for s in steps[:8])/8,
            last_epoch_mean_nll=sum(s['nll'] for s in steps[-8:])/8,adapter_sha256=hashlib.sha256(weights.read_bytes()).hexdigest())
    assert training['literal']['adapter_sha256']!=training['expression']['adapter_sha256']
    sources=json.loads((r/'sources.json').read_text()); vs=lean.rows(r/'verdicts.jsonl')
    assert len(vs)==len(sources) and {v['id'] for v in vs}==set(sources)
    verified={}
    for v in vs:
        assert v['id']==v['code_sha256']==lean.sha(sources[v['id']])
        assert not v['accepted'] or (v['lean_complete'] and v['axiom_audit_found'] and set(v['axioms'])<=lean.ALLOWED_AXIOMS)
        verified[v['id']]=v
    expected_edges=[]
    totals={}
    for arm in ('base','literal','expression'):
        totals[arm]={}
        for t in test:
            batch=json.loads((r/arm/(t['id']+'.json')).read_text())
            source=lean.HEADER+t['statement']
            assert batch['prompt']==lean.PREFIX+source and len(batch['rows'])==16
            counts=dict(accepted=0,unresolved=0,parse_errors=0)
            for i,row in enumerate(batch['rows']):
                assert row['sample_index']==i and row['seed']==20261203+int(lean.sha(t['id'].rsplit('-',1)[0])[:6],16)
                body,error=lean.completion_code(row['text'])
                key=None if error else lean.sha(source+body+'\n#print axioms target')
                v={} if error else verified[key]
                counts['accepted']+=int(bool(v.get('accepted')))
                counts['unresolved']+=int(bool(v.get('system_errors')))
                counts['parse_errors']+=int(bool(error))
                expected_edges.append(dict(arm=arm,task=t['id'],index=i,key=key,error=error))
            totals[arm][t['id']]=counts
    assert expected_edges==json.loads((r/'edges.json').read_text())
    assert totals==json.loads((r/'results.json').read_text())
    lean.write(args.output,dict(training=training,cells=totals,proposals=len(expected_edges),physical_checks=len(vs),
        fixture_checks=len(checks),unresolved=sum(c['unresolved'] for cells in totals.values() for c in cells.values())))


if __name__=='__main__':
    main()
