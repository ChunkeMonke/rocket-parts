"""Illustrated step-by-step guide: model the tail-cone thread and the collar groove in SolidWorks.

  .venv/bin/python tools/thread_guide.py --rev 9
  (3D pictures: out/guides/thread/*.png from out/guides/thread/render.py via pvbatch)

Numbers from design.yaml via parts/fin_can_md.params() and the same thread helpers that built the STEP/STL.
Writes out/guides/thread/thread_modelling_guide_rev<N>.pdf.
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.image as mpimg  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from matplotlib.backends.backend_pdf import PdfPages  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from parts import fin_can_md  # noqa: E402

G = ROOT / "out" / "guides" / "thread"
RED, BLUE, ORANGE, GREY = "#c0392b", "#2f5fb3", "#d9822b", "0.55"
plt.rcParams["font.family"] = "DejaVu Sans"


def page(pdf, step, title, text, draw=None, images=(), captions=()):
    fig = plt.figure(figsize=(11.69, 8.27))
    if step:
        fig.text(0.03, 0.955, f"STEP {step}", fontsize=13, color=RED, weight="bold")
    fig.text(0.12 if step else 0.03, 0.955, title, fontsize=15, weight="bold")
    fig.text(0.03, 0.9, text, fontsize=10.3, va="top", linespacing=1.55)
    if draw:
        draw(fig.add_axes([0.42, 0.07, 0.55, 0.82]))
    n = len(images)
    for k, (img, cap) in enumerate(zip(images, captions)):
        w = 0.55 / max(n, 1)
        ax = fig.add_axes([0.42 + k * w, 0.12, w - 0.01, 0.74])
        ax.imshow(mpimg.imread(G / img)); ax.axis("off"); ax.set_title(cap, fontsize=10)
    fig.text(0.97, 0.02, "thread modelling guide · numbers from design.yaml (rev 9)", fontsize=7, ha="right", color="0.5")
    pdf.savefig(fig); plt.close(fig)


def lbl(ax, x, y, s, dx=0.06, dy=0.06, ha="left", color=RED, fs=9):
    ax.plot(x, y, "o", color=color, ms=5, zorder=5)
    ax.text(x + dx, y + dy, s, fontsize=fs, color=color, ha=ha, zorder=6, bbox=dict(fc="white", ec="none", pad=0.4))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--rev", type=int, required=True)
    a = ap.parse_args()
    p = fin_can_md.params()
    m = json.load(open(G / "meta.json"))["nums"]
    Lc, Lb, ring, c, rb, re_, ri, rc, rs, Ls, P = (m[k] for k in ("Lc", "Lb", "ring", "c", "rb", "re", "ri", "rc", "rs", "Ls", "P"))
    h = p["thread_depth_mm"]
    hw = (P - 0.3) / 2
    hwr = hw - c * math.sqrt(2)
    rt = rc + min(h - c, hwr - 0.2)
    h_ridge, h_groove = m["h_ridge"], m["h_groove"]
    tooth = [(rs - 0.3, -hwr), (rc, -hwr), (rt, -0.2), (rt, 0.2), (rc, hwr), (rs - 0.3, hwr)]
    groove = [(rc - 0.1, -(hw + 0.1)), (rc + h, -(hw - h)), (rc + h, hw - h), (rc - 0.1, hw + 0.1)]
    out = G / f"thread_modelling_guide_rev{a.rev}.pdf"
    with PdfPages(out) as pdf:
        tab = (f"{'':26s}{'TAIL CONE (male)':>18s}{'COLLAR (female)':>18s}\n"
               f"{'operation':26s}{'Swept Boss':>18s}{'Swept Cut':>18s}\n"
               f"{'helix circle':26s}{'Ø' + format(2 * rc, '.2f'):>18s}{'Ø' + format(2 * rc, '.2f'):>18s}\n"
               f"{'pitch':26s}{P:>18.1f}{P:>18.1f}\n"
               f"{'height':26s}{h_ridge:>18.2f}{h_groove:>18.2f}\n"
               f"{'starts at':26s}{'2.5 above shoulder':>18s}{'collar bottom face':>18s}\n"
               f"{'rotation':26s}{'Clockwise':>18s}{'Clockwise (SAME)':>18s}\n"
               f"{'tooth':26s}{'6 points, sheet 4':>18s}{'4 points, sheet 8':>18s}\n"
               f"{'clearance':26s}{c:>18.2f}{'':>18s}")
        page(pdf, 0, "Threads by hand in SolidWorks: helix + sweep",
             "A thread = one tooth shape swept along a spiral.\nYou make the spiral (Helix), draw the tooth once, and\nsweep it: "
             "ADD it on the tail cone, CUT it in the collar.\n\nTHE NUMBERS YOU NEED (mm)\n\n" + tab +
             "\n\nBoth parts are modelled the way they print and\ngrow 'upward' = toward the nose in the assembled\nrocket, "
             "so the SAME rotation setting makes them mate.", images=["t05_thread.png"], captions=["the finished tail cone"])

        def body_profile(ax):
            pts = [(ri, 0), (re_, 0), (rb, Lb), (rs, Lb), (rs, Lb + Ls), (ri, Lb + Ls)]
            ax.fill(*zip(*pts), color="#b9cdf0", ec=BLUE, lw=1.5)
            ax.axvline(0, color=GREY, ls=(0, (10, 3, 2, 3)))
            names = ["A", "B", "C", "D", "E", "F"]
            offs = {"A": (-0.4, -2.2, "right"), "B": (0.4, -2.2, "left"), "C": (0.5, 0.6, "left"), "D": (-0.5, 0.6, "right"),
                    "E": (0.5, 1.2, "left"), "F": (-0.5, 1.2, "right")}
            for (x, y), nme in zip(pts, names):
                dx, dy, ha = offs[nme]
                lbl(ax, x, y, f"{nme} ({x:.2f}, {y:.2f})", dx=dx, dy=dy, ha=ha)
            ax.text(0.3, 20, "rocket axis\n(centerline)", fontsize=9, color=GREY)
            ax.set_xlim(-2, 32); ax.set_ylim(-5, 44); ax.set_aspect("equal"); ax.grid(alpha=0.2)
            ax.set_xlabel("radius from the axis (mm)"); ax.set_ylabel("height as printed (mm), aft end = 0")
            ax.set_title("Front plane sketch: half profile (x = radius, y = height)", fontsize=10)
        page(pdf, 1, "Tail cone body: sketch the half-profile",
             "Front plane, vertical CENTERLINE = rocket axis.\nDraw the closed outline A→B→C→D→E→F→A:\n\n"
             f"  A, B  aft end: bore r {ri:.2f}, outside r {re_:.2f} at height 0\n"
             f"  C     top of the taper: r {rb:.2f} at height {Lb:.0f}\n"
             f"  D     step in to the neck: r {rs:.2f}\n"
             f"  E, F  top of the neck at height {Lb + Ls:.2f}\n\n"
             "B→C is the straight boattail taper. D→E is the plain\nneck where the thread will go.", draw=body_profile)
        page(pdf, 2, "Revolve", "Features → Revolved Boss/Base, 360° about the\ncenterline.\n\nResult: the tapered cone with a "
             "plain neck on top\n(no thread yet).", images=["t01_blank.png"], captions=["revolved tail cone, plain neck"])
        page(pdf, 3, "Helix on the neck",
             f"1. Reference Geometry → Plane, parallel to the\n   shoulder face (height {Lb:.0f}), offset {P} up\n   (= height {Lb + P:.1f}).\n"
             f"2. Sketch on it: circle Ø{2 * rc:.2f}, centred on the axis.\n"
             "3. Insert → Curve → Helix/Spiral:\n"
             "     Defined by: Height and Pitch\n"
             f"     Height {h_ridge:.2f}   Pitch {P}\n"
             "     Start angle 0°   CLOCKWISE (remember this!)\n"
             "     Reverse direction if needed so it grows UP\n\n"
             f"The helix sits at the collar bore radius ({rc:.2f}), just\noutside the neck ({rs:.2f}); the tooth is drawn around it.",
             images=["t03_helix.png"], captions=["helix (red) around the neck"])

        def tooth_draw(ax):
            ax.axhline(0, color=RED, lw=0.6, ls=":")
            ax.add_patch(plt.Rectangle((rs - 1.2, -2.2), 1.2, 4.4, color="#dbe5f6"))
            ax.plot([rs, rs], [-2.2, 2.2], color=BLUE, lw=1.5)
            ax.text(rs - 0.6, -2.0, "neck\n(solid)", fontsize=9, ha="center", color=BLUE)
            ax.plot([rc, rc], [-2.2, 2.2], color=GREY, ls="--", lw=1)
            ax.text(rc + 0.03, 2.05, f"r {rc:.2f} (helix / collar bore)", fontsize=8, color=GREY)
            ax.text(rs - 0.05, 2.05, f"r {rs:.2f}", fontsize=8, color=BLUE, ha="right")
            ax.fill(*zip(*tooth), color="#9fb9ea", ec="k", lw=1.6)
            toffs = [(-0.08, -0.32, "right"), (0.08, -0.32, "left"), (0.08, -0.25, "left"), (0.08, 0.12, "left"),
                     (0.08, 0.15, "left"), (-0.08, 0.15, "right")]
            for k, (x, y) in enumerate(tooth):
                dx, dy, ha = toffs[k]
                lbl(ax, x, y, f"{k + 1}: ({x:.2f}, {y:+.2f})", dx=dx, dy=dy, ha=ha)
            ax.plot(rc, 0, "s", color=RED, ms=7)
            ax.annotate("PIERCE to the helix\n(the point on the helix)", (rc, 0), (rc + 0.5, -1.4), fontsize=9, color=RED,
                        arrowprops=dict(arrowstyle="->", color=RED))
            ax.text(rt + 0.05, 0, "0.40\nflat", fontsize=8, va="center")
            ax.text((rc + rt) / 2 + 0.02, 0.55, "45°", fontsize=9)
            ax.set_xlim(rs - 1.4, rc + 1.9); ax.set_ylim(-2.3, 2.4); ax.set_aspect("equal"); ax.grid(alpha=0.2)
            ax.set_xlabel("distance from the rocket axis (mm)"); ax.set_ylabel("up / down from the helix point (mm)")
            ax.set_title("Right plane sketch: male tooth (about 25:1)", fontsize=10)
        page(pdf, 4, "Male tooth sketch",
             "Right plane (it passes through the axis AND the\nhelix start point). Draw the closed 6-point shape:\n\n" +
             "\n".join(f"  {k + 1}.  r {x:.2f}   {y:+.2f}" for k, (x, y) in enumerate(tooth)) +
             "\n\n  • 45° flanks, 0.40 flat tip\n  • points 1 and 6 are 0.3 INSIDE the neck so the\n    sweep fuses with the body\n"
             f"  • Pierce: a sketch point at (r {rc:.2f}, 0) → helix\n\nGap to the groove = {c} all round (clearance).", draw=tooth_draw)
        page(pdf, 5, "Swept Boss: the thread appears",
             "Insert → Boss/Base → Swept\n  Profile: the tooth sketch\n  Path: the helix\n  Profile orientation: Follow path\n  Merge result: ON\n\n"
             f"≈ {h_ridge / P:.1f} turns of thread on the neck.\n\nOptional: chamfer the start of the thread 0.5 mm so it\ncatches easily.",
             images=["t05_thread.png", "t05b_half.png"], captions=["thread on the neck", "cut in half: 45° teeth"])
        page(pdf, 6, "Collar: helix in the fin can",
             f"In the FIN CAN part. The collar is the {Lc} mm ring below\nthe aft face, bore Ø{2 * rc:.2f}.\n\n"
             f"1. Sketch on the collar's BOTTOM face (height −{Lc}):\n   circle Ø{2 * rc:.2f} on the axis.\n"
             f"2. Helix/Spiral: Height {h_groove:.2f}, Pitch {P}, start 0°,\n   CLOCKWISE (same as the cone), growing UP into\n   the collar.\n\n"
             f"It ends {Lc - h_groove:.2f} below the aft face, i.e. below the\n{ring:.2f} mm zone where the motor's thrust ring sits.",
             images=["t07_collar_helix.png"], captions=["helix (red) inside the collar"])

        def groove_draw(ax):
            ax.add_patch(plt.Rectangle((rc, -2.2), rb - rc, 4.4, color="#f6dfc6"))
            ax.plot([rc, rc], [-2.2, 2.2], color=ORANGE, lw=1.5)
            ax.text(rb - 0.4, -2.0, "collar wall\n(solid)", fontsize=9, ha="center", color=ORANGE)
            ax.text(rc - 0.05, 2.05, f"bore r {rc:.2f}", fontsize=8, color=ORANGE, ha="right")
            ax.text(rb + 0.03, 2.05, f"OD r {rb:.2f}", fontsize=8, color=ORANGE)
            ax.plot([rb, rb], [-2.2, 2.2], color=ORANGE, lw=1.0)
            ax.fill(*zip(*groove), color="white", ec="k", lw=1.6, hatch="..")
            for k, (x, y) in enumerate(groove):
                lbl(ax, x, y, f"{k + 1}: ({x:.2f}, {y:+.2f})", dx=0.05 if x > rc else -0.05, ha="left" if x > rc else "right",
                    dy=0.12 if y > 0 else -0.25)
            ax.plot(rc, 0, "s", color=RED, ms=7)
            ax.annotate("PIERCE to the helix", (rc, 0), (rc + 0.25, -0.75), fontsize=9, color=RED, arrowprops=dict(arrowstyle="->", color=RED))
            ax.text(rc + h + 0.05, 0, "0.20", fontsize=8, va="center")
            ax.set_xlim(rc - 1.6, rb + 0.6); ax.set_ylim(-2.3, 2.4); ax.set_aspect("equal"); ax.grid(alpha=0.2)
            ax.set_xlabel("distance from the rocket axis (mm)"); ax.set_ylabel("up / down from the helix point (mm)")
            ax.set_title("Right plane sketch: groove (about 25:1)", fontsize=10)
        page(pdf, 7, "Groove sketch",
             "Right plane, at the collar helix start. Closed 4-point\nshape:\n\n" +
             "\n".join(f"  {k + 1}.  r {x:.2f}   {y:+.2f}" for k, (x, y) in enumerate(groove)) +
             f"\n\n  • 2.40 wide at the bore, 0.20 at the bottom,\n    {h:.1f} deep, 45° sides\n"
             "  • starts 0.1 inside the bore (empty space) for a\n    clean cut\n"
             f"  • Pierce: point (r {rc:.2f}, 0) → helix\n\nWall left behind the groove: {rb - rc - h:.2f} mm.", draw=groove_draw)
        page(pdf, 8, "Swept Cut: the groove",
             "Insert → Cut → Swept\n  Profile: the groove sketch\n  Path: the collar helix\n  Profile orientation: Follow path\n\n"
             "The groove opens on the collar's bottom face (so the\ncone can start screwing in) and stops inside the wall.",
             images=["t09_groove_half.png"], captions=["collar cut in half: the groove"])
        page(pdf, 9, "Check the fit in an assembly",
             "New Assembly: insert the fin can and the tail cone.\n  • Concentric mate: the two axes\n"
             f"  • Coincident: cone's neck top face ↔ a plane\n    {ring:.2f} below the fin can aft face (thrust ring)\n\n"
             "Evaluate → Interference Detection: NONE.\n\nSection View through the axis: each tooth sits inside\n"
             f"a groove with a ~{c} gap all round (drawing sheet 4,\nDetail D). If they clash, rotate the cone about the\n"
             "axis: for printing the start angle does not matter.",
             images=["t10_assembly_half.png"], captions=["section: blue cone tooth inside the orange groove"])
        page(pdf, 10, "Test print before the real thing",
             "Print a TEST RING: the fin can cut just above the\ncollar (or Split the body at height 0), plus the tail\ncone. "
             "≈15 g, ≈40 min.\n\nTUNING\n  too tight / won't start → make the tooth 0.1\n    smaller (points 3/4 in by 0.1, flanks 0.07)\n"
             "  loose / wobbly → 0.05 bigger\n  rough → print slower (outer wall 40 mm/s)\n\nCOMMON MISTAKES\n"
             "  ✗ different Clockwise setting in the two parts\n  ✗ tooth sketch not on a plane through the axis\n"
             "  ✗ 'Cosmetic Thread' (a picture only, won't print)\n  ✗ tooth not pierced to the helix → sweep fails",
             images=["t11_test_ring.png"], captions=["test ring with the internal thread"])
    print(out)


if __name__ == "__main__":
    main()
