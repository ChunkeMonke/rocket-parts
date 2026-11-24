"""Engineering drawing set for the flight vehicle "Ms. Piggy" (SolidWorks fin can + tail cone), black & white, A3.

  .venv/bin/python tools/drawing_owner.py

Sheets: 1 general arrangement (1:3, parts list, stations, CG/CP), 2 aft-end assembly section A-A + aft view (1:1),
3 fin can (section, fin planform, fin section B-B), 4 tail cone / motor retainer.
Geometry is cut from the SolidWorks STEP files (projects/l1-cheap/owner_cad/), dimensions measured from the same solids.
Writes out/owner/drawings/ms_piggy_drawings.pdf and one PNG per sheet (also copied to the report figures).
"""
from __future__ import annotations

import shutil
import sys
from pathlib import Path

import cadquery as cq
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import trimesh  # noqa: E402
from matplotlib.backends.backend_pdf import PdfPages  # noqa: E402
from matplotlib.patches import Circle, Polygon, Rectangle  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
import drawing as D  # noqa: E402

CAD = ROOT / "projects/l1-cheap/owner_cad"
OUT = ROOT / "out/owner/drawings"
FIG = ROOT / "projects/l1-cheap/report/figures/drawings"
CONE_DZ = -29.89                 # seated tail cone (shoulder on the collar aft face)
TIP = 1047.5                     # nose tip z in the OML frame (fin-can aft face z = 0)
N = 4
REV = "C"
KW = dict(drawn="rocket-parts", project="Ms. Piggy · L1 · H100W-14A", material="PETG",
          note="Geometry cut from the SolidWorks STEP solids; stations from the nose tip. Do not scale: use the dimensions.",
          finish="FDM 0.20 layer, 6 walls", tol="±0.2 · angles ±0.5°")


def mesh(name: str) -> trimesh.Trimesh:
    OUT.mkdir(parents=True, exist_ok=True)
    stl = OUT / (name + ".stl")
    if not stl.exists():
        cq.exporters.export(cq.importers.importStep(str(CAD / (name + ".STEP"))), str(stl), tolerance=0.02,
                            angularTolerance=0.08)
    return trimesh.load(stl, force="mesh")


def sec_xz(m, flip=False, dz=0.0):
    """Section y = 0 as polygons in (u, r): u = -z (aft to the right) unless flip."""
    out = []
    for ext, holes in D.section_y0(m):
        f = (lambda a: np.c_[(a[:, 0] + dz), a[:, 1]]) if flip else (lambda a: np.c_[-(a[:, 0] + dz), a[:, 1]])
        out.append((f(ext), [f(h) for h in holes]))
    return out


def sheet(title, n, scale, subtitle, dwg):
    fig, paper = D.new_sheet(title, n, REV, scale, None, subtitle=subtitle, n_sheets=N, dwg_no=dwg, **KW)
    return fig, paper


def parts_table(paper, x, y, rows, widths):
    h = 5.2
    heads = ["ITEM", "DESCRIPTION", "MATERIAL / SPEC", "QTY", "MASS g"]
    yy = y
    for r, cells in enumerate([heads] + rows):
        xx = x
        for c, w in zip(cells, widths):
            paper.add_patch(Rectangle((xx, yy), w, h, fill=(r == 0), fc="0.88", ec="k", lw=0.35))
            paper.text(xx + 1.2, yy + h / 2, str(c), fontsize=5.6, va="center", weight="bold" if r == 0 else "normal")
            xx += w
        yy -= h


# ------------------------------------------------------------------ sheet 1: general arrangement
def sheet1(pdf, oml):
    fig, paper = sheet("MS. PIGGY — GENERAL ARRANGEMENT", 1, "1:3", "L1 MINIMUM-DIAMETER ROCKET · H100W-14A", "L1C-GA-001")
    ax = D.view(fig, 18, 175, 384, 100, 1 / 3, 540, 0)
    for ext, holes in sec_xz(oml, flip=True):
        e = np.c_[TIP - ext[:, 0], ext[:, 1]]
        D.outline(ax, e, lw=D.LW_VIS)
        fin = e[(e[:, 1] > 23.6) & (e[:, 0] > 950)]
        if len(fin) > 5:                       # fins 1/2 at +-120 deg project at r cos120 below the axis
            fin = fin[np.argsort(fin[:, 0])]
            top = np.c_[fin[:, 0], -0.5 * fin[:, 1]]
            ax.fill(np.r_[top[:, 0]], np.r_[top[:, 1]], fc="white", ec="none", zorder=3)
            ax.plot(top[:, 0], np.minimum(top[:, 1], -23.4), color="k", lw=D.LW_VIS, zorder=4)
    D.centerline(ax, (-15, 0), (1095, 0))
    Lt = TIP + 29.89
    # station dimensions
    D.dim(ax, (0, -21), (Lt, -21), -22, "1077.4")
    D.dim(ax, (0, 21), (165, 21), 12, "165.0 NOSE")
    D.dim(ax, (165, 21), (TIP - 158.5, 21), 12, "724.0 BODY TUBE (EXPOSED)")
    D.dim(ax, (TIP - 158.5, 23.4), (TIP, 23.4), 16, "158.5 FIN CAN")
    D.dim(ax, (TIP, 21), (Lt, 21), 34, "29.9", inside=False)
    D.dim(ax, (500, -20.64), (500, 20.64), 0, "Ø41.28")
    D.dim(ax, (955, -23.4), (955, 23.4), 0, "Ø46.80")
    D.leader(ax, (1010, 69.5), (1060, 92), "3 FINS @ 120°, TIP R69.5")
    # CG / CP symbols
    for x, lab, kind in [(763.3, "CG 763.3 (EST.)", "cg"), (826.3, "CP 826.3 (CFD)", "cp")]:
        r = D.k_(ax, 2.6)
        ax.add_patch(Circle((x, 0), r, fc="white", ec="k", lw=0.6, zorder=9))
        if kind == "cg":
            ax.add_patch(matplotlib.patches.Wedge((x, 0), r, 0, 90, fc="k", zorder=10))
            ax.add_patch(matplotlib.patches.Wedge((x, 0), r, 180, 270, fc="k", zorder=10))
        else:
            ax.add_patch(Circle((x, 0), r * 0.3, fc="k", zorder=10))
        ax.text(x, -D.k_(ax, 7 if kind == "cg" else 13), lab, fontsize=6, ha="center", va="top")
        ax.plot([x, x], [-D.k_(ax, 3), -D.k_(ax, 6 if kind == "cg" else 12)], color="k", lw=D.LW_THIN)
    D.leader(ax, (74.6, 0), (40, -60), "NOSE BALLAST STATION 74.6", ha="left")
    D.leader(ax, (300, 0), (260, -60), "RECOVERY PACK ≈ 300, HELD BY PRINTED AFT BULKHEAD", ha="left")
    D.view_label(ax, (540, -112), "SIDE ELEVATION  (FIN 0 IN PLANE)")
    iso = plt.imread(str(ROOT / "projects/l1-cheap/report/figures/cover_rocket.png"))
    g = iso[..., :3].mean(axis=2)
    rgba = np.dstack([g, g, g, iso[..., 3]]) if iso.shape[2] == 4 else np.dstack([g, g, g])
    ia = fig.add_axes([60 / 420, 135 / 297, 300 / 420, 300 * iso.shape[0] / iso.shape[1] / 297])
    ia.imshow(rgba); ia.axis("off")
    paper.text(210, 130, "ISOMETRIC VIEW (REFERENCE, NOT TO SCALE)", fontsize=8, weight="bold", ha="center")
    # parts list
    rows = [[1, "Nose cone, 165 tangent ogive, cap + plug", "PETG", 1, "63"],
            [2, "Nose ballast (fill hole, plug)", "lead shot", "A/R", "2 + A/R"],
            [3, "Body tube BT-1.52 × 863", "LOC kraft paper", 1, "123"],
            [4, "Fin can, 3 fins (SolidWorks)", "PETG", 1, "97"],
            [5, "Tail cone / motor retainer", "PETG", 1, "15"],
            [6, "Parachute LOC 28 in, 84 mm spill hole, 8 lines", "ripstop nylon", 1, "38"],
            [7, "Shock cord 3.5 m, knotted ends", "Kevlar 750 lb", 1, "≈10"],
            [8, "Motor H100W-14A loaded, delay drilled 13 s", "AeroTech DMS 38/155", 1, "261"],
            ["", "LIFTOFF (ESTIMATE)", "", "", "610"]]
    parts_table(paper, 14, 122, rows, [10, 66, 36, 10, 22])
    notes = ["NOTES",
             "1. ALL DIMENSIONS IN MM. STATIONS MEASURED FROM THE NOSE TIP.",
             "2. TUBE AND MOTOR DIAMETERS ARE PUBLISHED NOMINAL VALUES; FIT-CHECK AT ASSEMBLY.",
             "3. CG FROM SLICER MASSES AT CAD CENTROIDS (ESTIMATE). CP FROM REFINED 3D CFD (L1C-CFD-002).",
             "4. BALLAST SIZED AT ASSEMBLY FROM THE AS-BUILT CG (EDR L1C-EDR-001 §6): MIN 1.7 CAL, TARGET 1.8 CAL.",
             "5. REFERENCE DIAMETER 41.275 MM. THIRD-ANGLE PROJECTION."]
    for k, t in enumerate(notes):
        paper.text(175, 122 - k * 5.5, t, fontsize=6 if k else 7, weight="bold" if k == 0 else "normal")
    pdf.savefig(fig); fig.savefig(FIG / "ga_vehicle.png", dpi=170); plt.close(fig)


# ------------------------------------------------------------------ sheet 2: aft-end assembly
def sheet2(pdf, fc, cn):
    fig, paper = sheet("AFT END ASSEMBLY — SECTION A-A", 2, "1:1", "FIN CAN · TAIL CONE · MOTOR · BODY TUBE", "L1C-AS-002")
    ax = D.view(fig, 14, 75, 245, 200, 1.0, -78, 0)
    # body tube (break at u = -200), motor, then printed parts
    tub = [(-200, 19.30), (-21.17, 19.30), (-21.17, 20.64), (-200, 20.64)]
    for s in (1, -1):
        ax.add_patch(Polygon([(x, s * y) for x, y in tub], closed=True, fc="white", ec="k", lw=D.LW_VIS, hatch="....", zorder=2))
        mot = [(-200, 19.05), (-18.5, 19.05), (-18.5, 20.5), (-8.975, 20.5), (-8.975, 0)]
        ax.plot([p[0] for p in mot], [s * p[1] for p in mot], color="k", lw=D.LW_VIS, ls=(0, (5, 2)), zorder=3)
    for ext, holes in sec_xz(fc):
        D.hatch_poly(ax, ext, holes)
    for ext, holes in sec_xz(cn, dz=CONE_DZ):
        ax.add_patch(Polygon(ext, closed=True, fc="white", ec="k", lw=D.LW_VIS, hatch="\\\\\\\\", zorder=2))
    D.centerline(ax, (-205, 0), (40, 0))
    for y in (25, -25):
        ax.plot([-200, -200], [y * 0.8, y * 0.8], color="k")
    ax.text(-200, -27, "BREAK", fontsize=5, ha="center")
    D.dim(ax, (-158.5, 23.4), (0, 23.4), 54, "158.5")
    D.dim(ax, (0, 20.8), (29.89, 20.8), 54, "29.9")
    D.dim(ax, (-18.5, -20.8), (0, -20.8), -14, "18.5 COLLAR")
    D.dim(ax, (30, -20.8), (30, 20.8), 0, "Ø41.6")
    D.dim(ax, (-120, -23.4), (-120, 23.4), 0, "Ø46.8")
    D.leader(ax, (-13, -20.3), (-75, -50), "THRUST RING Ø41.0 × 9.5 (NOMINAL), BEARS ON LIP Ø38.42 × 2.67")
    D.leader(ax, (-8.5, -20.2), (-75, -64), "0.9 GAP: RING TO CONE SHANK")
    D.leader(ax, (-4, 21.3), (25, 55), "THREAD P2.5 RH, 45° FLANKS, 0.2 CLEARANCE (VALIDATED)")
    D.leader(ax, (-150, 19.9), (-185, 40), "BODY TUBE BT-1.52 (3)")
    D.leader(ax, (-40, 45), (-120, 62), "FIN CAN (4)")
    D.leader(ax, (20, 22), (40, 38), "TAIL CONE (5)")
    D.leader(ax, (-150, 0), (-185, -45), "MOTOR H100W (8), PHANTOM")
    D.view_label(ax, (-80, -82), "SECTION A-A")
    # aft view
    av = D.view(fig, 268, 125, 140, 140, 1.0, 0, 0)
    sil = D.silhouette_z(fc)
    for g in getattr(sil, "geoms", [sil]):
        D.outline(av, np.array(g.exterior.coords)[:, :2])
        for h in g.interiors:
            D.outline(av, np.array(h.coords)[:, :2])
    av.add_patch(Circle((0, 0), 20.8, fill=False, lw=D.LW_VIS))
    av.add_patch(Circle((0, 0), 19.3, fill=False, lw=D.LW_THIN, ls=(0, (4, 2))))
    D.centerline(av, (-72, 0), (72, 0)); D.centerline(av, (0, -72), (0, 72))
    D.dim(av, (0, 0), (69.5, 0), 6, "R69.5")
    av.text(30, 50, "3 FINS × 120°", fontsize=6.5)
    D.view_label(av, (0, -66), "AFT VIEW (LOOKING FORWARD)")
    pdf.savefig(fig); fig.savefig(FIG / "ga_aft_section.png", dpi=170); plt.close(fig)


# ------------------------------------------------------------------ sheet 3: fin can
def sheet3(pdf, fc):
    fig, paper = sheet("FIN CAN", 3, "1:1", "SOLIDWORKS PART · PETG · 97 g (SLICER)", "L1C-FC-003")
    ax = D.view(fig, 14, 120, 240, 160, 1.0, -80, 22)
    for ext, holes in sec_xz(fc):
        D.hatch_poly(ax, ext, holes)
    D.centerline(ax, (-165, 0), (8, 0))
    D.dim(ax, (-158.5, -20.8), (0, -20.8), -22, "158.5")
    D.dim(ax, (-118, -23.4), (0, -23.4), -12, "118.0 SLEEVE Ø46.8")
    D.dim(ax, (-158.5, 21.64), (-118, 23.4), 10, "40.5 FAIRING")
    D.dim(ax, (-67.3, 23.4), (-14.9, 23.4), -8, "52.0 ROOT", text_shift=0)
    D.dim(ax, (-48.5, 69.5), (-18.6, 69.5), 8, "29.9 TIP")
    D.dim(ax, (-5, 23.4), (-5, 69.5), 0, "46.1 SPAN")
    D.dim(ax, (-67.3, 74), (-48.5, 74), 10, "18.8 SWEEP")
    D.leader(ax, (-150, 21.7), (-160, 40), "Ø43.3 AT FWD END (TUBE Ø41.3: 1.0 STEP)")
    D.leader(ax, (-60, 20.8), (-110, -50), "BORE Ø41.6 (SLIP FIT ON BT-1.52)")
    D.leader(ax, (-19.8, -19.21), (-60, -62), "LIP Ø38.42 × 2.67 (z 18.5–21.17)")
    D.leader(ax, (-5, -20.9), (-30, -42), "INTERNAL THREAD P2.5 RH, z 0–9")
    D.dim(ax, (-14.9, 23.4), (0, 23.4), -30, "14.9", inside=False)
    D.view_label(ax, (-80, -72), "SECTION A-A (THROUGH FIN 0)")
    # fin section B-B at r = 45
    bx = D.view(fig, 262, 175, 145, 70, 2.0, -38, 0)
    s = fc.section([1, 0, 0], [45, 0, 0])
    P, _ = s.to_2D(to_2D=np.array([[0, 1, 0, 0], [0, 0, 1, 0], [1, 0, 0, -45], [0, 0, 0, 1]]))
    pg = max([q for q in P.polygons_full if abs(q.centroid.x) < 15], key=lambda q: q.area)
    xy = np.array(pg.exterior.coords)
    D.hatch_poly(bx, np.c_[-xy[:, 1], xy[:, 0]])
    D.dim(bx, (-xy[:, 1].max(), -6), (-xy[:, 1].min(), -6), -6, f"{np.ptp(xy[:, 1]):.1f} CHORD")
    D.dim(bx, (-38, -4.7), (-38, 4.7), 0, "9.4 MAX")
    te = -xy[:, 1].min()
    D.leader(bx, (te, 0), (te - 6, 8), "TE 1.0", ha="right")
    D.view_label(bx, (-38, -15), "SECTION B-B (r = 45), SCALE 2:1")
    paper.text(268, 150, "FIN THICKNESS (MEASURED FROM SOLID)", fontsize=6.5, weight="bold")
    tab = [("r mm", "chord", "t max", "TE"), ("30", "49.1", "11.4", "1.0"), ("45", "42.2", "9.4", "1.0"),
           ("60", "34.9", "7.5", "1.0")]
    for i, row in enumerate(tab):
        for j, c in enumerate(row):
            paper.add_patch(Rectangle((268 + j * 22, 143 - i * 5), 22, 5, fill=(i == 0), fc="0.88", ec="k", lw=0.35))
            paper.text(269 + j * 22, 145.5 - i * 5, c, fontsize=5.8, va="center")
    pdf.savefig(fig); fig.savefig(FIG / "fincan_sheet.png", dpi=170); plt.close(fig)


# ------------------------------------------------------------------ sheet 4: tail cone
def sheet4(pdf, cn):
    fig, paper = sheet("TAIL CONE / MOTOR RETAINER", 4, "2:1", "SOLIDWORKS PART · PETG · 15 g (SLICER)", "L1C-TC-004")
    ax = D.view(fig, 20, 70, 230, 200, 2.0, 19, 0)
    for ext, holes in sec_xz(cn, flip=True):
        D.hatch_poly(ax, ext, holes)
    D.centerline(ax, (-5, 0), (44, 0))
    D.dim(ax, (0, 23.35), (38, 23.35), 18, "38.0")
    D.dim(ax, (0, -20.8), (29.89, -20.8), -14, "29.9 CONE")
    D.dim(ax, (29.89, -21.4), (38, -21.4), -14, "8.1 SHANK")
    D.dim(ax, (-2, -20.8), (-2, 20.8), 0, "Ø41.6")
    D.dim(ax, (28, -23.35), (28, 23.35), 0, "Ø46.7")
    D.leader(ax, (34, 21.4), (45, 32), "EXT. THREAD P2.5 RH, CREST Ø42.8, ROOT Ø41.2")
    D.leader(ax, (15, 19.3), (5, 8), "BORE Ø38.6 (NOZZLE CLEARANCE)")
    D.view_label(ax, (19, -40), "SECTION C-C")
    ev = D.view(fig, 270, 150, 120, 120, 2.0, 0, 0)
    for r, ls in [(23.35, "-"), (20.8, "-"), (19.3, (0, (4, 2)))]:
        ev.add_patch(Circle((0, 0), r, fill=False, lw=D.LW_VIS if ls == "-" else D.LW_THIN, ls=ls))
    D.centerline(ev, (-27, 0), (27, 0)); D.centerline(ev, (0, -27), (0, 27))
    D.dim(ev, (-23.35, 0), (23.35, 0), 30, "Ø46.7")
    D.dim(ev, (-20.8, 0), (20.8, 0), -20, "Ø41.6")
    D.leader(ev, (13.6, 13.6), (22, 25), "Ø38.6 BORE")
    D.view_label(ev, (0, -27), "AFT VIEW")
    for k, t in enumerate(["NOTES", "1. PRINT NARROW END DOWN, NO SUPPORTS.", "2. 5.0° HALF-ANGLE TAPER.",
                           "3. BORE LINED WITH ALUMINIUM FOIL (HEAT SHIELD).",
                           "4. THREAD FIT VALIDATED BY TEST PRINT 2026-11-23."]):
        paper.text(270, 95 - k * 6, t, fontsize=6.5 if k else 7.5, weight="bold" if k == 0 else "normal")
    pdf.savefig(fig); fig.savefig(FIG / "tailcone_sheet.png", dpi=170); plt.close(fig)


def main():
    FIG.mkdir(parents=True, exist_ok=True)
    fc, cn = mesh("L1-Rocket-FinCan"), mesh("FinCanBottom")
    oml = trimesh.load(ROOT / "out/cfd/rocket_oml_owner.stl", force="mesh")
    pdfp = OUT / "ms_piggy_drawings.pdf"
    with PdfPages(pdfp) as pdf:
        sheet1(pdf, oml); sheet2(pdf, fc, cn); sheet3(pdf, fc); sheet4(pdf, cn)
    shutil.copy(pdfp, FIG / "ms_piggy_drawings.pdf")
    print(pdfp)


if __name__ == "__main__":
    main()
