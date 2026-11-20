"""CLI: python make.py <part> --rev N [--project l1-cheap] [--param k=v ...]

Builds parts/<part>.py, exports STEP + STL, runs every verify.py check, writes renders and a
spec sheet to out/<part>/rev<N>/. Exit code 0 only if every automatic check passes.
Renders still need a visual review before the part may be called good.
"""
from __future__ import annotations

import argparse
import importlib
import json
import sys
from datetime import date
from pathlib import Path

import cadquery as cq
import trimesh

import verify

ROOT = Path(__file__).resolve().parent
STL_TOL_MM, STL_ANG_TOL_RAD = 0.02, 0.1  # mesh export resolution (not part geometry)


def parse_params(pairs: list[str]) -> dict:
    out = {}
    for s in pairs:
        if "=" not in s:
            sys.exit(f"--param expects k=v, got '{s}'")
        k, v = s.split("=", 1)
        try:
            out[k] = float(v) if "." in v or "e" in v.lower() else int(v)
        except ValueError:
            out[k] = v
    return out


def export(shape: cq.Workplane, path: Path) -> None:
    if path.suffix == ".stl":
        cq.exporters.export(shape, str(path), tolerance=STL_TOL_MM, angularTolerance=STL_ANG_TOL_RAD)
    else:
        cq.exporters.export(shape, str(path))


def spec_sheet(part, p, checks, extras, overrides, stem, rev) -> str:
    st = p.get("_status", {})
    placeholders = sorted(k for k, s in st.items() if s in ("PLACEHOLDER", "OPEN"))
    ok_auto = all(c.passed for c in checks)
    status = ("DRAFT — NOT PRINT-READY (placeholders/open items below)" if placeholders else
              "AUTO CHECKS PASS — pending visual review" if ok_auto else "FAILED VERIFY")
    m = next(c for c in checks if c.num == 2).data
    lines = [f"# {stem} — spec sheet", "",
             f"**Generated:** {date.today()} · `python make.py {part.__name__.split('.')[-1]} --rev {rev}"
             + "".join(f" --param {k}={v}" for k, v in overrides.items()) + "`",
             f"**Status:** {status}", "",
             "## Verify checks", "| # | Check | Result | Detail |", "|---|---|---|---|"]
    lines += [f"| {c.num} | {c.name} | {'PASS' if c.passed else 'FAIL'} | {c.detail} |" for c in checks]
    if m:
        lines += ["", "## Mass (walls + infill model)",
                  f"- Wall band {m.get('wall_mm', 0):.2f} mm · top {m.get('n_top')} / bottom {m.get('n_bottom')} layers "
                  f"of {m.get('layer_mm')} mm",
                  f"- Solid (walls/skins) {m.get('solid_mm3', 0) / 1000:.2f} cm³ · infill region "
                  f"{m.get('infill_region_mm3', 0) / 1000:.2f} cm³ · mesh volume {m.get('mesh_volume_mm3', 0) / 1000:.2f} cm³",
                  f"- Mass at 0 % / 100 % infill: {m.get('mass_0pct_g', 0):.1f} g / {m.get('mass_100pct_g', 0):.1f} g · "
                  f"target {m.get('target_g')} g · infill needed: "
                  + (f"{m['infill_needed_pct']:.1f} %" if m.get("infill_needed_pct") is not None else "n/a")]
    lines += ["", "## Print orientation", getattr(part, "INFO", {}).get("print_orientation", "TBD"),
              "", "## Loads vs. layers"] + [f"- {s}" for s in getattr(part, "INFO", {}).get("loads", [])]
    lines += ["", "## Parameters", "| Parameter | Value | Status | Source / note |", "|---|---|---|---|"]
    src = p.get("_source", {})
    for k, v in p.items():
        if k.startswith("_"):
            continue
        base = k.replace("_mm", "").replace("_deg", "")
        s = st.get(k, st.get(base, ""))
        val = f"{v:.3f}".rstrip("0").rstrip(".") if isinstance(v, float) else v
        lines.append(f"| `{k}` | {val} | {s or 'derived/shop'} | {src.get(k, '')} |")
    if placeholders:
        lines += ["", "## Not print-ready until resolved"] + [f"- `{k}`: {src.get(k, '')}" for k in placeholders]
    if extras:
        lines += ["", "## Extra outputs"] + [f"- `{Path(e).name}`" for e in extras]
    return "\n".join(lines) + "\n"


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("part")
    ap.add_argument("--rev", type=int, required=True)
    ap.add_argument("--project", default="l1-cheap")
    ap.add_argument("--param", action="append", default=[], metavar="k=v")
    a = ap.parse_args()

    part = importlib.import_module(f"parts.{a.part}")
    p = part.params(a.project)
    overrides = parse_params(a.param)
    unknown = set(overrides) - set(p)
    if unknown:
        sys.exit(f"unknown params: {sorted(unknown)}")
    p.update(overrides)

    stem = f"{a.part}_rev{a.rev}"
    out = ROOT / "out" / a.part / f"rev{a.rev}"
    (out / "mates").mkdir(parents=True, exist_ok=True)
    shape = part.build(p)
    export(shape, out / f"{stem}.step")
    export(shape, out / f"{stem}.stl")
    mesh = trimesh.load(out / f"{stem}.stl", force="mesh")
    mates = {}
    for name, solid in part.mating(p).items():
        f = out / "mates" / f"{name}.stl"
        export(solid, f)
        mates[name] = trimesh.load(f, force="mesh")

    checks = verify.run(mesh, p.get("target_mass_g"), mates, out, stem)
    extras = part.extras(p, out, stem) if hasattr(part, "extras") else []
    (out / f"{stem}_verify.json").write_text(json.dumps([c.__dict__ for c in checks], indent=2, default=str))
    (out / f"{stem}_spec.md").write_text(spec_sheet(part, p, checks, extras, overrides, stem, a.rev))
    print(verify.summary(checks))
    print(f"spec sheet: {out / f'{stem}_spec.md'}")
    sys.exit(0 if all(c.passed for c in checks) else 1)


if __name__ == "__main__":
    main()
