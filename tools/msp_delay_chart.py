"""Deploy speed vs drilled delay across the drag band (out/msp/flight.json) -> figures/msp/delay_choice.png"""
import json
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
ROOT = Path(__file__).resolve().parent.parent
f = json.load(open(ROOT / "out/msp/flight.json"))
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 9})
fig, ax = plt.subplots(figsize=(7, 3.6))
sty = {0.85: ":", 1.0: "-", 1.15: "--", 1.4: "-."}
lab = {0.85: "CFD drag −15 %", 1.0: "CFD drag (nominal)", 1.15: "CFD drag +15 %", 1.4: "drag ×1.40 (matches OpenRocket apogee)"}
for b in f["drag_band"]:
    d = sorted(int(k) for k in b["v_deploy"])
    ax.plot(d, [b["v_deploy"][str(k)] for k in d], "k", ls=sty[b["drag_factor"]], marker="o", ms=3,
            lw=1.6 if b["drag_factor"] == 1.0 else 1, label=f'{lab[b["drag_factor"]]} — apogee {b["apogee_m"]:.0f} m')
worst = {k: max(b["v_deploy"][str(k)] for b in f["drag_band"]) for k in (11, 12, 13, 14)}
ax.plot(list(worst), list(worst.values()), color="0.6", lw=5, alpha=.35, label="worst case over the band")
ax.set_xticks([11, 12, 13, 14]); ax.set_xlabel("drilled ejection delay (s after burnout)")
ax.set_ylabel("speed at ejection (m/s)"); ax.grid(alpha=.3); ax.legend(fontsize=7.2, loc="upper center")
ax.set_ylim(0, 40); ax.set_title("Speed at ejection vs delay, across the drag uncertainty band", fontsize=10)
fig.tight_layout(); fig.savefig(ROOT / "projects/l1-cheap/report/figures/msp/delay_choice.png", dpi=180)
print(worst)
