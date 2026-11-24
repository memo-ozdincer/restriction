"""Separate initiating a contract proof from completing its construction."""
import argparse
import json
from pathlib import Path
import math
import interface_discovery_pilot as lean
import run_policy_improvement as runtime
from policy_update_math import response_log_probs
from run_compiler_credit import probe
import universal_constructor as contracts

HEADS={'trained':'  have source_contract :','renamed':'  have auxiliary :'}
ARMS=['base','transport']
ADAPTER_SHA='6922fd9bfbe4e6ff7e6a143d6a73cfacfae6611805bff97c8bc8e77b6ca3cbc2'


def prior(bundle):return bundle/'runs/contract-closure-20261124-1400174/experiment'


def tasks(bundle):
    all_tasks=json.loads((prior(bundle)/'test.json').read_text())
    return [dict(id=t['id'],statement=t['statement'],seed=20261127+i,diagnostic=t['variant']=='original') for i,t in enumerate(all_tasks) if i>=4]


def prepare(a):
    a.out.mkdir(parents=True,exist_ok=False);p=prior(a.bundle);audit=json.loads((p/'independent-audit.json').read_text());assert audit['passed']
    assert lean.sha((p/'transport/adapter/adapter_model.safetensors').read_bytes())==ADAPTER_SHA
    ts=tasks(a.bundle);assert len(ts)==6
    lean.write(a.out/'tasks.json',ts);lean.write(a.out/'config.json',dict(heads=HEADS,arms=ARMS,total_response_budget=768,samples_per_cell=16,temperature=1,top_p=1,top_k=0,training=False))
    natural=[];old_edges=json.loads((p/'edges.json').read_text());old_vs={v['id']:v for v in lean.rows(p/'verdicts.jsonl')}
    for arm in ARMS:
        for t in ts:
            rows=json.loads((p/arm/(t['id'].replace('/','_')+'.json')).read_text())['rows'];es=[e for e in old_edges if e['arm']==arm and e['task']==t['id']];assert len(es)==len(rows)==16
            for e,s in zip(es,rows):
                assert e['index']==s['sample_index'];v=old_vs[e['key']] if e['key'] else None
                natural.append(dict(arm=arm,task=t['id'],index=e['index'],text=s['text'],key=e['key'],parse_error=e['parse_error'],accepted=bool(v and v['accepted']),unresolved=bool(v and v.get('system_errors'))))
    lean.write(a.out/'natural.json',natural)
    lean.write(a.out/'provenance.json',dict(adapter_sha256=ADAPTER_SHA,prior_test_sha256=lean.sha((p/'test.json').read_bytes()),
        prior_audit_sha256=lean.sha((p/'independent-audit.json').read_bytes()),prior_train_sha256=lean.sha((p/'train.json').read_bytes()),
        tasks_sha256=lean.sha((a.out/'tasks.json').read_bytes()),natural_sha256=lean.sha((a.out/'natural.json').read_bytes())))


def run(a):
    import torch
    ts=json.loads((a.out/'tasks.json').read_text());assert ts==tasks(a.bundle);dest=a.out/a.arm;dest.mkdir(exist_ok=False)
    model,tok=runtime.load_model(a.bundle,a.bundle/'models/c1-final');p=prior(a.bundle)
    if a.arm=='transport':
        assert lean.sha((p/'transport/adapter/adapter_model.safetensors').read_bytes())==ADAPTER_SHA
        model=runtime.add_adapter(model,p/'transport/adapter')
        records=json.loads((p/'transport/tokens.json').read_text());assert probe(model,records)==json.loads((p/'transport/reload-probes.json').read_text())
    lean.write(dest/'checkpoint-check.json',dict(arm=a.arm,adapter_sha256=ADAPTER_SHA if a.arm=='transport' else None,exact_reload_probe_match=a.arm=='transport'))
    probes=[]
    for t in ts:
        natural=lean.PREFIX+lean.HEADER+t['statement'];base_ids=tok.encode(natural)
        for name,head in HEADS.items():
            prompt=natural+head;ids=tok.encode(prompt);assert ids[:len(base_ids)]==base_ids
            supplied=ids[len(base_ids):];assert len(supplied)>0
            with torch.no_grad():logs=response_log_probs(model,base_ids,supplied,'cuda').tolist()
            probes.append(dict(task=t['id'],head=name,supplied_token_ids=supplied,log_probs=logs,sequence_log_probability=sum(logs)))
            rows=runtime.sample(model,tok,prompt,t['seed'],768-len(supplied),False)
            lean.write(dest/(t['id'].replace('/','_')+'_'+name+'.json'),dict(task=t['id'],head=name,prompt=prompt,supplied_token_ids=supplied,rows=rows))
    lean.write(dest/'prefix-probes.json',probes);lean.write(dest/'complete.json',dict(arm=a.arm,cells=len(ts)*len(HEADS)))


def scores(edges,vs,natural):
    cells={}
    for e in edges:
        c=cells.setdefault(e['arm'],{}).setdefault(e['task'],{}).setdefault(e['head'],dict(proposals=0,accepted=0,parse_errors=0,unresolved=0));c['proposals']+=1;c['parse_errors']+=bool(e['parse_error'])
        if e['key']:c['accepted']+=bool(vs[e['key']]['accepted']);c['unresolved']+=bool(vs[e['key']].get('system_errors'))
    for e in natural:
        c=cells[e['arm']][e['task']].setdefault('natural',dict(proposals=0,accepted=0,parse_errors=0,unresolved=0));c['proposals']+=1;c['accepted']+=e['accepted'];c['parse_errors']+=bool(e['parse_error']);c['unresolved']+=e['unresolved']
    resolved=all(c['unresolved']==0 for aa in cells.values() for task in aa.values() for c in task.values())
    wins=[k for k in cells['base'] if not k.startswith('original/') and cells['transport'][k]['natural']['accepted']<=1 and all(cells['transport'][k][h]['accepted']>=8 and cells['base'][k][h]['accepted']<=1 for h in HEADS)]
    return dict(cells=cells,winning_tasks=wins,conditional_gate=len(wins)>=3 and resolved,all_resolved=resolved)


def verify(a):
    ts=json.loads((a.out/'tasks.json').read_text());jobs={};edges=[]
    for arm in ARMS:
        assert json.loads((a.out/arm/'complete.json').read_text())==dict(arm=arm,cells=12)
        for t in ts:
            for name,head in HEADS.items():
                batch=json.loads((a.out/arm/(t['id'].replace('/','_')+'_'+name+'.json')).read_text());assert batch['prompt']==lean.PREFIX+lean.HEADER+t['statement']+head
                for i,s in enumerate(batch['rows']):
                    body,error=lean.completion_code(head+s['text']);key=None
                    if not error:
                        j=contracts.job(a.bundle,lean.HEADER+t['statement']+body+'\n#print axioms target\n');jobs[j['id']]=j;key=j['id']
                    edges.append(dict(arm=arm,task=t['id'],head=name,index=i,key=key,parse_error=error))
    lean.write(a.out/'sources.json',{k:j['code'] for k,j in jobs.items()});lean.write(a.out/'edges.json',edges)
    vs=lean.verify_jobs(list(jobs.values()),a.out/'verdicts.jsonl',workers=4);verdicts={v['id']:v for v in vs}
    result=dict(new_proposals=len(edges),saved_natural_proposals=192,unique_checks=len(vs),**scores(edges,verdicts,json.loads((a.out/'natural.json').read_text())))
    lean.write(a.out/'results.json',result);print(json.dumps(result,indent=2))


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('mode',choices=['prepare','run','verify']);p.add_argument('bundle',type=Path);p.add_argument('out',type=Path);p.add_argument('--arm',choices=ARMS);a=p.parse_args();globals()[a.mode](a)
