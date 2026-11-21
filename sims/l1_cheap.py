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


# RocketPy Tail needs length > 0; an abrupt diameter step is modelled as a cone this long (numerical stand-in)
STEP_LEN_M = 1e-4


def cd_table(design):
    """Cd(Mach) from design.yaml: aero.cd_vs_mach (list) if present, else the aero.cd_estimate string
    ("0.73 @ M0.1, 0.89 @ M0.5, ..."), held flat below the first and above the last Mach point, else
    stability.assumptions.cd_vs_mach. Returns (table, source)."""
    tab = _get(design, "aero.cd_vs_mach")
    if isinstance(tab, list) and tab:
        return tab, "aero.cd_vs_mach"
    est = _get(design, "aero.cd_estimate")
    if isinstance(est, str):
        import re
        pts = [(float(m), float(c)) for c, m in re.findall(r"([0-9.]+)\s*@\s*M\s*([0-9.]+)", est)]
        if pts:
            pts.sort()
            hi = max(_get(design, "stability.assumptions.cd_hold_to_mach") or 0, pts[-1][0] + 0.5)
            tab = [[0.0, pts[0][1]]] + [[m, c] for m, c in pts] + [[hi, pts[-1][1]]]
            return tab, "aero.cd_estimate (flat outside its Mach range)"
    return _get(design, "stability.assumptions.cd_vs_mach"), "stability.assumptions.cd_vs_mach"


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


def fins_geometry(N, Cr, Ct, s, xs, d_ref, r_body):
    """Barrowman fin normal-force slope (with body interference K = 1 + r_body/(s + r_body)), CP from
    root LE, and planform-area centroid from root LE. s is measured from the body the fins sit on
    (r_body); CN is normalised on the reference diameter d_ref. Formulas as in aero.md 0.3 / section 2."""
    lm = math.sqrt(s**2 + (xs + Ct / 2 - Cr / 2) ** 2)
    cn = 4 * N * (s / d_ref) ** 2 / (1 + math.sqrt(1 + (2 * lm / (Cr + Ct)) ** 2))
    cnf = (1 + r_body / (s + r_body)) * cn
    dx_cp = xs * (Cr + 2 * Ct) / (3 * (Cr + Ct)) + (Cr + Ct - Cr * Ct / (Cr + Ct)) / 6
    x_area = (Cr**2 + Cr * Ct + Ct**2 + xs * (Cr + 2 * Ct)) / (3 * (Cr + Ct))
    area = (Cr + Ct) / 2 * s
    return cnf, dx_cp, x_area, area


def transition_cn(d1, d2, length, x0, d_ref):
    """Barrowman conical shoulder/step d1 -> d2 (d2 > d1) starting at x0: CN_alpha and CP (mm).
    length 0 = an abrupt step (CP at x0). aero.md 0.3."""
    cn = 2 * ((d2 / d_ref) ** 2 - (d1 / d_ref) ** 2)
    if length <= 0:
        return cn, x0
    q = d1 / d2
    return cn, x0 + length / 3 * (1 + (1 - q) / (1 - q**2))


def _fcmd(design, key):
    """fin_can_md.<key> value, with the shop-token values resolved ('wall_band', 'snug_slip')."""
    v = _get(design, f"fin_can_md.{key}")
    v = v.get("value") if isinstance(v, dict) else v
    if v == "wall_band":
        return _crust_mm()
    if v == "snug_slip":
        return float(const("fits_in_tube.snug_slip_mm_per_side"))
    if v == "press":
        return float(const("fits_in_tube.press_mm_per_side"))
    if not _isnum(v):
        raise TBDValue(f"fin_can_md.{key} = {v!r}")
    return float(v)


def sleeve_geometry(design, d_tube):
    """Min-diameter fin can sleeve (parts/fin_can_md.py): returns dict of mm values.
    Sleeve bore = tube OD + 2 x fit; sleeve OD = bore + 2 x wall; fairing runs from the sleeve OD
    forward down to a feather edge (2 outer-wall lines) on the tube; lip under the tube end."""
    fit = _fcmd(design, "sleeve_fit")
    wall = _fcmd(design, "sleeve_wall")
    bore = d_tube + 2 * fit
    feather = 2 * const("print_profile_petg.line_width_mm")["outer_wall"]
    return dict(fit=fit, wall=wall, bore=bore, od=bore + 2 * wall, fair_fwd_od=bore + 2 * feather,
                sleeve_len=_fcmd(design, "sleeve_overlap_mm"), fair_len=_fcmd(design, "fairing_length_mm"),
                lip=_fcmd(design, "lip_thickness"))


# ----------------------------------------------------------------------------- mass budget
def build(design, allow_tbd=False):
    """Min-diameter layout (2026-11-21): nose | BT-1.52 tube (motor inside its aft end) | printed sleeve
    over the aft sleeve_len of tube, with a forward fairing and an aft lip under the tube end."""
    I = Inputs(design, allow_tbd)
    A = lambda k: _get(design, "stability.assumptions." + k)  # noqa: E731

    d = float(const("airframe.loc_38mm_paper.od_nominal_mm"))   # od_measured is TBD; reference diameter
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
    sg = sleeve_geometry(design, d)
    fin_od = _get(design, "aero.fin_body_od_mm")
    if _isnum(fin_od) and abs(fin_od - sg["od"]) > 0.01:
        print(f"WARNING: aero.fin_body_od_mm {fin_od} != sleeve OD {sg['od']:.3f} from fin_can_md")

    # avionics bay slot (payload agent): tube section between nose shoulder and main tube
    bay_len = I.pick("payload.bay_length_mm", "payload_bay_length_mm", "payload bay length")
    bay_len = bay_len or 0.0
    pay_m = I.pick("payload.mass_g", "payload_mass_g", "payload (Quasar-LR) mass")

    Lb = bay_len + Lt + sg["lip"]       # nose base to aft face (the lip is the only part aft of the tube)
    L = Ln + Lb                         # aft face of the fin can
    x_tube_aft = L - sg["lip"]
    x_fair_fwd = L - sg["sleeve_len"] - sg["fair_len"]
    x_motor_aft = L - float(A("motor_aft_offset_mm"))   # 0 = nozzle end flush with the aft face
    x_motor_fwd = x_motor_aft - m_len

    items = []   # (name, mass_g, cg_from_tip_mm, basis)

    def add(name, m, x, basis):
        if m is None:
            return
        items.append((name, float(m), float(x), basis))

    # nose: the printed SHELL (stability.nose_shell_mass_g, from nosecone.md) + ballast. nosecone.mass_g is the
    # owner's whole-nose target (shell + ballast), so it is only used if no shell mass is given.
    shell = _get(design, "stability.nose_shell_mass_g")
    if _isnum(shell):
        add("nose cone shell", shell, I.req("nosecone.cg_from_tip_mm"), "nosecone.md shell (ESTIMATE)")
    else:
        add("nose cone", I.req("nosecone.mass_g"), I.req("nosecone.cg_from_tip_mm"), "nosecone.mass_g")
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
            add("payload (bay contents)", pay_m, pay_x, "payload")
    add("body tube (BT-1.52)", rho_t * Lt, Ln + bay_len + Lt / 2, "assumption tube g/mm")

    # fin can = printed part model (parts/fin_can_md.py), fins included
    fc_m = I.pick("stability.fin_can_model_mass_g", None, "fin can model mass")
    fc_x = I.pick("stability.fin_can_model_cg_from_aft_mm", None, "fin can model CG")
    rho_p = const("material.petg.density_g_cm3") / 1000.0
    cnf, dx_cp, x_area, a_fin = fins_geometry(N, Cr, Ct, s, xs, d, sg["od"] / 2)
    if fc_m is not None and fc_x is not None:
        add("fin can md (part model, incl. fins)", fc_m, L - fc_x, "fin_can_md model (verify mass)")

    # motor stop / Kevlar anchor ring inside the tube, just forward of the motor (PROPOSED, ESTIMATE)
    stop_len = A("motor_stop_length_mm")
    stop_len = float(stop_len) if _isnum(stop_len) else 0.0
    add("fwd motor stop / anchor (ESTIMATE)", I.pick(None, "motor_stop_g"),
        x_motor_fwd - float(A("motor_stop_cg_fwd_of_motor_mm")), "ESTIMATE")

    # recovery: pack rests on the stop's forward face (most aft position it can take)
    x_pack_aft = x_motor_fwd - stop_len
    pack_len = I.pick("recovery.bay_length_mm", "recovery_pack_length_mm", "recovery pack length")
    rec_total = _get(design, "recovery.recovery_mass_g")
    rec_x = _get(design, "recovery.recovery_cg_from_nose_mm")
    pos = A("recovery_pack_position")
    if _isnum(rec_x):
        pack_x = float(rec_x)
    elif _isnum(pos):                   # a number = pack CG from the nose tip (mm), e.g. the owner's OR position
        pack_x = float(pos)
    else:                               # 'on_motor': pack rests on the stop/motor forward face (most aft)
        pack_x = x_pack_aft - pack_len / 2
    if _isnum(rec_total):
        add("recovery (chute+cord+wadding)", rec_total, pack_x, "recovery")
    else:
        add("parachute", I.pick("recovery.chute_mass_g", "chute_mass_g", "chute mass"), pack_x, "chute")
        cord_m = (A("shock_cord_length_factor") * L + A("shock_cord_loop_allowance_mm")) / 1000.0
        add("shock cord (Kevlar)", cord_m * I.pick(None, "shock_cord_g_per_m"), pack_x, f"{cord_m:.2f} m")
        add("wadding", I.pick(None, "wadding_g"), x_pack_aft - 10 if not _isnum(pos) else pack_x, "assumption")
    add("epoxy", I.pick(None, "epoxy_g"), L - sg["sleeve_len"] / 2, "ESTIMATE (sleeve joint)")
    add("rail buttons", I.pick(None, "rail_buttons_g"), L - A("rail_button_cg_from_aft_mm"), "ESTIMATE")
    add("motor retention (3 x M3 insert sets)", I.pick(None, "retention_g"),
        L - A("retention_cg_from_aft_mm"), "ESTIMATE")

    m_s = sum(i[1] for i in items)
    x_s = sum(i[1] * i[2] for i in items) / m_s
    x_motor_cg = x_motor_aft - m_len / 2           # assumption motor_dry_cg: midpoint
    m_dry = m_loaded - m_prop
    cg_lo = (m_s * x_s + m_loaded * x_motor_cg) / (m_s + m_loaded)
    cg_bo = (m_s * x_s + m_dry * x_motor_cg) / (m_s + m_dry)

    # Barrowman CP, subsonic: nose + step (tube -> fairing feather edge) + fairing cone + fins
    k = NOSE_K[shape]
    comps = [("nose", 2.0, k * Ln),
             ("step", *transition_cn(d, sg["fair_fwd_od"], 0.0, x_fair_fwd, d)),
             ("fairing", *transition_cn(sg["fair_fwd_od"], sg["od"], sg["fair_len"], x_fair_fwd, d)),
             ("fins", cnf, L - Cr + dx_cp)]
    cn_tot = sum(c[1] for c in comps)
    cp = sum(c[1] * c[2] for c in comps) / cn_tot
    d_max = max(d, sg["od"])

    return dict(
        inputs=I, d=d, d_max=d_max, Ln=Ln, Lt=Lt, bay_len=bay_len, Lb=Lb, L=L, shape=shape, sleeve=sg,
        x_tube_aft=x_tube_aft, x_fair_fwd=x_fair_fwd, cp_components=comps,
        fins=dict(N=N, Cr=Cr, Ct=Ct, s=s, xs=xs, t=t_fin, cnf=cnf, area=a_fin,
                  analytic_mass=N * a_fin * t_fin * rho_p),
        items=items, m_struct=m_s, x_struct=x_s,
        motor=dict(len=m_len, dia=m_dia, loaded=m_loaded, prop=m_prop, dry=m_dry,
                   x_aft=x_motor_aft, x_fwd=x_motor_fwd, x_cg=x_motor_cg),
        cg_liftoff=cg_lo, cg_burnout=cg_bo, cp=cp,
        sm_liftoff=(cp - cg_lo) / d, sm_burnout=(cp - cg_bo) / d,
        sm_liftoff_dmax=(cp - cg_lo) / d_max, sm_burnout_dmax=(cp - cg_bo) / d_max,
        m_liftoff=m_s + m_loaded, m_burnout=m_s + m_dry,
    )


# ----------------------------------------------------------------------------- RocketPy
def simulate(design, b, rail_length_m):
    from rocketpy import Environment, Flight, GenericMotor, Rocket

    A = lambda k: _get(design, "stability.assumptions." + k)  # noqa: E731
    site = A("launch_site")
    env = Environment(latitude=site["latitude"], longitude=site["longitude"], elevation=site["elevation_m"])
    wind = A("wind_m_s")
    if _isnum(wind) and wind != 0:   # constant wind blowing toward +east (u), standard atmosphere
        env.set_atmospheric_model(type="custom_atmosphere", pressure=None, temperature=None,
                                  wind_u=float(wind), wind_v=0)
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

    cd_tab, _ = cd_table(design)
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
    sg = b["sleeve"]
    # abrupt step tube OD -> fairing feather edge (RocketPy needs length > 0: STEP_LEN_M stand-in), then the cone
    rkt.add_tail(top_radius=R, bottom_radius=sg["fair_fwd_od"] / 2000, length=STEP_LEN_M,
                 position=b["x_fair_fwd"] / 1000, name="sleeve step")
    rkt.add_tail(top_radius=sg["fair_fwd_od"] / 2000, bottom_radius=sg["od"] / 2000, length=sg["fair_len"] / 1000,
                 position=b["x_fair_fwd"] / 1000, name="sleeve fairing")
    rkt.add_trapezoidal_fins(n=f["N"], root_chord=f["Cr"] / 1000, tip_chord=f["Ct"] / 1000,
                             span=f["s"] / 1000, position=L - f["Cr"] / 1000, sweep_length=f["xs"] / 1000,
                             radius=sg["od"] / 2000)

    t_bo = float(motor.burn_out_time)
    dmin, dmax = (int(x) for x in A("delay_range_s"))
    max_delay_s = dmax
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
        rp_cp_M0_mm=float(rkt.cp_position(0)) * 1000, rp_cp_M05_mm=float(rkt.cp_position(0.5)) * 1000,
        rp_cp_M08_mm=float(rkt.cp_position(0.8)) * 1000, rp_cp_M09_mm=float(rkt.cp_position(0.9)) * 1000,
        rail_exit_margin=float(fl.out_of_rail_stability_margin), max_margin=float(fl.max_stability_margin),
        deploy=[],
    )
    for delay in range(dmax, dmin - 1, -1):
        t = t_bo + delay
        if t > fl.t_final:
            continue
        out["deploy"].append(dict(delay=delay, t=t, alt=float(fl.z(t)) - elev, speed=float(fl.speed(t)),
                                  vz=float(fl.vz(t))))
    out["_flight"], out["_rocket"] = fl, rkt
    out["apogee_drift_m"] = float(math.hypot(fl.x(t_ap), fl.y(t_ap)))
    return out


# ----------------------------------------------------------------------------- margin vs time
def margin_history(design, b, sim, extra_loss_g=0.0, delay_s=None, n=600):
    """Static margin vs time, liftoff -> apogee: (CP(Mach(t)) - CG(t)) / d.
    CP(M) is RocketPy's Mach-dependent Barrowman CP; CG(t) is RocketPy's (propellant burns per the
    thrust curve, impulse-proportional, same as the RSE m(t)). extra_loss_g = delay grain + ejection
    mass (unpublished), modelled as burning linearly over the delay at the motor's FORWARD end."""
    fl, rkt = sim["_flight"], sim["_rocket"]
    d_m = b["d"] / 1000
    t_bo, t_ap = sim["t_burnout"], sim["t_apogee"]
    if delay_s is None:
        delay_s = float(_get(design, "stability.recommended_delay_s"))
    x_fwd = (b["motor"]["x_aft"] - b["motor"]["len"]) / 1000
    t = np.linspace(0, t_ap, n)
    t = np.unique(np.concatenate([t, [sim["t_rail"], t_bo, float(fl.max_dynamic_pressure_time)]]))
    mach = np.array([float(fl.mach_number(x)) for x in t])
    cp = np.array([float(rkt.cp_position(m)) for m in mach])
    m_tot = np.array([float(rkt.total_mass(x)) for x in t])
    cg = np.array([float(rkt.center_of_mass(x)) for x in t])
    lost = extra_loss_g / 1000 * np.clip((t - t_bo) / delay_s, 0, 1)
    cg = (m_tot * cg - lost * x_fwd) / (m_tot - lost)
    sm = (cp - cg) / d_m
    return dict(t=t, mach=mach, cp_mm=cp * 1000, cg_mm=cg * 1000, sm=sm, mass_g=(m_tot - lost) * 1000)


def key_events(sim, hist):
    fl = sim["_flight"]
    ev = [("liftoff", 0.0), ("rail exit", sim["t_rail"]), ("max q", float(fl.max_dynamic_pressure_time)),
          ("Vmax", sim["t_vmax"]), ("burnout", sim["t_burnout"]),
          ("coast, M 0.5", None), ("coast, M 0.3", None), ("apogee", sim["t_apogee"])]
    rows = []
    t, mach = hist["t"], hist["mach"]
    i_vmax = int(np.argmax(mach))
    for name, te in ev:
        if te is None:
            target = float(name.split("M ")[1])
            j = i_vmax + int(np.argmin(np.abs(mach[i_vmax:] - target)))
        else:
            j = int(np.argmin(np.abs(t - te)))
        rows.append((name, t[j], mach[j], hist["cp_mm"][j], hist["cg_mm"][j], hist["mass_g"][j], hist["sm"][j]))
    jmin = int(np.argmin(hist["sm"]))
    rows.append(("MINIMUM", t[jmin], mach[jmin], hist["cp_mm"][jmin], hist["cg_mm"][jmin],
                 hist["mass_g"][jmin], hist["sm"][jmin]))
    return rows


def margin_plot(design, b, sim, path):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    losses = _get(design, "stability.assumptions.delay_ejection_loss_sensitivity_g") or [0]
    tgt = _get(design, "owner.stability_target_cal")
    band = _get(design, "owner.stability_band_cal")
    fig, axes = plt.subplots(1, 2, figsize=(12, 5), gridspec_kw={"width_ratios": [1, 1.6]})
    hs = [(el, margin_history(design, b, sim, el)) for el in losses]
    for ax, (t0, t1, title) in zip(axes, ((0, sim["t_burnout"] + 0.3, "boost (linear, 0 to burnout + 0.3 s)"),
                                          (0, sim["t_apogee"], "whole ascent to apogee"))):
        for el, h in hs:
            ax.plot(h["t"], h["sm"], label=f"static margin, +{el} g delay/ejection loss")
        ax.axhspan(tgt - band, tgt + band, color="g", alpha=0.12, label=f"owner band {tgt}±{band} (liftoff gate)")
        ax2 = ax.twinx()
        ax2.plot(hs[0][1]["t"], hs[0][1]["mach"], "k:", lw=1, label="Mach")
        ax2.set_ylabel("Mach")
        ax2.set_ylim(0, 1)
        ax.set_xlim(t0, t1)
        lo_y = min(min(h["sm"].min() for _, h in hs), tgt - band) - 0.2
        hi_y = max(h["sm"].max() for _, h in hs) + 0.2
        ax.set_ylim(lo_y, hi_y)
        for name, te in (("rail exit", sim["t_rail"]), ("burnout", sim["t_burnout"]), ("apogee", sim["t_apogee"])):
            if t0 <= te <= t1:
                ax.axvline(te, color="grey", lw=0.8)
                ax.text(te, lo_y + 0.05, " " + name, rotation=90, va="bottom", fontsize=8)
        ax.set_xlabel("time from ignition (s)")
        ax.set_ylabel("static margin (cal)")
        ax.set_title(title, fontsize=10)
        ax.grid(alpha=0.3)
    l1, n1 = axes[1].get_legend_handles_labels()
    l2, n2 = ax2.get_legend_handles_labels()
    axes[1].legend(l1 + l2, n1 + n2, fontsize=8, loc="lower right")
    fig.suptitle(f"l1-cheap static margin vs time: CP(Mach) - CG(t); rail {sim['rail_m']} m, "
                 f"ballast {_get(design, 'stability.ballast_g')} g")
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(path, dpi=130)
    return path


def load_design(path, sets):
    design = yaml.safe_load(Path(path).read_text())
    for s in sets:
        k, v = s.split("=", 1)
        _set(design, k, yaml.safe_load(v))
    return design


def run(design, allow_tbd=False, rails=None):
    b = build(design, allow_tbd)
    rails = rails or _get(design, "stability.assumptions.rail_lengths_m")
    if b["sm_liftoff"] <= 0:   # statically unstable: a 6-DOF tumble is meaningless and very slow
        return b, []
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
    sg = b["sleeve"]
    print(f"Length {b['L']:.2f} mm (nose {b['Ln']:.0f} + bay {b['bay_len']:.0f} + tube {b['Lt']:.0f} "
          f"+ lip {sg['lip']:.2f}); min-diameter, motor aft end {b['motor']['x_aft']:.2f} (aft face {b['L']:.2f})")
    print(f"Sleeve OD {sg['od']:.3f} over the aft {sg['sleeve_len']:.0f} mm, fairing {sg['fair_fwd_od']:.3f} -> "
          f"{sg['od']:.3f} over {sg['fair_len']:.0f} mm from x {b['x_fair_fwd']:.2f}; fins "
          f"{b['fins']['N']}x Cr {b['fins']['Cr']:.0f} / Ct {b['fins']['Ct']:.0f} / s {b['fins']['s']:.0f} / "
          f"sweep {b['fins']['xs']:.0f} / t {b['fins']['t']:.0f}")
    print("\nMass budget (x from nose tip):")
    print(f"  {'item':38s} {'g':>7s} {'x mm':>7s}  basis")
    for n, m, x, basis in b["items"]:
        print(f"  {n:38s} {m:7.1f} {x:7.1f}  {basis}")
    mo = b["motor"]
    print(f"  {'motor loaded / burnout':38s} {mo['loaded']:7.1f} {mo['x_cg']:7.1f}  motor ({mo['dry']:.0f} g dry)")
    print(f"  structure {b['m_struct']:.1f} g @ {b['x_struct']:.1f}; liftoff {b['m_liftoff']:.1f} g; burnout {b['m_burnout']:.1f} g")
    print("\nBarrowman CP components (CN_alpha @ x mm, ref d %.3f):" % b["d"])
    for n, cn, x in b["cp_components"]:
        print(f"  {n:8s} {cn:7.3f} @ {x:7.1f}")
    print(f"  Cd source: {cd_table(design)[1]}: {cd_table(design)[0]}")

    def verdict(sm):
        return "PASS" if lo <= sm <= hi else ("FAIL (low)" if sm < lo else "FAIL (high)")
    print(f"\nCP (Barrowman, M~0) {b['cp']:.1f} mm   CG liftoff {b['cg_liftoff']:.1f}   CG burnout {b['cg_burnout']:.1f}")
    gated_bo = _get(design, "owner.stability_band_applies") != "liftoff_only"
    bo_txt = verdict(b["sm_burnout"]) if gated_bo else "reported, not gated (owner: liftoff only)"
    print(f"Static margin liftoff {b['sm_liftoff']:.2f} cal  {verdict(b['sm_liftoff'])}   "
          f"burnout {b['sm_burnout']:.2f} cal  {bo_txt}   [target {tgt} +/- {band}, ref d {b['d']:.3f}]")
    print(f"  on max diameter {b['d_max']:.3f} (OpenRocket default reference): liftoff {b['sm_liftoff_dmax']:.2f} cal, "
          f"burnout {b['sm_burnout_dmax']:.2f} cal (same CP and CG; only the divisor changes)")
    if not sims:
        print("\nUNSTABLE at liftoff (margin <= 0): flight NOT simulated.")
        return
    s0 = sims[0]
    print(f"RocketPy: CP M0 {s0['rp_cp_M0_mm']:.1f} / M0.5 {s0['rp_cp_M05_mm']:.1f} / M0.8 {s0['rp_cp_M08_mm']:.1f} mm; static margin "
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
    ap.add_argument("--margin-plot", help="write static-margin-vs-time PNG here and print the key-event table")
    a = ap.parse_args()
    design = load_design(a.design, a.set)
    b, sims = run(design, a.allow_tbd)
    report(b, sims, design)
    if a.margin_plot and sims:
        s0 = sims[-1]
        print(f"\nMargin vs time (rail {s0['rail_m']} m; extra delay/ejection loss as labelled):")
        print(f"  {'event':14s} {'t s':>6s} {'Mach':>5s} {'CP mm':>6s} {'CG mm':>6s} {'mass g':>6s} {'SM cal':>6s}")
        for el in _get(design, "stability.assumptions.delay_ejection_loss_sensitivity_g") or [0]:
            print(f"  -- +{el} g --")
            for r in key_events(s0, margin_history(design, b, s0, el)):
                print(f"  {r[0]:14s} {r[1]:6.3f} {r[2]:5.3f} {r[3]:6.1f} {r[4]:6.1f} {r[5]:6.1f} {r[6]:6.2f}")
        print("plot:", margin_plot(design, b, s0, a.margin_plot))
    if a.json:
        bb = {k: v for k, v in b.items() if k != "inputs"}
        bb["missing_tbd"] = b["inputs"].missing
        bb["assumptions_used"] = sorted(set(b["inputs"].used_assumptions))
        fl = [{k: v for k, v in x.items() if not k.startswith("_")} for x in sims]
        Path(a.json).write_text(json.dumps(dict(budget=bb, flights=fl), indent=1))


if __name__ == "__main__":
    main()
