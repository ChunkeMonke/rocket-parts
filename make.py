"""CLI: python make.py <part> --rev N --param k=v [--param k=v ...]

Step 1 skeleton: argument parsing only. Generation and the mandatory
verify.py run are wired up in steps 2-3.
"""
from __future__ import annotations

import argparse
import sys


def parse_params(pairs: list[str]) -> dict[str, float | str]:
    out: dict[str, float | str] = {}
    for p in pairs:
        if "=" not in p:
            sys.exit(f"--param expects k=v, got '{p}'")
        k, v = p.split("=", 1)
        try:
            out[k] = float(v)
        except ValueError:
            out[k] = v
    return out


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("part", help="module name in parts/")
    ap.add_argument("--rev", type=int, required=True)
    ap.add_argument("--param", action="append", default=[], metavar="k=v")
    args = ap.parse_args()
    params = parse_params(args.param)
    sys.exit(f"make.py: generation not implemented yet (step 3). part={args.part} rev={args.rev} params={params}")


if __name__ == "__main__":
    main()
