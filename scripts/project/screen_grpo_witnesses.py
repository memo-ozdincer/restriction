"""Select literal-witness support on discovery proposals before opening reserved groups."""
import argparse
from collections import Counter, defaultdict
import hashlib
import json
from pathlib import Path
import re

BINDER = re.compile(r':\s*∃\s+(?:\(\s*)?(\w+)(?:\s+\w+)*\s*:\s*([ℕℤℚℝ])\s*[),]')
LITERAL = re.compile(r"^\s*(?:use\s+(\d+)(?=\s*(?:,|\n|$))|(?:refine'?|exact)\s+⟨\s*(\d+)\s*,)")


def stats(rows):
    counts=Counter(r['witness'] for r in rows if r['witness'] is not None)
    return dict(counts=dict(counts),accepted=sum(r['correct'] for r in rows))


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('log',type=Path)
    p.add_argument('output',type=Path)
    a=p.parse_args()
    groups=defaultdict(dict)
    digest=hashlib.sha256()
    with a.log.open('rb') as f:
        for line in f:
            digest.update(line)
            row=json.loads(line)
            stmt=row['theorem_statement']
            # The theorem conclusion begins after the last top-level binder.
            conclusion=stmt.split(':= by')[0]
            matches=list(BINDER.finditer(conclusion))
            if len(matches)!=1 or matches[0].start()!=conclusion.find(':', conclusion.rfind(')',0,matches[0].start())+1):
                continue
            key=row['theorem_name'];i=row['candidate_index']
            if i in groups[key]:
                continue
            m=LITERAL.match(row['proof']) if row['correct'] else None
            groups[key][i]=dict(witness=int(m[1] or m[2]) if m else None,correct=row['correct'],statement=stmt,
                                proof=row['proof'],proposal_id=row['proposal_id'])
    assert digest.hexdigest()=='1db715569b8d1d8d7abf558bfd0c0c9b59779fd2ae7e959af0a31f0bb622d9f0'
    eligible=[]
    for name,rows in groups.items():
        if set(rows)!=set(range(32)):continue
        first=stats([rows[i] for i in range(16)])
        ranked=sorted(first['counts'].values(),reverse=True)
        if len(ranked)>=2 and ranked[0]>=2 and ranked[0]>ranked[1]:
            eligible.append(name)
    panel=[]
    for name in sorted(eligible,key=lambda k:hashlib.sha256(k.encode()).digest())[:8]:
        rows=groups[name]
        panel.append(dict(name=name,statement=rows[0]['statement'],discovery=stats([rows[i] for i in range(16)]),
                          confirmation=stats([rows[i] for i in range(16,32)]),
                          examples={r['witness']:r['proof'] for r in rows.values() if r['witness'] is not None}))
    a.output.write_text(json.dumps(dict(log_sha256=digest.hexdigest(),eligible=len(eligible),panel=panel),indent=2)+'\n')


if __name__=='__main__':
    main()
