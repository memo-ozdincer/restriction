import json
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
folder=Path(__file__).resolve().parent
x=json.loads((folder/'results.json').read_text())
fig,axes=plt.subplots(2,2,figsize=(10,6.8),sharex=True,sharey=True)
for ax,row in zip(axes.flat,sorted(x['rows'],key=lambda r:r['seed'])):
    ax.axvspan(11.5,12.5,ymin=0,ymax=8/15,color='#4c566a')
    ax.axvspan(11.5,12.5,ymin=14/15,ymax=1,color='#4c566a')
    for label,ev,color,style in [('Common',row['baseline'],'#777777','--'),('Ordinary final',row['arms']['ordinary']['final'],'#d55e00',':'),('Exposure midpoint',row['arms']['random']['mid'],'#0072b2','-'),('Exposure final',row['arms']['random']['final'],'#009e73','-.')]:
        idx=ev['maps'].index(7);states=np.array(ev['path'])[:,0,idx];states=states[:min(ev['finish_times'][idx],50)]
        pos=np.r_[1,states//49//15];y=np.r_[7,states//49%15]
        ax.plot(pos,y,style,color=color,label=label,linewidth=2,marker='.',markersize=3)
    ax.scatter([1],[7],color='black',s=23,zorder=9);ax.axvline(23,color='#888',alpha=.6)
    ax.set_title(f"Seed {row['seed']}");ax.set_xlim(-.5,23.5);ax.set_ylim(-.5,14.5);ax.set_aspect('equal');ax.grid(alpha=.12)
fig.suptitle('Held-out barrier gap: same entrance and evaluation noise',fontsize=14)
fig.legend(*axes.flat[0].get_legend_handles_labels(),loc='lower center',ncol=4,frameon=False)
fig.supxlabel('Horizontal position',y=.06);fig.supylabel('Vertical position');fig.tight_layout(rect=[0,.1,1,.95])
fig.savefig(folder/'heldout_paths.png',dpi=150,bbox_inches='tight')
