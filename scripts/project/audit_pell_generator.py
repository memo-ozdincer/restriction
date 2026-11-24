"""Audit matched generator training and execute prospectively fixed fuel ablations."""
import argparse
import json
from pathlib import Path
import re
import sys
import audit_pell_training as core
from train_pell_generator import panel,engine


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('bundle',type=Path);p.add_argument('run',type=Path)
    a=p.parse_args();r=a.run
    core.panel=panel
    sys.argv=[sys.argv[0],str(r),str(r/'core-audit.json')]
    core.main()
    result=json.loads((r/'core-audit.json').read_text())
    assert result['proposals']==384 and result['fixture_checks']==48
    from transformers import AutoTokenizer
    tokenizer=AutoTokenizer.from_pretrained(str(a.bundle/'models/c1-final'),local_files_only=True)
    train,test=panel();primary=[t for t in test if t['discriminant'] in [11,13] and t['level'] in [4,6]]
    for arm in ['literal','expression']:
        tokens=json.loads((r/arm/'tokens.json').read_text())
        for t,x in zip(train,tokens,strict=True):
            assert x['prompt_token_ids']==tokenizer.encode(engine.lean.PREFIX+engine.lean.HEADER+t['statement'])
            assert x['response_token_ids']==tokenizer.encode(t[arm]+'\n```',add_special_tokens=False)
    numeric=not result['unresolved'] and all(result['cells']['expression'][t['id']]['accepted']>=8
        and all(result['cells'][c][t['id']]['accepted']<=1 for c in ['base','literal']) for t in primary)
    verdicts={v['id']:v for v in engine.lean.rows(r/'verdicts.jsonl')}
    pattern=re.compile(r'(?m)^(?P<prefix>[ \t]*let[ \t]+\w+[^\n]*Nat\.rec[^\n]*[ \t]+)(?P<fuel>[0-9]+)(?P<tail>[ \t]*)$')
    jobs=[];selected=[]
    for t in primary:
        batch=json.loads((r/'expression'/(t['id']+'.json')).read_text())
        for row in batch['rows']:
            body,error=engine.lean.completion_code(row['text'])
            if error:continue
            original=engine.lean.HEADER+t['statement']+body+'\n#print axioms target'
            key=engine.lean.sha(original)
            if not verdicts[key]['accepted']:continue
            matches=list(pattern.finditer(body))
            if len(matches)!=1 or int(matches[0]['fuel'])<=2:continue
            m=matches[0];changed=body[:m.start('fuel')]+'2'+body[m.end('fuel'):]
            code=engine.lean.HEADER+t['statement']+changed+'\n#print axioms target'
            identity=engine.lean.sha(code)
            jobs.append(dict(id=identity,code=code,lake=str(a.bundle/'lean/elan/bin/lake'),verifier=str(a.bundle/'verifier/DeepSeek-Prover-V1.5')))
            selected.append(dict(task=t['id'],index=row['sample_index'],original_fuel=int(m['fuel']),
                original_code_sha256=key,ablation_code_sha256=identity))
            break
    engine.lean.write(r/'fuel-ablation-sources.json',jobs)
    engine.lean.write(r/'fuel-ablation-selection.json',selected)
    vs=engine.lean.verify_jobs(jobs,r/'fuel-ablation-verdicts.jsonl',workers=2)
    mechanism=len(vs)==4 and all(not v['accepted'] and not v.get('system_errors') for v in vs)
    result.update(passed=True,numeric_outcome=numeric,mechanism_outcome=mechanism,
        registered_outcome=numeric and mechanism,fuel_ablation_checks=len(vs),selected_generator_proofs=selected,
        fuel_ablation_unresolved=sum(bool(v.get('system_errors')) for v in vs),
        scope='Supervised bounded generator with supplied fundamental unit; no autonomous unit discovery')
    engine.lean.write(r/'independent-audit.json',result)
    print(json.dumps({k:v for k,v in result.items() if k not in ['cells','training']}))


if __name__=='__main__':main()
