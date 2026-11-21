"""One-piece printed fin can: fins + motor mount + liner seat + centering + airframe shoulder.

Coordinates (as printed): Z = rocket axis, z = 0 is the AFT face on the build plate, +Z is forward.
Fin i lies in the plane at angle i*360/fin_count about Z; thickness is tangential.

Parameters (all from projects/<project>/design.yaml `fin_can:` + `aero:` + skills/SKILL.md):
  body_od_mm          mm   exposed OD, flush with the airframe tube OD
  shoulder_od_mm      mm   = tube id_measured - 2 x fit (per side), fit from fits_in_tube
  exposed_length_mm   mm   aft section outside the tube (= fin root chord)
  shoulder_length_mm  mm   section epoxied inside the tube
  liner_od_mm         mm   paper liner OD; bore = liner OD + 2 x bore fit (per side)
  liner_length_mm     mm   liner (and motor) length
  fin_count           -    number of fins
  root_chord_mm, tip_chord_mm, span_mm, sweep_mm   mm   planform; TE square and flush with the aft face
  fin_thickness_mm    mm   max airfoil thickness (constant root to tip)
  te_thickness_mm     mm   blunt trailing-edge thickness (printable)
  root_fillet_r_mm    mm   fin-root fillet radius (loft approximation)
  root_fillet_sections  -  loft stations through the fillet
  airfoil_points      -    cosine-spaced chord stations per surface
  anchor_groove_width_mm, anchor_groove_depth_mm  mm   Kevlar groove in the shoulder OD
  anchor_angle_deg    deg  groove position about Z (between fins)
  thrust_ring_od_mm, thrust_ring_thk_mm  mm  motor thrust ring (mating check; sets washer size)
  insert_hole_d_mm, insert_depth_mm       mm  M3 heat-set insert hole (one per fin, axial, from the aft face)
  boss_wall_mm        mm   plastic around the insert hole (= print-profile perimeter band)
  insert_radius_mm    mm   insert axis radius = bore/2 + boss wall + hole/2 (derived: keeps a full wall to the bore)
  boss_fairing_length_mm  mm  taper from the boss into the fin root, forward of the insert
  washer_min_overlap_mm   mm  required washer overlap on the thrust ring
  target_mass_g       g    declared target for verify check 2
"""
from __future__ import annotations

import math
from pathlib import Path

import cadquery as cq
import numpy as np
import yaml

from parts.shop import const

ROOT = Path(__file__).resolve().parent.parent

INFO = {
    "print_orientation": "Aft face DOWN on the bed, axis vertical (+Z = forward). No supports: "
                         "fin outlines shrink going up (TE square at the bed, LE swept back).",
    "loads": [
        "Motor thrust: the thrust ring pushes UP (+Z) on the aft face, so the layers are pressed together "
        "(compression across layers). Good direction.",
        "Fin root bending (aero side load): bending stress runs radially/tangentially, WITHIN the layers.",
        "Kevlar anchor (deploy): the cord pulls +Z on a groove epoxied under the tube. The bond is loaded "
        "in shear on vertical faces, so the PETG layers are sheared in-plane, not peeled apart.",
        "Ejection kick on the motor (aft): thrust ring pulls the screws/washers aft (-Z); each insert is "
        "pulled out of its boss along Z, which loads the boss across the layers (the weak direction). "
        "Capacity estimate in motor.md (SF ~2.6 for 2 inserts; rev 2 has one per fin).",
    ],
}


# ------------------------------------------------------------------ parameters
def params(project: str = "l1-cheap") -> dict:
    d = yaml.safe_load((ROOT / "projects" / project / "design.yaml").read_text())
    fc, aero = d["fin_can"], d["aero"]
    v = {k: (x["value"] if isinstance(x, dict) else x) for k, x in fc.items()}
    status = {k: x.get("status", "") for k, x in fc.items() if isinstance(x, dict)}
    lw = const("print_profile_petg.line_width_mm")
    tube_id = const("airframe.loc_38mm_paper.id_measured_mm")
    fit = lambda name: const(f"fits_in_tube.{name}_mm_per_side")  # noqa: E731
    p = {
        "body_od_mm": v["body_od_mm"],
        "tube_id_mm": tube_id,
        "shoulder_od_mm": tube_id - 2 * fit(v["shoulder_fit"]),
        "exposed_length_mm": v["exposed_length_mm"],
        "shoulder_length_mm": v["shoulder_length_mm"],
        "liner_od_mm": v["liner_od_mm"],
        "liner_id_mm": v["liner_id_mm"],
        "liner_length_mm": v["liner_length_mm"],
        "bore_d_mm": v["liner_od_mm"] + 2 * fit(v["bore_fit"]),
        "fin_count": aero["fin_count"],
        "root_chord_mm": aero["fin_root_chord_mm"],
        "tip_chord_mm": aero["fin_tip_chord_mm"],
        "span_mm": aero["fin_span_mm"],
        "sweep_mm": aero["fin_sweep_mm"],
        "fin_thickness_mm": aero["fin_thickness_mm"],
        "te_thickness_mm": 2 * lw["outer_wall"],
        "root_fillet_r_mm": v["root_fillet_r_mm"],
        "root_fillet_sections": v["root_fillet_sections"],
        "airfoil_points": v["airfoil_points"],
        "anchor_groove_width_mm": v["anchor_groove_width_mm"],
        "anchor_groove_depth_mm": v["anchor_groove_depth_mm"],
        "anchor_angle_deg": v["anchor_angle_deg"],
        "thrust_ring_od_mm": v["thrust_ring_od_mm"],
        "thrust_ring_thk_mm": v["thrust_ring_thk_mm"],
        "target_mass_g": v["target_mass_g"],
        "retention": v["retention"],
    }
    if v["retention"] == "insert_bosses_at_fin_roots":
        wall = lw["outer_wall"] + (const("print_profile_petg.wall_loops") - 1) * lw["inner_wall"]
        p.update({
            "insert_hole_d_mm": v["insert_hole_d_mm"],
            "insert_depth_mm": v["insert_depth_mm"],
            "boss_wall_mm": wall,
            "insert_radius_mm": p["bore_d_mm"] / 2 + wall + v["insert_hole_d_mm"] / 2,
            "boss_fairing_length_mm": v["boss_fairing_length_mm"],
            "washer_min_overlap_mm": v["washer_min_overlap_mm"],
        })
        # washer OD the screws need so the washer overlaps the ring by the required amount
        p["washer_min_od_mm"] = 2 * (p["washer_min_overlap_mm"] + p["insert_radius_mm"] - p["thrust_ring_od_mm"] / 2)
    p["_status"] = status
    p["_source"] = {k: (fc[k].get("note", "") if isinstance(fc.get(k), dict) else "") for k in fc}
    return p


# ------------------------------------------------------------------ airfoil
def naca_half_thickness(x: np.ndarray, t_max: float, te: float) -> np.ndarray:
    """NACA 4-digit symmetric half-thickness (mm) at chord fraction x, max thickness t_max,
    with a linear blend so the trailing-edge thickness is exactly `te`."""
    poly = 0.2969 * np.sqrt(x) - 0.1260 * x - 0.3516 * x**2 + 0.2843 * x**3 - 0.1015 * x**4
    yt = 5 * t_max * poly
    yt_te = 5 * t_max * (0.2969 - 0.1260 - 0.3516 + 0.2843 - 0.1015)
    return yt + (te / 2 - yt_te) * x


def chord_stations(n: int) -> np.ndarray:
    beta = np.linspace(0, math.pi, n)
    return (1 - np.cos(beta)) / 2


def section_points(p: dict, chord: float, scale: float, t: float | None = None,
                   te: float | None = None) -> list[tuple[float, float]]:
    """Closed (y, z) loop: upper TE -> LE -> lower TE. LE at z = chord, TE at z = 0."""
    x = chord_stations(p["airfoil_points"])
    t = p["fin_thickness_mm"] if t is None else t
    te = p["te_thickness_mm"] if te is None else te
    yt = scale * naca_half_thickness(x, t, te)
    z = chord * (1 - x)
    upper = [(yt[i], z[i]) for i in range(len(x) - 1, -1, -1)]      # TE -> LE
    lower = [(-yt[i], z[i]) for i in range(1, len(x))]               # LE -> TE
    return upper + lower


def chord_at(p: dict, r: float) -> float:
    rb = p["body_od_mm"] / 2
    frac = min(max((r - rb) / p["span_mm"], 0.0), 1.0)
    return p["root_chord_mm"] - (p["root_chord_mm"] - p["tip_chord_mm"]) * frac


def fin_solid(p: dict) -> cq.Solid:
    rb, f, t = p["body_od_mm"] / 2, p["root_fillet_r_mm"], p["fin_thickness_mm"]
    # The fillet's widest edge (|y| = t/2 + f) must land ON the round body, not at r = rb,
    # or its flat side pokes out past the curved surface as a ledge.
    r_start = math.sqrt(rb**2 - (t / 2 + f) ** 2)
    run = rb + f - r_start                     # radial run of the fillet arc
    stations = [r_start - f]                   # inside the body so the fin fuses
    stations += list(r_start + np.linspace(0, run, p["root_fillet_sections"]))
    stations.append(rb + p["span_mm"])
    wires = []
    for r in stations:
        u = min(max((r - r_start) / run, 0.0), 1.0)
        extra = f * (1 - math.sqrt(max(1 - (1 - u) ** 2, 0.0)))   # concave arc: f at the body -> 0
        # optional spanwise taper of max thickness and TE thickness (root -> tip)
        frac = min(max((r - rb) / p["span_mm"], 0.0), 1.0)
        t_r = t + (p.get("fin_tip_thickness_mm", t) - t) * frac
        te0 = p.get("te_root_thickness_mm", p["te_thickness_mm"])
        te_r = te0 + (p["te_thickness_mm"] - te0) * frac
        scale = (t_r + 2 * extra) / t_r
        pts = section_points(p, chord_at(p, r), scale, t_r, te_r)
        wires.append(cq.Wire.makePolygon([cq.Vector(r, y, z) for y, z in pts], close=True))
    return cq.Solid.makeLoft(wires, ruled=True)


# ------------------------------------------------------------------ part
def build(p: dict) -> cq.Workplane:
    le, ls = p["exposed_length_mm"], p["shoulder_length_mm"]
    body = (cq.Workplane("XY").circle(p["body_od_mm"] / 2).extrude(le)
            .faces(">Z").workplane().circle(p["shoulder_od_mm"] / 2).extrude(ls))
    fin = fin_solid(p)
    for i in range(p["fin_count"]):
        body = body.union(cq.Workplane("XY").add(fin.rotate(cq.Vector(0, 0, 0), cq.Vector(0, 0, 1),
                                                           i * 360.0 / p["fin_count"])))
    if p.get("retention") == "insert_bosses_at_fin_roots":
        body = body.union(retention_bosses(p))
    bore = cq.Workplane("XY").circle(p["bore_d_mm"] / 2).extrude(le + ls)
    body = body.cut(bore)
    if p.get("retention") == "insert_bosses_at_fin_roots":
        body = body.cut(insert_holes(p))
    # Kevlar anchor groove on the shoulder OD
    w, dep = p["anchor_groove_width_mm"], p["anchor_groove_depth_mm"]
    r_sh = p["shoulder_od_mm"] / 2
    groove = (cq.Workplane("XY").box(dep + 1.0, w, ls, centered=(False, True, False))
              .translate((r_sh - dep, 0, le))
              .rotate((0, 0, 0), (0, 0, 1), p["anchor_angle_deg"]))
    return body.cut(groove)


def _at_fins(p: dict, solid: cq.Workplane) -> cq.Workplane:
    out = None
    for i in range(p["fin_count"]):
        s = solid.rotate((0, 0, 0), (0, 0, 1), i * 360.0 / p["fin_count"])
        out = s if out is None else out.union(s)
    return out


def retention_bosses(p: dict) -> cq.Workplane:
    """Per fin: a cylinder around the insert (insert depth + a wall-thick cap), then a loft that
    tapers it into the fin root so the outside stays faired."""
    r_b = p["insert_hole_d_mm"] / 2 + p["boss_wall_mm"] + p.get("boss_extra_wall_mm", 0.0)
    h_b = p["insert_depth_mm"] + p["boss_wall_mm"]
    cyl = cq.Solid.makeCylinder(r_b, h_b, cq.Vector(p["insert_radius_mm"], 0, 0))
    w0 = cq.Wire.makeCircle(r_b, cq.Vector(p["insert_radius_mm"], 0, h_b), cq.Vector(0, 0, 1))
    w1 = cq.Wire.makeCircle(p["fin_thickness_mm"] / 2,
                            cq.Vector(p["insert_radius_mm"], 0, h_b + p["boss_fairing_length_mm"]),
                            cq.Vector(0, 0, 1))
    fair = cq.Solid.makeLoft([w0, w1], ruled=True)
    return _at_fins(p, cq.Workplane("XY").add(cyl).union(cq.Workplane("XY").add(fair)))


def insert_holes(p: dict) -> cq.Workplane:
    hole = cq.Workplane("XY").add(cq.Solid.makeCylinder(p["insert_hole_d_mm"] / 2, p["insert_depth_mm"],
                                                        cq.Vector(p["insert_radius_mm"], 0, 0)))
    return _at_fins(p, hole)


def mating(p: dict) -> dict[str, cq.Workplane]:
    le, ls = p["exposed_length_mm"], p["shoulder_length_mm"]
    tube_len = ls + p["root_chord_mm"]  # tube continues forward past the shoulder top
    tube = (cq.Workplane("XY").circle(p["body_od_mm"] / 2).circle(p["tube_id_mm"] / 2)
            .extrude(tube_len).translate((0, 0, le)))
    liner = cq.Workplane("XY").circle(p["liner_od_mm"] / 2).extrude(p["liner_length_mm"])
    ring = (cq.Workplane("XY").circle(p["thrust_ring_od_mm"] / 2).extrude(p["thrust_ring_thk_mm"])
            .translate((0, 0, -p["thrust_ring_thk_mm"])))
    return {"tube_wall": tube, "liner_and_motor": liner, "motor_thrust_ring": ring}


def extras(p: dict, out_dir: Path, stem: str) -> list[Path]:
    """ANSYS/XFOIL exports: Selig .dat airfoils (root, tip) and a single-fin STEP."""
    paths = []
    for name, chord in (("root", p["root_chord_mm"]), ("tip", p["tip_chord_mm"])):
        x = chord_stations(p["airfoil_points"])
        yt = naca_half_thickness(x, p["fin_thickness_mm"], p["te_thickness_mm"]) / chord
        up = [(x[i], yt[i]) for i in range(len(x) - 1, -1, -1)]
        lo = [(x[i], -yt[i]) for i in range(1, len(x))]
        f = out_dir / f"{stem}_airfoil_{name}.dat"
        f.write_text(f"{stem} fin {name} section, chord {chord:g} mm, t {p['fin_thickness_mm']:g} mm "
                     f"(NACA 4-digit symmetric, TE {p['te_thickness_mm']:.2f} mm)\n"
                     + "\n".join(f" {a:.6f} {b:.6f}" for a, b in up + lo) + "\n")
        paths.append(f)
    fin_step = out_dir / f"{stem}_fin_only.step"
    cq.exporters.export(cq.Workplane("XY").add(fin_solid(p)), str(fin_step))
    paths.append(fin_step)
    return paths
