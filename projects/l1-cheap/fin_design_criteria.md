# l1-cheap — Fin can acceptance criteria ("perfect" = all met at the lowest mass)

Owner request (2026-11-21): iterate rev 7, 8, 9 … until the fins are right for this rocket. Each
revision is generated with `make.py fin_can_md`, then analysed with `tools/fea_ccx.py` at the **same
settings** (mesh 3.0 mm global / 0.8 mm root box, C3D10, direct solver). Failure indices are scaled
to the owner's ANSYS calibration using rev 5 run at those same settings.

| # | Criterion | Requirement | Basis |
|---|---|---|---|
| C1 | Sideways landing hit, 200 N at the tip (Y) | **FI ≤ 0.5** (ANSYS-scaled): a 2× margin | 200 N = main-session realistic landing ESTIMATE (ansys_results.md); 2× covers print variability |
| C2 | Tilted landing, 200 N at 45° (Y + Z) | FI ≤ 0.5 (scaled) | same |
| C3 | Tail-first landing, 200 N axial (Z) | FI ≤ 0.5 (scaled) | same |
| C4 | Flight gust (15 N Y) | FI ≤ 0.1 | ansys_results.md case 1 |
| C5 | Flutter | Vf ≥ 1.5 × Vmax (250 m/s) at G = 394 MPa | aero method (NACA TN 4197); thickness only increases Vf |
| C6 | Printable and verified | verify checks 1, 3, 4, 5 PASS; no overhang (TE flush, planform shrinks going up); check 2 once the owner gives the slicer mass | shop rules |
| C7 | Aero and stability unchanged | owner's OpenRocket planform kept (50/30/43.18/20.32); ballast re-solved for 1.8 cal | owner decision |
| C8 | **Mass** | the **lowest** fin-can mass that meets C1–C7 | every gram at the tail costs ~0.4 g of nose ballast |

**Stop rule:** stop when a revision meets C1–C7 and the next, lighter step fails one of them. Hard cap: rev 10.
Then hand off to stability (ballast), docs (report) and the owner (slicer mass, ANSYS cross-check, print).

**Outcome (2026-11-21):** the owner stopped the loop at **rev 7** (C1–C4 ALL PASS: C1 0.28, C2 0.25,
C3 0.084, C4 0.022 scaled FI; `out/fea/rev7/criteria.json`). Rev 8 (root 10 mm) was not analysed: its
FEA mesh failed in gmsh (ScaledJac) and the owner chose rev 7. C6 mass check still needs the slicer mass.
