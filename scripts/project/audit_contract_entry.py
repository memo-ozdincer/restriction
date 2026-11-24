"""Independently reconstruct prefixed continuation correctness and accounting."""
import argparse
import json
import math
from pathlib import Path
import interface_discovery_pilot as lean
from contract_entry import ARMS,HEADS,ADAPTER_SHA,prior,tasks


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('bundle',type=Path);p.add_argument('run',type=Path);a=p.parse_args();b=a.bundle;r=a.run;old=prior(b)
    from transformers import AutoTokenizer
    tok=AutoTokenizer.from_pretrained(str(b/'models/c1-final'),local_files_only=True)
    ts=tasks(b);assert ts==json.loads((r/'tasks.json').read_text());prov=json.loads((r/'provenance.json').read_text())
    assert prov['adapter_sha256']==ADAPTER_SHA==lean.sha((old/'transport/adapter/adapter_model.safetensors').read_bytes())
    for name in ['test','train','independent-audit']:
        key='prior_'+('audit' if name=='independent-audit' else name)+'_sha256';assert prov[key]==lean.sha((old/(name+'.json')).read_bytes())
    for name in ['tasks','natural']:assert prov[name+'_sha256']==lean.sha((r/(name+'.json')).read_bytes())
    old_edges=json.loads((old/'edges.json').read_text());old_vs={v['id']:v for v in lean.rows(old/'verdicts.jsonl')};old_sources=json.loads((old/'sources.json').read_text());natural=[]
    cells={};used=set();accepted=[];accounting={};probabilities={}
    for arm in ARMS:
        for t in ts:
            batch=json.loads((old/arm/(t['id'].replace('/','_')+'.json')).read_text());assert batch['prompt']==lean.PREFIX+lean.HEADER+t['statement']
            es=[e for e in old_edges if e['arm']==arm and e['task']==t['id']];assert len(es)==len(batch['rows'])==16
            c=dict(proposals=16,accepted=0,parse_errors=0,unresolved=0);cells.setdefault(arm,{})[t['id']]={'natural':c}
            for e,s in zip(es,batch['rows']):
                assert e['index']==s['sample_index'] and s['seed']==t['seed'];body,error=lean.completion_code(s['text']);key=None;v=None
                if not error:
                    code=lean.HEADER+t['statement']+body+'\n#print axioms target\n';key=lean.sha(code);v=old_vs[key];assert old_sources[key]==code and v['code_sha256']==key
                    assert v['accepted']==bool(v['lean_complete'] and v['axiom_audit_found'] and set(v['axioms'])<=lean.ALLOWED_AXIOMS)
                assert e['key']==key and e['parse_error']==error
                row=dict(arm=arm,task=t['id'],index=e['index'],text=s['text'],key=key,parse_error=error,accepted=bool(v and v['accepted']),unresolved=bool(v and v.get('system_errors')))
                natural.append(row);c['accepted']+=row['accepted'];c['unresolved']+=row['unresolved'];c['parse_errors']+=bool(error)
    assert natural==json.loads((r/'natural.json').read_text()) and len(natural)==192
    edges=json.loads((r/'edges.json').read_text());sources=json.loads((r/'sources.json').read_text());rows=lean.rows(r/'verdicts.jsonl');vs={v['id']:v for v in rows}
    assert len(rows)==len(vs)==len(sources) and set(vs)==set(sources)
    for k,v in vs.items():
        assert k==v['code_sha256']==lean.sha(sources[k]);assert v['accepted']==bool(v['lean_complete'] and v['axiom_audit_found'] and set(v['axioms'])<=lean.ALLOWED_AXIOMS)
    index={(e['arm'],e['task'],e['head'],e['index']):e for e in edges};assert len(edges)==len(index)==384
    for arm in ARMS:
        assert json.loads((r/arm/'complete.json').read_text())==dict(arm=arm,cells=12)
        check=json.loads((r/arm/'checkpoint-check.json').read_text());assert check==dict(arm=arm,adapter_sha256=ADAPTER_SHA if arm=='transport' else None,exact_reload_probe_match=arm=='transport')
        probes=json.loads((r/arm/'prefix-probes.json').read_text());assert len(probes)==12;probe_map={(q['task'],q['head']):q for q in probes};assert len(probe_map)==12
        accounting[arm]=dict(generated_tokens=0,supplied_tokens_across_proposals=0);probabilities[arm]={}
        for t in ts:
            base_prompt=lean.PREFIX+lean.HEADER+t['statement'];base_ids=tok.encode(base_prompt)
            for name,head in HEADS.items():
                batch=json.loads((r/arm/(t['id'].replace('/','_')+'_'+name+'.json')).read_text());prompt=base_prompt+head;ids=tok.encode(prompt);assert ids[:len(base_ids)]==base_ids;supplied=ids[len(base_ids):]
                assert batch['task']==t['id'] and batch['head']==name and batch['prompt']==prompt and batch['supplied_token_ids']==supplied and len(batch['rows'])==16
                q=probe_map[t['id'],name];assert q['supplied_token_ids']==supplied and len(q['log_probs'])==len(supplied) and all(math.isfinite(v) and v<=0 for v in q['log_probs']) and q['sequence_log_probability']==sum(q['log_probs'])
                probabilities[arm][t['id']+'/'+name]=dict(log_probability=q['sequence_log_probability'],probability=math.exp(q['sequence_log_probability']))
                c=dict(proposals=16,accepted=0,parse_errors=0,unresolved=0);cells[arm][t['id']][name]=c
                for i,s in enumerate(batch['rows']):
                    assert s['sample_index']==i and s['seed']==t['seed'] and s['prompt_token_ids']==ids
                    assert len(s['response_token_ids'])==s['generated_tokens']<=768-len(supplied)
                    decoded=tok.decode(s['response_token_ids'],skip_special_tokens=True);assert decoded==s['full_decoded_response'] and s['text']==(decoded.split('```',1)[0]+'```' if '```' in decoded else decoded)
                    accounting[arm]['generated_tokens']+=s['generated_tokens'];accounting[arm]['supplied_tokens_across_proposals']+=len(supplied)
                    body,error=lean.completion_code(head+s['text']);key=None
                    if not error:
                        code=lean.HEADER+t['statement']+body+'\n#print axioms target\n';key=lean.sha(code);assert sources[key]==code;used.add(key);v=vs[key];c['accepted']+=bool(v['accepted']);c['unresolved']+=bool(v.get('system_errors'))
                        if v['accepted']:accepted.append(dict(arm=arm,task=t['id'],head=name,index=i,key=key))
                    c['parse_errors']+=bool(error);assert index[arm,t['id'],name,i]==dict(arm=arm,task=t['id'],head=name,index=i,key=key,parse_error=error)
    assert used==set(sources)
    resolved=all(c['unresolved']==0 for aa in cells.values() for tt in aa.values() for c in tt.values())
    wins=[t['id'] for t in ts if not t['diagnostic'] and cells['transport'][t['id']]['natural']['accepted']<=1 and all(cells['transport'][t['id']][h]['accepted']>=8 and cells['base'][t['id']][h]['accepted']<=1 for h in HEADS)]
    result=dict(new_proposals=384,saved_natural_proposals=192,unique_checks=len(vs),cells=cells,winning_tasks=wins,conditional_gate=len(wins)>=3 and resolved,all_resolved=resolved)
    assert result==json.loads((r/'results.json').read_text())
    lean.write(r/'accepted-examples.json',accepted);report=dict(passed=True,accounting=accounting,prefix_probabilities=probabilities,**result);lean.write(r/'independent-audit.json',report);print(json.dumps(report,indent=2))


if __name__=='__main__':main()
