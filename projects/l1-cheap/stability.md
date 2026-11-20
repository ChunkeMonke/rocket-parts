# Project: l1-cheap — Phase 2 Stability & Integration

**Status:** Phase 2 integration, 2026-11-20. **PROVISIONAL.** The Quasar-LR payload mass and bay
length are TBD, and the tube, fin can, chute, epoxy and rail-button masses are estimates (see §2).

- **Sim:** `sims/l1_cheap.py` (RocketPy 1.13.0). It reads every number from `design.yaml` and the shop
  constants. Each component takes the owning agent's value when it is a number, and otherwise falls back
  to `stability.assumptions`. When an item is still TBD, a strict run stops; `--allow-tbd` leaves the
  item out and stamps the run PROVISIONAL. The payload, chute mass, recovery pack and Cd slot in from
  `design.yaml` with no code change.
- **Sweeps:** `sims/l1_cheap_sweep.py [mass|payload|cd|all]`.
- **Run used for every result below:**
  `.venv/bin/python sims/l1_cheap.py --allow-tbd --set payload.mass_g=0 --set payload.bay_length_mm=0`

## 1. Headline

| Item | Value | vs. target |
|---|---|---|
| Configuration | 165 ogive nose + 863 mm BT-1.52 (uncut) + 100 mm exposed fin can, span 40, **96 g nose ballast** | |
| Length / liftoff mass / burnout mass | 1128 mm / 736 g / 621 g | |
| CP (Barrowman, M≈0) | 845.5 mm (RocketPy 845.4; 856.6 at M 0.9) | |
| CG liftoff / burnout | 771.4 / 724.2 mm | |
| **Static margin, liftoff** | **1.79 cal** | **PASS** (1.8 ± 0.2) |
| **Static margin, burnout** | **2.94 cal** | **FAIL (high)** |
| Margin at rail exit / max in flight (RocketPy) | 1.88 / 3.21 cal | |

**Why burnout fails.** The burn removes 115 g of propellant from about 255 mm aft of the CG, which
adds **+0.8 to +1.15 cal** in every practical configuration (§4, §5). The band is only 0.4 cal wide, so no
practical design holds both ends inside it.
- A grid search found only a few designs that do: 565–715 mm long with 75–90 mm fins, which are bad
  for flutter, and too short to hold the 40 in chute and the avionics bay.
- So the owner must decide whether the ±0.2 band applies at liftoff only. Being over-stable at burnout
  means more weathercocking into the wind. It is not an instability.

**Without ballast the rocket is unstable:** −0.74 cal at liftoff with span 40. Most of the reason is the
207 g motor plus the ~197 g fin can, all in the aft 203 mm.

## 2. Mass budget (no payload; x from the nose tip)

| Item | g | x (mm) | Basis |
|---|---|---|---|
| Nose cone | 52.7 | 119.9 | nosecone.md (estimate) |
| Ballast | 96 | 74.6 | stability. Fill tip→100 mm, so it needs ≥ 3.54 g/cm³ packed. Material TBD |
| BT-1.52 tube, 863 mm | 93.6 | 596.5 | **ESTIMATE** 0.1085 g/mm = shop wall area 159.6 mm² × 0.68 g/cm³ (OpenRocket "cardboard" density). No published LOC mass found |
| Fin can, exposed (OD 41.275, bore 29, 100 mm) | 77.7 | 1078.0 | **ESTIMATE**, walls+infill model at 25 % |
| Fin can shoulder (OD 38.555, 103 mm) | 66.3 | 976.5 | **ESTIMATE**. Assumes the bore supports the full 203 mm motor |
| 3 fins, solid 5 mm | 53.3 | 1090.9 | aero geometry × 1.27 g/cm³ |
| Parachute, 40 in | 57 | 865.0 | recovery's ≤57 g estimate; weigh it |
| Kevlar, 3.68 m × 2.91 g/m | 10.7 | 865.0 | owner; 3 × 1128 mm + 0.3 m loop allowance (estimate) |
| Wadding | 2 | 915.0 | **ESTIMATE**, 8 sheets × ≤0.24 g |
| Epoxy | 10 | 976.5 | **ESTIMATE** |
| Rail buttons | 5 | 828.0 | **ESTIMATE**, 2 × 2.5 g |
| Retention screws + inserts | 4 | 1126.0 | **ESTIMATE** |
| **Structure** | **528.7** | **671.2** | |
| Motor, loaded / dry | 207 / 92 | 1026.5 | motor.md. CG assumed at mid-length |

The recovery pack is placed resting on the motor's forward end, which is its most aft (conservative)
position.

**Fin can lever:** cutting the shoulder to 40 mm saves 40 g aft and 10 g of ballast.

## 3. Flight (nominal Cd, vertical, no wind, standard atmosphere)

The motor is the H182R.eng file. Cd is aero.md's table, held at 0.83 above M 0.7 with no transonic
rise (assumption).
- **Apogee:** 1280 m (4198 ft) at 13.97 s.
- **Burnout:** 1.235 s. **Coast to apogee:** 12.73 s.
- **Vmax:** 274.6 m/s (**M 0.81**). Max q 45.5 kPa.
- **Rail exit:** **25.1 m/s** on the 1.5 m rail, **27.9 m/s** on the 1.83 m rail. Rail-button geometry is
  not modelled. The owner's threshold is TBD.

**Deployment vs. delay** (timed from burnout; recovery flags: ≤ 20 m/s preferred, ≤ 27 m/s limit)

| Delay (s) | 14 | 13 | 12 | 11 | 10 | 9 | 8 | 6 | 4 |
|---|---|---|---|---|---|---|---|---|---|
| Altitude AGL (m) | 1272 | 1279 | 1277 | 1265 | 1243 | 1210 | 1167 | 1043 | 860 |
| Speed (m/s) | 12.2↓ | 2.6↓ | 7.2↑ | 17.1↑ | 27.3↑ | 37.9 | 49.3 | 75.4 | 109.4 |
| Flag | pref. | pref. | pref. | pref. | too fast | too fast | too fast | too fast | too fast |

**Cd sensitivity at 12 / 13 / 14 s delay**

| Cd scale | Coast to apogee | 12 s | 13 s | 14 s |
|---|---|---|---|---|
| × 0.85 | 13.56 s | 15.3 m/s | 5.5 m/s | 4.3 m/s |
| × 1.15 | 12.04 s | 0.4 m/s | 9.4 m/s | 16.6 m/s |
| × 1.30 | 11.46 s | 5.3 m/s | 14.2 m/s | 21.5 m/s |

**Recommended delay: 12 s.** It stays ≤ 15.3 m/s across Cd × 0.85–1.3 and the +150 g cases. 13 s is
equally good if the AeroTech tool offers 1 s steps. The 14 s uncut delay is acceptable at nominal Cd
but goes over 20 m/s at Cd × 1.3. The delay-tool steps and the motor's delay tolerance are TBD.

## 4. Mass trade: subsonic vs. light (owner decides)

All rows use the 1.83 m rail. The "ballast" column is the ballast solved for a 1.8 cal liftoff margin,
unless stated otherwise.

| Config | Ballast | Liftoff | SM lo/bo | Vmax | Mach | Apogee | Rail |
|---|---|---|---|---|---|---|---|
| s50, tube −200 mm | 58 | 687 g | 1.80/2.59 | 291 | 0.86 | 1287 | 28.9 |
| s50, full tube | 43 | 696 g | 1.80/2.74 | 288 | 0.85 | 1286 | 28.7 |
| s45, full tube | 65 | 711 g | 1.80/2.84 | 283 | 0.83 | 1284 | 28.4 |
| **s40, full tube (baseline)** | **96** | **736 g** | **1.80/2.95** | **275** | **0.81** | **1280** | **27.9** |
| s40, +50 g ballast | 146 | 786 g | 2.87/4.12 | 259 | 0.76 | 1266 | 27.0 |
| s40, +100 g | 196 | 836 g | 3.82/5.13 | 245 | 0.72 | 1246 | 26.2 |
| s40, +150 g | 246 | 886 g | 4.66/6.01 | 231 | 0.68 | 1221 | 25.5 |

- **Every stable design is subsonic (M ≤ 0.86).** Aero's M 1.09 case assumed a 300 g structure. The
  real budget is about 530 g, so it can't be that light.
- **Apogee barely moves with mass:** −59 m for +150 g.
- **Each 50 g cuts Vmax by about 14 m/s.** That is the main lever for flutter and Mach margin. It costs
  over-stability, because ballast also pushes the margin far above the band, and rail-exit speed
  (−0.8 m/s per 50 g).
- **Cutting the tube shorter** saves almost no mass, because the ballast grows to compensate. It does
  shrink the ejection free volume.

## 5. Payload slot (Quasar-LR bay, cut from the same 863 mm stock; ballast solved)

| Payload / bay | Ballast for 1.8 | Liftoff | Margin at 0 ballast | Vmax / Mach | Apogee |
|---|---|---|---|---|---|
| 0 g / 0 | 96 g | 736 g | −0.74 | 275 / 0.81 | 1280 |
| 80 g / 180 mm | 37 g | 756 g | 0.93 | 268 / 0.79 | 1275 |
| 120 g / 180 mm | 7 g | 767 g | 1.64 | 265 / 0.78 | 1272 |

The bay's forward mass helps the margin and lowers Vmax. **I will re-solve the ballast when the
payload agent reports.**

## 6. Target masses for verify.py (±5 %)

- **Nose cone: 52.7 g.** This is the shell only; ballast is added after printing.
- **Fin can: 197.3 g.**
  - That is the 100 mm exposed section + the 103 mm shoulder + 3 fins.
  - It is almost all solid (radial walls < 2 crusts), so infill barely moves it. The geometry has to match.
  - Print height 203 mm, footprint 121 mm, both ≤ 256.
  - If the can is designed lighter, tell me and I will re-run. Every 10 g taken off the can saves about
    2.6 g of ballast.

## 7. Sources (accessed 2026-11-20)

- OpenRocket cardboard density, 0.68 g/cm³: [TRF post](https://www.rocketryforum.com/goto/post?id=2317962),
  [WSU OpenRocket model](https://hub.wsu.edu/aerospace/wp-content/uploads/sites/204/2015/02/OpenRocket-Model.pdf)
- LOC BT-1.52, 34 in, no published mass: [Wildman](https://wildmanrocketry.com/products/bt-1-52),
  [LOC](https://locprecision.com/products/cardboard-airframes)
- Wadding: [hobbyetc listing](https://store.hobbyetc.com/parts/view/123056) (17 g shipping weight, 72 sheets)
- Chute: recovery's estimate (the-rocketman.com/?p=3121). Kevlar: owner's vendor table.

## 8. Open questions for the owner

1. Does the ±0.2 band apply at **liftoff only**? Burnout is ~1 cal higher whatever we do.
2. Ballast material and form: it needs ≥ 3.54 g/cm³ packed to fit tip→100 mm.
3. The club's rail length and the minimum rail-exit speed you want.
4. Lighter-and-faster (s50, 43 g ballast, M 0.85) or heavier-and-slower (s40 + ballast)?
5. Weigh the tube, the chute and the Kevlar once they are in hand.
