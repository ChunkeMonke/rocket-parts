"""Extra CFD figures for the rocket run: cross-sections behind the fins, streamlines, and pressure on each fin.

  .venv/bin/python tools/cfd_figures_extra.py --name a4

Needs the internal field in legacy VTK (written by Allrun, or by hand):
  mpirun -np 4 foamToVTK -parallel -time 800 -no-boundary -legacy -name VTKI
and the surface export VTKL/ (see tools/cfd_post.py). CFD frame: x aft from the nose tip, z = pitch plane through
fin 0 (fin 0 points +z), y >= 0 half model (mirrored here for display). Freestream (U cos a, 0, U sin a).
Figures -> out/cfd/of_<name>/figures/.
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import matplotlib.tri as mtri  # noqa: E402
import numpy as np  # noqa: E402
from matplotlib.collections import LineCollection, PolyCollection  # noqa: E402
from vtkmodules.util.numpy_support import vtk_to_numpy  # noqa: E402
from vtkmodules.vtkCommonDataModel import vtkPlane  # noqa: E402
from vtkmodules.vtkFiltersCore import vtkCellDataToPointData, vtkCutter, vtkTriangleFilter  # noqa: E402
from vtkmodules.vtkFiltersFlowPaths import vtkStreamTracer  # noqa: E402
from vtkmodules.vtkFiltersSources import vtkPointSource  # noqa: E402
from vtkmodules.vtkIOLegacy import vtkUnstructuredGridReader  # noqa: E402
from vtkmodules.vtkCommonCore import vtkPoints  # noqa: E402
from vtkmodules.vtkCommonDataModel import vtkPolyData  # noqa: E402

import cfd_post as P  # noqa: E402  (same folder)

ROOT = Path(__file__).resolve().parent.parent


def load_volume(case: Path, t: int):
    r = vtkUnstructuredGridReader()
    r.SetFileName(str(case / "VTKI" / f"{case.name}_{t}.vtk"))
    r.ReadAllScalarsOn(); r.ReadAllVectorsOn(); r.ReadAllFieldsOn(); r.Update()
    c2p = vtkCellDataToPointData(); c2p.SetInputData(r.GetOutput()); c2p.PassCellDataOff(); c2p.Update()
    return c2p.GetOutput()


def cut_x(grid, x: float):
    pl = vtkPlane(); pl.SetOrigin(x, 0, 0); pl.SetNormal(1, 0, 0)
    cu = vtkCutter(); cu.SetCutFunction(pl); cu.SetInputData(grid)
    tf = vtkTriangleFilter(); tf.SetInputConnection(cu.GetOutputPort()); tf.Update()
    pd = tf.GetOutput()
    pts = vtk_to_numpy(pd.GetPoints().GetData())
    cells = pd.GetPolys()
    off, con = vtk_to_numpy(cells.GetOffsetsArray()), vtk_to_numpy(cells.GetConnectivityArray())
    tris = np.array([con[off[k]:off[k + 1]] for k in range(len(off) - 1) if off[k + 1] - off[k] == 3])
    pdat = pd.GetPointData()
    return pts, tris, vtk_to_numpy(pdat.GetArray("U")), vtk_to_numpy(pdat.GetArray("p"))


def body_outline(rpts, rpolys, x, tol=0.004):
    """Rocket surface vertices within tol of station x, mirrored: (y, z) in mm, for drawing the body in a section."""
    C = np.array([rpts[f].mean(axis=0) for f in rpolys])
    s = np.abs(C[:, 0] - x) < tol
    yz = C[s][:, [1, 2]] * 1000
    return np.vstack([yz, yz * [-1, 1]])


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--name", default="a4")
    ap.add_argument("--time", type=int, default=800)
    a = ap.parse_args()
    case = ROOT / "out" / "cfd" / f"of_{a.name}"
    c = json.load(open(case / "case.json"))
    V, al = c["speed"], math.radians(c["alpha_deg"])
    Uinf = np.array(c["U"])
    figs = case / "figures"; figs.mkdir(exist_ok=True)
    grid = load_volume(case, a.time)
    rpts, rpolys, rd = P.read(case / "VTKL" / "rocket" / f"rocket_{a.time}.vtk")
    L = c["L"]

    # ---------------------------------------------------------------- 1. cross-sections through/behind the fins
    stations = [(L - 0.025, "through the fins (mid root chord)"), (L + 0.010, "10 mm behind the base"),
                (L + 0.080, "80 mm behind (near wake)"), (L + 0.250, "250 mm behind (far wake)")]
    fig, axs = plt.subplots(2, 2, figsize=(12, 11))
    for ax, (x, title) in zip(axs.flat, stations):
        pts, tris, U, p = cut_x(grid, x)
        y, z = pts[:, 1] * 1000, pts[:, 2] * 1000
        Y = np.concatenate([y, -y]); Z = np.concatenate([z, z])
        T = np.vstack([tris, tris + len(y)])
        u = np.concatenate([U[:, 0], U[:, 0]]) / V
        tri = mtri.Triangulation(Y, Z, T)
        cs = ax.tripcolor(tri, u, shading="gouraud", cmap="viridis", vmin=0.0, vmax=1.1)
        # crossflow relative to the freestream crossflow (shows vortices / wake swirl)
        gy, gz = np.meshgrid(np.linspace(-90, 90, 25), np.linspace(-90, 90, 25))
        vy = np.concatenate([U[:, 1], -U[:, 1]]); vz = np.concatenate([U[:, 2], U[:, 2]]) - Uinf[2]
        from scipy.interpolate import griddata
        iy = griddata((Y, Z), vy, (gy, gz)); iz = griddata((Y, Z), vz, (gy, gz))
        inside = np.hypot(gy, gz) < 24.0                     # no arrows inside the rocket
        iy[inside] = np.nan; iz[inside] = np.nan
        ax.quiver(gy, gz, iy, iz, color="white", scale=120, width=0.003)
        ob = body_outline(rpts, rpolys, x)
        if len(ob):
            ax.scatter(ob[:, 0], ob[:, 1], s=1, color="0.85")
        ax.set_xlim(-90, 90); ax.set_ylim(-90, 90); ax.set_aspect("equal"); ax.set_facecolor("0.3")
        ax.set_title(f"x = {x * 1000:.0f} mm: {title}"); ax.set_xlabel("y (mm)"); ax.set_ylabel("z (mm)")
    fig.colorbar(cs, ax=axs, label="axial speed u / U∞ (dark = slow wake)", shrink=0.7)
    fig.suptitle(f"Cross-sections looking forward, {V:.0f} m/s, α = {c['alpha_deg']}° (fin 0 points up; "
                 "arrows = sideways flow minus the freestream's)")
    fig.savefig(figs / "cfd_cross_sections.png", dpi=110); plt.close(fig)

    # ---------------------------------------------------------------- 2. streamlines
    seeds = vtkPoints()
    xs = L - 0.12
    for r in np.linspace(0.027, 0.085, 7):
        for th in np.radians(np.arange(0, 181, 15)):
            seeds.InsertNextPoint(xs, r * math.sin(th), r * math.cos(th))
    for zz in np.linspace(-0.06, 0.06, 13):                 # rake through the base wake
        seeds.InsertNextPoint(L + 0.005, 0.002, zz)
    sp = vtkPolyData(); sp.SetPoints(seeds)
    st = vtkStreamTracer(); st.SetInputData(grid); st.SetSourceData(sp)
    st.SetIntegrationDirectionToForward(); st.SetMaximumPropagation(1.2); st.SetIntegratorTypeToRungeKutta45()
    st.SetInputArrayToProcess(0, 0, 0, 0, "U"); st.Update()
    so = st.GetOutput()
    spts = vtk_to_numpy(so.GetPoints().GetData())
    sU = np.linalg.norm(vtk_to_numpy(so.GetPointData().GetArray("U")), axis=1)
    lines = so.GetLines()
    off, con = vtk_to_numpy(lines.GetOffsetsArray()), vtk_to_numpy(lines.GetConnectivityArray())
    polylines = [con[off[k]:off[k + 1]] for k in range(len(off) - 1)]
    C = np.array([rpts[f].mean(axis=0) for f in rpolys]) * 1000
    fig, axs = plt.subplots(2, 1, figsize=(13, 10), gridspec_kw={"hspace": 0.35})
    for ax, (i, j, lab, mirror) in zip(axs, ((0, 2, "SIDE view (x, z): pitch plane", False),
                                            (0, 1, "TOP view (x, y), mirrored", True))):
        ax.scatter(C[:, i], C[:, j], s=0.3, color="0.55")
        if mirror:
            ax.scatter(C[:, i], -C[:, j], s=0.3, color="0.55")
        segs, cols = [], []
        for pl in polylines:
            if len(pl) < 2:
                continue
            P2 = spts[pl][:, [i, j]] * 1000
            for m in ((1, -1) if mirror else (1,)):
                Q = P2 * [1, m]
                segs += list(zip(Q[:-1], Q[1:])); cols += list(sU[pl][:-1] / V)
        lc = LineCollection(segs, array=np.array(cols), cmap="plasma", linewidths=0.7)
        lc.set_clim(0, 1.15)
        ax.add_collection(lc)
        ax.set_xlim(L * 1000 - 140, L * 1000 + 320); ax.set_ylim(-110, 110); ax.set_aspect("equal")
        ax.set_title(lab + " (lines are projected onto this view)"); ax.set_xlabel("x from nose tip (mm)"); ax.set_ylabel("mm")
    fig.colorbar(lc, ax=axs, label="speed / U∞", shrink=0.7)
    fig.suptitle(f"Streamlines around the fin can, {V:.0f} m/s, α = {c['alpha_deg']}° (flow left to right)")
    fig.savefig(figs / "cfd_streamlines.png", dpi=110); plt.close(fig)

    # ---------------------------------------------------------------- 3. pressure on each fin
    Av, Cc = P.face_geom(rpts, rpolys)
    cp = rd["p"] / (0.5 * V * V)
    nb = -Av / np.linalg.norm(Av, axis=1)[:, None]
    r = np.hypot(Cc[:, 1], Cc[:, 2])
    th = np.degrees(np.arctan2(Cc[:, 1], Cc[:, 2]))          # 0 = fin 0 (+z), +120 = fin 1 (y > 0)
    r_body = 0.0234 + 0.0006
    fins = {"fin 0 (in the pitch plane, points up)": 0.0, "fin 1 (120°, y > 0; fin 2 is its mirror)": 120.0}
    fig, axs = plt.subplots(2, 2, figsize=(12, 9.5), gridspec_kw={"hspace": 0.45})
    q = 0.5 * P.RHO * V * V
    Aref = math.pi * P.D_REF ** 2 / 4
    summary = []
    for row, (name, ang) in enumerate(fins.items()):
        sel = (r > r_body) & (np.abs(((th - ang + 180) % 360) - 180) < 25) & (Cc[:, 0] > L - 0.06)
        et = np.array([0.0, math.cos(math.radians(ang)), -math.sin(math.radians(ang))])   # fin-normal direction
        er = np.array([0.0, math.sin(math.radians(ang)), math.cos(math.radians(ang))])    # spanwise
        side = np.sign(nb[:, :] @ et)
        Fn = 0.0
        for col, sgn in enumerate((1, -1)):
            ax = axs[row, col]
            s = np.where(sel & (side == sgn) & (np.abs(nb @ et) > 0.5))[0]
            polys = [np.column_stack([rpts[rpolys[k]][:, 0] * 1000, (rpts[rpolys[k]] @ er) * 1000]) for k in s]
            pc = PolyCollection(polys, array=cp[s], cmap="RdBu_r", edgecolors="face", linewidths=0.2)
            pc.set_clim(-0.6, 0.6)
            ax.add_collection(pc)
            ax.set_xlim(L * 1000 - 60, L * 1000 + 5); ax.set_ylim(20, 70); ax.set_aspect("equal")
            face = "face toward +θ" if sgn > 0 else "face toward −θ"
            ax.set_title(f"{name}\n{face}" if ang else f"{name}\n(both faces identical by symmetry)" if col == 0 else "")
            ax.set_xlabel("x from nose tip (mm)"); ax.set_ylabel("radius (mm)")
            if ang == 0 and col == 1:
                ax.set_visible(False)
        flat = np.where(sel & (np.abs(nb @ et) > 0.5))[0]                  # the two flat faces of this fin
        F_lift = (P.RHO * rd["p"][flat, None] * Av[flat]).sum(axis=0) @ et  # force normal to this fin's plane
        if ang == 0:
            F_lift = 0.0          # fin 0 is edge-on to the crossflow; only its +y face is in the half model (lift 0 by symmetry)
        summary.append((name.split(" (")[0], F_lift / (q * Aref) / al, F_lift * et[2] / (q * Aref) / al))
    fig.colorbar(pc, ax=axs, label="surface Cp (red = pressure, blue = suction)", shrink=0.7)
    l1, z1 = summary[1][1], summary[1][2]
    txt = (f"fin 0: edge-on, no lift  ·  fin 1 lift {abs(l1):.2f}/rad normal to the fin, {abs(z1):.2f}/rad of it in the pitch plane"
           f"  ·  fins 1 + 2: {2 * abs(z1):.2f}/rad (CN_α, ref 41.275 mm)")
    fig.suptitle(f"Pressure on each fin, {V:.0f} m/s, α = {c['alpha_deg']}°\n{txt}")
    fig.savefig(figs / "cfd_fin_pressure.png", dpi=110); plt.close(fig)
    print("per-fin lift slope (/rad, normal to fin; pitch-plane part):", [(n, round(l, 2), round(z, 2)) for n, l, z in summary])
    print("figures:", ["cfd_cross_sections.png", "cfd_streamlines.png", "cfd_fin_pressure.png"])


if __name__ == "__main__":
    main()
