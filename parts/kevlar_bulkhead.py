"""Aft Kevlar anchor bulkhead, rev 1: printed baffle epoxied inside the LOC BT-1.52 body tube.

Two vented plates (aft and forward) with vents staggered by 30 deg form a baffle: ejection gas passes, hot particles
do not reach the chute. A central pillar ties the plates; the Kevlar runs down one 5 mm hole, round the pillar and up the
other, and is knotted on the forward face. The outside is a snug fit in the tube (0.09 mm per side) with two epoxy key
grooves and a lead-in chamfer at the aft (insertion) end.

Frame: aft face z = 0 (towards the motor), forward face z = length (towards the nose). Printed AFT FACE DOWN, no
supports (forward plate bridges at most 13 mm between pillar and wall).
"""
from __future__ import annotations

import math

import cadquery as cq
import yaml


INFO = {
    "print_orientation": "Aft face (z = 0) on the bed, axis vertical. No supports: the forward plate bridges "
                         "about 13 mm between the pillar and the wall. 0.20 mm layers, 6 walls (fully solid).",
    "loads": [
        "Kevlar snatch load (axial, forward): ≤ 686 N at 20 m/s separation (recovery analysis); 343 N at 10 m/s.",
        "Path: cord bears on the underside of the forward plate around the pillar; the pillar shares it with the aft "
        "plate. Plate bending is in-plane (within layers). Pillar-to-aft-plate joint is across layers (tension).",
        "Bond: epoxy shear on the outer surface, 3153 mm²; at 1 MPa (paper-ply limit, conservative) capacity ≈ 3.1 kN.",
        "Ejection pressure acts on both plates; the vents relieve it.",
    ],
}


def _val(d, k):
    v = d[k]
    return v["value"] if isinstance(v, dict) else v


def params(project: str = "l1-cheap") -> dict:
    from pathlib import Path
    root = Path(__file__).resolve().parent.parent
    d = yaml.safe_load((root / "projects" / project / "design.yaml").read_text())
    b = d["kevlar_bulkhead"]
    p = {k: _val(b, k) for k in ("od_mm", "wall_mm", "length_mm", "aft_plate_mm", "gap_mm", "fwd_plate_mm",
                                  "pillar_d_mm", "install_fwd_face_from_tip_mm")}
    p.update(tube_id_mm=38.735, tube_od_mm=41.275, aft_vent_d_mm=7.0, aft_vent_r_mm=11.5, fwd_vent_d_mm=6.0,
             fwd_vent_r_mm=12.5, kevlar_hole_d_mm=5.0, kevlar_hole_spacing_mm=14.0, groove_w_mm=1.5,
             groove_depth_mm=0.5, chamfer_mm=0.8, target_mass_g=15.2)   # model mass, fully solid at 6 walls
    return p


def build(p: dict) -> cq.Workplane:
    R, Ri, L = p["od_mm"] / 2, p["od_mm"] / 2 - p["wall_mm"], p["length_mm"]
    ta, g, tf = p["aft_plate_mm"], p["gap_mm"], p["fwd_plate_mm"]
    body = cq.Workplane("XY").circle(R).circle(Ri).extrude(L)
    plates = (cq.Workplane("XY").circle(Ri + 0.01).extrude(ta)
              .union(cq.Workplane("XY").workplane(offset=ta + g).circle(Ri + 0.01).extrude(tf)))
    pillar = cq.Workplane("XY").workplane(offset=ta - 0.01).circle(p["pillar_d_mm"] / 2).extrude(g + 0.02)
    part = body.union(plates).union(pillar)
    # vents (aft: 0/60/.., fwd: staggered 30 deg)
    for k in range(6):
        a = math.radians(60 * k)
        part = part.cut(cq.Workplane("XY").workplane(offset=-1).center(p["aft_vent_r_mm"] * math.cos(a), p["aft_vent_r_mm"] * math.sin(a))
                        .circle(p["aft_vent_d_mm"] / 2).extrude(ta + 2))
        b = math.radians(60 * k + 30)
        part = part.cut(cq.Workplane("XY").workplane(offset=ta + g - 1).center(p["fwd_vent_r_mm"] * math.cos(b), p["fwd_vent_r_mm"] * math.sin(b))
                        .circle(p["fwd_vent_d_mm"] / 2).extrude(tf + 2))
    # Kevlar holes through the forward plate, either side of the pillar, with edge chamfers
    s = p["kevlar_hole_spacing_mm"] / 2
    for x in (-s, s):
        hole = cq.Workplane("XY").workplane(offset=ta + g - 1).center(x, 0).circle(p["kevlar_hole_d_mm"] / 2).extrude(tf + 2)
        part = part.cut(hole)
        for z0, z1 in ((ta + g, ta + g + 0.5), (ta + g + tf - 0.5, ta + g + tf)):
            r_lo = p["kevlar_hole_d_mm"] / 2 + (0.5 if z0 == ta + g else 0.0)
            r_hi = p["kevlar_hole_d_mm"] / 2 + (0.0 if z0 == ta + g else 0.5)
            cone = cq.Workplane("XY").add(cq.Solid.makeLoft([
                cq.Wire.makeCircle(r_lo, cq.Vector(x, 0, z0), cq.Vector(0, 0, 1)),
                cq.Wire.makeCircle(r_hi, cq.Vector(x, 0, z1), cq.Vector(0, 0, 1))]))
            part = part.cut(cone)
    # epoxy key grooves on the outside, and a lead-in chamfer at the aft (insertion) end
    for zc in (L * 0.3, L * 0.7):
        ring = (cq.Workplane("XY").workplane(offset=zc - p["groove_w_mm"] / 2).circle(R + 1)
                .circle(R - p["groove_depth_mm"]).extrude(p["groove_w_mm"]))
        part = part.cut(ring)
    c = p["chamfer_mm"]
    lead = cq.Workplane("XY").add(cq.Solid.makeLoft([
        cq.Wire.makeCircle(R + 1, cq.Vector(0, 0, -0.01), cq.Vector(0, 0, 1)),
        cq.Wire.makeCircle(R + 1, cq.Vector(0, 0, c), cq.Vector(0, 0, 1))]))
    keep = cq.Workplane("XY").add(cq.Solid.makeLoft([
        cq.Wire.makeCircle(R - c, cq.Vector(0, 0, -0.02), cq.Vector(0, 0, 1)),
        cq.Wire.makeCircle(R + 0.001, cq.Vector(0, 0, c), cq.Vector(0, 0, 1))]))
    part = part.cut(lead.cut(keep))
    return part


def mating(p: dict) -> dict[str, cq.Workplane]:
    """Body tube around the bulkhead (ID 38.735 measured, OD 41.275), over the bulkhead length + 10 mm each side."""
    L = p["length_mm"]
    tube = (cq.Workplane("XY").workplane(offset=-10).circle(p["tube_od_mm"] / 2).circle(p["tube_id_mm"] / 2)
            .extrude(L + 20))
    return {"body_tube": tube}
