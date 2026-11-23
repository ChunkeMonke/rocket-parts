"""Where the normal force comes from, region by region, for two CFD cases (default r9a4 vs own_a4).

  .venv/bin/python tools/cfd_lift_breakdown.py [caseA caseB]
Regions (CFD frame, mm): nose x<165; tube/sleeve 165..950; fin flanks = fin side faces (|n_theta|>0.7, r>26);
root fillets / LE-TE caps / skirt = remaining fin-region faces (r>23.9); body between fins x 950..1033; aft body x>1033.
"""
import json, math, sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
import cfd_post as P  # noqa: E402

A_REF = math.pi * 0.041275 ** 2 / 4
NAMES = ["nose", "tube + sleeve", "fin panels\n(side faces)", "fin roots\n(fillets, edges)", "body between\nfins", "aft body /\ntail cone"]


def split(name):
    case = ROOT / "out" / "cfd" / f"of_{name}"; c = json.load(open(case / "case.json"))
    pts, polys, d = P.read(case / "VTKL" / "rocket" / f"rocket_{c['t_last']}.vtk"); Av, C = P.face_geom(pts, polys)
    K = 1 / (0.5 * P.RHO * c["speed"] ** 2 * A_REF) / math.radians(c["alpha_deg"])
    dF = 2 * P.RHO * d["p"] * Av[:, 2] * K
    x = C[:, 0] * 1000; r = np.hypot(C[:, 1], C[:, 2]) * 1000; th = np.arctan2(C[:, 1], C[:, 2])
    n = Av / np.linalg.norm(Av, axis=1)[:, None]; nt = n[:, 1] * np.cos(th) - n[:, 2] * np.sin(th)
    fr = (x > 950) & (r > 23.9); fl = fr & (np.abs(nt) > 0.7) & (r > 26)
    m = [x < 165, (x >= 165) & (x < 950) & ~fr, fl, fr & ~fl, ~fr & (x >= 950) & (x < 1033), ~fr & (x >= 1033)]
    return np.array([dF[k].sum() for k in m])


def main():
    a, b = (sys.argv[1:3] if len(sys.argv) > 2 else ("r9a4", "own_a4"))
    A, B = split(a), split(b)
    fig, ax = plt.subplots(1, 2, figsize=(15, 5), gridspec_kw={"width_ratios": [1.4, 1]})
    i = np.arange(len(NAMES)); w = 0.38
    ax[0].bar(i - w / 2, A, w, color="#7a8b99", label=f"rev 9 (total {A.sum():.2f})")
    ax[0].bar(i + w / 2, B, w, color="#d1495b", label=f"your design (total {B.sum():.2f})")
    ax[0].set_xticks(i, NAMES, fontsize=9); ax[0].set_ylabel("share of CNα (/rad)"); ax[0].legend()
    ax[0].set_title("Where the side force comes from"); ax[0].grid(axis="y", alpha=.3)
    dlt = B - A
    ax[1].barh(i, dlt, color=["#d1495b" if v < 0 else "#3a7d44" for v in dlt])
    for k, v in enumerate(dlt):
        ax[1].text(v + (0.01 if v >= 0 else -0.01), k, f"{v:+.2f}", va="center", ha="left" if v >= 0 else "right")
    ax[1].set_yticks(i, [s.replace("\n", " ") for s in NAMES], fontsize=9); ax[1].invert_yaxis()
    ax[1].axvline(0, color="k", lw=.8); ax[1].set_xlim(-0.75, 0.3); ax[1].grid(axis="x", alpha=.3)
    ax[1].set_title(f"Your design minus rev 9 (total {dlt.sum():+.2f})")
    fig.tight_layout()
    out = ROOT / "projects/l1-cheap/report/figures/cfd/owner/cfd_lift_breakdown.png"
    fig.savefig(out, dpi=140); print(out, A.round(2), B.round(2))


if __name__ == "__main__":
    main()
