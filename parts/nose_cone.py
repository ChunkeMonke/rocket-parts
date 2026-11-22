"""Nose cone, rev 1 (l1-cheap): tangent ogive + shoulder, ballast pocket in the tip closed by a screw-in plug,
empty payload bay behind it, screw-on bottom cap (Kevlar anchor) in a printed thread at the shoulder's aft end.

Coordinates (as printed, TIP UP): Z = rocket axis, z = 0 is the shoulder's AFT face on the build plate.
The shoulder runs z = 0 .. shoulder_length, the ogive from there to the tip.

Parameters (projects/<project>/design.yaml `nosecone:` + `nosecone.part:`; all mm unless noted):
  length_mm                exposed ogive length, tip to shoulder step
  base_od_mm               ogive base OD (= tube OD)
  shoulder_length_mm, shoulder_od_mm
  wall_thickness_mm        cone and shoulder wall (normal to the surface)
  ballast_bulkhead_from_tip_mm, ballast_bulkhead_thickness_mm   internal bulkhead closing the tip pocket (its forward face)
  plug_bore_d_mm           threaded fill hole in the bulkhead (thread minor diameter)
  plug_head_d_mm, plug_head_thickness_mm, plug_slot_width_mm, plug_slot_depth_mm
  cap_bore_d_mm            threaded ring bore at the aft end (thread minor diameter) = payload access
  cap_ring_height_mm       height of the internal thread ring
  cap_flange_thickness_mm, cap_shank_length_mm, cap_wall_mm
  kevlar_hole_d_mm, kevlar_hole_spacing_mm
  thread_pitch_mm, thread_depth_mm, thread_clearance_mm   printed 45-degree trapezoid thread
  ogive_points             profile resolution (count)
  tip_flat_r_mm            tip ends in a flat of this radius (= outer line width) so the mesh has no degenerate apex
  target_mass_g        g   verify check 2 target
"""
from __future__ import annotations

import math
from pathlib import Path

import cadquery as cq
import yaml

from parts.shop import const

ROOT = Path(__file__).resolve().parent.parent

INFO = {
    "print_orientation": "TIP UP, shoulder's aft face on the bed. No supports: the ballast bulkhead's underside is a 45° cone, "
                         "the thread ring top is an up-facing ledge, thread flanks are 45°.",
    "loads": [
        "Recovery snatch: the Kevlar pulls the cap aft (-Z); the cap thread shears the ring across layers "
        "(about pi x 30 x 15 x 0.5 = 700 mm2 x 15 MPa = ~10 kN), then the shoulder wall carries it forward in Z tension "
        "across layers (251 mm2, 15 MPa reference -> 3.77 kN, nosecone.md section 4). Wall is the weak link.",
        "Ballast at landing/deploy: pushes the plug forward... no: inertia pushes ballast AFT onto the bulkhead (+plug) in "
        "compression/bending within layers; the bulkhead's 45° cone carries it to the wall.",
    ],
}


def params(project: str = "l1-cheap") -> dict:
    d = yaml.safe_load((ROOT / "projects" / project / "design.yaml").read_text())
    n = d["nosecone"]
    pt = n["part"]
    p = {k: n[k] for k in ("length_mm", "base_od_mm", "shoulder_length_mm", "shoulder_od_mm", "wall_thickness_mm")}
    p.update({k: v for k, v in pt.items() if k != "target_mass_g"})
    p["ogive_points"] = 60
    p["tip_flat_r_mm"] = const("print_profile_petg.line_width_mm")["outer_wall"]   # tip ends in a one-line-wide flat
    p["target_mass_g"] = pt["target_mass_g"]["nose_cone"]
    p["_targets"] = pt["target_mass_g"]
    return p


# ---------------------------------------------------------------- profiles
def ogive_r(p: dict, x: float) -> float:
    """Outer radius (mm) at distance x (mm) aft of the tip, tangent ogive."""
    R, L = p["base_od_mm"] / 2, p["length_mm"]
    rho = (R * R + L * L) / (2 * R)
    return math.sqrt(max(rho * rho - (L - x) ** 2, 0.0)) + R - rho


def z_of_tip(p: dict) -> float:
    return p["shoulder_length_mm"] + p["length_mm"]


def outer_pts(p: dict) -> list[tuple[float, float]]:
    zs, L, n = p["shoulder_length_mm"], p["length_mm"], p["ogive_points"]
    pts = [(0.0, 0.0), (p["shoulder_od_mm"] / 2, 0.0), (p["shoulder_od_mm"] / 2, zs)]
    for i in range(n + 1):
        x = L * (1 - i / n)                       # base -> tip
        if ogive_r(p, x) >= p["tip_flat_r_mm"]:
            pts.append((ogive_r(p, x), zs + L - x))
    lo, hi = 0.0, L                                   # exact x where r = tip_flat_r (bisection)
    for _ in range(60):
        mid = (lo + hi) / 2
        lo, hi = (mid, hi) if ogive_r(p, mid) < p["tip_flat_r_mm"] else (lo, mid)
    pts.append((p["tip_flat_r_mm"], zs + L - hi))
    pts.append((0.0, zs + L - hi))
    return pts


def inner_pts(p: dict) -> list[tuple[float, float]]:
    """Cavity profile: the ogive offset inward by the wall (along the surface normal), then the shoulder bore."""
    zs, L, n, w = p["shoulder_length_mm"], p["length_mm"], p["ogive_points"], p["wall_thickness_mm"]
    R, rho = p["base_od_mm"] / 2, (p["base_od_mm"] ** 2 / 4 + L * L) / p["base_od_mm"]
    pts = []
    for i in range(n + 1):
        x = L * (1 - i / n)
        slope = (L - x) / math.sqrt(rho * rho - (L - x) ** 2)   # dr/dx
        th = math.atan(slope)
        r = ogive_r(p, x) - w * math.cos(th)
        z = zs + L - x - w * math.sin(th)
        if r <= 0.3:
            break
        pts.append((r, z))
    r_sb = p["shoulder_od_mm"] / 2 - w
    base_r = pts[0][0]
    prof = [(0.0, -1.0), (r_sb, -1.0), (r_sb, zs - (r_sb - base_r) if r_sb > base_r else zs)]
    prof += [(min(r, r_sb), z) for r, z in pts]
    prof.append((0.0, pts[-1][1]))
    return prof


def revolve(pts: list[tuple[float, float]]) -> cq.Workplane:
    pts = [q for i, q in enumerate(pts) if i == 0 or math.dist(q, pts[i - 1]) > 1e-6]
    return cq.Workplane("XZ").polyline(pts).close().revolve(360, (0, 0, 0), (0, 1, 0))


# ---------------------------------------------------------------- threads
def _helix_sweep(prof: list[tuple[float, float]], r_ref: float, pitch: float, z0: float, height: float) -> cq.Workplane:
    """Sweep a thread profile [(r, dz)] along a helix starting at angle 0, axial position z0."""
    helix = cq.Wire.makeHelix(pitch, height, r_ref, center=cq.Vector(0, 0, z0))
    sec = cq.Workplane("XZ").polyline([(r, z0 + dz) for r, dz in prof]).close()
    return sec.sweep(cq.Workplane("XY").add(helix), isFrenet=True)


def groove(p: dict, r_bore: float, z0: float, height: float) -> cq.Workplane:
    """Female thread groove (to CUT) in a bore of minor radius r_bore. 45° flanks."""
    h = p["thread_depth_mm"]
    hw = (p["thread_pitch_mm"] - 0.3) / 2                    # half-width at the bore (0.3 mm land between turns)
    # the flank runs 0.1 mm inside the bore so no groove face is coincident with the bore cylinder (OCC cut fails silently)
    prof = [(r_bore - 0.1, -(hw + 0.1)), (r_bore + h, -(hw - h)), (r_bore + h, hw - h), (r_bore - 0.1, hw + 0.1)]
    return _helix_sweep(prof, r_bore, p["thread_pitch_mm"], z0, height)


def ridge(p: dict, r_bore: float, z0: float, height: float) -> cq.Workplane:
    """Male thread ridge (to ADD) mating a groove in bore r_bore: thread_clearance_mm radial at the root and normal to
    the 45° flanks; the crest is truncated to a 0.4 mm flat (one printed line)."""
    h, c = p["thread_depth_mm"], p["thread_clearance_mm"]
    hw = (p["thread_pitch_mm"] - 0.3) / 2 - c * math.sqrt(2)   # axial half-width at r_bore
    crest = 0.2
    r_s, r_t = r_bore - c, r_bore + min(h - c, hw - crest)
    prof = [(r_s - 0.3, -hw), (r_bore, -hw), (r_t, -crest), (r_t, crest), (r_bore, hw), (r_s - 0.3, hw)]
    return _helix_sweep(prof, r_bore, p["thread_pitch_mm"], z0, height)


# ---------------------------------------------------------------- layout (installed coordinates = nose print coords)
def layout(p: dict) -> dict:
    zt = z_of_tip(p)
    zb_top = zt - p["ballast_bulkhead_from_tip_mm"]
    pitch = p["thread_pitch_mm"]
    zb_bot = zb_top - p["ballast_bulkhead_thickness_mm"]
    return dict(z_tip=zt, zb_top=zb_top, zb_bot=zb_bot,
                g_plug_z0=zb_bot,      # plug-hole groove helix start: opens on the bulkhead's aft face, ends inside
                g_cap_z0=0.0)          # cap-ring groove helix start: opens on the shoulder's aft face, ends inside the ring
    # (a groove that runs out through BOTH faces tessellates non-manifold; ending it inside the wall is clean)


def nose_body(p: dict) -> cq.Workplane:
    L = layout(p)
    w = p["wall_thickness_mm"]
    outer = revolve(outer_pts(p))
    body = outer.cut(revolve(inner_pts(p)))
    # thread ring at the aft end of the shoulder
    r_sb = p["shoulder_od_mm"] / 2 - w
    ring = cq.Workplane("XY").circle(r_sb + 0.2).circle(p["cap_bore_d_mm"] / 2).extrude(p["cap_ring_height_mm"])
    body = body.union(ring)
    body = body.cut(groove(p, p["cap_bore_d_mm"] / 2, L["g_cap_z0"], p["cap_ring_height_mm"] - p["thread_pitch_mm"]))
    # ballast bulkhead: flat top at zb_top, flat landing for the plug head, 45° cone underside out to the wall
    r_hole, r_land = p["plug_bore_d_mm"] / 2, p["plug_head_d_mm"] / 2 + 1.0
    r_far = p["base_od_mm"] / 2 + 1.0
    prof = [(r_hole, L["zb_bot"]), (r_land, L["zb_bot"]), (r_far, L["zb_bot"] - (r_far - r_land)),
            (r_far, L["zb_top"]), (r_hole, L["zb_top"])]
    bulk = revolve(prof).intersect(outer)
    body = body.union(bulk)
    body = body.cut(groove(p, r_hole, L["g_plug_z0"], p["ballast_bulkhead_thickness_mm"] - p["thread_pitch_mm"]))
    return body


def cap_installed(p: dict) -> cq.Workplane:
    """Cap in nose coordinates: flange below z = 0, shank up into the thread ring."""
    tf, ls, wc = p["cap_flange_thickness_mm"], p["cap_shank_length_mm"], p["cap_wall_mm"]
    c, pitch = p["thread_clearance_mm"], p["thread_pitch_mm"]
    r_shank = p["cap_bore_d_mm"] / 2 - c
    cap = cq.Workplane("XY").circle(p["shoulder_od_mm"] / 2).extrude(tf).translate((0, 0, -tf))
    cap = cap.union(cq.Workplane("XY").circle(r_shank).circle(r_shank - wc).extrude(ls))
    turns_h = math.floor((ls - pitch / 2) / pitch) * pitch - pitch      # ridge centre-line from z = pitch upward
    cap = cap.union(ridge(p, p["cap_bore_d_mm"] / 2, pitch, turns_h).intersect(
        cq.Workplane("XY").circle(r_shank + 2).extrude(ls)))
    s = p["kevlar_hole_spacing_mm"] / 2
    holes = (cq.Workplane("XY").pushPoints([(-s, 0), (s, 0)]).circle(p["kevlar_hole_d_mm"] / 2)
             .extrude(tf + 2).translate((0, 0, -tf - 1)))
    return cap.cut(holes)


def plug_installed(p: dict) -> cq.Workplane:
    """Plug in nose coordinates: head under the bulkhead landing, threaded shank up into the fill hole."""
    L = layout(p)
    c, pitch, th = p["thread_clearance_mm"], p["thread_pitch_mm"], p["plug_head_thickness_mm"]
    r_shank = p["plug_bore_d_mm"] / 2 - c
    tb = p["ballast_bulkhead_thickness_mm"]
    z0 = L["zb_bot"]
    head = cq.Workplane("XY").circle(p["plug_head_d_mm"] / 2).extrude(th).translate((0, 0, z0 - th - c))
    shank = cq.Workplane("XY").circle(r_shank).extrude(tb - 0.5).translate((0, 0, z0 - c))
    plug = head.union(shank)
    turns_h = math.floor((tb - pitch / 2) / pitch) * pitch
    plug = plug.union(ridge(p, p["plug_bore_d_mm"] / 2, z0, turns_h).intersect(
        cq.Workplane("XY").circle(r_shank + 2).extrude(tb - 0.5).translate((0, 0, z0 - c))))
    slot = (cq.Workplane("XY").rect(p["plug_head_d_mm"] + 2, p["plug_slot_width_mm"]).extrude(p["plug_slot_depth_mm"])
            .translate((0, 0, z0 - th - c)))
    return plug.cut(slot)


# ---------------------------------------------------------------- part API (the nose shell)
def build(p: dict) -> cq.Workplane:
    return nose_body(p)


def mating(p: dict) -> dict[str, cq.Workplane]:
    zs = p["shoulder_length_mm"]
    tube_od = p["base_od_mm"]
    tube_id = p["shoulder_od_mm"] + 2 * 0.09 + 0.0   # = tube id_measured (shoulder = id - 2 x snug_slip)
    tube = cq.Workplane("XY").circle(tube_od / 2).circle(tube_id / 2).extrude(zs + 60).translate((0, 0, -60))
    return {"tube_wall": tube, "bottom_cap": cap_installed(p), "ballast_plug": plug_installed(p)}


def extras(p: dict, out_dir: Path, stem: str) -> list[Path]:
    return []
