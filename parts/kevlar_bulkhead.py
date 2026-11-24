"""Aft Kevlar anchor bulkhead, rev 2: printed, epoxied inside the LOC BT-1.52 body tube.

Rev 2 (2026-11-24) replaces the rev 1 two-plate baffle: its Kevlar had to be threaded round a pillar inside a closed
chamber, and slicer supports would have been trapped there. Rev 2 is a single vented plate with an open Kevlar EYE on
the forward face: the cord passes straight through a 6 mm tunnel and is knotted. The tunnel roof is a 45 deg diamond,
so the part prints without supports and has no enclosed cavity. The LOC reusable wadding protects the chute.

Frame: aft face z = 0 (towards the motor), forward edge z = length (towards the nose). Printed AFT FACE DOWN.
Tunnel axis = Y. Vents avoid the eye footprint.
"""
from __future__ import annotations

import math
from pathlib import Path

import cadquery as cq
import yaml

INFO = {
    "print_orientation": "Aft face (z = 0) on the bed, axis vertical, NO supports: the eye tunnel has a 45° diamond "
                         "roof and there is no enclosed cavity. 0.20 mm layers, 6 walls.",
    "loads": [
        "Kevlar snatch load (axial, forward): ≤ 686 N at 20 m/s separation (recovery analysis); 343 N at 10 m/s.",
        "Eye bar: 6 mm span, 6 mm deep above the apex, 12 mm long; bending ≈ 14 MPa at 686 N, within layers.",
        "Eye posts: 2 × 5 × 12 mm = 120 mm² in tension ACROSS layers: 5.7 MPa at 686 N (PETG interlayer ≈ 15–20 MPa).",
        "Plate: 6 mm, in-plane bending ≈ 10 MPa at 686 N. Bond: epoxy shear on ≈ 2900 mm² ≈ 2.9 kN at 1 MPa.",
    ],
}


def _val(d, k):
    v = d[k]
    return v["value"] if isinstance(v, dict) else v


def params(project: str = "l1-cheap") -> dict:
    root = Path(__file__).resolve().parent.parent
    d = yaml.safe_load((root / "projects" / project / "design.yaml").read_text())
    b = d["kevlar_bulkhead_rev2"]
    p = {k: _val(b, k) for k in ("od_mm", "wall_mm", "length_mm", "plate_mm", "eye_tunnel_w_mm", "eye_tunnel_h_mm",
                                  "eye_bar_mm", "eye_post_mm", "eye_length_mm", "install_fwd_face_from_tip_mm")}
    p.update(tube_id_mm=38.735, tube_od_mm=41.275, vent_d_mm=6.5, vent_r_mm=12.25, groove_w_mm=1.5,
             groove_depth_mm=0.5, chamfer_mm=0.8, edge_break_mm=1.0, target_mass_g=15.0)   # model, ~fully solid at 6 walls
    return p


def eye(p: dict) -> cq.Workplane:
    t, w, h, bar, post, le = (p["plate_mm"], p["eye_tunnel_w_mm"], p["eye_tunnel_h_mm"], p["eye_bar_mm"],
                              p["eye_post_mm"], p["eye_length_mm"])
    xo = w / 2 + post
    top = t + h + w / 2 + bar
    outer = (cq.Workplane("XZ").polyline([(-xo, t - 0.01), (xo, t - 0.01), (xo, top), (-xo, top)]).close()
             .extrude(le / 2, both=True))
    tunnel = (cq.Workplane("XZ").polyline([(-w / 2, t - 1), (w / 2, t - 1), (w / 2, t + h), (0, t + h + w / 2),
                                            (-w / 2, t + h)]).close().extrude(le / 2 + 1, both=True))
    e = outer.cut(tunnel)
    try:   # break the tunnel-mouth edges so the cord is not cut (edges on the two end faces)
        e = e.faces(">Y").edges().chamfer(p["edge_break_mm"] * 0.6).faces("<Y").edges().chamfer(p["edge_break_mm"] * 0.6)
    except Exception:
        pass
    return e


def build(p: dict) -> cq.Workplane:
    R, Ri, L, t = p["od_mm"] / 2, p["od_mm"] / 2 - p["wall_mm"], p["length_mm"], p["plate_mm"]
    part = cq.Workplane("XY").circle(R).circle(Ri).extrude(L)
    part = part.union(cq.Workplane("XY").circle(Ri + 0.01).extrude(t))
    for k in range(6):
        a = math.radians(60 * k)
        part = part.cut(cq.Workplane("XY").workplane(offset=-1)
                        .center(p["vent_r_mm"] * math.cos(a), p["vent_r_mm"] * math.sin(a))
                        .circle(p["vent_d_mm"] / 2).extrude(t + 2))
    part = part.union(eye(p))
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
    return part.cut(lead.cut(keep))


def mating(p: dict) -> dict[str, cq.Workplane]:
    """Body tube around the bulkhead (ID 38.735 measured, OD 41.275), over the bulkhead length + 10 mm each side."""
    L = p["length_mm"]
    tube = (cq.Workplane("XY").workplane(offset=-10).circle(p["tube_od_mm"] / 2).circle(p["tube_id_mm"] / 2)
            .extrude(L + 20))
    return {"body_tube": tube}
