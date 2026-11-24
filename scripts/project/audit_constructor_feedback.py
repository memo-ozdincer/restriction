"""Audit exact prompts, tokens, seeds, certificates and universal contract outcomes."""
import argparse
from collections import Counter
import json
from pathlib import Path
import interface_discovery_pilot as lean
import universal_constructor as contracts


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('run',type=Path);r=p.parse_args().run
    b=r.parents[2]
    from transformers import AutoTokenizer
    tok=AutoTokenizer.from_pretrained(str(b/'models/c1-final'))
    ready=json.loads((r/'ready.json').read_text());assert ready['passed']
    for file,key in [('inputs.json','inputs_sha256'),('feedback.json','feedback_sha256')]:
        assert lean.sha((r/file).read_bytes())==ready[key]
    old=b/'runs/universal-constructor-20261123-1399519/experiment/samples.jsonl'
    assert lean.sha(old.read_bytes())==ready['old_samples_sha256']
    old_rows=lean.rows(old);feedback=json.loads((r/'feedback.json').read_text())
    tasks=contracts.panel();inputs=json.loads((r/'inputs.json').read_text())
    assert len(inputs)==6 and len(feedback)==2
    by_input={i['id']:i for i in inputs};assert len(by_input)==6
    fs=json.loads((r/'fixture-sources.json').read_text());fv=lean.rows(r/'fixture-verdicts.jsonl')
    assert len(fs)==8 and len(fv)==8 and {v['id'] for v in fv}==set(fs)
    vfs={v['id']:v for v in fv}
    for v in fv:
        assert lean.sha(fs[v['id']])==v['id']==v['code_sha256'] and not v.get('system_errors')
    for ti,(task,f) in enumerate(zip(tasks,feedback)):
        assert f['task_id']==task['id']
        family=[x for x in old_rows if x['task_id']==task['id']]
        text,count=Counter(x['text'] for x in family).most_common(1)[0]
        assert (f['selected_response'],f['count'])==(text,count)
        assert f['function'] in text
        assert f['proposal_ids']==[x['id'] for x in family if x['text']==text]
        assert f['lhs_value']!=f['rhs_value']
        assert len(f['feedback_source_sha256'])==2
        assert all(vfs[k]['accepted'] for k in f['feedback_source_sha256'])
        for kind in ['witness','invalid']:
            code=lean.HEADER+task['statement']+task[kind]+'\n#print axioms target\n'
            assert fs[lean.sha(code)]==code and vfs[lean.sha(code)]['accepted']==(kind=='witness')
        for arm in ['failure','counterexample','residual']:
            inp=by_input[task['id']+'/'+arm]
            assert inp['seed']==20261125+1000*ti and inp['task_id']==task['id'] and inp['arm']==arm
            prefix=(f"-- Rejected candidate: {f['function']}\n-- This candidate does not satisfy the following contract.\n")
            info={'failure':'No additional feedback.',
                'counterexample':f"Input {f['assignment']} gives left side {f['lhs_value']}, right side {f['rhs_value']}; they differ.",
                'residual':f"For arbitrary integer inputs, left side minus right side of the first law is {f['residual']}. It must be zero."}[arm]
            expected=lean.PREFIX+lean.HEADER+prefix+'-- Verification feedback: '+info+'\n-- Supply an implementation and proof satisfying every clause.\n'+task['statement']
            assert inp['prompt']==expected
    samples=lean.rows(r/'samples.jsonl');edges=json.loads((r/'edges.json').read_text());sources=json.loads((r/'sources.json').read_text())
    vs=lean.rows(r/'verdicts.jsonl');verdicts={v['id']:v for v in vs};by_edge={e['id']:e for e in edges}
    assert len(vs)==len(sources)==len(verdicts) and set(sources)==set(verdicts)
    expected={i+'/'+str(n) for i in by_input for n in range(16)}
    assert len(samples)==96 and len(edges)==96 and {s['id'] for s in samples}==set(by_edge)==expected
    assert lean.sha((r/'samples.jsonl').read_bytes())==json.loads((r/'generation-complete.json').read_text())['samples_sha256']
    tasks={t['id']:t for t in tasks};cells={};used=set()
    for v in vs:
        assert v['id']==v['code_sha256']==lean.sha(sources[v['id']])
        assert v['accepted']==bool(v['lean_complete'] and v['axiom_audit_found'] and set(v['axioms'])<=lean.ALLOWED_AXIOMS)
    for s in samples:
        name=s['id'].rsplit('/',1)[0];inp=by_input[name]
        assert s['id']==name+'/'+str(s['sample_index']) and s['seed']==inp['seed']
        assert s['task_id']==inp['task_id'] and s['arm']==inp['arm']
        assert s['prompt_token_ids']==tok.encode(inp['prompt']) and s['prompt_tokens']==len(s['prompt_token_ids'])
        assert s['generated_tokens']==len(s['response_token_ids'])<=768
        assert tok.decode(s['response_token_ids'],skip_special_tokens=True)==s['full_decoded_response']
        body,error=lean.completion_code(s['text']);key=None
        if not error:
            code=lean.HEADER+tasks[s['task_id']]['statement']+body+'\n#print axioms target\n';key=lean.sha(code)
            assert sources[key]==code;used.add(key)
        assert by_edge[s['id']]==dict(id=s['id'],key=key,parse_error=error)
        c=cells.setdefault(name,dict(proposals=0,accepted=0,parse_errors=0,unresolved=0))
        c['proposals']+=1;c['parse_errors']+=bool(error)
        if key:c['accepted']+=bool(verdicts[key]['accepted']);c['unresolved']+=bool(verdicts[key].get('system_errors'))
    assert used==set(sources)
    strong={a:all(cells[t+'/'+a]['accepted']>=4 and cells[t+'/failure']['accepted']<=1 for t in tasks)
        and all(not c['unresolved'] for c in cells.values()) for a in ['counterexample','residual']}
    result=json.loads((r/'results.json').read_text());assert result['cells']==cells and result['strong_feedback_effect']==strong
    assert result['proposals']==96 and result['unique_checks']==len(vs)
    report=dict(passed=True,cells=cells,proposals=96,unique_checks=len(vs),fixture_checks=8,
        strong_feedback_effect=strong,accepted_ids=[e['id'] for e in edges if e['key'] and verdicts[e['key']]['accepted']],
        generated_tokens=sum(s['generated_tokens'] for s in samples),prompt_tokens=sum(s['prompt_tokens'] for s in samples))
    lean.write(r/'independent-audit.json',report);print(json.dumps(report,indent=2))


if __name__=='__main__':main()
