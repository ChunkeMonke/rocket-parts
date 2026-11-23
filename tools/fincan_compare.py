"""Visual comparison: rev 9 fin can vs the owner's STEP fin can, and why the owner's is less stable (CFD).

  .venv/bin/python tools/fincan_compare.py
Uses out/cfd/rocket_oml.stl (rev 9) and out/cfd/rocket_oml_owner.stl, CFD results r9a4 / own_a4.
Writes projects/l1-cheap/report/figures/cfd/owner/fincan_compare.png (+ .pdf).
"""
import json
import math
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import trimesh

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
from cfd_lift_breakdown import NAMES, split  # noqa: E402

C9, CO = "#5b6b7a", "#d1495b"
D = 41.275


def load(f):
    m = trimesh.load(ROOT / "out/cfd" / f); return m, m.bounds[1][2]   # tip z


def side(ax, m, ztip, col, lab, fill):
    s = m.section([0, 1, 0], [0, 0, 0])
    for k, e in enumerate(s.discrete):
        x, r = ztip - e[:, 2], e[:, 0]
        if fill: ax.fill(x, r, color=col, alpha=0.18, lw=0)
        ax.plot(x, r, color=col, lw=1.6, label=lab if k == 0 else None)


def xsec(ax, m, ztip, x, col, lab):
    s = m.section([0, 0, 1], [0, 0, ztip - x])
    for k, e in enumerate(s.discrete):
        ax.plot(e[:, 1], e[:, 0], color=col, lw=1.8, label=lab if k == 0 else None)


def main():
    m9, t9 = load("rocket_oml.stl"); mo, to = load("rocket_oml_owner.stl")
    r9 = json.load(open(ROOT / "out/cfd/of_r9a4/result.json"))["final"]
    ro = json.load(open(ROOT / "out/cfd/of_own_a4/result.json"))["final"]
    fig = plt.figure(figsize=(17, 11.5))
    gs = fig.add_gridspec(3, 3, height_ratios=[1.15, 1, 1], hspace=0.42, wspace=0.28)

    # A: side profile overlay
    a = fig.add_subplot(gs[0, :])
    side(a, m9, t9, C9, "rev 9 (my design)", True); side(a, mo, to, CO, "your STEP design", False)
    for cp, col, lab in [(r9["CP_from_tip_mm"], C9, "rev 9 CP"), (ro["CP_from_tip_mm"], CO, "your CP")]:
        pass
    a.set_xlim(860, 1085); a.set_ylim(-5, 75); a.set_aspect("equal"); a.grid(alpha=.25)
    a.set_xlabel("distance from nose tip (mm)  →  aft"); a.set_ylabel("radius (mm)")
    a.set_title("A. Side profile through a fin (same nose-tip reference, both 1077 mm long)", loc="left", fontsize=11)
    notes = [(905, 30, "fairing:\nrev 9 shorter step\nyours 40 mm taper", None),
             (1040, 52, "your fin TE stops\n15 mm before the\nend of the sleeve", (1032, 30)),
             (1062, 8, "rev 9: 18.5 mm full-dia collar,\nthen 30 mm boattail\nyours: cone tapers\nright after the sleeve", None)]
    for x, y, t, arr in notes:
        a.annotate(t, (arr if arr else (x, y)), xytext=(x, y), fontsize=8.5, ha="center",
                   arrowprops=dict(arrowstyle="->", lw=.8) if arr else None)
    a.legend(loc="upper left", fontsize=9)

    # B: root junction cross-section
    b = fig.add_subplot(gs[1, 0])
    xm = 1005
    xsec(b, m9, t9, xm, C9, "rev 9"); xsec(b, mo, to, xm, CO, "yours")
    b.set_xlim(-12, 12); b.set_ylim(18, 42); b.set_aspect("equal"); b.grid(alpha=.25)
    b.set_title(f"B. Where the fin meets the body\n(cut across the rocket at {xm} mm)", loc="left", fontsize=10)
    b.annotate("rev 9: 6 mm root fillets\n(fin widens into the body)", (-6.4, 24.6), xytext=(-11.5, 36), fontsize=8,
               arrowprops=dict(arrowstyle="->", lw=.8))
    b.annotate("yours: sharp corner", (5.6, 23.9), xytext=(3, 33), fontsize=8, arrowprops=dict(arrowstyle="->", lw=.8))
    b.set_xlabel("mm"); b.legend(fontsize=8, loc="upper right")

    # C: fin planform overlay (radius vs x)
    c = fig.add_subplot(gs[1, 1])
    side(c, m9, t9, C9, "rev 9: span 43.2 mm", True); side(c, mo, to, CO, "yours: span 46.1 mm", False)
    c.set_xlim(970, 1045); c.set_ylim(20, 72); c.set_aspect("equal"); c.grid(alpha=.25)
    c.set_title("C. Fin shape (side view)\nyours is bigger: +10 % fin area", loc="left", fontsize=10)
    c.set_xlabel("from nose tip (mm)"); c.legend(fontsize=8, loc="lower left")

    # D: numbers
    d = fig.add_subplot(gs[1, 2]); d.axis("off")
    cg = 752.0
    rows = [("", "rev 9", "yours"),
            ("fin span", "43.2 mm", "46.1 mm"),
            ("root fillets", "6 mm", "none"),
            ("CFD lift slope CNα", f"{r9['CN_alpha_per_rad']:.1f}", f"{ro['CN_alpha_per_rad']:.1f}"),
            ("CFD CP from tip", f"{r9['CP_from_tip_mm']:.0f} mm", f"{ro['CP_from_tip_mm']:.0f} mm"),
            ("drag CA (est.)", f"{r9['CA_total_est']:.3f}", f"{ro['CA_total_est']:.3f}"),
            (f"margin @ CG {cg:.0f} mm*", f"{(r9['CP_from_tip_mm'] - cg) / D:.2f} cal", f"{(ro['CP_from_tip_mm'] - cg) / D:.2f} cal")]
    t = d.table(cellText=rows, loc="center", cellLoc="center", colWidths=[.46, .27, .27])
    t.auto_set_font_size(False); t.set_fontsize(10); t.scale(1, 1.9)
    for (i, j), cell in t.get_celld().items():
        if i == 0: cell.set_text_props(weight="bold")
        if j == 2 and i > 0: cell.set_text_props(color=CO)
    d.set_title("D. Results (CFD, 100 m/s, 4°)", loc="left", fontsize=10)
    d.text(0, -0.02, "* same CG for both (your OR file with mass fixes, ESTIMATE),\n  tube reference 41.275 mm (1.625 in)",
           fontsize=8, transform=d.transAxes)

    # E: lift breakdown delta
    e = fig.add_subplot(gs[2, :2])
    A, B = split("r9a4"), split("own_a4"); i = np.arange(len(NAMES)); w = .38
    e.bar(i - w / 2, A, w, color=C9, label=f"rev 9 (total {A.sum():.1f})")
    e.bar(i + w / 2, B, w, color=CO, label=f"yours (total {B.sum():.1f})")
    for k in i:
        e.text(k + w / 2, B[k] + .1, f"{B[k] - A[k]:+.2f}", ha="center", fontsize=9, color=CO, weight="bold")
    e.set_xticks(i, NAMES, fontsize=9); e.set_ylabel("lift slope share (/rad)"); e.grid(axis="y", alpha=.3)
    e.legend(fontsize=9); e.set_title("E. Where each design's lift comes from (red numbers = yours minus rev 9)", loc="left", fontsize=10)

    # F: explanation
    f = fig.add_subplot(gs[2, 2]); f.axis("off")
    f.text(0, 1, "Why yours is less stable", fontsize=12, weight="bold", va="top")
    f.text(0, .88,
           "Stability = how far the CP (where lift acts) sits\n"
           "behind the CG. Fin lift pulls the CP aft.\n\n"
           "1. Fin roots (−0.53): the sharp fin-body corner\n"
           "   lifts much less than rev 9's filleted root.\n"
           "   The air next to the body is the strongest\n"
           "   flow the fin sees, so losing it costs most.\n"
           "2. Aft body (−0.25) and between fins (−0.17):\n"
           "   rev 9's full-diameter collar behind the fins\n"
           "   carries extra lift; your cone tapers sooner.\n"
           "3. Fin panels (−0.19): the extra span is at the\n"
           "   tip, where a fin lifts least.\n\n"
           "Net: 9 % less lift, CP 17 mm further forward.\n"
           "Fix: 6 mm root fillets (+ stronger roots).",
           fontsize=9.3, va="top", family="DejaVu Sans")
    fig.suptitle("Fin can comparison: rev 9 vs your SolidWorks design", fontsize=15, weight="bold", y=0.985)
    out = ROOT / "projects/l1-cheap/report/figures/cfd/owner/fincan_compare"
    fig.savefig(str(out) + ".png", dpi=140, bbox_inches="tight"); fig.savefig(str(out) + ".pdf", bbox_inches="tight")
    print(out)


if __name__ == "__main__":
    main()
