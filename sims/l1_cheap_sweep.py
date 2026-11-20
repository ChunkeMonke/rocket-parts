#!/usr/bin/env python
"""Sensitivity sweeps for l1-cheap, on top of sims/l1_cheap.py (same design.yaml inputs).

Each case is a set of design.yaml overrides. Ballast can be 'solve', which finds the
nose ballast that puts the LIFTOFF static margin on owner.stability_target_cal.
Runs with --allow-tbd semantics (payload slot defaults to the case's values).

  .venv/bin/python sims/l1_cheap_sweep.py [mass|payload|cd|nose|target|all]
"""
from __future__ import annotations

import copy
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import l1_cheap as S  # noqa: E402

BASE = S.load_design(S.DESIGN, [])
RAIL = max(S._get(BASE, "stability.assumptions.rail_lengths_m"))
TARGET = S._get(BASE, "owner.stability_target_cal")


def design_with(over):
    d = copy.deepcopy(BASE)
    for k, v in over.items():
        S._set(d, k, v)
    return d


def solve_ballast(over, target=TARGET):
    lo, hi = 0.0, 500.0
    over = dict(over)
    over["stability.ballast_g"] = 0.0
    if S.build(design_with(over), True)["sm_liftoff"] >= target:
        return 0.0
    for _ in range(40):
        mid = (lo + hi) / 2
        over["stability.ballast_g"] = mid
        if S.build(design_with(over), True)["sm_liftoff"] < target:
            lo = mid
        else:
            hi = mid
    return hi


def case(label, over, rail=RAIL):
    over = dict(over)
    if over.get("stability.ballast_g") == "solve":
        over["stability.ballast_g"] = round(solve_ballast(over), 1)
    d = design_with(over)
    b = S.build(d, True)
    row = dict(label=label, ballast=S._get(d, "stability.ballast_g"), L=b["L"], m=b["m_liftoff"],
               sml=b["sm_liftoff"], smb=b["sm_burnout"])
    if b["sm_liftoff"] < 0.5:
        row.update(note="unstable or marginal: flight not simulated")
        return row
    f = S.simulate(d, b, rail)
    dep = {r["delay"]: r["speed"] for r in f["deploy"]}
    row.update(vmax=f["vmax"], mach=f["mach_max"], apogee=f["apogee_m"], t_ap=f["t_apogee"],
               coast=f["coast_to_apogee"], rail=f["rail_exit"], q=f["max_q_pa"] / 1000, dep=dep)
    return row


def show(rows, delays=(14, 13, 12, 11, 10)):
    print(f"{'case':44s} {'ball g':>6s} {'L mm':>5s} {'m g':>5s} {'SM lo/bo':>10s} {'Vmax':>6s} {'Mach':>5s}"
          f" {'apo m':>6s} {'coast s':>7s} {'rail':>5s} " + " ".join(f"v@{x}s" for x in delays))
    for r in rows:
        head = (f"{r['label']:44s} {r['ballast']:6.1f} {r['L']:5.0f} {r['m']:5.0f} "
                f"{r['sml']:4.2f}/{r['smb']:4.2f}")
        if "vmax" not in r:
            print(head + "  " + r["note"])
            continue
        print(head + f" {r['vmax']:6.1f} {r['mach']:5.3f} {r['apogee']:6.0f} {r['coast']:7.2f} {r['rail']:5.1f} "
              + " ".join(f"{r['dep'].get(x, float('nan')):5.1f}" for x in delays))


NOPAY = {"payload.mass_g": 0, "payload.bay_length_mm": 0}
STOCK = S._get(BASE, "stability.body_tube_length_mm")


def mass_cases():
    rows = [case("s40, ballast solved (baseline)", {**NOPAY, "stability.ballast_g": "solve"})]
    b0 = rows[0]["ballast"]
    for extra in (50, 100, 150):
        rows.append(case(f"s40, ballast solved +{extra} g", {**NOPAY, "stability.ballast_g": b0 + extra}))
    for s in (45, 50):
        rows.append(case(f"s{s}, ballast solved", {**NOPAY, "stability.fin_span_request_mm": s,
                                                   "stability.ballast_g": "solve"}))
    for cut in (100, 200):
        rows.append(case(f"s40, tube cut -{cut} mm, ballast solved",
                         {**NOPAY, "stability.body_tube_length_mm": STOCK - cut, "stability.ballast_g": "solve"}))
        rows.append(case(f"s50, tube cut -{cut} mm, ballast solved",
                         {**NOPAY, "stability.body_tube_length_mm": STOCK - cut,
                          "stability.fin_span_request_mm": 50, "stability.ballast_g": "solve"}))
    return rows


def payload_cases():
    rows = []
    for bay in (0, 180):
        for m in (0, 80, 120):
            # the bay is cut from the same 863 mm stock tube, so the main tube shortens by the bay length
            over = {"payload.mass_g": m, "payload.bay_length_mm": bay,
                    "stability.body_tube_length_mm": STOCK - bay}
            if bay == 0 and m > 0:
                over["payload.cg_from_nose_mm"] = S._get(BASE, "nosecone.length_mm") + \
                    S._get(BASE, "nosecone.shoulder_length_mm")   # just aft of the nose shoulder
            rows.append(case(f"payload {m} g, bay {bay} mm, ballast 0", {**over, "stability.ballast_g": 0}))
            rows.append(case(f"payload {m} g, bay {bay} mm, ballast solved", {**over, "stability.ballast_g": "solve"}))
    return rows


def nose_cases(masses=(40, 45, 52.7, 60, 70)):
    """Nose cone mass sensitivity; CG kept at nosecone.cg_from_tip_mm (same shape)."""
    return [case(f"nose {m} g, ballast solved", {**NOPAY, "nosecone.mass_g": m, "stability.ballast_g": "solve"})
            for m in masses]


def target_cases(targets=(1.0, 1.3, 1.5, 1.6, 1.8, 2.0), wind=4.5):
    """Liftoff-margin target -> ballast, flight, margins in flight; calm and with a sample wind."""
    print(f"{'target':>6s} {'ball':>6s} {'m g':>5s} {'SM rail':>7s} {'SM bo':>6s} {'SM max':>6s} {'SM apo':>6s} "
          f"{'Vmax':>6s} {'Mach':>5s} {'apo':>5s} {'v@12':>5s} | wind {wind}: {'apo':>5s} {'drift':>5s} {'v@12':>5s}")
    for tg in targets:
        over = {**NOPAY}
        over["stability.ballast_g"] = round(solve_ballast(over, tg), 1)
        d = design_with(over)
        b = S.build(d, True)
        f = S.simulate(d, b, RAIL)
        h = S.margin_history(d, b, f)
        dep = {r["delay"]: r["speed"] for r in f["deploy"]}
        dw = design_with({**over, "stability.assumptions.wind_m_s": wind})
        fw = S.simulate(dw, b, RAIL)
        depw = {r["delay"]: r["speed"] for r in fw["deploy"]}
        print(f"{tg:6.2f} {over['stability.ballast_g']:6.1f} {b['m_liftoff']:5.0f} {f['rail_exit_margin']:7.2f} "
              f"{b['sm_burnout']:6.2f} {h['sm'].max():6.2f} {h['sm'][-1]:6.2f} {f['vmax']:6.1f} {f['mach_max']:5.3f} "
              f"{f['apogee_m']:5.0f} {dep[12]:5.1f} | {fw['apogee_m']:5.0f} {fw['apogee_drift_m']:5.0f} {depw[12]:5.1f}")
    return []


def cd_cases():
    rows = []
    for sc in (0.85, 1.0, 1.15, 1.3):
        rows.append(case(f"s40 baseline, Cd x {sc}", {**NOPAY, "stability.ballast_g": "solve",
                                                       "stability.assumptions.cd_scale": sc}))
    return rows


if __name__ == "__main__":
    which = sys.argv[1] if len(sys.argv) > 1 else "all"
    for name, fn in (("mass", mass_cases), ("payload", payload_cases), ("cd", cd_cases),
                     ("nose", nose_cases), ("target", target_cases)):
        if which in (name, "all"):
            print(f"\n== {name} (rail {RAIL} m) ==")
            show(fn())
