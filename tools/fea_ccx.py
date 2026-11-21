"""Open-source FEA of the fin can (gmsh + CalculiX), mirroring the owner's ANSYS setup.

  .venv/bin/python tools/fea_ccx.py --rev 6 --load Y=50 [--load Z=770 ...] [--mesh 1.5] [--name tipY50]

Setup (same as the owner's ANSYS runs, projects/l1-cheap/ansys_results.md):
  - geometry   out/fin_can_md/rev<N>/fin_can_md_rev<N>.step  (mm, Z = rocket axis = print direction)
  - support    fixed on the sleeve bore (radius = design sleeve bore / 2)
  - load       total force (N) spread over the TIP face of the fin pointing along +X
  - material   orthotropic 3D-printed PETG, CONSERVATIVE set (ansys_results.md), X/Y in-plane, Z across layers
  - output     max normal stress across layers (SZ) and failure index FI = SZ / 19 MPa in the ROOT ZONE
               (nodes within `root_zone_mm` of the sleeve OD, excluding the load face), plus renders
Element type C3D10 (quadratic tets). Units: mm, N, MPa.
"""
from __future__ import annotations

import argparse
import json
import math
import os
import re
import subprocess
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

# Material: conservative orthotropic PETG (MPa). Source: projects/l1-cheap/ansys_results.md (owner confirmed).
MAT = {"E1": 1472.0, "E2": 1472.0, "E3": 1087.0, "nu12": 0.38, "nu13": 0.38, "nu23": 0.38,
       "G12": 533.0, "G13": 394.0, "G23": 394.0}
Z_STRENGTH_MPA = 19.0      # across-layer tensile (Ultimaker TDS, upright) — same limit used in the owner's ANSYS FI
SOLVER = ""            # "" = CalculiX default direct solver (SPOOLES); ", SOLVER=ITERATIVE CHOLESKY" for big meshes
ROOT_ZONE_MM = 8.0         # radial band above the sleeve OD treated as the "fin root" for reporting
LOAD_EXCLUDE_MM = 5.0      # ignore nodes this close to the loaded tip face (load-application spike)


def mesh_and_groups(step: Path, p: dict, h: float, h_root: float, workdir: Path) -> dict:
    import gmsh
    gmsh.initialize()
    gmsh.option.setNumber("General.Terminal", 0)
    gmsh.option.setString("Geometry.OCCTargetUnit", "MM")
    gmsh.model.occ.importShapes(str(step))
    gmsh.model.occ.synchronize()
    r_bore = p["sleeve_bore_d_mm"] / 2
    r_tip = p["body_od_mm"] / 2 + p["span_mm"]
    bore, tip = [], []
    for dim, tag in gmsh.model.getEntities(2):
        lo, hi = gmsh.model.getParametrizationBounds(2, tag)
        us = np.linspace(lo[0], hi[0], 5)
        vs = np.linspace(lo[1], hi[1], 5)
        pts = np.array(gmsh.model.getValue(2, tag, [c for u in us for v in vs for c in (u, v)])).reshape(-1, 3)
        r = np.hypot(pts[:, 0], pts[:, 1])
        if np.all(np.abs(r - r_bore) < 0.05):
            bore.append(tag)
        xmin, ymin, zmin, xmax, ymax, zmax = gmsh.model.getBoundingBox(2, tag)
        if xmin > r_tip - 0.3 and abs(ymin) < 10 and abs(ymax) < 10:
            tip.append(tag)
    if not bore or not tip:
        raise SystemExit(f"face detection failed: bore={bore} tip={tip}")
    vols = [t for _, t in gmsh.model.getEntities(3)]
    gmsh.model.addPhysicalGroup(3, vols, name="SOLID")
    gmsh.model.addPhysicalGroup(2, bore, name="BORE")
    gmsh.model.addPhysicalGroup(2, tip, name="TIP")
    # local refinement box around the loaded (+X) fin root, where the owner's ANSYS shows the peak
    r_od = p["body_od_mm"] / 2
    f = gmsh.model.mesh.field.add("Box")
    gmsh.model.mesh.field.setNumber(f, "VIn", h_root)
    gmsh.model.mesh.field.setNumber(f, "VOut", h)
    gmsh.model.mesh.field.setNumber(f, "XMin", r_od - 4); gmsh.model.mesh.field.setNumber(f, "XMax", r_od + ROOT_ZONE_MM + 4)
    gmsh.model.mesh.field.setNumber(f, "YMin", -12); gmsh.model.mesh.field.setNumber(f, "YMax", 12)
    gmsh.model.mesh.field.setNumber(f, "ZMin", -1); gmsh.model.mesh.field.setNumber(f, "ZMax", p["root_chord_mm"] + 5)
    gmsh.model.mesh.field.setNumber(f, "Thickness", 6)
    gmsh.model.mesh.field.setAsBackgroundMesh(f)
    gmsh.option.setNumber("Mesh.MeshSizeExtendFromBoundary", 0)
    gmsh.option.setNumber("Mesh.MeshSizeMax", h)
    gmsh.option.setNumber("Mesh.MeshSizeMin", h_root / 2)
    gmsh.option.setNumber("Mesh.MeshSizeFromCurvature", 12)
    gmsh.option.setNumber("Mesh.ElementOrder", 2)
    gmsh.option.setNumber("Mesh.HighOrderOptimize", 1)
    gmsh.option.setNumber("Mesh.Algorithm3D", 10)
    gmsh.option.setNumber("General.NumThreads", os.cpu_count() or 1)
    gmsh.model.mesh.generate(3)
    nodes = {}
    tags, xyz, _ = gmsh.model.mesh.getNodes()
    xyz = np.asarray(xyz).reshape(-1, 3)
    node_xyz = dict(zip(tags.tolist(), xyz))
    etypes, etags, enodes = gmsh.model.mesh.getElements(3)
    i = list(etypes).index(11)  # 10-node tet
    tets = np.asarray(enodes[i]).reshape(-1, 10)
    def group_nodes(dim, name):
        for d, t in gmsh.model.getPhysicalGroups(dim):
            if gmsh.model.getPhysicalName(d, t) == name:
                return np.unique(gmsh.model.mesh.getNodesForPhysicalGroup(d, t)[0]).astype(int)
    out = {"node_xyz": node_xyz, "tets": tets.astype(int),
           "bore_nodes": group_nodes(2, "BORE"), "tip_nodes": group_nodes(2, "TIP"),
           "n_bore_faces": len(bore), "n_tip_faces": len(tip)}
    # boundary triangles for rendering
    gmsh.model.mesh.createFaces()
    gmsh.finalize()
    return out


def write_deck(m: dict, loads: dict, job: Path) -> None:
    global SOLVER
    # gmsh 10-node tet ordering -> CalculiX C3D10 ordering (nodes 9 and 10 swapped)
    perm = [0, 1, 2, 3, 4, 5, 6, 7, 9, 8]
    used = np.unique(m["tets"])
    lines = ["*HEADING", "fin can FEA (gmsh + CalculiX), mm-N-MPa", "*NODE"]
    lines += [f"{n}, {x:.6f}, {y:.6f}, {z:.6f}" for n in used for x, y, z in [m["node_xyz"][n]]]
    lines.append("*ELEMENT, TYPE=C3D10, ELSET=SOLID")
    lines += [f"{k + 1}, " + ", ".join(str(t[j]) for j in perm) for k, t in enumerate(m["tets"])]
    def nset(name, ids):
        out = [f"*NSET, NSET={name}"]
        ids = list(map(int, ids))
        out += [", ".join(map(str, ids[i:i + 12])) for i in range(0, len(ids), 12)]
        return out
    lines += nset("NBORE", m["bore_nodes"]) + nset("NTIP", m["tip_nodes"])
    M = MAT
    lines += ["*MATERIAL, NAME=PETG_PRINTED", "*ELASTIC, TYPE=ENGINEERING CONSTANTS",
              f"{M['E1']}, {M['E2']}, {M['E3']}, {M['nu12']}, {M['nu13']}, {M['nu23']}, {M['G12']}, {M['G13']},",
              f"{M['G23']}, 0.",
              "*SOLID SECTION, ELSET=SOLID, MATERIAL=PETG_PRINTED",
              "*BOUNDARY", "NBORE, 1, 3", "*STEP", f"*STATIC{SOLVER}", "*CLOAD"]
    n_tip = len(m["tip_nodes"])
    for comp, dof in (("X", 1), ("Y", 2), ("Z", 3)):
        if loads.get(comp):
            f = loads[comp] / n_tip
            lines += [f"{int(n)}, {dof}, {f:.8e}" for n in m["tip_nodes"]]
    lines += ["*NODE FILE", "U", "*EL FILE", "S", "*END STEP"]
    job.with_suffix(".inp").write_text("\n".join(lines) + "\n")


def read_frd(frd: Path) -> tuple[dict, dict]:
    disp, stress, block = {}, {}, None
    num = re.compile(r"[-+]?\d\.\d+E[-+]\d+")
    with open(frd) as f:
        for line in f:
            if line.startswith("    1PSTEP"):
                continue
            if line.startswith(" -4"):
                block = line.split()[1]
                continue
            if line.startswith(" -3"):
                block = None
                continue
            if block in ("DISP", "STRESS") and line.startswith(" -1"):
                nid = int(line[3:13])
                vals = [float(v) for v in num.findall(line[13:])]
                (disp if block == "DISP" else stress)[nid] = vals
    return disp, stress


def render(m: dict, fi: dict, path: Path, title: str, zoom: bool) -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib import cm, colors
    from mpl_toolkits.mplot3d.art3d import Poly3DCollection
    # outer faces of the linear sub-tets: faces used by exactly one element
    t4 = m["tets"][:, :4]
    faces = np.vstack([t4[:, [0, 1, 2]], t4[:, [0, 1, 3]], t4[:, [0, 2, 3]], t4[:, [1, 2, 3]]])
    key = np.sort(faces, axis=1)
    _, idx, cnt = np.unique(key, axis=0, return_index=True, return_counts=True)
    surf = faces[idx[cnt == 1]]
    xyz = np.array([m["node_xyz"][n] for n in surf.ravel()]).reshape(-1, 3, 3)
    val = np.array([np.mean([fi.get(n, 0.0) for n in tri]) for tri in surf])
    norm = colors.Normalize(0, 1)
    fig = plt.figure(figsize=(8, 7), dpi=120)
    ax = fig.add_subplot(projection="3d")
    ax.add_collection3d(Poly3DCollection(xyz, facecolors=cm.jet(norm(np.clip(val, 0, 1))), edgecolor="none"))
    if zoom:
        c, rr = np.array([24.0, 0.0, 12.0]), 16.0
    else:
        lo, hi = xyz.reshape(-1, 3).min(0), xyz.reshape(-1, 3).max(0)
        c, rr = (lo + hi) / 2, (hi - lo).max() / 2
    ax.set_xlim(c[0] - rr, c[0] + rr); ax.set_ylim(c[1] - rr, c[1] + rr); ax.set_zlim(c[2] - rr, c[2] + rr)
    ax.set_box_aspect((1, 1, 1)); ax.view_init(elev=15, azim=-35)
    ax.set_xlabel("X mm"); ax.set_ylabel("Y mm"); ax.set_zlabel("Z mm")
    fig.colorbar(cm.ScalarMappable(norm=norm, cmap="jet"), ax=ax, shrink=0.6, label="FI = SZ / 19 MPa (red = fails)")
    ax.set_title(title, fontsize=9)
    fig.savefig(path, bbox_inches="tight"); plt.close(fig)


def main() -> None:
    from parts import fin_can_md
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--rev", type=int, required=True)
    ap.add_argument("--load", action="append", default=[], metavar="Y=50")
    ap.add_argument("--mesh", type=float, default=2.5, help="max element size away from the fin root, mm")
    ap.add_argument("--root-mesh", type=float, default=0.8, help="element size in the +X fin root box, mm")
    ap.add_argument("--name", default=None)
    ap.add_argument("--iterative", action="store_true", help="low-memory iterative solver")
    ap.add_argument("--project", default="l1-cheap")
    a = ap.parse_args()
    global SOLVER
    SOLVER = ", SOLVER=ITERATIVE CHOLESKY" if a.iterative else ""
    loads = {k.upper(): float(v) for k, v in (s.split("=") for s in a.load)}
    name = a.name or "tip_" + "_".join(f"{k}{v:g}" for k, v in loads.items())
    step = ROOT / "out" / "fin_can_md" / f"rev{a.rev}" / f"fin_can_md_rev{a.rev}.step"
    work = ROOT / "out" / "fea" / f"rev{a.rev}" / name
    work.mkdir(parents=True, exist_ok=True)
    p = fin_can_md.params(a.project)
    m = mesh_and_groups(step, p, a.mesh, a.root_mesh, work)
    job = work / "job"
    write_deck(m, loads, job)
    env = dict(os.environ, OMP_NUM_THREADS=str(os.cpu_count() or 1))
    r = subprocess.run(["ccx", "-i", "job"], cwd=work, capture_output=True, text=True, env=env)
    (work / "ccx.log").write_text(r.stdout + r.stderr)
    if r.returncode != 0 or not (work / "job.frd").exists():
        raise SystemExit(f"ccx failed, see {work / 'ccx.log'}")
    disp, stress = read_frd(work / "job.frd")
    xyz = m["node_xyz"]
    r_od = p["body_od_mm"] / 2
    x_tip = r_od + p["span_mm"]
    sz = {n: s[2] for n, s in stress.items()}
    fi = {n: v / Z_STRENGTH_MPA for n, v in sz.items()}
    def in_root(n):
        x, y, z = xyz[n]
        r = math.hypot(x, y)
        return r_od - 1.0 <= r <= r_od + ROOT_ZONE_MM and x > 0 and abs(y) < 15
    away = [n for n in sz if xyz[n][0] < x_tip - LOAD_EXCLUDE_MM]
    root = [n for n in sz if in_root(n)]
    n_root = max(root, key=lambda n: sz[n])
    n_glob = max(away, key=lambda n: sz[n])
    umax = max(math.sqrt(sum(c * c for c in v[:3])) for v in disp.values())
    res = {"rev": a.rev, "loads_N": loads, "mesh_max_mm": a.mesh, "mesh_root_mm": a.root_mesh, "nodes": len(stress), "tets": len(m["tets"]),
           "bore_faces": m["n_bore_faces"], "tip_faces": m["n_tip_faces"], "tip_nodes": len(m["tip_nodes"]),
           "max_disp_mm": umax,
           "root_SZ_max_MPa": sz[n_root], "root_FI_max": fi[n_root], "root_FI_at_mm": list(map(float, xyz[n_root])),
           "global_SZ_max_excl_load_MPa": sz[n_glob], "global_FI_max_excl_load": fi[n_glob],
           "global_FI_at_mm": list(map(float, xyz[n_glob])), "material": MAT, "Z_strength_MPa": Z_STRENGTH_MPA}
    (work / "result.json").write_text(json.dumps(res, indent=2))
    title = f"rev {a.rev}  loads {loads} N  |  root FI max {fi[n_root]:.3f}  (SZ {sz[n_root]:.2f} MPa)"
    render(m, fi, work / "fi_overview.png", title, zoom=False)
    render(m, fi, work / "fi_root_zoom.png", title, zoom=True)
    print(json.dumps({k: v for k, v in res.items() if k != "material"}, indent=1))


if __name__ == "__main__":
    main()
