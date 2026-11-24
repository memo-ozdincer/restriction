"""Check sequential backward equivalence and the context-gradient directions."""
import json
import torch
from train_hindsight_contracts import part_loss

results=[]
for contrast in [False,True]:
    p=torch.tensor([-2.,-1.3,-.7],requires_grad=True);n=torch.tensor([-1.1,-2.,-.4],requires_grad=True)
    rp=torch.tensor([-1.9,-1.4,-.8]);rn=torch.tensor([-1.,-1.9,-.5])
    joint=-p.mean()+float(contrast)*torch.nn.functional.softplus(1-((p.mean()-rp.mean())-(n.mean()-rn.mean())))+.01*((p-rp).square().mean()+(n-rn).square().mean())
    gp,gn=torch.autograd.grad(joint,[p,n])
    pl,_,_=part_loss(p,rp,n.detach().mean(),rn.mean(),True,contrast)
    nl,_,_=part_loss(n,rn,p.detach().mean(),rp.mean(),False,contrast)
    hp,hn=torch.autograd.grad(pl+nl,[p,n])
    assert torch.allclose(gp,hp,atol=1e-7,rtol=0) and torch.allclose(gn,hn,atol=1e-7,rtol=0)
    if contrast:assert (gp<0).all() and (gn>0).all()
    results.append(dict(contrast=contrast,positive_gradient_max_abs=float((gp-hp).abs().max()),negative_gradient_max_abs=float((gn-hn).abs().max())))
print(json.dumps(dict(passed=True,cases=results),indent=2))
