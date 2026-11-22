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
