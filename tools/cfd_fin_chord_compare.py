import sys, json, math, numpy as np
sys.path.insert(0,'tools'); import cfd_post as P
from pathlib import Path
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
q=0.5*100**2
fig,ax=plt.subplots(1,3,figsize=(16,4.8),sharey=True)
for name,col,lab in [('r9a4','#9a9a9a','rev 9 reference'),('own_a4','#000000','SolidWorks fin can')]:
    case=Path(f'out/cfd/of_{name}'); c=json.load(open(case/'case.json'))
    pts,polys,d=P.read(case/'VTKL'/'rocket'/f"rocket_{c['t_last']}.vtk"); Av,C=P.face_geom(pts,polys)
    cp=d['p']/q; x=C[:,0]*1000; r=np.hypot(C[:,1],C[:,2])*1000; th=np.arctan2(C[:,1],C[:,2])
    et=np.stack([np.zeros_like(th),np.cos(th),-np.sin(th)],1)   # tangential dir (+theta)
    nt=(Av*et).sum(1)/np.linalg.norm(Av,axis=1)
    fin1=(np.degrees(th)>100)&(np.degrees(th)<140)
    for a,rr in zip(ax,[30,45,60]):
        m=fin1&(abs(r-rr)<2.5)
        for s,ls in [(1,'-'),(-1,'--')]:
            mm=m&(s*nt>0.8); o=np.argsort(x[mm])
            a.plot(x[mm][o],cp[mm][o],ls,color=col,lw=1.4,label=f"{lab}, {'face +θ' if s>0 else 'face −θ'}")
        a.set_title(f'fin 1 pressure along the chord at r = {rr} mm')
for a in ax: a.invert_yaxis(); a.grid(alpha=.3); a.set_xlabel('x from nose tip (mm)')
ax[0].set_ylabel('Cp (up = suction)'); ax[0].legend(fontsize=8)
fig.tight_layout(); fig.savefig('projects/l1-cheap/report/figures/cfd/owner/cfd_fin_chord_pressure.png',dpi=110)
