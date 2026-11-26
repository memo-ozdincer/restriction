"""Freeze handoff payloads and independently authenticate helper facts."""
import json
import textwrap
from pathlib import Path
from verify import ROOT,verify

panel=json.loads((ROOT/'panel.json').read_text())
selection=json.loads((ROOT/'selection.json').read_text())['checks']
ideas={}; medium={}; facts={}; fact_audit=[]
for r in panel:
    n=r['id']
    for arm,out in [('luna-low',ideas),('luna-medium',medium)]:
        m=json.loads((ROOT/'rollouts'/arm/n/'metadata.json').read_text())
        assert m['valid'] and not m['tool_items']
        a=json.loads((ROOT/'rollouts'/arm/n/'answer.json').read_text())
        if not m['verification']['accepted']:out[n]=a['idea']
    teacher=json.loads((ROOT/'rollouts/terra-high'/n/'answer.json').read_text())
    tm=json.loads((ROOT/'rollouts/terra-high'/n/'metadata.json').read_text())
    typ,body=teacher['insight_statement'],teacher['insight_proof']
    ar=dict(task=n,teacher_root_accepted=tm['verification']['accepted'],type=typ,proof=body)
    if not typ or not body:
        ar.update(eligible=False,reason='empty')
    else:
        # Use authenticated archived witness, clear added fact before continuing.
        k=next(i for i,x in enumerate([x for x in selection if x['name']==n]) if x['accepted'])
        src=(ROOT/'selection-checks'/n/str(k)/'candidate.lean').read_text()
        witness=src.split(r['statement'].rstrip()+'\n',1)[1].split('\n#print axioms ',1)[0]
        result=verify(r['statement'],n,'clear h_help\n'+textwrap.dedent(witness),ROOT/'fact-checks'/n,(typ,body))
        ar.update(eligible=result['accepted'],verification=result)
        if result['accepted']:facts[n]=[typ,body]
    fact_audit.append(ar)
for fname,data in [('low-ideas.json',ideas),('medium-divergent-ideas.json',{k:medium[k] for k in ['mathd_numbertheory_457','mathd_algebra_156','mathd_numbertheory_521']}),('verified-teacher-facts.json',facts),('fact-audit.json',fact_audit)]:
    (ROOT/fname).write_text(json.dumps(data,indent=2,ensure_ascii=False)+'\n')
print('full low',len(ideas),'medium divergent',3,'verified facts',list(facts))
