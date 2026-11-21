"""Score a fin-can revision against projects/<project>/fin_design_criteria.md.

  .venv/bin/python tools/fin_iter.py --rev 7 [--run]      # --run: (re)run the 4 FEA cases first

Same settings for every revision: mesh 3.0 mm global / 0.8 mm root box (tools/fea_ccx.py).
ANSYS calibration: rev 5 at the same settings vs the owner's ANSYS rev 5 values (ansys_results.md):
  sideways 50 N Y → FI 0.571;  axial: 770 N Z → FI 1.0 (i.e. 0.5195 at 400 N).
Linear static, so FI scales with load: criteria loads are scaled from the run loads.
Writes out/fea/rev<N>/criteria.json and prints a table.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MESH = ["--mesh", "3.0", "--root-mesh", "0.8"]
CASES = {  # name: (fea loads, criteria load scale, label)
    "m30r08_tipY50": (["--load", "Y=50"], 200 / 50, "C1 sideways 200 N"),
    "m30r08_tipZ400": (["--load", "Z=400"], 200 / 400, "C3 axial 200 N"),
    "m30r08_200N_at45": (["--load", "Y=141.4", "--load", "Z=141.4"], 1.0, "C2 tilted 200 N @45°"),
    "m30r08_gust15": (["--load", "Y=15"], 1.0, "C4 flight gust 15 N"),
}
LIMIT = {"C1": 0.5, "C2": 0.5, "C3": 0.5, "C4": 0.1}
ANSYS_REV5 = {"Y50": 0.571, "Z400": 400 / 770}


def fi(rev: int, name: str) -> float | None:
    f = ROOT / "out" / "fea" / f"rev{rev}" / name / "result.json"
    return json.loads(f.read_text())["root_FI_max"] if f.exists() else None


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--rev", type=int, required=True)
    ap.add_argument("--run", action="store_true")
    a = ap.parse_args()
    if a.run:
        for name, (loads, _, _) in CASES.items():
            if fi(a.rev, name) is None:
                r = subprocess.run([str(ROOT / ".venv/bin/python"), str(ROOT / "tools/fea_ccx.py"), "--rev", str(a.rev),
                                    *MESH, *loads, "--name", name], cwd=ROOT, capture_output=True, text=True)
                if fi(a.rev, name) is None:
                    sys.exit(f"FEA failed for rev {a.rev} {name}:\n{(r.stdout + r.stderr)[-1500:]}")
    c5y, c5z = fi(5, "m30r08_tipY50"), fi(5, "m30r08_tipZ400")
    if c5y is None or c5z is None:
        sys.exit("rev 5 calibration runs (m30r08_tipY50 / m30r08_tipZ400) missing")
    sy, sz = ANSYS_REV5["Y50"] / c5y, ANSYS_REV5["Z400"] / c5z
    rows, ok = [], True
    for name, (_, scale, label) in CASES.items():
        raw = fi(a.rev, name)
        if raw is None:
            rows.append((label, None, None, None, "MISSING")); ok = False; continue
        k = label[:2]
        s = sz if k == "C3" else max(sy, sz) if k == "C2" else sy
        val = raw * scale * s
        passed = val <= LIMIT[k]
        ok &= passed
        rows.append((label, raw * scale, val, LIMIT[k], "PASS" if passed else "FAIL"))
    out = {"rev": a.rev, "calibration": {"sideways": sy, "axial": sz}, "all_pass_C1_C4": ok,
           "rows": [dict(zip(["criterion", "FI_raw", "FI_scaled", "limit", "result"], r)) for r in rows]}
    (ROOT / "out" / "fea" / f"rev{a.rev}" / "criteria.json").write_text(json.dumps(out, indent=2))
    print(f"rev {a.rev}  (ANSYS calibration ×{sy:.3f} sideways, ×{sz:.3f} axial)")
    for r in rows:
        print(f"  {r[0]:<24} raw {r[1] if r[1] is None else round(r[1], 3)}  scaled {r[2] if r[2] is None else round(r[2], 3)}  "
              f"limit {r[3]}  {r[4]}")
    print("C1–C4:", "ALL PASS" if ok else "NOT MET")


if __name__ == "__main__":
    main()
