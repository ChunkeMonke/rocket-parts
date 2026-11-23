"""Engineering drawing set (ISO/ASME-style, A3, black & white) for the nose cone, cap and ballast plug.

  .venv/bin/python tools/drawing_nose.py --rev 1

Sheets: 1 nose cone section A-A + view from aft, 2 details (base thread ring, ballast bulkhead) + ogive table,
3 bottom cap and ballast plug. Geometry cut from out/nose_*/rev<N>/*.stl; numbers from design.yaml via
parts/nose_cone.params(). Writes out/nose_cone/rev<N>/nose_cone_rev<N>_drawings.pdf.
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
from matplotlib.patches import Circle, Rectangle  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))
import drawing as D  # noqa: E402
from parts import nose_cone as N  # noqa: E402

NS = 3
SUB = "NOSE CONE: BALLAST POCKET, PAYLOAD BAY, SCREW CAP"


def sheet(title, k, rev, scale, p, material="PETG"):
    return D.new_sheet(title, k, rev, scale, p, subtitle=SUB, prefix="NC", material=material, n_sheets=NS)


def thread_numbers(p, r_bore):
    P_, h, c = p["thread_pitch_mm"], p["thread_depth_mm"], p["thread_clearance_mm"]
    hw = (P_ - 0.3) / 2
    hwr = hw - c * math.sqrt(2)
    crest = r_bore + min(h - c, hwr - 0.2)
    return dict(P=P_, h=h, c=c, major=2 * (r_bore + h), minor=2 * r_bore, male_root=2 * (r_bore - c), male_crest=2 * crest)


def s1(pdf, p, rev):
    m = D.load(rev, "nose_cone")
    L, zs, R = p["length_mm"], p["shoulder_length_mm"], p["base_od_mm"] / 2
    rsh = p["shoulder_od_mm"] / 2
    w = p["wall_thickness_mm"]
    lay = N.layout(p)
    zt = float(m.bounds[1][2])
    fig, paper = sheet("NOSE CONE", 1, rev, "1:1", p)
    ax = D.view(fig, 15, 75, 300, 205, 1.0, 110, 0)
    for ext, holes in D.section_y0(m):
        D.hatch_poly(ax, ext, holes)
    D.centerline(ax, (-8, 0), (zt + 8, 0))
    D.view_label(ax, (110, -R - 40), "SECTION A-A")
    # lengths (below, all horizontal at the base radius line)
    D.dim(ax, (0, -R), (zs, -R), -12, f"{zs:.0f}")
    D.dim(ax, (zs, -R), (zt, -R), -12, f"{zt - zs:.2f}")
    D.dim(ax, (0, -R), (zt, -R), -24, f"{zt:.2f}")
    D.dim(ax, (lay["zb_top"], R * 0.6), (zt, R * 0.6), 18, f"{zt - lay['zb_top']:.2f}  BALLAST POCKET")
    D.dim(ax, (0, rsh), (lay["zb_bot"], rsh), 26, f"{lay['zb_bot']:.0f}  PAYLOAD BAY (TO BULKHEAD)")
    # diameters
    D.dim(ax, (zs + 4, -R), (zs + 4, R), 0, f"Ø{2 * R:.3f}", tol="±0.1")
    D.dim(ax, (zs * 0.45, -rsh), (zs * 0.45, rsh), 0, f"Ø{2 * rsh:.3f}", tol="±0.05")
    D.dim(ax, (lay["zb_top"] - 3, -p["plug_bore_d_mm"] / 2), (lay["zb_top"] - 3, p["plug_bore_d_mm"] / 2), 0,
          f"Ø{p['plug_bore_d_mm']:.1f}")
    D.leader(ax, (zt - 0.2, 0), (zt + 4, 10), f"TIP FLAT Ø{2 * p['tip_flat_r_mm']:.2f}")
    D.leader(ax, (zs + 60, R - 0.4), (zs + 55, R + 14),
             f"TANGENT OGIVE  L {L:.0f}  R {R:.3f}  ρ {(R * R + L * L) / (2 * R):.1f}  (TABLE, SHEET 2)")
    D.leader(ax, (2, p["cap_bore_d_mm"] / 2 + 0.3), (-4, R + 34), "INT. THREAD P2.5 45° — DETAIL B")
    D.leader(ax, (lay["zb_bot"] + 2, p["plug_bore_d_mm"] / 2 + 0.3), (lay["zb_bot"] - 30, R + 34),
             "BULKHEAD + THREADED FILL HOLE — DETAIL C")
    D.detail_circle(ax, (7, -16), 12, "B")
    D.detail_circle(ax, (lay["zb_bot"] + 2, -13), 12, "C")
    D.datum(ax, (0, -rsh - 1), "A")
    ax.text(-2, -R - 30, "DATUM A = SHOULDER AFT FACE", fontsize=5.5)
    # wall callouts
    D.leader(ax, (zs + 100, -R * 0.55), (zs + 112, -R - 4), f"WALL {w} NORMAL TO THE SURFACE (TYP.)")
    # view from aft
    ev = D.view(fig, 318, 175, 90, 95, 1.5, 0, 0)
    for r_, ls in ((rsh, "-"), (R, (0, (4, 2))), (p["cap_bore_d_mm"] / 2, "-"), (p["cap_bore_d_mm"] / 2 + p["thread_depth_mm"], (0, (4, 2))),
                   (p["plug_bore_d_mm"] / 2, "-")):
        ev.add_patch(Circle((0, 0), r_, fill=False, lw=D.LW_VIS if ls == "-" else D.LW_THIN, ls=ls))
    D.centerline(ev, (-R - 4, 0), (R + 4, 0)); D.centerline(ev, (0, -R - 4), (0, R + 4))
    for sgn in (1, -1):
        y = sgn * (R + 6)
        ev.plot([0, 0], [y, y - sgn * D.k_(ev, 5)], color="k", lw=1.2)
        D.arrow(ev, (-D.k_(ev, 7), y), (0, y))
        ev.text(-D.k_(ev, 10), y, "A", fontsize=9, weight="bold", va="center")
    D.view_label(ev, (0, -R - 10), "VIEW FROM AFT (1.5:1)")
    paper.text(320, 165, "NOTES\n"
               "1. Print TIP UP, no supports (bulkhead underside 45°).\n"
               f"2. Wall {w} = 2 outer + 3 inner lines: fully solid.\n"
               "3. Ballast: lead shot / steel BBs in epoxy through the\n   Ø20 fill hole; close with the plug (sheet 3).\n"
               "4. Shoulder is a snug slip in the Ø38.735 tube ID.\n"
               "5. Flight nose mass 65 g (63 printed + 2 ballast); +25 g ballast\n   recommended for 1.8 cal (EDR L1C-EDR-001 §7).",
               fontsize=6.3, va="top", linespacing=1.45)
    pdf.savefig(fig); plt.close(fig)


def s2(pdf, p, rev):
    m = D.load(rev, "nose_cone")
    secs = D.section_y0(m)
    zs, R = p["shoulder_length_mm"], p["base_od_mm"] / 2
    rsh, w = p["shoulder_od_mm"] / 2, p["wall_thickness_mm"]
    lay = N.layout(p)
    rc, h, P_ = p["cap_bore_d_mm"] / 2, p["thread_depth_mm"], p["thread_pitch_mm"]
    Hr = p["cap_ring_height_mm"]
    r_in = rsh - w
    fig, paper = sheet("NOSE CONE — DETAILS", 2, rev, "4:1", p)
    # detail B: base / thread ring (upper half)
    ax = D.view(fig, 15, 150, 190, 132, 4.0, 10, 17)
    for ext, holes in secs:
        D.hatch_poly(ax, ext, holes, lw=0.9)
    D.view_label(ax, (10, 2.2), "DETAIL B (4:1)")
    D.dim(ax, (6, rc), (6, rsh), 0, f"{rsh - rc:.2f}", inside=False)
    D.dim(ax, (Hr + 6, r_in), (Hr + 6, rsh), 0, f"{w:.2f}", inside=False)
    D.dim(ax, (0, rsh), (Hr, rsh), 8, f"{Hr:.0f}")
    D.dim(ax, (0, rsh), (Hr - P_, rsh), 16, f"{Hr - P_:.1f} THREAD")
    D.leader(ax, (1.2, rc), (-5, rc - 3.5), f"Ø{2 * rc:.2f} +0.10/0 (MINOR)", ha="right")
    D.leader(ax, (3.6, rc + h - 0.1), (-5, rc + 5.5), f"Ø{2 * (rc + h):.2f} (MAJOR)", ha="right")
    D.leader(ax, (Hr + 2, r_in), (Hr + 6, r_in - 3.5), f"Ø{2 * r_in:.3f} SHOULDER BORE")
    D.leader(ax, (0.2, rsh - 0.3), (-5, rsh + 3), f"Ø{2 * rsh:.3f} SHOULDER OD", ha="right")
    # detail C: bulkhead (upper half)
    zb, zt_b = lay["zb_bot"], lay["zb_top"]
    rh, rl = p["plug_bore_d_mm"] / 2, p["plug_head_d_mm"] / 2 + 1.0
    ax2 = D.view(fig, 210, 150, 200, 132, 4.0, zb + 2, 13)
    for ext, holes in secs:
        D.hatch_poly(ax2, ext, holes, lw=0.9)
    D.view_label(ax2, (zb + 2, -1.2), "DETAIL C (4:1)")
    D.dim(ax2, (zb, rh), (zt_b, rh), -8, f"{zt_b - zb:.0f}")
    D.dim(ax2, (zb - 0.5, rh), (zb - 0.5, rl), 0, f"{rl - rh:.1f}", inside=False)
    D.leader(ax2, (zb + 1.5, rh), (zb - 9, rh - 3.2), f"Ø{2 * rh:.1f} FILL HOLE, INT. THREAD P2.5,\nL {p['ballast_bulkhead_thickness_mm'] - P_:.1f} (MINOR)", ha="right")
    D.leader(ax2, ((zb + zb - (13)) / 2 + 1, rl + 3), (zb - 12, rl + 8), "45° UNDERSIDE (NO SUPPORTS)", ha="right")
    D.leader(ax2, (zt_b + 0.4, rh + 2), (zt_b + 6, rh + 7), f"POCKET FLOOR, {(N.z_of_tip(p) - zt_b):.0f} FROM THE TIP")
    D.leader(ax2, (zb + 0.5, rl - 0.3), (zb + 8, rl - 6), f"PLUG LANDING Ø{2 * rl:.0f}")
    # ogive table
    Lo = p["length_mm"]
    xs = [0, 5, 10, 20, 30, 40, 60, 80, 100, 120, 140, 165]
    x0, y0 = 20, 66
    cw = 25
    paper.add_patch(Rectangle((x0, y0), 30 + cw * len(xs), 24, fill=False, lw=0.6))
    paper.text(x0 + 2, y0 + 19.5, "x FROM TIP", fontsize=6)
    paper.text(x0 + 2, y0 + 11.5, "OUTER Ø", fontsize=6)
    paper.text(x0 + 2, y0 + 3.5, "OUTER r", fontsize=6)
    for j, x in enumerate(xs):
        r_ = N.ogive_r(p, x)
        cx = x0 + 30 + j * cw
        paper.plot([cx, cx], [y0, y0 + 24], lw=0.3, color="k")
        paper.text(cx + cw / 2, y0 + 19.5, f"{x}", fontsize=6, ha="center")
        paper.text(cx + cw / 2, y0 + 11.5, f"{2 * r_:.2f}", fontsize=6, ha="center")
        paper.text(cx + cw / 2, y0 + 3.5, f"{r_:.3f}", fontsize=6, ha="center")
    for yy in (8, 16):
        paper.plot([x0, x0 + 30 + cw * len(xs)], [y0 + yy, y0 + yy], lw=0.3, color="k")
    rho = (R * R + Lo * Lo) / (2 * R)
    paper.text(x0, y0 + 27, f"TANGENT OGIVE: r(x) = √(ρ² − (L − x)²) + R − ρ,  L {Lo:.0f}, R {R:.4f}, ρ {rho:.2f}. "
               "In SolidWorks: 3-point arc, radius ρ, tangent to the body line at the base.", fontsize=6)
    pdf.savefig(fig); plt.close(fig)


def s3(pdf, p, rev):
    mc, mp = D.load(rev, "nose_cap"), D.load(rev, "nose_plug")
    tf, ls_, wc = p["cap_flange_thickness_mm"], p["cap_shank_length_mm"], p["cap_wall_mm"]
    rsh = p["shoulder_od_mm"] / 2
    rc = p["cap_bore_d_mm"] / 2
    tc = thread_numbers(p, rc)
    tp = thread_numbers(p, p["plug_bore_d_mm"] / 2)
    fig, paper = sheet("BOTTOM CAP + BALLAST PLUG", 3, rev, "2:1 / 3:1", p)
    # cap section (axis horizontal, flange left)
    ax = D.view(fig, 15, 150, 190, 128, 2.0, (tf + ls_) / 2, 0)
    for ext, holes in D.section_y0(mc):
        D.hatch_poly(ax, ext, holes, lw=0.9)
    D.centerline(ax, (-4, 0), (tf + ls_ + 4, 0))
    D.view_label(ax, ((tf + ls_) / 2, -rsh - 13), "CAP — SECTION A-A (2:1)")
    D.dim(ax, (0, -rsh), (tf, -rsh), -8, f"{tf:.0f}")
    D.dim(ax, (tf, -rc), (tf + ls_, -rc), -14 - (rsh - rc) * 2, f"{ls_:.0f}")
    D.dim(ax, (0, -rsh), (tf + ls_, -rsh), -24, f"{tf + ls_:.0f}")
    D.dim(ax, (tf / 2, -rsh), (tf / 2, rsh), -12, f"Ø{2 * rsh:.3f}")
    D.dim(ax, (tf + ls_ - 1, -(rc - p['thread_clearance_mm'] - wc)), (tf + ls_ - 1, rc - p['thread_clearance_mm'] - wc), 0,
          f"Ø{2 * (rc - p['thread_clearance_mm'] - wc):.2f}")
    D.dim(ax, (tf + ls_ + 1, -tc["male_root"] / 2), (tf + ls_ + 1, tc["male_root"] / 2), 12, f"Ø{tc['male_root']:.2f}")
    D.leader(ax, (tf + ls_ * 0.6, tc["male_crest"] / 2), (tf + 2, rsh + 8),
             f"EXT. THREAD P{tc['P']} 45° RH, CREST Ø{tc['male_crest']:.2f}, ROOT Ø{tc['male_root']:.2f}")
    D.leader(ax, (tf / 2, p["kevlar_hole_spacing_mm"] / 2 + p["kevlar_hole_d_mm"] / 2), (-6, rsh + 6),
             f"2× Ø{p['kevlar_hole_d_mm']:.0f} THRU, {p['kevlar_hole_spacing_mm']:.0f} APART (KEVLAR)", ha="right")
    # cap end view
    ev = D.view(fig, 210, 168, 95, 108, 2.0, 0, 0)
    ev.add_patch(Circle((0, 0), rsh, fill=False, lw=D.LW_VIS))
    ev.add_patch(Circle((0, 0), rc - p["thread_clearance_mm"], fill=False, lw=D.LW_THIN, ls=(0, (4, 2))))
    s_ = p["kevlar_hole_spacing_mm"] / 2
    for x in (-s_, s_):
        ev.add_patch(Circle((x, 0), p["kevlar_hole_d_mm"] / 2, fill=False, lw=D.LW_VIS))
        D.centerline(ev, (x, -4), (x, 4))
    D.centerline(ev, (-rsh - 3, 0), (rsh + 3, 0)); D.centerline(ev, (0, -rsh - 3), (0, rsh + 3))
    D.dim(ev, (-s_, -6), (s_, -6), -8, f"{2 * s_:.0f}")
    D.view_label(ev, (0, -rsh - 6), "CAP — VIEW FROM AFT (2:1)")
    # plug
    ax3 = D.view(fig, 310, 150, 100, 128, 3.0, 4.5, 0)
    for ext, holes in D.section_y0(mp):
        D.hatch_poly(ax3, ext, holes, lw=0.9)
    D.centerline(ax3, (-3, 0), (12, 0))
    th = p["plug_head_thickness_mm"]
    tb = p["ballast_bulkhead_thickness_mm"] - 0.5
    rp = p["plug_head_d_mm"] / 2
    D.dim(ax3, (0, -rp), (th, -rp), -6, f"{th:.0f}")
    D.dim(ax3, (0, -rp), (th + tb, -rp), -14, f"{th + tb:.1f}")
    D.dim(ax3, (-1, -rp), (-1, rp), -6, f"Ø{2 * rp:.0f}")
    D.dim(ax3, (th + tb + 0.5, -tp["male_root"] / 2), (th + tb + 0.5, tp["male_root"] / 2), 8, f"Ø{tp['male_root']:.2f}")
    D.leader(ax3, (0.4, p["plug_slot_width_mm"] / 2), (-3, rp + 5), f"SLOT {p['plug_slot_width_mm']:.0f} × {p['plug_slot_depth_mm']} DEEP", ha="right")
    D.leader(ax3, (th + tb * 0.5, tp["male_crest"] / 2), (th + 1, rp + 9), f"EXT. THREAD P2.5, CREST Ø{tp['male_crest']:.2f}")
    D.view_label(ax3, (4.5, -rp - 12), "PLUG — SECTION (3:1)")
    paper.text(20, 100, "THREAD DATA (all threads: pitch 2.5, 45° flanks, right-hand, 0.2 clearance)\n\n"
               f"                     FEMALE (nose cone)            MALE (part)\n"
               f"cap thread     minor Ø{tc['minor']:.2f}  major Ø{tc['major']:.2f}     root Ø{tc['male_root']:.2f}  crest Ø{tc['male_crest']:.2f}\n"
               f"plug thread    minor Ø{tp['minor']:.2f}  major Ø{tp['major']:.2f}     root Ø{tp['male_root']:.2f}  crest Ø{tp['male_crest']:.2f}\n\n"
               "Tooth profiles as the tail-cone thread (fin can drawing sheet 4, Detail D).\n"
               "Print the cap flange down and the plug head down; no supports.\n"
               "Cap: 100 % infill recommended (the Kevlar web carries the recovery snatch).",
               fontsize=7, va="top", family="DejaVu Sans Mono", linespacing=1.5)
    pdf.savefig(fig); plt.close(fig)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--rev", type=int, default=1)
    a = ap.parse_args()
    p = N.params()
    out = ROOT / "out" / "nose_cone" / f"rev{a.rev}" / f"nose_cone_rev{a.rev}_drawings.pdf"
    with PdfPages(out) as pdf:
        for fn in (s1, s2, s3):
            fn(pdf, p, a.rev)
    print(out)


if __name__ == "__main__":
    main()
