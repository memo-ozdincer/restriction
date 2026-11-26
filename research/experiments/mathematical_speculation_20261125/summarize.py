"""Verify and aggregate all observed math rollouts, separate answer/strategy metrics."""
import json,hashlib,re,statistics
from pathlib import Path
from fractions import Fraction
from collections import Counter
ROOT=Path(__file__).resolve().parent
panel=json.loads((ROOT/'panel.json').read_text())
answers=json.loads((ROOT/'answers.json').read_text())
hints=json.loads((ROOT/'teacher-hints.json').read_text())
strategy=json.loads((ROOT/'strategy-audit.json').read_text())['cases']
result={'per_arm':{},'per_task':{},'strategy':{}}
expected={
 'luna-baseline':set(answers),'terra-high':set(answers),
 'luna-insight':set(hints),'luna-control':set(hints),
 'luna-sharper':set(json.loads((ROOT/'sharper-hints.json').read_text()))
}
for arm,roots in expected.items():
 rows=[]
 for i in sorted(roots):
  d=ROOT/'rollouts'/arm/i
  r=json.loads((d/'metadata.json').read_text())
  a=json.loads((d/'answer.json').read_text())
  assert hashlib.sha256((d/'prompt.txt').read_bytes()).hexdigest()==r['prompt_sha256']
  events=[json.loads(l) for l in (d/'events.jsonl').read_text().splitlines()]
  bad=[e['item']['type'] for e in events if isinstance(e.get('item'),dict) and e['item'].get('type') not in {'agent_message','reasoning','todo_list','plan'}]
  assert r['valid'] and not bad and not r['tool_items']
  try:correct=Fraction(a['answer'].replace(',','').strip())==Fraction(answers[i])
  except ValueError:correct=False
  assert correct==r['correct']
  rows.append(r)
  result['per_task'].setdefault(i,{'reference':answers[i]})[arm]={'answer':a['answer'],'correct':correct,'time_seconds':r['elapsed_seconds']}
 result['per_arm'][arm]={'n':len(rows),'correct':sum(r['correct'] for r in rows),
                         'elapsed_sum_seconds':sum(r['elapsed_seconds'] for r in rows),
                         'elapsed_median_seconds':statistics.median(r['elapsed_seconds'] for r in rows),
                         'output_tokens':sum(u.get('output_tokens',0) for r in rows for u in r['usage'] if u),
                         'reasoning_output_tokens':sum(u.get('reasoning_output_tokens',0) for r in rows for u in r['usage'] if u)}
 for p in (ROOT/'rollouts'/arm).iterdir():assert p.name in roots
for typ in ['baseline','insight','control']:
 result['strategy'][typ]={'n':len(strategy),'same_method':sum(x[typ]['same_method'] for x in strategy.values()),
                          'explicit_teacher_fact_use':sum(x[typ].get('teacher_fact_use',False) for x in strategy.values()) if typ!='control' else None}
for typ in ['insight','control']:
 result[f'{typ}_rescued_luna_failures']=sum(result['per_task'][i]['luna-'+typ]['correct'] and not result['per_task'][i]['luna-baseline']['correct'] for i in hints)
 print(typ,result[f'{typ}_rescued_luna_failures'])
print(json.dumps(result,indent=2))
(ROOT/'summary.json').write_text(json.dumps(result,indent=2)+'\n')
