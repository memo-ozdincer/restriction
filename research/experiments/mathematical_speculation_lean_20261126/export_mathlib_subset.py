"""Read only pinned compiled Lean modules on cluster; export transitive imports."""
import sys, pathlib, re, tarfile, hashlib, json, io, os
base=pathlib.Path('/scratch/memoozd/rrl/restriction-rl/verifier/DeepSeek-Prover-V1.5/mathlib4')
roots=[base]+sorted((base/'.lake/packages').iterdir())
core=('Init','Lean','Lake')
requested=['Mathlib.Data.Real.Basic','Mathlib.Tactic.Ring','Mathlib.Tactic.Linarith','Mathlib.Tactic.NormNum','Mathlib.Tactic.Positivity','Mathlib.Tactic.FieldSimp','Aesop','Mathlib.Algebra.BigOperators.Group.Finset','Mathlib.Algebra.BigOperators.Ring','Mathlib.Data.Complex.Basic','Mathlib.Data.Nat.Factorial.Basic','Mathlib.Data.Nat.Prime','Mathlib.Tactic.IntervalCases','Mathlib.Tactic.Contrapose','Mathlib.Tactic.PushNeg','Mathlib.Tactic.LinearCombination']
seen=set()
files={}
def visit(mod):
    if mod in seen or mod.split('.')[0] in core:return
    seen.add(mod)
    rel=pathlib.Path(*mod.split('.'))
    for root in roots:
        src=root/(str(rel)+'.lean')
        compiled=root/'.lake/build/lib'/(str(rel)+'.olean')
        if src.is_file() and compiled.is_file():
            files[str(rel)+'.olean']=compiled
            text=src.read_text(errors='replace')
            # All imports in the ordinary header. Strip nested Lean comments.
            text=re.sub(r'/-(?:(?!/-|-/).)*-/', '',text,flags=re.S)
            while '/-' in text:
                newer=re.sub(r'/-(?:(?!/-|-/).)*-/', '',text,flags=re.S)
                if newer==text:break
                text=newer
            for line in text.splitlines():
                if not line.strip() or line.lstrip().startswith('--') or line.strip()=='prelude':continue
                m=re.match(r'^\s*import\s+([^\n]+)',line)
                if m:
                    for dep in m.group(1).split('--')[0].split():
                        if re.fullmatch(r"[\w.!']+",dep):visit(dep)
                else:break
            return
    raise RuntimeError('missing dependency '+mod)
for m in requested:visit(m)
total=sum(p.stat().st_size for p in files.values())
if '--dry' in sys.argv:
    print(len(files),total)
else:
    manifest={'modules':requested,'files':[],'size':total}
    with tarfile.open(fileobj=sys.stdout.buffer,mode='w|gz') as tar:
        for name,p in sorted(files.items()):
            h=hashlib.sha256(p.read_bytes()).hexdigest()
            manifest['files'].append({'path':name,'sha256':h,'size':p.stat().st_size})
            if globals().get('existing',{}).get(name)!=h:tar.add(p,arcname=name,recursive=False)
        data=json.dumps(manifest,indent=2).encode();info=tarfile.TarInfo('manifest.json');info.size=len(data);tar.addfile(info,io.BytesIO(data))
