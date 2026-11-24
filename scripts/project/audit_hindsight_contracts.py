"""Audit hindsight selection, exact training/evaluation tokens and comparative outcomes."""
import argparse
import json
import math
from pathlib import Path
import interface_discovery_pilot as lean
from constructor_certificates import extract
from mine_hindsight_contracts import infer,signed_statement
from train_hindsight_contracts import panel,ARMS


def audit_mining(b):
    r=b/'runs/hindsight-contracts-mining-20261124'
    prov=json.loads((r/'provenance.json').read_text());src=b/'runs/universal-constructor-20261123-1399519/experiment/samples.jsonl'
    assert lean.sha(src.read_bytes())==prov['input_sha256']
    rows=[x for x in lean.rows(src) if x['task_id']=='quadratic-composition'];assert len(rows)==64
    edges=json.loads((r/'edges.json').read_text());assert [e['id'] for e in edges]==[x['id'] for x in rows]
    sources=json.loads((r/'sources.json').read_text());vs=lean.rows(r/'verdicts.jsonl');verdicts={v['id']:v for v in vs}
    assert len(vs)==len(verdicts)==len(sources) and set(verdicts)==set(sources)
    for v in vs:
        assert not v.get('system_errors') and v['code_sha256']==v['id']==lean.sha(sources[v['id']])
        assert v['accepted']==bool(v['lean_complete'] and v['axiom_audit_found'] and set(v['axioms'])<=lean.ALLOWED_AXIOMS)
    chosen=[];seen=set();used={prov['invalid_control']};accepted=0
    for x,e in zip(rows,edges):
        assert e['response']==x['text'];p=extract(x['text'],'quadratic-composition');assert e['extraction_error']==p['error']
        if p['error']:assert e['key'] is None;continue
        assert e['function']==p['function'] and e['original_symbolic_valid']==p['symbolic_valid']
        inferred=infer(p['function']);assert e['inference']==inferred
        if inferred['sign'] is None:assert e['key'] is None;continue
        body,error=lean.completion_code(x['text']);assert not error
        code=lean.HEADER+signed_statement(inferred['sign'])+body+'\n#print axioms target\n'
        key=lean.sha(code);assert key==e['key'] and sources[key]==code;used.add(key)
        if verdicts[key]['accepted']:
            accepted+=1
            if inferred['sign']==1 and not p['symbolic_valid'] and x['text'] not in seen and len(chosen)<8:
                chosen.append(dict(id=x['id'],response=x['text'],positive=signed_statement(1),negative=signed_statement(-1),source_key=key));seen.add(x['text'])
    assert used==set(sources) and not verdicts[prov['invalid_control']]['accepted']
    assert chosen==json.loads((r/'selected.json').read_text()) and len(chosen)==8
    result=json.loads((r/'results.json').read_text());assert result['hindsight_accepted']==accepted and result['ready'] and result['unresolved']==[]
    report=dict(passed=True,original_proposals=64,hindsight_accepted=accepted,selected=len(chosen),unique_checks=len(vs),input_sha256=prov['input_sha256'])
    lean.write(r/'independent-audit.json',report)
    return chosen,report


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('bundle',type=Path);p.add_argument('--run',type=Path);a=p.parse_args();b=a.bundle
    train,mining=audit_mining(b)
    if a.run is None:print(json.dumps(mining,indent=2));return
    r=a.run
    from transformers import AutoTokenizer
    tok=AutoTokenizer.from_pretrained(str(b/'models/c1-final'),local_files_only=True)
    assert train==json.loads((r/'train.json').read_text());tasks=panel();assert tasks==json.loads((r/'test.json').read_text())
    ready=json.loads((r/'ready.json').read_text());assert ready['passed']
    assert ready['train_sha256']==lean.sha((r/'train.json').read_bytes()) and ready['test_sha256']==lean.sha((r/'test.json').read_bytes())
    fs=json.loads((r/'fixture-sources.json').read_text());fv=lean.rows(r/'fixture-verdicts.jsonl');fe=json.loads((r/'fixture-edges.json').read_text())
    expected={};expected_edges=[]
    for example in train:
        body,error=lean.completion_code(example['response']);assert not error
        for context in ['positive','negative']:
            code=lean.HEADER+example[context]+body+'\n#print axioms target\n';key=lean.sha(code)
            assert fs[key]==code;expected[key]=context=='positive';expected_edges.append(dict(id=example['id']+'/'+context,key=key))
    for t in tasks:
        for kind in ['witness','invalid']:
            code=t['witness_source'] if kind=='witness' else lean.HEADER+t['statement']+'  refine ⟨fun _ _ _ _ _ => (0,0), ?_⟩\n  norm_num\n#print axioms target\n'
            key=lean.sha(code);assert fs[key]==code;expected[key]=kind=='witness';expected_edges.append(dict(id=t['id']+'/'+kind,key=key))
    assert fe==expected_edges and len(fe)==32 and len(fv)==len(fs)==len(expected)
    assert {v['id'] for v in fv}==set(expected)
    assert all(not v.get('system_errors') and v['accepted']==expected[v['id']] and v['id']==v['code_sha256'] for v in fv)
    training={}
    for arm in ['replay','contrast']:
        d=r/arm;records=json.loads((d/'tokens.json').read_text());refs=json.loads((d/'reference-probes.json').read_text());final=json.loads((d/'reload-probes.json').read_text())
        assert len(records)==len(refs)==len(final)==16 and final!=refs
        for i,example in enumerate(train):
            for j,context in enumerate(['positive','negative']):
                rec=records[2*i+j]
                assert rec==dict(id=example['id']+'/'+context,prompt_token_ids=tok.encode(lean.PREFIX+lean.HEADER+example[context]),response_token_ids=tok.encode(example['response'],add_special_tokens=False))
                assert len(refs[2*i+j])==len(final[2*i+j])==len(rec['response_token_ids'])
                assert all(math.isfinite(x) for x in refs[2*i+j]+final[2*i+j])
        metrics=lean.rows(d/'metrics.jsonl');assert len(metrics)==32
        for i,m in enumerate(metrics):
            assert m['step']==i+1 and m['id']==train[i%8]['id']
            assert m['positive_tokens']==m['negative_tokens']==len(records[2*(i%8)]['response_token_ids'])
            assert all(math.isfinite(m[k]) for k in ['positive_nll','negative_nll','preference','positive_anchor','negative_anchor','grad_norm'])
            assert 0<=m['negative_recompute_delta']<=1e-5
        done=json.loads((d/'training-complete.json').read_text());assert done['steps']==32 and done['reference_unchanged'] and done['initial_adapter_equal_reference'] and done['serialized_weights_exact']
        assert done['adapter_sha256']==lean.sha((d/'adapter/adapter_model.safetensors').read_bytes()) and done['train_sha256']==ready['train_sha256']
        training[arm]=done
    assert (r/'replay/tokens.json').read_bytes()==(r/'contrast/tokens.json').read_bytes()
    assert (r/'replay/reference-probes.json').read_bytes()==(r/'contrast/reference-probes.json').read_bytes()
    edges=json.loads((r/'edges.json').read_text());sources=json.loads((r/'sources.json').read_text());vs=lean.rows(r/'verdicts.jsonl');verdicts={v['id']:v for v in vs}
    assert len(vs)==len(verdicts)==len(sources) and set(sources)==set(verdicts)
    by_edge={(e['arm'],e['task'],e['index']):e for e in edges};assert len(edges)==len(by_edge)==384
    for v in vs:
        assert v['id']==v['code_sha256']==lean.sha(sources[v['id']])
        assert v['accepted']==bool(v['lean_complete'] and v['axiom_audit_found'] and set(v['axioms'])<=lean.ALLOWED_AXIOMS)
    cells={};used=set()
    for arm in ARMS:
        for ti,t in enumerate(tasks):
            batch=json.loads((r/arm/(t['id'].replace('/','_')+'.json')).read_text());prompt=lean.PREFIX+lean.HEADER+t['statement']
            assert batch['prompt']==prompt and len(batch['rows'])==16
            c=dict(proposals=16,accepted=0,unresolved=0,parse_errors=0);cells.setdefault(arm,{})[t['id']]=c
            for i,s in enumerate(batch['rows']):
                assert s['sample_index']==i and s['seed']==20261126+ti and s['prompt_token_ids']==tok.encode(prompt)
                assert len(s['response_token_ids'])==s['generated_tokens']<=768 and tok.decode(s['response_token_ids'],skip_special_tokens=True)==s['full_decoded_response']
                body,error=lean.completion_code(s['text']);key=None
                if not error:
                    code=lean.HEADER+t['statement']+body+'\n#print axioms target\n';key=lean.sha(code);assert sources[key]==code;used.add(key)
                    c['accepted']+=bool(verdicts[key]['accepted']);c['unresolved']+=bool(verdicts[key].get('system_errors'))
                c['parse_errors']+=bool(error)
                assert by_edge[arm,t['id'],i]==dict(arm=arm,task=t['id'],index=i,key=key,parse_error=error)
    assert used==set(sources)
    strong=all(cells['contrast'][v+'/-1']['accepted']>=8 and cells['base'][v+'/-1']['accepted']<=1 and cells['replay'][v+'/-1']['accepted']<=1 for v in ['renamed','scaled','nonlinear'])
    retention=all(cells['contrast'][v+'/1']['accepted']>=cells['replay'][v+'/1']['accepted']-2 for v in ['original','renamed','scaled','nonlinear'])
    resolved=all(c['unresolved']==0 for arm in cells.values() for c in arm.values());result=json.loads((r/'results.json').read_text())
    assert result==dict(cells=cells,proposals=384,unique_checks=len(vs),target_criterion=strong,retention_criterion=retention,registered_outcome=strong and retention and resolved,all_resolved=resolved)
    report=dict(passed=True,mining=mining,training=training,**result);lean.write(r/'independent-audit.json',report);print(json.dumps(report,indent=2))


if __name__=='__main__':main()
