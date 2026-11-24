"""Ms. Piggy aerodynamic database from the CFD campaign (tools/cfd_campaign_msp.sh).

  .venv/bin/python tools/msp_aero.py

Reads out/cfd/of_msp_*/result.json (+ surface VTK for the base-drag split) and writes
out/msp/aero.json and monochrome figures in projects/l1-cheap/report/figures/msp/:
  mesh_study.png, cn_cp_vs_alpha.png, ca_vs_mach.png, drag_breakdown.png.

Method
- Normal force / CP: incompressible α sweep (coarse mesh) scaled by the fine/coarse ratio at α = 4°
  (mesh correction); Mach effect from the compressible runs (M 0.5, 0.8) as ratios to the M 0.29 coarse run.
- Axial force: CFD pressure part (forebody + base) + skin friction from a turbulent flat plate with
  compressibility (Re on body length), smooth for the paper tube and rough (ks = 40 µm, 0.2 mm FDM layers)
  for the printed parts, area-weighted on the OML wetted areas.
"""
import json
import math
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
import cfd_post as P  # noqa: E402

FIG = ROOT / "projects/l1-cheap/report/figures/msp"
D_REF = 0.041275
A_REF = math.pi * D_REF ** 2 / 4
L_BODY = 1.0783
NU, A_SND = 1.5e-5, 340.3
KS = 40e-6
CA_RAIL = 0.06        # two printed rail guides (1010 or 1515), ESTIMATE (≈0.03 each on the 41 mm reference area)


def res(name):
    f = ROOT / f"out/cfd/of_{name}/result.json"
    return json.load(open(f)) if f.exists() else None


def offset_correct(r, r0):
    """Remove the zero-incidence force offset (numerical: a 3-fin rocket has CN = 0 at alpha = 0 by symmetry).
    CN' = CN - CN0;  CP' = (CN*CP - CN0*CP0) / CN'."""
    if not r0:
        return dict(r)
    cn0, mc0 = r0["CN"], r0["CN"] * r0["CP_from_tip_mm"]
    out = dict(r)
    cn = r["CN"] - cn0
    out["CN"] = cn
    out["CP_from_tip_mm"] = (r["CN"] * r["CP_from_tip_mm"] - mc0) / cn
    out["CN_alpha_per_rad"] = r["CN_alpha_per_rad"] * cn / r["CN"]
    return out


def split_areas_and_base(name):
    """Wetted area split (printed vs tube) and base axial coefficient from the surface VTK."""
    case = ROOT / f"out/cfd/of_{name}"
    c = json.load(open(case / "case.json"))
    P.configure(c)
    pts, polys, d = P.read(case / "VTKL" / "rocket" / f"rocket_{c['t_last']}.vtk")
    Av, C = P.face_geom(pts, polys)
    a = np.linalg.norm(Av, axis=1)
    x = C[:, 0] * 1000
    L = c["L"] * 1000
    tube = (x > 163.5 + 0.5) & (x < L - 30 - 158.5 - 0.5)          # paper tube between nose and fin can
    base = (x > L - 0.6) & (np.abs(Av[:, 0]) > 0.9 * a)
    q = 0.5 * P.RHO * c["speed"] ** 2
    ca_base = 2 * P.RHO * (d["p"][base] * Av[base, 0]).sum() / (q * A_REF)
    return dict(A_tube=2 * a[tube].sum(), A_print=2 * a[~tube].sum(), ca_base=float(ca_base))


def cf_smooth(re, m):
    return 0.074 * re ** -0.2 / (1 + 0.144 * m * m) ** 0.65


def cf_rough(m):
    return (1.89 + 1.62 * math.log10(L_BODY / KS)) ** -2.5 / (1 + 0.144 * m * m) ** 0.65


def main():
    FIG.mkdir(parents=True, exist_ok=True)
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 9})
    R = {n: res(n) for n in ("msp_a0", "msp_a2", "msp_a4", "msp_a6", "msp_a8", "msp_a4_f", "msp_m05", "msp_m08")}
    raw = {k: v["final"] for k, v in R.items() if v}
    r0c = raw.get("msp_a0")
    f0 = res("msp_a0_f")
    r0f = f0["final"] if f0 else r0c          # refined-mesh offset; falls back to the coarse offset
    have = {}
    for k, v in raw.items():
        if k in ("msp_a0",):
            have[k] = v
        else:
            have[k] = offset_correct(v, r0f if k.endswith("_f") else r0c)
    print("cases:", sorted(have), "| refined offset from", "msp_a0_f" if f0 else "coarse msp_a0 (fallback)")
    out = {"cases": {k: {kk: v[kk] for kk in ("CN", "CN_alpha_per_rad", "CP_from_tip_mm", "CA_pressure")} for k, v in have.items()},
           "raw": {k: {kk: v[kk] for kk in ("CN", "CN_alpha_per_rad", "CP_from_tip_mm", "CA_pressure")} for k, v in raw.items()},
           "offset": {"coarse": {"CN0": r0c["CN"], "CP0": r0c["CP_from_tip_mm"]} if r0c else None,
                      "refined_source": "msp_a0_f" if f0 else "msp_a0 (fallback)"}}
    # ---- mesh study
    c4, f4 = have.get("msp_a4"), have.get("msp_a4_f")
    corr = {"CN": 1.0, "CP_mm": 0.0, "CA_p": 1.0}
    if c4 and f4:
        corr = {"CN": f4["CN"] / c4["CN"], "CP_mm": f4["CP_from_tip_mm"] - c4["CP_from_tip_mm"],
                "CA_p": f4["CA_pressure"] / c4["CA_pressure"]}
        cells = {}
        for n in ("msp_a4", "msp_a4_f"):
            t = (ROOT / f"out/cfd/of_{n}/log.checkMesh").read_text()
            cells[n] = int([l for l in t.splitlines() if "cells:" in l][0].split()[-1])
        out["mesh_study"] = dict(cells=cells, coarse=c4, fine=f4, correction=corr)
        fig, ax = plt.subplots(1, 3, figsize=(9, 2.8))
        for a, key, lab in zip(ax, ("CN_alpha_per_rad", "CP_from_tip_mm", "CA_pressure"),
                               ("CNα (/rad)", "CP from tip (mm)", "CA pressure")):
            v = [c4[key], f4[key]]
            a.plot([cells["msp_a4"] / 1e6, cells["msp_a4_f"] / 1e6], v, "ko-")
            for xx, vv in zip([cells["msp_a4"] / 1e6, cells["msp_a4_f"] / 1e6], v):
                a.annotate(f"{vv:.3g}", (xx, vv), textcoords="offset points", xytext=(4, 4), fontsize=8)
            a.set_xlabel("cells (millions)"); a.set_title(lab, fontsize=9); a.grid(alpha=.3)
        fig.suptitle("Mesh study, 100 m/s, α = 4°: coarse vs refined surface/near-field mesh", fontsize=9.5)
        fig.tight_layout(); fig.savefig(FIG / "mesh_study.png", dpi=180); plt.close(fig)
    # ---- alpha sweep
    al, cn, cp = [], [], []
    for a_deg in (0, 2, 4, 6, 8):
        r = have.get(f"msp_a{a_deg}")
        if r:
            al.append(a_deg); cn.append(0.0 if a_deg == 0 else r["CN"] * corr["CN"])
            cp.append(r["CP_from_tip_mm"] + corr["CP_mm"] if a_deg > 0 else np.nan)
    if len(al) >= 3:
        al_a, cn_a = np.array(al, float), np.array(cn)
        k = np.polyfit(np.radians(al_a[al_a <= 4]), cn_a[al_a <= 4], 1)[0]
        out["alpha_sweep"] = dict(alpha_deg=al, CN=cn, CP_mm=cp, CNalpha_linear=k)
        fig, ax = plt.subplots(1, 2, figsize=(9, 3.2))
        ax[0].plot(al, cn, "ko-", label="CFD (mesh-corrected)")
        aa = np.linspace(0, 8, 20); ax[0].plot(aa, k * np.radians(aa), "k--", lw=0.8, label=f"linear, CNα = {k:.2f} /rad")
        ax[0].set_xlabel("angle of attack (deg)"); ax[0].set_ylabel("normal-force coefficient CN"); ax[0].legend(fontsize=8)
        ax[0].grid(alpha=.3)
        ax[1].plot(al[1:], cp[1:], "ko-"); ax[1].set_xlabel("angle of attack (deg)"); ax[1].set_ylabel("CP from nose tip (mm)")
        ax[1].grid(alpha=.3)
        fig.suptitle("Normal force and centre of pressure vs angle of attack (100 m/s)", fontsize=9.5)
        fig.tight_layout(); fig.savefig(FIG / "cn_cp_vs_alpha.png", dpi=180); plt.close(fig)
    # ---- Mach: CP, CNα, CA
    base_ref = have.get("msp_a4")
    mach_pts = [(0.294, base_ref)] if base_ref else []
    for n, m in (("msp_m05", 0.5), ("msp_m08", 0.8)):
        if have.get(n):
            mach_pts.append((m, have[n]))
    a0 = have.get("msp_a0")
    sp = split_areas_and_base("msp_a0" if a0 else "msp_a4")
    out["areas"] = sp
    d_alpha = (base_ref["CA_pressure"] - a0["CA_pressure"]) if (a0 and base_ref) else 0.0
    rows = []
    # Pressure drag: refined-mesh, offset-free incompressible value at M 0.29 (forebody + base). Compressible runs use
    # first-order upwinding and over-predict CA_pressure (0.55 at M 0.5 vs 0.24 at M 0.29), so their CA is not used.
    # Base drag scaled with the subsonic base-drag rise (0.12 + 0.13 M^2, OpenRocket/Barrowman); forebody constant.
    # CN / CP vs Mach: compressible runs as increments over the coarse M 0.29 run at the same alpha and mesh.
    ref_c = raw.get("msp_a4")
    ca_p_fine = (base_ref["CA_pressure"] - d_alpha) * corr["CA_p"] if base_ref else 0.0
    base0 = sp["ca_base"] * corr["CA_p"]
    fore = ca_p_fine - base0
    # compressibility of the forebody/fin pressure drag: same-scheme ratio of the compressible runs
    # (both first-order upwind, so the numerical bias largely cancels), anchored with Prandtl-Glauert 0.294 -> 0.5
    comp = {m: raw[k]["CA_pressure"] for m, k in ((0.5, "msp_m05"), (0.8, "msp_m08")) if k in raw}
    pg = lambda m: 1 / math.sqrt(1 - m * m)  # noqa: E731
    def fore_m(m):
        if m <= 0.5 or 0.8 not in comp:
            return fore * pg(min(m, 0.5)) / pg(0.294)
        f05 = fore * pg(0.5) / pg(0.294)
        k = comp[0.8] / comp[0.5]
        return f05 * (1 + (k - 1) * (m - 0.5) / 0.3)
    grid = sorted(set([0.294, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9] + [m for m, _ in mach_pts]))
    for m in grid:
        r = next((rr for mm, rr in mach_pts if abs(mm - m) < 1e-6), None)
        base_m = base0 * (0.12 + 0.13 * m * m) / (0.12 + 0.13 * 0.294 ** 2)
        re = m * A_SND * L_BODY / NU
        ca_f = (cf_smooth(re, m) * sp["A_tube"] + max(cf_smooth(re, m), cf_rough(m)) * sp["A_print"]) / A_REF
        fm = fore_m(min(m, 0.8)) if m <= 0.8 else fore_m(0.8) * (1 + 1.5 * (m - 0.8))   # beyond 0.8: extrapolated
        row = dict(mach=m, CA_forebody=fm, CA_base=base_m, CA_pressure0=fm + base_m, CA_friction=ca_f, CA_rail=CA_RAIL,
                   CA0=fm + base_m + ca_f + CA_RAIL, source="CFD" if r else "interpolated")
        if r is not None:
            if m < 0.3:
                row.update(CNalpha=r["CN_alpha_per_rad"] * corr["CN"], CP_mm=r["CP_from_tip_mm"] + corr["CP_mm"])
            else:
                rr = raw[[k for k in ("msp_m05", "msp_m08") if k.endswith(f"{int(round(m * 10)):02d}")][0]]
                k_cn = rr["CN"] / ref_c["CN"]
                d_cp = rr["CP_from_tip_mm"] - ref_c["CP_from_tip_mm"]
                f4 = have.get("msp_a4_f", r)
                row.update(CNalpha=f4["CN_alpha_per_rad"] * k_cn, CP_mm=f4["CP_from_tip_mm"] + d_cp)
        rows.append(row)
    out["mach"] = rows
    out["ca_base_M029"] = base0
    if rows:
        fig, ax = plt.subplots(1, 3, figsize=(10, 3))
        mm = [r["mach"] for r in rows]
        ax[0].plot(mm, [r["CA0"] for r in rows], "ko-", label="total (α = 0)")
        ax[0].plot(mm, [r["CA_pressure0"] for r in rows], "k--", marker="s", ms=3, label="pressure (CFD)")
        ax[0].plot(mm, [r["CA_friction"] for r in rows], "k:", marker="^", ms=3, label="skin friction")
        ax[0].set_ylabel("axial-force coefficient CA"); ax[0].legend(fontsize=7.5)
        cr = [r for r in rows if "CP_mm" in r]
        ax[1].plot([r["mach"] for r in cr], [r["CNalpha"] for r in cr], "ko-"); ax[1].set_ylabel("CNα (/rad)")
        ax[2].plot([r["mach"] for r in cr], [r["CP_mm"] for r in cr], "ko-"); ax[2].set_ylabel("CP from tip (mm)")
        for a in ax:
            a.set_xlabel("Mach number"); a.grid(alpha=.3)
        fig.suptitle("Aerodynamic coefficients vs Mach (mesh-corrected; ref. diameter 41.275 mm)", fontsize=9.5)
        fig.tight_layout(); fig.savefig(FIG / "ca_cn_cp_vs_mach.png", dpi=180); plt.close(fig)
        r0 = rows[0]
        fig, ax = plt.subplots(figsize=(6, 2.8))
        parts = {"forebody + fin pressure": r0["CA_forebody"], "base pressure": r0["CA_base"],
                 "skin friction": r0["CA_friction"], "rail guides (est.)": r0["CA_rail"]}
        ax.barh(list(parts), list(parts.values()), color=["0.25", "0.45", "0.7", "0.9"], edgecolor="k")
        for i, v in enumerate(parts.values()):
            ax.text(v + 0.005, i, f"{v:.3f} ({v / r0['CA0'] * 100:.0f} %)", va="center", fontsize=8)
        ax.set_xlabel(f"CA contribution at M {r0['mach']:.2f}, α = 0 (total {r0['CA0']:.3f})"); ax.grid(axis="x", alpha=.3)
        ax.set_xlim(0, max(parts.values()) * 1.45)
        fig.tight_layout(); fig.savefig(FIG / "drag_breakdown.png", dpi=180); plt.close(fig)
    json.dump(out, open(ROOT / "out/msp/aero.json", "w"), indent=1, default=float)
    print(json.dumps({k: out[k] for k in out if k != "cases"}, indent=1, default=float)[:3000])


if __name__ == "__main__":
    main()
