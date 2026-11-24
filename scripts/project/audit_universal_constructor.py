"""Reconstruct all proposal-to-contract verdicts without trusting aggregate counts."""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import interface_discovery_pilot as lean
from universal_constructor import panel


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('run',type=Path);a=p.parse_args();r=a.run
    tasks=panel();assert json.loads((r/'panel.json').read_text())==tasks
    ready=json.loads((r/'ready.json').read_text())
    for filename,key in [('panel.json','panel_sha256'),('model-inputs.json','inputs_sha256')]:
        assert lean.sha((r/filename).read_bytes())==ready[key]
    inputs=json.loads((r/'model-inputs.json').read_text())
    assert inputs==[dict(id=t['id'],prompt=lean.PREFIX+lean.HEADER+t['statement']) for t in tasks]
    samples=lean.rows(r/'samples.jsonl');edges=json.loads((r/'edges.json').read_text())
    assert len(samples)==128 and len(edges)==128
    assert lean.sha((r/'samples.jsonl').read_bytes())==json.loads((r/'generation-complete.json').read_text())['samples_sha256']
    expected={f"{t['id']}/{i}" for t in tasks for i in range(64)}
    assert {s['id'] for s in samples}==expected=={e['id'] for e in edges}
    by_edge={e['id']:e for e in edges};task_idx={t['id']:i for i,t in enumerate(tasks)}
    sources=json.loads((r/'sources.json').read_text());vs=lean.rows(r/'verdicts.jsonl')
    assert len(vs)==len(sources) and {v['id'] for v in vs}==set(sources)
    verdicts={v['id']:v for v in vs};used=set();cells={}
    for v in vs:
        assert lean.sha(sources[v['id']])==v['id']==v['code_sha256']
        assert v['accepted']==bool(v['lean_complete'] and v['axiom_audit_found'] and set(v['axioms'])<=lean.ALLOWED_AXIOMS)
    for s in samples:
        ti=task_idx[s['task_id']];task=tasks[ti]
        assert s['id']==f"{s['task_id']}/{16*s['batch']+s['sample_index']}"
        assert 0<=s['batch']<4 and 0<=s['sample_index']<16
        assert s['seed']==20261124+1000*ti+s['batch']
        assert s['prompt_tokens']==len(s['prompt_token_ids'])
        assert 0<s['generated_tokens']==len(s['response_token_ids'])<=768
        body,error=lean.completion_code(s['text']);key=None
        if not error:
            code=lean.HEADER+task['statement']+body+'\n#print axioms target\n';key=lean.sha(code)
            assert sources[key]==code;used.add(key)
        assert by_edge[s['id']]==dict(id=s['id'],task_id=s['task_id'],key=key,parse_error=error)
        c=cells.setdefault(s['task_id'],dict(proposals=0,accepted=0,parse_errors=0,unresolved=0))
        c['proposals']+=1;c['parse_errors']+=bool(error)
        if key:
            c['accepted']+=bool(verdicts[key]['accepted']);c['unresolved']+=bool(verdicts[key].get('system_errors'))
    assert used==set(sources)
    result=json.loads((r/'results.json').read_text());assert result['cells']==cells
    assert result['unique_checks']==len(vs) and result['proposals']==128
    gate=all(0<c['accepted']<64 and c['unresolved']==0 for c in cells.values())
    assert result['reward_support_gate']==gate
    fixture_sources=json.loads((r/'fixture-sources.json').read_text());fixtures=lean.rows(r/'fixture-verdicts.jsonl')
    assert len(fixtures)==4 and len(fixture_sources)==4
    fixture_expected={}
    for t in tasks:
        for kind in ['witness','invalid']:
            code=lean.HEADER+t['statement']+t[kind]+'\n#print axioms target\n';key=lean.sha(code)
            assert fixture_sources[key]==code;fixture_expected[key]=kind=='witness'
    assert {v['id'] for v in fixtures}==set(fixture_expected)
    assert all(v['accepted']==fixture_expected[v['id']] and not v.get('system_errors') for v in fixtures)
    report=dict(passed=True,cells=cells,proposals=128,unique_checks=len(vs),fixture_checks=4,
        reward_support_gate=gate,total_generated_tokens=sum(s['generated_tokens'] for s in samples),
        total_prompt_tokens=sum(s['prompt_tokens'] for s in samples),
        accepted_proposal_ids=[e['id'] for e in edges if e['key'] and verdicts[e['key']]['accepted']],
        scope='Audited universal-existence proofs; no parameter updates or extracted-program claim')
    lean.write(r/'independent-audit.json',report);print(json.dumps(report,indent=2))


if __name__=='__main__':main()
