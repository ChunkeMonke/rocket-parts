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
