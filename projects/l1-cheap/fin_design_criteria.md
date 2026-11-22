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

## Rev 8 (2026-11-22, owner request): boattail tail cone, landing strength kept

Rev 7 fins unchanged; threaded collar (12 mm) behind the aft face; screw-on tail cone (parts/tail_cone.py) traps the
thrust ring (motor retainer, insert holes removed, bosses solid) and tapers 46.8 -> 43.0 mm over 20 mm (5.4 deg);
45-deg gussets under each fin root TE onto the collar (the first rev 8 FEA peaked at that 90-deg corner, C1 0.46).

| Criterion | Rev 7 | Rev 8 (no gusset) | **Rev 8 (gusseted)** | Limit |
|---|---|---|---|---|
| C1 sideways 200 N | 0.28 | 0.46 | **0.30** | 0.5 |
| C2 tilted 200 N @45 | 0.25 | 0.39 | **0.33** | 0.5 |
| C3 axial 200 N | 0.084 | 0.20 | **0.11** | 0.5 |
| C4 gust 15 N | 0.022 | 0.031 | **0.023** | 0.1 |

C5 flutter: fins unchanged (pass). C6: verify 1/3/4/5 PASS; check 2 needs slicer masses; the fin TEs now overhang
12 mm (collar on the bed) -> small supports under the three TEs. C7: OR planform kept.
CFD (100 m/s, alpha 4, same tools): CP 834.4 mm (rev 7 836.3), CN_alpha 13.67 (14.06), pressure CA 0.266 (0.375,
-29 %), total CA est 0.608 (0.709, -14 %); base+fin pressure drag 0.360 -> 0.236. Fin 1 lift 4.26/rad (4.42).
Flight sim (OR weights + extras, fin can + cone ESTIMATE 94.6 + 12.6 g, Cd x0.857): CG 758.8 mm, **1.83 cal on the CFD
CP** (rev 7 2.02), apogee **1341 m** (1224), M 0.781, coast 11.75 s (12 s delay deploys at 2.4 m/s).
Tail cone: print in ABS/ASA or tape-line the bore (it surrounds the nozzle exit during the burn).

## Rev 9 (2026-11-22, owner request): no bosses, thin TE, smooth TE skirt, 30 mm boattail, 40 mm fairing

Changes vs rev 8: M3 insert bosses removed (tail cone retains the motor); TE root 8 -> 2.5 mm; the 45-deg gusset
replaced by a smooth concave R6 skirt that follows the fin footprint into the collar; boattail 30 mm to 41.6 mm
(5.0 deg); forward fairing 20 -> 40 mm; collar 18.5 mm for a 9.5 mm thrust ring (forum estimate).

| Criterion | Rev 7 | Rev 8 | **Rev 9** | Limit |
|---|---|---|---|---|
| C1 sideways 200 N | 0.28 | 0.30 | **0.34** | 0.5 |
| C2 tilted 200 N @45 | 0.25 | 0.33 | **0.27** | 0.5 |
| C3 axial 200 N | 0.084 | 0.11 | **0.15** | 0.5 |
| C4 gust 15 N | 0.022 | 0.023 | **0.026** | 0.1 |

CFD 100 m/s alpha 4: CP 827.4 mm (rev 8 834.4, rev 7 836.3); CN_alpha 13.12; pressure CA 0.232; total CA est 0.578
(rev 7 0.709: -18 %). Fin 1 lift 4.00/rad.
Sim (OR weights + extras, fin can 97.9 g est + tail cone 16.0 g model, CG 31.5 mm fwd of the fin-can aft face):
CG 761.0 mm -> **1.61 cal** with the 65 g nose; **+7.4 g nose ballast (nose 72 g) for 1.8 cal**; apogee 1383 m
(rev 7 1224, rev 8 1341); coast 12.09 s -> 12 s delay deploys at 0.9 m/s.
Printing: TE overhangs still need light tree supports outboard of the skirt.
