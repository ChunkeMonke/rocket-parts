#!/usr/bin/env python
"""l1-cheap flight + stability sim (RocketPy 1.13.0).

Every design number is read from projects/l1-cheap/design.yaml or the shop
constants (skills/SKILL.md via parts/shop.py). Nothing design-specific is
hard-coded here: the code only holds the *structure* of the rocket (which
component sits where) and textbook method constants (Barrowman nose CP factor).

Value resolution, per component:
  1. the owning agent's key in design.yaml, if it is a number;
  2. else stability.assumptions.<key> (labelled estimate, basis in the yaml);
  3. else TBD -> error, or with --allow-tbd the item is EXCLUDED and the run is
     stamped PROVISIONAL with the list of what is missing.

Usage:
  .venv/bin/python sims/l1_cheap.py                       # strict
  .venv/bin/python sims/l1_cheap.py --allow-tbd           # provisional
  .venv/bin/python sims/l1_cheap.py --allow-tbd --set stability.ballast_g=50 \
        --set payload.mass_g=80 --set payload.bay_length_mm=180 --json out.json
"""
from __future__ import annotations

import argparse
import copy
import json
import math
import sys
from pathlib import Path

import numpy as np
import yaml

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from parts.shop import const  # noqa: E402

DESIGN = ROOT / "projects" / "l1-cheap" / "design.yaml"

# Barrowman nose CP as a fraction of nose length (method constant, aero.md section 2)
NOSE_K = {"tangent ogive": 0.466, "ogive": 0.466, "von karman": 0.5, "haack": 0.5,
          "parabolic": 0.5, "cone": 0.666, "conical": 0.666}
ROCKETPY_NOSE = {"tangent ogive": "tangent", "ogive": "tangent", "von karman": "von karman",
                 "haack": "lvhaack", "parabolic": "parabolic", "cone": "conical", "conical": "conical"}


class TBDValue(Exception):
    pass


# ----------------------------------------------------------------------------- yaml helpers
def _get(d, dotted):
    node = d
    for k in dotted.split("."):
        if not isinstance(node, dict) or k not in node:
            return None
        node = node[k]
    return node


def _set(d, dotted, value):
    keys = dotted.split(".")
    node = d
    for k in keys[:-1]:
        node = node.setdefault(k, {})
    node[keys[-1]] = value


def _isnum(v):
    return isinstance(v, (int, float)) and not isinstance(v, bool)


class Inputs:
    """Resolves values from design.yaml with owner-section -> assumption -> TBD order."""

    def __init__(self, design, allow_tbd):
        self.d = design
        self.allow_tbd = allow_tbd
        self.missing = []      # TBD items excluded
        self.used_assumptions = []

    def req(self, dotted):
        v = _get(self.d, dotted)
        if not _isnum(v):
            raise TBDValue(f"{dotted} = {v!r} (required, no fallback)")
        return float(v)

    def pick(self, owner_key, assumption_key=None, label=None):
        """Number from owner_key, else from stability.assumptions.<assumption_key>, else TBD."""
        v = _get(self.d, owner_key) if owner_key else None
        if _isnum(v):
            return float(v)
        if assumption_key:
            a = _get(self.d, "stability.assumptions." + assumption_key)
            if _isnum(a):
                self.used_assumptions.append(assumption_key)
                return float(a)
        what = label or owner_key or assumption_key
        if self.allow_tbd:
            self.missing.append(what)
            return None
        raise TBDValue(f"{what}: TBD in design.yaml (owner key {owner_key}, assumption {assumption_key}). "
                       "Use --allow-tbd for a provisional run.")


# ----------------------------------------------------------------------------- printed-part model
def _crust_mm():
    """Perimeter crust thickness (mm) from the print profile: 1 outer + (n-1) inner lines."""
    lw = const("print_profile_petg.line_width_mm")
    n = const("print_profile_petg.wall_loops")
    return lw["outer_wall"] + (n - 1) * lw["inner_wall"]


def annulus_mass_g(od, idd, length, infill_pct):
    """Walls+infill mass (g) of a tube printed axis-vertical: each ring has an outer and a
    bore perimeter; width beyond 2 crusts is infill. Top/bottom shells ignored (open tube)."""
    rho = const("material.petg.density_g_cm3") / 1000.0     # g/mm^3
    c = _crust_mm()
    ro, ri = od / 2, idd / 2
    if ro - ri <= 2 * c:
        return math.pi * (ro**2 - ri**2) * length * rho
    solid = math.pi * ((ro**2 - (ro - c)**2) + ((ri + c)**2 - ri**2)) * length
    core = math.pi * ((ro - c)**2 - (ri + c)**2) * length
    return (solid + core * infill_pct / 100.0) * rho


def fins_geometry(N, Cr, Ct, s, xs, d):
    """Barrowman fin normal-force slope (with body interference), CP from root LE, and
    planform-area centroid from root LE. Formulas as written out in aero.md section 2."""
    r = d / 2
    lm = math.sqrt(s**2 + (xs + Ct / 2 - Cr / 2) ** 2)
    cn = 4 * N * (s / d) ** 2 / (1 + math.sqrt(1 + (2 * lm / (Cr + Ct)) ** 2))
    cnf = (1 + r / (s + r)) * cn
    dx_cp = xs * (Cr + 2 * Ct) / (3 * (Cr + Ct)) + (Cr + Ct - Cr * Ct / (Cr + Ct)) / 6
    x_area = (Cr**2 + Cr * Ct + Ct**2 + xs * (Cr + 2 * Ct)) / (3 * (Cr + Ct))
    area = (Cr + Ct) / 2 * s
    return cnf, dx_cp, x_area, area


# ----------------------------------------------------------------------------- mass budget
def build(design, allow_tbd=False):
    I = Inputs(design, allow_tbd)
    A = lambda k: _get(design, "stability.assumptions." + k)  # noqa: E731

    d = float(const("airframe.loc_38mm_paper.od_nominal_mm"))   # od_measured is TBD
    tube_id = float(const("airframe.loc_38mm_paper.id_measured_mm"))
    shape = str(_get(design, "nosecone.shape")).strip().lower()
    Ln = I.req("nosecone.length_mm")
    Lt = I.req("stability.body_tube_length_mm")
    N = int(I.req("aero.fin_count"))
    Cr = I.req("aero.fin_root_chord_mm")
    Ct = I.req("aero.fin_tip_chord_mm")
    xs = I.req("aero.fin_sweep_mm")
    t_fin = I.req("aero.fin_thickness_mm")
    s_req = _get(design, "stability.fin_span_request_mm")
    s = float(s_req) if _isnum(s_req) else I.req("aero.fin_span_mm")
    m_len = I.req("motor.length_mm")
    m_dia = I.req("motor.diameter_class_mm")
    m_loaded = I.req("motor.loaded_mass_g")
    m_prop = I.req("motor.propellant_mass_g")

    # avionics bay slot (payload agent): tube section between nose shoulder and main tube
    bay_len = I.pick("payload.bay_length_mm", "payload_bay_length_mm", "payload bay length")
    bay_len = bay_len or 0.0
    pay_m = I.pick("payload.mass_g", "payload_mass_g", "payload (Quasar-LR) mass")

    Cr_exp = Cr if A("fin_can.exposed_length_mm") == "root_chord" else float(A("fin_can.exposed_length_mm"))
    Lb = bay_len + Lt + Cr_exp          # nose base to aft end
    L = Ln + Lb
    aft_off = float(A("motor_aft_offset_mm"))
    x_motor_aft = L - aft_off
    x_motor_fwd = x_motor_aft - m_len

    items = []   # (name, mass_g, cg_from_tip_mm, basis)

    def add(name, m, x, basis):
        if m is None:
            return
        items.append((name, float(m), float(x), basis))

    add("nose cone", I.req("nosecone.mass_g"), I.req("nosecone.cg_from_tip_mm"), "nosecone (estimate)")
    add("ballast", I.req("stability.ballast_g"), I.req("stability.ballast_cg_from_nose_mm"), "stability choice")

    rho_t = I.pick(None, "tube_linear_density_g_per_mm", "tube g/mm")
    if bay_len > 0:
        add("bay tube (BT-1.52)", rho_t * bay_len, Ln + bay_len / 2, "assumption tube g/mm")
    pay_x = _get(design, "payload.cg_from_nose_mm")
    if not _isnum(pay_x):
        pay_x = (Ln + bay_len / 2) if bay_len > 0 else A("payload_cg_from_nose_mm")
    if pay_m:
        if not _isnum(pay_x):
            if not allow_tbd:
                raise TBDValue("payload mass given but no position (payload.cg_from_nose_mm / bay length)")
            I.missing.append("payload position")
        else:
            add("payload (Quasar-LR bay contents)", pay_m, pay_x, "payload")
    add("body tube (BT-1.52)", rho_t * Lt, Ln + bay_len + Lt / 2, "assumption tube g/mm")

    # fin can (ESTIMATE, walls + infill)
    fc = A("fin_can")
    bore = m_dia if fc["bore_diameter_mm"] == "motor_class" else float(fc["bore_diameter_mm"])
    sh_od = (tube_id - 2 * const("fits_in_tube.snug_slip_mm_per_side")
             if fc["shoulder_od_mm"] == "snug_slip" else float(fc["shoulder_od_mm"]))
    Ssh = (m_len - Cr_exp) if fc["shoulder_length_mm"] == "motor_minus_exposed" else float(fc["shoulder_length_mm"])
    infill = float(fc["infill_pct"])
    rho_p = const("material.petg.density_g_cm3") / 1000.0
    cnf, dx_cp, x_area, a_fin = fins_geometry(N, Cr, Ct, s, xs, d)
    m_exp = annulus_mass_g(d, bore, Cr_exp, infill)
    m_sh = annulus_mass_g(sh_od, bore, Ssh, infill)
    m_fins = N * a_fin * t_fin * rho_p     # t_fin < 2 crusts -> solid
    add("fin can body, exposed", m_exp, L - Cr_exp / 2, "ESTIMATE walls+infill")
    add("fin can shoulder", m_sh, L - Cr_exp - Ssh / 2, "ESTIMATE walls+infill")
    add("fins (printed with can)", m_fins, L - Cr + x_area, "ESTIMATE solid, aero geometry")

    # recovery
    x_pack_aft = x_motor_fwd
    pack_len = I.pick("recovery.bay_length_mm", "recovery_pack_length_mm", "recovery pack length")
    rec_total = _get(design, "recovery.recovery_mass_g")
    rec_x = _get(design, "recovery.recovery_cg_from_nose_mm")
    pack_x = _isnum(rec_x) and float(rec_x) or (x_pack_aft - pack_len / 2)
    if _isnum(rec_total):
        add("recovery (chute+cord+wadding)", rec_total, pack_x, "recovery")
    else:
        add("parachute", I.pick("recovery.chute_mass_g", "chute_mass_g", "chute mass"), pack_x, "chute")
        cord_m = (A("shock_cord_length_factor") * L + A("shock_cord_loop_allowance_mm")) / 1000.0
        add("shock cord (Kevlar)", cord_m * I.pick(None, "shock_cord_g_per_m"), pack_x, f"{cord_m:.2f} m")
        add("wadding", I.pick(None, "wadding_g"), x_pack_aft - 10, "assumption")
    add("epoxy", I.pick(None, "epoxy_g"), L - Cr_exp - Ssh / 2, "ESTIMATE")
    add("rail buttons", I.pick(None, "rail_buttons_g"), L - A("rail_button_cg_from_aft_mm"), "ESTIMATE")
    add("motor retention", I.pick(None, "retention_g"), L - 2, "ESTIMATE")

    m_s = sum(i[1] for i in items)
    x_s = sum(i[1] * i[2] for i in items) / m_s
    x_motor_cg = x_motor_aft - m_len / 2           # assumption motor_dry_cg: midpoint
    m_dry = m_loaded - m_prop
    cg_lo = (m_s * x_s + m_loaded * x_motor_cg) / (m_s + m_loaded)
    cg_bo = (m_s * x_s + m_dry * x_motor_cg) / (m_s + m_dry)

    # Barrowman CP, subsonic (aero.md section 2)
    k = NOSE_K[shape]
    x_f = Ln + Lb - Cr + dx_cp
    cp = (2 * k * Ln + cnf * x_f) / (2 + cnf)

    return dict(
        inputs=I, d=d, Ln=Ln, Lt=Lt, bay_len=bay_len, Lb=Lb, L=L, shape=shape,
        fins=dict(N=N, Cr=Cr, Ct=Ct, s=s, xs=xs, t=t_fin, cnf=cnf),
        items=items, m_struct=m_s, x_struct=x_s,
        motor=dict(len=m_len, dia=m_dia, loaded=m_loaded, prop=m_prop, dry=m_dry,
                   x_aft=x_motor_aft, x_cg=x_motor_cg),
        fin_can=dict(exposed=m_exp, shoulder=m_sh, fins=m_fins, total=m_exp + m_sh + m_fins,
                     shoulder_len=Ssh, bore=bore, shoulder_od=sh_od, height=Cr_exp + Ssh),
        cg_liftoff=cg_lo, cg_burnout=cg_bo, cp=cp,
        sm_liftoff=(cp - cg_lo) / d, sm_burnout=(cp - cg_bo) / d,
        m_liftoff=m_s + m_loaded, m_burnout=m_s + m_dry,
    )


# ----------------------------------------------------------------------------- RocketPy
def simulate(design, b, rail_length_m, max_delay_s=14):
    from rocketpy import Environment, Flight, GenericMotor, Rocket

    A = lambda k: _get(design, "stability.assumptions." + k)  # noqa: E731
    site = A("launch_site")
    env = Environment(latitude=site["latitude"], longitude=site["longitude"], elevation=site["elevation_m"])
    eng = ROOT / str(_get(design, "motor.thrust_curve_source")).split()[0]
    mo = b["motor"]
    mlen = mo["len"] / 1000
    r_ch = mo["dia"] / 2000
    m_dry = mo["dry"] / 1000
    motor = GenericMotor.load_from_eng_file(
        str(eng), nozzle_radius=A("motor_nozzle_radius_mm") / 1000, chamber_radius=r_ch,
        chamber_height=mlen, chamber_position=mlen / 2, center_of_dry_mass_position=mlen / 2,
        dry_mass=m_dry, propellant_initial_mass=mo["prop"] / 1000,
        dry_inertia=(m_dry * (mlen**2 / 12 + r_ch**2 / 4),) * 2 + (m_dry * r_ch**2 / 2,),
        coordinate_system_orientation="nozzle_to_combustion_chamber")

    cd_tab = _get(design, "aero.cd_vs_mach") or A("cd_vs_mach")
    scale = A("cd_scale") if _isnum(A("cd_scale")) else 1.0
    cd = [[float(mach), float(c) * scale] for mach, c in cd_tab]

    # structure inertia about its own CG: point masses + tubes as rods (estimate)
    ms = b["m_struct"] / 1000
    xs = b["x_struct"] / 1000
    R = b["d"] / 2000
    I_lat = sum(m / 1000 * ((x / 1000 - xs) ** 2) for _, m, x, _ in b["items"])
    I_lat += sum(m / 1000 * (b["Lt"] / 1000) ** 2 / 12 for n, m, _, _ in b["items"] if n.startswith("body tube"))
    I_ax = 0.5 * ms * R**2
    L = b["L"] / 1000
    f = b["fins"]
    rkt = Rocket(radius=R, mass=ms, inertia=(I_lat, I_lat, I_ax), power_off_drag=cd, power_on_drag=cd,
                 center_of_mass_without_motor=xs, coordinate_system_orientation="nose_to_tail")
    rkt.add_motor(motor, position=mo["x_aft"] / 1000)
    rkt.add_nose(length=b["Ln"] / 1000, kind=ROCKETPY_NOSE[b["shape"]], position=0)
    rkt.add_trapezoidal_fins(n=f["N"], root_chord=f["Cr"] / 1000, tip_chord=f["Ct"] / 1000,
                             span=f["s"] / 1000, position=L - f["Cr"] / 1000, sweep_length=f["xs"] / 1000)

    t_bo = float(motor.burn_out_time)
    fl = Flight(rocket=rkt, environment=env, rail_length=rail_length_m,
                inclination=A("launch_inclination_deg"), heading=0, terminate_on_apogee=False,
                max_time=t_bo + max_delay_s + 2, verbose=False)
    elev = site["elevation_m"]
    t_ap = float(fl.apogee_time)
    out = dict(
        rail_m=rail_length_m, apogee_m=float(fl.apogee) - elev, t_apogee=t_ap, t_burnout=t_bo,
        coast_to_apogee=t_ap - t_bo, vmax=float(fl.max_speed), mach_max=float(fl.max_mach_number),
        t_vmax=float(fl.max_speed_time), max_q_pa=float(fl.max_dynamic_pressure),
        rail_exit=float(fl.out_of_rail_velocity), t_rail=float(fl.out_of_rail_time),
        rp_static_margin_liftoff=float(rkt.static_margin(0)), rp_static_margin_burnout=float(rkt.static_margin(t_bo)),
        rp_cp_M0_mm=float(rkt.cp_position(0)) * 1000, rp_cp_M09_mm=float(rkt.cp_position(0.9)) * 1000,
        rail_exit_margin=float(fl.out_of_rail_stability_margin), max_margin=float(fl.max_stability_margin),
        deploy=[],
    )
    for delay in range(max_delay_s, -1, -1):
        t = t_bo + delay
        if t > fl.t_final:
            continue
        out["deploy"].append(dict(delay=delay, t=t, alt=float(fl.z(t)) - elev, speed=float(fl.speed(t)),
                                  vz=float(fl.vz(t))))
    return out


def load_design(path, sets):
    design = yaml.safe_load(Path(path).read_text())
    for s in sets:
        k, v = s.split("=", 1)
        _set(design, k, yaml.safe_load(v))
    return design


def run(design, allow_tbd=False, rails=None):
    b = build(design, allow_tbd)
    rails = rails or _get(design, "stability.assumptions.rail_lengths_m")
    sims = [simulate(design, b, r) for r in rails]
    return b, sims


def report(b, sims, design):
    I = b["inputs"]
    tgt = _get(design, "owner.stability_target_cal")
    band = _get(design, "owner.stability_band_cal")
    lo, hi = tgt - band, tgt + band
    if I.missing:
        print("=" * 78)
        print("PROVISIONAL RUN: these TBD items were EXCLUDED:", ", ".join(I.missing))
        print("=" * 78)
    print(f"Length {b['L']:.0f} mm (nose {b['Ln']:.0f} + bay {b['bay_len']:.0f} + tube {b['Lt']:.0f} "
          f"+ fin can exposed {b['L'] - b['Ln'] - b['bay_len'] - b['Lt']:.0f}); fin span {b['fins']['s']:.0f} mm")
    print("\nMass budget (x from nose tip):")
    print(f"  {'item':34s} {'g':>7s} {'x mm':>7s}  basis")
    for n, m, x, basis in b["items"]:
        print(f"  {n:34s} {m:7.1f} {x:7.1f}  {basis}")
    mo = b["motor"]
    print(f"  {'motor loaded / burnout':34s} {mo['loaded']:7.1f} {mo['x_cg']:7.1f}  motor ({mo['dry']:.0f} g dry)")
    print(f"  structure {b['m_struct']:.1f} g @ {b['x_struct']:.1f}; liftoff {b['m_liftoff']:.1f} g; burnout {b['m_burnout']:.1f} g")
    fc = b["fin_can"]
    print(f"  fin can total {fc['total']:.1f} g (exposed {fc['exposed']:.1f} + shoulder {fc['shoulder']:.1f} "
          f"[{fc['shoulder_len']:.0f} mm] + fins {fc['fins']:.1f}); print height {fc['height']:.0f} mm")

    def verdict(sm):
        return "PASS" if lo <= sm <= hi else ("FAIL (low)" if sm < lo else "FAIL (high)")
    print(f"\nCP (Barrowman, M~0) {b['cp']:.1f} mm   CG liftoff {b['cg_liftoff']:.1f}   CG burnout {b['cg_burnout']:.1f}")
    print(f"Static margin liftoff {b['sm_liftoff']:.2f} cal  {verdict(b['sm_liftoff'])}   "
          f"burnout {b['sm_burnout']:.2f} cal  {verdict(b['sm_burnout'])}   [target {tgt} +/- {band}]")
    s0 = sims[0]
    print(f"RocketPy: CP M0 {s0['rp_cp_M0_mm']:.1f} / M0.9 {s0['rp_cp_M09_mm']:.1f} mm; static margin "
          f"{s0['rp_static_margin_liftoff']:.2f} / {s0['rp_static_margin_burnout']:.2f} cal; at rail exit "
          f"{s0['rail_exit_margin']:.2f}, max in flight {s0['max_margin']:.2f}")
    for s in sims:
        print(f"\nRail {s['rail_m']} m: rail exit {s['rail_exit']:.1f} m/s at {s['t_rail']:.3f} s")
    print(f"Apogee {s0['apogee_m']:.0f} m ({s0['apogee_m'] / 0.3048:.0f} ft) at {s0['t_apogee']:.2f} s; burnout "
          f"{s0['t_burnout']:.3f} s; coast to apogee {s0['coast_to_apogee']:.2f} s")
    print(f"Vmax {s0['vmax']:.1f} m/s at {s0['t_vmax']:.2f} s, Mach {s0['mach_max']:.3f}, max q {s0['max_q_pa'] / 1000:.1f} kPa")
    print("\nDelay  t(s)   alt AGL(m)  speed(m/s)  vz(m/s)  flag (<=20 preferred, <=27 limit)")
    for r in s0["deploy"]:
        flag = "preferred" if r["speed"] <= 20 else ("limit" if r["speed"] <= 27 else "TOO FAST")
        print(f"{r['delay']:5d}  {r['t']:5.2f}  {r['alt']:10.0f}  {r['speed']:10.1f}  {r['vz']:7.1f}  {flag}")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--design", default=str(DESIGN))
    ap.add_argument("--allow-tbd", action="store_true", help="exclude TBD items and stamp the run PROVISIONAL")
    ap.add_argument("--set", action="append", default=[], help="override dotted.key=value (yaml value)")
    ap.add_argument("--json", help="write results to this JSON file")
    a = ap.parse_args()
    design = load_design(a.design, a.set)
    b, sims = run(design, a.allow_tbd)
    report(b, sims, design)
    if a.json:
        bb = {k: v for k, v in b.items() if k != "inputs"}
        bb["missing_tbd"] = b["inputs"].missing
        bb["assumptions_used"] = sorted(set(b["inputs"].used_assumptions))
        Path(a.json).write_text(json.dumps(dict(budget=bb, flights=sims), indent=1))


if __name__ == "__main__":
    main()
