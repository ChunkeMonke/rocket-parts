"""Generate a Fluent-ready 2D C-domain around the fin airfoil section.

  .venv/bin/python tools/fluent_domain.py [--project l1-cheap] [--section root|tip|both]
         [--farfield-chords 20] [--wake-chords 20]

Uses parts/fin_can.py (same NACA section, thickness and TE as the printed fin) and writes, per section,
to out/cfd/:
  <section>_domain.step   2D surface body (XY plane, z = 0, mm). Its edges are split so you can name
                          airfoil_upper, airfoil_lower, airfoil_te, farfield_inlet (arc),
                          farfield_top, farfield_bottom, outlet
  <section>_airfoil.csv   x, y points (mm) of the closed section
  <section>_domain.png    full domain + close-up, for checking
  fluent_setup.md         setup sheet with first-cell-height estimates
Domain-size defaults (20 chords) follow common external-aero CFD practice; change them on the command line.
"""
from __future__ import annotations

import argparse
import math
import sys
from pathlib import Path

import cadquery as cq
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from parts import fin_can  # noqa: E402


def section_xy(p: dict, chord: float) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Upper and lower surfaces, LE at (0, 0), TE at x = chord; blunt TE as in the printed fin."""
    x = fin_can.chord_stations(p["airfoil_points"])
    yt = fin_can.naca_half_thickness(x, p["fin_thickness_mm"], p["te_thickness_mm"])
    return x * chord, yt, -yt


def build_domain(p: dict, chord: float, ff: float, wake: float):
    xs, yu, yl = section_xy(p, chord)
    up = [cq.Vector(a, b, 0) for a, b in zip(xs, yu)]
    lo = [cq.Vector(a, b, 0) for a, b in zip(xs, yl)]
    e_up = cq.Edge.makeSpline(up)
    e_lo = cq.Edge.makeSpline(lo)
    e_te = cq.Edge.makeLine(up[-1], lo[-1])
    airfoil = cq.Wire.assembleEdges([e_up, e_te, e_lo])

    R = ff * chord
    xc = chord                     # arc centred on the TE; wake box from TE to TE + wake
    xo = chord + wake * chord
    e_arc = cq.Edge.makeThreePointArc(cq.Vector(xc, R, 0), cq.Vector(xc - R, 0, 0), cq.Vector(xc, -R, 0))
    e_bot = cq.Edge.makeLine(cq.Vector(xc, -R, 0), cq.Vector(xo, -R, 0))
    e_out = cq.Edge.makeLine(cq.Vector(xo, -R, 0), cq.Vector(xo, R, 0))
    e_top = cq.Edge.makeLine(cq.Vector(xo, R, 0), cq.Vector(xc, R, 0))
    outer = cq.Wire.assembleEdges([e_arc, e_bot, e_out, e_top])
    face = cq.Face.makeFromWires(outer, [airfoil])
    return face, xs, yu, yl, (R, xc, xo)


def first_cell(u: float, chord_m: float, yplus: float = 1.0) -> dict:
    """Flat-plate estimate (ISA sea level): Re, Cf = 0.026 Re^-1/7, y = y+ * nu / u_tau."""
    rho, mu = 1.225, 1.789e-5
    re = rho * u * chord_m / mu
    cf = 0.026 / re ** (1 / 7)
    u_tau = math.sqrt(0.5 * cf * u**2)
    return {"Re": re, "y_mm": yplus * (mu / rho) / u_tau * 1000}


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--project", default="l1-cheap")
    ap.add_argument("--section", default="both", choices=["root", "tip", "both"])
    ap.add_argument("--farfield-chords", type=float, default=20)
    ap.add_argument("--wake-chords", type=float, default=20)
    a = ap.parse_args()
    p = fin_can.params(a.project)
    out = ROOT / "out" / "cfd"
    out.mkdir(parents=True, exist_ok=True)
    secs = {"root": p["root_chord_mm"], "tip": p["tip_chord_mm"]}
    if a.section != "both":
        secs = {a.section: secs[a.section]}

    rows = []
    for name, c in secs.items():
        face, xs, yu, yl, (R, xc, xo) = build_domain(p, c, a.farfield_chords, a.wake_chords)
        stem = f"fin_{name}"
        cq.exporters.export(cq.Workplane("XY").add(face), str(out / f"{stem}_domain.step"))
        pts = np.r_[np.c_[xs[::-1], yu[::-1]], np.c_[xs[1:], yl[1:]]]
        np.savetxt(out / f"{stem}_airfoil.csv", pts, delimiter=",", header="x_mm,y_mm", comments="", fmt="%.5f")
        exp_area = (math.pi * R**2 / 2 + 2 * R * (xo - xc)) - face.innerWires()[0].Length() * 0  # outer area
        print(f"{stem}: chord {c:g} mm, face area {face.Area():.1f} mm2 (outer {exp_area:.1f}), "
              f"edges {len(face.Edges())}, valid={face.isValid()}")
        fig, ax = plt.subplots(1, 2, figsize=(13, 4.5), dpi=110)
        for e in face.Edges():
            v = np.array([e.positionAt(t).toTuple()[:2] for t in np.linspace(0, 1, 200)])
            for k in (0, 1):
                ax[k].plot(v[:, 0], v[:, 1], "k-", lw=0.8)
        ax[0].set_title(f"{stem}: C-domain, R = {a.farfield_chords:g}c, wake {a.wake_chords:g}c")
        ax[1].set_xlim(-0.08 * c, 1.08 * c); ax[1].set_ylim(-0.15 * c, 0.15 * c)
        ax[1].set_title(f"airfoil close-up (chord {c:g} mm, t {p['fin_thickness_mm']:g} mm, TE {p['te_thickness_mm']:.2f} mm)")
        for k in (0, 1):
            ax[k].set_aspect("equal"); ax[k].grid(alpha=0.3); ax[k].set_xlabel("x mm"); ax[k].set_ylabel("y mm")
        fig.savefig(out / f"{stem}_domain.png", bbox_inches="tight"); plt.close(fig)
        rows.append((name, c, face.Area()))

    # flight speeds from the stability sim results in design.yaml
    import yaml
    d = yaml.safe_load((ROOT / "projects" / a.project / "design.yaml").read_text())
    vmax = float(d["stability"]["max_velocity_m_s"])
    speeds = [("rail exit", float(d["stability"]["rail_exit_velocity_m_s"]["rail_1p83m"])),
              ("~Mach 0.3", 0.3 * 340.3), ("~Mach 0.6", 0.6 * 340.3), ("Vmax", vmax)]
    lines = ["# Fluent 2D fin-section setup (generated by tools/fluent_domain.py)", "",
             f"Sections: {', '.join(f'{n} (chord {c:g} mm)' for n, c, _ in rows)}. Geometry in **mm**, XY plane.",
             "", "## Workbench steps",
             "1. Workbench → *Fluid Flow (Fluent)*. Before opening the geometry, set **Analysis Type = 2D** on the Geometry cell's properties.",
             "2. Geometry → import `fin_<section>_domain.step` (one surface body).",
             "3. Named Selections (in SpaceClaim or Meshing): `airfoil` = upper + lower + TE edges; "
             "`farfield` = arc + top + bottom (+ outlet edge, or name it `outlet` separately).",
             "4. Mesh: Face Sizing on the airfoil edges; **Inflation** on `airfoil` using the first-cell height below "
             "(growth rate ~1.2, enough layers to cover the boundary layer); refine the wake region behind the TE.",
             "5. Fluent: **density-based** solver (compressible up to Mach 0.83); material air = **ideal gas**; "
             "viscosity Sutherland; model **k-ω SST**.",
             "6. Boundaries: `farfield` = **pressure far-field** (Mach number + flow-direction components set the angle of attack: "
             "x = cos α, y = sin α); `airfoil` = wall (no slip).",
             "7. Reference values: compute from `farfield`, length = chord (m), area = chord × 1 m (2D, per unit span).",
             "8. Monitors: lift and drag coefficients (drag direction (cos α, sin α), lift (−sin α, cos α)). Run AoA 0, 2, 4, 6° at each Mach.",
             "9. **Scale:** Fluent may read the mesh in metres; check with Domain → Mesh → Scale (mm → m).", "",
             "## First-cell height for y+ ≈ 1 (ESTIMATE: flat-plate Cf = 0.026 Re^-1/7, ISA sea level)", "",
             "| Condition | V (m/s) | Section | Re | first cell (mm) |", "|---|---|---|---|---|"]
    for lbl, v in speeds:
        for n, c, _ in rows:
            fc = first_cell(v, c / 1000)
            lines.append(f"| {lbl} | {v:.1f} | {n} | {fc['Re']:.2e} | {fc['y_mm']:.4f} |")
    lines += ["", "Re and y+ are estimates; check the y+ contour on the airfoil after the first solve and adjust.",
              "The 2D section ignores span and root/tip effects. For those, use `fin_can_rev2_fin_only.step` in 3D."]
    (out / "fluent_setup.md").write_text("\n".join(lines) + "\n")
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
