# Project: l1-cheap — Phase 2 Stability & Integration

**Status:** Phase 2 integration, rev 2, 2026-11-20. Uses the **real fin can mass** from `parts/fin_can.py`
rev 1. **PROVISIONAL:** the Quasar-LR payload mass and bay are TBD, and the tube, liner, nose, chute,
epoxy, rail-button and retention masses are estimates (§2).

**Sim.** `sims/l1_cheap.py` (RocketPy 1.13.0) reads every number from `design.yaml` and the shop
constants.
- Each component takes the owning agent's value when it is a number, and falls back to
  `stability.assumptions` otherwise.
- A strict run stops on any TBD. `--allow-tbd` leaves the item out and stamps the run PROVISIONAL.
- If the liftoff margin is ≤ 0, the flight is not simulated, because a tumble is meaningless.
- Fin can: the sim uses `stability.fin_can_model_mass_g` and `fin_can_model_cg_from_aft_mm` when those
  are numbers. Otherwise it falls back to the walls+infill estimate.
- Liner: computed from `fin_can.liner_*` × `assumptions.cardboard_density_g_cm3`.

**Sweeps.** `sims/l1_cheap_sweep.py [mass|payload|cd|nose|all]`.

**Baseline run, used for every result below:**
`.venv/bin/python sims/l1_cheap.py --allow-tbd --set payload.mass_g=0 --set payload.bay_length_mm=0`

**Rev 2 change.** The fin can went from a 197.3 g estimate at 1047.4 mm (weighted CG of the three
estimate items) to 171.1 g at 1047.7 mm (80.3 mm forward of the aft face). The CG barely moved; the
26 g mass cut is what matters. Adding the liner (+10.0 g),
the solved ballast dropped from 96 g to **90 g**, and the liftoff mass from 736 g to 713 g.

## 1. Headline

| Item | Value | vs. target |
|---|---|---|
| Configuration | 165 ogive nose + 863 mm BT-1.52 (uncut) + 100 mm exposed fin can, span 40, **90 g nose ballast** | |
| Length / liftoff / burnout mass | 1128 mm / 713 g / 598 g | |
| CP (Barrowman, M≈0) | 845.5 mm (RocketPy 845.4; 856.6 at M 0.9) | |
| CG liftoff / burnout | 770.8 / 721.6 mm | |
| **Static margin, liftoff** | **1.81 cal** | **PASS** (1.8 ± 0.2) |
| **Static margin, burnout** | **3.00 cal** | **FAIL (high)**, not forced |
| Margin at rail exit / max in flight (RocketPy) | 1.90 / 3.27 cal | |

**Why burnout fails.** The burn removes 115 g of propellant from about 256 mm aft of the CG, which
adds **+0.8 to +1.2 cal** in every practical configuration (§4). The band is only 0.4 cal wide.
- The only designs that hold both ends are 565–715 mm long with 75–90 mm fins (rev 1 grid). Those are
  bad for flutter, and too short for the chute and the bay.
- The owner has not yet ruled on whether the band applies at burnout.

**Without ballast the rocket is unstable:** −0.63 cal at liftoff.

## 2. Mass budget (no payload; x from the nose tip)

| Item | g | x (mm) | Basis |
|---|---|---|---|
| Nose cone | 52.7 | 119.9 | nosecone.md, ESTIMATE |
| Ballast | 90 | 74.6 | stability. Fill tip→100 mm (27.2 cm³) needs ≥ 3.31 g/cm³ packed |
| BT-1.52 tube, 863 mm | 93.6 | 596.5 | **ESTIMATE** 0.1085 g/mm = shop wall area 159.6 mm² × 0.68 g/cm³ (OpenRocket cardboard) |
| **Fin can incl. fins (rev 1 model)** | **171.1** | **1047.7** | verify mass model at 25 % infill (170.5–173.0 over 0–100 %). Solid-mesh CG 80.3 mm forward of the aft face |
| Motor liner MMT-1.14, 203 mm | 10.0 | 1026.5 | **ESTIMATE** π/4 (30.5² − 28.956²) × 203 × 0.68 g/cm³. **OD 30.5 is a placeholder**. Placed at the motor midpoint |
| Parachute, 40 in | 57 | 865.0 | recovery's ≤57 g estimate |
| Kevlar, 3.68 m × 2.91 g/m | 10.7 | 865.0 | owner; 3 × 1128 + 0.3 m allowance (estimate) |
| Wadding | 2 | 915.0 | **ESTIMATE** |
| Epoxy | 10 | 976.5 | **ESTIMATE** |
| Rail buttons | 5 | 828.0 | **ESTIMATE** |
| Retention (screws + inserts) | 4 | 1126.0 | **ESTIMATE**. fin_can rev 1 has no retention yet |
| **Structure** | **506.1** | **666.2** | |
| Motor, loaded / dry | 207 / 92 | 1026.5 | motor.md. CG assumed at mid-length |

The recovery pack is placed resting on the motor's forward end, its most aft (conservative) position.

## 3. Flight (nominal Cd, vertical, no wind, standard atmosphere)

Cd is aero.md's table, held at 0.83 above M 0.7 with no transonic rise (assumption).
- **Apogee:** 1284 m (4213 ft) at 13.88 s.
- **Burnout:** 1.235 s. **Coast to apogee:** 12.65 s.
- **Vmax:** 282.1 m/s (**M 0.83**). Max q 48.0 kPa.
- **Rail exit:** **25.5 m/s** on the 1.5 m rail, **28.4 m/s** on the 1.83 m rail. Rail-button geometry is
  not modelled.

**Deployment vs. delay** (timed from burnout; recovery flags: ≤ 20 m/s preferred, ≤ 27 m/s limit)

| Delay (s) | 14 | 13 | 12 | 11 | 10 | 9 | 8 | 6 | 4 |
|---|---|---|---|---|---|---|---|---|---|
| Altitude AGL (m) | 1275 | 1283 | 1282 | 1271 | 1249 | 1218 | 1175 | 1053 | 871 |
| Speed (m/s) | 12.8↓ | 3.4↓ | 6.3↑ | 16.3↑ | 26.4↑ | 37.1 | 48.4 | 74.6 | 108.9 |
| Flag | pref. | pref. | pref. | pref. | limit | too fast | too fast | too fast | too fast |

**Cd sensitivity at 12 / 13 / 14 s delay**

| Cd scale | Coast to apogee | 12 s | 13 s | 14 s |
|---|---|---|---|---|
| × 0.85 | 13.48 s | 14.6 m/s | 4.8 m/s | 5.0 m/s |
| × 1.15 | 11.95 s | 0.5 m/s | 10.2 m/s | 17.2 m/s |
| × 1.30 | 11.36 s | 6.2 m/s | 14.6 m/s | 22.0 m/s |

**Recommended delay: 12 s.** It stays ≤ 14.6 m/s across Cd × 0.85–1.3. 13 s is equally good if the
AeroTech tool offers it. 14 s goes over 20 m/s at Cd × 1.3.

## 4. Mass trade: subsonic vs. light (owner decides)

All rows use the 1.83 m rail. The "ballast" column is the ballast solved for a 1.8 cal liftoff margin,
unless stated otherwise.

| Config | Ballast | Liftoff | SM lo/bo | Vmax | Mach | Apogee | v @ 12 s |
|---|---|---|---|---|---|---|---|
| s50, tube −200 mm | 48 | 647 g | 1.80/2.65 | 307 | 0.90 | 1289 | 3.3 |
| s50, full tube | 34 | 657 g | 1.80/2.81 | 303 | 0.89 | 1289 | 3.8 |
| s45, full tube | 57 | 680 g | 1.80/2.89 | 294 | 0.87 | 1288 | 5.0 |
| **s40, full tube (baseline)** | **90** | **713 g** | **1.80/2.99** | **282** | **0.83** | **1284** | **6.3** |
| s40, +50 g ballast | 140 | 763 g | 2.91/4.20 | 266 | 0.78 | 1273 | 8.0 |
| s40, +100 g | 190 | 813 g | 3.88/5.24 | 251 | 0.74 | 1255 | 9.2 |
| s40, +150 g | 240 | 863 g | 4.73/6.14 | 237 | 0.70 | 1233 | 9.8 |

- Each 50 g cuts Vmax by about 15 m/s, but apogee by only about 10–20 m.
- Each 50 g of extra ballast adds about +1 cal of over-stability, and costs about 0.8 m/s of rail exit.
- The lighter, bigger-fin options approach M 0.9, where the flat Cd is least trustworthy and flutter is
  worst.

## 5. Nose cone mass sweep (CG held at 119.9 mm; ballast solved for 1.8 cal at liftoff)

| Nose | Ballast | Liftoff | SM lo/bo | Vmax / Mach | Apogee | v @ 12 s |
|---|---|---|---|---|---|---|
| 40 g | 101.5 g | 712 g | 1.80/2.99 | 282.6 / 0.832 | 1284 | 6.3 |
| 45 g | 96.8 g | 712 g | 1.80/2.99 | 282.5 / 0.832 | 1284 | 6.3 |
| **52.7 g** | **89.6 g** | **713 g** | **1.80/2.99** | **282.3 / 0.831** | **1284** | **6.3** |
| 60 g | 82.8 g | 713 g | 1.80/2.99 | 282.1 / 0.831 | 1284 | 6.3 |
| 70 g | 73.4 g | 714 g | 1.80/2.99 | 281.9 / 0.830 | 1284 | 6.3 |

- **Nose mass error is absorbed by the ballast almost one-for-one:** −0.93 g of ballast per +1 g of nose,
  because both sit forward.
- The flight barely changes.
- So the nose target stays **52.7 g**. Its ±5 % tolerance (±2.6 g) moves the ballast by about ∓2.5 g.
- **Set the final ballast from the weighed nose**, and check it with a CG balance test on the built
  rocket.

## 6. Payload slot (Quasar-LR bay cut from the 863 mm stock; ballast solved)

| Payload / bay | Ballast | Liftoff | Vmax / Mach | Apogee |
|---|---|---|---|---|
| 0 g / 0 | 90 g | 713 g | 282 / 0.83 | 1284 |
| 80 g / 180 mm | 30 g | 733 g | 275 / 0.81 | 1280 |
| 120 g / 180 mm | 1 g | 744 g | 272 / 0.80 | 1278 |

## 7. Target masses for verify.py (±5 %)

- **Fin can: 171.1 g**, the value this budget uses. Rev 1 reaches 170.5–173.0 g, so it passes at any
  infill.
- **Nose cone: 52.7 g, unchanged.** This is the shell only, without ballast (§5).

## 8. Sources (accessed 2026-11-20)

- OpenRocket cardboard 0.68 g/cm³: [TRF post](https://www.rocketryforum.com/goto/post?id=2317962),
  [WSU OpenRocket model](https://hub.wsu.edu/aerospace/wp-content/uploads/sites/204/2015/02/OpenRocket-Model.pdf)
- LOC BT-1.52, no published mass: [Wildman](https://wildmanrocketry.com/products/bt-1-52),
  [LOC](https://locprecision.com/products/cardboard-airframes)
- Wadding: [hobbyetc](https://store.hobbyetc.com/parts/view/123056). Chute: recovery (the-rocketman.com/?p=3121).
  Kevlar: owner.
- Fin can mass and CG: `out/fin_can/rev1/` (verify mass model, solid-mesh CG). Liner ID: `fin_can.liner_id_mm`.

## 9. Open questions for the owner

1. Does the ±0.2 band apply at liftoff only? Burnout is about 1.2 cal higher.
2. Ballast density: it needs ≥ 3.31 g/cm³ packed to fit tip→100 mm.
3. Rail length and the minimum rail-exit speed you want.
4. Light (s50, M 0.89) or heavier (s40 + ballast, M 0.83)?
5. Measure the liner OD; weigh the tube, chute, nose and Kevlar.
