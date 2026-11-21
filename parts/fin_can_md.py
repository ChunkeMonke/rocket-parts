"""Minimum-diameter fin can: a printed sleeve that slides OVER the airframe tube's aft end.

The 38 mm motor sits directly in the tube. The sleeve carries the fins, a forward fairing down to the tube OD,
and an aft lip under the tube end that the motor's thrust ring bears on. Retention: M3 heat-set inserts in
faired bosses at the fin roots (screw + washer over the thrust ring).

Coordinates (as printed): Z = rocket axis, z = 0 is the AFT face on the build plate, +Z forward.

Parameters (projects/<project>/design.yaml `fin_can_md:` + `aero:` + skills/SKILL.md):
  tube_od_mm          mm   airframe tube OD; sleeve bore = tube OD + 2 x fit
  sleeve_wall_mm      mm   sleeve wall (= print-profile perimeter band)
  sleeve_length_mm    mm   aft face to start of fairing (= fin root chord)
  fairing_length_mm   mm   taper from sleeve OD down to a feather edge on the tube
  feather_edge_mm     mm   thinnest printable fairing edge (= 2 outer-wall lines)
  lip_thickness_mm    mm   aft lip under the tube end (thrust stop)
  lip_bore_d_mm       mm   = motor case OD + 2 x fit
  motor_case_od_mm, motor_length_mm, thrust_ring_od_mm, thrust_ring_thk_mm   mm   mating geometry
  fin params, insert/boss params: as parts/fin_can.py
  target_mass_g       g    verify check 2 target
"""
from __future__ import annotations

from pathlib import Path

import cadquery as cq
import yaml

from parts import fin_can
from parts.shop import const

ROOT = Path(__file__).resolve().parent.parent

INFO = {
    "print_orientation": "Aft face (lip) DOWN on the bed, axis vertical. No supports: lip and sleeve are vertical walls, "
                         "fins shrink going up, the forward fairing narrows going up.",
    "loads": [
        "Motor thrust: the thrust ring pushes UP (+Z) on the lip's underside, and the lip pushes the tube end forward. "
        "The layers are pressed together (compression across layers). Good direction.",
        "Fin root bending: within the layers (radial/tangential).",
        "Sleeve-to-tube epoxy joint: carries fin loads and drag in shear on vertical (cylindrical) faces, "
        "so the PETG is sheared in-plane.",
        "Ejection kick on the motor (-Z): the ring pulls the screws aft, and the inserts pull out of their bosses "
        "along Z (across layers, the weak direction). See motor.md for capacity.",
    ],
}


def params(project: str = "l1-cheap") -> dict:
    d = yaml.safe_load((ROOT / "projects" / project / "design.yaml").read_text())
    fc, aero = d["fin_can_md"], d["aero"]
    v = {k: (x["value"] if isinstance(x, dict) else x) for k, x in fc.items()}
    lw = const("print_profile_petg.line_width_mm")
    wall = lw["outer_wall"] + (const("print_profile_petg.wall_loops") - 1) * lw["inner_wall"]
    fit = const(f"fits_in_tube.{v['sleeve_fit']}_mm_per_side")
    sleeve_bore = v["tube_od_mm"] + 2 * fit
    p = {
        "tube_od_mm": v["tube_od_mm"],
        "tube_id_mm": const("airframe.loc_38mm_paper.id_measured_mm"),
        "sleeve_bore_d_mm": sleeve_bore,
        "sleeve_wall_mm": wall,
        "body_od_mm": sleeve_bore + 2 * wall,          # sleeve OD = fin root body
        "sleeve_length_mm": v["sleeve_overlap_mm"],
        "fairing_length_mm": v["fairing_length_mm"],
        "feather_edge_mm": 2 * lw["outer_wall"],
        "lip_thickness_mm": wall,
        "motor_case_od_mm": v["motor_case_od_mm"],
        "lip_bore_d_mm": v["motor_case_od_mm"] + 2 * fit,
        "motor_length_mm": v["motor_length_mm"],
        "thrust_ring_od_mm": v["thrust_ring_od_mm"],
        "thrust_ring_thk_mm": v["thrust_ring_thk_mm"],
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
        "insert_hole_d_mm": v["insert_hole_d_mm"],
        "insert_depth_mm": v["insert_depth_mm"],
        "boss_wall_mm": wall,
        "insert_radius_mm": sleeve_bore / 2 + wall + v["insert_hole_d_mm"] / 2,
        "boss_fairing_length_mm": v["boss_fairing_length_mm"],
        "target_mass_g": v["target_mass_g"],
    }
    p["washer_min_od_mm"] = 2 * (2.0 + p["insert_radius_mm"] - p["thrust_ring_od_mm"] / 2)
    p["_status"] = {k: x.get("status", "") for k, x in fc.items() if isinstance(x, dict)}
    p["_source"] = {k: x.get("note", "") for k, x in fc.items() if isinstance(x, dict)}
    return p


def build(p: dict) -> cq.Workplane:
    r_so, r_sb = p["body_od_mm"] / 2, p["sleeve_bore_d_mm"] / 2
    L, Lf = p["sleeve_length_mm"], p["fairing_length_mm"]
    sleeve = cq.Workplane("XY").circle(r_so).extrude(L)
    fair = cq.Workplane("XY").add(cq.Solid.makeLoft([
        cq.Wire.makeCircle(r_so, cq.Vector(0, 0, L), cq.Vector(0, 0, 1)),
        cq.Wire.makeCircle(r_sb + p["feather_edge_mm"], cq.Vector(0, 0, L + Lf), cq.Vector(0, 0, 1))], ruled=True))
    body = sleeve.union(fair)
    fin = fin_can.fin_solid(p)
    for i in range(p["fin_count"]):
        body = body.union(cq.Workplane("XY").add(
            fin.rotate(cq.Vector(0, 0, 0), cq.Vector(0, 0, 1), i * 360.0 / p["fin_count"])))
    body = body.union(fin_can.retention_bosses(p))
    t = p["lip_thickness_mm"]
    body = body.cut(cq.Workplane("XY").circle(p["lip_bore_d_mm"] / 2).extrude(t))
    body = body.cut(cq.Workplane("XY").circle(r_sb).extrude(L + Lf).translate((0, 0, t)))
    return body.cut(fin_can.insert_holes(p))


def mating(p: dict) -> dict[str, cq.Workplane]:
    t = p["lip_thickness_mm"]
    tube_len = p["sleeve_length_mm"] + p["fairing_length_mm"] + p["root_chord_mm"]
    tube = (cq.Workplane("XY").circle(p["tube_od_mm"] / 2).circle(p["tube_id_mm"] / 2)
            .extrude(tube_len).translate((0, 0, t)))
    motor = cq.Workplane("XY").circle(p["motor_case_od_mm"] / 2).extrude(p["motor_length_mm"])
    ring = (cq.Workplane("XY").circle(p["thrust_ring_od_mm"] / 2).extrude(p["thrust_ring_thk_mm"])
            .translate((0, 0, -p["thrust_ring_thk_mm"])))
    return {"tube_wall": tube, "motor_case": motor, "motor_thrust_ring": ring}


def extras(p: dict, out_dir: Path, stem: str) -> list[Path]:
    return fin_can.extras(p, out_dir, stem)
