"""Rev 8 tail cone: screws into the fin can's threaded collar, traps the motor thrust ring (motor retainer) and
forms a 20 mm boattail (46.8 -> 43 mm). Geometry and parameters: parts/fin_can_md.py (`tail_cone_installed`).

Coordinates (as printed): narrow aft end DOWN on the bed, threaded shank up; z = 0 is the aft (narrow) face.
Parameters (design.yaml `fin_can_md:`): collar_length_mm, collar_bore_d_mm, boattail_length_mm, boattail_end_od_mm,
tail_cone_bore_d_mm, thread_pitch_mm, thread_depth_mm, thread_clearance_mm, thrust_ring_thk_mm (all mm).
"""
from __future__ import annotations

import cadquery as cq

from parts import fin_can_md as F

INFO = {
    "print_orientation": "Narrow aft end on the bed, shank up. No supports: the outer taper leans 5.4 deg outward, "
                         "thread flanks are 45 deg.",
    "loads": [
        "Tail-first landing: the cone is pushed forward; load goes through the shank onto the thrust ring and "
        "motor into the fin can lip (compression across layers).",
        "Ejection kick: the motor pulls the ring aft onto the shank face; the thread shears across layers "
        "(about pi x 41.6 x 6.5 x 0.5 = 425 mm2 x 15 MPa = ~6 kN).",
        "HEAT: the cone bore surrounds the nozzle exit during the 2.4 s burn. PETG softens near 80 C; "
        "print this part in ABS/ASA or line the bore with aluminium tape.",
    ],
}


def _shift(p: dict) -> float:
    return p["collar_length_mm"] + p["boattail_length_mm"]


def params(project: str = "l1-cheap") -> dict:
    p = F.params(project)
    p["target_mass_g"] = None
    return p


def build(p: dict) -> cq.Workplane:
    return F.tail_cone_installed(p).translate((0, 0, _shift(p)))


def mating(p: dict) -> dict[str, cq.Workplane]:
    s = _shift(p)
    m = {k: v.translate((0, 0, s)) for k, v in F.mating(p).items() if k != "tail_cone"}
    m["fin_can"] = F.build(p).translate((0, 0, s))
    return m
