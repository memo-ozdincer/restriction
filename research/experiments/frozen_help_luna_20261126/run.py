"""Frozen CLI responses; independent Lean checks; preserve every physical call."""
import argparse
import concurrent.futures as cf
from collections import Counter
import hashlib
import json
from pathlib import Path
import re
import subprocess
import tempfile
import textwrap
import time

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parents[2]
LEAN = REPO / 'artifacts/lean-cli-verifier/lean-4.9.0-rc1-darwin_aarch64/bin/lean'
MODEL = 'gpt-6-luna'
K = 3
ALLOWED_AXIOMS = {'propext', 'Classical.choice', 'Quot.sound'}
SCHEMAS = {
    'proof': {'type':'object','properties':{'body':{'type':'string'}},
              'required':['body'],'additionalProperties':False},
    'helper': {'type':'object','properties':{
        'binding':{'type':'string','enum':['have','let','decline']},
        'type':{'type':'string'},'term':{'type':'string'}},
        'required':['binding','type','term'],'additionalProperties':False}
}
COMMON = ('Use only your own mathematical reasoning; do not use any tools, files, shell, '
          'code execution, browsing, external resources, or other agents. Lean version '
          '4.9.0-rc1, import Lean (core, no Mathlib). Return only JSON matching the schema. '
          'No sorry, admit, new axioms, global declarations, or metaprogramming.\n')
PROOF_RULE = ('Write ONLY the tactic body after the final by (without the enclosing theorem '
              'or initial by). You may use native Lean tactics and any supplied local '
              'bindings, or ignore them. Complete the unchanged target.\n')
HELP_RULE = ('You are the mathematical partner. Independently choose a single arbitrary '
             'well-typed local mathematical object useful to another prover working on '
             'this target, or decline. Return binding have or let, the type and a complete '
             'Lean term of that type (a by tactic term is fine), all under the given '
             'theorem binders. There is no prescribed type or mathematical structure; '
             'you may prove the target itself. Do not give extra prose. If you decline, '
             'return binding decline and empty strings.\n')

def dump(path, obj):
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + '\n')

def sha(path):
    return hashlib.file_digest(path.open('rb'), 'sha256').hexdigest()

def header(row):
    return 'import Lean\n\n'+row['definitions']+'\n\n'

def declaration(row):
    return f"theorem root {row['binders']} : {row['goal']} := by"

def pad(s, n=2):
    return textwrap.indent(textwrap.dedent(s).strip(), ' '*n, lambda _:True)

def clean(s):
    # Restrict generated snippets to ordinary local mathematical syntax.
    # This is a lexical admission gate, not a correctness judge.
    return bool(s.strip()) and not re.search(
        r'(?mi)\b(sorry|admit|axiom|unsafe|run_tac|run_meta|elab|syntax|macro|IO|set_option|import)\b|^\s*#',
        s)

def source(row, body, objects):
    lines=[header(row)+declaration(row)]
    for o in objects:
        lines.append(f"  {o['binding']} {o['name']} : (\n{pad(o['type'],4)}\n  ) := (\n{pad(o['term'],4)}\n  )")
    lines.append(pad(body))
    lines.append('#print axioms root')
    return '\n'.join(lines)+'\n'

def helper_source(row, o):
    return header(row)+f"noncomputable def obj {row['binders']} : (\n{pad(o['type'])}\n) := (\n{pad(o['term'])}\n)\n#print axioms obj\n"

def verify(path, code, target):
    path.mkdir(parents=True,exist_ok=False)
    f=path/'source.lean'; f.write_text(code)
    t=time.monotonic()
    try:
        p=subprocess.run([str(LEAN),str(f)],text=True,capture_output=True,timeout=25,cwd=path)
        out=p.stdout+p.stderr; rc=p.returncode
    except subprocess.TimeoutExpired as e:
        out=str(e);rc=124
    (path/'lean.log').write_text(out)
    found=re.findall(rf"'{target}' depends on axioms: \[([^\]]*)\]",out)
    no_axioms=bool(re.search(rf"'{target}' does not depend on any axioms",out))
    axioms={a.strip() for a in found[0].split(',') if a.strip()} if len(found)==1 else set()
    accepted=(rc==0 and (len(found)==1 or no_axioms) and axioms<=ALLOWED_AXIOMS and
              not re.search(r'\b(sorryAx|sorry|admit)\b',out))
    result={'accepted':accepted,'returncode':rc,'axioms':sorted(axioms),'source_sha256':sha(f),
            'elapsed_seconds':time.monotonic()-t}
    dump(path/'verdict.json',result)
    return result

def task_text(row):
    return 'Lean source:\n'+header(row)+declaration(row)+'\n'

def actor_prompt(row, objects):
    prompt=COMMON+PROOF_RULE+task_text(row)
    if objects:
        prompt+='\nThe following independently checked local bindings are already present at the start of the tactic body. Do NOT re-declare them.\n'
        for o in objects:
            prompt+=f"{o['name']} : {o['type']}\n"
            if o['binding']=='let':
                prompt+=f"{o['name']} := {o['term']}\n"
    else:
        prompt+='\nNo additional local bindings are supplied.\n'
    return prompt

def cli(out, prompt, schema_kind, effort):
    out.mkdir(parents=True,exist_ok=False)
    (out/'prompt.txt').write_text(prompt);dump(out/'schema.json',SCHEMAS[schema_kind])
    cmd=['codex','exec','--ignore-user-config','--ephemeral','--skip-git-repo-check',
         '--sandbox','read-only','--color','never','--json','-m',MODEL,'-c',
         f'model_reasoning_effort="{effort}"','--output-schema',str(out/'schema.json'),
         '--output-last-message',str(out/'answer.json'),'-']
    start=time.monotonic()
    with tempfile.TemporaryDirectory(prefix='frozen-help-isolated-') as cwd:
        with (out/'events.jsonl').open('w') as stdout,(out/'stderr.txt').open('w') as stderr:
            try:
                p=subprocess.run(cmd,input=prompt,text=True,cwd=cwd,stdout=stdout,stderr=stderr,timeout=180)
                rc=p.returncode
            except subprocess.TimeoutExpired:
                rc=124
    events=[]; bad_events=0
    for line in (out/'events.jsonl').read_text().splitlines():
        try:events.append(json.loads(line))
        except json.JSONDecodeError:bad_events+=1
    tools=[e['item'].get('type') for e in events if isinstance(e.get('item'),dict)
            and e['item'].get('type') not in {'agent_message','reasoning','todo_list','plan'}]
    try:answer=json.loads((out/'answer.json').read_text())
    except (FileNotFoundError,json.JSONDecodeError):answer=None
    expected=SCHEMAS[schema_kind]['required']
    valid=(rc==0 and isinstance(answer,dict) and set(answer)==set(expected)
           and all(isinstance(answer[k],str) for k in expected) and not tools and not bad_events)
    info={'returncode':rc,'elapsed_seconds':time.monotonic()-start,'valid':bool(valid),
          'tools':tools,'malformed_events':bad_events,'effort':effort,'model':MODEL,
          'usage':[e.get('usage') for e in events if e.get('type')=='turn.completed'],
          'prompt_sha256':sha(out/'prompt.txt'),'command':cmd[:-1]+['<prompt via stdin>']}
    dump(out/'metadata.json',info)
    return answer if valid else None

def one_helper(row,i):
    out=ROOT/'rollouts'/row['id']/'helper'/str(i)
    answer=cli(out,COMMON+HELP_RULE+task_text(row),'helper','medium')
    obj=None
    if answer and answer['binding'] in ('have','let') and clean(answer['type']) and clean(answer['term']):
        candidate={**answer,'name':f'help{i}'}
        if verify(out/'object_check',helper_source(row,candidate),'obj')['accepted']:
            obj=candidate
    dump(out/'checked-object.json',obj)
    print(f"{row['id']}/helper/{i}: checked={obj is not None}",flush=True)

def one_proof(row,arm,i,objects,effort):
    out=ROOT/'rollouts'/row['id']/arm/str(i)
    answer=cli(out,actor_prompt(row,objects),'proof',effort)
    dump(out/'objects.json',objects)
    accepted=False
    if answer and clean(answer['body']):
        accepted=verify(out/'root_check',source(row,answer['body'],objects),'root')['accepted']
    dump(out/'outcome.json',{'accepted':accepted})
    print(f"{row['id']}/{arm}/{i}: accepted={accepted}",flush=True)

def parallel(jobs,workers):
    with cf.ThreadPoolExecutor(max_workers=workers) as pool:
        fs=[pool.submit(fn,*args) for fn,args in jobs]
        for f in cf.as_completed(fs): f.result()

def main():
    p=argparse.ArgumentParser();p.add_argument('stage',choices=['fixtures','discovery','completion','replay']);p.add_argument('--workers',type=int,default=6);a=p.parse_args()
    panel=json.loads((ROOT/'panel.json').read_text())
    if a.stage=='fixtures':
        proofs=json.loads((ROOT/'fixture-proofs.json').read_text())
        for row in panel:
            path=ROOT/'fixtures'/row['id']; code=source(row,proofs[row['id']],[])
            if path.exists():
                assert (path/'source.lean').read_text()==code and json.loads((path/'verdict.json').read_text())['accepted'],row['id']
            else:
                assert verify(path,code,'root')['accepted'],row['id']
        # Controls prove ordinary kernel acceptance, reject unresolved and unallowed axioms.
        row=panel[0]
        for name,body in [('negative','sorry'),('invalid','exact True.intro')]:
            path=ROOT/'fixtures'/name;code=source(row,body,[])
            if path.exists():
                assert (path/'source.lean').read_text()==code and not json.loads((path/'verdict.json').read_text())['accepted']
            else:
                assert not verify(path,code,'root')['accepted']
        dump(ROOT/'runtime.json',{'lean_version':subprocess.check_output([str(LEAN),'--version'],text=True).strip(),
             'lean_binary_sha256':sha(LEAN),'lean_archive_sha256':sha(LEAN.parents[2]/'lean-4.9.0-rc1-darwin_aarch64.tar.zst'),
             'cli_version':subprocess.check_output(['codex','--version'],text=True).strip(),
             'panel_sha256':sha(ROOT/'panel.json'),'runner_sha256':sha(Path(__file__)),
             'git_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=REPO,text=True).strip(),
             'git_status':subprocess.check_output(['git','status','--porcelain'],cwd=REPO,text=True)})
    elif a.stage=='discovery':
        jobs=[]
        for row in panel:
            for i in range(K):
                jobs.extend([(one_helper,(row,i)),(one_proof,(row,'bare_low',i,[],'low')),(one_proof,(row,'direct_medium',i,[],'medium'))])
        parallel(jobs,a.workers)
    elif a.stage=='completion':
        jobs=[]
        for row in panel:
            candidates=[json.loads((ROOT/'rollouts'/row['id']/'helper'/str(i)/'checked-object.json').read_text()) for i in range(K)]
            all_valid=[o for o in candidates if o]
            for i in range(K):
                jobs.extend([(one_proof,(row,'isolated_low',i,[candidates[i]] if candidates[i] else [],'low')),
                             (one_proof,(row,'bundle_low',i,all_valid,'low'))])
        parallel(jobs,a.workers)
    else:
        for row in panel:
            for i in range(K):
                out=ROOT/'rollouts'/row['id']/'bundle_low'/str(i)
                if not json.loads((out/'outcome.json').read_text())['accepted']:continue
                objects=json.loads((out/'objects.json').read_text())
                if len(objects)<2:continue
                body=json.loads((out/'answer.json').read_text())['body']
                verify(out/'replay_bare',source(row,body,[]),'root')
                for o in objects:
                    verify(out/f"replay_without_{o['name']}",source(row,body,[p for p in objects if p!=o]),'root')

if __name__=='__main__':main()
