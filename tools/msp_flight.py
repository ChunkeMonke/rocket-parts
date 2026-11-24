"""Ms. Piggy flight simulation on the CFD aerodynamic database (out/msp/aero.json).

  .venv/bin/python tools/msp_flight.py

6-DOF RocketPy ascent to deployment with the CFD axial-force curve (power-off; power-on = power-off minus the CFD
base drag), the H100W thrust curve and the ESTIMATED mass model (liftoff 610 g, CG 763.3 mm without added ballast).
Static margin over the flight uses the CFD centre of pressure CP(Mach) and the simulated CG(t); RocketPy's own
Barrowman margin is reported for comparison. Descent on the LOC 28 in parachute is analytic (recovery analysis).
Writes out/msp/flight.json and figures in projects/l1-cheap/report/figures/msp/.
"""
import json
import math
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import yaml
from rocketpy import Environment, Flight, GenericMotor, Rocket

ROOT = Path(__file__).resolve().parent.parent
FIG = ROOT / "projects/l1-cheap/report/figures/msp"
D = 0.041275
TIP = 1048.3                      # nose-tip z in the assembly frame (fin-can aft face z = 0), mm
L = 1078.3
M0, CG0 = 610.0, 763.3            # liftoff mass / CG without added ballast (ESTIMATE, EDR §2.5)
M_MOT, M_PROP = 261.0, 121.0
X_MOT_AFT, X_MOT_FWD = TIP - 8.4, TIP - 173.4     # motor nozzle / forward end from the tip, mm
X_BALLAST = 74.6
DELAY = 12.0
RAIL = 1.83
V_DESC = 5.35                     # m/s, LOC 28 in, 514 g (recovery analysis)


def build(ballast_g, aero, base, drag_k=1.0):
    x_mot = (X_MOT_AFT + X_MOT_FWD) / 2
    m_tot = M0 + ballast_g
    cg_tot = (M0 * CG0 + ballast_g * X_BALLAST) / m_tot
    m_s = m_tot - M_MOT
    x_s = (m_tot * cg_tot - M_MOT * x_mot) / m_s
    eng = ROOT / "projects/l1-cheap/motor/H100W.eng"
    mlen, r_ch, dry = (X_MOT_AFT - X_MOT_FWD) / 1000, 0.019, (M_MOT - M_PROP) / 1000
    motor = GenericMotor.load_from_eng_file(
        str(eng), nozzle_radius=0.007, chamber_radius=r_ch, chamber_height=mlen, chamber_position=mlen / 2,
        center_of_dry_mass_position=mlen / 2, dry_mass=dry, propellant_initial_mass=M_PROP / 1000,
        dry_inertia=(dry * (mlen ** 2 / 12 + r_ch ** 2 / 4),) * 2 + (dry * r_ch ** 2 / 2,),
        coordinate_system_orientation="nozzle_to_combustion_chamber")
    mach = [r["mach"] for r in aero["mach"]]
    ca0 = [r["CA0"] for r in aero["mach"]]
    off = [[0.0, ca0[0] * drag_k]] + [[m, c * drag_k] for m, c in zip(mach, ca0)] + [[1.2, ca0[-1] * drag_k]]
    on = [[m, max(c - base, 0.05)] for m, c in off]
    I_lat = m_s / 1000 * (L / 1000) ** 2 / 12
    rkt = Rocket(radius=D / 2, mass=m_s / 1000, inertia=(I_lat, I_lat, 0.5 * m_s / 1000 * (D / 2) ** 2),
                 power_off_drag=off, power_on_drag=on, center_of_mass_without_motor=x_s / 1000,
                 coordinate_system_orientation="nose_to_tail")
    rkt.add_motor(motor, position=X_MOT_AFT / 1000)
    rkt.add_nose(length=0.1634, kind="tangent", position=0)
    rkt.add_tail(top_radius=D / 2, bottom_radius=0.0234, length=0.0405, position=(TIP - 158.5) / 1000, name="fairing")
    rkt.add_trapezoidal_fins(n=3, root_chord=0.052, tip_chord=0.030, span=0.0461, position=(TIP - 67.3) / 1000,
                             sweep_length=0.0188, radius=0.0234)
    rkt.add_tail(top_radius=0.0234, bottom_radius=0.0208, length=0.0299, position=TIP / 1000, name="tail cone")
    return rkt, motor, cg_tot


def fly(rkt, wind_ms=0.0, incl=90.0):
    env = Environment(latitude=28.03, longitude=-80.59, elevation=0)
    if wind_ms:
        env.set_atmospheric_model(type="custom_atmosphere", pressure=None, temperature=None, wind_u=wind_ms, wind_v=0)
    return Flight(rocket=rkt, environment=env, rail_length=RAIL, inclination=incl, heading=90,
                  terminate_on_apogee=False, max_time=2.6 + 18, verbose=False)


def main():
    FIG.mkdir(parents=True, exist_ok=True)
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 9})
    aero = json.load(open(ROOT / "out/msp/aero.json"))
    base = aero.get("ca_base_M029", 0.0)
    cp_m = [(r["mach"], r["CP_mm"]) for r in aero["mach"] if "CP_mm" in r]
    cp_of = lambda m: float(np.interp(m, [a for a, _ in cp_m], [b for _, b in cp_m]))  # noqa: E731
    cp_low = cp_m[0][1]
    ball = {"no added ballast": 0.0}
    for sm in (1.7, 1.8):
        tgt = cp_low - sm * D * 1000
        ball[f"{sm} cal at liftoff"] = max(0.0, M0 * (CG0 - tgt) / (tgt - X_BALLAST))
    out = {"inputs": dict(M0=M0, CG0=CG0, delay=DELAY, rail=RAIL, cp_by_mach=cp_m, ca_base=base,
                          drag=[(r["mach"], r["CA0"]) for r in aero["mach"]]), "cases": []}
    series = {}
    for lab, b in ball.items():
        rkt, motor, cg_tot = build(b, aero, base)
        f = fly(rkt)
        t_bo = float(motor.burn_out_time)
        t = np.linspace(0, f.t_final, 600)
        mach = np.array([f.mach_number(x) for x in t])
        cg_t = np.array([rkt.center_of_mass(x) for x in t]) * 1000
        sm_cfd = (np.array([cp_of(m) for m in mach]) - cg_t) / (D * 1000)
        sm_bar = np.array([rkt.static_margin(x) for x in t])
        t_dep = t_bo + DELAY
        rec = dict(case=lab, ballast_g=b, liftoff_g=M0 + b, cg_mm=cg_tot,
                   apogee_m=float(f.apogee), apogee_ft=float(f.apogee) / 0.3048, t_apogee=float(f.apogee_time),
                   vmax=float(f.max_speed), mach_max=float(f.max_mach_number), amax_g=float(f.max_acceleration) / 9.81,
                   rail_exit=float(f.out_of_rail_velocity), t_burnout=t_bo, t_deploy=t_dep,
                   v_deploy=float(f.speed(t_dep)), max_q_kpa=float(f.max_dynamic_pressure) / 1000,
                   sm_cfd_liftoff=float(sm_cfd[0]), sm_cfd_min_powered=float(sm_cfd[t <= t_bo].min()),
                   sm_cfd_burnout=float(np.interp(t_bo, t, sm_cfd)), sm_barrowman_liftoff=float(sm_bar[0]),
                   t_descent=float(f.apogee) / V_DESC, ideal_delay_s=float(f.apogee_time) - t_bo)
        out["cases"].append(rec)
        series[lab] = dict(t=t, z=np.array([f.z(x) for x in t]), v=np.array([f.speed(x) for x in t]),
                           a=np.array([f.acceleration(x) for x in t]) / 9.81, mach=mach, sm=sm_cfd, sm_bar=sm_bar,
                           cg=cg_t, t_bo=t_bo)
        print(f"{lab:20s} +{b:5.1f} g  apogee {rec['apogee_m']:.0f} m  vmax {rec['vmax']:.0f} m/s M{rec['mach_max']:.2f} "
              f"rail {rec['rail_exit']:.1f} m/s  SM(CFD) lift-off {rec['sm_cfd_liftoff']:.2f} burnout {rec['sm_cfd_burnout']:.2f} "
              f"Barrowman {rec['sm_barrowman_liftoff']:.2f}  v_dep {rec['v_deploy']:.1f}")
    # drag sensitivity on the 1.8 cal configuration
    out["drag_band"] = []
    for k in (0.85, 1.0, 1.15, 1.40):
        rkt, motor, _ = build(ball["1.8 cal at liftoff"], aero, base, drag_k=k)
        f = fly(rkt)
        t_bo = float(motor.burn_out_time)
        out["drag_band"].append(dict(drag_factor=k, apogee_m=float(f.apogee), apogee_ft=float(f.apogee) / 0.3048,
                                     vmax=float(f.max_speed), mach_max=float(f.max_mach_number),
                                     t_apogee=float(f.apogee_time), ideal_delay_s=float(f.apogee_time) - t_bo,
                                     v_deploy_12s=float(f.speed(t_bo + DELAY)),
                                     v_deploy={d: float(f.speed(t_bo + d)) for d in (11, 12, 13, 14)}))
        print(f"drag x{k:.2f}: apogee {f.apogee:.0f} m, M {f.max_mach_number:.2f}, ideal delay {f.apogee_time - t_bo:.1f} s, "
              f"v at 12 s {f.speed(t_bo + DELAY):.1f} m/s")
    # wind cases on the 1.8 cal configuration
    lab18 = "1.8 cal at liftoff"
    rkt, motor, _ = build(ball[lab18], aero, base)
    out["wind"] = []
    for mph in (0, 5, 10, 15, 20):
        w = mph * 0.44704
        f = fly(rkt, wind_ms=w)
        x_ap = float(f.x(f.apogee_time))
        out["wind"].append(dict(wind_mph=mph, apogee_m=float(f.apogee), x_apogee_m=x_ap,
                                aoa_max_deg=float(max(abs(f.angle_of_attack(x)) for x in np.linspace(f.out_of_rail_time + 0.05, 2.4, 60))),
                                landing_x_m=x_ap + w * float(f.apogee) / V_DESC))
        print(f"wind {mph:2d} mph: apogee {f.apogee:.0f} m, apogee offset {x_ap:+.0f} m, landing {out['wind'][-1]['landing_x_m']:+.0f} m")
    json.dump(out, open(ROOT / "out/msp/flight.json", "w"), indent=1, default=float)

    # ---------------- figures
    sty = {"no added ballast": ":", "1.7 cal at liftoff": "--", "1.8 cal at liftoff": "-"}
    s18 = series[lab18]
    fig, ax = plt.subplots(3, 1, figsize=(7, 7.2), sharex=True)
    ax[0].plot(s18["t"], s18["z"], "k"); ax[0].set_ylabel("altitude (m)")
    ax[1].plot(s18["t"], s18["v"], "k"); ax[1].set_ylabel("speed (m/s)")
    ax1b = ax[1].twinx(); ax1b.plot(s18["t"], s18["mach"], "k--", lw=0.8); ax1b.set_ylabel("Mach (dashed)")
    ax[2].plot(s18["t"], s18["a"], "k"); ax[2].set_ylabel("acceleration (g)"); ax[2].set_xlabel("time (s)")
    for a in ax:
        a.axvline(s18["t_bo"], color="0.6", lw=0.8); a.axvline(s18["t_bo"] + DELAY, color="0.6", lw=0.8, ls="--"); a.grid(alpha=.3)
    ax[0].text(s18["t_bo"] + 0.2, 100, "burnout", fontsize=7.5); ax[0].text(s18["t_bo"] + DELAY + 0.2, 100, "ejection", fontsize=7.5)
    fig.suptitle("Flight profile to ejection (1.8 cal ballast case, no wind)", fontsize=10)
    fig.tight_layout(); fig.savefig(FIG / "flight_profile.png", dpi=180); plt.close(fig)

    fig, ax = plt.subplots(figsize=(7, 3.6))
    for lab, s in series.items():
        m = s["t"] <= s["t_bo"] + DELAY
        ax.plot(s["t"][m], s["sm"][m], "k", ls=sty[lab], label=f"{lab} (+{ball[lab]:.1f} g)")
    ax.axhline(1.7, color="0.4", lw=0.8); ax.axhline(1.8, color="0.4", lw=0.8, ls="--")
    ax.text(0.2, 1.72, "1.7 minimum", fontsize=7.5); ax.text(0.2, 1.82, "1.8 target", fontsize=7.5)
    ax.axvline(series[lab18]["t_bo"], color="0.6", lw=0.8)
    ax.set_xlabel("time (s)"); ax.set_ylabel("static margin (cal), CFD CP"); ax.grid(alpha=.3); ax.legend(fontsize=7.5)
    ax.set_title("Static margin during flight: CFD CP(Mach) against simulated CG(t)", fontsize=10)
    fig.tight_layout(); fig.savefig(FIG / "margin_vs_time.png", dpi=180); plt.close(fig)

    fig, ax = plt.subplots(1, 2, figsize=(9, 3.2))
    W = out["wind"]
    ax[0].plot([w["wind_mph"] for w in W], [w["apogee_m"] for w in W], "ko-"); ax[0].set_xlabel("wind (mph)")
    ax[0].set_ylabel("apogee (m)"); ax[0].grid(alpha=.3); ax[0].set_title("Apogee vs wind (weathercocking)", fontsize=9)
    ax[1].plot([w["wind_mph"] for w in W], [w["landing_x_m"] for w in W], "ko-", label="landing")
    ax[1].plot([w["wind_mph"] for w in W], [w["x_apogee_m"] for w in W], "ks--", ms=3, label="apogee position")
    ax[1].set_xlabel("wind (mph)"); ax[1].set_ylabel("downwind distance (m)"); ax[1].legend(fontsize=7.5); ax[1].grid(alpha=.3)
    ax[1].set_title("Apogee and landing position vs wind", fontsize=9)
    fig.tight_layout(); fig.savefig(FIG / "wind_cases.png", dpi=180); plt.close(fig)
    print(json.dumps(out["cases"], indent=1, default=float)[:2500])


if __name__ == "__main__":
    main()
