"""Dimensioned blueprint (PDF) of the min-diameter fin can + tail cone, for re-modelling in SolidWorks.

  .venv/bin/python tools/blueprint.py --rev 9

Every number is read from projects/<project>/design.yaml through parts/fin_can_md.params() (the same source the
STEP/STL were built from), so the drawing always matches the generated part. Writes
out/fin_can_md/rev<N>/fin_can_md_rev<N>_blueprint.pdf. Units mm. z = 0 is the fin can's aft face (lip underside),
+z forward; the collar and tail cone are at z < 0.
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

INK, DIM, FILL, FILL2 = "#111111", "#c0392b", "#f3c79a", "#a9c6f0"


def dim(ax, p1, p2, text, off=(0, 0), fs=8, color=DIM):
    """Dimension line between p1 and p2, offset by `off`, with the label at the middle."""
    a = np.array(p1, float) + off
    b = np.array(p2, float) + off
    for p, q in ((p1, a), (p2, b)):
        if off != (0, 0):
            ax.plot([p[0], q[0]], [p[1], q[1]], color=color, lw=0.5, ls=":")
    ax.annotate("", a, b, arrowprops=dict(arrowstyle="<->", color=color, lw=0.8))
    m = (a + b) / 2
    ang = math.degrees(math.atan2(b[1] - a[1], b[0] - a[0]))
    if ang > 90 or ang < -90:
        ang += 180
    ax.text(m[0], m[1], text, color=color, fontsize=fs, ha="center", va="center", rotation=ang,
            bbox=dict(fc="white", ec="none", pad=0.6))


def note(ax, xy, text, xytext, fs=7.5):
    ax.annotate(text, xy, xytext, fontsize=fs, color=INK, ha="left", va="center",
                arrowprops=dict(arrowstyle="-", color="0.4", lw=0.6),
                bbox=dict(fc="white", ec="0.6", pad=2, boxstyle="round,pad=0.25"))


def frame(fig, title, rev, sheet, n):
    fig.text(0.02, 0.975, f"FIN CAN rev {rev} + TAIL CONE: {title}", fontsize=12, weight="bold", va="top")
    fig.text(0.98, 0.975, f"sheet {sheet}/{n} · mm · source design.yaml via parts/fin_can_md.py",
             fontsize=8, ha="right", va="top", color="0.35")


def sheet_section(pdf, p, rev):
    """Half-section of the fin can body (right half), dimensioned."""
    rb, ri = p["body_od_mm"] / 2, p["sleeve_bore_d_mm"] / 2
    L, Lf, t = p["sleeve_length_mm"], p["fairing_length_mm"], p["lip_thickness_mm"]
    rl, Lc, rc = p["lip_bore_d_mm"] / 2, p["collar_length_mm"], p["collar_bore_d_mm"] / 2
    r_end = ri + p["feather_edge_mm"]
    poly = [(rl, 0), (rl, t), (ri, t), (ri, L + Lf), (r_end, L + Lf), (rb, L), (rb, -Lc), (rc, -Lc), (rc, 0)]
    fig, ax = plt.subplots(figsize=(11.7, 8.3))
    frame(fig, "body half-section (revolve this profile 360° about the axis)", rev, 1, 5)
    ax.fill(*zip(*poly), fc=FILL, ec=INK, lw=1)
    ax.fill([-x for x, _ in poly], [z for _, z in poly], fc=FILL, ec=INK, lw=1, alpha=0.35)
    ax.axvline(0, color="0.5", ls="-.", lw=0.6)
    ax.text(0.3, L + Lf + 4, "rocket axis", fontsize=7, color="0.4")
    # thread band
    ax.add_patch(plt.Rectangle((rc, -Lc), p["thread_depth_mm"], Lc - p["thrust_ring_thk_mm"] - p["thread_pitch_mm"] + 1.1,
                               fc="none", ec="#2c7a2c", hatch="////", lw=0.6))
    # dimensions
    dim(ax, (-rb, L + 10), (rb, L + 10), f"Ø{2 * rb:.3f} sleeve OD", fs=8)
    dim(ax, (-ri, L * 0.6), (ri, L * 0.6), f"Ø{2 * ri:.3f} sleeve bore (tube OD {p['tube_od_mm']} + 2×0.09)")
    dim(ax, (-rl, t / 2 + 6), (rl, t / 2 + 6), f"Ø{2 * rl:.2f} lip bore (case {p['motor_case_od_mm']} + 0.18)")
    dim(ax, (-rc, -Lc / 2), (rc, -Lc / 2), f"Ø{2 * rc:.2f} collar bore = thread minor Ø")
    dim(ax, (-r_end, L + Lf + 3), (r_end, L + Lf + 3), f"Ø{2 * r_end:.2f} feather edge")
    dim(ax, (rb + 2, 0), (rb + 2, L), f"{L:.0f} sleeve (= fin root chord)", off=(14, 0))
    dim(ax, (rb + 2, L), (rb + 2, L + Lf), f"{Lf:.0f} fairing", off=(14, 0))
    dim(ax, (rb + 2, -Lc), (rb + 2, 0), f"{Lc} collar", off=(14, 0))
    dim(ax, (rl - 1, 0), (rl - 1, t), f"{t} lip", off=(-12, 0), fs=7)
    note(ax, (rc + 0.5, -Lc + 3), f"female thread: pitch {p['thread_pitch_mm']}, depth {p['thread_depth_mm']}, 45° flanks,\n"
         f"right-hand, starts at the collar's aft face, length "
         f"{Lc - p['thrust_ring_thk_mm'] - p['thread_pitch_mm']:.1f} mm (+ profile); see sheet 4", (rb + 22, -Lc - 6))
    note(ax, (rl + 0.5, 1.3), "LIP: motor thrust ring bears on the underside (z = 0)", (rb + 22, 8))
    note(ax, (ri, t + 1), "tube end sits on the lip top", (rb + 22, 18))
    note(ax, (rb, L + Lf / 2), "straight (ruled) taper to the feather edge", (rb + 22, L + Lf / 2 + 6))
    ax.text(rb + 22, 40, "fins: sheet 2 (TE flush at z = 0, root along the sleeve)\n"
            "3 × R" + f"{p['te_fillet_r_mm']:.0f} TE skirt under each fin root onto the collar: sheet 2",
            fontsize=7.5, va="center", bbox=dict(fc="#fff8e6", ec="0.6"))
    ax.set_aspect("equal")
    ax.set_xlim(-30, 95)
    ax.set_ylim(-Lc - 14, L + Lf + 14)
    ax.set_xlabel("radius (mm)")
    ax.set_ylabel("z (mm), 0 = aft face, + forward")
    ax.grid(alpha=0.2)
    ax.set_position([0.04, 0.06, 0.5, 0.86])
    # detail: aft end (lip + collar), 5x
    az = fig.add_axes([0.6, 0.08, 0.38, 0.8])
    az.fill(*zip(*poly), fc=FILL, ec=INK, lw=1)
    az.add_patch(plt.Rectangle((rc, -Lc), p["thread_depth_mm"], Lc - p["thrust_ring_thk_mm"] - p["thread_pitch_mm"] + 1.1,
                               fc="none", ec="#2c7a2c", hatch="////", lw=0.6))
    dim(az, (rl, t + 1.2), (rb, t + 1.2), f"{rb - rl:.2f}", fs=7)
    dim(az, (rb + 0.4, 0), (rb + 0.4, t), f"lip {t}", off=(1.2, 0), fs=7)
    dim(az, (ri, 6), (rb, 6), f"wall {rb - ri:.2f}", fs=7)
    dim(az, (rc, -Lc - 1.2), (rb, -Lc - 1.2), f"collar wall {rb - rc:.2f}", fs=7)
    dim(az, (rb + 0.4, -Lc), (rb + 0.4, 0), f"{Lc}", off=(1.2, 0), fs=7)
    dim(az, (rc - 0.3, -p["thrust_ring_thk_mm"]), (rc - 0.3, 0), f"ring zone {p['thrust_ring_thk_mm']:.2f}", off=(-0.8, 0), fs=7)
    az.text(rl, -2, f"r {rl:.2f}\n(lip bore)", fontsize=7, ha="right")
    az.text(rc - 0.15, -Lc + 2, f"r {rc:.2f}", fontsize=7, ha="right")
    az.text(rb + 0.2, 8.5, f"r {rb:.3f}", fontsize=7)
    az.text(ri - 0.15, 9, f"r {ri:.3f}", fontsize=7, ha="right")
    az.set_aspect("equal"); az.grid(alpha=0.25)
    az.set_xlim(rl - 3, rb + 4.5); az.set_ylim(-Lc - 3, 11)
    az.set_title("DETAIL: aft end (lip, collar, thread band), right half", fontsize=9)
    az.set_xlabel("radius (mm)")
    pdf.savefig(fig)
    plt.close(fig)


def sheet_fins(pdf, p, rev):
    rb, cr, ct, s = p["body_od_mm"] / 2, p["root_chord_mm"], p["tip_chord_mm"], p["span_mm"]
    fig = plt.figure(figsize=(11.7, 8.3))
    frame(fig, "fins (×3 at 0°, 120°, 240°)", rev, 2, 5)
    ax = fig.add_axes([0.05, 0.12, 0.42, 0.78])
    pl = [(rb, 0), (rb, cr), (rb + s, ct), (rb + s, 0)]
    ax.fill(*zip(*pl), fc=FILL, ec=INK)
    ax.add_patch(plt.Rectangle((rb - 8, -p["collar_length_mm"]), 8, cr + p["collar_length_mm"] + 10, fc="0.9", ec="0.5"))
    R = p["te_fillet_r_mm"]
    th = np.linspace(0, math.pi / 2, 30)
    ax.fill(np.r_[rb, rb + R - R * np.cos(th), rb], np.r_[0, -R + R * np.sin(th)[::-1] * 0 + (-R + R * np.sin(th)), 0][: 32],
            fc=FILL, ec=INK, lw=0.8)
    dim(ax, (rb, -3), (rb + s, -3), f"span {s}", off=(0, -9))
    dim(ax, (rb - 2, 0), (rb - 2, cr), f"root chord {cr:.0f}", off=(-6, 0))
    dim(ax, (rb + s + 2, 0), (rb + s + 2, ct), f"tip chord {ct:.0f}", off=(5, 0))
    dim(ax, (rb + s, ct + 2), (rb + s, cr + 2), f"LE sweep {cr - ct:.0f} (OR: {p['sweep_mm']})", off=(4, 0), fs=7)
    note(ax, (rb + R * 0.6, -R * 0.5), f"TE skirt: concave R{R:.0f}, tangent to the collar,\n"
         f"width {p['te_root_thickness_mm'] + 2 * p['root_fillet_r_mm']:.1f} (TE root + 2×root fillet)", (rb + 16, -16))
    note(ax, (rb + 0.5, cr * 0.6), f"root fillet R{p['root_fillet_r_mm']} both sides", (rb + 12, cr + 10))
    ax.text(rb + s / 2, cr / 3, "TE flush with the aft face (z = 0)\nLE straight root→tip", fontsize=7, ha="center")
    ax.set_aspect("equal"); ax.grid(alpha=0.2)
    ax.set_xlim(rb - 22, rb + s + 18); ax.set_ylim(-p["collar_length_mm"] - 14, cr + 18)
    ax.set_xlabel("radius from the rocket axis (mm)"); ax.set_ylabel("z (mm)")
    ax.set_title("planform (seen from the side)", fontsize=9)
    # airfoil sections
    ax2 = fig.add_axes([0.55, 0.52, 0.42, 0.36])
    ax3 = fig.add_axes([0.55, 0.12, 0.42, 0.3])
    for a_, chord, tmax, te, lab in ((ax2, cr, p["fin_thickness_mm"], p["te_root_thickness_mm"], "ROOT"),
                                    (ax3, ct, p["fin_tip_thickness_mm"], p["te_thickness_mm"], "TIP")):
        x = fin_can.chord_stations(61)
        yt = fin_can.naca_half_thickness(x, tmax, te)
        z = chord * (1 - x)                                   # LE at z = chord, TE at z = 0
        a_.fill(np.r_[z, z[::-1]], np.r_[yt, -yt[::-1]], fc=FILL, ec=INK)
        dim(a_, (chord, 0), (0, 0), f"chord {chord:.0f}", off=(0, -tmax / 2 - 3), fs=7)
        i = int(np.argmax(yt))
        dim(a_, (z[i], -yt[i]), (z[i], yt[i]), f"t {tmax:.1f}", off=(0, 0), fs=7)
        dim(a_, (0, -te / 2), (0, te / 2), f"TE {te:.2f}", off=(-4, 0), fs=7)
        a_.set_aspect("equal"); a_.grid(alpha=0.2)
        a_.set_title(f"{lab} section: NACA 4-digit symmetric, t_max {tmax} at {100 * (1 - z[i] / chord):.0f} % chord "
                     f"(from LE), blunt TE {te}", fontsize=8)
        a_.set_xlabel("z (mm), TE at 0 → LE at chord"); a_.set_ylim(-tmax / 2 - 7, tmax / 2 + 4)
    fig.text(0.55, 0.045, "Linear taper root → tip for t_max and TE. Exact coordinates: fin_can_md_rev"
             f"{rev}_airfoil_root.dat / _tip.dat (Selig) and fin_can_md_rev{rev}_fin_only.step.\n"
             "Half-thickness y_t = 5 t (0.2969√x − 0.1260x − 0.3516x² + 0.2843x³ − 0.1015x⁴) + linear blend to the TE.",
             fontsize=7.5)
    pdf.savefig(fig)
    plt.close(fig)


def sheet_tailcone(pdf, p, rev):
    Lc, Lb, ring, c = p["collar_length_mm"], p["boattail_length_mm"], p["thrust_ring_thk_mm"], p["thread_clearance_mm"]
    rb, re_, ri = p["body_od_mm"] / 2, p["boattail_end_od_mm"] / 2, p["tail_cone_bore_d_mm"] / 2
    rs = p["collar_bore_d_mm"] / 2 - c
    Ls = Lc - ring
    # printed coordinates: aft end at 0
    poly = [(ri, 0), (re_, 0), (rb, Lb), (rs, Lb), (rs, Lb + Ls), (ri, Lb + Ls)]
    fig, ax = plt.subplots(figsize=(11.7, 8.3))
    frame(fig, "tail cone / motor retainer (revolve 360°), printed aft end down", rev, 3, 5)
    ax.fill(*zip(*poly), fc=FILL2, ec=INK)
    ax.fill([-x for x, _ in poly], [z for _, z in poly], fc=FILL2, ec=INK, alpha=0.35)
    ax.axvline(0, color="0.5", ls="-.", lw=0.6)
    dim(ax, (-re_, -3), (re_, -3), f"Ø{2 * re_:.2f} aft end OD")
    dim(ax, (-rb, Lb + 2), (rb, Lb + 2), f"Ø{2 * rb:.3f} (= sleeve OD, flush)", off=(0, 0))
    dim(ax, (-ri, Lb / 2), (ri, Lb / 2), f"Ø{2 * ri:.2f} bore (clears the Ø{p['motor_case_od_mm']} case / nozzle)")
    dim(ax, (-rs, Lb + Ls + 3), (rs, Lb + Ls + 3), f"Ø{2 * rs:.2f} shank root Ø (collar bore − 2×{c})")
    dim(ax, (rb + 2, 0), (rb + 2, Lb), f"{Lb:.0f} boattail ({math.degrees(math.atan((rb - re_) / Lb)):.1f}° half-angle)",
        off=(12, 0))
    dim(ax, (rb + 2, Lb), (rb + 2, Lb + Ls), f"{Ls:.2f} shank (= collar {Lc} − ring {ring:.2f})", off=(12, 0))
    note(ax, (rs + 0.5, Lb + Ls / 2), f"male thread: pitch {p['thread_pitch_mm']}, 45° flanks, crest flat 0.4,\n"
         f"major Ø ≈ {2 * (p['collar_bore_d_mm'] / 2 + min(p['thread_depth_mm'] - c, (p['thread_pitch_mm'] - 0.3) / 2 - c * math.sqrt(2) - 0.2)):.2f};"
         f" clearance {c} radial and on the flanks (sheet 4)", (rb + 14, Lb + Ls + 6))
    note(ax, ((rs + ri) / 2, Lb + Ls), "shank top face bears on the thrust ring (retention)", (rb + 14, Lb + Ls + 14))
    ax.text(rb + 14, 6, "MATERIAL: ABS or ASA (surrounds the nozzle exit during the burn),\n"
            "or PETG with an aluminium-tape-lined bore. Print aft end down, no supports.", fontsize=7.5,
            bbox=dict(fc="#fff8e6", ec="0.6"))
    ax.set_aspect("equal"); ax.grid(alpha=0.2)
    ax.set_xlim(-30, 85); ax.set_ylim(-9, Lb + Ls + 22)
    ax.set_xlabel("radius (mm)"); ax.set_ylabel("height as printed (mm), aft end = 0")
    pdf.savefig(fig)
    plt.close(fig)


def sheet_thread(pdf, p, rev):
    P_, h, c = p["thread_pitch_mm"], p["thread_depth_mm"], p["thread_clearance_mm"]
    rb_ = p["collar_bore_d_mm"] / 2
    hw = (P_ - 0.3) / 2
    hwr = hw - c * math.sqrt(2)
    rt = rb_ + min(h - c, hwr - 0.2)
    fig, ax = plt.subplots(figsize=(11.7, 8.3))
    frame(fig, "thread profile detail (axial section, one pitch shown ×3)", rev, 4, 5)
    for k in range(3):
        z0 = k * P_
        g = [(rb_ - 0.1, z0 - hw - 0.1), (rb_ + h, z0 - (hw - h)), (rb_ + h, z0 + hw - h), (rb_ - 0.1, z0 + hw + 0.1)]
        ax.fill(*zip(*g), fc="white", ec="#2c7a2c", lw=1.2, label="female groove (cut into the collar)" if k == 0 else None)
        r_ = [(rb_ - c - 0.3, z0 - hwr), (rb_, z0 - hwr), (rt, z0 - 0.2), (rt, z0 + 0.2), (rb_, z0 + hwr), (rb_ - c - 0.3, z0 + hwr)]
        ax.fill(*zip(*r_), fc=FILL2, ec=INK, lw=1, alpha=0.9, label="male ridge (on the tail cone shank)" if k == 0 else None)
    ax.axvline(rb_, color="0.4", ls="--", lw=0.6)
    ax.axvline(rb_ - c, color="0.4", ls=":", lw=0.6)
    dim(ax, (rb_ + h + 0.15, 0), (rb_ + h + 0.15, P_), f"pitch {P_}", fs=8)
    dim(ax, (rb_, -1.9), (rb_ + h, -1.9), f"depth {h}", fs=8)
    dim(ax, (rb_ - c, 2 * P_ + 1.6), (rb_, 2 * P_ + 1.6), f"{c}", fs=8)
    ax.text(rb_ + 0.05, 2 * P_ + 2.3, "radial clearance", fontsize=7)
    ax.text(rb_ - c - 0.25, -2.6, f"r = {rb_ - c:.2f} shank root\nr = {rb_:.2f} collar bore (minor)\n"
            f"r = {rb_ + h:.2f} groove root (major)\nr = {rt:.2f} ridge crest", fontsize=7.5, va="top")
    ax.set_aspect("equal"); ax.grid(alpha=0.2); ax.legend(loc="upper right", fontsize=8)
    ax.set_xlim(rb_ - 0.8, rb_ + 2.2); ax.set_ylim(-3.6, 3 * P_ + 0.6)
    ax.set_xlabel("radius (mm)"); ax.set_ylabel("z (mm)")
    fig.text(0.06, 0.06, "45° flanks print without supports in both parts. Groove width at the bore 2.4, ridge root "
             f"width {2 * hwr:.2f}, crest flat 0.4. Right-hand helix. In SolidWorks: Helix (pitch {P_}, height = thread "
             "length) + Swept Cut of the groove profile on the collar,\nSwept Boss of the ridge profile on the shank. "
             "Both helices must start at the same angle and z phase (groove at the collar aft face; ridge one pitch up), or "
             "use the SolidWorks Thread feature with a custom profile.", fontsize=8)
    pdf.savefig(fig)
    plt.close(fig)


def sheet_steps(pdf, p, rev):
    fig = plt.figure(figsize=(11.7, 8.3))
    frame(fig, "SolidWorks build order + key numbers", rev, 5, 5)
    rb = p["body_od_mm"] / 2
    steps = f"""FIN CAN (Part 1)                                                            units mm, z = 0 at the aft face, +z forward
 1. Front plane: sketch the half-section of sheet 1 (lip, sleeve, fairing, collar); Revolve 360° about the axis.
 2. Top-view sketch on the front plane: fin planform of sheet 2 (root at r = {rb:.3f} along z 0→{p['root_chord_mm']:.0f}, tip at
    r = {rb + p['span_mm']:.3f}, TE flush at z = 0). Fin solid: Loft between the ROOT and TIP airfoil sketches (sheet 2),
    placed in planes normal to the radius at r = {rb - 1:.1f} (inside the sleeve, so it fuses) and r = {rb + p['span_mm']:.3f}.
    Easiest: import fin_can_md_rev{rev}_airfoil_root.dat / _tip.dat as curves (Insert > Curve > Curve Through XYZ Points).
 3. Fillet the fin-to-sleeve edges R{p['root_fillet_r_mm']} (both sides; SolidWorks Fillet, constant radius, tangent propagation).
 4. TE skirt: Fillet (face fillet / "Face Fillet" type) between each fin's AFT FACE (TE strip + root fillets, at z = 0)
    and the collar's outer cylinder, radius R{p['te_fillet_r_mm']:.0f}. It follows the fin footprint automatically
    (tangent to the collar at z = −{p['te_fillet_r_mm']:.0f}, meets the aft face at r = {rb + p['te_fillet_r_mm']:.3f}).
 5. Circular pattern: fin + fillets + skirt, 3 instances, 360°.
 6. Collar thread: Helix (pitch {p['thread_pitch_mm']}, start at z = −{p['collar_length_mm']}, length
    {p['collar_length_mm'] - p['thrust_ring_thk_mm'] - p['thread_pitch_mm']:.2f}) + Swept Cut of the groove profile (sheet 4).
 7. Check: no M3 insert bosses or holes in rev 9 (the tail cone is the motor retainer).

TAIL CONE (Part 2)
 1. Sketch the half-section of sheet 3; Revolve 360°.
 2. Shank thread: Helix (pitch {p['thread_pitch_mm']}) + Swept Boss of the ridge profile (sheet 4); same hand and phase as the collar.
 3. Test-fit print first; adjust thread clearance ({p['thread_clearance_mm']}) to your printer.

ASSEMBLY
 Tube (OD {p['tube_od_mm']}) slides into the sleeve to the lip (epoxy). Motor goes in from the aft end until the thrust ring
 (Ø{p['thrust_ring_od_mm']} × {p['thrust_ring_thk_mm']:.2f} PLACEHOLDER) seats on the lip underside. Screw the tail cone into the
 collar until its shank presses the ring. The nozzle sits ≈ {p['collar_length_mm'] + p['boattail_length_mm'] - p['thrust_ring_thk_mm']:.0f} mm inside the cone.

PLACEHOLDERS TO MEASURE before printing: tube OD (sets the sleeve bore), motor case OD (lip bore),
 thrust ring OD and length (collar bore and length). Change them in design.yaml and re-run make.py: every sheet updates.
PRINT: fin can aft (collar) end down, tree supports under the three fin trailing edges only; 6 walls, 25 % gyroid.
"""
    fig.text(0.04, 0.92, steps, fontsize=8.6, va="top", family="monospace")
    pdf.savefig(fig)
    plt.close(fig)


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
        sheet_section(pdf, p, a.rev)
        sheet_fins(pdf, p, a.rev)
        sheet_tailcone(pdf, p, a.rev)
        sheet_thread(pdf, p, a.rev)
        sheet_steps(pdf, p, a.rev)
    print(out)


if __name__ == "__main__":
    main()
