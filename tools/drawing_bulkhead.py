"""Drawing L1C-KB-005: aft Kevlar anchor bulkhead (parts/kevlar_bulkhead.py rev 2). A3, black & white.

  .venv/bin/python tools/drawing_bulkhead.py   -> out/kevlar_bulkhead/rev2/kevlar_bulkhead_rev2_drawing.pdf/.png
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

OUT = ROOT / "out/kevlar_bulkhead/rev2"
FIG = ROOT / "projects/l1-cheap/report/figures/drawings"


def main():
    p = K.params()
    m = trimesh.load(OUT / "kevlar_bulkhead_rev2.stl", force="mesh")
    fig, paper = D.new_sheet("AFT KEVLAR ANCHOR BULKHEAD", 1, "B", "2:1", None,
                             subtitle="VENTED PLATE + OPEN KEVLAR EYE · EPOXIED IN BODY TUBE · PETG", n_sheets=1, dwg_no="L1C-KB-005",
                             drawn="rocket-parts", project="Ms. Piggy · L1 · H100W-14A", material="PETG",
                             note="Geometry cut from the part model (parts/kevlar_bulkhead.py rev 2). Do not scale: use the dimensions.",
                             finish="FDM 0.20 layer, 6 walls", tol="±0.2 · fit Ø ±0.05")
    R, L, t = p["od_mm"] / 2, p["length_mm"], p["plate_mm"]
    w, h, bar = p["eye_tunnel_w_mm"], p["eye_tunnel_h_mm"], p["eye_bar_mm"]
    top = t + h + w / 2 + bar
    # ---- section A-A across the tunnel (x-z plane at y = 0), axis vertical, forward up
    ax = D.view(fig, 42, 120, 135, 150, 2.0, 0, 12)
    s_ = m.section([0, 1, 0], [0, 0, 0])
    P, _ = s_.to_2D(to_2D=np.array([[1, 0, 0, 0], [0, 0, 1, 0], [0, -1, 0, 0], [0, 0, 0, 1]]))
    for q in P.polygons_full:
        D.hatch_poly(ax, np.array(q.exterior.coords), [np.array(hh.coords) for hh in q.interiors])
    D.centerline(ax, (0, -4), (0, L + 4))
    D.dim(ax, (-R, L), (R, L), 10, f"Ø{p['od_mm']:.3f} (SNUG IN Ø38.735 BORE)")
    D.dim(ax, (R, 0), (R, L), -12, f"{L:.1f}")
    D.dim(ax, (-R, 0), (-R, t), 8, f"{t:.1f}", inside=False)
    D.dim(ax, (-w / 2, t + 0.5), (w / 2, t + 0.5), -14, f"{w:.1f} TUNNEL", inside=False)
    D.dim(ax, (-w / 2 - p["eye_post_mm"], top), (w / 2 + p["eye_post_mm"], top), 4, f"{w + 2 * p['eye_post_mm']:.1f}")
    D.dim(ax, (w / 2 + p["eye_post_mm"], t), (w / 2 + p["eye_post_mm"], top), -4, f"{top - t:.1f}")
    D.leader(ax, (0, t + h + w / 2 - 0.3), (14, L + 7), "45° DIAMOND ROOF: PRINTS WITHOUT SUPPORTS", ha="left")
    D.leader(ax, (-R + 0.25, L * 0.7), (-22, L * 0.95), "2× EPOXY GROOVE 1.5 × 0.5 DP", ha="right")
    D.leader(ax, (-R + 0.4, 0.3), (-22, -2), "LEAD-IN 0.8×45° (INSERT FIRST)", ha="right")
    ax.text(0, -9, "FWD (NOSE) ↑   AFT (MOTOR) ↓", ha="center", fontsize=6.5)
    D.view_label(ax, (0, -12), "SECTION A-A (ACROSS THE KEVLAR TUNNEL)")
    # ---- forward view (looking aft) and aft view
    for i, (title, fwd) in enumerate([("FORWARD FACE (LOOKING AFT)", True), ("AFT FACE (LOOKING FORWARD)", False)]):
        v = D.view(fig, 180 + i * 115, 165, 105, 105, 2.0, 0, 0)
        v.add_patch(Circle((0, 0), R, fill=False, lw=D.LW_VIS)); v.add_patch(Circle((0, 0), R - p["wall_mm"], fill=False, lw=D.LW_THIN))
        for k in range(6):
            a = math.radians(60 * k)
            v.add_patch(Circle((p["vent_r_mm"] * math.cos(a), p["vent_r_mm"] * math.sin(a)), p["vent_d_mm"] / 2, fill=False, lw=D.LW_VIS))
        xo, le = w / 2 + p["eye_post_mm"], p["eye_length_mm"]
        v.add_patch(Rectangle((-xo, -le / 2), 2 * xo, le, fill=False, lw=D.LW_VIS if fwd else D.LW_THIN, ls="-" if fwd else (0, (4, 2))))
        if fwd:
            v.plot([-w / 2, -w / 2], [-le / 2, le / 2], color="k", lw=D.LW_THIN, ls=(0, (4, 2)))
            v.plot([w / 2, w / 2], [-le / 2, le / 2], color="k", lw=D.LW_THIN, ls=(0, (4, 2)))
            v.annotate("", (0, le / 2 + 6), (0, -le / 2 - 6), arrowprops=dict(arrowstyle="<->", lw=0.6))
            v.text(1.5, -le / 2 - 7.5, "KEVLAR THROUGH TUNNEL", fontsize=5.5)
            v.text(0, le / 2 + 1.2, f"EYE {2 * xo:.0f} × {le:.0f}", fontsize=5.5, ha="center")
        D.centerline(v, (-R - 3, 0), (R + 3, 0)); D.centerline(v, (0, -R - 3), (0, R + 3))
        D.leader(v, (p["vent_r_mm"], 0), (R - 2, R + 3), f"6× Ø{p['vent_d_mm']:.1f} ON R{p['vent_r_mm']} @60°", ha="left")
        D.view_label(v, (0, -R - 6), title)
    # ---- installation sketch (tube, nose shoulder, pack, bulkhead) not to scale
    paper.text(182, 145, "INSTALLATION (IN BT-1.52, FROM THE FORWARD END)", fontsize=8, weight="bold")
    x0, y0, s = 182, 118, 0.62       # mm paper per mm model (sketch scale, along the tube)
    paper.add_patch(Rectangle((x0, y0), 230 * s / 0.62 * 0.62, 12, fill=False, lw=0.8))
    paper.add_patch(Rectangle((x0, y0 + 1.5), 45 * s, 9, fc="0.85", ec="k", lw=0.5)); paper.text(x0 + 2, y0 + 5.5, "NOSE SHOULDER", fontsize=5)
    paper.add_patch(Rectangle((x0 + 45 * s, y0 + 1.5), 131.6 * s, 9, fill=False, ec="k", lw=0.4, ls=(0, (3, 2))))
    paper.text(x0 + (45 + 40) * s, y0 + 5.5, "CHUTE + CORD + WADDING (131.6)", fontsize=5)
    paper.add_patch(Rectangle((x0 + (45 + 131.6) * s, y0), 24 * s, 12, fc="0.3", ec="k", lw=0.6))
    paper.text(x0 + (45 + 131.6) * s, y0 - 4, "BULKHEAD FWD EDGE 176.6 FROM TUBE FWD END = 340 FROM NOSE TIP", fontsize=5.5)
    paper.text(x0 + 230 * s - 2, y0 + 5.5, "→ MOTOR", fontsize=5.5, ha="right")
    notes = ["NOTES",
             "1. PRINT AFT FACE DOWN, AXIS VERTICAL, NO SUPPORTS (NO ENCLOSED CAVITY). 0.20 mm LAYERS, 6 WALLS. ≈ 14–15 g.",
             "2. DRY-FIT FIRST: SNUG SLIDE, NO FORCE. IF TIGHT, SAND OD LIGHTLY; IF LOOSE, A FULL EPOXY FILM FILLS ≤ 0.2 mm.",
             "3. KEVLAR: PASS THE CORD STRAIGHT THROUGH THE TUNNEL AND TIE A FIGURE-8 ON A BIGHT (OR A BOWLINE) ROUND THE EYE.",
             "   TIE IT BEFORE GLUING; LEAVE THE LONG END RUNNING FORWARD TO THE CHUTE AND NOSE.",
             "4. EPOXY (30-MIN OR SLOWER): COAT THE TUBE BORE AT THE MARK AND THE BULKHEAD OD; PUSH IN AFT END FIRST WITH A DOWEL",
             "   MARKED AT 176.6 mm; WIPE EXCESS FROM THE VENTS; CURE AXIS VERTICAL, FORWARD END UP.",
             "5. KEEP ALL 6 VENTS OPEN: EJECTION GAS MUST PASS TO DEPLOY THE PARACHUTE. LOC REUSABLE WADDING PROTECTS THE CHUTE.",
             "6. LOADS: SNATCH ≤ 686 N; EYE POSTS 5.7 MPa ACROSS LAYERS; BAR 14 MPa; EPOXY BOND ≈ 2.9 kN."]
    for k, t in enumerate(notes):
        paper.text(182, 100 - k * 5.2, t, fontsize=6.2 if k else 7.5, weight="bold" if k == 0 else "normal")
    FIG.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT / "kevlar_bulkhead_rev2_drawing.pdf"); fig.savefig(FIG / "kevlar_bulkhead_sheet.png", dpi=170)
    print(OUT / "kevlar_bulkhead_rev2_drawing.pdf")


if __name__ == "__main__":
    main()
