"""Engineering drawing set (ISO/ASME-style, black & white) for the fin can + tail cone.

  .venv/bin/python tools/drawing.py --rev 9

Sheets (A3 landscape, true scale): 1 fin can (section A-A + end view), 2 fin can details B/C/D, 3 fins,
4 tail cone (section + end view + thread detail). Geometry is cut from the generated STL (exact), numbers come from
design.yaml via parts/fin_can_md.params(). Writes out/fin_can_md/rev<N>/fin_can_md_rev<N>_drawings.pdf.
"""
from __future__ import annotations

import argparse
import math
import sys
from datetime import date
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import trimesh  # noqa: E402
from matplotlib.backends.backend_pdf import PdfPages  # noqa: E402
from matplotlib.patches import Circle, Polygon, Rectangle  # noqa: E402
from shapely.geometry import Polygon as SPoly  # noqa: E402
from shapely.ops import unary_union  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from parts import fin_can, fin_can_md  # noqa: E402

A3 = (420.0, 297.0)
MM = 1 / 25.4
LW_VIS, LW_THIN, LW_CL = 0.7, 0.25, 0.25
FONT = dict(family="DejaVu Sans", size=7)
N_SHEETS = 4
plt.rcParams["hatch.linewidth"] = 0.3
plt.rcParams["font.family"] = "DejaVu Sans"


# ------------------------------------------------------------------ sheet frame and title block
def new_sheet(title, number, rev, scale_txt, p, subtitle="MIN-DIAMETER FIN CAN + TAIL CONE RETAINER", prefix="FC-MD",
              material="PETG (tail cone: ABS/ASA)", n_sheets=None, drawn="rocket-parts", project="l1-cheap (H100W, 38 mm)",
              note="Geometry cut from the generated STL; dimensions from design.yaml (parts/). Do not scale the print: use the dimensions.",
              dwg_no=None, finish="FDM 0.2 layer, 6 walls", tol="±0.2 · angles ±0.5°"):
    n_sheets = n_sheets or N_SHEETS
    fig = plt.figure(figsize=(A3[0] * MM, A3[1] * MM))
    paper = fig.add_axes([0, 0, 1, 1])
    paper.set_xlim(0, A3[0]); paper.set_ylim(0, A3[1]); paper.axis("off")
    paper.add_patch(Rectangle((10, 10), A3[0] - 20, A3[1] - 20, fill=False, lw=1.0))
    # zone markers
    for k, x in enumerate(np.linspace(10, A3[0] - 10, 9)[:-1]):
        paper.text(x + (A3[0] - 20) / 16, A3[1] - 7, str(8 - k), ha="center", va="center", fontsize=7)
        paper.text(x + (A3[0] - 20) / 16, 7, str(8 - k), ha="center", va="center", fontsize=7)
        paper.plot([x, x], [A3[1] - 10, A3[1] - 5], lw=0.4, color="k")
        paper.plot([x, x], [5, 10], lw=0.4, color="k")
    for k, y in enumerate(np.linspace(10, A3[1] - 10, 7)[:-1]):
        paper.text(7, y + (A3[1] - 20) / 12, "ABCDEF"[k], ha="center", va="center", fontsize=7)
        paper.text(A3[0] - 7, y + (A3[1] - 20) / 12, "ABCDEF"[k], ha="center", va="center", fontsize=7)
    # title block (bottom right) 180 x 46
    x0, y0, w = A3[0] - 10 - 180, 10, 180
    rows = [(0, 9), (9, 9), (18, 9), (27, 19)]
    paper.add_patch(Rectangle((x0, y0), w, 46, fill=False, lw=0.8))
    for yy in (9, 18, 27):
        paper.plot([x0, x0 + w], [y0 + yy, y0 + yy], lw=0.4, color="k")
    for xx in (45, 90, 135):
        paper.plot([x0 + xx, x0 + xx], [y0, y0 + 27], lw=0.4, color="k")

    def cell(cx, cy, label, val, fs=8):
        paper.text(x0 + cx + 1.2, y0 + cy + 7.4, label, fontsize=4.8, color="0.3", va="top")
        paper.text(x0 + cx + 1.5, y0 + cy + 2.2, val, fontsize=fs, va="bottom")
    cell(0, 18, "MATERIAL", material, 6.5)
    cell(45, 18, "FINISH / PRINT", finish, 6.5)
    cell(90, 18, "SCALE", scale_txt)
    cell(135, 18, "SHEET", f"{number} / {n_sheets}")
    cell(0, 9, "DRAWN", drawn)
    cell(45, 9, "DATE", str(date.today()))
    cell(90, 9, "UNITS", "mm")
    cell(135, 9, "REV", str(rev))
    cell(0, 0, "PROJECT", project, 6.5)
    cell(45, 0, "DWG NO.", dwg_no or f"{prefix}-R{rev}-{number:02d}", 6.5 if dwg_no else 8)
    cell(90, 0, "GENERAL TOL.", tol, 6.5)
    paper.text(x0 + 137, y0 + 2.4, "SIZE A3", fontsize=7)
    paper.text(x0 + 2, y0 + 39, title, fontsize=11, weight="bold", va="center")
    paper.text(x0 + 2, y0 + 31.5, subtitle, fontsize=6.5, va="center", color="0.25")
    # third-angle projection symbol
    sx, sy = x0 + 150, y0 + 37
    paper.add_patch(Circle((sx + 18, sy), 3.2, fill=False, lw=0.5))
    paper.add_patch(Circle((sx + 18, sy), 1.4, fill=False, lw=0.5))
    paper.add_patch(Polygon([(sx, sy - 3.2), (sx + 9, sy - 2), (sx + 9, sy + 2), (sx, sy + 3.2)], closed=True, fill=False, lw=0.5))
    paper.plot([sx - 1, sx + 23], [sy, sy], lw=0.25, color="k", ls=(0, (6, 2, 1, 2)))
    paper.text(sx + 11.5, sy - 6.3, "THIRD-ANGLE", fontsize=4.8, ha="center")
    # source note
    paper.text(14, 13, note, fontsize=5.5, color="0.35")
    return fig, paper


def view(fig, x, y, w, h, scale, cx, cy):
    """Axes covering paper rectangle (x, y, w, h) in mm where 1 model mm = `scale` paper mm, centred at model (cx, cy)."""
    ax = fig.add_axes([x / A3[0], y / A3[1], w / A3[0], h / A3[1]])
    ax.set_xlim(cx - w / 2 / scale, cx + w / 2 / scale)
    ax.set_ylim(cy - h / 2 / scale, cy + h / 2 / scale)
    ax.set_aspect("equal"); ax.axis("off")
    ax._scale = scale
    return ax


# ------------------------------------------------------------------ line work and dimensions (ISO style)
def k_(ax, mm):
    """paper mm -> model units for this view."""
    return mm / ax._scale


def hatch_poly(ax, xy, holes=(), lw=LW_VIS):
    ax.add_patch(Polygon(xy, closed=True, fc="white", ec="k", lw=lw, hatch="////", zorder=2))
    for h in holes:
        ax.add_patch(Polygon(h, closed=True, fc="white", ec="k", lw=lw, zorder=3))


def outline(ax, xy, lw=LW_VIS, ls="-", z=4):
    xy = np.asarray(xy)
    ax.plot(np.r_[xy[:, 0], xy[0, 0]], np.r_[xy[:, 1], xy[0, 1]], color="k", lw=lw, ls=ls, zorder=z)


def centerline(ax, p1, p2):
    ax.plot([p1[0], p2[0]], [p1[1], p2[1]], color="k", lw=LW_CL, ls=(0, (12, 3, 2, 3)), zorder=1)


def arrow(ax, tip, frm, z=6):
    ax.annotate("", tip, frm, arrowprops=dict(arrowstyle="-|>", color="k", lw=LW_THIN, mutation_scale=7,
                                              shrinkA=0, shrinkB=0), zorder=z)


def dim(ax, p1, p2, off, text, tol=None, fs=6.5, inside=True, text_shift=0.0):
    """Linear dimension. p1, p2: feature points (model units); off: offset of the dimension line along the normal,
    in PAPER mm (signed). Extension lines start 1 mm from the feature and run 2 mm past the dimension line."""
    p1, p2 = np.array(p1, float), np.array(p2, float)
    d = p2 - p1
    L = np.linalg.norm(d)
    u = d / L
    n = np.array([-u[1], u[0]])
    o = k_(ax, off)
    a, b = p1 + n * o, p2 + n * o
    gap, over = k_(ax, 1.0) * np.sign(off or 1), k_(ax, 2.0) * np.sign(off or 1)
    for p, q in ((p1, a), (p2, b)):
        if abs(off) > 0.01:
            ax.plot([p[0] + n[0] * gap, q[0] + n[0] * over], [p[1] + n[1] * gap, q[1] + n[1] * over],
                    color="k", lw=LW_THIN, zorder=5)
    if inside and L * ax._scale > 8:
        ax.annotate("", b, a, arrowprops=dict(arrowstyle="<|-|>", color="k", lw=LW_THIN, mutation_scale=7,
                                              shrinkA=0, shrinkB=0), zorder=6)
        m = (a + b) / 2 + u * k_(ax, text_shift)
    else:
        s = k_(ax, 5)
        arrow(ax, a, a - u * s); arrow(ax, b, b + u * s)
        ax.plot([a[0], b[0]], [a[1], b[1]], color="k", lw=LW_THIN, zorder=6)
        m = b + u * (s + k_(ax, 2 + text_shift))
    ang = math.degrees(math.atan2(u[1], u[0]))
    if ang > 90.5 or ang < -89.5:
        ang += 180
    lbl = text if tol is None else f"{text} {tol}"
    tp = m + n * k_(ax, 1.6) * (1 if ang == math.degrees(math.atan2(u[1], u[0])) else -1)
    ax.text(*tp, lbl, fontsize=fs, ha="center" if (inside and L * ax._scale > 8) else "left", va="center",
            rotation=ang, rotation_mode="anchor", zorder=7, bbox=dict(fc="white", ec="none", pad=0.3))


def leader(ax, tip, txt_xy, text, fs=6.5, ha="left"):
    tip, t = np.array(tip, float), np.array(txt_xy, float)
    arrow(ax, tip, t)
    ax.plot([t[0], t[0] + k_(ax, 3) * (1 if ha == "left" else -1)], [t[1], t[1]], color="k", lw=LW_THIN)
    ax.text(t[0] + k_(ax, 3.5) * (1 if ha == "left" else -1), t[1], text, fontsize=fs, ha=ha, va="center", zorder=7)


def view_label(ax, xy, text, fs=9):
    ax.text(*xy, text, fontsize=fs, weight="bold", ha="center", va="top")


def detail_circle(ax, c, r, letter):
    ax.add_patch(Circle(c, r, fill=False, lw=LW_THIN, ls=(0, (6, 3)), zorder=8))
    a = math.radians(40)
    p = (c[0] + r * math.cos(a), c[1] + r * math.sin(a))
    q = (p[0] + k_(ax, 6), p[1] + k_(ax, 6))
    ax.plot([p[0], q[0]], [p[1], q[1]], color="k", lw=LW_THIN)
    ax.text(q[0] + k_(ax, 1), q[1], letter, fontsize=10, weight="bold", va="center")


def gdt(ax, xy, cells, fs=6):
    """Feature control frame at model xy (lower-left), cells = list of strings."""
    x, y = xy
    w_char = k_(ax, 2.0)
    h = k_(ax, 5)
    for c in cells:
        w = max(k_(ax, 6), len(c) * w_char + k_(ax, 2))
        ax.add_patch(Rectangle((x, y), w, h, fill=True, fc="white", ec="k", lw=LW_THIN, zorder=8))
        ax.text(x + w / 2, y + h / 2, c, fontsize=fs, ha="center", va="center", zorder=9)
        x += w


def datum(ax, xy, letter, direction=(0, -1)):
    x, y = xy
    s = k_(ax, 4.5)
    dx, dy = direction
    bx, by = x + dx * s * 2.2, y + dy * s * 2.2
    ax.plot([x, bx], [y, by], color="k", lw=LW_THIN)
    ax.add_patch(Polygon([(x - s * 0.45, y), (x + s * 0.45, y), (x, y + dy * s * 0.8)] if dx == 0 else
                         [(x, y - s * 0.45), (x, y + s * 0.45), (x + dx * s * 0.8, y)], closed=True, fc="k", zorder=8))
    ax.add_patch(Rectangle((bx - s / 2, by - s / 2), s, s, fc="white", ec="k", lw=LW_THIN, zorder=8))
    ax.text(bx, by, letter, fontsize=7, ha="center", va="center", zorder=9)


# ------------------------------------------------------------------ geometry from the STL
def load(rev, part):
    return trimesh.load(ROOT / "out" / part / f"rev{rev}" / f"{part}_rev{rev}.stl", force="mesh")


def section_y0(mesh, swap=True):
    """Polygons of the cut at y = 0, as (axial, radial) = (z, x) when swap, else (x, z)."""
    s = mesh.section(plane_origin=[0, 0, 0], plane_normal=[0, 1, 0])
    pl, _ = s.to_2D(to_2D=np.array([[1, 0, 0, 0], [0, 0, 1, 0], [0, -1, 0, 0], [0, 0, 0, 1]]))
    out = []
    for q in pl.polygons_full:
        ext = np.array(q.exterior.coords)
        holes = [np.array(h.coords) for h in q.interiors]
        if swap:
            ext = ext[:, ::-1]
            holes = [h[:, ::-1] for h in holes]
        out.append((ext, holes))
    return out


def silhouette_z(mesh):
    """Outline seen along the z axis (union of all triangles projected on XY)."""
    tris = mesh.vertices[mesh.faces][:, :, :2]
    polys = [SPoly(t) for t in tris if SPoly(t).area > 1e-6]
    return unary_union(polys).buffer(0)


# ------------------------------------------------------------------ sheet 1: fin can section + end view
def sheet1(pdf, p, rev):
    m = load(rev, "fin_can_md")
    rb, ri, rl = p["body_od_mm"] / 2, p["sleeve_bore_d_mm"] / 2, p["lip_bore_d_mm"] / 2
    L, Lf, Lc, t = p["sleeve_length_mm"], p["fairing_length_mm"], p["collar_length_mm"], p["lip_thickness_mm"]
    rc = p["collar_bore_d_mm"] / 2
    r_end = ri + p["feather_edge_mm"]
    rt = rb + p["span_mm"]
    fig, paper = new_sheet("FIN CAN", 1, rev, "1:1 (details 4:1, sheet 2)", p)
    # section A-A (axis horizontal, aft to the left)
    ax = view(fig, 18, 70, 250, 210, 1.0, 60, 18)
    for ext, holes in section_y0(m):
        hatch_poly(ax, ext, holes)
    centerline(ax, (-Lc - 8, 0), (L + Lf + 8, 0))
    view_label(ax, (60, -rb - 25), "SECTION A-A")
    # overall lengths (below)
    dim(ax, (-Lc, -rb), (0, -rb), -10, f"{Lc}")
    dim(ax, (0, -rb), (L, -rb), -10, f"{L:.0f}")
    dim(ax, (L, -rb), (L + Lf, -r_end), -10 - (rb - r_end), f"{Lf:.0f}")
    dim(ax, (-Lc, -rb), (L + Lf, -r_end), -20 - 0, f"{Lc + L + Lf:.1f}")
    # diameters (vertical dims to the right of features, Ø)
    dim(ax, (L + Lf, -r_end), (L + Lf, r_end), -12, f"Ø{2 * r_end:.2f}")
    dim(ax, (L + 20, -ri), (L + 20, ri), 0, f"Ø{2 * ri:.3f}", tol="±0.05")
    dim(ax, (L - 30, -rb), (L - 30, rb), 0, f"Ø{2 * rb:.3f}", tol="±0.1")
    dim(ax, (1.3, -rl), (1.3, rl), -40, f"Ø{2 * rl:.2f}", tol="+0.10/0")
    dim(ax, (-Lc / 2, -rc), (-Lc / 2, rc), 22, f"Ø{2 * rc:.2f}", tol="+0.10/0")
    # fin height/span (fin 0 is in the cut plane, top)
    dim(ax, (-2, rb), (-2, rt), 8, f"{p['span_mm']}")
    dim(ax, (0, rt), (p["tip_chord_mm"], rt), 6, f"{p['tip_chord_mm']:.0f}")
    dim(ax, (0, rb + 3), (p["root_chord_mm"], rb + 3), 0, f"{p['root_chord_mm']:.0f}", text_shift=-8)
    # callouts
    leader(ax, (-Lc + 3, rc + 0.6), (-Lc - 6, rb + 22), "THREAD P2.5, 45° FLANKS\nRH, L 6.5 — SEE DETAIL B", ha="right")
    leader(ax, (L + Lf * 0.5, (rb + r_end) / 2), (L + Lf * 0.3, rb + 18), f"TAPER {math.degrees(math.atan((rb - r_end) / Lf)):.2f}°")
    detail_circle(ax, (-Lc / 2 + 2, -rb + 2), 14, "B")
    detail_circle(ax, (L + Lf - 4, -rb + 2), 12, "C")
    datum(ax, (0, -rb - 2), "A")
    gdt(ax, (L - 64, -rb - 32), ["◎", "Ø0.1", "B"])
    ax.text(L - 64, -rb - 35, "COLLAR BORE COAXIAL TO B", fontsize=5.5, va="top")
    datum(ax, (L + 20, -ri), "B", direction=(0, 1))
    # end view from aft (looking forward), to the right
    ev = view(fig, 262, 120, 148, 160, 1.0, 0, 6)
    sil = silhouette_z(m)
    geoms = sil.geoms if hasattr(sil, "geoms") else [sil]
    for g in geoms:
        outline(ev, np.array(g.exterior.coords))
        for h in g.interiors:
            outline(ev, np.array(h.coords))
    for r_, ls in ((rc, "-"), (ri, (0, (4, 2))), (rc + p["thread_depth_mm"], (0, (4, 2)))):
        ev.add_patch(Circle((0, 0), r_, fill=False, lw=LW_VIS if ls == "-" else LW_THIN, ls=ls, zorder=4))
    centerline(ev, (-rt - 6, 0), (rt + 6, 0)); centerline(ev, (0, -rt - 6), (0, rt + 6))
    for k in range(3):
        a = math.radians(90 - 120 * k)
        centerline(ev, (0, 0), ((rt + 5) * math.cos(a), (rt + 5) * math.sin(a)))
    # cutting plane A-A (through fin 0 = vertical in this view)
    for sgn in (1, -1):
        y = sgn * (rt + 8)
        ev.plot([0, 0], [y, y - sgn * k_(ev, 6)], color="k", lw=1.2)
        arrow(ev, (-k_(ev, 8), y), (0, y))
        ev.text(-k_(ev, 11), y, "A", fontsize=10, weight="bold", va="center")
    view_label(ev, (0, -rt - 14), "VIEW FROM AFT")
    dim(ev, (-rb, -rb - 4), (rb, -rb - 4), -6, f"Ø{2 * rb:.3f}")
    ev.text(rt * 0.5, rt * 0.86, "3× FINS\nEQUALLY SPACED 120°", fontsize=6, ha="left")
    # notes
    paper.text(272, 98, "NOTES\n"
               "1. Datum A: aft face (lip underside). Datum B: sleeve bore axis.\n"
               "2. Fin profile: NACA 4-digit symmetric, see sheet 3.\n"
               f"3. Root fillets R{p['root_fillet_r_mm']} both sides of each fin; TE skirt R{p['te_fillet_r_mm']:.0f}\n"
               "   tangent to the collar (sheet 3).\n"
               "4. No insert bosses (rev 9): the tail cone retains the motor.\n"
               "5. Print collar end down; supports under the fin TEs only.\n"
               "6. Fits marked with tolerances depend on PLACEHOLDER sizes:\n"
               f"   tube OD {p['tube_od_mm']}, case OD {p['motor_case_od_mm']},\n"
               f"   thrust ring Ø{p['thrust_ring_od_mm']} × {p['thrust_ring_thk_mm']:.2f}. Measure first.",
               fontsize=6.5, va="top", linespacing=1.45)
    pdf.savefig(fig); plt.close(fig)


# ------------------------------------------------------------------ sheet 2: details B (aft) and C (fairing)
def sheet2(pdf, p, rev):
    m = load(rev, "fin_can_md")
    rb, ri, rl = p["body_od_mm"] / 2, p["sleeve_bore_d_mm"] / 2, p["lip_bore_d_mm"] / 2
    L, Lf, Lc, t = p["sleeve_length_mm"], p["fairing_length_mm"], p["collar_length_mm"], p["lip_thickness_mm"]
    rc, h, P_, ring = p["collar_bore_d_mm"] / 2, p["thread_depth_mm"], p["thread_pitch_mm"], p["thrust_ring_thk_mm"]
    r_end = ri + p["feather_edge_mm"]
    fig, paper = new_sheet("FIN CAN — DETAILS", 2, rev, "4:1", p)
    secs = section_y0(m)
    # DETAIL B: aft end (lower half, radial negative = below the axis, like sheet 1)
    ax = view(fig, 15, 60, 205, 222, 4.0, -6.5, -21)
    for ext, holes in secs:
        hatch_poly(ax, ext, holes, lw=0.9)
    ax.add_patch(Rectangle((-Lc - 3, -rb - 9), Lc + 17, 18, fill=False, lw=0))
    view_label(ax, (-6.5, -rb - 11.5), "DETAIL B  (4:1)")
    # radial wall dims (vertical in this view, below = -r)
    dim(ax, (8, -ri), (8, -rb), 0, f"{rb - ri:.2f}", inside=False)
    dim(ax, (t / 2 - 0.4, -rl), (t / 2 - 0.4, -ri), 0, f"{ri - rl:.2f}", inside=False)
    dim(ax, (-ring / 2, -rc), (-ring / 2, -rb), 0, f"{rb - rc:.2f}", inside=False)
    dim(ax, (-Lc + P_, -rc - h), (-Lc + P_, -rb), 0, f"{rb - rc - h:.2f}", inside=False)
    dim(ax, (-Lc + 2 * P_, -rc), (-Lc + 2 * P_, -rc - h), 0, f"{h:.2f}", inside=False)
    # axial dims (below the part)
    dim(ax, (0, -rb), (t, -rb), -8, f"{t:.2f}", inside=False)
    dim(ax, (-ring, -rb), (0, -rb), -16, f"{ring:.2f}")
    dim(ax, (-Lc, -rb), (-Lc + Lc - ring - P_, -rb), -16, f"{Lc - ring - P_:.2f}")
    dim(ax, (-Lc, -rb), (0, -rb), -26, f"{Lc}")
    # radii labels via leaders
    leader(ax, (1.0, -rl), (5, -rl + 7.0), f"Ø{2 * rl:.2f} +0.10/0 LIP BORE")
    leader(ax, (0.15, -rl - 0.8), (5, -rl + 4.0), "THRUST RING SEAT = DATUM A (z = 0)")
    leader(ax, (11.0, -ri), (13, -ri + 10.0), f"Ø{2 * ri:.3f} ±0.05 SLEEVE BORE")
    leader(ax, (-ring - 1.5, -rc), (-9, -rc + 8.0), f"Ø{2 * rc:.2f} +0.10/0 COLLAR BORE (THREAD MINOR)", ha="right")
    leader(ax, (-Lc + 0.9, -rc - h + 0.15), (-Lc - 2.5, -rc + 3.5), f"Ø{2 * (rc + h):.2f} THREAD MAJOR", ha="right")
    # DETAIL C: fairing (upper half)
    cx = L + Lf / 2
    ax2 = view(fig, 228, 120, 182, 162, 4.0, cx + 3, 21)
    for ext, holes in secs:
        hatch_poly(ax2, ext, holes, lw=0.9)
    view_label(ax2, (cx + 3, rb - 7), "DETAIL C  (4:1)")
    for zz in (L, L + Lf / 2, L + Lf):
        r_o = rb + (r_end - rb) * (zz - L) / Lf
        dim(ax2, (zz, ri), (zz, r_o), 0, f"{r_o - ri:.2f}", inside=False)
    dim(ax2, (L, rb), (L + Lf, rb), 8, f"{Lf:.0f}")
    leader(ax2, (L + Lf - 0.3, r_end), (L + Lf - 6, r_end + 4.2), f"FEATHER EDGE Ø{2 * r_end:.2f}", ha="right")
    ax2.text(L + 2, ri - 1.4, f"SLEEVE BORE Ø{2 * ri:.3f}", fontsize=6, va="top")
    paper.text(232, 108, "THICKNESSES (mm)\n"
               f"sleeve wall .................. {rb - ri:.2f}\n"
               f"lip (axial) ................... {t:.2f}\n"
               f"lip ledge under tube ...... {ri - rl:.2f}\n"
               f"collar wall (ring zone) .... {rb - rc:.2f}\n"
               f"collar wall behind thread .. {rb - rc - h:.2f}\n"
               f"thread depth .................. {h:.2f}\n"
               f"fairing wall, start → end .. {rb - ri:.2f} → {r_end - ri:.2f}",
               fontsize=6.8, va="top", family="DejaVu Sans Mono", linespacing=1.5)
    pdf.savefig(fig); plt.close(fig)


# ------------------------------------------------------------------ sheet 3: fins
def sheet3(pdf, p, rev):
    rb, cr, ct, s = p["body_od_mm"] / 2, p["root_chord_mm"], p["tip_chord_mm"], p["span_mm"]
    R = p["te_fillet_r_mm"]
    fig, paper = new_sheet("FIN DEFINITION", 3, rev, "2:1 / 4:1", p)
    ax = view(fig, 15, 70, 175, 210, 2.0, rb + s / 2 - 2, cr / 2 - 6)
    pl = np.array([(rb, 0), (rb, cr), (rb + s, ct), (rb + s, 0)])
    outline(ax, pl, lw=0.9)
    ax.plot([rb, rb], [-p["collar_length_mm"], cr + 8], color="k", lw=LW_THIN, ls=(0, (4, 2)))
    th = np.linspace(0, math.pi / 2, 40)
    ax.plot(rb + R - R * np.cos(th), -R + R * np.sin(th), color="k", lw=0.9)
    dim(ax, (rb, 0), (rb + s, 0), -12, f"{s}")
    dim(ax, (rb, 0), (rb, cr), 10, f"{cr:.0f}")
    dim(ax, (rb + s, 0), (rb + s, ct), -8, f"{ct:.0f}")
    dim(ax, (rb + s, ct), (rb + s, cr), -18, f"{cr - ct:.0f}")
    leader(ax, (rb + R * 0.3, -R * 0.7), (rb + 12, -14), f"R{R:.0f} TE SKIRT, TANGENT TO COLLAR")
    leader(ax, (rb, cr * 0.7), (rb + 10, cr + 8), f"ROOT FILLET R{p['root_fillet_r_mm']} BOTH SIDES")
    ax.text(rb + 1, cr + 3, "SLEEVE OD", fontsize=6)
    for k_s, (zc, lab) in enumerate(((cr * 0.7, "D"), )):
        pass
    ax.plot([rb - 3, rb + s + 3], [cr * 0.7 * 0 + 21, 21], lw=0)  # spacer
    view_label(ax, (rb + s / 2, -p["collar_length_mm"] - 8), "FIN PLANFORM (2:1)")
    ax.text(rb + s / 2, cr * 0.3, "TE FLUSH WITH DATUM A", fontsize=6, ha="center")
    # airfoil sections at 4:1
    for k, (chord, tmax, te, lab) in enumerate(((cr, p["fin_thickness_mm"], p["te_root_thickness_mm"], "ROOT"),
                                                (ct, p["fin_tip_thickness_mm"], p["te_thickness_mm"], "TIP"))):
        a_ = view(fig, 198, 200 - k * 85, 212, 75, 4.0 if chord <= 30 else 3.2, chord / 2, 0)
        x = fin_can.chord_stations(81)
        yt = fin_can.naca_half_thickness(x, tmax, te)
        z = chord * (1 - x)
        xy = np.c_[np.r_[z, z[::-1]], np.r_[yt, -yt[::-1]]]
        hatch_poly(a_, xy, lw=0.9)
        centerline(a_, (-3, 0), (chord + 3, 0))
        i = int(np.argmax(yt))
        dim(a_, (z[i], -yt[i]), (z[i], yt[i]), 0, f"{2 * yt[i]:.2f}", inside=False)
        dim(a_, (0, -te / 2), (0, te / 2), 0, f"{te:.2f}", inside=False)
        dim(a_, (0, -yt[0] if False else -yt.max()), (chord, -yt.max()), -6, f"{chord:.0f}")
        dim(a_, (z[i], yt[i]), (chord, 0), 9, f"{chord - z[i]:.1f}")
        r_le = 1.1019 * (tmax / chord) ** 2 * chord
        leader(a_, (chord - r_le * 0.4, r_le * 0.6), (chord - 6, yt.max() + 3.5), f"R{r_le:.2f} LE")
        view_label(a_, (chord / 2, -yt.max() - k_(a_, 13)), f"SECTION {lab} ({'3.2' if chord > 30 else '4'}:1)")
    # thickness table
    xs = [0.0, 0.05, 0.10, 0.25, 0.30, 0.50, 0.75, 0.90, 1.0]
    tr = 2 * fin_can.naca_half_thickness(np.array(xs), p["fin_thickness_mm"], p["te_root_thickness_mm"])
    tt = 2 * fin_can.naca_half_thickness(np.array(xs), p["fin_tip_thickness_mm"], p["te_thickness_mm"])
    x0, y0 = 198, 62
    paper.add_patch(Rectangle((x0, y0), 30 + 9 * 16, 24, fill=False, lw=0.6))
    paper.text(x0 + 2, y0 + 20, "x/c (LE=0)", fontsize=6)
    paper.text(x0 + 2, y0 + 12, "t ROOT", fontsize=6)
    paper.text(x0 + 2, y0 + 4, "t TIP", fontsize=6)
    for j, (xx, a1, a2) in enumerate(zip(xs, tr, tt)):
        cx = x0 + 30 + j * 16
        paper.plot([cx, cx], [y0, y0 + 24], lw=0.3, color="k")
        paper.text(cx + 8, y0 + 20, f"{xx:.2f}", fontsize=6, ha="center")
        paper.text(cx + 8, y0 + 12, f"{a1:.2f}", fontsize=6, ha="center")
        paper.text(cx + 8, y0 + 4, f"{a2:.2f}", fontsize=6, ha="center")
    for yy in (8, 16):
        paper.plot([x0, x0 + 30 + 9 * 16], [y0 + yy, y0 + yy], lw=0.3, color="k")
    paper.text(x0, y0 + 27, "FIN THICKNESS t (mm) ALONG THE CHORD — LINEAR ROOT → TIP. POINT FILES: "
               f"fin_can_md_rev{rev}_airfoil_root/_tip.dat", fontsize=5.8)
    pdf.savefig(fig); plt.close(fig)


# ------------------------------------------------------------------ sheet 4: tail cone
def sheet4(pdf, p, rev):
    m = load(rev, "tail_cone")
    Lc, Lb, ring, c = p["collar_length_mm"], p["boattail_length_mm"], p["thrust_ring_thk_mm"], p["thread_clearance_mm"]
    rb, re_, ri = p["body_od_mm"] / 2, p["boattail_end_od_mm"] / 2, p["tail_cone_bore_d_mm"] / 2
    rs = p["collar_bore_d_mm"] / 2 - c
    Ls = Lc - ring
    P_, h = p["thread_pitch_mm"], p["thread_depth_mm"]
    fig, paper = new_sheet("TAIL CONE / MOTOR RETAINER", 4, rev, "2:1 (detail 10:1)", p)
    ax = view(fig, 15, 70, 200, 210, 2.0, (Lb + Ls) / 2, 0)
    for ext, holes in section_y0(m):
        hatch_poly(ax, ext, holes, lw=0.9)
    centerline(ax, (-6, 0), (Lb + Ls + 6, 0))
    view_label(ax, ((Lb + Ls) / 2, -rb - 18), "SECTION A-A (2:1)  AFT END LEFT")
    dim(ax, (0, -re_), (Lb, -rb), -10 - (rb - re_) * 2, f"{Lb:.0f}")
    dim(ax, (Lb, -rb), (Lb + Ls, -rs), -10, f"{Ls:.2f}")
    dim(ax, (0, -rb), (Lb + Ls, -rb), -22, f"{Lb + Ls:.2f}")
    dim(ax, (-2, -re_), (-2, re_), -6, f"Ø{2 * re_:.2f}")
    dim(ax, (Lb - 2, -rb), (Lb - 2, rb), 0, f"Ø{2 * rb:.3f}", tol="±0.1")
    dim(ax, (Lb * 0.45, -ri), (Lb * 0.45, ri), 0, f"Ø{2 * ri:.2f}", tol="+0.10/0")
    dim(ax, (Lb + Ls + 1, -rs), (Lb + Ls + 1, rs), 10, f"Ø{2 * rs:.2f}")
    dim(ax, (2, re_), (2, ri), 0, f"{re_ - ri:.2f}", inside=False)
    dim(ax, (Lb + Ls - 1.5, rs), (Lb + Ls - 1.5, ri), 0, f"{rs - ri:.2f}", inside=False)
    ang = math.degrees(math.atan((rb - re_) / Lb))
    leader(ax, (Lb * 0.5, (rb + re_) / 2), (Lb * 0.25, rb + 8), f"TAPER {ang:.2f}°")
    leader(ax, (Lb + Ls * 0.5, rs + 0.4), (Lb + 3, rb + 15),
           f"EXT. THREAD P{P_} 45° RH, CREST Ø{2 * (rs + c + min(h - c, (P_ - 0.3) / 2 - c * math.sqrt(2) - 0.2)):.2f}\nSEE DETAIL D")
    detail_circle(ax, (Lb + Ls * 0.55, rs + 0.3), 3.2, "D")
    datum(ax, (Lb + Ls, -ri + 0.2), "R", direction=(1, 0))
    ax.text(Lb + Ls + 2.5, -ri - 4.5, "SHANK FACE BEARS ON\nTHE THRUST RING", fontsize=5.5)
    # end view from aft
    ev = view(fig, 222, 165, 95, 110, 2.0, 0, 0)
    for r_, lw in ((rb, LW_VIS), (re_, LW_VIS), (ri, LW_VIS), (rs, LW_THIN)):
        ev.add_patch(Circle((0, 0), r_, fill=False, lw=lw, ls="-" if lw == LW_VIS else (0, (4, 2)), zorder=4))
    centerline(ev, (-rb - 4, 0), (rb + 4, 0)); centerline(ev, (0, -rb - 4), (0, rb + 4))
    view_label(ev, (0, -rb - 6), "VIEW FROM AFT (2:1)")
    # detail D: thread profile 10:1
    rc = p["collar_bore_d_mm"] / 2
    hw = (P_ - 0.3) / 2
    hwr = hw - c * math.sqrt(2)
    rt = rc + min(h - c, hwr - 0.2)
    d = view(fig, 322, 120, 88, 160, 10.0, rc + 0.4, P_)
    for kk in range(3):
        z0 = kk * P_
        g = [(z0 - hw - 0.1, rc - 0.1), (z0 - (hw - h), rc + h), (z0 + hw - h, rc + h), (z0 + hw + 0.1, rc - 0.1)]
        outline(d, [(y, x) for x, y in [(gx, gy) for gx, gy in g]][::1] and [(gy, gx) for gx, gy in g], lw=LW_THIN, ls=(0, (3, 1.5)))
        r_ = [(z0 - hwr, rc - c - 0.35), (z0 - hwr, rc), (z0 - 0.2, rt), (z0 + 0.2, rt), (z0 + hwr, rc), (z0 + hwr, rc - c - 0.35)]
        hatch_poly(d, [(gy, gx) for gx, gy in r_], lw=0.8)
    # (rotate detail: radius horizontal, axial vertical)
    dim(d, (rc + h + 0.2, 0), (rc + h + 0.2, P_), 0, f"P {P_}")
    dim(d, (rc, -1.5), (rc + h, -1.5), 0, f"{h:.1f}", inside=False)
    dim(d, (rc - c, 2 * P_ + 1.4), (rc, 2 * P_ + 1.4), 0, f"{c}", inside=False)
    dim(d, (rt + 0.1, -0.2), (rt + 0.1, 0.2), 0, "0.40", inside=False)
    d.text(rc + 0.15, -0.9, "45°", fontsize=6.5)
    view_label(d, (rc + 0.4, -2.3), "DETAIL D (10:1)")
    d.text(rc - 0.85, 3 * P_ + 0.3, "dashed: female groove in\nthe fin can collar (sheet 2)", fontsize=5.5, va="top")
    paper.text(225, 98, "NOTES\n"
               "1. Material ABS or ASA: the bore surrounds the nozzle\n   exit during the burn (or PETG with an aluminium-tape\n   lined bore).\n"
               "2. Print aft end down, no supports.\n"
               f"3. Thread clearance {c} radial and on the flanks; print a\n   test pair with the fin can and adjust.\n"
               f"4. Shank length = collar {Lc} − thrust ring {ring:.2f} (PLACEHOLDER).",
               fontsize=6.5, va="top", linespacing=1.45)
    pdf.savefig(fig); plt.close(fig)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--rev", type=int, required=True)
    ap.add_argument("--project", default="l1-cheap")
    a = ap.parse_args()
    p = fin_can_md.params(a.project)
    out = ROOT / "out" / "fin_can_md" / f"rev{a.rev}" / f"fin_can_md_rev{a.rev}_drawings.pdf"
    with PdfPages(out) as pdf:
        for fn in (sheet1, sheet2, sheet3, sheet4):
            fn(pdf, p, a.rev)
    print(out)


if __name__ == "__main__":
    main()
