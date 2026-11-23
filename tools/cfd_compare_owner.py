"""Owner STEP model vs rev 9: CFD comparison chart (CP, CN_alpha, drag, margin estimate).

  .venv/bin/python tools/cfd_compare_owner.py
Margin uses the rev 9 flight-sim CG (761.0 mm, OR weights + 65 g nose), shifted 2 mm forward for the owner
model's motor sitting 9 mm further forward (ESTIMATE until the owner's slicer masses are in).
"""
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parent.parent
D = 41.275
r9 = json.load(open(ROOT / "out/cfd/of_r9a4/result.json"))["final"]
ow = json.load(open(ROOT / "out/cfd/of_own_a4/result.json"))["final"]
CG = {"rev 9 reference": 763.3, "SolidWorks fin can": 763.3}
rows = [("rev 9 reference", r9, "#b0b0b0"), ("SolidWorks fin can", ow, "#303030")]
fig, ax = plt.subplots(1, 4, figsize=(15, 4.6))
for a, key, ttl, fmt in [(ax[0], "CP_from_tip_mm", "CP from nose tip (mm)\nfurther aft = more stable", "{:.0f}"),
                         (ax[1], "CN_alpha_per_rad", "Normal-force slope CNα (/rad)\nfin 'grip'", "{:.2f}"),
                         (ax[2], "CA_total_est", "Axial drag coeff. CA (est.)\nlower = higher apogee", "{:.3f}")]:
    v = [r[key] for _, r, _ in rows]
    b = a.bar([n for n, _, _ in rows], v, color=[c for *_, c in rows])
    for bi, vi in zip(b, v):
        a.text(bi.get_x() + bi.get_width() / 2, vi, fmt.format(vi), ha="center", va="bottom", fontsize=11)
    a.set_title(ttl, fontsize=10); a.set_ylim(min(v) * 0.9 if key == "CP_from_tip_mm" else 0, max(v) * 1.08)
m = [(r["CP_from_tip_mm"] - CG[n]) / D for n, r, _ in rows]
b = ax[3].bar([n for n, _, _ in rows], m, color=[c for *_, c in rows])
for bi, vi in zip(b, m):
    ax[3].text(bi.get_x() + bi.get_width() / 2, vi, f"{vi:.2f} cal", ha="center", va="bottom", fontsize=11)
ax[3].axhline(1.8, ls="--", color="k", lw=1); ax[3].text(1.45, 1.82, "target 1.8", ha="right", fontsize=9)
ax[3].axhline(1.0, ls=":", color="k", lw=1); ax[3].text(1.45, 1.02, "minimum 1.0", ha="right", fontsize=9)
ax[3].set_ylim(0, 2.2); ax[3].set_title("Static margin, 65 g nose (cal)\nCG 763.3 mm corrected (ESTIMATE)", fontsize=10)
for a in ax: a.tick_params(axis="x", labelsize=9); a.grid(axis="y", alpha=0.3)
fig.suptitle("CFD at 100 m/s, α = 4°: SolidWorks fin can (46.1 mm span) vs rev 9 reference (43.2 mm span)", fontsize=12)
fig.tight_layout()
out = ROOT / "projects/l1-cheap/report/figures/cfd/owner/cfd_owner_vs_rev9.png"
fig.savefig(out, dpi=150); print(out, [round(x, 2) for x in m])
