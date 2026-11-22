"""Dimensioned drawing set (PDF) of the min-diameter fin can + tail cone, for re-modelling in SolidWorks.

  .venv/bin/python tools/blueprint.py --rev 9

Every number is read from projects/<project>/design.yaml through parts/fin_can_md.params() (the same source the
STEP/STL were built from), so the drawings always match the generated part. Writes
out/fin_can_md/rev<N>/fin_can_md_rev<N>_blueprint.pdf. Units mm. z = 0 is the fin can's aft face (lip underside),
+z forward; the collar and tail cone are at z < 0. Every wall/thickness has its own arrowed dimension.
"""
from __future__ import annotations

import argparse
import math
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from matplotlib.backends.backend_pdf import PdfPages  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from parts import fin_can, fin_can_md  # noqa: E402

INK, DIM, FILL, FILL2, THR = "#111111", "#c0392b", "#f3c79a", "#a9c6f0", "#2c7a2c"
FS = 9
N_SHEETS = 8


# ------------------------------------------------------------------ drawing helpers
def ext(ax, p, q, color=DIM):
    ax.plot([p[0], q[0]], [p[1], q[1]], color=color, lw=0.6)


def dim_h(ax, x1, x2, y, ref1, ref2, text, fs=FS, inside=True):
    """Horizontal dimension between x1 and x2 at height y, with extension lines from the feature points ref1/ref2."""
    for x, r in ((x1, ref1), (x2, ref2)):
        if r is not None:
            ext(ax, (x, r), (x, y + (0.15 if y > r else -0.15) * abs(y - r) / max(abs(y - r), 1e-9)))
    _arrow_pair(ax, (x1, y), (x2, y), text, fs, inside, horiz=True)


def dim_v(ax, y1, y2, x, ref1, ref2, text, fs=FS, inside=True):
    """Vertical dimension between y1 and y2 at x, extension lines from x positions ref1/ref2."""
    for y, r in ((y1, ref1), (y2, ref2)):
        if r is not None:
            ext(ax, (r, y), (x + (0.15 if x > r else -0.15) * abs(x - r) / max(abs(x - r), 1e-9), y))
    _arrow_pair(ax, (x1 := x, y1), (x, y2), text, fs, inside, horiz=False)


def _arrow_pair(ax, a, b, text, fs, inside, horiz):
    a, b = np.array(a, float), np.array(b, float)
    L = np.linalg.norm(b - a)
    u = (b - a) / L
    if inside:
        ax.annotate("", b, a, arrowprops=dict(arrowstyle="<|-|>", color=DIM, lw=0.9, mutation_scale=9))
        m = (a + b) / 2
        ax.text(m[0], m[1], text, color=DIM, fontsize=fs, ha="center", va="center", rotation=0 if horiz else 90,
                bbox=dict(fc="white", ec="none", pad=0.8))
    else:   # small gap: arrows outside pointing in, text beside
        s = max(L * 0.9, 1.2)
        ax.annotate("", a, a - u * s, arrowprops=dict(arrowstyle="-|>", color=DIM, lw=0.9, mutation_scale=9))
        ax.annotate("", b, b + u * s, arrowprops=dict(arrowstyle="-|>", color=DIM, lw=0.9, mutation_scale=9))
        ax.plot([a[0], b[0]], [a[1], b[1]], color=DIM, lw=0.9)
        t = b + u * (s * 1.15)
        ax.text(t[0], t[1], text, color=DIM, fontsize=fs, ha="left" if horiz else "center",
                va="center" if horiz else "bottom", rotation=0, bbox=dict(fc="white", ec="none", pad=0.8))


def wall(ax, x1, x2, z, text, col_x, fs=FS):
    """Thickness between x1 and x2 at height z: arrows on the two edges (inside if wide, outside if thin),
    a dotted leader to the label column at col_x, and the label there."""
    w = x2 - x1
    if w >= 1.4:
        ax.annotate("", (x2, z), (x1, z), arrowprops=dict(arrowstyle="<|-|>", color=DIM, lw=1.0, mutation_scale=10))
    else:
        s = 0.9
        ax.annotate("", (x1, z), (x1 - s, z), arrowprops=dict(arrowstyle="-|>", color=DIM, lw=1.0, mutation_scale=10))
        ax.annotate("", (x2, z), (x2 + s, z), arrowprops=dict(arrowstyle="-|>", color=DIM, lw=1.0, mutation_scale=10))
    ax.plot([x2 + (0.9 if w < 1.4 else 0), col_x - 0.2], [z, z], color=DIM, lw=0.5, ls=":")
    ax.text(col_x, z, text, color=DIM, fontsize=fs, ha="left", va="center", bbox=dict(fc="white", ec="none", pad=0.5))


def vlen(ax, z1, z2, x, ref_x, text, fs=FS):
    """Axial length z1..z2 drawn at x with extension lines from ref_x; label rotated beside the line."""
    for z in (z1, z2):
        ax.plot([ref_x, x + 0.3], [z, z], color=DIM, lw=0.5)
    if abs(z2 - z1) >= 1.6:
        ax.annotate("", (x, z2), (x, z1), arrowprops=dict(arrowstyle="<|-|>", color=DIM, lw=1.0, mutation_scale=10))
    else:
        for z, d in ((z1, -1), (z2, 1)):
            ax.annotate("", (x, z), (x, z + d * 1.2), arrowprops=dict(arrowstyle="-|>", color=DIM, lw=1.0, mutation_scale=10))
    ax.text(x + 0.35, (z1 + z2) / 2, text, color=DIM, fontsize=fs, ha="left", va="center", rotation=90,
            bbox=dict(fc="white", ec="none", pad=0.5))


def leader(ax, xy, text, xytext, fs=FS - 0.5):
    ax.annotate(text, xy, xytext, fontsize=fs, color=INK, ha="left", va="center",
                arrowprops=dict(arrowstyle="->", color="0.35", lw=0.7),
                bbox=dict(fc="white", ec="0.6", boxstyle="round,pad=0.25"))


def radius(ax, center, r, ang_deg, text, fs=FS):
    a = math.radians(ang_deg)
    tip = (center[0] + r * math.cos(a), center[1] + r * math.sin(a))
    ax.annotate("", tip, center, arrowprops=dict(arrowstyle="-|>", color=DIM, lw=0.9, mutation_scale=9))
    ax.text(*(np.array(center) + 0.5 * (np.array(tip) - np.array(center))), text, color=DIM, fontsize=fs,
            ha="center", va="center", bbox=dict(fc="white", ec="none", pad=0.6))


def sheet(pdf, rev, k, title, scale_note=""):
    fig = plt.figure(figsize=(16.5, 11.7))   # A3 landscape
    fig.text(0.015, 0.985, f"FIN CAN rev {rev} + TAIL CONE  ·  {title}", fontsize=14, weight="bold", va="top")
    fig.text(0.985, 0.985, f"sheet {k}/{N_SHEETS} · all dimensions mm · {scale_note}", fontsize=9, ha="right", va="top",
             color="0.35")
    fig.text(0.985, 0.012, "source: projects/l1-cheap/design.yaml → parts/fin_can_md.py (same numbers as the STEP/STL)",
             fontsize=7.5, ha="right", color="0.45")
    return fig


def body_profile(p):
    rb, ri = p["body_od_mm"] / 2, p["sleeve_bore_d_mm"] / 2
    L, Lf, t = p["sleeve_length_mm"], p["fairing_length_mm"], p["lip_thickness_mm"]
    rl, Lc, rc = p["lip_bore_d_mm"] / 2, p["collar_length_mm"], p["collar_bore_d_mm"] / 2
    r_end = ri + p["feather_edge_mm"]
    return [(rl, 0), (rl, t), (ri, t), (ri, L + Lf), (r_end, L + Lf), (rb, L), (rb, -Lc), (rc, -Lc), (rc, 0)]


def draw_body(ax, p, mirror=True, thread=True):
    poly = body_profile(p)
    ax.fill(*zip(*poly), fc=FILL, ec=INK, lw=1.2)
    if mirror:
        ax.fill([-x for x, _ in poly], [z for _, z in poly], fc=FILL, ec=INK, lw=1.0, alpha=0.4)
        ax.axvline(0, color="0.45", ls=(0, (8, 3, 2, 3)), lw=0.8)
    if thread:
        rc, Lc = p["collar_bore_d_mm"] / 2, p["collar_length_mm"]
        P_, h = p["thread_pitch_mm"], p["thread_depth_mm"]
        n = int((Lc - p["thrust_ring_thk_mm"] - P_) / P_) + 1
        hw = (P_ - 0.3) / 2
        for k in range(n + 1):
            z0 = -Lc + k * P_
            g = [(rc, z0 - hw), (rc + h, z0 - (hw - h)), (rc + h, z0 + hw - h), (rc, z0 + hw)]
            g = [(x, min(max(z, -Lc), 0)) for x, z in g]
            ax.fill(*zip(*g), fc="white", ec=THR, lw=0.8)


# ------------------------------------------------------------------ sheets
def s1_overview(pdf, p, rev):
    rb, ri, rl = p["body_od_mm"] / 2, p["sleeve_bore_d_mm"] / 2, p["lip_bore_d_mm"] / 2
    L, Lf, Lc = p["sleeve_length_mm"], p["fairing_length_mm"], p["collar_length_mm"]
    r_end = ri + p["feather_edge_mm"]
    rc = p["collar_bore_d_mm"] / 2
    fig = sheet(pdf, rev, 1, "OVERVIEW: body half-section (revolve the right-hand profile 360° about the axis)", "scale ≈1:1")
    ax = fig.add_axes([0.05, 0.05, 0.62, 0.88])
    draw_body(ax, p)
    # diameters (stacked above)
    top = L + Lf
    dim_h(ax, -r_end, r_end, top + 6, top, top, f"Ø{2 * r_end:.2f}  fairing end (feather edge)")
    dim_h(ax, -rb, rb, L - 8, None, None, f"Ø{2 * rb:.3f}  sleeve OD")
    dim_h(ax, -ri, ri, L * 0.55, None, None, f"Ø{2 * ri:.3f}  sleeve bore")
    dim_h(ax, -rl, rl, 9, None, None, f"Ø{2 * rl:.2f}  lip bore")
    dim_h(ax, -rc, rc, -Lc / 2 - 3, None, None, f"Ø{2 * rc:.2f}  collar bore")
    dim_h(ax, -rb, rb, -Lc - 6, -Lc, -Lc, f"Ø{2 * rb:.3f}  collar OD (= sleeve OD)")
    # lengths (stacked right)
    x0 = rb + 8
    dim_v(ax, -Lc, 0, x0, rb, rb, f"{Lc}  collar")
    dim_v(ax, 0, L, x0, rb, rb, f"{L:.0f}  sleeve (= fin root chord)")
    dim_v(ax, L, L + Lf, x0, rb, r_end, f"{Lf:.0f}  fairing")
    dim_v(ax, -Lc, L + Lf, x0 + 16, rb, r_end, f"{Lc + L + Lf:.1f}  overall")
    ax.set_aspect("equal"); ax.set_xlim(-40, 60); ax.set_ylim(-Lc - 12, top + 12)
    ax.set_xlabel("radius (mm)"); ax.set_ylabel("z (mm)   0 = aft face, + forward"); ax.grid(alpha=0.15)
    ax.text(0.5, top + 9, "axis ℄", fontsize=8, color="0.4")
    ax2 = fig.add_axes([0.68, 0.1, 0.3, 0.8]); ax2.axis("off")
    ax2.text(0, 1, "WHAT IS WHERE\n\n"
             "• Walls and small features are too thin to read at this\n  scale: see the enlarged details.\n\n"
             "  Detail A (sheet 2): aft end, lip, collar, thread\n"
             "  Detail B (sheet 3): forward fairing taper\n"
             "  Fins (sheets 4-5): planform, airfoil, root fillets\n"
             "  Tail cone (sheet 6), thread profile (sheet 7)\n\n"
             "• 3 fins at 0°, 120°, 240°, trailing edge flush with z = 0.\n"
             "• No insert bosses or holes (rev 9): the tail cone retains\n  the motor.\n\n"
             "MATERIAL: PETG, 6 walls, 25 % gyroid.\n"
             "PRINT: collar end down; tree supports under the three\n"
             "fin trailing edges only.\n\n"
             "PLACEHOLDERS (measure, then regenerate):\n"
             f"  tube OD {p['tube_od_mm']}  → sleeve bore\n"
             f"  motor case OD {p['motor_case_od_mm']}  → lip bore\n"
             f"  thrust ring {p['thrust_ring_od_mm']} × {p['thrust_ring_thk_mm']:.2f}  → collar bore/length",
             fontsize=10, va="top", family="DejaVu Sans")
    pdf.savefig(fig); plt.close(fig)


def s2_aft(pdf, p, rev):
    rb, ri, rl = p["body_od_mm"] / 2, p["sleeve_bore_d_mm"] / 2, p["lip_bore_d_mm"] / 2
    t, Lc, rc = p["lip_thickness_mm"], p["collar_length_mm"], p["collar_bore_d_mm"] / 2
    ring, P_, h = p["thrust_ring_thk_mm"], p["thread_pitch_mm"], p["thread_depth_mm"]
    th_len = Lc - ring - P_
    fig = sheet(pdf, rev, 2, "DETAIL A: aft end (lip, sleeve wall, collar, thread band), right half", "scale ≈5:1")
    ax = fig.add_axes([0.04, 0.05, 0.66, 0.9])
    draw_body(ax, p, mirror=False)
    col = rb + 6.5                                       # label column
    # radial thicknesses (each at its own height)
    wall(ax, ri, rb, 10.0, f"{rb - ri:.2f}   sleeve wall (bore r {ri:.3f} → OD r {rb:.3f})", col)
    wall(ax, rl, ri, 1.8, f"{ri - rl:.2f}   lip ledge: lip bore r {rl:.2f} → sleeve bore (tube seat)", col)
    wall(ax, rl, rb, 0.6, f"{rb - rl:.2f}   lip, bore to OD", col)
    wall(ax, rc, rb, -6.0, f"{rb - rc:.2f}   collar wall in the ring zone (bore r {rc:.2f})", col)
    wall(ax, rc + h, rb, -Lc + P_, f"{rb - rc - h:.2f}   collar wall behind the thread", col)
    wall(ax, rc, rc + h, -Lc + 2 * P_ + 0.1, f"{h:.2f}   thread depth (groove root r {rc + h:.2f})", col)
    # axial lengths
    vlen(ax, 0, t, rb + 1.2, rb, f"{t:.2f} lip")
    vlen(ax, -ring, 0, rb + 2.6, rb, f"{ring:.2f} ring zone")
    vlen(ax, -Lc, -Lc + th_len, rb + 2.6, rb, f"{th_len:.2f} thread")
    vlen(ax, -Lc, 0, rb + 4.4, rb, f"{Lc} collar")
    # context (dashed reference parts)
    ax.add_patch(plt.Rectangle((p["tube_id_mm"] / 2, t), p["tube_od_mm"] / 2 - p["tube_id_mm"] / 2, 13, fc="#e6dcc8",
                               ec="0.5", lw=0.6, ls="--"))
    ax.text((p["tube_id_mm"] + p["tube_od_mm"]) / 4, t + 13.5, "tube\n(ref)", fontsize=7, color="0.4", ha="center")
    ax.add_patch(plt.Rectangle((16.2, -ring), p["thrust_ring_od_mm"] / 2 - 16.2, ring, fc="none", ec="0.45", lw=0.8,
                               ls="--", hatch=".."))
    ax.text(16.4, -ring / 2, "thrust ring (ref)", fontsize=7.5, color="0.3", va="center")
    ax.text(16.4, -Lc + 1, "← axis is 16 mm to the left", fontsize=7, color="0.45")
    ax.set_aspect("equal"); ax.set_xlim(16, rb + 26); ax.set_ylim(-Lc - 2.5, 17.5)
    ax.set_xlabel("radius (mm)"); ax.set_ylabel("z (mm)   0 = aft face (lip underside)"); ax.grid(alpha=0.12)
    ax3 = fig.add_axes([0.72, 0.12, 0.27, 0.75]); ax3.axis("off")
    rows = [("sleeve wall", rb - ri), ("lip axial thickness", t), ("lip ledge under the tube", ri - rl),
            ("lip, bore to OD", rb - rl), ("collar wall (ring zone)", rb - rc), ("collar wall behind thread", rb - rc - h),
            ("thread depth", h), ("collar length", Lc), ("ring zone (no thread)", ring), ("thread length", th_len),
            ("lip bore Ø", 2 * rl), ("sleeve bore Ø", 2 * ri), ("collar bore Ø", 2 * rc), ("OD Ø", 2 * rb)]
    ax3.text(0, 1, "TABLE: Detail A", fontsize=11, weight="bold", va="top")
    for k, (n, v) in enumerate(rows):
        ax3.text(0, 0.94 - k * 0.055, n, fontsize=10, va="top")
        ax3.text(0.95, 0.94 - k * 0.055, f"{v:.2f}", fontsize=10, va="top", ha="right", family="monospace", color=DIM)
    pdf.savefig(fig); plt.close(fig)


def s3_fairing(pdf, p, rev):
    rb, ri = p["body_od_mm"] / 2, p["sleeve_bore_d_mm"] / 2
    L, Lf = p["sleeve_length_mm"], p["fairing_length_mm"]
    r_end = ri + p["feather_edge_mm"]
    fig = sheet(pdf, rev, 3, "DETAIL B: forward fairing (taper from the sleeve OD to a feather edge on the tube)", "scale ≈4:1")
    ax = fig.add_axes([0.04, 0.05, 0.7, 0.9])
    draw_body(ax, p, mirror=False, thread=False)
    ax.add_patch(plt.Rectangle((p["tube_id_mm"] / 2, L - 10), p["tube_od_mm"] / 2 - p["tube_id_mm"] / 2, Lf + 18,
                               fc="#e6dcc8", ec="0.5", lw=0.6, ls="--"))
    ax.text(p["tube_id_mm"] / 2 + 0.2, L + Lf + 6, "tube (ref)", fontsize=7, color="0.4")
    col = rb + 6
    for zz in (L - 5, L, L + Lf * 0.25, L + Lf * 0.5, L + Lf * 0.75, L + Lf):
        r_o = rb if zz <= L else rb + (r_end - rb) * (zz - L) / Lf
        wall(ax, ri, r_o, zz, f"{r_o - ri:.2f}   wall at z = {zz:.0f}" + ("  (feather edge)" if zz == L + Lf else
                                                                         "  (fairing start)" if zz == L else ""), col)
    vlen(ax, L, L + Lf, rb + 2.0, rb, f"{Lf:.0f} fairing length")
    ang = math.degrees(math.atan((rb - r_end) / Lf))
    leader(ax, ((rb + r_end) / 2 + 0.05, L + Lf * 0.62), f"straight (ruled) taper, {ang:.2f}° from the axis",
           (rb + 6, L + Lf * 0.62 + 3))
    ax.text(ri - 0.2, L - 8.5, f"bore r {ri:.3f}", fontsize=8, ha="right", color="0.25")
    ax.text(rb + 0.2, L - 8.5, f"OD r {rb:.3f}", fontsize=8, color="0.25")
    ax.set_aspect("equal"); ax.set_xlim(17, rb + 26); ax.set_ylim(L - 10, L + Lf + 8)
    ax.set_xlabel("radius (mm)"); ax.set_ylabel("z (mm)"); ax.grid(alpha=0.12)
    pdf.savefig(fig); plt.close(fig)


def s4_fins(pdf, p, rev):
    rb, cr, ct, s = p["body_od_mm"] / 2, p["root_chord_mm"], p["tip_chord_mm"], p["span_mm"]
    R = p["te_fillet_r_mm"]
    fig = sheet(pdf, rev, 4, "FINS: planform and airfoil sections (×3 at 0°, 120°, 240°)", "planform ≈1.5:1")
    ax = fig.add_axes([0.04, 0.08, 0.46, 0.84])
    ax.add_patch(plt.Rectangle((rb - 6, -p["collar_length_mm"]), 6, cr + p["collar_length_mm"] + 12, fc="0.9", ec="0.5"))
    ax.text(rb - 3, cr + 8, "sleeve\n(ref)", fontsize=7, ha="center", color="0.4")
    pl = [(rb, 0), (rb, cr), (rb + s, ct), (rb + s, 0)]
    ax.fill(*zip(*pl), fc=FILL, ec=INK, lw=1.2)
    th = np.linspace(0, math.pi / 2, 40)
    sk = [(rb, 0)] + [(rb + R - R * math.cos(a), -R + R * math.sin(a)) for a in th[::-1]][::-1] + [(rb, -R)]
    sk = [(rb, 0), (rb + R, 0)] + [(rb + R - R * math.cos(a), -R + R * math.sin(a)) for a in th[::-1]] + [(rb, -R)]
    ax.fill(*zip(*sk), fc=FILL, ec=INK, lw=1.0)
    dim_h(ax, rb, rb + s, -p["collar_length_mm"] - 4, 0, 0, f"{s}  span (exposed, from the sleeve OD)")
    dim_v(ax, 0, cr, rb - 9, rb, rb, f"{cr:.0f}  root chord")
    dim_v(ax, 0, ct, rb + s + 4, rb + s, rb + s, f"{ct:.0f}  tip chord")
    dim_v(ax, ct, cr, rb + s + 11, rb + s, rb, f"{cr - ct:.0f}  LE sweep")
    radius(ax, (rb + R, -R), R, 180 + 35, f"R{R:.0f}")
    leader(ax, (rb + R * 0.4, -R * 0.35), "TE skirt: concave R6, tangent to the collar;\n"
           "same cross-section as the fin + root fillets\n(SolidWorks: face fillet aft face ↔ collar)", (rb + 14, -14))
    leader(ax, (rb + 0.4, cr * 0.65), f"root fillet R{p['root_fillet_r_mm']} both sides (sheet 5)", (rb + 10, cr + 8))
    ax.text(rb + s * 0.5, cr * 0.28, "trailing edge flush with the aft face (z = 0)", fontsize=8, ha="center")
    ax.text(rb + 1, -0.5, f"r = {rb:.3f}", fontsize=8, va="top")
    ax.text(rb + s - 1, -0.5, f"r = {rb + s:.3f}", fontsize=8, va="top", ha="right")
    ax.set_aspect("equal"); ax.grid(alpha=0.15)
    ax.set_xlim(rb - 16, rb + s + 22); ax.set_ylim(-p["collar_length_mm"] - 10, cr + 16)
    ax.set_xlabel("radius from the rocket axis (mm)"); ax.set_ylabel("z (mm)")
    # sections
    for k, (chord, tmax, te, lab) in enumerate(((cr, p["fin_thickness_mm"], p["te_root_thickness_mm"], "ROOT"),
                                                (ct, p["fin_tip_thickness_mm"], p["te_thickness_mm"], "TIP"))):
        a_ = fig.add_axes([0.52, 0.56 - k * 0.42, 0.38, 0.33])
        x = fin_can.chord_stations(81)
        yt = fin_can.naca_half_thickness(x, tmax, te)
        z = chord * (1 - x)
        a_.fill(np.r_[z, z[::-1]], np.r_[yt, -yt[::-1]], fc=FILL, ec=INK, lw=1.1)
        i = int(np.argmax(yt))
        dim_v(a_, -yt[i], yt[i], z[i], None, None, f"{2 * yt[i]:.2f} max")
        dim_v(a_, -te / 2, te / 2, -2.2, 0, 0, f"{te:.2f} TE", inside=False, fs=8)
        dim_h(a_, 0, chord, -tmax / 2 - 3.5, None, None, f"{chord:.0f} chord")
        dim_h(a_, z[i], chord, tmax / 2 + 2.2, yt[i], 0, f"{chord - z[i]:.1f} LE → max t", fs=8)
        r_le = 1.1019 * (tmax / chord) ** 2 * chord
        leader(a_, (chord - r_le * 0.3, 0), f"LE radius ≈ {r_le:.2f}", (chord * 0.72, -tmax / 2 - 1.2))
        # thickness table
        xs = [0.0, 0.05, 0.10, 0.25, 0.30, 0.50, 0.75, 0.90, 1.0]
        tt = 2 * fin_can.naca_half_thickness(np.array(xs), tmax, te)
        tab = fig.add_axes([0.905, 0.56 - k * 0.42, 0.09, 0.33]); tab.axis("off")
        tab.text(0, 1, f"{lab}\nx/c    t (mm)\n" + "\n".join(f"{xx:4.2f}  {tv:6.2f}" for xx, tv in zip(xs, tt)),
                 fontsize=8, va="top", family="monospace")
        a_.set_aspect("equal"); a_.grid(alpha=0.15)
        a_.set_xlim(-6, chord + 4); a_.set_ylim(-tmax / 2 - 6, tmax / 2 + 5)
        a_.set_title(f"{lab} section: NACA 4-digit symmetric (t = {tmax}) + linear blend to a blunt TE {te} "
                     f"→ actual max {2 * yt[i]:.2f} at {100 * (1 - z[i] / chord):.0f} % chord", fontsize=9)
        a_.set_xlabel("z (mm): TE at 0, LE at the chord")
    fig.text(0.54, 0.05, "Thickness and TE taper linearly root → tip. Exact point files: fin_can_md_rev"
             f"{rev}_airfoil_root.dat / _tip.dat (Selig format, import as curves).", fontsize=8.5)
    pdf.savefig(fig); plt.close(fig)


def s5_root_xsec(pdf, p, rev):
    import trimesh
    rb, ri, f, t = p["body_od_mm"] / 2, p["sleeve_bore_d_mm"] / 2, p["root_fillet_r_mm"], p["fin_thickness_mm"]
    z_cut = p["root_chord_mm"] * 0.7               # 30 % chord from the LE = max thickness at the root
    m = trimesh.load(ROOT / "out" / "fin_can_md" / f"rev{rev}" / f"fin_can_md_rev{rev}.stl", force="mesh")
    sec = m.section(plane_origin=[0, 0, z_cut], plane_normal=[0, 0, 1])
    pl, _ = sec.to_2D(to_2D=np.eye(4))
    fig = sheet(pdf, rev, 5, f"FIN ROOT CROSS-SECTION at z = {z_cut:.0f} (max fin thickness), looking forward; "
                f"cut from the actual part", "scale ≈3:1")
    ax = fig.add_axes([0.04, 0.05, 0.64, 0.9])
    for poly in pl.polygons_full:
        ax.fill(*poly.exterior.xy, fc=FILL, ec=INK, lw=1.0)
        for hole in poly.interiors:
            ax.fill(*hole.xy, fc="white", ec=INK, lw=1.0)
    # the fin at +X in the part = draw dimensions on the fin pointing +x
    yt = fin_can.naca_half_thickness(np.array([0.3]), t, p["te_root_thickness_mm"])[0]
    t_cut = 2 * yt
    span = p["span_mm"]
    t_tip_cut = 2 * fin_can.naca_half_thickness(np.array([0.3]), p["fin_tip_thickness_mm"], p["te_thickness_mm"])[0]
    xr = rb + 10
    ax.plot([xr, xr], [-t_cut / 2 - 8, -t_cut / 2], color=DIM, lw=0.5)
    ax.annotate("", (xr, t_cut / 2), (xr, -t_cut / 2), arrowprops=dict(arrowstyle="<|-|>", color=DIM, lw=1.0))
    ax.text(xr, -t_cut / 2 - 9, f"{t_cut:.1f} fin thickness\nnear the root", color=DIM, fontsize=FS, ha="center", va="top")
    ax.annotate("", (-ri, 0.0), (-rb, 0.0), arrowprops=dict(arrowstyle="<|-|>", color=DIM, lw=1.0))
    ax.plot([-rb, -rb - 6], [0, 0], color=DIM, lw=0.5, ls=":")
    ax.text(-rb - 6.3, 0, f"{rb - ri:.2f}\nsleeve wall\n(between fins)", color=DIM, fontsize=FS, ha="right", va="center")
    radius(ax, (rb * math.cos(math.radians(9)) + f * 0.9, t_cut / 2 + f * 0.95), f, 215, f"R{f}")
    ax.annotate("", (-rb, -rb - 4), (rb, -rb - 4), arrowprops=dict(arrowstyle="<|-|>", color=DIM, lw=1.0))
    ax.text(0, -rb - 4, f"Ø{2 * rb:.3f} sleeve OD", color=DIM, fontsize=FS, ha="center", va="center", bbox=dict(fc="white", ec="none"))
    ax.annotate("", (-ri, -6), (ri, -6), arrowprops=dict(arrowstyle="<|-|>", color=DIM, lw=1.0))
    ax.text(0, -6, f"Ø{2 * ri:.3f} bore", color=DIM, fontsize=FS, ha="center", va="center", bbox=dict(fc="white", ec="none"))
    leader(ax, (rb + 3, t_cut / 2 + 1.0), f"root fillet R{f}, both sides of every fin, full root length", (rb + 4, rb + 6))
    ax.text(rb + span - 2, 3.2, f"t ≈ {t_tip_cut:.1f} near the tip", fontsize=8, color=DIM, ha="right")
    ax.set_aspect("equal"); ax.grid(alpha=0.12)
    ax.set_xlim(-58, rb + span + 6); ax.set_ylim(-rb - 10, rb + 22)
    ax.set_xlabel("mm"); ax.set_ylabel("mm")
    ax2 = fig.add_axes([0.7, 0.2, 0.28, 0.6]); ax2.axis("off")
    ax2.text(0, 1, "NOTES\n\n• Cut through the real part at z = " + f"{z_cut:.0f}" + ", where the root\n  airfoil is thickest "
             "(30 % chord from the LE).\n\n• Fin thickness varies along the chord (sheet 4\n  table) and tapers root → tip.\n\n"
             f"• Root fillet R{f} blends each fin face into the\n  round sleeve; its outer edge lands on the sleeve\n  OD (no ledge).\n\n"
             "• Fins at 0°, 120°, 240°.", fontsize=10, va="top")
    pdf.savefig(fig); plt.close(fig)


def s6_tailcone(pdf, p, rev):
    Lc, Lb, ring, c = p["collar_length_mm"], p["boattail_length_mm"], p["thrust_ring_thk_mm"], p["thread_clearance_mm"]
    rb, re_, ri = p["body_od_mm"] / 2, p["boattail_end_od_mm"] / 2, p["tail_cone_bore_d_mm"] / 2
    rs = p["collar_bore_d_mm"] / 2 - c
    Ls = Lc - ring
    poly = [(ri, 0), (re_, 0), (rb, Lb), (rs, Lb), (rs, Lb + Ls), (ri, Lb + Ls)]
    fig = sheet(pdf, rev, 6, "TAIL CONE / MOTOR RETAINER (revolve 360°), shown as printed: aft end down", "scale ≈4:1")
    ax = fig.add_axes([0.04, 0.06, 0.6, 0.88])
    ax.fill(*zip(*poly), fc=FILL2, ec=INK, lw=1.2)
    dim_h(ax, ri, re_, -2.0, 0, 0, f"{re_ - ri:.2f}  wall at the aft end", inside=False)
    dim_h(ax, ri, rb, Lb + 1.2, None, None, f"{rb - ri:.2f}  wall at the shoulder")
    dim_h(ax, ri, rs, Lb + Ls + 1.6, Lb + Ls, Lb + Ls, f"{rs - ri:.2f}  shank wall", inside=False)
    dim_v(ax, 0, Lb, rb + 2.5, re_, rb, f"{Lb:.0f}  boattail")
    dim_v(ax, Lb, Lb + Ls, rb + 2.5, rs, rs, f"{Ls:.2f}  shank")
    dim_v(ax, 0, Lb + Ls, rb + 7.5, re_, rs, f"{Lb + Ls:.2f}  overall")
    ang = math.degrees(math.atan((rb - re_) / Lb))
    leader(ax, ((rb + re_) / 2, Lb / 2), f"straight taper {ang:.1f}° from the axis", (rb + 4, Lb * 0.35))
    for r_, z_, lab in ((ri - 1.2, -5.2, f"r {ri:.2f}\n(bore Ø{2 * ri:.2f})"), (re_ + 1.4, -5.2, f"r {re_:.2f}\n(Ø{2 * re_:.2f})"),
                        (rb, Lb + 4.5, f"r {rb:.3f}\n(Ø{2 * rb:.3f})"), (rs, Lb + Ls + 5.2, f"r {rs:.2f}\n(Ø{2 * rs:.2f})")):
        ax.text(r_, z_, lab, fontsize=8, ha="center", color="0.25")
    leader(ax, (rs + 0.3, Lb + Ls * 0.55), f"male thread on the shank: pitch {p['thread_pitch_mm']}, 45° flanks,\n"
           f"crest flat 0.4, clearance {c} (sheet 7)", (rb + 4, Lb + Ls * 0.75))
    leader(ax, ((rs + ri) / 2, Lb + Ls), "shank top face presses the thrust ring (retention)", (rb + 4, Lb + Ls + 3))
    ax.set_aspect("equal"); ax.set_xlim(16.5, 36); ax.set_ylim(-7, Lb + Ls + 8)
    ax.set_xlabel("radius (mm)"); ax.set_ylabel("height as printed (mm), aft end = 0"); ax.grid(alpha=0.15)
    ax3 = fig.add_axes([0.67, 0.15, 0.31, 0.7]); ax3.axis("off")
    rows = [("wall at the aft end", re_ - ri), ("wall at the shoulder", rb - ri), ("shank wall (to thread root)", rs - ri),
            ("bore Ø", 2 * ri), ("aft end Ø", 2 * re_), ("shoulder Ø (= sleeve OD)", 2 * rb), ("shank root Ø", 2 * rs),
            ("boattail length", Lb), ("shank length", Ls), ("taper angle (deg)", ang)]
    ax3.text(0, 1, "THICKNESS TABLE (tail cone)", fontsize=11, weight="bold", va="top")
    for k, (n, v) in enumerate(rows):
        ax3.text(0, 0.93 - k * 0.06, n, fontsize=10, va="top")
        ax3.text(0.9, 0.93 - k * 0.06, f"{v:.2f}", fontsize=10, va="top", ha="right", family="monospace", color=DIM)
    ax3.text(0, 0.25, "MATERIAL: ABS or ASA (the bore surrounds the nozzle\nexit during the burn), or PETG with an "
             "aluminium-tape\nlined bore. Print aft end down, no supports.", fontsize=9.5, va="top",
             bbox=dict(fc="#fff8e6", ec="0.6"))
    pdf.savefig(fig); plt.close(fig)


def s7_thread(pdf, p, rev):
    P_, h, c = p["thread_pitch_mm"], p["thread_depth_mm"], p["thread_clearance_mm"]
    rb_ = p["collar_bore_d_mm"] / 2
    hw = (P_ - 0.3) / 2
    hwr = hw - c * math.sqrt(2)
    rt = rb_ + min(h - c, hwr - 0.2)
    fig = sheet(pdf, rev, 7, "THREAD PROFILE (axial section through the joint)", "scale ≈20:1")
    ax = fig.add_axes([0.05, 0.08, 0.6, 0.85])
    for k in range(3):
        z0 = k * P_
        g = [(rb_ - 0.1, z0 - hw - 0.1), (rb_ + h, z0 - (hw - h)), (rb_ + h, z0 + hw - h), (rb_ - 0.1, z0 + hw + 0.1)]
        ax.fill(*zip(*g), fc="white", ec=THR, lw=1.4, label="female groove (cut into the fin can collar)" if k == 0 else None)
        r_ = [(rb_ - c - 0.35, z0 - hwr), (rb_, z0 - hwr), (rt, z0 - 0.2), (rt, z0 + 0.2), (rb_, z0 + hwr), (rb_ - c - 0.35, z0 + hwr)]
        ax.fill(*zip(*r_), fc=FILL2, ec=INK, lw=1.2, label="male ridge (on the tail cone shank)" if k == 0 else None)
    for x, lab in ((rb_ - c, f"r {rb_ - c:.2f}  shank root"), (rb_, f"r {rb_:.2f}  collar bore (minor)"),
                   (rt, f"r {rt:.2f}  ridge crest"), (rb_ + h, f"r {rb_ + h:.2f}  groove root (major)")):
        ax.axvline(x, color="0.55", ls="--", lw=0.6)
    dim_v(ax, 0, P_, rb_ + h + 0.25, rb_ + h, rb_ + h, f"pitch {P_}")
    dim_h(ax, rb_, rb_ + h, -1.75, None, None, f"depth {h}")
    dim_h(ax, rb_ - c, rb_, 2 * P_ + 1.55, None, None, f"{c} radial clearance", inside=False, fs=8)
    dim_v(ax, -hwr, hwr, rb_ - 0.05, None, None, f"{2 * hwr:.2f} ridge root", inside=False, fs=8)
    dim_v(ax, -0.2, 0.2, rt + 0.05, None, None, "0.40 crest", inside=False, fs=8)
    dim_v(ax, P_ - hw - 0.1, P_ + hw + 0.1, rb_ - 0.45, None, None, f"{2 * hw + 0.2:.2f} groove width", inside=False, fs=8)
    ax.text(rb_ + 0.5, -1.0, "45°", fontsize=10, color=DIM)
    ax.set_aspect("equal"); ax.grid(alpha=0.15); ax.legend(loc="upper right", fontsize=9)
    ax.set_xlim(rb_ - 0.9, rb_ + 2.0); ax.set_ylim(-2.4, 3 * P_ + 0.4)
    ax.set_xlabel("radius (mm)"); ax.set_ylabel("z (mm)")
    ax2 = fig.add_axes([0.68, 0.2, 0.3, 0.6]); ax2.axis("off")
    ax2.text(0, 1, "THREAD DATA\n\n"
             f"pitch                 {P_}\n"
             f"depth (female)        {h}\n"
             f"flank angle           45° (prints without supports)\n"
             f"hand                  right-hand\n"
             f"clearance             {c} radial and on the flanks\n"
             f"female major Ø        {2 * (rb_ + h):.2f}\n"
             f"female minor Ø        {2 * rb_:.2f}\n"
             f"male crest Ø          {2 * rt:.2f}\n"
             f"male root Ø           {2 * (rb_ - c):.2f}\n"
             f"thread length         {p['collar_length_mm'] - p['thrust_ring_thk_mm'] - P_:.2f}\n\n"
             "SolidWorks: Helix (pitch, height) + Swept Cut (groove)\n"
             "on the collar, Swept Boss (ridge) on the shank. Start\n"
             "both helices at the same angle; groove starts at the\n"
             "collar's aft face, ridge one pitch up. Or use the\n"
             "Thread feature with a custom profile.\n\n"
             "Print a test pair first; tune the clearance.",
             fontsize=10, va="top", family="monospace")
    pdf.savefig(fig); plt.close(fig)


def s8_steps(pdf, p, rev):
    rb = p["body_od_mm"] / 2
    fig = sheet(pdf, rev, 8, "SOLIDWORKS BUILD ORDER", "")
    txt = f"""FIN CAN (Part 1)   units mm, z = 0 at the aft face, + forward
 1. Front plane: sketch the right-hand profile of sheet 1 (use Detail A / B for the small numbers). Revolve 360°.
 2. Fin: planes normal to the radius at r = {rb - 1:.1f} (inside the sleeve so it fuses) and r = {rb + p['span_mm']:.3f};
    on them sketch the ROOT and TIP airfoils (sheet 4; import the .dat files with Insert > Curve > Curve Through XYZ Points),
    TE at z = 0, LE at z = chord. Loft root → tip.
 3. Fillet fin ↔ sleeve, R{p['root_fillet_r_mm']}, both sides, full root (sheet 5).
 4. TE skirt: Face Fillet between the fin's aft face (z = 0) and the collar OD, R{p['te_fillet_r_mm']:.0f} (sheet 4).
 5. Circular pattern fin + fillets + skirt: 3 instances, 360°.
 6. Collar thread (sheet 7): Helix pitch {p['thread_pitch_mm']}, start z = −{p['collar_length_mm']}, height
    {p['collar_length_mm'] - p['thrust_ring_thk_mm'] - p['thread_pitch_mm']:.2f}; Swept Cut of the groove profile.

TAIL CONE (Part 2)
 1. Sketch the profile of sheet 6, revolve 360°.
 2. Shank thread: Helix pitch {p['thread_pitch_mm']}, same hand/phase; Swept Boss of the ridge profile (sheet 7).

DRAWING TIPS: Section View through the axis for walls; Detail View (circle) for the lip/collar and fairing; dimension
from the aft face (z = 0) as the datum; one dimension per feature; tolerance only the fits: sleeve bore (tube),
lip bore (motor), thread (tail cone), e.g. ±0.1.

CHECK before printing: measured tube OD, motor case OD, thrust ring OD and length → design.yaml → regenerate.
"""
    fig.text(0.03, 0.92, txt, fontsize=10.5, va="top", family="monospace")
    pdf.savefig(fig); plt.close(fig)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--rev", type=int, required=True)
    ap.add_argument("--project", default="l1-cheap")
    a = ap.parse_args()
    p = fin_can_md.params(a.project)
    if not p.get("tail_cone"):
        sys.exit("blueprint.py covers the tail-cone layout (rev 8+)")
    out = ROOT / "out" / "fin_can_md" / f"rev{a.rev}" / f"fin_can_md_rev{a.rev}_blueprint.pdf"
    with PdfPages(out) as pdf:
        for fn in (s1_overview, s2_aft, s3_fairing, s4_fins, s5_root_xsec, s6_tailcone, s7_thread, s8_steps):
            fn(pdf, p, a.rev)
    print(out)


if __name__ == "__main__":
    main()
