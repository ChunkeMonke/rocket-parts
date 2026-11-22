"""Half-section drawing of the fin can + tail cone + motor + tube assembly (y = 0 plane through fin 0).

  .venv/bin/python tools/assembly_section.py --rev 8      (after make.py fin_can_md --rev 8)
Writes out/fin_can_md/rev<N>/fin_can_md_rev<N>_assembly_section.png. Dimensions come from design.yaml via
parts/fin_can_md.params(); mating solids are the STLs make.py wrote to out/fin_can_md/rev<N>/mates/.
"""
import argparse
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import trimesh  # noqa: E402
from matplotlib.patches import Polygon  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from parts import fin_can_md as F  # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument("--rev", type=int, required=True)
a = ap.parse_args()
p = F.params()
Lc, ring, Lb = p.get("collar_length_mm", 0), p["thrust_ring_thk_mm"], p.get("boattail_length_mm", 0)
d = ROOT / "out" / "fin_can_md" / f"rev{a.rev}"
parts = [("fin can (PETG)", d / f"fin_can_md_rev{a.rev}.stl", "#e8913a"),
         ("tail cone / motor retainer (ABS/ASA)", d / "mates" / "tail_cone.stl", "#3a7be8"),
         ("airframe tube BT-1.52 (paper)", d / "mates" / "tube_wall.stl", "#b9a27a"),
         (f"motor case H100W ({p['motor_case_od_mm']} mm, PLACEHOLDER)", d / "mates" / "motor_case.stl", "#555555"),
         (f"thrust ring ({p['thrust_ring_od_mm']} OD x {ring:.1f} mm, PLACEHOLDER)", d / "mates" / "motor_thrust_ring.stl",
          "#111111")]


def section(path):
    if not path.exists():
        return []
    s = trimesh.load(path, force="mesh").section(plane_origin=[0, 0, 0], plane_normal=[0, 1, 0])
    pl, _ = s.to_2D(to_2D=np.array([[1, 0, 0, 0], [0, 0, 1, 0], [0, -1, 0, 0], [0, 0, 0, 1]]))
    return [(np.array(q.exterior.coords), [np.array(i.coords) for i in q.interiors]) for q in pl.polygons_full]


fig, axs = plt.subplots(1, 2, figsize=(15, 9.5), gridspec_kw={"width_ratios": [1, 1.35]})
for ax, (xl, zl, title) in zip(axs, (((-75, 75), (-Lc - Lb - 8, 165), "Whole fin can, cut in half (forward = up)"),
                                     ((-42, 42), (-Lc - Lb - 4, 14), "Aft end close-up: how the motor is held"))):
    for lab, path, col in parts:
        for k, (e, hs) in enumerate(section(path)):
            ax.add_patch(Polygon(e, closed=True, fc=col, ec="k", lw=0.4, alpha=0.95, label=lab if k == 0 else None))
            for h in hs:
                ax.add_patch(Polygon(h, closed=True, fc="white", ec="k", lw=0.3))
    ax.set_xlim(*xl); ax.set_ylim(*zl); ax.set_aspect("equal"); ax.grid(alpha=0.25)
    ax.set_xlabel("mm"); ax.set_ylabel("z (mm), 0 = fin can aft face"); ax.set_title(title)
ax = axs[1]
for x, z, s in [(-33, 7, "LIP: ring pushes UP on it\n(stops the motor going forward)"),
                (0, -ring / 2, "THRUST RING (the motor's 'overhang')"),
                (33, -(ring + Lc) / 2, "collar thread\n(in the fin can)"),
                (-34, -(ring + Lc) / 2, "cone shank presses UP\non the ring (retention)"),
                (33, -Lc - Lb / 2, "boattail\n46.8 → 43 mm"),
                (0, -Lc - Lb + 3, f"nozzle exit (flush with ring bottom)\n~{Lc + Lb - ring:.0f} mm inside the cone")]:
    ax.annotate(s, (x, z), fontsize=8, ha="center", va="center",
                bbox=dict(boxstyle="round,pad=0.2", fc="white", ec="0.6", alpha=0.9))
axs[0].legend(loc="upper right", fontsize=8)
fig.suptitle(f"Rev {a.rev} assembly section (collar {Lc} mm, thrust ring {ring:.1f} mm): fin can + tail cone + H100W + tube")
fig.tight_layout()
out = d / f"fin_can_md_rev{a.rev}_assembly_section.png"
fig.savefig(out, dpi=120)
print(out)
