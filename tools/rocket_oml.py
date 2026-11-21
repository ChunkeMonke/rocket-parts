"""Outer-mold-line (OML) solid of the whole rocket, for 3D CFD (Fluent): nose + tube + fin can.

  .venv/bin/python tools/rocket_oml.py [--project l1-cheap] [--rev 6]

Aft face at z = 0, nose tip at +Z, units mm. Solid and watertight; internal parts (motor, bore) are filled.
Geometry sources: design.yaml nosecone: (tangent ogive length, base OD) and stability.body_tube_length_mm;
fin can = parts/fin_can_md.py with the current design.yaml (fins from aero:).
Writes out/cfd/rocket_oml.step and .stl, plus a side-view PNG.
"""
from __future__ import annotations

import argparse
import math
import sys
from pathlib import Path

import cadquery as cq
import yaml

ROOT = Path(__file__).resolve().parent.parent
TIP_FLAT_R_MM = 0.3   # CFD meshing convention (sharp tips make degenerate cells); not a part dimension
sys.path.insert(0, str(ROOT))
from parts import fin_can, fin_can_md  # noqa: E402


def ogive_profile(R: float, L: float, n: int = 200) -> list[tuple[float, float]]:
    """Tangent ogive (r, x) points from tip (x = 0) to base (x = L)."""
    rho = (R * R + L * L) / (2 * R)
    pts = []
    for i in range(n + 1):
        x = L * i / n
        r = math.sqrt(max(rho * rho - (L - x) ** 2, 0.0)) + R - rho
        pts.append((max(r, 0.0), x))
    return pts


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--project", default="l1-cheap")
    a = ap.parse_args()
    d = yaml.safe_load((ROOT / "projects" / a.project / "design.yaml").read_text())
    p = fin_can_md.params(a.project)
    R = p["tube_od_mm"] / 2
    L_nose = float(d["nosecone"]["length_mm"])
    L_tube = float(d["stability"]["body_tube_length_mm"])
    z0 = p["lip_thickness_mm"]                       # tube starts on top of the lip
    z_nose = z0 + L_tube

    body = cq.Workplane("XY").circle(R).extrude(z_nose)          # solid tube + filled bore/motor
    prof = ogive_profile(R, L_nose)
    # revolve in XZ: points (radius, z) with tip at top
    # meshing convention: blunt the mathematically sharp tip to a tiny flat of radius tip_flat_r_mm
    pts = [(r, z_nose + (L_nose - x)) for r, x in prof if r >= TIP_FLAT_R_MM]
    nose = (cq.Workplane("XZ").polyline([(0, pts[0][1])] + pts + [(0, z_nose)])
            .close().revolve(360, (0, 0, 0), (0, 1, 0)))
    can = fin_can_md.build(p)
    rocket = body.union(nose).union(can).union(fin_can.insert_holes(p))  # fill M3 insert holes (not aero)
    out = ROOT / "out" / "cfd"
    out.mkdir(parents=True, exist_ok=True)
    cq.exporters.export(rocket, str(out / "rocket_oml.step"))
    cq.exporters.export(rocket, str(out / "rocket_oml.stl"), tolerance=0.05, angularTolerance=0.1)
    bb = rocket.val().BoundingBox()
    print(f"OML: length {bb.zlen:.1f} mm, max XY {bb.xlen:.1f} x {bb.ylen:.1f} mm, valid={rocket.val().isValid()}")


if __name__ == "__main__":
    main()
