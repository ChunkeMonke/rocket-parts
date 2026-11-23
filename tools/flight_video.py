"""Animated flight video of the rocket (simulation), MP4 via ffmpeg.

  .venv/bin/python tools/flight_video.py FLIGHT_JSON [--out out/video/flight.mp4]
FLIGHT_JSON: time series from the RocketPy sim (sims/l1_cheap.py), keys t, x, y, z, speed, mach, ax, theta, t_bo, ...
Rocket silhouette = owner OML (out/cfd/rocket_oml_owner.stl). Ascent in real time, descent fast-forwarded.
After deployment the descent is analytic: parachute terminal speed (OR 12.3 mph = 5.5 m/s), drifting with the wind.
"""
import argparse
import json
import math
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.animation as anim
import matplotlib.pyplot as plt
import numpy as np
import trimesh
from matplotlib.patches import Polygon, Rectangle

ROOT = Path(__file__).resolve().parent.parent
FPS = 30
V_CHUTE = 5.5
DELAY = 12.0
FF = 20.0                 # descent fast-forward factor


def silhouette():
    m = trimesh.load(ROOT / "out/cfd/rocket_oml_owner.stl")
    tip = m.bounds[1][2]
    s = m.section([0, 1, 0], [0, 0, 0])
    e = max(s.discrete, key=len)
    xs, rs = (tip - e[:, 2]) / 1000, e[:, 0] / 1000       # x aft from tip, r (fin 0 up, fins below by mirror)
    return np.column_stack([xs, rs])


def build_track(F):
    t = np.array(F["t"]); z = np.array(F["z"]); x = np.array(F["x"]); y = np.array(F["y"])
    t_dep = F["t_bo"] + DELAY
    k = np.searchsorted(t, t_dep)
    t, x, y, z = t[:k], x[:k], y[:k], z[:k]
    sp, mach, th = np.array(F["speed"])[:k], np.array(F["mach"])[:k], np.array(F["theta"])[:k]
    h = np.hypot(x, y) * np.sign(y + 1e-9)
    # descent
    dt = 1 / 60; tt, hh, zz, vz = [t[-1]], [h[-1]], [z[-1]], (z[-1] - z[-2]) / (t[-1] - t[-2])
    vh = (h[-1] - h[-2]) / (t[-1] - t[-2]); w = float(F.get("wind") or 0)
    while zz[-1] > 0:
        vz += (-V_CHUTE - vz) * dt / 0.8; vh += (w - vh) * dt / 1.5
        tt.append(tt[-1] + dt); zz.append(zz[-1] + vz * dt); hh.append(hh[-1] + vh * dt)
    td, hd, zd = np.array(tt[1:]), np.array(hh[1:]), np.maximum(np.array(zz[1:]), 0)
    vd = np.full_like(td, V_CHUTE)
    T = np.concatenate([t, td]); H = np.concatenate([h, hd]); Z = np.concatenate([z, zd])
    SP = np.concatenate([sp, vd]); M = np.concatenate([mach, vd / 340])
    TH = np.concatenate([th, np.full_like(td, 90.0)])
    return T, H, Z, SP, M, TH, t_dep


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("flight"); ap.add_argument("--out", default="out/video/flight.mp4")
    ap.add_argument("--title", default="Pepto B. #2  ·  H100W-14A (drilled 12 s)")
    a = ap.parse_args()
    F = json.load(open(a.flight))
    T, H, Z, SP, M, TH, t_dep = build_track(F)
    t_bo, t_ap = F["t_bo"], F["t_ap"]
    t_land = T[-1]
    # video time -> flight time: real time until deploy + 3 s, then fast-forward
    t_switch = t_dep + 3
    vid_len = t_switch + (t_land - t_switch) / FF + 2.5
    nfr = int(vid_len * FPS)
    tv = np.arange(nfr) / FPS
    tf = np.where(tv < t_switch, tv, t_switch + (tv - t_switch) * FF)
    tf = np.minimum(tf, t_land)
    sil = silhouette()
    L = sil[:, 0].max()

    fig = plt.figure(figsize=(19.2, 10.8), dpi=100, facecolor="#0b1320")
    gs = fig.add_gridspec(3, 2, width_ratios=[1.55, 1], left=.03, right=.97, top=.92, bottom=.06, hspace=.35, wspace=.12)
    cam = fig.add_subplot(gs[:, 0]); tr = fig.add_subplot(gs[0, 1]); pa = fig.add_subplot(gs[1, 1]); pv = fig.add_subplot(gs[2, 1])
    fig.text(.03, .955, a.title, color="w", fontsize=20, weight="bold")
    fig.text(.97, .955, "SIMULATION (RocketPy, OR-matched masses)", color="#9fb3c8", fontsize=12, ha="right")
    fig.text(.03, .02, f"Vertical launch, no wind on ascent; descent drifts in a {float(F.get('wind') or 0):.1f} m/s wind. Chute at burnout + {DELAY:.0f} s. Rocket icon enlarged for visibility.", color="#9fb3c8", fontsize=11)
    for axx in (tr, pa, pv):
        axx.set_facecolor("#13203a"); axx.tick_params(colors="#c8d3df"); [s.set_color("#3a4c6a") for s in axx.spines.values()]
        axx.grid(alpha=.2)
    tr.plot(H, Z, color="#5fa8ff", lw=1, alpha=.5); tr.set_title("Trajectory", color="w", loc="left")
    tr.set_xlabel("downrange (m)", color="#c8d3df"); tr.set_ylabel("altitude (m)", color="#c8d3df")
    tr.set_aspect("auto")
    pa.plot(T, Z, color="#5fa8ff", lw=1.2); pa.set_title("Altitude (m)", color="w", loc="left"); pa.set_xlim(0, t_land)
    pv.plot(T, SP, color="#ffb347", lw=1.2); pv.set_title("Speed (m/s)", color="w", loc="left"); pv.set_xlim(0, t_land)
    pv.set_xlabel("flight time (s)", color="#c8d3df")
    trd, = tr.plot([], [], "o", color="#ff5a5f", ms=8)
    cur_a = pa.axvline(0, color="w", lw=1); cur_v = pv.axvline(0, color="w", lw=1)
    for axx in (pa, pv):
        axx.axvspan(0, t_bo, color="#ff7b39", alpha=.12); axx.axvline(t_ap, color="#9fe870", lw=.8, ls="--")

    sky = cam.imshow(np.linspace(0, 1, 256)[:, None], aspect="auto", cmap="Blues_r", extent=(0, 1, 0, 1),
                     transform=cam.transAxes, zorder=0, vmin=-.6, vmax=1.4)
    cam.set_xticks([]); cam.set_yticks([])
    for s in cam.spines.values(): s.set_color("#3a4c6a")
    ground = cam.add_patch(Rectangle((-1e4, -1e4), 2e4, 1e4, color="#2f5d34", zorder=1))
    tower, = cam.plot([0, 0], [0, 1.5], color="#bbbbbb", lw=3, zorder=2)          # 1.5 m rail (drawn)
    trail, = cam.plot([], [], color="#d9d9d9", lw=2.5, alpha=.55, zorder=2)
    rocket = Polygon(np.zeros((3, 2)), closed=True, fc="#f2f2f2", ec="#222", lw=1, zorder=5); cam.add_patch(rocket)
    flame = Polygon(np.zeros((3, 2)), closed=True, fc="#ffb000", ec="#ff5a00", lw=1, zorder=4); cam.add_patch(flame)
    chute = Polygon(np.zeros((3, 2)), closed=True, fc="#ff4d6d", ec="#7a0019", lw=1.5, zorder=6, visible=False)
    cam.add_patch(chute)
    lines, = cam.plot([], [], color="#eee", lw=1, zorder=5)
    hgrid = [cam.axhline(k, color="w", lw=.6, alpha=.25, zorder=1) for k in range(0, 2001, 100)]
    hlab = [cam.text(0, k, f"{k} m", color="w", alpha=.6, fontsize=9, zorder=1) for k in range(0, 2001, 100)]
    hud = cam.text(.02, .97, "", transform=cam.transAxes, color="w", fontsize=17, va="top", family="DejaVu Sans Mono",
                   bbox=dict(fc="#0b1320", alpha=.6, ec="none"), zorder=10)
    phase = cam.text(.98, .97, "", transform=cam.transAxes, color="#ffd166", fontsize=22, ha="right", va="top",
                     weight="bold", zorder=10)
    ffx = cam.text(.98, .03, "", transform=cam.transAxes, color="#9fb3c8", fontsize=14, ha="right", zorder=10)

    def frame(i):
        t = tf[i]
        k = min(np.searchsorted(T, t), len(T) - 1)
        h, z, sp, th = H[k], Z[k], SP[k], TH[k]
        # camera window: grows with speed / altitude
        W = np.interp(t, [0, 0.4, t_bo, t_ap, t_dep + 2, t_land - 8, t_land], [6, 9, 70, 90, 30, 30, 10])
        Hh = W * 9.5 / 11.0
        cx, cy = h, max(z, Hh * 0.3)
        cam.set_xlim(cx - W / 2, cx + W / 2); cam.set_ylim(cy - Hh * .45, cy + Hh * .55)
        for k2, lab in enumerate(hlab):
            lab.set_position((cx - W / 2 + W * .01, k2 * 100 + Hh * .005))
        frac = np.clip(z / 1500, 0, 1)
        sky.set_clim(-.6 - frac, 1.4 - frac * .6)
        # rocket icon: true shape, scaled to be visible (display length = max(true, 12 % of window))
        sc = max(1.0, 0.16 * Hh / L)
        ang = math.radians(th if t < t_dep else 90)
        u = np.array([math.cos(ang), math.sin(ang)]); n = np.array([-u[1], u[0]])
        tip = np.array([h, z]) + u * L * sc * (0.98 if t > 0.05 else 1.0)
        if t < 0.02: tip = np.array([h, L * sc])
        if t < t_dep:
            pts = np.vstack([sil, sil[::-1] * [1, -1]])
            P = tip - np.outer(pts[:, 0] * sc, u) + np.outer(pts[:, 1] * sc, n)
            rocket.set_xy(P); rocket.set_visible(True); chute.set_visible(False); lines.set_data([], [])
        else:
            # under chute: nose + body hang below the canopy
            base = np.array([h, z]); rocket.set_visible(True)
            pts = np.vstack([sil, sil[::-1] * [1, -1]])
            uu = np.array([0, 1.0]); nn = np.array([-1.0, 0])
            P = base + np.array([0, -L * sc * .2]) - np.outer(pts[:, 0] * sc * .9, uu) * -1 + np.outer(pts[:, 1] * sc, nn)
            P = base + np.outer(L * sc - pts[:, 0] * sc, uu) * -1 + np.outer(pts[:, 1] * sc, nn) + np.array([0, -L * sc * .1])
            rocket.set_xy(P)
            open_f = np.clip((t - t_dep) / 0.8, 0.05, 1)
            R = 0.36 * sc * open_f; top = base + np.array([0, L * sc * 0.9])
            ang2 = np.linspace(0, math.pi, 25)
            canopy = np.column_stack([top[0] + R * np.cos(ang2), top[1] + R * 0.55 * np.sin(ang2)])
            chute.set_xy(canopy); chute.set_visible(True)
            lx = [top[0] - R, base[0], top[0] + R, base[0], top[0]]
            ly = [top[1], base[1], top[1], base[1], top[1]]
            lines.set_data(lx, ly)
        burn = t < t_bo and t > 0
        if burn:
            fl_len = L * sc * (0.35 + 0.08 * math.sin(i * 1.7))
            aft = tip - u * L * sc
            flame.set_xy([aft + n * L * sc * .02, aft - n * L * sc * .02, aft - u * fl_len]); flame.set_visible(True)
        else:
            flame.set_visible(False)
        m = (T <= t) & (T <= t_dep + 0.5)
        trail.set_data(H[m], Z[m])
        trd.set_data([h], [z]); cur_a.set_xdata([t, t]); cur_v.set_xdata([t, t])
        hud.set_text(f"T+ {t:6.2f} s\nALT {z:7.0f} m  {z * 3.281:6.0f} ft\nSPD {sp:7.1f} m/s {sp * 2.237:5.0f} mph\n"
                     f"MACH {sp / 340.3:5.2f}")
        ph = ("ON THE PAD" if t <= 0 else "BOOST" if t < t_bo else "COAST" if t < t_ap - 0.3 else
              "APOGEE" if t < t_dep else "EJECTION · CHUTE OUT" if t < t_dep + 2 else
              "DESCENT ON 28 in CHUTE" if z > 0.5 else "TOUCHDOWN")
        phase.set_text(ph)
        ffx.set_text(f"fast-forward ×{FF:.0f}" if tv[i] >= t_switch and z > 0.5 else "real time" if z > 0.5 else "")
        return []

    out = ROOT / a.out; out.parent.mkdir(parents=True, exist_ok=True)
    w = anim.FFMpegWriter(fps=FPS, bitrate=6000, codec="libx264", extra_args=["-pix_fmt", "yuv420p"])
    with w.saving(fig, str(out), dpi=100):
        for i in range(nfr):
            frame(i); w.grab_frame()
    print(out, f"{vid_len:.1f} s, {nfr} frames; apogee {Z.max():.0f} m at {t_ap:.1f} s, deploy {t_dep:.1f} s, land {t_land:.0f} s")


if __name__ == "__main__":
    main()
