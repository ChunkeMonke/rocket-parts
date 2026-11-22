"""Nose cone bottom cap, rev 1: screws into the shoulder's aft thread ring; Kevlar anchor (two holes in the floor).

Printed FLANGE DOWN (as installed, flipped: flange on the bed, threaded shank up). Parameters: see parts/nose_cone.py.
"""
from __future__ import annotations

import cadquery as cq

from parts import nose_cone as N

INFO = {
    "print_orientation": "Flange on the bed, threaded shank up. No supports (45° thread flanks).",
    "loads": ["Snatch: Kevlar pulls the floor web aft; the floor bends within its layers; the thread carries it to the nose ring."],
}


def params(project: str = "l1-cheap") -> dict:
    p = N.params(project)
    p["target_mass_g"] = p["_targets"]["nose_cap"]
    return p


def build(p: dict) -> cq.Workplane:
    return N.cap_installed(p).translate((0, 0, p["cap_flange_thickness_mm"]))


def mating(p: dict) -> dict[str, cq.Workplane]:
    return {"nose_cone": N.nose_body(p).translate((0, 0, p["cap_flange_thickness_mm"]))}
