"""Nose cone ballast plug, rev 1: screws into the ballast bulkhead's fill hole from the payload-bay side.

Printed HEAD DOWN (slot on the bed). Parameters: see parts/nose_cone.py.
"""
from __future__ import annotations

import cadquery as cq

from parts import nose_cone as N

INFO = {
    "print_orientation": "Head on the bed (screwdriver slot down), threaded shank up. No supports.",
    "loads": ["Ballast inertia pushes aft on the plug; the thread carries it to the bulkhead."],
}


def _shift(p: dict) -> float:
    return -(N.layout(p)["zb_bot"] - p["plug_head_thickness_mm"] - p["thread_clearance_mm"])


def params(project: str = "l1-cheap") -> dict:
    p = N.params(project)
    p["target_mass_g"] = p["_targets"]["nose_plug"]
    return p


def build(p: dict) -> cq.Workplane:
    return N.plug_installed(p).translate((0, 0, _shift(p)))


def mating(p: dict) -> dict[str, cq.Workplane]:
    return {"nose_cone": N.nose_body(p).translate((0, 0, _shift(p)))}
