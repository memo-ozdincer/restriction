"""Reconstruct the crossed Pell interfaces and reconcile all sampled proof checks."""
import argparse
import json
from pathlib import Path
from train_pell_construction import ALIASES, NAMES, lean, panel


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('run',type=Path)
    p.add_argument('output',type=Path)
    a=p.parse_args();r=a.run
    sources=json.loads((r/'sources.json').read_text())
    vs=lean.rows(r/'verdicts.jsonl');checked={v['id']:v for v in vs}
    assert len(vs)==len(checked)==len(sources) and set(checked)==set(sources)
    for key,v in checked.items():
        assert key==v['code_sha256']==lean.sha(sources[key])
        assert not v.get('system_errors')
        if v['accepted']:
            assert v['lean_complete'] and v['axiom_audit_found'] and set(v['axioms'])<=lean.ALLOWED_AXIOMS
    expected_cells={};counts={};examples={};used=set()
    for t in panel()[1]:
        if t['id'] not in ['d6-level3-named','d10-level3-named']:continue
        decl,root=t['statement'].split('\n\n');lines=decl.splitlines()
        for condition in ['rename_only','reorder_only']:
            newlines=([line.replace(old,new) for line,old,new in zip(lines,NAMES,ALIASES,strict=True)]
                      if condition=='rename_only' else [lines[i] for i in [4,0,1,3,2]])
            source=lean.HEADER+'\n'.join(newlines)+'\n\n'+root
            prefix=t['id'].rsplit('-',1)[0];cell=prefix+'-'+condition
            batch=json.loads((r/(cell+'.json')).read_text())
            assert batch['prompt']==lean.PREFIX+source and len(batch['rows'])==16
            expected_cells[cell]=[];counts[cell]=0
            for i,row in enumerate(batch['rows']):
                assert row['sample_index']==i and row['seed']==20261203+int(lean.sha(prefix)[:6],16)
                body,error=lean.completion_code(row['text']);key=None
                if not error:
                    code=source+body+'\n#print axioms target';key=lean.sha(code)
                    assert sources[key]==code;used.add(key)
                    if checked[key]['accepted']:
                        counts[cell]+=1
                        examples.setdefault(cell,dict(index=i,code_sha256=key,body=body))
                expected_cells[cell].append(dict(index=i,key=key,error=error))
    assert used==set(sources)
    assert expected_cells==json.loads((r/'cells.json').read_text())
    summary=json.loads((r/'audit.json').read_text())
    assert counts==summary['counts'] and summary['reload_max_abs']<=1e-4
    lean.write(a.output,dict(passed=True,proposals=64,physical_checks=len(checked),unresolved=0,
        counts=counts,reload_max_abs=summary['reload_max_abs'],first_accepted_examples=examples,
        scope='Crossed test interfaces on the same saved expression adapter; no new training'))


if __name__=='__main__':main()
