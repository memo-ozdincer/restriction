import concurrent.futures as cf, hashlib, json, pathlib, subprocess, sys, tempfile, time
ROOT=pathlib.Path(__file__).resolve().parent
PREV=ROOT.parent/'mathematical_speculation_lean_20261126'
sys.path.insert(0,str(PREV))
from verify import verify, HEADER, TOOLCHAIN, MATHLIB
PAIRS={'low':(('gpt-6-luna','low'),('gpt-6.1-terra','low')),'medium':(('gpt-6-luna','medium'),('gpt-6.1-terra','medium'))}
ROWS=json.loads((PREV/'panel.json').read_text())[:4]
SCHEMAS={'actor':{'action':{'type':'string','enum':['proof','question']},'message':{'type':'string'}},'partner':{'response':{'type':'string'}},'final':{'proof':{'type':'string'}}}
COMMON='Work on the exact Lean theorem below. Use only your own reasoning; no tools, commands, files, browsing, or other agents. Do not change the theorem or imports. No sorry, admit, new axioms, or new top-level declarations.\n'
def dump(p,x): p.write_text(json.dumps(x,indent=2)+'\n')
def base(r): return COMMON+HEADER+'\n'+r['statement']+'\n'
def call(r,pair,trial,stage,model,prompt,kind):
    out=ROOT/'rollouts'/pair/r['id']/str(trial)/stage; out.mkdir(parents=True,exist_ok=True)
    if (out/'metadata.json').exists(): return json.loads((out/'metadata.json').read_text())
    schema={'type':'object','properties':SCHEMAS[kind],'required':list(SCHEMAS[kind]),'additionalProperties':False}
    dump(out/'schema.json',schema); (out/'prompt.txt').write_text(prompt)
    name,effort=model; cmd=['codex','exec','--ignore-user-config','--ephemeral','--skip-git-repo-check','--sandbox','read-only','--color','never','--json','-m',name,'-c',f'model_reasoning_effort="{effort}"','--output-schema',str(out/'schema.json'),'--output-last-message',str(out/'answer.json'),'-']
    start=time.monotonic()
    with tempfile.TemporaryDirectory(prefix='lean-matched-help-') as cwd,(out/'events.jsonl').open('w') as so,(out/'stderr.txt').open('w') as se:
        try: rc=subprocess.run(cmd,input=prompt,text=True,cwd=cwd,stdout=so,stderr=se,timeout=360).returncode
        except subprocess.TimeoutExpired: rc=124
    elapsed=time.monotonic()-start; events=[]
    for line in (out/'events.jsonl').read_text().splitlines():
        try: events.append(json.loads(line))
        except ValueError: pass
    tool_items=[e['item']['type'] for e in events if isinstance(e.get('item'),dict) and e['item'].get('type') not in {'agent_message','reasoning','todo_list','plan'}]
    try: ans=json.loads((out/'answer.json').read_text()); valid=rc==0 and not tool_items and all(isinstance(ans[k],str) for k in SCHEMAS[kind]) and (kind!='actor' or ans['action'] in ['proof','question'])
    except Exception: ans=None; valid=False
    v=None
    if valid and (kind=='final' or kind=='actor' and ans['action']=='proof'): v=verify(r['statement'],r['id'],ans['proof'] if kind=='final' else ans['message'],out)
    m={'task':r['id'],'pair':pair,'trial':trial,'stage':stage,'model':name,'effort':effort,'cli_returncode':rc,'valid':valid,'tool_items':tool_items,'answer':ans,'generated_seconds':elapsed,'prompt_sha256':hashlib.sha256(prompt.encode()).hexdigest(),'usage':[e.get('usage') for e in events if e.get('type')=='turn.completed'],'verification':v}
    dump(out/'metadata.json',m); print(pair,r['id'],trial,stage,ans.get('action') if valid and kind=='actor' else v['accepted'] if v else valid,round(elapsed,1),flush=True); return m

def actor(r,p,i): return call(r,p,i,'actor',PAIRS[p][0],base(r)+'You may either submit the complete Lean tactic proof body after := by (action proof), or ask a partner model any question that you believe would help complete this theorem (action question). You may include any reasoning or attempted code in your question. Choose whichever you prefer. Put the proof or question in message. No Markdown fences around a proof.','actor')
def helper(r,p,i,a): return call(r,p,i,'partner',PAIRS[p][1],base(r)+'Another model working on this theorem sent the following message. Respond however you think useful. You may provide mathematical reasoning, Lean code, a complete proof, or any other response.\n\n'+a['answer']['message'],'partner')
def finish(r,p,i,a,stage,q=None,h=None):
    prompt=base(r)+'You previously sent this message while trying to solve the theorem:\n'+a['answer']['message']+'\n\n'
    if q is not None: prompt+='Here is a conversation about the same theorem:\nQuestion:\n'+q['answer']['message']+'\nResponse:\n'+h['answer']['response']+'\n\n'
    else: prompt+='No partner response is available.\n\n'
    prompt+='Now complete the original theorem. You may abandon any previous reasoning or use any available information. Return the complete tactic body after := by in proof, without Markdown fences.'
    return call(r,p,i,stage,PAIRS[p][0],prompt,'final')

def main():
    assert (TOOLCHAIN/'bin/lean').exists() and MATHLIB.exists()
    units=[(r,p,i) for p in PAIRS for r in ROWS for i in range(2)]
    lookup={(p,r['id'],i):r for r,p,i in units}
    with cf.ThreadPoolExecutor(max_workers=4) as ex:
        actors=list(ex.map(lambda x:actor(*x),units)); bank={(a['pair'],a['task'],a['trial']):a for a in actors}
        qs=[a for a in actors if a['valid'] and a['answer']['action']=='question']; jobs=[(lookup[(a['pair'],a['task'],a['trial'])],a['pair'],a['trial'],a) for a in qs]
        helpers=list(ex.map(lambda x:helper(*x),jobs)); replies={(h['pair'],h['task'],h['trial']):h for h in helpers}
        finals=[]
        for r,p,i,a in jobs:
            key=(p,r['id'],i); other=(p,r['id'],1-i); h=replies[key]
            finals.append((r,p,i,a,'control'))
            if h['valid']: finals.append((r,p,i,a,'matched',a,h))
            if h['valid'] and other in replies and replies[other]['valid']: finals.append((r,p,i,a,'swapped',bank[other],replies[other]))
        list(ex.map(lambda x:finish(*x),finals))
    dump(ROOT/'summary.json',[json.loads(p.read_text()) for p in sorted((ROOT/'rollouts').glob('*/*/*/*/metadata.json'))])
if __name__=='__main__': main()
