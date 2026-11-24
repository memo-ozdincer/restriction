"""Reconstruct closure-learning data, tokens, verifier edges and decision gates."""
import argparse
import json
import math
from pathlib import Path
import interface_discovery_pilot as lean
from train_contract_closure import training,panel,fixtures,CONFIG,ARMS


def checked_verdicts(path,sources):
    rows=lean.rows(path);vs={v['id']:v for v in rows};assert len(rows)==len(vs)==len(sources) and set(vs)==set(sources)
    for k,v in vs.items():
        assert k==v['code_sha256']==lean.sha(sources[k])
        assert v['accepted']==bool(v['lean_complete'] and v['axiom_audit_found'] and set(v['axioms'])<=lean.ALLOWED_AXIOMS)
    return vs


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('bundle',type=Path);p.add_argument('run',type=Path);p.add_argument('--panel-only',action='store_true');a=p.parse_args();b=a.bundle;r=a.run
    train=training(b);tasks=panel(b)
    assert train==json.loads((r/'train.json').read_text()) and tasks==json.loads((r/'test.json').read_text()) and CONFIG==json.loads((r/'config.json').read_text())
    ready=json.loads((r/'ready.json').read_text());assert ready['passed'] and ready['failures']==[]
    assert ready['train_sha256']==lean.sha((r/'train.json').read_bytes()) and ready['test_sha256']==lean.sha((r/'test.json').read_bytes())
    jobs,fe=fixtures(b,train,tasks);fs={k:j['code'] for k,j in jobs.items()}
    assert fs==json.loads((r/'fixture-sources.json').read_text()) and fe==json.loads((r/'fixture-edges.json').read_text())
    fv=checked_verdicts(r/'fixture-verdicts.jsonl',fs)
    assert all(not fv[e['key']].get('system_errors') and fv[e['key']]['accepted']==e['expected'] for e in fe)
    assert len(fe)==ready['fixture_edges']==44 and len(fv)==ready['unique_checks']
    assert [x['statement'] for x in train['executable']]==[x['statement'] for x in train['transport']]
    old={t['statement'] for rs in train.values() for t in rs}
    assert len(tasks)==10 and all(t['statement'] not in old for t in tasks[:8])
    assert all('source_contract' not in t['statement'] for t in tasks)
    report=dict(passed=True,fixture_edges=len(fe),unique_fixture_checks=len(fv),new_targets=8,original_diagnostics=2)
    if a.panel_only:
        lean.write(r/'panel-audit.json',report);print(json.dumps(report,indent=2));return
    from transformers import AutoTokenizer
    tok=AutoTokenizer.from_pretrained(str(b/'models/c1-final'),local_files_only=True)
    trainings={}
    for arm in ARMS[1:]:
        d=r/arm;records=json.loads((d/'tokens.json').read_text());refs=json.loads((d/'reference-probes.json').read_text());final=json.loads((d/'reload-probes.json').read_text())
        assert len(records)==len(refs)==len(final)==8 and final!=refs
        for i,row in enumerate(train[arm]):
            expected=dict(id=row['id'],prompt_token_ids=tok.encode(lean.PREFIX+lean.HEADER+row['statement']),response_token_ids=tok.encode(row['response'],add_special_tokens=False))
            assert records[i]==expected and len(refs[i])==len(final[i])==len(expected['response_token_ids'])
            assert all(math.isfinite(v) for v in refs[i]+final[i])
        metrics=lean.rows(d/'metrics.jsonl');assert len(metrics)==32
        for i,m in enumerate(metrics):
            assert m['step']==i+1 and m['id']==train[arm][i%8]['id'] and m['tokens']==len(records[i%8]['response_token_ids'])
            assert all(math.isfinite(m[k]) for k in ['nll','anchor','grad_norm'])
        done=json.loads((d/'training-complete.json').read_text())
        assert done['steps']==32 and all(done[k] for k in ['reference_unchanged','initial_adapter_equal_reference','serialized_weights_exact'])
        assert done['train_sha256']==ready['train_sha256'] and done['adapter_sha256']==lean.sha((d/'adapter/adapter_model.safetensors').read_bytes())
        cfg=json.loads((d/'adapter/adapter_config.json').read_text());assert cfg['r']==8 and cfg['lora_alpha']==16 and set(cfg['target_modules'])=={'q_proj','v_proj'} and cfg['lora_dropout']==0
        trainings[arm]=dict(**done,response_tokens_per_epoch=sum(len(x['response_token_ids']) for x in records))
    edges=json.loads((r/'edges.json').read_text());sources=json.loads((r/'sources.json').read_text());vs=checked_verdicts(r/'verdicts.jsonl',sources)
    assert len(edges)==640;by_edge={(e['arm'],e['task'],e['index']):e for e in edges};assert len(by_edge)==640
    cells={};used=set();accepted=[];generated={}
    for arm in ARMS:
        assert json.loads((r/arm/'complete.json').read_text())==dict(arm=arm,tasks=[t['id'] for t in tasks]);generated[arm]=0
        for ti,t in enumerate(tasks):
            batch=json.loads((r/arm/(t['id'].replace('/','_')+'.json')).read_text());prompt=lean.PREFIX+lean.HEADER+t['statement']
            assert batch['id']==t['id'] and batch['prompt']==prompt and len(batch['rows'])==16
            c=dict(proposals=16,accepted=0,parse_errors=0,unresolved=0);cells.setdefault(arm,{})[t['id']]=c
            for i,s in enumerate(batch['rows']):
                assert s['sample_index']==i and s['seed']==20261127+ti and s['prompt_token_ids']==tok.encode(prompt)
                assert len(s['response_token_ids'])==s['generated_tokens']<=768
                decoded=tok.decode(s['response_token_ids'],skip_special_tokens=True);assert decoded==s['full_decoded_response']
                assert s['text']==(decoded.split('```',1)[0]+'```' if '```' in decoded else decoded)
                generated[arm]+=s['generated_tokens'];body,error=lean.completion_code(s['text']);key=None
                if not error:
                    code=lean.HEADER+t['statement']+body+'\n#print axioms target\n';key=lean.sha(code);assert sources[key]==code;used.add(key)
                    c['accepted']+=bool(vs[key]['accepted']);c['unresolved']+=bool(vs[key].get('system_errors'))
                    if vs[key]['accepted']:accepted.append(dict(arm=arm,task=t['id'],index=i,key=key))
                c['parse_errors']+=bool(error)
                assert by_edge[arm,t['id'],i]==dict(arm=arm,task=t['id'],index=i,key=key,parse_error=error)
    assert used==set(sources)
    wins={arm:[t['id'] for t in tasks[:8] if cells[arm][t['id']]['accepted']>=8 and cells['base'][t['id']]['accepted']<=1 and cells['hindsight'][t['id']]['accepted']<=1] for arm in ['executable','transport']}
    resolved=all(c['unresolved']==0 for cs in cells.values() for c in cs.values())
    closure=any(len(keys)>=3 and any(k.startswith('opaque/') for k in keys) and any(k.startswith('renamed/') for k in keys) for keys in wins.values()) and resolved
    opaque=[t['id'] for t in tasks if t['variant'] in ['opaque','renamed']]
    abstract=(len([k for k in opaque if cells['transport'][k]['accepted']>=8])>=3 and len([k for k in opaque if cells['transport'][k]['accepted']>=cells['executable'][k]['accepted']+4])>=2 and resolved)
    result=dict(cells=cells,proposals=640,unique_checks=len(vs),closure_winning_cells=wins,closure_gate=closure,abstraction_gate=abstract,all_resolved=resolved)
    assert result==json.loads((r/'results.json').read_text())
    report.update(training=trainings,generated_tokens=generated,**result)
    lean.write(r/'accepted-examples.json',accepted);lean.write(r/'independent-audit.json',report);print(json.dumps(report,indent=2))


if __name__=='__main__':main()
