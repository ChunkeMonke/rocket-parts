"""Drawing L1C-KB-005: aft Kevlar anchor bulkhead (parts/kevlar_bulkhead.py rev 1). A3, black & white.

  .venv/bin/python tools/drawing_bulkhead.py   -> out/kevlar_bulkhead/rev1/kevlar_bulkhead_rev1_drawing.pdf/.png
"""
import math
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import trimesh
from matplotlib.patches import Circle, Rectangle

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools")); sys.path.insert(0, str(ROOT))
import drawing as D  # noqa: E402
from parts import kevlar_bulkhead as K  # noqa: E402

OUT = ROOT / "out/kevlar_bulkhead/rev1"
FIG = ROOT / "projects/l1-cheap/report/figures/drawings"


def main():
    p = K.params()
    m = trimesh.load(OUT / "kevlar_bulkhead_rev1.stl", force="mesh")
    fig, paper = D.new_sheet("AFT KEVLAR ANCHOR BULKHEAD", 1, "A", "2:1", None,
                             subtitle="PRINTED BAFFLE · EPOXIED IN BODY TUBE · PETG", n_sheets=1, dwg_no="L1C-KB-005",
                             drawn="rocket-parts", project="Ms. Piggy · L1 · H100W-14A", material="PETG",
                             note="Geometry cut from the part model (parts/kevlar_bulkhead.py rev 1). Do not scale: use the dimensions.",
                             finish="FDM 0.20 layer, 6 walls", tol="±0.2 · fit Ø ±0.05")
    R, L = p["od_mm"] / 2, p["length_mm"]
    ta, g, tf = p["aft_plate_mm"], p["gap_mm"], p["fwd_plate_mm"]
    # ---- section A-A through the Kevlar holes (x-z plane), axis vertical, forward up
    ax = D.view(fig, 42, 120, 135, 150, 2.0, 0, 13)
    s = m.section([0, 1, 0], [0, 0, 0])
    P, _ = s.to_2D(to_2D=np.array([[1, 0, 0, 0], [0, 0, 1, 0], [0, -1, 0, 0], [0, 0, 0, 1]]))
    for q in P.polygons_full:
        D.hatch_poly(ax, np.array(q.exterior.coords), [np.array(h.coords) for h in q.interiors])
    D.centerline(ax, (0, -4), (0, L + 4))
    D.dim(ax, (-R, L), (R, L), 10, f"Ø{p['od_mm']:.3f} (SNUG IN Ø38.735 BORE)")
    D.dim(ax, (R, 0), (R, L), -12, f"{L:.1f}")
    D.dim(ax, (-R, 0), (-R, ta), 8, f"{ta:.1f}", inside=False)
    D.dim(ax, (-R, ta + g), (-R, ta + g + tf), 8, f"{tf:.1f}", inside=False)
    D.dim(ax, (-7, ta + g + tf + 0.5), (7, ta + g + tf + 0.5), 18, "14.0")
    D.leader(ax, (7, ta + g + tf - 0.3), (14, L + 8), "2× Ø5.0 KEVLAR HOLES, 0.5×45° BOTH ENDS", ha="left")
    D.leader(ax, (0, ta + g / 2), (-14, -6), f"PILLAR Ø{p['pillar_d_mm']:.0f} (CORD WRAPS ROUND IT)", ha="right")
    D.leader(ax, (-R + 0.25, L * 0.3), (-26, L * 0.45), "2× EPOXY GROOVE 1.5 × 0.5 DP", ha="right")
    D.leader(ax, (-R + 0.4, 0.3), (-22, -2), "LEAD-IN 0.8×45° (INSERT FIRST)", ha="right")
    ax.text(0, -9, "FWD (NOSE) ↑   AFT (MOTOR) ↓", ha="center", fontsize=6.5)
    D.view_label(ax, (0, -12), "SECTION A-A (THROUGH KEVLAR HOLES)")
    # ---- forward view (looking aft) and aft view
    for i, (title, vents, vr, vd, kev) in enumerate([
            ("FORWARD FACE (LOOKING AFT)", [60 * k + 30 for k in range(6)], p["fwd_vent_r_mm"], p["fwd_vent_d_mm"], True),
            ("AFT FACE (LOOKING FORWARD)", [60 * k for k in range(6)], p["aft_vent_r_mm"], p["aft_vent_d_mm"], False)]):
        v = D.view(fig, 180 + i * 115, 165, 105, 105, 2.0, 0, 0)
        v.add_patch(Circle((0, 0), R, fill=False, lw=D.LW_VIS)); v.add_patch(Circle((0, 0), R - p["wall_mm"], fill=False, lw=D.LW_THIN))
        for a in vents:
            c = (vr * math.cos(math.radians(a)), vr * math.sin(math.radians(a)))
            v.add_patch(Circle(c, vd / 2, fill=False, lw=D.LW_VIS))
        if kev:
            for x in (-7, 7):
                v.add_patch(Circle((x, 0), 2.5, fill=False, lw=D.LW_VIS)); v.add_patch(Circle((x, 0), 3.0, fill=False, lw=D.LW_THIN))
            v.add_patch(Circle((0, 0), p["pillar_d_mm"] / 2, fill=False, lw=D.LW_THIN, ls=(0, (4, 2))))
        D.centerline(v, (-R - 3, 0), (R + 3, 0)); D.centerline(v, (0, -R - 3), (0, R + 3))
        c0 = (vr * math.cos(math.radians(vents[0])), vr * math.sin(math.radians(vents[0])))
        D.leader(v, c0, (R - 2, R + 3), f"6× Ø{vd:.0f} ON R{vr} @60°" + (" (30° OFFSET)" if kev else ""), ha="left")
        D.view_label(v, (0, -R - 6), title)
    # ---- installation sketch (tube, nose shoulder, pack, bulkhead) not to scale
    paper.text(182, 145, "INSTALLATION (IN BT-1.52, FROM THE FORWARD END)", fontsize=8, weight="bold")
    x0, y0, s = 182, 118, 0.62       # mm paper per mm model (sketch scale, along the tube)
    paper.add_patch(Rectangle((x0, y0), 230 * s / 0.62 * 0.62, 12, fill=False, lw=0.8))
    paper.add_patch(Rectangle((x0, y0 + 1.5), 45 * s, 9, fc="0.85", ec="k", lw=0.5)); paper.text(x0 + 2, y0 + 5.5, "NOSE SHOULDER", fontsize=5)
    paper.add_patch(Rectangle((x0 + 45 * s, y0 + 1.5), 131.6 * s, 9, fill=False, ec="k", lw=0.4, ls=(0, (3, 2))))
    paper.text(x0 + (45 + 40) * s, y0 + 5.5, "CHUTE + CORD + WADDING (131.6)", fontsize=5)
    paper.add_patch(Rectangle((x0 + (45 + 131.6) * s, y0), 26 * s, 12, fc="0.3", ec="k", lw=0.6))
    paper.text(x0 + (45 + 131.6) * s, y0 - 4, "BULKHEAD FWD FACE 176.6 FROM TUBE FWD END = 340 FROM NOSE TIP", fontsize=5.5)
    paper.text(x0 + 230 * s - 2, y0 + 5.5, "→ MOTOR", fontsize=5.5, ha="right")
    notes = ["NOTES",
             "1. PRINT AFT FACE DOWN, AXIS VERTICAL, NO SUPPORTS. 0.20 mm LAYERS, 6 WALLS (FULLY SOLID). ≈ 14–15 g.",
             "2. DRY-FIT FIRST: SNUG SLIDE, NO FORCE. IF TIGHT, SAND OD LIGHTLY; IF LOOSE, A FULL EPOXY FILM FILLS ≤ 0.2 mm.",
             "3. TIE KEVLAR BEFORE GLUING: DOWN ONE HOLE, ROUND THE PILLAR, UP THE OTHER; KNOT ON THE FORWARD FACE.",
             "4. EPOXY (30-MIN OR SLOWER): COAT TUBE BORE 20–40 mm PAST THE MARK AND THE BULKHEAD OD; PUSH IN AFT END FIRST",
             "   WITH A DOWEL MARKED AT 176.6 mm; WIPE EXCESS FROM THE VENTS; CURE AXIS VERTICAL, FORWARD END UP.",
             "5. KEEP ALL 12 VENTS OPEN: EJECTION GAS MUST PASS THE BAFFLE TO DEPLOY THE PARACHUTE.",
             "6. LOADS: SNATCH ≤ 686 N (20 m/s SEPARATION); EPOXY BOND ≈ 3.1 kN; FWD PLATE IN-PLANE BENDING ≈ 16 MPa."]
    for k, t in enumerate(notes):
        paper.text(182, 100 - k * 5.2, t, fontsize=6.2 if k else 7.5, weight="bold" if k == 0 else "normal")
    FIG.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT / "kevlar_bulkhead_rev1_drawing.pdf"); fig.savefig(FIG / "kevlar_bulkhead_sheet.png", dpi=170)
    print(OUT / "kevlar_bulkhead_rev1_drawing.pdf")


if __name__ == "__main__":
    main()
