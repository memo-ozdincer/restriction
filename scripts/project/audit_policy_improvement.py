#!/usr/bin/env python3
"""Reconstruct policy-update provenance and accepted proofs from saved bytes."""
import argparse
from collections import defaultdict
import hashlib
import json
from pathlib import Path
import random


def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def textsha(s): return hashlib.sha256(s.encode()).hexdigest()
def rows(p): return [json.loads(s) for s in p.read_text().splitlines() if s.strip()]


def matrix(root):
    sources=json.loads((root/'unique-sources.json').read_text())
    checks=rows(root/'verdicts.jsonl')
    by={r['id']:r for r in checks}
    assert len(by)==len(checks)==len(sources)
    assert set(by)=={s['id'] for s in sources}
    for s in sources:
        v=by[s['id']]
        assert textsha(s['code'])==s['id']==v['code_sha256']
        if v['accepted']:
            assert v['lean_complete'] and v['axiom_audit_found'] and not v.get('system_errors')
            assert set(v['axioms']) <= {'propext','Classical.choice','Quot.sound'}
    return by,{s['id']:s['code'] for s in sources}


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--run',type=Path,required=True)
    p.add_argument('--panel',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True)
    a=p.parse_args(); run=a.run
    import interface_discovery_pilot as instrument
    status=json.loads((run/'status.json').read_text())
    assert status['state']=='complete'
    assert sha(a.panel/'manifest.json')==status['panel_manifest_sha256']
    manifest=json.loads((a.panel/'manifest.json').read_text())
    for name,h in manifest['files'].items(): assert sha(a.panel/name)==h
    config=json.loads((a.panel/'config.json').read_text())
    train=json.loads((a.panel/'train-tasks.json').read_text())
    evaluation=train+json.loads((a.panel/'evaluation-tasks.json').read_text())
    task={r['id']:r for r in evaluation}
    traces=rows(run/'traces.jsonl'); by={r['id']:r for r in traces}
    assert len(traces)==len(by)==320
    assert set(by)=={f"base/{t['id']}/{i}" for t in train for i in range(16)}
    from transformers import AutoTokenizer
    tokenizer=AutoTokenizer.from_pretrained(str(Path(__file__).resolve().parents[3]/'models/base'),local_files_only=True)
    for r in traces:
        assert r['prompt']==instrument.PREFIX+instrument.HEADER+task[r['target']]['statement']
        assert tokenizer.encode(r['prompt'])==r['prompt_token_ids']
        decoded=tokenizer.decode(r['response_token_ids'],skip_special_tokens=True)
        assert decoded==r['full_decoded_response']
        assert r['text']==(decoded.split('```',1)[0]+'```' if '```' in decoded else decoded)
        assert r['seed']==config['seed']+int(textsha(r['target'])[:6],16)
        assert len(r['response_token_ids'])==len(r['behavior_log_probs'])==len(r['reference_log_probs'])
        diff=[abs(x-y) for x,y in zip(r['behavior_log_probs'],r['reference_log_probs'])]
        assert max(diff)<=config['behavior_reference_max_abs_tolerance']
        assert sum(diff)/len(diff)<=config['behavior_reference_mean_abs_tolerance']
    checked,sources=matrix(run/'matrix')
    edges=json.loads((run/'matrix/edges.json').read_text())
    assert len(edges)==1280
    expected_edges={}
    for r in traces:
        body,error=instrument.completion_code(r['text'])
        for t in train:
            if t['family']!=task[r['target']]['family']: continue
            code=instrument.HEADER+t['statement']+(body or '')+'\n#print axioms target\n'
            key=textsha(code) if not error else None
            expected_edges[r['id'],t['id']]=key
            if key: assert sources[key]==code
    for e in edges: assert expected_edges.pop((e['proposal_id'],e['target']))==e['code_sha256']
    assert not expected_edges
    analysis=json.loads((run/'matrix/analysis.json').read_text())
    grouped=defaultdict(list)
    for e in edges: grouped[e['proposal_id']].append(e)
    for r in analysis['proposals']:
        es=grouped[r['id']]
        good=lambda e: bool(e['code_sha256'] and checked[e['code_sha256']]['accepted'])
        local=next(e for e in es if e['source']==e['target'])
        peers=sum(good(e) for e in es if e!=local)
        assert all(not e['code_sha256'] or not checked[e['code_sha256']].get('system_errors') for e in es)
        assert r['reward_eligible'] and r['local_reward']==float(good(local))
        assert r['cross_reward']==float(good(local))*peers/3
    checkpoints={}
    for arm in config['arms']:
        cert=json.loads((run/arm/'complete.json').read_text())
        metrics=rows(run/arm/'metrics.jsonl')
        assert cert['arm']==arm and cert['optimizer_steps']==len(metrics)==40
        assert cert['candidate_passes']==640 and cert['frozen_reference_bitwise_unchanged']
        assert cert['changed_parameter_tensors']>0 and cert['config']==config
        assert cert['trace_sha256']==sha(run/'traces.jsonl') and cert['reward_sha256']==sha(run/'matrix/analysis.json')
        assert cert['adapter_sha256']==sha(run/arm/'adapter/adapter_model.safetensors')
        order=[]
        for epoch in range(2):
            keys=sorted(t['id'] for t in train); random.Random(config['seed']+epoch).shuffle(keys);order+=keys
        assert [m['source'] for m in metrics]==order
        checkpoints[arm]=cert['adapter_sha256']
    checked,sources=matrix(run/'judgments')
    edges=json.loads((run/'judgments/edges.json').read_text())
    assert len(edges)==3200 and len({e['id'] for e in edges})==3200
    edgeby={e['id']:e for e in edges}
    cells=defaultdict(lambda:[0,0,0])
    for arm in ['base']+config['arms']:
        raw=rows(run/'evaluation'/(arm+'.jsonl'))
        assert len(raw)==640 and {r['id'] for r in raw}=={f'{arm}/{t}/{i}' for t in task for i in range(16)}
        cert=json.loads((run/'evaluation'/(arm+'.complete.json')).read_text())
        assert cert['sha256']==sha(run/'evaluation'/(arm+'.jsonl'))
        assert arm=='base' or cert['reload_max_abs']<=config['adapter_reload_tolerance']
        for r in raw:
            e=edgeby[r['id']]; t=task[r['target']]
            assert r['prompt']==instrument.PREFIX+instrument.HEADER+t['statement']
            assert r['seed']==config['evaluation_seed']+int(textsha(t['id'])[:6],16)
            body,error=instrument.completion_code(r['text'])
            code=instrument.HEADER+t['statement']+(body or '')+'\n#print axioms '+t['theorem']+'\n'
            key=textsha(code) if not error else None
            assert e['code_sha256']==key and e['parse_error']==error
            if key: assert sources[key]==code
            v=checked.get(key)
            cell=cells[arm,t['id']]
            cell[0]+=1;cell[1]+=int(bool(v and v['accepted']))
            cell[2]+=int(not error and (v is None or bool(v.get('system_errors'))))
    final=json.loads((run/'judgments/analysis.json').read_text())
    for r in final['cells']: assert cells[r['model'],r['target']]==[r['proposals'],r['accepted'],r['unresolved']]
    result=dict(passed=True,job_id=status['job_id'],training_proposals=320,training_logical_checks=1280,
        optimizer_steps=160,candidate_training_passes=2560,evaluation_proposals=3200,
        unresolved_evaluation=sum(c[2] for c in cells.values()),adapter_sha256=checkpoints,
        analysis_sha256=sha(run/'judgments/analysis.json'))
    with a.output.open('x') as f: json.dump(result,f,indent=2);f.write('\n')
    print(json.dumps(result))


if __name__=='__main__':main()
