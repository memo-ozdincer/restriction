#!/usr/bin/env python3
"""Render a local, offline reader for the authenticated diagnostic attempts."""
import argparse
import gzip
import json
from pathlib import Path

p = argparse.ArgumentParser()
p.add_argument('attempts', type=Path)
p.add_argument('output', type=Path)
a = p.parse_args()
with gzip.open(a.attempts, 'rt') as f:
    data = json.load(f)
payload = json.dumps(data, ensure_ascii=False).replace('<', '\\u003c')
page = """<!doctype html><meta charset="utf-8"><title>Deduction versus witness construction · Rollout reader</title>
<style>
*{box-sizing:border-box}body{font:16px/1.5 system-ui;margin:0;background:#f5f7fb;color:#1b2738}
main{max-width:1200px;margin:auto;padding:28px}h1{line-height:1.1}section,article{background:white;border:1px solid #dce2ea;border-radius:12px;margin:12px 0;padding:18px}
pre{font:14px/1.5 ui-monospace,monospace;background:#142136;color:#e4edfc;white-space:pre-wrap;overflow-wrap:anywhere;padding:14px;border-radius:7px}
label{display:inline-block;margin:8px 12px 8px 0}select,input,button{font:inherit;padding:7px;border:1px solid #aeb9c9;border-radius:6px;background:white}
button{cursor:pointer}.good{color:#087345}.bad{color:#af351f}.muted{color:#596b81}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(210px,1fr));gap:10px}
</style><main><h1>Deduction versus witness construction</h1>
<p>Actual archived model proofs. 14 diagnostic statements × 128 samples × four policies. Original Lean labels; no regrading. The selected set includes nested existential claims, so it is not a pure constructive benchmark.</p>
<section><h2>Start here</h2><div class="grid">
<div><button data-root="amc12b_2020_p6">Factorial square</button><p>Known witness n+1 sometimes fails at certification. Compare C0 and C1.</p></div>
<div><button data-root="imo_1993_p5">Function synthesis</button><p>All four policies fail. Look at proposed functions and their constraints.</p></div>
<div><button data-root="algebra_others_exirrpowirrrat">Irrational powers</button><p>Witness must satisfy multiple arithmetic properties simultaneously.</p></div>
<div><button data-root="numbertheory_notequiv2i2jasqbsqdiv8">Counterexample</button><p>A negated universal claim contains a witness-selection operation.</p></div>
<div><button data-root="amc12a_2002_p6">Easy witness</button><p>p=0 or p=1 makes the proof simple. A useful negative control for task classification.</p></div>
</div></section>
<section><label>Statement <select id="root"></select></label><label>Policy <select id="policy"><option value="c0">C0 pristine SFT</option><option value="c1">C1 GRPO</option><option value="c2">C2 soft unlikeliness</option><option value="c3">C3 hard exclusion</option></select></label><label>Outcome <select id="outcome"><option value="">All</option><option>accepted</option><option>rejected</option><option>unresolved</option></select></label><label>Proof contains <input id="query" placeholder="e.g. use (n + 1)"></label><pre id="statement"></pre><div id="counts"></div></section>
<section><div><button id="prev">Previous</button> <span id="position"></span> <button id="next">Next</button></div><div id="results"></div></section></main>
<script id="data" type="application/json">""" + payload + """</script>
<script>
const data=JSON.parse(document.getElementById('data').textContent);
const $=id=>document.getElementById(id); const root=$('root'),policy=$('policy'),outcome=$('outcome'),query=$('query');
Object.keys(data.c0).sort().forEach(k=>{const opt=document.createElement('option');opt.value=k;opt.textContent=k;root.append(opt)});
root.value='amc12b_2020_p6';let page=0;const size=12;
function render(){const k=root.value,r=data[policy.value][k];$('statement').textContent=r.statement;
  let counts=Object.keys(data).map(c=>{const arr=data[c][k].attempts;return c.toUpperCase()+': '+arr.filter(a=>a.outcome==='accepted').length+'/128 accepted'});$('counts').textContent=counts.join('   ·   ');
  let arr=r.attempts.filter(a=>(!outcome.value||a.outcome===outcome.value)&&a.proof.includes(query.value));page=Math.max(0,Math.min(page,Math.ceil(arr.length/size)-1));
  $('position').textContent=arr.length?(page*size+1)+'–'+Math.min((page+1)*size,arr.length)+' of '+arr.length:'No matching attempts';
  $('results').replaceChildren(); for(const a of arr.slice(page*size,(page+1)*size)){const el=document.createElement('article'),h=document.createElement('strong'),pre=document.createElement('pre'); h.textContent=a.outcome+' · '+a.proposal_id;h.className=a.outcome==='accepted'?'good':a.outcome==='rejected'?'bad':'muted';pre.textContent=a.proof;el.append(h,pre);$('results').append(el)} }
for(const el of [root,policy,outcome,query])el.addEventListener('input',()=>{page=0;render()});
document.querySelectorAll('[data-root]').forEach(b=>b.onclick=()=>{root.value=b.dataset.root;page=0;render()});
$('prev').onclick=()=>{page--;render()};$('next').onclick=()=>{page++;render()};render();
</script>"""
a.output.write_text(page)
