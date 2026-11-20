#!/usr/bin/env python3
"""Independent exact-token, training-budget and complete-root evaluation audit."""
import argparse
from collections import defaultdict
import hashlib
import json
from pathlib import Path


def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def digest(s):return hashlib.sha256(s.encode()).hexdigest()
def rows(p):return [json.loads(s) for s in p.read_text().splitlines() if s.strip()]


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for n in ['bundle','run','panel','tokens','output']:p.add_argument('--'+n,type=Path,required=True)
    a=p.parse_args();r=a.run
    import interface_discovery_pilot as lean
    import compiler_credit_data as data
    from transformers import AutoTokenizer
    data.authenticate(a.panel)
    status=json.loads((r/'status.json').read_text());assert status['state']=='complete'
    assert status['panel_sha256']==sha(a.panel/'manifest.json') and status['tokens_sha256']==sha(a.tokens/'tokens.json')
    assert json.loads((a.panel/'validation-summary.json').read_text())==dict(passed=True,checks=65,errors=[])
    ss={x['id']:x for x in json.loads((a.panel/'validation-sources.json').read_text())}
    vv=rows(a.panel/'validation.jsonl');assert len(vv)==len(ss)==65
    for v in vv:
        assert v['code_sha256']==digest(ss[v['id']]['code'])
        assert v['accepted']==v['id'].endswith('/positive') and not v.get('system_errors')
    examples=json.loads((a.panel/'train.json').read_text());tokens=json.loads((a.tokens/'tokens.json').read_text())
    tokenizer=AutoTokenizer.from_pretrained(str(a.bundle/'models/base'),local_files_only=True)
    assert len(examples)==len(tokens)==8
    for x,t in zip(examples,tokens):
        assert x['id']==t['id'] and t['prompt']==lean.PREFIX+lean.HEADER+x['statement'] and t['response']==x['body']+'\n```'
        enc=tokenizer(t['response'],add_special_tokens=False,return_offsets_mapping=True)
        assert t['response_token_ids']==enc['input_ids'] and t['prompt_token_ids']==tokenizer(t['prompt'])['input_ids']
        assert t['offsets']==[list(v) for v in enc['offset_mapping']] and t['spans']==x['spans']
        mask=[int(any(end>s['start'] and start<s['end'] for s in x['spans'])) for start,end in enc['offset_mapping']]
        shift=len(mask)//2;rotated=mask[-shift:]+mask[:-shift]
        assert mask==t['mapped'] and rotated==t['rotated'] and sum(mask)==sum(rotated)>0
        assert t['mask_overlap']==sum(m*n for m,n in zip(mask,rotated))
    refs=[];training={}
    for arm in ['full','mapped','rotated']:
        cert=json.loads((r/arm/'complete.json').read_text());metrics=rows(r/arm/'metrics.jsonl')
        assert cert['arm']==arm and cert['optimizer_steps']==80 and cert['changed_tensors']>0 and cert['frozen_reference_bitwise_unchanged']
        assert cert['config']==data.CONFIG and cert['tokens_sha256']==sha(a.tokens/'tokens.json')
        assert cert['adapter_sha256']==sha(r/arm/'adapter/adapter_model.safetensors')
        assert len(metrics)==80 and [x['step'] for x in metrics]==list(range(1,81))
        for i,x in enumerate(metrics):
            t=tokens[i%8];assert x['example']==t['id'] and x['arm']==arm and x['epoch']==i//8
            assert x['response_tokens']==len(t['response_token_ids'])
            assert x['supervised_tokens']==(len(t['response_token_ids']) if arm=='full' else sum(t[arm]))
        refs.append(json.loads((r/arm/'reference-probes.json').read_text()))
        ec=json.loads((r/'evaluation'/(arm+'.complete.json')).read_text())
        assert ec['reload_max_abs'] is not None and ec['reload_max_abs']<=1e-4
        training[arm]=dict(optimizer_steps=80,adapter_sha256=cert['adapter_sha256'],reload_max_abs=ec['reload_max_abs'])
    assert refs[0]==refs[1]==refs[2]
    tasks={x['id']:x for x in json.loads((a.panel/'evaluation.json').read_text())};assert len(tasks)==44
    raw={}
    for arm in ['base','full','mapped','rotated']:
        path=r/'evaluation'/(arm+'.jsonl');xs=rows(path)
        assert len(xs)==704 and {x['id'] for x in xs}=={f'{arm}/{tid}/{i}' for tid in tasks for i in range(16)}
        assert sha(path)==json.loads(path.with_suffix('.complete.json').read_text())['sha256']
        for x in xs:
            assert x['model']==arm and x['prompt']==lean.PREFIX+lean.HEADER+tasks[x['target']]['statement']
            assert x['seed']==20261124+int(digest(x['target'])[:6],16)
            raw[x['id']]=x
    sources={x['id']:x['code'] for x in json.loads((r/'matrix/sources.json').read_text())}
    verdicts=rows(r/'matrix/verdicts.jsonl');checked={x['id']:x for x in verdicts}
    assert len(verdicts)==len(checked)==len(sources) and set(checked)==set(sources)
    for k,v in checked.items():
        assert k==digest(sources[k])==v['code_sha256']
        if v['accepted']:assert v['lean_complete'] and v['axiom_audit_found'] and set(v['axioms'])<={'propext','Classical.choice','Quot.sound'}
    edges=json.loads((r/'matrix/edges.json').read_text());assert len(edges)==2816 and {x['id'] for x in edges}==set(raw)
    counts=defaultdict(lambda:[0,0,0])
    for e in edges:
        x=raw[e['id']];t=tasks[x['target']];body,error=lean.completion_code(x['text'])
        code=lean.HEADER+t['statement']+(body or '')+'\n#print axioms '+t['theorem']+'\n';key=digest(code) if not error else None
        assert key==e['code_sha256'] and error==e['parse_error']
        assert e['model']==x['model'] and e['target']==t['id'] and e['split']==t['split'] and e['transition']==t['transition'] and e['family']==t['family']
        if key:assert sources[key]==code
        v=checked.get(key);c=counts[x['model'],t['id']];c[0]+=1;c[1]+=int(bool(v and v['accepted']))
        c[2]+=int(not error and (not v or bool(v.get('system_errors'))))
    analysis=json.loads((r/'matrix/analysis.json').read_text())
    assert len(analysis['cells'])==176 and {(c['model'],c['target']) for c in analysis['cells']}==set(counts)
    for c in analysis['cells']:assert counts[c['model'],c['target']]==[c['proposals'],c['accepted'],c['unresolved']]
    score={arm:{split:sum(counts[arm,k][1] for k,t in tasks.items() if t['split']==split)/(384 if split=='composition' else 320)
        for split in ['composition','retention']} for arm in ['base','full','mapped','rotated']}
    assert score==analysis['scores']
    qualifying=[k for k,t in tasks.items() if t['split']=='composition' and t['family'] in ['nonzero','witness']
        and counts['mapped',k][1]>=4 and all(counts[arm,k][1]<=1 for arm in ['base','full','rotated'])]
    assert set(qualifying)==set(analysis['qualifying_roots'])
    errors=sum(c[2] for c in counts.values());margin=score['mapped']['composition']-max(score[x]['composition'] for x in ['full','rotated'])
    retention=score['mapped']['retention']-score['base']['retention']
    outcome=not errors and margin>=.10 and retention>=-.05 and len({tasks[k]['transition'] for k in qualifying})>=2
    assert analysis['registered_outcome']==outcome and analysis['unresolved']==errors and analysis['margin']==margin and analysis['retention_change']==retention
    result=dict(passed=True,proposals=2816,physical_checks=len(checked),unresolved=errors,registered_outcome=outcome,
        scores=score,qualifying_roots=qualifying,training=training,analysis_sha256=sha(r/'matrix/analysis.json'))
    with a.output.open('x') as f:json.dump(result,f,indent=2);f.write('\n')
    print(json.dumps(result))


if __name__=='__main__':main()
