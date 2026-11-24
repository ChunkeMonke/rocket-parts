"""Outer mould line of the full SolidWorks assembly (Ms.Piggy_Assembly.STEP) for CFD.

  .venv/bin/python tools/rocket_oml_asm.py        (parts exported to out/msp/part_*.stl first)

Union of the nose cone, body tube, fin can and tail cone as placed in the assembly (fin-can aft face z = 0, nose
tip +z), with the bores, threads, motor and nose cavities filled; only the outer shell is kept.
Writes out/cfd/rocket_oml_asm.stl and out/msp/oml_side.png.
"""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import trimesh

ROOT = Path(__file__).resolve().parent.parent
P = ROOT / "out/msp"


def cyl(r, z0, z1):
    c = trimesh.creation.cylinder(radius=r, height=z1 - z0, sections=256)
    c.apply_translation([0, 0, (z0 + z1) / 2]); return c


def main():
    parts = [trimesh.load(P / f"part_{n}.stl", force="mesh") for n in
             ("L1-Rocket-FinCan", "FinCanBottom", "nose_cone_rev1")]
    tube = trimesh.load(P / "part_BodyTubeLOC.stl", force="mesh")      # plain cylinder: rebuilt exactly
    r_t = float(np.hypot(tube.vertices[:, 0], tube.vertices[:, 1]).max())
    parts.append(cyl(r_t, float(tube.bounds[0][2]), float(tube.bounds[1][2])))
    for n, m in zip(("fincan", "cone", "nose", "tube"), parts):
        print(n, "watertight", m.is_watertight, "volume", round(m.volume / 1000, 1), "cm3")
    fill = [cyl(21.0, -28.9, 158.0),        # fin-can bore, collar, cone cavity
            cyl(20.2, -29.99, -28.0),       # nozzle opening -> flat base
            cyl(22.6, -1.0, 12.0),          # thread gaps
            cyl(20.3, 150.0, 900.0),        # tube interior
            cyl(19.5, 880.0, 890.0)]        # nose shoulder joint (inner cavities are dropped with the inner shells)
    oml = trimesh.boolean.union(parts + fill, engine="manifold")
    comps = oml.split(only_watertight=False)
    outer = max(comps, key=lambda c: abs(c.volume))
    print("components", len(comps), "-> outer volume", round(outer.volume / 1000, 1), "cm3")
    outer.export(ROOT / "out/cfd/rocket_oml_asm.stl")
    tip = outer.bounds[1][2]
    r = np.hypot(outer.vertices[:, 0], outer.vertices[:, 1])
    print(f"OML: z {outer.bounds[0][2]:.1f}..{tip:.1f} (length {np.ptp(outer.vertices[:, 2]):.1f}), max r {r.max():.2f}, "
          f"watertight {outer.is_watertight}, faces {len(outer.faces)}")
    s = outer.section([0, 1, 0], [0, 0, 0])
    fig, ax = plt.subplots(2, 1, figsize=(14, 5))
    for a, lim in zip(ax, [(outer.bounds[0][2] - 5, tip + 5), (-40, 200)]):
        for e in s.discrete:
            a.plot(e[:, 2], e[:, 0], "k-", lw=0.8)
        a.set_xlim(*lim); a.set_aspect("equal"); a.grid(alpha=.3)
    ax[0].set_title("Ms. Piggy assembly OML (XZ section through fin 0), mm")
    fig.tight_layout(); fig.savefig(P / "oml_side.png", dpi=130)


if __name__ == "__main__":
    main()
