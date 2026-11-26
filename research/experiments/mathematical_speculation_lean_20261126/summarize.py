"""Reconcile all CLI sessions, verifier results, payloads and budget totals."""
import hashlib,json
from pathlib import Path
from collections import Counter
from statistics import median
from verify import ROOT
panel=json.loads((ROOT/'panel.json').read_text())
roots={r['id'] for r in panel}
partial={'terra-from-medium-idea':set(json.loads((ROOT/'medium-divergent-ideas.json').read_text())),
         'luna-with-verified-fact':set(json.loads((ROOT/'verified-teacher-facts.json').read_text()))}
arms=['luna-low','luna-medium','terra-high','terra-from-low-idea',
      'terra-from-medium-idea','luna-with-verified-fact','luna-idea-only','terra-from-idea-only']
data={};per_task={}
for arm in arms:
    path=ROOT/'rollouts'/arm
    actual={p.name for p in path.iterdir()}
    assert actual==partial.get(arm,roots),(arm,actual)
    rows=[]
    for n in sorted(actual):
        p=path/n;m=json.loads((p/'metadata.json').read_text());a=json.loads((p/'answer.json').read_text())
        assert hashlib.sha256((p/'prompt.txt').read_bytes()).hexdigest()==m['prompt_sha256']
        events=[json.loads(l) for l in (p/'events.jsonl').read_text().splitlines()]
        bad=[e['item']['type'] for e in events if isinstance(e.get('item'),dict) and e['item'].get('type') not in {'agent_message','reasoning','todo_list','plan'}]
        assert m['valid'] and not bad and not m['tool_items']
        if arm!='luna-idea-only':
            v=m['verification']
            if v['accepted']:assert v['returncode']==0 and set(v['axioms'])<={'propext','Classical.choice','Quot.sound'}
            if (p/'candidate.lean').exists():assert (p/'lean-output.txt').exists()
        rows.append(m)
        per_task.setdefault(n,{})[arm]={'idea':a['idea'],'accepted':m.get('verification',{}).get('accepted'),'generation_seconds':m['generated_seconds'],
          'output_tokens':sum(x.get('output_tokens',0) for x in m['usage'] if x)}
    data[arm]={'n':len(rows),'accepted':None if arm=='luna-idea-only' else sum(m['verification']['accepted'] for m in rows),
               'accepted_roots':sorted(m['task'] for m in rows if m.get('verification',{}).get('accepted')),
               'generation_seconds_sum':sum(m['generated_seconds'] for m in rows),
               'generation_seconds_median':median(m['generated_seconds'] for m in rows),
               'verification_seconds_sum':sum(m.get('verification',{}).get('elapsed_seconds',0) for m in rows),
               **{k:sum(x.get(k,0) for m in rows for x in m['usage'] if x) for k in ['input_tokens','cached_input_tokens','output_tokens','reasoning_output_tokens']}}
for arm,payload in [('terra-from-low-idea','low-ideas.json'),('terra-from-medium-idea','medium-divergent-ideas.json'),('terra-from-idea-only','idea-only-handoffs.json')]:
    for n,idea in json.loads((ROOT/payload).read_text()).items():
        text=(ROOT/'rollouts'/arm/n/'prompt.txt').read_text()
        assert text.endswith(idea+'\n'),(arm,n)
hybrids={}
for name,pair in [('full_proof_idea',['luna-low','terra-from-low-idea']),('idea_only',['luna-idea-only','terra-from-idea-only'])]:
    hybrids[name]={k:sum(data[a][k] for a in pair) for k in ['input_tokens','output_tokens','reasoning_output_tokens','generation_seconds_sum','verification_seconds_sum']}
    hybrids[name]['accepted']=data[pair[1]]['accepted']
    hybrids[name]['accepted_roots']=data[pair[1]]['accepted_roots']
result=dict(arms=data,hybrids=hybrids,per_task=per_task,total_sessions=sum(v['n'] for v in data.values()))
(ROOT/'summary.json').write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n')
print(json.dumps({'arms':data,'hybrids':hybrids,'total_sessions':result['total_sessions']},indent=2))
