"""FEA of the aft Kevlar bulkhead (gmsh + CalculiX), same orthotropic PETG and failure index as tools/fea_ccx.py.

  .venv/bin/python tools/fea_bulkhead.py --rev 2 --load 686 [--name snatch20]

Support: fixed on the outer cylindrical surface (epoxy bond to the tube). Load: total force (N) along +Z (forward)
on the eye's tunnel roof, where the Kevlar bears. Z = print direction (layers horizontal).
Output: max SZ (across layers) and FI = SZ / 19 MPa away from the load faces; max in-plane principal stress.
"""
import argparse
import json
import subprocess
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools")); sys.path.insert(0, str(ROOT))
import fea_ccx as F  # noqa: E402
from parts import kevlar_bulkhead as K  # noqa: E402


def mesh(step, p, h, h_eye, work, load_box=None, r_fix=None):
    import gmsh
    gmsh.initialize(); gmsh.option.setNumber("General.Terminal", 0)
    gmsh.model.occ.importShapes(str(step)); gmsh.model.occ.synchronize()
    R = p["od_mm"] / 2; t, w, hh = p["plate_mm"], p["eye_tunnel_w_mm"], p["eye_tunnel_h_mm"]
    outer, roof = [], []
    for dim, tag in gmsh.model.getEntities(2):
        x0, y0, z0, x1, y1, z1 = gmsh.model.getBoundingBox(2, tag)
        lo, hi = gmsh.model.getParametrizationBounds(2, tag)
        uv = [(lo[0] + (hi[0] - lo[0]) * a, lo[1] + (hi[1] - lo[1]) * b) for a in (0.3, 0.7) for b in (0.3, 0.7)]
        pts = np.array(gmsh.model.getValue(2, tag, [c for q in uv for c in q])).reshape(-1, 3)
        r = np.hypot(pts[:, 0], pts[:, 1])
        if r.min() > (r_fix if r_fix else R - 0.65):
            outer.append(tag)
        elif load_box is not None:
            bx = load_box
            if (pts[:, 0].min() >= bx[0] and pts[:, 0].max() <= bx[1] and pts[:, 1].min() >= bx[2]
                    and pts[:, 1].max() <= bx[3] and pts[:, 2].min() >= bx[4] and pts[:, 2].max() <= bx[5]):
                roof.append(tag)
        elif (pts[:, 2].min() > t + hh - 0.05 and np.abs(pts[:, 0]).max() <= w / 2 + 0.01
              and np.abs(pts[:, 1]).max() <= p["eye_length_mm"] / 2 + 0.01):
            roof.append(tag)
    gmsh.model.addPhysicalGroup(3, [t_ for _, t_ in gmsh.model.getEntities(3)], name="SOLID")
    gmsh.model.addPhysicalGroup(2, outer, name="BORE"); gmsh.model.addPhysicalGroup(2, roof, name="TIP")
    f = gmsh.model.mesh.field.add("Box")
    for k, v in (("VIn", h_eye), ("VOut", h), ("XMin", -12), ("XMax", 12), ("YMin", -9), ("YMax", 9),
                 ("ZMin", -1), ("ZMax", 24), ("Thickness", 3)):
        gmsh.model.mesh.field.setNumber(f, k, v)
    gmsh.model.mesh.field.setAsBackgroundMesh(f)
    gmsh.option.setNumber("Mesh.MeshSizeExtendFromBoundary", 0)
    gmsh.option.setNumber("Mesh.MeshSizeMax", h); gmsh.option.setNumber("Mesh.MeshSizeMin", h_eye / 2)
    gmsh.option.setNumber("Mesh.ElementOrder", 2); gmsh.option.setNumber("Mesh.HighOrderOptimize", 1)
    gmsh.model.mesh.generate(3)
    tags, xyz, _ = gmsh.model.mesh.getNodes()
    node_xyz = dict(zip(tags.tolist(), np.asarray(xyz).reshape(-1, 3)))
    et, _, en = gmsh.model.mesh.getElements(3)
    tets = np.asarray(en[list(et).index(11)]).reshape(-1, 10).astype(int)
    def gn(name):
        for d, t_ in gmsh.model.getPhysicalGroups(2):
            if gmsh.model.getPhysicalName(d, t_) == name:
                return np.unique(gmsh.model.mesh.getNodesForPhysicalGroup(d, t_)[0]).astype(int)
    out = {"node_xyz": node_xyz, "tets": tets, "bore_nodes": gn("BORE"), "tip_nodes": gn("TIP"),
           "n_outer": len(outer), "n_roof": len(roof)}
    gmsh.finalize()
    return out


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--rev", type=int, default=2)
    ap.add_argument("--load", type=float, default=686.0); ap.add_argument("--name", default=None)
    ap.add_argument("--mesh", type=float, default=1.5); ap.add_argument("--eye-mesh", type=float, default=0.4)
    ap.add_argument("--step", default=None, help="any bulkhead STEP (default: parts model rev)")
    ap.add_argument("--load-box", default=None, help="xmin,xmax,ymin,ymax,zmin,zmax of the cord-contact faces")
    ap.add_argument("--r-fix", type=float, default=None, help="faces with all samples beyond this radius are fixed (bond)")
    ap.add_argument("--tag", default=None)
    a = ap.parse_args()
    p = K.params()
    step = Path(a.step) if a.step else ROOT / f"out/kevlar_bulkhead/rev{a.rev}/kevlar_bulkhead_rev{a.rev}.step"
    work = ROOT / f"out/fea/kevlar_bulkhead_{a.tag or f'rev{a.rev}'}/{a.name or f'Z{a.load:g}'}"
    lb = [float(v) for v in a.load_box.split(",")] if a.load_box else None
    work.mkdir(parents=True, exist_ok=True)
    m = mesh(step, p, a.mesh, a.eye_mesh, work, load_box=lb, r_fix=a.r_fix)
    print(f"faces: outer {m['n_outer']}, roof {m['n_roof']}; nodes {len(m['node_xyz'])}, tets {len(m['tets'])}")
    job = work / "job"
    F.write_deck(m, {"Z": a.load}, job)
    subprocess.run(["ccx", "-i", str(job)], cwd=work, capture_output=True, check=True)
    disp, stress = F.read_frd(job.with_suffix(".frd"))
    xyz = m["node_xyz"]; roof = set(int(n) for n in m["tip_nodes"])
    roof_pts = np.array([xyz[n] for n in roof])
    from scipy.spatial import cKDTree
    tree = cKDTree(roof_pts)
    res = []
    for n, s in stress.items():
        x = xyz[n]
        d = tree.query(x)[0]
        sxx, syy, szz, sxy, syz, szx = s[:6]
        inplane = 0.5 * (sxx + syy) + np.sqrt((0.5 * (sxx - syy)) ** 2 + sxy ** 2)
        tau_z = np.hypot(syz, szx)
        res.append((n, szz, inplane, tau_z, d, x))
    keep = [r for r in res if r[4] > 1.0]           # exclude the load-application faces
    sz = max(keep, key=lambda r: r[1]); ip = max(keep, key=lambda r: r[2]); tz = max(keep, key=lambda r: r[3])
    umax = max(np.linalg.norm(v[:3]) for v in disp.values())
    out = dict(load_N=a.load, SZ_max_MPa=sz[1], SZ_at=sz[5].round(2).tolist(), FI_z=sz[1] / F.Z_STRENGTH_MPA,
               inplane_max_MPa=ip[2], inplane_at=ip[5].round(2).tolist(), interlayer_shear_max_MPa=tz[3],
               tau_at=tz[5].round(2).tolist(), FI_shear=tz[3] / 15.0, u_max_mm=umax,
               nodes=len(m["node_xyz"]), tets=len(m["tets"]))
    (work / "result.json").write_text(json.dumps(out, indent=1, default=float))
    fi = {n: max(r[1], 0) / F.Z_STRENGTH_MPA for n, *r in [(r[0], r[1]) for r in res]}
    F.render(m, fi, work / "fi.png", f"Kevlar bulkhead {a.tag or 'rev %d' % a.rev}: {a.load:g} N Kevlar pull, FI = SZ/19 MPa", zoom=False)
    print(json.dumps(out, indent=1, default=float))


if __name__ == "__main__":
    main()
