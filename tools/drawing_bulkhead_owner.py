"""Drawing L1C-KB-005 Rev C: aft Kevlar bulkhead, SolidWorks design (owner_cad/Bulkhead_Ms_Piggy.STEP). A3, B&W.

  .venv/bin/python tools/drawing_bulkhead_owner.py  -> out/kevlar_bulkhead/owner/kb_owner_drawing.pdf (+ report PNG)
"""
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import numpy as np
import trimesh
from matplotlib.patches import Rectangle

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
import drawing as D  # noqa: E402

OUT = ROOT / "out/kevlar_bulkhead/owner"
FIG = ROOT / "projects/l1-cheap/report/figures/drawings"


def polys(mesh, normal, origin, to2d):
    s = mesh.section(normal, origin)
    P, _ = s.to_2D(to_2D=to2d)
    return P.polygons_full


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    m = trimesh.load(ROOT / "out/kevlar_bulkhead/owner_bulkhead.stl", force="mesh")
    fig, paper = D.new_sheet("AFT KEVLAR ANCHOR BULKHEAD", 1, "C", "2:1", None,
                             subtitle="SOLIDWORKS DESIGN · SOLID VENTED PLUG · EPOXIED IN BODY TUBE · PETG", n_sheets=1,
                             dwg_no="L1C-KB-005", drawn="rocket-parts", project="Ms. Piggy · L1 · H100W-14A",
                             material="PETG", finish="FDM 0.20 layer, 6 walls, 25 % gyroid", tol="±0.2 · fit Ø ±0.05",
                             note="Geometry cut from Bulkhead_Ms_Piggy.STEP (SolidWorks). Do not scale: use the dimensions.")
    # section A-A through the Kevlar holes (x-z, y = 0), forward up
    ax = D.view(fig, 42, 118, 135, 150, 2.0, 0, 12.5)
    for q in polys(m, [0, 1, 0], [0, 0, 0], np.array([[1, 0, 0, 0], [0, 0, 1, 0], [0, -1, 0, 0], [0, 0, 0, 1]])):
        D.hatch_poly(ax, np.array(q.exterior.coords), [np.array(h.coords) for h in q.interiors])
    D.centerline(ax, (0, -4), (0, 29))
    R = 19.278
    D.dim(ax, (-R, 25), (R, 25), 10, "Ø38.556 (SNUG IN Ø38.735 BORE)")
    D.dim(ax, (R, 0), (R, 25), -12, "25.0")
    D.dim(ax, (-8, 0), (-2, 0), -10, "Ø6.0", inside=False)
    D.dim(ax, (-5, 25), (5, 25), 4, "10.0")
    D.dim(ax, (-2, 12.5), (2, 12.5), 0, "4.0 WEB")
    D.leader(ax, (-R + 0.5, 14.5), (-22, 22), "3× SAWTOOTH EPOXY GROOVE, 1.0 DP", ha="right")
    D.leader(ax, (1.8, 0.6), (12, -5), "CORD BEARS HERE (WEB UNDERSIDE, R2 ROUNDED)", ha="left")
    ax.text(0, -9, "FWD (NOSE) ↑   AFT (MOTOR) ↓", ha="center", fontsize=6.5)
    D.view_label(ax, (0, -12), "SECTION A-A (THROUGH KEVLAR HOLES)")
    # forward face (looking aft): section at mid-thickness shows every hole
    v = D.view(fig, 190, 165, 105, 105, 2.0, 0, 0)
    for q in polys(m, [0, 0, 1], [0, 0, 12.5], np.array([[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, -12.5], [0, 0, 0, 1]])):
        D.outline(v, np.array(q.exterior.coords))
        for h in q.interiors:
            D.outline(v, np.array(h.coords))
    v.add_patch(__import__("matplotlib").patches.Circle((0, 0), R, fill=False, lw=D.LW_THIN, ls=(0, (4, 2))))
    D.centerline(v, (-22, 0), (22, 0)); D.centerline(v, (0, -22), (0, 22))
    D.leader(v, (0, 12), (8, 22), "6× Ø6.0 VENT ON R12 @60° (30°, 90° …)", ha="left")
    D.leader(v, (5, 0), (13, -16), "2× Ø6.0 KEVLAR HOLE @ (±5, 0)", ha="left")
    D.view_label(v, (0, -24), "FORWARD FACE (LOOKING AFT)")
    # Kevlar path sketch (side view, schematic)
    k = D.view(fig, 300, 165, 105, 105, 2.0, 0, 12.5)
    k.add_patch(Rectangle((-19.3, 0), 38.6, 25, fill=False, lw=D.LW_VIS))
    for x in (-5, 5):
        k.add_patch(Rectangle((x - 3, 0), 6, 25, fill=False, lw=D.LW_THIN, ls=(0, (3, 2))))
    path = np.array([[-5, 40], [-5, -1.5], [-3.5, -3], [3.5, -3], [5, -1.5], [5, 34], [4, 36], [-4, 36]])
    k.plot(path[:, 0], path[:, 1], "k-", lw=1.6)
    k.text(-6, 41, "TO CHUTE / NOSE", fontsize=5.5, ha="right"); k.text(0, -6.5, "CORD ACROSS AFT FACE", fontsize=5.5, ha="center")
    k.text(0, 37.5, "FIGURE-8 KNOT", fontsize=5.5, ha="center")
    D.view_label(k, (0, -11), "KEVLAR PATH (SCHEMATIC)")
    # installation + notes
    paper.text(182, 112, "INSTALLATION: FWD FACE 340 FROM NOSE TIP (176.6 INSIDE THE TUBE'S FORWARD END)", fontsize=7, weight="bold")
    notes = ["NOTES",
             "1. PRINT FLAT (AFT FACE DOWN), NO SUPPORTS. 0.20 mm LAYERS, 6 WALLS, 25 % GYROID ≈ 25 g (MODEL 23.6–27.9 g).",
             "2. DRY-FIT: SNUG SLIDE IN THE TUBE, NO FORCE. SAND OD LIGHTLY IF TIGHT.",
             "3. KEVLAR BEFORE GLUING: DOWN ONE Ø6 HOLE, ACROSS THE AFT FACE UNDER THE 4 mm WEB, UP THE OTHER HOLE;",
             "   TIE A FIGURE-8 (OR DOUBLE FISHERMAN'S) ON THE FORWARD SIDE. LONG END RUNS FORWARD TO CHUTE AND NOSE.",
             "4. EPOXY: COAT THE BORE AT THE MARK AND THE OD (FILL THE GROOVES); PUSH IN AFT FACE FIRST WITH A DOWEL",
             "   MARKED AT 176.6 mm; CLEAR THE 6 VENTS; CURE AXIS VERTICAL, FORWARD END UP.",
             "5. LOAD PATH: CORD PRESSES THE WEB FORWARD = COMPRESSION AND IN-LAYER BENDING (LAYERS HORIZONTAL).",
             "6. ALSO ACTS AS FORWARD BALLAST: ≈ 25 g AT 352 mm FROM THE TIP GIVES ≈ 1.9 CAL WITHOUT NOSE BALLAST."]
    for i, t in enumerate(notes):
        paper.text(182, 102 - i * 5.0, t, fontsize=6.0 if i else 7.5, weight="bold" if i == 0 else "normal")
    FIG.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT / "kb_owner_drawing.pdf"); fig.savefig(FIG / "kevlar_bulkhead_owner_sheet.png", dpi=170)
    print(OUT / "kb_owner_drawing.pdf")


if __name__ == "__main__":
    main()
