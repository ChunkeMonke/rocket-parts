"""Recovery analysis, LOC Precision 28 in parachute (84 mm spill hole, 8 lines): descent rate, landing energy, opening load, shock-cord snatch, drift,
deployment speed vs actual delay.

  .venv/bin/python tools/recovery_analysis.py

Inputs: design.yaml (recovery, motor), out/msp/flight_series.json (RocketPy on the CFD drag, L1C-CFD-002; 13 s delay).
Writes projects/l1-cheap/report/figures/recovery/*.png and recovery_results.json.
"""
import json
import math
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import yaml

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "projects/l1-cheap/report/figures/recovery"
G = 9.80665
RHO = 1.20            # Palm Bay, mid-December, near sea level, ~20 °C (ISA sea level 1.225)
D_IN = 28.0
D = D_IN * 0.0254
D_SPILL = 0.084       # LOC Precision 28 in parachute: 84 mm spill hole, 8 shroud lines (vendor listing)
A = math.pi * (D ** 2 - D_SPILL ** 2) / 4
CD = {"low (0.60)": 0.60, "nominal (0.75)": 0.75, "high (0.90)": 0.90}
CX = 1.6              # opening-force coefficient, flat circular canopy, infinite-mass upper bound (Knacke)
KEV_RATED = 3336.0    # 750 lb hollow-braid Kevlar
KNOT_EFF = 0.40       # figure-8 knot efficiency (aramid study); cord ends are knotted (design decision 2026-11-23)
EA_KEV = 65e3         # N, axial stiffness of the 2.3 mm braid (E ≈ 70 GPa on ≈ 0.93 mm² load-bearing area)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    d = yaml.safe_load((ROOT / "projects/l1-cheap/design.yaml").read_text())
    prop = float(d["motor"]["propellant_mass_g"])
    liftoff = float(d["owner_design"]["liftoff_mass_g"]["value"])
    cases = {"no added ballast": liftoff - prop, "+6.4 g ballast": liftoff + 6.4 - prop, "+10.2 g ballast": liftoff + 10.2 - prop}
    nose = {"no added ballast": 65.0, "+6.4 g ballast": 71.4, "+10.2 g ballast": 75.2}
    L_cord = 3 * 1.0774 + 0.3            # 3 x rocket length + loop allowance
    F = json.load(open(ROOT / "out/msp/flight_series.json"))
    t, v, z = map(np.array, (F["t"], F["speed"], F["z"]))
    apogee, t_bo = float(F["apogee"]), float(F["t_bo"])

    res = {"inputs": {"chute_d_in": D_IN, "spill_d_m": D_SPILL, "area_m2": A, "rho": RHO, "cd": CD, "cx": CX, "propellant_g": prop,
                      "liftoff_g": liftoff, "cord_length_m": L_cord, "apogee_m": apogee}}
    # 1. descent rate and landing energy
    rows = []
    for k, m in cases.items():
        for cn, cd in CD.items():
            vd = math.sqrt(2 * m / 1000 * G / (RHO * cd * A))
            ke_body = 0.5 * (m - nose[k]) / 1000 * vd ** 2
            ke_nose = 0.5 * nose[k] / 1000 * vd ** 2
            rows.append(dict(case=k, mass_g=m, cd=cd, v=vd, v_fps=vd / 0.3048, t_desc=apogee / vd,
                             ke_body_j=ke_body, ke_nose_j=ke_nose, ke_body_ftlbf=ke_body / 1.3558))
    res["descent"] = rows
    # 2. deployment speed vs actual delay (nominal 13 s, ±1.5 s motor-delay tolerance band shown)
    delays = np.arange(10.0, 16.01, 0.5)
    vdep = [float(np.interp(t_bo + dl, t, v)) for dl in delays]
    res["deploy"] = [dict(delay=float(a), t=float(t_bo + a), v=b) for a, b in zip(delays, vdep)]
    # 3. opening load (upper bound) at deploy speed, nominal Cd
    m_des = cases["+10.2 g ballast"] / 1000
    fo = [0.5 * RHO * vv ** 2 * CD["nominal (0.75)"] * A * CX + m_des * G for vv in vdep]
    res["opening"] = [dict(delay=float(a), v=float(b), F_open_N=float(c)) for a, b, c in zip(delays, vdep, fo)]
    # 4. shock-cord snatch (energy method): nose vs body separating at dv after ejection
    mu = (0.0752 * (m_des - 0.0752)) / m_des
    k = EA_KEV / L_cord
    snatch = [dict(dv=dv, F_N=math.sqrt(2 * 0.5 * mu * dv ** 2 * k)) for dv in (5, 10, 15, 20)]
    res["snatch"] = dict(mu_kg=mu, k_N_per_m=k, cases=snatch)
    # 5. drift from apogee (vertical flight, constant wind, descent at nominal rate)
    vnom = [r for r in rows if r["case"] == "+10.2 g ballast" and r["cd"] == 0.75][0]["v"]
    winds_mph = [0, 5, 10, 15, 20]
    res["drift"] = [dict(wind_mph=w, wind_ms=w * 0.44704, drift_m=w * 0.44704 * apogee / vnom,
                         drift_ft=w * 0.44704 * apogee / vnom / 0.3048) for w in winds_mph]
    res["limits"] = dict(kevlar_rated_N=KEV_RATED, kevlar_knotted_N=KEV_RATED * KNOT_EFF,
                         rec_descent_fps=[15, 20], ke_guideline_ftlbf=75)
    json.dump(res, open(OUT / "recovery_results.json", "w"), indent=1)

    # ---------------- figures (monochrome)
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 9})
    ls = {"no added ballast": ":", "+6.4 g ballast": "--", "+10.2 g ballast": "-"}
    # fig 1: descent rate vs descent mass for Cd band
    fig, ax = plt.subplots(figsize=(7, 3.8))
    mm = np.linspace(420, 560, 50)
    for (cn, cd), sty in zip(CD.items(), (":", "-", "--")):
        ax.plot(mm, np.sqrt(2 * mm / 1000 * G / (RHO * cd * A)), "k", ls=sty, label=f"Cd {cd:.2f}")
    ax.axhspan(15 * 0.3048, 20 * 0.3048, color="0.88", zorder=0, label="common target 15–20 ft/s")
    for kname, m in cases.items():
        ax.axvline(m, color="0.5", lw=0.7); ax.text(m + 1, 6.85, kname, rotation=90, fontsize=7, va="top", color="0.3")
    ax.set_xlabel("descent mass (g)"); ax.set_ylabel("descent rate (m/s)"); ax.set_ylim(3.5, 7)
    ax.grid(alpha=.3); ax.legend(fontsize=7.5, loc="lower right")
    ax.set_title("28 in parachute: steady descent rate vs descent mass", fontsize=10)
    fig.tight_layout(); fig.savefig(OUT / "descent_rate.png", dpi=180); plt.close(fig)
    # fig 2: deploy speed and opening load vs actual delay
    fig, ax = plt.subplots(figsize=(7, 3.8)); ax2 = ax.twinx()
    ax.plot(delays, vdep, "k-", marker="o", ms=3, label="speed at deployment")
    ax2.plot(delays, fo, "k--", label="opening load (upper bound)")
    ax.axvspan(11.5, 14.5, color="0.9", zorder=0); ax.axvline(13, color="k", lw=0.8)
    ax.text(13.05, max(vdep) * 0.95, "13 s nominal\n±1.5 s band", fontsize=7.5)
    ax.set_xlabel("actual ejection delay after burnout (s)"); ax.set_ylabel("speed at deployment (m/s)")
    ax2.set_ylabel("opening load (N)"); ax.grid(alpha=.3)
    h1, l1 = ax.get_legend_handles_labels(); h2, l2 = ax2.get_legend_handles_labels()
    ax.legend(h1 + h2, l1 + l2, fontsize=7.5, loc="upper left")
    ax.set_title("Deployment speed and opening load vs ejection delay", fontsize=10)
    fig.tight_layout(); fig.savefig(OUT / "deploy_vs_delay.png", dpi=180); plt.close(fig)
    # fig 3: drift
    fig, ax = plt.subplots(figsize=(7, 3.2))
    ax.bar([str(r["wind_mph"]) for r in res["drift"]], [r["drift_m"] for r in res["drift"]], color="0.35")
    for i, r in enumerate(res["drift"]):
        ax.text(i, r["drift_m"] + 30, f'{r["drift_m"]:.0f} m\n({r["drift_ft"]:.0f} ft)', ha="center", fontsize=7.5)
    ax.set_xlabel("constant wind speed (mph)"); ax.set_ylabel("drift from apogee (m)")
    ax.set_ylim(0, max(r["drift_m"] for r in res["drift"]) * 1.25); ax.grid(axis="y", alpha=.3)
    ax.set_title(f"Drift under the 28 in parachute from {apogee:.0f} m (descent {vnom:.2f} m/s)", fontsize=10)
    fig.tight_layout(); fig.savefig(OUT / "drift.png", dpi=180); plt.close(fig)

    # console summary
    print(f"A = {A:.4f} m2, cord {L_cord:.2f} m")
    for r in rows:
        if r["cd"] == 0.75:
            print(f'{r["case"]:18s} m {r["mass_g"]:.0f} g  v {r["v"]:.2f} m/s ({r["v_fps"]:.1f} ft/s)  '
                  f't {r["t_desc"]:.0f} s  KE body {r["ke_body_j"]:.1f} J ({r["ke_body_ftlbf"]:.1f} ft-lbf) nose {r["ke_nose_j"]:.2f} J')
    print("Cd band (+25 g):", [f'{r["v"]:.2f}' for r in rows if r["case"] == "+10.2 g ballast"])
    print("deploy:", [(r["delay"], round(r["v"], 1)) for r in res["deploy"]])
    print("opening N:", [(r["delay"], round(r["F_open_N"])) for r in res["opening"]])
    print("snatch:", [(s["dv"], round(s["F_N"])) for s in snatch], f"mu {mu:.3f} k {k:.0f}")
    print("drift:", [(r["wind_mph"], round(r["drift_m"])) for r in res["drift"]])


if __name__ == "__main__":
    main()
