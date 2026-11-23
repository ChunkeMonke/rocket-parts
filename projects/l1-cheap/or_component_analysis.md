# OpenRocket component analysis vs our model (owner screenshot, 2026-11-21)

OR config H100W_DMS-6, Mach 0.300, AoA 0, ref length 1.625 in (41.275 mm), ref area 2.07 in².

| Component | Mass (lb / g) | CG (in) | CP (in) | CNα |
|---|---|---|---|---|
| Total | 1.404 / 637 | 29.442 | **32.914** | **11.364** |
| Nose cone | 0.176 / 80 | 4.842 | 3.018 | 2 |
| Body tube | 0.272 / 123 | 23.5 | — | 0 |
| Trapezoidal fin set (3) | 0.265 / 120 (override) | 39.696 | 39.299 | **9.364** |
| Inner tube | 0.014 / 6 | 37.45 | — | 0 |
| H100W_DMS | 0.575 / 261 | 37.55 | — | 0 |
| Parachute | 0.084 / 38 | 13.992 | — | 0 |
| Bulkhead | 0.005 / 2 | 19.461 | — | 0 |
| Shock cord | 0.012 / 5 | 14.992 | — | 0 |

## Fin normal-force slope, same fins (50 / 30 / 43.18 / sweep 20.32 mm, 3 fins, no sleeve)
| Method | CNα (fins) |
|---|---|
| Barrowman (RocketPy / our sim) | 6.97 |
| Lifting-surface single-fin slope × N/2 × body interference, N = 3 | 7.08 |
| Same, **N = 4** | **9.43** |
| OpenRocket | **9.364** |

OR's fin CNα is ~34 % above two independent 3-fin methods and within 1 % of the 4-fin value.
Nose agrees exactly (CNα 2, CP 3.018 in = k·L with k ≈ 0.464).
Masses: the OR body tube is 123 g (our ESTIMATE 94 g; weigh it). Nose 80 g and fins 120 g are owner overrides.

## OpenRocket export 2026-11-22 (owner "test.pdf", Pepto B. #2) vs in-house sim

OR inputs: nose 65 g TOTAL (PETG ogive 6.5 in), tube 34 in / 123 g, 3 fins 0.35 in thick (mass override 90 g = rev 7 fin can),
28 in ripstop chute 38 g, elastic shock cord 122 in (owner keeps the KEVLAR; OR cord is a placeholder), ABS bulkhead, inner tube 6.1 in.
OR results, H100W_DMS-6: 594 g, CG 29.545 in (750.4 mm), CP 32.914 in (836.0 mm), **2.07 cal**, apogee 3945 ft (1202 m),
Vmax 615 mph, off pad 41.5 mph, optimum delay 11.6 s, landing 11.8 mph. (H182R-6: 3420 ft, superseded motor.)

In-house (sims/l1_cheap.py, same 65 g nose, 28 in chute, ref 41.275 mm):

| Case | Margin liftoff | Ballast for 1.8 cal |
|---|---|---|
| chute pack on the motor stop (where boost pushes it) | **0.16 cal: UNSTABLE** | 62.7 g (nose 126 g) |
| chute pack held at 300 mm from the tip (OR-like) | 1.20 cal | 24.1 g (nose 89 g) |

The gap is (1) pack position: ~45 mm of CG, and (2) CP: OR 836 vs Barrowman/RocketPy 805 mm (~0.75 cal), the same
unresolved difference as section 0.3 of stability.md. Design value kept at 63 g ballast pending the owner's decision and the balance check.

## 3D CFD settles the CP (2026-11-22, tools/cfd_rocket.py + tools/cfd_post.py, case out/cfd/of_a4)

OpenFOAM v1912 simpleFoam, k-omega SST, half model (symmetry plane through fin 0), 590k cells (snappyHexMesh,
1.6 mm on fins), 100 m/s (M 0.29), alpha 4 deg, rev 7 fin can OML. Converged (residuals 1e-7 to 1e-8; CP moved
< 0.001 mm from iteration 600 to 800). Forces from surface pressure (the forces function object crashes in this build).

| Item | CFD | Barrowman / RocketPy | OpenRocket |
|---|---|---|---|
| CP from tip | **836.3 mm** | 804.7 mm | 836.0 mm |
| CN_alpha total (/rad, ref 41.275) | 14.06 | 9.69 | n/a |
| nose CN_alpha (check) | 2.01 at 78.0 mm | 2.00 at 76.9 mm | |
| fins only | 7.70 | 7.12 (incl. interference) | |
| body around the fins (sleeve, carry-over) | 3.01 | (in the 7.12 factor) | |
| tube + fairing step | 1.34 | 0.57 (step + fairing only) | |
| CA (pressure + flat-plate friction est.) | 0.375 + 0.33 = 0.71 | Cd 0.73 (aero.cd_estimate) | |

**Result:** the CFD agrees with OpenRocket (836 mm). Barrowman misses the body lift around the fin can and along the
tube, which puts its CP 31 mm too far forward (conservative). With the owner's 65 g nose:
OR CG 750.4 -> **2.08 cal**; with the real extras (CG 753) -> 2.01 cal; if the chute pack slides onto the motor
(CG 788) -> 1.17 cal (still stable). Caveats: one angle (4 deg), one speed (incompressible; CP moves aft with Mach,
which adds margin), one mesh (no grid study), wall functions, friction from a flat-plate estimate.
Figures: projects/l1-cheap/report/figures/cfd/.

## Mach 0.8 CFD: INTERIM (2026-11-22, stopped at ~1500 of 2500 iterations for owner shutdown)

rhoPimpleFoam (local time stepping, first-order upwind, temperature limiter), M 0.8 = 272 m/s, alpha 4 deg, ISA sea level,
same mesh as the 100 m/s run. The steady rhoSimpleFoam start diverged (negative temperature) twice; LTS was stable.

| Iteration | CP from tip | CN_alpha (/rad) | CA pressure | Surface T |
|---|---|---|---|---|
| 500 | 822.0 mm | 15.21 | 1.138 | 260-352 K |
| 1000 | 821.1 mm | 15.17 | 0.957 | 260-350 K |

CP and CN_alpha settled within ~1 mm / 0.3 %; drag still falling. NOT YET TRUSTED: CP is ~15 mm forward of the
100 m/s result (836 mm), opposite to the expected aft shift with Mach, and the 350 K peak exceeds the ~321 K adiabatic
wall temperature, so first-order smearing is suspected. Next: finish 2500, continue second-order from it, compare CP.
Raw data: out/cfd/of_m08/result_interim.json. Re-run: tools/cfd_rocket.py setup --name m08 --mach 0.8; bash Allrun.

### Mach 0.8 final (first-order, 2500 iterations, 2026-11-22): out/cfd/of_m08/result.json
| Iteration | CP | CN_alpha | CA pressure | Surface T |
|---|---|---|---|---|
| 2000 | 817.7 mm | 14.88 | 0.952 | 262-350 K |
| 2500 | 818.3 mm | 14.89 | 0.958 | 261-350 K |
Converged for the first-order scheme (CP +0.6 mm over the last 500). CA total ~1.23 (friction flat-plate ESTIMATE 0.273).
On the OR CG: 1.64 cal. Not yet trusted (first-order smearing; T peak above the adiabatic wall value). Next: second order.

### Owner-PC reproduction of the 100 m/s case (2026-11-22, main session record)
WSL Ubuntu, OpenFOAM v2406 (OpenFOAM.com), 8 cores, same tools/cfd_rocket.py case: CP 836.2966 mm, CN_alpha 14.0585/rad,
CA_total_est 0.7089. Cloud run (OpenFOAM v1912, 4 cores): 836.3131 mm, 14.0586, 0.7088. Agreement 0.02 mm.

### In-house flight sim with the OR weights (2026-11-22, sims/l1_cheap_sweep.py case(), main session record)
Case A (OR weights only, chute pack at 370 mm, extras zeroed): 583 g, CG 749.2 mm, 1.35 cal on the Barrowman CP,
apogee 1212 m, Vmax 266.1 m/s, M 0.785, rail exit 25.5 m/s on the 1.83 m rail (24.1 m/s for case B).
Case B (+ motor stop, epoxy, buttons, retention): 619 g, CG 753.0, apogee 1224 m, M 0.761. Case C (pack slid onto the
motor): CG 788.3, 0.40 cal on Barrowman (1.17 cal on the CFD CP).

## Owner STEP model CFD (2026-11-23, case own_a4)

Geometry: owner's SolidWorks fin can (fin tip r 69.5, span 46.1 mm on the r 23.40 sleeve, **intentional**) + owner tail cone
seated (tools/rocket_oml_owner.py), tube 863 + 165 mm ogive. 633k cells, 1 skewed face (4.37), CP converged (-0.11 mm last quarter).
simpleFoam, 100 m/s, α 4°.

| | rev 9 (r9a4) | owner model (own_a4) |
|---|---|---|
| CP from tip | 827.4 mm | **809.9 mm** |
| CN_α | 13.12 /rad | **11.89 /rad** |
| per-fin pitch-plane lift slope | 3.46 /rad | 3.19 /rad |
| CA total est. | 0.578 | 0.600 |
| margin, 65 g nose (CG est. 761 / 759) | 1.61 cal | **≈1.23 cal** |

The larger span did not raise the fin lift. The aft ~40 % of the owner fins carry almost no load
(cfd_fin_pressure.png), and CN_α is 9 % lower. The cause is not yet isolated: the planform, thickness and mid-plane
(no cant) were all checked. To reach 1.8 cal: about +23 g of nose ballast (ESTIMATE, at ≈1.05 mm CG per g). Redo this
with the owner's slicer masses.

### Why the owner fins make less lift (tools/cfd_lift_breakdown.py, cfd_fin_chord_compare.py)
CN_α difference −1.23, by region: fin roots (fillets, edges, skirt) −0.53; aft body/tail cone −0.25; fin panels −0.19
(even with +10 % panel area); body between fins −0.17; nose and tube −0.08. Chordwise Cp at r = 30/45/60 mm is almost
the same for both, so the panels themselves work the same. The loss sits at the junction and behind the fins.
- The owner fins meet the sleeve with no root fillet (11.2 mm thick at the root vs rev 9's 13.6 mm with R6
  fillets). Rev 9 also has the R6 TE skirt blending into the collar.
- The rev 9 collar keeps full diameter for 18.5 mm behind the fin TE. The owner part starts the tail-cone taper about 16 mm behind it.
Not yet proven by a controlled run (only one variable changed).

## Owner OpenRocket "Pepto B. #2" (2026-11-23, owner_cad/OR_Pepto_B_2.pdf)
Nose cone 6.5 in, 0.132 lb (59.9 g). Tube 29.25 in (exposed). Transition 1.625→1.842 in over 0.75 in (34.9 g).
Sleeve 1.842 OD × 4 in (45.8 g). 3 trapezoidal fins, 0.315 in thick (15.9 g). Tail transition 1.842→1.638 in over 1.909 in (15.9 g).
28 in chute. Total length 1077 mm, the same as the CFD OML.
OR results: mass 1.31 lb (594 g), CG 29.552 in (750.6 mm), CP 32.896 in (835.6 mm), **1.82 cal**, apogee 4404 ft,
optimum delay 11.5 s, max 614 mph (M 0.80), landing 11.9 mph.
CFD of the owner STEP gives CP 809.9 mm, **25.7 mm forward of OR**. With OR's CG that is **1.44 cal**.
For 1.8 cal on the CFD CP: CG 735.6 mm, about **+15 g of nose ballast** (ESTIMATE, lever about 610 mm, 594 g).

## Owner OR v3 (2026-11-23, owner_cad/OR_Pepto_B_3.pdf): geometry updated to the STEP
Results: 1.43 lb (649 g), CG 30.502 in (774.8 mm), CP 33.918 in (861.5 mm), 1.85 cal, 4122 ft.
Issues:
- OR's caliber is now the max diameter, 1.842 in (sleeve): (33.918 - 30.502) / 1.85 = 1.846 in.
  On the 1.625 in tube reference the same rocket is 2.10 cal.
- The fin TE is flush with the sleeve bottom (from the drawing): the -0.59 in offset was not applied, so the fins sit 15 mm too far aft.
- The fairing transition is filled solid: 0.17 lb (77 g). The OR fin-can total is 146 g vs the real part's ~95 g, so the CG is too far aft.
- Still set: delay 14 s, nose 0.132 lb, elastic cords.
CFD CP 809.9 with this CG gives 0.85 cal (tube ref). After the mass fix (CG ≈ 752 mm, ESTIMATE) it gives ≈1.40 cal.
