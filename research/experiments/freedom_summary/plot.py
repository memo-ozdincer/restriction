"""Plot the completed fixed-task intervention panels."""
import json
from pathlib import Path
from collections import defaultdict
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
def read(path):
    return json.loads((ROOT/path).read_text())

sort=read("freedom_sorting_new/results.json")["runs"]+read("freedom_sorting_new/followup.json")
groups=defaultdict(list)
for row in sort:
    groups[tuple(row["mode"])].append(row["independent_root_hits"]/row["independent_root_trials"])
labels=["tiny","short","radius6","radius8","medium","long","wide"]
radius=[2,4,6,8,12,24,36]
rev=read("freedom_reversible_new/results.json")["records"]
rv=defaultdict(list)
for row in rev:rv[(row["distribution"],row["horizon"],row["switch"])].append(row["final_root_probability"])
fig,axs=plt.subplots(1,2,figsize=(11.8,4.8),constrained_layout=True)
for switch,col,label in [(False,"#4178a4","Continue varied starts"),(True,"#d47935","Switch to ordinary")]:
    assert all(len(groups[(x,12,False,switch)])==8 for x in labels)
    rates=[np.mean(groups[(x,12,False,switch)])*100 for x in labels]
    axs[0].plot(radius,rates,marker="o",lw=2,color=col,label=label)
axs[0].set(title="Sorting: moderate perturbation wins",xlabel="Maximum random comparator-walk length",ylabel="Ordinary-start success (%)",xticks=radius,ylim=(-2,78))
axs[0].legend(frameon=False,loc="upper right")
for mode,col,label in [("goal_walk4","#4178a4","Near-goal walks"),("balanced_shell","#d47935","Balanced distance shells")]:
    xs=[0.1,0.3,0.6,0.9,1.0]
    assert all(len(rv[(mode,8,None if x==1 else x)])==8 for x in xs)
    ys=[100*np.mean(rv[(mode,8,None if x==1 else x)]) for x in xs]
    axs[1].plot(np.array(xs)*100,ys,marker="o",lw=2,color=col,label=label)
axs[1].set(title="Reversible: later specialization wins",xlabel="Training spent on varied starts (%)",ylabel="Ordinary-start success (%)",xticks=[10,30,60,90,100],ylim=(-2,78))
axs[1].legend(frameon=False,loc="upper left")
for ax in axs:
    ax.grid(axis="y",alpha=.22)
    ax.spines[["right","top"]].set_visible(False)
fig.suptitle("Fixed-task terminal-reward training, eight paired seeds per condition",fontsize=13,fontweight="bold")
fig.savefig(Path(__file__).with_name("reset_comparison.png"),dpi=180)
