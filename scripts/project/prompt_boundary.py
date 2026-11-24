"""Factorial C1 BOS-placement control using authenticated native training format."""
import argparse
import json
import math
from pathlib import Path
import interface_discovery_pilot as lean
import run_policy_improvement as runtime
from policy_update_math import response_log_probs
from proof_prompt_interface import prompt,MODES,BOS,ExplicitTokenizer
import universal_constructor as contracts
from train_contract_closure import new_task


def panel():
    ts=[]
    for t in contracts.panel():
        ts.append(dict(id=t['id'],statement=t['statement'],witness_source=lean.HEADER+t['statement']+t['witness']+'\n#print axioms target\n',invalid_source=lean.HEADER+t['statement']+t['invalid']+'\n#print axioms target\n'))
    ts += [{k:v for k,v in new_task('opaque',sign).items() if k in ['id','statement','witness_source','invalid_source']} for sign in [-1,1]]
    return ts


def prepare(a):
    a.out.mkdir(parents=True,exist_ok=False);ts=panel();lean.write(a.out/'tasks.json',ts)
    audit=a.bundle/'runs/prompt-interface-audit-20261124/audit.json';assert json.loads(audit.read_text())['exact_native_matches']==128
    lean.write(a.out/'config.json',dict(modes=MODES,proposals=256,samples_per_cell=16,max_generated_tokens=768,seed_base=20261129,
        temperature=1,top_p=1,top_k=0,dtype='float32',tf32=False,training=False,native_audit_sha256=lean.sha(audit.read_bytes())))
    jobs={};edges=[]
    for t in ts:
        for kind in ['witness','invalid']:
            j=contracts.job(a.bundle,t[kind+'_source']);jobs[j['id']]=j;edges.append(dict(task=t['id'],kind=kind,key=j['id'],expected=kind=='witness'))
    lean.write(a.out/'fixture-edges.json',edges);lean.write(a.out/'fixture-sources.json',{k:j['code'] for k,j in jobs.items()})
    vs=lean.verify_jobs(list(jobs.values()),a.out/'fixture-verdicts.jsonl',workers=4);v={x['id']:x for x in vs}
    assert all(not v[e['key']].get('system_errors') and v[e['key']]['accepted']==e['expected'] for e in edges)
    lean.write(a.out/'ready.json',dict(passed=True,checks=len(vs),tasks_sha256=lean.sha((a.out/'tasks.json').read_bytes())))


def run(a):
    import torch
    ts=json.loads((a.out/'tasks.json').read_text());assert ts==panel() and json.loads((a.out/'ready.json').read_text())['passed']
    model,tok=runtime.load_model(a.bundle,a.bundle/'models/c1-final');explicit=ExplicitTokenizer(tok);dest=a.out/'samples';dest.mkdir(exist_ok=False);probes=[]
    for ti,t in enumerate(ts):
        plain=lean.PREFIX+lean.HEADER+t['statement'];core=tok.encode(plain,add_special_tokens=False)
        assert core[0]!=tok.bos_token_id and core[-1]!=tok.bos_token_id
        for mode,(leading,trailing) in MODES.items():
            text=prompt(t['statement'],mode);ids=explicit.encode(text);assert ids==([tok.bos_token_id] if leading else [])+core+([tok.bos_token_id] if trailing else [])
            if mode=='legacy':assert ids==tok.encode(plain)
            for head in ['  have source_contract :','  use fun']:
                extended=explicit.encode(text+head);assert extended[:len(ids)]==ids;suffix=extended[len(ids):]
                with torch.no_grad():lp=response_log_probs(model,ids,suffix,'cuda').tolist()
                probes.append(dict(task=t['id'],mode=mode,head=head,token_ids=suffix,log_probs=lp,log_probability=sum(lp)))
            rows=runtime.sample(model,explicit,text,20261129+ti,768,False)
            lean.write(dest/(t['id'].replace('/','_')+'_'+mode+'.json'),dict(task=t['id'],mode=mode,prompt=text,rows=rows))
    lean.write(a.out/'prefix-probes.json',probes);lean.write(a.out/'generation-complete.json',dict(cells=16,proposals=256))


def summarize(edges,vs):
    cells={}
    for e in edges:
        c=cells.setdefault(e['task'],{}).setdefault(e['mode'],dict(proposals=0,accepted=0,parse_errors=0,unresolved=0));c['proposals']+=1;c['parse_errors']+=bool(e['parse_error'])
        if e['key']:c['accepted']+=bool(vs[e['key']]['accepted']);c['unresolved']+=bool(vs[e['key']].get('system_errors'))
    resolved=all(c['unresolved']==0 for cs in cells.values() for c in cs.values());wins=[k for k,cs in cells.items() if cs['native']['accepted']>=cs['legacy']['accepted']+4]
    return dict(cells=cells,large_effect_tasks=wins,large_effect_gate=len(wins)>=2 and resolved,all_resolved=resolved)


def verify(a):
    ts=panel();assert json.loads((a.out/'generation-complete.json').read_text())==dict(cells=16,proposals=256);jobs={};edges=[]
    for t in ts:
        for mode in MODES:
            batch=json.loads((a.out/'samples'/(t['id'].replace('/','_')+'_'+mode+'.json')).read_text());assert batch['prompt']==prompt(t['statement'],mode) and len(batch['rows'])==16
            for i,s in enumerate(batch['rows']):
                body,error=lean.completion_code(s['text']);key=None
                if not error:
                    j=contracts.job(a.bundle,lean.HEADER+t['statement']+body+'\n#print axioms target\n');jobs[j['id']]=j;key=j['id']
                edges.append(dict(task=t['id'],mode=mode,index=i,key=key,parse_error=error))
    lean.write(a.out/'sources.json',{k:j['code'] for k,j in jobs.items()});lean.write(a.out/'edges.json',edges)
    rows=lean.verify_jobs(list(jobs.values()),a.out/'verdicts.jsonl',workers=4);vs={v['id']:v for v in rows}
    result=dict(proposals=256,unique_checks=len(vs),**summarize(edges,vs));lean.write(a.out/'results.json',result);print(json.dumps(result,indent=2))


def audit(a):
    from transformers import AutoTokenizer
    tok=AutoTokenizer.from_pretrained(str(a.bundle/'models/c1-final'),local_files_only=True);ts=panel();assert ts==json.loads((a.out/'tasks.json').read_text())
    sourceaudit=a.bundle/'runs/prompt-interface-audit-20261124/audit.json';assert lean.sha(sourceaudit.read_bytes())==json.loads((a.out/'config.json').read_text())['native_audit_sha256']
    ready=json.loads((a.out/'ready.json').read_text());assert ready['passed'] and ready['checks']==8 and ready['tasks_sha256']==lean.sha((a.out/'tasks.json').read_bytes())
    for stem in ['fixture-','']:
        sources=json.loads((a.out/(stem+'sources.json')).read_text());rows=lean.rows(a.out/(stem+'verdicts.jsonl'));vs={v['id']:v for v in rows}
        assert len(rows)==len(vs)==len(sources) and set(vs)==set(sources)
        for k,v in vs.items():
            assert k==v['code_sha256']==lean.sha(sources[k]);assert v['accepted']==bool(v['lean_complete'] and v['axiom_audit_found'] and set(v['axioms'])<=lean.ALLOWED_AXIOMS)
        if stem:
            expected=[]
            for t in ts:
                for kind in ['witness','invalid']:
                    code=t[kind+'_source'];key=lean.sha(code);assert sources[key]==code and not vs[key].get('system_errors') and vs[key]['accepted']==(kind=='witness');expected.append(dict(task=t['id'],kind=kind,key=key,expected=kind=='witness'))
            assert expected==json.loads((a.out/'fixture-edges.json').read_text())
    edges=json.loads((a.out/'edges.json').read_text());by={(e['task'],e['mode'],e['index']):e for e in edges};assert len(edges)==len(by)==256;used=set();cells={};accepted=[];token_counts={m:0 for m in MODES}
    probes=json.loads((a.out/'prefix-probes.json').read_text());ps={(p['task'],p['mode'],p['head']):p for p in probes};assert len(probes)==len(ps)==32
    for ti,t in enumerate(ts):
        core=tok.encode(lean.PREFIX+lean.HEADER+t['statement'],add_special_tokens=False)
        for mode,(leading,trailing) in MODES.items():
            ids=([100000] if leading else [])+core+([100000] if trailing else []);text=(BOS if leading else '')+lean.PREFIX+lean.HEADER+t['statement']+(BOS if trailing else '')
            batch=json.loads((a.out/'samples'/(t['id'].replace('/','_')+'_'+mode+'.json')).read_text());assert batch['prompt']==text and batch['task']==t['id'] and batch['mode']==mode and len(batch['rows'])==16
            c=dict(proposals=16,accepted=0,parse_errors=0,unresolved=0);cells.setdefault(t['id'],{})[mode]=c
            for head in ['  have source_contract :','  use fun']:
                extended=tok.encode(text+head,add_special_tokens=False);assert extended[:len(ids)]==ids;q=ps[t['id'],mode,head]
                assert q['token_ids']==extended[len(ids):] and len(q['log_probs'])==len(q['token_ids']) and all(math.isfinite(v) and v<=0 for v in q['log_probs']) and q['log_probability']==sum(q['log_probs'])
            for i,s in enumerate(batch['rows']):
                assert s['sample_index']==i and s['seed']==20261129+ti and s['prompt_token_ids']==ids and len(s['response_token_ids'])==s['generated_tokens']<=768
                decoded=tok.decode(s['response_token_ids'],skip_special_tokens=True);assert decoded==s['full_decoded_response'] and s['text']==(decoded.split('```',1)[0]+'```' if '```' in decoded else decoded)
                token_counts[mode]+=s['generated_tokens'];body,error=lean.completion_code(s['text']);key=None
                if not error:
                    code=lean.HEADER+t['statement']+body+'\n#print axioms target\n';key=lean.sha(code);assert sources[key]==code;used.add(key);c['accepted']+=bool(vs[key]['accepted']);c['unresolved']+=bool(vs[key].get('system_errors'))
                    if vs[key]['accepted']:accepted.append(dict(task=t['id'],mode=mode,index=i,key=key))
                c['parse_errors']+=bool(error);assert by[t['id'],mode,i]==dict(task=t['id'],mode=mode,index=i,key=key,parse_error=error)
    assert used==set(sources);resolved=all(c['unresolved']==0 for cc in cells.values() for c in cc.values());wins=[k for k,cc in cells.items() if cc['native']['accepted']-cc['legacy']['accepted']>=4]
    result=dict(proposals=256,unique_checks=len(vs),cells=cells,large_effect_tasks=wins,large_effect_gate=len(wins)>=2 and resolved,all_resolved=resolved);assert result==json.loads((a.out/'results.json').read_text())
    lean.write(a.out/'accepted-examples.json',accepted);report=dict(passed=True,generated_tokens=token_counts,**result);lean.write(a.out/'independent-audit.json',report);print(json.dumps(report,indent=2))


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('mode',choices=['prepare','run','verify','audit']);p.add_argument('bundle',type=Path);p.add_argument('out',type=Path);a=p.parse_args();globals()[a.mode](a)
