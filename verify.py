"""Geometry QA for generated parts. Every part must pass before it is called good.

Checks (constants come from skills/SKILL.md via parts.shop):
  1 mesh     watertight, manifold (consistent winding, positive volume), exactly one body
  2 mass     slicer-style walls + top/bottom shells solid, interior at infill %.
             PASS when the declared target mass is reachable with 0-100 % infill
             (within verify.mass_tolerance_pct); reports the infill % that hits it
  3 mating   boolean intersection volume with each declared mating solid == 0
  4 renders  iso, front and axial-section PNGs written (a human/agent must still LOOK)
  5 volume   bounding box (print orientation) within printer.bambu_p1s max X/Y/Z

CLI:  python verify.py part.stl --target-mass 52.7 --mate tube=tube.stl --out out/x
"""
from __future__ import annotations

import argparse
import json
import math
from dataclasses import dataclass, field
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import trimesh  # noqa: E402
from mpl_toolkits.mplot3d.art3d import Poly3DCollection  # noqa: E402
from shapely.geometry import MultiPolygon, Polygon  # noqa: E402
from shapely.ops import unary_union  # noqa: E402

from parts.shop import const  # noqa: E402

INTERFERENCE_EPS_MM3 = 1e-3  # numerical noise floor for boolean volumes, not a design value


@dataclass
class Check:
    num: int
    name: str
    passed: bool
    detail: str
    data: dict = field(default_factory=dict)


# ---------------------------------------------------------------- 1. mesh
def check_mesh(mesh: trimesh.Trimesh) -> Check:
    bodies = mesh.split(only_watertight=False)
    ok = bool(mesh.is_watertight and mesh.is_winding_consistent and mesh.volume > 0 and len(bodies) == 1)
    return Check(1, "mesh integrity", ok,
                 f"watertight={mesh.is_watertight}, winding_consistent={mesh.is_winding_consistent}, "
                 f"volume={mesh.volume:.1f} mm3, bodies={len(bodies)}",
                 {"bodies": len(bodies), "volume_mm3": float(mesh.volume)})


# ---------------------------------------------------------------- 2. mass
def _layer_polys(mesh: trimesh.Trimesh, zs: np.ndarray) -> list:
    secs = mesh.section_multiplane(plane_origin=[0, 0, 0], plane_normal=[0, 0, 1], heights=zs)
    out = []
    for s in secs:
        if s is None:
            out.append(Polygon())
        else:
            out.append(unary_union([p.buffer(0) for p in s.polygons_full]) if s.polygons_full else Polygon())
    return out


def print_shell_params() -> dict:
    lw = const("print_profile_petg.line_width_mm")
    loops = const("print_profile_petg.wall_loops")
    h = const("print_profile_petg.layer_height_mm")
    top_t = max(const("print_profile_petg.top_shell_layers") * h, const("print_profile_petg.top_shell_thickness_mm"))
    bot_t = max(const("print_profile_petg.bottom_shell_layers") * h, const("print_profile_petg.bottom_shell_thickness_mm"))
    return {
        "wall_mm": lw["outer_wall"] + (loops - 1) * lw["inner_wall"],
        "layer_mm": h,
        "n_top": math.ceil(round(top_t / h, 6)),
        "n_bottom": math.ceil(round(bot_t / h, 6)),
    }


def mass_model(mesh: trimesh.Trimesh) -> dict:
    """Slice like a slicer: per layer, solid = perimeter band + top/bottom skins; rest = infill region."""
    sp = print_shell_params()
    zmin, zmax = mesh.bounds[:, 2]
    h = sp["layer_mm"]
    zs = np.arange(zmin + h / 2, zmax, h)
    polys = _layer_polys(mesh, zs)
    empty = Polygon()
    solid_mm3 = infill_mm3 = 0.0
    for i, a in enumerate(polys):
        if a.is_empty:
            continue
        core = a.buffer(-sp["wall_mm"], join_style=2)
        for k in range(1, sp["n_top"] + 1):
            core = core.intersection(polys[i + k] if i + k < len(polys) else empty)
        for k in range(1, sp["n_bottom"] + 1):
            core = core.intersection(polys[i - k] if i - k >= 0 else empty)
        solid_mm3 += (a.area - core.area) * h
        infill_mm3 += core.area * h
    rho = const("material.petg.density_g_cm3") / 1000.0  # g/mm3
    return {"solid_mm3": solid_mm3, "infill_region_mm3": infill_mm3,
            "mass_0pct_g": solid_mm3 * rho, "mass_100pct_g": (solid_mm3 + infill_mm3) * rho,
            "mesh_volume_mm3": float(mesh.volume), **sp}


def check_mass(mesh: trimesh.Trimesh, target_g: float | None) -> Check:
    m = mass_model(mesh)
    tol = const("verify.mass_tolerance_pct") / 100.0
    lo, hi = m["mass_0pct_g"], m["mass_100pct_g"]
    if target_g is None:
        return Check(2, "mass", False, "no target mass declared", m)
    if m["infill_region_mm3"] > 0:
        need = (target_g / (const("material.petg.density_g_cm3") / 1000.0) - m["solid_mm3"]) / m["infill_region_mm3"]
    else:
        need = float("nan")
    ok = lo <= target_g * (1 + tol) and hi >= target_g * (1 - tol)
    m["infill_needed_pct"] = None if math.isnan(need) else 100 * need
    m["target_g"] = target_g
    fill_txt = "no infill region (fully solid)" if math.isnan(need) else f"infill to hit target = {100 * need:.1f} %"
    return Check(2, "mass", ok,
                 f"target {target_g:.1f} g (±{tol * 100:.0f} %); reachable {lo:.1f} g (0 %) – {hi:.1f} g (100 %); {fill_txt}", m)


# ---------------------------------------------------------------- 3. mating
def check_mating(mesh: trimesh.Trimesh, mates: dict[str, trimesh.Trimesh]) -> Check:
    vols = {}
    for name, mate in mates.items():
        inter = trimesh.boolean.intersection([mesh, mate], engine="manifold")
        vols[name] = float(inter.volume) if inter is not None and len(inter.faces) else 0.0
    ok = bool(mates) and all(v <= INTERFERENCE_EPS_MM3 for v in vols.values())
    det = ", ".join(f"{k}: {v:.3f} mm3" for k, v in vols.items()) or "no mating geometry declared"
    return Check(3, "mating interference", ok, det, {"interference_mm3": vols})


# ---------------------------------------------------------------- 4. renders
def _draw(ax, mesh, elev, azim):
    tris = mesh.vertices[mesh.faces]
    n = mesh.face_normals
    light = np.array([0.4, -0.6, 0.7]) / np.linalg.norm([0.4, -0.6, 0.7])
    shade = 0.35 + 0.65 * np.clip(n @ light, 0, 1)
    col = np.c_[0.95 * shade, 0.55 * shade, 0.15 * shade, np.ones_like(shade)]
    ax.add_collection3d(Poly3DCollection(tris, facecolors=col, edgecolor="none"))
    lo, hi = mesh.bounds
    c, r = (lo + hi) / 2, (hi - lo).max() / 2
    ax.set_xlim(c[0] - r, c[0] + r); ax.set_ylim(c[1] - r, c[1] + r); ax.set_zlim(c[2] - r, c[2] + r)
    ax.set_box_aspect((1, 1, 1)); ax.view_init(elev=elev, azim=azim)
    ax.set_xlabel("X mm"); ax.set_ylabel("Y mm"); ax.set_zlabel("Z mm (print up)")


def render(mesh: trimesh.Trimesh, out_dir: Path, stem: str) -> Check:
    out_dir.mkdir(parents=True, exist_ok=True)
    paths = []
    for view, (elev, azim) in {"iso": (25, -60), "front": (0, -90)}.items():
        fig = plt.figure(figsize=(7, 7), dpi=110)
        _draw(fig.add_subplot(projection="3d"), mesh, elev, azim)
        fig.suptitle(f"{stem} — {view}")
        p = out_dir / f"{stem}_{view}.png"; fig.savefig(p, bbox_inches="tight"); plt.close(fig); paths.append(p)
    # section through the axis: plane y = centre, viewed along -Y
    cy = float(mesh.bounds[:, 1].mean())
    sec = mesh.section(plane_origin=[0, cy, 0], plane_normal=[0, 1, 0])
    fig, ax = plt.subplots(figsize=(7, 8), dpi=110)
    if sec is not None:
        planar, to3d = sec.to_2D(to_2D=np.array([[1, 0, 0, 0], [0, 0, 1, 0], [0, -1, 0, cy], [0, 0, 0, 1]]))
        for poly in planar.polygons_full:
            geoms = poly.geoms if isinstance(poly, MultiPolygon) else [poly]
            for g in geoms:
                ax.fill(*g.exterior.xy, color="#e8892a", alpha=0.85, lw=0.6, ec="k")
                for hole in g.interiors:
                    ax.fill(*hole.xy, color="white", lw=0.6, ec="k")
    ax.set_aspect("equal"); ax.set_xlabel("X mm"); ax.set_ylabel("Z mm (print up)")
    ax.set_title(f"{stem} — section through axis (y = {cy:.1f})"); ax.grid(alpha=0.3)
    p = out_dir / f"{stem}_section.png"; fig.savefig(p, bbox_inches="tight"); plt.close(fig); paths.append(p)
    ok = all(p.exists() and p.stat().st_size > 0 for p in paths)
    return Check(4, "renders", ok, "written: " + ", ".join(p.name for p in paths) + " — VISUAL REVIEW REQUIRED",
                 {"paths": [str(p) for p in paths]})


# ---------------------------------------------------------------- 5. build volume
def check_build_volume(mesh: trimesh.Trimesh) -> Check:
    ext = mesh.extents
    lim = np.array([const(f"printer.bambu_p1s.max_{a}_mm") for a in "xyz"])
    ok = bool(np.all(ext <= lim))
    return Check(5, "build volume", ok,
                 f"extents X {ext[0]:.1f} / Y {ext[1]:.1f} / Z {ext[2]:.1f} mm vs limit {lim[0]:.0f}/{lim[1]:.0f}/{lim[2]:.0f}",
                 {"extents_mm": ext.tolist()})


# ---------------------------------------------------------------- driver
def run(mesh: trimesh.Trimesh, target_mass_g: float | None, mates: dict[str, trimesh.Trimesh],
        out_dir: Path, stem: str) -> list[Check]:
    return [check_mesh(mesh), check_mass(mesh, target_mass_g), check_mating(mesh, mates),
            render(mesh, out_dir, stem), check_build_volume(mesh)]


def summary(checks: list[Check]) -> str:
    return "\n".join(f"  [{'PASS' if c.passed else 'FAIL'}] {c.num} {c.name}: {c.detail}" for c in checks)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("stl")
    ap.add_argument("--target-mass", type=float)
    ap.add_argument("--mate", action="append", default=[], metavar="name=path.stl")
    ap.add_argument("--out", default="out/verify")
    a = ap.parse_args()
    mesh = trimesh.load(a.stl, force="mesh")
    mates = {k: trimesh.load(v, force="mesh") for k, v in (m.split("=", 1) for m in a.mate)}
    checks = run(mesh, a.target_mass, mates, Path(a.out), Path(a.stl).stem)
    print(summary(checks))
    (Path(a.out) / f"{Path(a.stl).stem}_verify.json").write_text(
        json.dumps([c.__dict__ for c in checks], indent=2, default=str))
    raise SystemExit(0 if all(c.passed for c in checks) else 1)


if __name__ == "__main__":
    main()
