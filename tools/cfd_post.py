"""Post-process the OpenFOAM rocket run (tools/cfd_rocket.py): forces, CN_alpha, CP, drag, and figures.

  .venv/bin/python tools/cfd_post.py --name a4

Reads legacy VTK written by
  mpirun -np 4 foamToVTK -parallel -time '600,800' -no-internal -no-point-data -legacy -ascii -name VTKL
(the `forces` / `wallShearStress` function objects crash in this OpenFOAM build, so forces are integrated here).
Forces are PRESSURE ONLY (they set CN and CP). Skin friction is added to the axial coefficient with a turbulent
flat-plate estimate (Cf = 0.074 Re^-0.2 on the wetted area) and labelled as such.
OpenFOAM boundary normals point OUT of the fluid (into the rocket), so F_body = sum(rho * p_kin * n_foam * A).
Half model about y = 0: Fx, Fz, My are doubled.
Figures -> out/cfd/of_<name>/figures/.
"""
from __future__ import annotations

import argparse
import json
import math
import re
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import yaml  # noqa: E402
from matplotlib.collections import PolyCollection  # noqa: E402
from mpl_toolkits.mplot3d.art3d import Poly3DCollection  # noqa: E402
from vtkmodules.vtkIOLegacy import vtkPolyDataReader  # noqa: E402
from vtkmodules.util.numpy_support import vtk_to_numpy  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
RHO, NU = 1.225, 1.5e-5
D_REF = 0.041275


def read(path: Path):
    r = vtkPolyDataReader()
    r.SetFileName(str(path))
    r.ReadAllScalarsOn(); r.ReadAllVectorsOn(); r.ReadAllFieldsOn()
    r.Update()
    pd = r.GetOutput()
    pts = vtk_to_numpy(pd.GetPoints().GetData()).astype(float)
    cells = pd.GetPolys()
    off, con = vtk_to_numpy(cells.GetOffsetsArray()), vtk_to_numpy(cells.GetConnectivityArray())
    polys = [con[off[k]:off[k + 1]] for k in range(len(off) - 1)]
    cd = pd.GetCellData()
    data = {cd.GetArrayName(k): vtk_to_numpy(cd.GetArray(k)).astype(float) for k in range(cd.GetNumberOfArrays())}
    return pts, polys, data


def face_geom(pts, polys):
    """Area vectors (Newell) and centroids."""
    Av, C = np.zeros((len(polys), 3)), np.zeros((len(polys), 3))
    for j, f in enumerate(polys):
        P = pts[f]
        Av[j] = 0.5 * np.cross(P, np.roll(P, -1, axis=0)).sum(axis=0)
        C[j] = P.mean(axis=0)
    return Av, C


def forces(case: Path, t: int, c: dict) -> dict:
    pts, polys, d = read(case / "VTKL" / "rocket" / f"rocket_{t}.vtk")
    Av, C = face_geom(pts, polys)
    p = d["p"]
    dF = RHO * p[:, None] * Av                       # n_foam points into the body
    F = 2 * dF.sum(axis=0)
    My = 2 * (C[:, 2] * dF[:, 0] - C[:, 0] * dF[:, 2]).sum()
    V = c["speed"]
    q, A = 0.5 * RHO * V * V, math.pi * D_REF ** 2 / 4
    al = math.radians(c["alpha_deg"])
    wet = 2 * np.linalg.norm(Av, axis=1).sum()
    Re = V * c["L"] / NU
    cf = 0.074 * Re ** -0.2
    CA_fric = cf * wet / A
    return {"time": t, "Fx_N": F[0], "Fz_N": F[2], "My_Nm": My,
            "CN": F[2] / (q * A), "CN_alpha_per_rad": F[2] / (q * A) / al, "CP_from_tip_mm": -My / F[2] * 1000,
            "CA_pressure": F[0] / (q * A), "CA_friction_flatplate": CA_fric, "CA_total_est": F[0] / (q * A) + CA_fric,
            "wetted_area_m2": wet, "Re_L": Re}


def residuals(case: Path):
    it, res, t = [], {}, 0
    for line in (case / "log.simpleFoam").read_text().splitlines():
        if line.startswith("Time ="):
            t = int(float(line.split("=")[1]))
        m = re.search(r"Solving for (\w+), Initial residual = ([0-9.eE+-]+)", line)
        if m and m.group(1) not in res.get(t, {}):
            res.setdefault(t, {})[m.group(1)] = float(m.group(2))
    return res


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--name", default="a4")
    a = ap.parse_args()
    case = ROOT / "out" / "cfd" / f"of_{a.name}"
    c = json.load(open(case / "case.json"))
    figs = case / "figures"; figs.mkdir(exist_ok=True)
    r6, r8 = forces(case, 600, c), forces(case, 800, c)
    res = {"case": c, "t600": r6, "t800": r8,
           "CP_change_600_800_mm": r8["CP_from_tip_mm"] - r6["CP_from_tip_mm"]}
    (case / "result.json").write_text(json.dumps(res, indent=2, default=float))
    print(json.dumps(res, indent=2, default=float))
    V = c["speed"]; q = 0.5 * V * V                      # kinematic

    # ---------------------------------------------------------------- rocket surface data (full = mirror)
    pts, polys, d = read(case / "VTKL" / "rocket" / "rocket_800.vtk")
    Av, C = face_geom(pts, polys)
    cp_s = d["p"] / q

    # 1. symmetry plane: |U| and Cp
    sp, spol, sd = read(case / "VTKL" / "symmetry" / "symmetry_800.vtk")
    verts = [sp[f][:, [0, 2]] * 1000 for f in spol]
    Umag = np.linalg.norm(sd["U"], axis=1)
    cps = sd["p"] / q
    views = [("whole rocket", (-80, 1400), (-160, 160)), ("nose", (-20, 260), (-60, 60)),
             ("fin can and fins", (820, 1120), (-110, 110))]
    for field, vals, cmap, lab, lim in (("velocity", Umag, "viridis", "|U| (m/s)", (0, 1.25 * V)),
                                        ("pressure", cps, "RdBu_r", "Cp = p / q", (-1, 1))):
        fig, axs = plt.subplots(3, 1, figsize=(11, 11), gridspec_kw={"height_ratios": [1, 1, 1.3]})
        for ax, (title, xl, zl) in zip(axs, views):
            sel = [i for i, v in enumerate(verts) if xl[0] - 50 < v[:, 0].mean() < xl[1] + 50 and zl[0] - 50 < v[:, 1].mean() < zl[1] + 50]
            pc = PolyCollection([verts[i] for i in sel], array=vals[sel], cmap=cmap, edgecolors="none")
            pc.set_clim(*lim)
            ax.add_collection(pc)
            ax.set_xlim(*xl); ax.set_ylim(*zl); ax.set_aspect("equal")
            ax.set_facecolor("0.25"); ax.set_title(f"{title}: symmetry plane through fin 0 (grey = rocket)")
            ax.set_xlabel("x from nose tip (mm)"); ax.set_ylabel("z (mm)")
            fig.colorbar(pc, ax=ax, label=lab, shrink=0.9)
        fig.suptitle(f"CFD {field}: {V:.0f} m/s, angle of attack {c['alpha_deg']}° (flow left to right, tilted up)")
        fig.tight_layout(); fig.savefig(figs / f"cfd_{field}_plane.png", dpi=110); plt.close(fig)

    # 2. surface Cp seen from below (windward) and above (leeward), full rocket (mirror of the half model)
    nb = -Av / np.linalg.norm(Av, axis=1)[:, None]          # outward body normal
    fig, axs = plt.subplots(4, 1, figsize=(12, 13), gridspec_kw={"height_ratios": [1, 1, 1.6, 1.6], "hspace": 0.55})
    for ax, (side, sgn, xl, title) in zip(axs, ((-1, -1, (0, 1035), "from BELOW (windward): whole rocket"),
                                                (1, 1, (0, 1035), "from ABOVE (leeward): whole rocket"),
                                                (-1, -1, (860, 1035), "from BELOW: fin can"),
                                                (1, 1, (860, 1035), "from ABOVE: fin can"))):
        sel = np.where(nb[:, 2] * sgn > 0)[0]
        sel = sel[np.argsort(C[sel, 2] * sgn)]               # far side first, near side drawn on top
        vs, vals = [], []
        for m in (1, -1):
            for k in sel:
                P = pts[polys[k]][:, [0, 1]] * 1000
                P[:, 1] *= m
                vs.append(P); vals.append(cp_s[k])
        pc = PolyCollection(vs, array=np.array(vals), cmap="RdBu_r", edgecolors="face", linewidths=0.2)
        pc.set_clim(-0.5, 0.5)
        ax.add_collection(pc); ax.set_xlim(*xl); ax.set_ylim(-75, 75); ax.set_aspect("equal")
        ax.set_title(title); ax.set_xlabel("x from nose tip (mm)"); ax.set_ylabel("y (mm)")
    fig.colorbar(pc, ax=axs, label="surface Cp (red = pressure, blue = suction)", shrink=0.6)
    fig.suptitle(f"Surface pressure at {V:.0f} m/s, α = {c['alpha_deg']}°: the flow pushes up on the underside")
    fig.savefig(figs / "cfd_surface_cp.png", dpi=110); plt.close(fig)

    # 3. where the side force comes from: dCN/dx by station, and body Cp lines
    q_d = 0.5 * RHO * V * V
    Aref = math.pi * D_REF ** 2 / 4
    dFz = 2 * RHO * d["p"] * Av[:, 2]
    bins = np.arange(0, 1040, 10) / 1000
    idx = np.digitize(C[:, 0], bins)
    dcn = np.array([dFz[idx == i].sum() for i in range(1, len(bins))]) / (q_d * Aref) / 0.010   # per metre
    xb = (bins[:-1] + bins[1:]) / 2 * 1000
    r = np.hypot(C[:, 1], C[:, 2]); ang = np.degrees(np.arctan2(C[:, 1], -C[:, 2]))   # 0 = windward (-z)
    body = (r * 1000 > 19.5) & (r * 1000 < 24.5) & (C[:, 0] * 1000 < 925)
    fig, axs = plt.subplots(2, 1, figsize=(11, 8), sharex=True)
    axs[0].bar(xb, dcn, width=10, color="#3b6ea8")
    cp_mm = r8["CP_from_tip_mm"]
    axs[0].axvline(cp_mm, color="crimson", lw=2, label=f"CFD CP {cp_mm:.0f} mm")
    axs[0].set_ylabel("dCN/dx (1/m)"); axs[0].legend(); axs[0].set_title("Where the side (normal) force comes from")
    for lo, hi, col, lab in ((0, 20, "crimson", "windward line (underside)"), (160, 180, "navy", "leeward line (top)")):
        s = body & (ang >= lo) & (ang <= hi)
        o = np.argsort(C[s, 0])
        axs[1].plot(C[s, 0][o] * 1000, cp_s[s][o], ".", ms=2, color=col, label=lab)
    axs[1].set_ylim(-0.6, 1.0); axs[1].invert_yaxis(); axs[1].legend(); axs[1].grid(alpha=0.3)
    axs[1].set_xlabel("x from nose tip (mm)"); axs[1].set_ylabel("body Cp (inverted)")
    fig.tight_layout(); fig.savefig(figs / "cfd_force_distribution.png", dpi=110); plt.close(fig)

    # 4. CG / CP comparison on the rocket outline
    dsn = yaml.safe_load((ROOT / "projects/l1-cheap/design.yaml").read_text())
    side = sp[np.concatenate(spol)] * 1000
    fig, ax = plt.subplots(figsize=(12, 4.2))
    rx = C[:, 0] * 1000; rz = C[:, 2] * 1000
    ax.scatter(rx, rz, s=0.2, color="0.6"); ax.scatter(rx, -rz, s=0.2, color="0.6")
    marks = [("CG, OpenRocket (65 g nose)", 750.4, "tab:blue", "o"), ("CG, our sim, OR weights", 749.2, "tab:cyan", "o"),
             ("CP, Barrowman / RocketPy", 804.7, "tab:orange", "D"), ("CP, OpenRocket", 836.0, "tab:purple", "D"),
             (f"CP, CFD (this run)", cp_mm, "crimson", "*")]
    for k, (lab, x, col, mk) in enumerate(marks):
        yy = -30 if lab.startswith("CG") else 30
        yy += (-12 if "our sim" in lab else 0)
        ax.plot(x, yy if lab.startswith("CG") else 0, mk, color=col, ms=14 if mk == "*" else 10,
                label=f"{lab}: {x:.0f} mm", zorder=5, alpha=0.9)
    for k, (lab, x) in enumerate((("Barrowman", 804.7), ("OpenRocket", 836.0), ("CFD", cp_mm))):
        m = (x - 750.4) / (D_REF * 1000)
        ax.annotate(f"{lab} CP: {m:.2f} cal", (x, 0), xytext=(560 + 170 * k, 75), ha="center", fontsize=9,
                    arrowprops=dict(arrowstyle="-", color="0.5"))
    ax.set_xlim(-20, 1060); ax.set_ylim(-110, 100); ax.set_aspect("equal")
    ax.set_xlabel("x from nose tip (mm)"); ax.legend(loc="lower left", fontsize=8, ncol=2)
    ax.set_title("Stability margin vs the OpenRocket CG (750 mm): CP from three methods (ref 41.275 mm)")
    fig.tight_layout(); fig.savefig(figs / "cfd_cp_comparison.png", dpi=110); plt.close(fig)

    # 5. convergence
    R = residuals(case)
    ts = sorted(R)
    fig, ax = plt.subplots(figsize=(8, 4))
    for fld in ("Ux", "Uz", "p", "k", "omega"):
        ax.semilogy(ts, [R[t].get(fld, np.nan) for t in ts], label=fld)
    ax.set_xlabel("iteration"); ax.set_ylabel("initial residual"); ax.grid(alpha=0.3); ax.legend()
    ax.set_title(f"Convergence (CP moved {res['CP_change_600_800_mm']:+.1f} mm from iteration 600 to 800)")
    fig.tight_layout(); fig.savefig(figs / "cfd_convergence.png", dpi=110); plt.close(fig)
    print("figures:", sorted(p.name for p in figs.glob("*.png")))


if __name__ == "__main__":
    main()
