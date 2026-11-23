"""OML of the rocket built from the OWNER's SolidWorks STEP files (fin can + tail cone), for 3D CFD.

  .venv/bin/python tools/rocket_oml_owner.py

Inputs: projects/l1-cheap/owner_cad/L1-Rocket-FinCan.STEP, FinCanBottom.STEP (owner 2026-11-23, fin tip r 69.5,
span 46.1 mm on the r 23.40 sleeve, intentional). Frame as tools/rocket_oml.py: fin-can aft face z = 0, nose +Z,
fin 0 along +X. Tail cone seated as checked in the thread review (shoulder at the collar aft face, dz = -29.89).
Tube (OD from design.yaml) starts on the owner's lip (top z = 21.17); nose = design.yaml tangent ogive.
Inner bores, threads, motor cavity and the cone nozzle cavity are filled (not aero).
Writes out/cfd/rocket_oml_owner.stl and a side-view PNG.
"""
from __future__ import annotations

import math
from pathlib import Path

import cadquery as cq
import numpy as np
import trimesh
import yaml

ROOT = Path(__file__).resolve().parent.parent
CAD = ROOT / "projects" / "l1-cheap" / "owner_cad"
OUT = ROOT / "out" / "cfd"
TIP_FLAT_R = 0.3
CONE_DZ = -29.89          # seated position (thread review 2026-11-23, overlap 0 at 0 deg)
LIP_TOP = 21.17           # owner fin can: lip z 18.5..21.17 (bore 38.42)


def step_mesh(path: Path) -> trimesh.Trimesh:
    s = cq.importers.importStep(str(path))
    tmp = OUT / (path.stem + "_tmp.stl")
    cq.exporters.export(s, str(tmp), tolerance=0.03, angularTolerance=0.1)
    m = trimesh.load(tmp, force="mesh"); tmp.unlink()
    return m


def revolve(prof: list[tuple[float, float]], n: int = 256) -> trimesh.Trimesh:
    """Closed solid of revolution from (r, z) points going from the axis round to the axis."""
    m = trimesh.creation.revolve(np.array(prof), sections=n)
    if m.volume < 0: m.invert()
    return m


def cyl(r: float, z0: float, z1: float) -> trimesh.Trimesh:
    c = trimesh.creation.cylinder(radius=r, height=z1 - z0, sections=256)
    c.apply_translation([0, 0, (z0 + z1) / 2]); return c


def main() -> None:
    d = yaml.safe_load((ROOT / "projects" / "l1-cheap" / "design.yaml").read_text())
    R = float(d["fin_can_md"]["tube_od_mm"]["value"]) / 2
    L_nose = float(d["nosecone"]["length_mm"]); L_tube = float(d["stability"]["body_tube_length_mm"])
    fc = step_mesh(CAD / "L1-Rocket-FinCan.STEP")
    cn = step_mesh(CAD / "FinCanBottom.STEP"); cn.apply_translation([0, 0, CONE_DZ])
    z_nose = LIP_TOP + L_tube
    rho = (R * R + L_nose * L_nose) / (2 * R)
    og = []
    for i in range(301):
        x = L_nose * i / 300
        r = math.sqrt(max(rho * rho - (L_nose - x) ** 2, 0)) + R - rho
        if r >= TIP_FLAT_R: og.append((r, z_nose + L_nose - x))
    nose = revolve([(0, og[0][1])] + og + [(R, z_nose - 1.0), (0, z_nose - 1.0)])
    parts = [fc, cn, nose,
             cyl(21.0, CONE_DZ + 1.0, 158.0),        # fills cone cavity, collar/thread bore, sleeve-tube gap
             cyl(20.2, CONE_DZ, CONE_DZ + 1.5),      # fills the nozzle opening to a flat base
             cyl(22.6, -1.0, 12.0),                  # fills the sealed thread gaps (collar/shank)
             cyl(R, 150.0, z_nose + 0.5)]            # tube
    oml = trimesh.boolean.union(parts, engine="manifold")
    oml.merge_vertices()
    OUT.mkdir(parents=True, exist_ok=True)
    oml.export(OUT / "rocket_oml_owner.stl")
    print(f"OML owner: watertight {oml.is_watertight}, length {oml.extents[2]:.1f} mm, "
          f"fin tip r {np.hypot(oml.vertices[:,0], oml.vertices[:,1]).max():.2f}, faces {len(oml.faces)}")
    import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
    fig, ax = plt.subplots(2, 1, figsize=(14, 5), gridspec_kw={"height_ratios": [1, 1.4]})
    for a, (lo, hi) in zip(ax, [(oml.bounds[0, 2] - 5, oml.bounds[1, 2] + 5), (-35, 170)]):
        sec = oml.section([0, 1, 0], [0, 0, 0])
        for e in sec.discrete:
            a.plot(e[:, 2], e[:, 0], "k-", lw=0.8)
        a.set_xlim(lo, hi); a.set_aspect("equal"); a.grid(alpha=0.3)
    ax[0].set_title("Flight configuration OML (XZ section through fin 0): full rocket / aft end, mm")
    fig.tight_layout(); fig.savefig(OUT / "rocket_oml_owner_side.png", dpi=130)


if __name__ == "__main__":
    main()
