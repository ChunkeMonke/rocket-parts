"""Export a RocketPy flight time series for tools/flight_video.py (OR-matched overrides: pack at 300 mm, fin can + cone 113.9 g, CG 31.5 mm, Cd x0.857).
  .venv/bin/python tools/flight_export.py  -> out/video/flight.json"""
import sys, json, numpy as np
sys.path.insert(0,'sims'); import l1_cheap as S, rocketpy
cap={}
class F(rocketpy.Flight):
    def __init__(s,*a,**k): super().__init__(*a,**k); cap['f']=s
S_rp=rocketpy.Flight
import rocketpy as R; R.Flight=F
d=S.load_design(S.DESIGN,[])
for k,v in {"stability.assumptions.recovery_pack_position":300,"stability.fin_can_model_mass_g":113.9,"stability.fin_can_model_cg_from_aft_mm":31.5,"stability.assumptions.cd_scale":0.857}.items(): S._set(d,k,v)
b=S.build(d,True); print("sm",b["sm_liftoff"],"m",b["m_liftoff"],flush=True)
rail=max(S._get(d,"stability.assumptions.rail_lengths_m"))
out=S.simulate(d,b,rail); f=cap['f']
t=np.linspace(0,f.t_final,int(f.t_final*60)+1)
el=S._get(d,"stability.assumptions.launch_site")["elevation_m"]
data=dict(t=t.tolist(),x=[float(f.x(i)) for i in t],y=[float(f.y(i)) for i in t],z=[float(f.z(i))-el for i in t],
 vz=[float(f.vz(i)) for i in t],speed=[float(f.speed(i)) for i in t],mach=[float(f.mach_number(i)) for i in t],
 ax=[float(f.acceleration(i)) for i in t],theta=[float(f.attitude_angle(i)) for i in t],
 t_bo=out['t_burnout'],t_ap=out['t_apogee'],apogee=out['apogee_m'],vmax=out['vmax'],mach_max=out['mach_max'],
 rail_exit=out['rail_exit'], sm=b['sm_liftoff'], m=b['m_liftoff'], wind=S._get(d,"stability.assumptions.wind_m_s"),
 inc=S._get(d,"stability.assumptions.launch_inclination_deg"))
json.dump(data,open('out/video/flight.json','w'))
print({k:data[k] for k in ['t_bo','t_ap','apogee','vmax','mach_max','rail_exit','sm','m','wind','inc']}, 't_final',t[-1], 'max x', max(data['x']))
