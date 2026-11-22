"""Illustrated step-by-step guide: model the fins in SolidWorks by hand (sketched airfoil + loft), no equations.

  .venv/bin/python tools/fin_guide.py --rev 9
  (3D pictures: out/guides/fin/*.png from out/guides/fin/render.py via pvbatch)

Writes out/guides/fin/fin_modelling_guide_rev<N>.pdf. Numbers come from design.yaml via parts/fin_can_md.params();
the sketch points are read off the NACA thickness (the same values as the drawing's sheet 3 table).
"""
from __future__ import annotations

import argparse
import math
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.image as mpimg  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from matplotlib.backends.backend_pdf import PdfPages  # noqa: E402
from matplotlib.patches import Circle  # noqa: E402
from scipy.interpolate import PchipInterpolator  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from parts import fin_can, fin_can_md  # noqa: E402

G = ROOT / "out" / "guides" / "fin"
RED, BLUE, GREY, INK = "#c0392b", "#1f5fbf", "0.55", "#111111"
plt.rcParams["font.family"] = "DejaVu Sans"


def airfoil_numbers(chord, tmax, te):
    x = np.linspace(0, 1, 2001)                              # chord fraction from the LE
    yt = fin_can.naca_half_thickness(x, tmax, te)
    i = int(np.argmax(yt))
    r_le = 1.1019 * (tmax / chord) ** 2 * chord
    pts = []
    for f in (0.5, 0.75):
        pts.append((chord * (1 - f), float(fin_can.naca_half_thickness(np.array([f]), tmax, te)[0])))
    return dict(chord=chord, x_le_max=x[i] * chord, half_max=yt[i], r_le=r_le, te=te,
                pts=pts, curve=(chord * (1 - x), yt))


def page(pdf, title, step, text, draw=None, images=(), captions=()):
    fig = plt.figure(figsize=(11.69, 8.27))
    fig.text(0.03, 0.955, f"STEP {step}" if step else "", fontsize=13, color=RED, weight="bold")
    fig.text(0.12 if step else 0.03, 0.955, title, fontsize=15, weight="bold")
    fig.text(0.03, 0.9, text, fontsize=10.5, va="top", linespacing=1.55, wrap=True)
    n = len(images)
    if draw:
        ax = fig.add_axes([0.4, 0.06, 0.57, 0.82])
        draw(ax)
    for k, (img, cap) in enumerate(zip(images, captions)):
        w = 0.57 / max(n, 1)
        ax = fig.add_axes([0.4 + k * w, 0.12, w - 0.01, 0.74])
        ax.imshow(mpimg.imread(G / img))
        ax.axis("off")
        ax.set_title(cap, fontsize=10)
    fig.text(0.97, 0.02, "fin modelling guide · numbers from design.yaml (rev 9)", fontsize=7, ha="right", color="0.5")
    pdf.savefig(fig)
    plt.close(fig)


def sketch_axes(ax, a, title):
    ax.set_aspect("equal")
    ax.set_xlim(-6, a["chord"] + 6)
    ax.set_ylim(-a["half_max"] - 7, a["half_max"] + 7)
    ax.grid(alpha=0.18)
    ax.set_title(title, fontsize=11)
    ax.set_xlabel("mm along the chord (TE at 0)")


def hdim(ax, x1, x2, y, text):
    ax.annotate("", (x2, y), (x1, y), arrowprops=dict(arrowstyle="<|-|>", color=RED, lw=1))
    ax.text((x1 + x2) / 2, y, text, color=RED, fontsize=9, ha="center", va="center", bbox=dict(fc="white", ec="none", pad=0.5))


def vdim(ax, x, y1, y2, text, side=1):
    ax.annotate("", (x, y2), (x, y1), arrowprops=dict(arrowstyle="<|-|>", color=RED, lw=1))
    ax.text(x + side * 0.8, (y1 + y2) / 2, text, color=RED, fontsize=9, ha="left" if side > 0 else "right",
            va="center", bbox=dict(fc="white", ec="none", pad=0.5))


def build_sketch(ax, a, upto, label):
    c, hm, xm, R, te = a["chord"], a["half_max"], a["chord"] - a["x_le_max"], a["r_le"], a["te"]
    sketch_axes(ax, a, label)
    if upto >= 1:
        ax.plot([0, c], [0, 0], color=GREY, ls=(0, (10, 3, 2, 3)), lw=1)
        ax.plot([0, 0], [-0.6, 0.6], color=INK, lw=1); ax.plot([c, c], [-0.6, 0.6], color=INK, lw=1)
        ax.text(0, -1.6, "TE", ha="center", fontsize=9); ax.text(c, -1.6, "LE", ha="center", fontsize=9)
        if upto == 1:
            hdim(ax, 0, c, -a["half_max"] - 3, f"{c:.0f}  chord")
    if upto >= 2:
        ax.add_patch(Circle((c - R, 0), R, fill=False, ec=BLUE if upto == 2 else GREY, lw=1.4))
        if upto == 2:
            ax.plot([c - R, c - R + R * 0.7], [0, R * 0.7], color=RED, lw=1)
            ax.text(c - R - 0.5, R + 1.0, f"R{R:.1f}", color=RED, fontsize=10, ha="right")
            hdim(ax, c - R, c, -R - 2, f"{R:.1f}")
    if upto >= 3:
        ax.plot([xm, xm], [-hm, hm], color=BLUE if upto == 3 else GREY, lw=1.4, ls="--" if upto > 3 else "-")
        if upto == 3:
            vdim(ax, xm + 1.5, -hm, hm, f"{2 * hm:.2f}  thickest")
            hdim(ax, xm, c, hm + 2.5, f"{c - xm:.0f} from the LE")
    if upto >= 4:
        ax.plot([0, 0], [-te / 2, te / 2], color=BLUE if upto == 4 else INK, lw=1.6)
        if upto == 4:
            vdim(ax, -1.5, -te / 2, te / 2, f"{te:.2f}  flat TE", side=-1)
    if upto >= 5:
        X, Y = a["curve"]
        ax.plot(X, Y, color=BLUE if upto == 5 else INK, lw=1.8)
        pts = [(0, te / 2)] + a["pts"] + [(xm, hm)]
        for (px, py) in pts:
            ax.plot(px, py, "o", color=RED, ms=5)
            if upto == 5:
                ax.text(px, py + 1.0, f"({px:.1f}, {py:.2f})", fontsize=8, ha="center", color=RED)
        if upto == 5:
            ax.annotate("horizontal\n(tangent)", (xm, hm), (xm - 6, hm + 4.3), fontsize=8, color=RED,
                        arrowprops=dict(arrowstyle="->", color=RED))
            ax.annotate("tangent to\nthe circle", (c - R * 0.7, R * 0.7), (c - 2, hm + 3.2), fontsize=8, color=RED,
                        arrowprops=dict(arrowstyle="->", color=RED))
    if upto >= 6:
        X, Y = a["curve"]
        ax.plot(X, -Y, color=BLUE if upto == 6 else INK, lw=1.8)
        if upto == 6:
            ax.fill(np.r_[X, X[::-1]], np.r_[Y, -Y[::-1]], color="#f3c79a", alpha=0.6, zorder=0)
            ax.text(c * 0.45, 0, "closed profile", ha="center", va="center", fontsize=10)


def plane_layout(ax, p):
    rb = p["body_od_mm"] / 2
    ax.remove()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--rev", type=int, required=True)
    a_ = ap.parse_args()
    p = fin_can_md.params()
    rb, s = p["body_od_mm"] / 2, p["span_mm"]
    root = airfoil_numbers(p["root_chord_mm"], p["fin_thickness_mm"], p["te_root_thickness_mm"])
    tip = airfoil_numbers(p["tip_chord_mm"], p["fin_tip_thickness_mm"], p["te_thickness_mm"])
    out = G / f"fin_modelling_guide_rev{a_.rev}.pdf"
    with PdfPages(out) as pdf:
        # cover
        def cover(ax):
            ax.axis("off")
            ax.imshow(mpimg.imread(G / "s14_pattern.png"))
        rows = (f"{'':22s}{'ROOT':>8s}{'TIP':>8s}\n"
                f"{'chord':22s}{root['chord']:8.0f}{tip['chord']:8.0f}\n"
                f"{'LE circle radius':22s}{root['r_le']:8.1f}{tip['r_le']:8.1f}\n"
                f"{'thickest, from LE':22s}{root['x_le_max']:8.0f}{tip['x_le_max']:8.0f}\n"
                f"{'max thickness':22s}{2 * root['half_max']:8.2f}{2 * tip['half_max']:8.2f}\n"
                f"{'flat TE':22s}{root['te']:8.2f}{tip['te']:8.2f}\n"
                f"{'spline pt at 50 %':22s}{'(%.1f, %.2f)' % root['pts'][0]:>14s}{'(%.1f, %.2f)' % tip['pts'][0]:>14s}\n"
                f"{'spline pt at 75 %':22s}{'(%.1f, %.2f)' % root['pts'][1]:>14s}{'(%.1f, %.2f)' % tip['pts'][1]:>14s}\n"
                f"{'sketch plane, r =':22s}{rb - 1:8.1f}{rb + s:8.1f}")
        page(pdf, "Fins by hand in SolidWorks: sketched airfoil + loft", 0,
             "What you will build: 3 fins with a smooth airfoil, R6 root fillets\nand a smooth skirt under the trailing "
             "edge, all on the revolved\nfin can body. No equations: every shape comes from a few\ndimensions and a spline.\n\n"
             "THE NUMBERS YOU NEED\n\n" + rows +
             "\n\n(x, y): x along the chord from the TE, y = half thickness.\nAll mm. Drawings sheet 3 has the same values.",
             draw=cover)
        page(pdf, "Start from the revolved body", 1,
             "Revolve the body profile from drawing sheet 1 (sleeve,\nfairing, lip, collar) about the axis.\n\n"
             "Coordinate convention used in this guide:\n  • the rocket axis is SolidWorks' Y axis (vertical),\n"
             "  • the aft face (lip underside) is at height 0,\n  • the fin roots run from 0 (TE) up to 50 (LE).\n\n"
             "Fin 0 will point along +X.",
             images=["s01_body.png"], captions=["body only (no fins yet)"])
        page(pdf, "Make the two sketch planes", 2,
             "Reference Geometry → Plane, parallel to the Right plane:\n\n"
             f"  • ROOT plane at X = {rb - 1:.1f}  (1 mm INSIDE the sleeve OD\n    {rb:.3f}, so the loft fuses into the body)\n"
             f"  • TIP plane at X = {rb + s:.3f}  (sleeve OD + span {s})\n\n"
             "Both planes face along the radius (X), so a sketch on them\nis a slice across the fin.",
             images=["s02_planes.png"], captions=["blue = root plane (partly inside the sleeve), green = tip plane"])
        steps = [(1, "Draw the chord line", "On the ROOT plane: a horizontal CENTERLINE (construction)\n"
                  f"{root['chord']:.0f} long, along the rocket axis direction.\n\n"
                  "  • left end = trailing edge (TE), at height 0 (aft face)\n"
                  f"  • right end = leading edge (LE), at height {root['chord']:.0f}\n\n"
                  "Everything else is drawn symmetric about this line."),
                 (2, "Nose circle", f"Circle R{root['r_le']:.1f}, centre ON the centerline, {root['r_le']:.1f} in from\nthe LE "
                  "end (so the circle touches the LE point).\n\nThis gives the round nose. You will trim it later\nso only the "
                  "front half stays."),
                 (3, "Thickest point", f"Vertical construction line at {root['chord'] - root['x_le_max']:.0f} from the TE\n"
                  f"({root['x_le_max']:.0f} back from the LE), {2 * root['half_max']:.2f} tall, centred on\nthe chord line.\n\n"
                  "Its top end is where the spline will be highest."),
                 (4, "Flat trailing edge", f"Vertical line at the TE end, {root['te']:.2f} tall, centred.\n\n"
                  "Keep it flat: a knife edge breaks fillets and lofts and\ncannot be printed."),
                 (5, "Upper surface spline", "Sketch → Spline through, in order:\n"
                  f"  TE top (0, {root['te'] / 2:.2f})\n"
                  f"  ({root['pts'][1][0]:.1f}, {root['pts'][1][1]:.2f})\n"
                  f"  ({root['pts'][0][0]:.1f}, {root['pts'][0][1]:.2f})\n"
                  f"  top of the thickest line ({root['chord'] - root['x_le_max']:.0f}, {root['half_max']:.2f})\n"
                  "  ... and end it on the nose circle.\n\n"
                  "Relations:\n  • HORIZONTAL tangent at the thickest point\n  • TANGENT where the spline meets the circle\n\n"
                  "Dimension the two middle points from the TE and the\ncenterline (smart dimension to the spline point)."),
                 (6, "Mirror and close", "Mirror the spline about the centerline. Trim the circle so\nonly the front arc "
                  "remains (between the two spline ends).\n\nYou now have one closed loop: upper spline, nose arc,\nlower "
                  "spline, flat TE. The sketch should turn black\n(fully defined) once all dimensions are on.")]
        for k, (u, title, text) in enumerate(steps):
            page(pdf, f"ROOT sketch: {title}", 3 + k, text,
                 draw=lambda ax, u=u, title=title: build_sketch(ax, root, u, f"ROOT airfoil, step {u}/6: {title}"))
        page(pdf, "TIP sketch: same recipe, smaller numbers", 9,
             "On the TIP plane repeat steps 3-8 with:\n\n"
             f"  chord {tip['chord']:.0f}  (TE at 0, LE at {tip['chord']:.0f})\n"
             f"  nose circle R{tip['r_le']:.1f}\n"
             f"  thickest {2 * tip['half_max']:.2f} at {tip['x_le_max']:.0f} from the LE\n"
             f"  flat TE {tip['te']:.2f}\n"
             f"  spline points ({tip['pts'][1][0]:.1f}, {tip['pts'][1][1]:.2f}) and ({tip['pts'][0][0]:.1f}, {tip['pts'][0][1]:.2f})\n\n"
             "IMPORTANT: the TE of both sketches sits at height 0\n(flush with the aft face). The tip LE is lower than the\n"
             f"root LE by {root['chord'] - tip['chord']:.0f}: that is the sweep.",
             draw=lambda ax: build_sketch(ax, tip, 6, "TIP airfoil (finished)"))

        def layout(ax):
            ax.remove()
            fig = plt.gcf()
            a3 = fig.add_axes([0.4, 0.06, 0.57, 0.84], projection="3d")
            th = np.linspace(0, 2 * np.pi, 60)
            for zz in (-18.5, 0, 50, 100):
                a3.plot(rb * np.cos(th), rb * np.sin(th), zz, color="0.75", lw=0.6)
            for t_ in np.linspace(0, 2 * np.pi, 13)[:-1]:
                a3.plot([rb * np.cos(t_)] * 2, [rb * np.sin(t_)] * 2, [-18.5, 100], color="0.85", lw=0.5)
            for a_s, r_, col in ((root, rb - 1, BLUE), (tip, rb + s, "#1e8c3a")):
                X, Y = a_s["curve"]
                a3.plot([r_] * len(X), Y, X, color=col, lw=1.6)
                a3.plot([r_] * len(X), -Y, X, color=col, lw=1.6)
            a3.plot([rb - 1, rb + s], [0, 0], [root["chord"], tip["chord"]], color=RED, lw=1.4)
            a3.plot([rb - 1, rb + s], [0, 0], [0, 0], color=RED, lw=1.4)
            a3.text(rb + s / 2, 0, (root["chord"] + tip["chord"]) / 2 + 4, "LE guide line", color=RED, fontsize=9)
            a3.text(rb + s / 2, 0, -6, "TE guide line", color=RED, fontsize=9)
            a3.text(rb - 1, 0, root["chord"] + 8, "root sketch", color=BLUE, fontsize=9)
            a3.text(rb + s, 0, tip["chord"] + 8, "tip sketch", color="#1e8c3a", fontsize=9)
            a3.set_box_aspect((1, 1, 1.3)); a3.view_init(18, -60)
            a3.set_xlim(-30, 70); a3.set_ylim(-50, 50); a3.set_zlim(-20, 100)
            a3.set_xlabel("X (radius)"); a3.set_zlabel("height (axis)")
        page(pdf, "Guide lines", 10,
             "Exit the sketches. Make two 3D sketches (or two\nstraight lines in a 3D sketch):\n\n"
             "  • LE guide: root LE point → tip LE point\n  • TE guide: root TE point → tip TE point\n\n"
             "They keep the leading and trailing edges straight and\nstop the loft from twisting.", draw=layout)
        page(pdf, "Loft", 11,
             "Features → Lofted Boss/Base\n\n  Profiles: root sketch, then tip sketch\n  Guide curves: LE guide, TE guide\n"
             "  Merge result: ON\n\nIf the preview twists, drag the green connector dots so\nthey join TE to TE.",
             images=["s11_loft.png"], captions=["one fin lofted onto the sleeve"])
        page(pdf, "Root fillets R6", 12,
             f"Fillet, constant radius R{p['root_fillet_r_mm']}: select the two edges where the\nfin's sides meet the sleeve. "
             "Tangent propagation ON.\n\nIf it fails near the LE:\n  • try R5, or a Variable Size fillet (R4 at the LE,\n    R6 elsewhere)\n"
             "  • or Face Fillet between the fin side and the sleeve\n    face with 'Hold line'.",
             images=["s12a_noroot.png", "s12b_rootfillet.png"], captions=["before", "after: fillets blend the root"])
        page(pdf, "Trailing-edge skirt (smooth, under the fin)", 13,
             f"Fillet → FACE FILLET, radius R{p['te_fillet_r_mm']:.0f}:\n  face set 1: the fin's flat aft face (TE strip +\n"
             "  fillet ends, at height 0)\n  face set 2: the collar's outer cylinder\n\n"
             "It follows the fin footprint and curves into the collar,\ntangent to it. Look from below to check there is\n"
             "no step or sharp corner.",
             images=["s13a_noskirt.png", "s13b_skirt.png"], captions=["before (sharp corner)", "after: smooth skirt"])
        page(pdf, "Pattern the fin", 14,
             "Circular Pattern around the rocket axis:\n  instances 3, equal spacing 360°\n"
             "  features: loft, root fillets, skirt fillet\n\nPatterning the features (not bodies) keeps all three\nfins identical.",
             images=["s14_pattern.png", "s14b_aft.png"], captions=["finished fin can", "from aft: 3 fins at 120°"])

        def check(ax):
            for a_s, col, lab in ((root, BLUE, "root"), (tip, "#1e8c3a", "tip")):
                X, Y = a_s["curve"]
                xm = a_s["chord"] - a_s["x_le_max"]
                px = [0, a_s["pts"][1][0], a_s["pts"][0][0], xm]
                py = [a_s["te"] / 2, a_s["pts"][1][1], a_s["pts"][0][1], a_s["half_max"]]
                sp = PchipInterpolator(px, py)
                xs = np.linspace(0, xm, 200)
                ytrue = np.interp(xs, X[::-1], Y[::-1])
                ax.plot(xs / a_s["chord"], sp(xs) - ytrue, color=col, lw=1.6, label=f"{lab}: spline − exact")
            ax.axhline(0, color="0.5", lw=0.8)
            ax.axhspan(-0.3, 0.3, color="#2ecc71", alpha=0.12, label="±0.3 mm (fine for FDM)")
            ax.set_xlabel("x / chord from the TE"); ax.set_ylabel("half-thickness error (mm)")
            ax.set_title("A 4-point spline vs the exact airfoil", fontsize=11); ax.legend(); ax.grid(alpha=0.2)
        page(pdf, "Check it", 15,
             "1. Section View through a fin at height 35 (root\n   thickest point): thickness ≈ 12.7.\n"
             "2. Compare with drawing sheet 3 (sections + table):\n   within ~0.3 mm is fine for a 0.4 mm nozzle.\n"
             "3. Evaluate → Mass Properties: volume close to the\n   STEP I sent (import both and compare).\n\n"
             "The plot shows how close a 4-point spline gets to the\nexact shape (the gap is smaller than one printed line).",
             draw=check)
    print(out)


if __name__ == "__main__":
    main()
