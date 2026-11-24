"""Nose ballast required vs the measured ready-to-fly CG (without added ballast), for the 1.7 cal minimum and the
1.8 cal target on both CFD centre-of-pressure bases. Ballast station 74.6 mm from the tip; liftoff mass 610 g ESTIMATE.

  .venv/bin/python tools/ballast_chart.py
"""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parent.parent
D, M, XB = 41.275, 610.0, 74.6
cg = np.linspace(735, 790, 200)
fig, ax = plt.subplots(figsize=(7, 4))
for cp, lab, lw in [(826.3, "CP 826.3 mm (refined CFD, assembly, L1C-CFD-002)", 1.6)]:
    for sm, ls in [(1.7, "--"), (1.8, "-")]:
        tgt = cp - sm * D
        mb = np.clip(M * (cg - tgt) / (tgt - XB), 0, None)
        ax.plot(cg, mb, "k", ls=ls, lw=lw, label=f"{sm} cal · {lab}")
ax.axvline(763.3, color="0.5", lw=0.8); ax.text(763.8, 24, "estimated CG\n763.3 mm", fontsize=7.5, color="0.3")
ax.set_xlabel("measured ready-to-fly CG without added ballast (mm from nose tip)")
ax.set_ylabel("nose ballast required (g)"); ax.set_ylim(0, 30); ax.grid(alpha=.3); ax.legend(fontsize=7.5, loc="upper left")
ax.set_title("Nose ballast required vs as-built CG (ballast at 74.6 mm, 610 g basis)", fontsize=10)
fig.tight_layout()
out = ROOT / "projects/l1-cheap/report/figures/ballast_vs_cg.png"
fig.savefig(out, dpi=180); print(out)
