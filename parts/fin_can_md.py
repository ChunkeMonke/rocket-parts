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
  fin_tip_thickness_mm  mm  optional spanwise taper (aero.fin_tip_thickness_mm; default = root thickness)
  te_root_thickness_mm  mm  blunt TE thickness at the root, tapering to te_thickness at the tip
  boss_extra_wall_mm    mm  extra plastic around the insert boss beyond the perimeter band (rev 7)
  tail_cone             bool rev 8: no insert holes; threaded collar behind the aft face for parts/tail_cone.py
  collar_length_mm, collar_bore_d_mm   mm  collar below the aft face (z < 0), bore = thread minor dia
  boattail_length_mm, boattail_end_od_mm, tail_cone_bore_d_mm   mm  tail cone (used by parts/tail_cone.py)
  thread_pitch_mm, thread_depth_mm, thread_clearance_mm   mm  printed 45-deg thread (parts/nose_cone.py helpers)
  te_gusset_mm          mm  rev 8: 45-deg wedge under each fin root TE onto the collar (stress-corner fix; 0 = off)
  te_fillet_r_mm        mm  rev 9: smooth concave skirt (radius) under each fin root TE onto the collar
  insert_bosses         bool rev 9: False = no M3 insert bosses (tail cone retains the motor)
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
                         "fins shrink going up, the forward fairing narrows going up. REV 8 (tail_cone): the collar is on the bed and "
                         "the fins' blunt trailing edges (1-8 mm wide) hang 12 mm above it: add small supports under the "
                         "three fin TEs only (paint-on / tree, build plate only).",
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
        "fin_thickness_mm": aero["fin_thickness_mm"],          # root max thickness
        "fin_tip_thickness_mm": aero.get("fin_tip_thickness_mm", aero["fin_thickness_mm"]),
        "te_thickness_mm": 2 * lw["outer_wall"],
        "root_fillet_r_mm": v["root_fillet_r_mm"],
        "te_root_thickness_mm": v.get("te_root_thickness_mm", 2 * lw["outer_wall"]),
        "root_fillet_sections": v["root_fillet_sections"],
        "airfoil_points": v["airfoil_points"],
        "insert_hole_d_mm": v["insert_hole_d_mm"],
        "insert_depth_mm": v["insert_depth_mm"],
        "boss_wall_mm": wall,
        "boss_extra_wall_mm": v.get("boss_extra_wall_mm", 0.0),
        "insert_radius_mm": sleeve_bore / 2 + wall + v["insert_hole_d_mm"] / 2,
        "boss_fairing_length_mm": v["boss_fairing_length_mm"],
        "target_mass_g": v["target_mass_g"],
        "tail_cone": bool(v.get("tail_cone", False)),
    }
    if p["tail_cone"]:
        for k in ("collar_length_mm", "collar_bore_d_mm", "boattail_length_mm", "boattail_end_od_mm",
                  "tail_cone_bore_d_mm", "thread_pitch_mm", "thread_depth_mm", "thread_clearance_mm", "te_gusset_mm"):
            p[k] = v[k]
        p["te_fillet_r_mm"] = v.get("te_fillet_r_mm", 0.0)
        p["insert_bosses"] = bool(v.get("insert_bosses", True))
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
    if p.get("insert_bosses", True):
        body = body.union(fin_can.retention_bosses(p))
    t = p["lip_thickness_mm"]
    body = body.cut(cq.Workplane("XY").circle(p["lip_bore_d_mm"] / 2).extrude(t))
    body = body.cut(cq.Workplane("XY").circle(r_sb).extrude(L + Lf).translate((0, 0, t)))
    if not p["tail_cone"]:
        return body.cut(fin_can.insert_holes(p))
    body = body.union(collar(p))
    if p.get("te_gusset_mm", 0) > 0:
        body = body.union(te_gussets(p))
    if p.get("te_fillet_r_mm", 0) > 0:
        body = body.union(te_fillets(p))
    return body


def te_fillets(p: dict) -> cq.Workplane:
    """Rev 9: smooth concave skirt under each fin root TE: a quarter-circle of radius R that is tangent to the collar
    (vertical) at z = -R and meets the fin's aft face at r = r_body + R. Width = TE root + 2 x root fillet, so the
    fin's filleted root footprint is carried down into the collar without a sharp corner."""
    import math
    R, r0 = p["te_fillet_r_mm"], p["body_od_mm"] / 2
    w = p["te_root_thickness_mm"] + 2 * p["root_fillet_r_mm"]
    arc = [(r0 + R - R * math.cos(t), -R + R * math.sin(t)) for t in [k * (math.pi / 2) / 16 for k in range(17)]]
    pts = [(r0 - 0.5, -R - 0.5), (r0 - 0.5, 0.0)] + list(reversed(arc))[:-1] + [(r0, -R)]
    pts = [(r0 - 0.5, 0.0), (r0 + R, 0.0)] + [(r0 + R - R * math.cos(t), -R + R * math.sin(t))
                                               for t in [k * (math.pi / 2) / 16 for k in range(16, -1, -1)]][1:] \
          + [(r0 - 0.5, -R)]
    prof = cq.Workplane("XZ").polyline(pts).close().extrude(w / 2, both=True)
    out = None
    for i in range(p["fin_count"]):
        pi = prof.rotate((0, 0, 0), (0, 0, 1), i * 360.0 / p["fin_count"])
        out = pi if out is None else out.union(pi)
    return out


def te_gussets(p: dict) -> cq.Workplane:
    """Rev 8: 45-deg wedge under each fin's root trailing edge, from the fin's aft face (z = 0) down onto the collar.
    Width = blunt TE root thickness; it removes the 90-deg re-entrant corner at the fin root TE."""
    g, r0 = p["te_gusset_mm"], p["body_od_mm"] / 2
    w = p["te_root_thickness_mm"]
    wedge = (cq.Workplane("XZ").polyline([(r0 - 0.5, 0.0), (r0 + g, 0.0), (r0 - 0.5, -g - 0.5)]).close()
             .extrude(w / 2, both=True))
    out = None
    for i in range(p["fin_count"]):
        wi = wedge.rotate((0, 0, 0), (0, 0, 1), i * 360.0 / p["fin_count"])
        out = wi if out is None else out.union(wi)
    return out


def collar(p: dict) -> cq.Workplane:
    """Rev 8: threaded collar below the aft face (z from -collar_length to 0), OD = sleeve OD, female thread.
    The groove opens on the collar's aft face and ends inside the wall above the thread run-out."""
    from parts import nose_cone
    Lc, r_b = p["collar_length_mm"], p["collar_bore_d_mm"] / 2
    c = (cq.Workplane("XY").circle(p["body_od_mm"] / 2).circle(r_b).extrude(Lc).translate((0, 0, -Lc)))
    h = Lc - p["thrust_ring_thk_mm"] - p["thread_pitch_mm"]
    return c.cut(nose_cone.groove(p, r_b, -Lc, h))


def tail_cone_installed(p: dict) -> cq.Workplane:
    """Rev 8 tail cone in fin-can coordinates: threaded shank inside the collar (its forward face bears on the
    thrust ring at z = -ring thickness) and a boattail frustum aft of the collar."""
    from parts import nose_cone
    Lc, Lb, pitch, c = p["collar_length_mm"], p["boattail_length_mm"], p["thread_pitch_mm"], p["thread_clearance_mm"]
    r_b, r_i = p["collar_bore_d_mm"] / 2, p["tail_cone_bore_d_mm"] / 2
    z_ring = -p["thrust_ring_thk_mm"]
    shank = cq.Workplane("XY").circle(r_b - c).circle(r_i).extrude(z_ring + Lc).translate((0, 0, -Lc))
    h_groove = Lc - p["thrust_ring_thk_mm"] - pitch
    z0 = -Lc + pitch                                     # same helix phase as the collar groove (starts at -Lc)
    ridge = nose_cone.ridge(p, r_b, z0, h_groove - pitch).intersect(
        cq.Workplane("XY").circle(r_b + 2).circle(r_i + 0.3).extrude(z_ring + Lc).translate((0, 0, -Lc)))
    body = cq.Workplane("XY").add(cq.Solid.makeLoft([
        cq.Wire.makeCircle(p["boattail_end_od_mm"] / 2, cq.Vector(0, 0, -Lc - Lb), cq.Vector(0, 0, 1)),
        cq.Wire.makeCircle(p["body_od_mm"] / 2, cq.Vector(0, 0, -Lc), cq.Vector(0, 0, 1))], ruled=True))
    body = body.cut(cq.Workplane("XY").circle(r_i).extrude(Lb + 1).translate((0, 0, -Lc - Lb - 0.5)))
    return body.union(shank).union(ridge)


def mating(p: dict) -> dict[str, cq.Workplane]:
    t = p["lip_thickness_mm"]
    tube_len = p["sleeve_length_mm"] + p["fairing_length_mm"] + p["root_chord_mm"]
    tube = (cq.Workplane("XY").circle(p["tube_od_mm"] / 2).circle(p["tube_id_mm"] / 2)
            .extrude(tube_len).translate((0, 0, t)))
    motor = cq.Workplane("XY").circle(p["motor_case_od_mm"] / 2).extrude(p["motor_length_mm"])
    ring = (cq.Workplane("XY").circle(p["thrust_ring_od_mm"] / 2).extrude(p["thrust_ring_thk_mm"])
            .translate((0, 0, -p["thrust_ring_thk_mm"])))
    m = {"tube_wall": tube, "motor_case": motor, "motor_thrust_ring": ring}
    if p.get("tail_cone"):
        m["tail_cone"] = tail_cone_installed(p)
    return m


def extras(p: dict, out_dir: Path, stem: str) -> list[Path]:
    return fin_can.extras(p, out_dir, stem)
