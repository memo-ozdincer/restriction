"""Authenticate the frozen panel, prompts, sources and exact terminal counts."""
from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor
import hashlib
import json
from pathlib import Path
import tempfile

from run import ROOT, LEAN, sha, source, helper_source, actor_prompt, COMMON, HELP_RULE, task_text, verify

def read(p):
    return json.loads(p.read_text())

panel=read(ROOT/'panel.json')
runtime=read(ROOT/'runtime.json')
assert sha(ROOT/'panel.json')==runtime['panel_sha256']
assert sha(ROOT/'run.py')==runtime['runner_sha256']
assert sha(LEAN)==runtime['lean_binary_sha256']
assert sha(LEAN.parents[2]/'lean-4.9.0-rc1-darwin_aarch64.tar.zst')==runtime['lean_archive_sha256']
summary={'panel':{},'calls':Counter(),'token_totals':defaultdict(Counter),'verifier_checks':Counter(),'diagnostics':{}}
accepted=[]
for row in panel:
    rd=ROOT/'rollouts'/row['id']
    helpers=[read(rd/'helper'/str(i)/'checked-object.json') for i in range(3)]
    info=summary['panel'][row['id']]={}
    info['verified_objects']=sum(o is not None for o in helpers)
    info['helper_types']=[read(rd/'helper'/str(i)/'answer.json')['type'] for i in range(3)]
    for arm in ['helper','bare_low','direct_medium','isolated_low','bundle_low']+(['format_only_low'] if row['id']=='reverse' else []):
        count=0
        for i in range(3):
            d=rd/arm/str(i);m=read(d/'metadata.json');a=read(d/'answer.json')
            assert m['valid'] and m['returncode']==0 and not m['tools'] and not m['malformed_events']
            assert m['model']=='gpt-6-luna' and m['effort']==('medium' if arm in ('helper','direct_medium') else 'low')
            assert sha(d/'prompt.txt')==m['prompt_sha256']
            ev=[json.loads(l) for l in (d/'events.jsonl').read_text().splitlines()]
            assert not [e for e in ev if isinstance(e.get('item'),dict) and
                        e['item'].get('type') not in {'agent_message','reasoning','todo_list','plan'}]
            summary['calls'][arm]+=1
            for u in m['usage']:
                summary['token_totals'][arm].update({k:int(v) for k,v in u.items()})
            summary['token_totals'][arm]['sum_cli_seconds']+=m['elapsed_seconds']
            if arm=='helper':
                assert (d/'prompt.txt').read_text()==COMMON+HELP_RULE+task_text(row)
                obj=helpers[i]
                expected={**a,'name':f'help{i}'}
                v=d/'object_check'/'verdict.json'
                if v.exists():
                    assert (v.parent/'source.lean').read_text()==helper_source(row,expected)
                    ok=read(v)['accepted']
                    assert (obj is not None)==ok
                    if ok:assert obj==expected
                else:
                    assert obj is None
                count+=obj is not None
            else:
                expected=[] if arm in ('bare_low','direct_medium') else (
                    [helpers[i]] if helpers[i] else []) if arm=='isolated_low' else (
                    [o for o in helpers if o] if arm=='bundle_low' else
                    [read(ROOT/'diagnostics'/'reverse-format-only-object.json')])
                assert read(d/'objects.json')==expected
                assert (d/'prompt.txt').read_text()==actor_prompt(row,expected)
                v=d/'root_check'/'verdict.json'
                outcome=read(d/'outcome.json')['accepted']
                if v.exists():
                    assert (v.parent/'source.lean').read_text()==source(row,a['body'],expected)
                    assert outcome==read(v)['accepted']
                else:assert not outcome
                count+=outcome
                if outcome:accepted.append({'task':row['id'],'arm':arm,'trial':i,'body':a['body'],'objects':[o['name'] for o in expected]})
        info[arm]=count
assert summary['calls']=={'helper':12,'bare_low':12,'direct_medium':12,'isolated_low':12,'bundle_low':12,'format_only_low':3}
summary['accepted_continuations']=accepted
# Replay every original certificate verbatim in fresh independently created paths.
checks=sorted(ROOT.rglob('verdict.json'))
def recheck(p):
    v=read(p);f=p.parent/'source.lean'
    assert sha(f)==v['source_sha256']
    code=f.read_text();target='obj' if code.rstrip().endswith('#print axioms obj') else 'root'
    with tempfile.TemporaryDirectory(prefix='frozen-help-audit-') as td:
        r=verify(Path(td)/'check',code,target)
        assert r['accepted']==v['accepted'],p
        assert r['returncode']==v['returncode'],p
    return p,v
with ThreadPoolExecutor(max_workers=4) as ex:
    for p,v in ex.map(recheck,checks):
        summary['verifier_checks']['total']+=1
        summary['verifier_checks']['accepted' if v['accepted'] else 'rejected']+=1
        if v['returncode']==124:summary['verifier_checks']['timeouts']+=1
        rel=str(p.relative_to(ROOT))
        if rel.startswith('diagnostics/') or 'replay_bare/' in rel:
            summary['diagnostics'][rel]=v['accepted']
summary['audit']='PASS (all source/prompt hashes, 63 actual CLI calls, all saved Lean verdicts rerun)'
(ROOT/'summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(summary,ensure_ascii=False,indent=2))
