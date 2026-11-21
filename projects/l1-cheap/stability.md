# Project: l1-cheap — Phase 2 Stability & Integration

## 0. H100W-14A minimum-diameter re-simulation (2026-11-21) — CURRENT

**Configuration.**
- Motor: H100W-14A (`motor/H100W.eng`, 228.4 N·s, burns to 2.398 s), 261 g loaded / 140 g burnt out, aft end at the fin can's aft face, no liner.
- Airframe: 165 mm ogive + 863 mm BT-1.52 + fin_can_md **rev 5**. The sleeve (OD 46.795) covers the aft 100 mm, with a 20 mm fairing (43.135 → 46.795) and a 2.67 mm lip.
- Fins: owner OR set, 3 × 50/30/43.18/20.32/6.

**Run.** `.venv/bin/python sims/l1_cheap.py --allow-tbd --margin-plot out/sims/l1_cheap_margin_vs_time.png`, with all inputs from `design.yaml`. The sim now models the sleeve step and fairing as RocketPy tails, with the fins on the sleeve radius. Case drivers are in the session scratchpad and are reproducible with `--set`.

### 0.1 Mass budget (liftoff, pack on the motor; x from the tip)
| Item | g | x mm | Basis |
|---|---|---|---|
| Nose shell | 52.7 | 119.9 | nosecone.md ESTIMATE |
| **Ballast** | **70** | 74.6 | solved for 1.8 cal; fill tip → 100 mm needs ≥ 2.57 g/cm³ packed |
| Tube 863 mm | 93.6 | 596.5 | ESTIMATE 0.1085 g/mm (OR "LOC avg" gives 150.6 g, so weigh it) |
| Fin can rev 5 | 84.0 | 987.4 | model at 25 % infill, CG 43.3 mm forward of the aft face |
| Stop/anchor ring | 10 | 870.7 | ESTIMATE, not designed |
| Chute 57 + Kevlar 9.9 (3 × L + 0.3 m) | 66.9 | 805.7 | ESTIMATES; pack rests on the ring |
| Wadding / epoxy / buttons / retention | 2 / 10 / 5 / 5 | 855.7 / 980.7 / 730.7 / 1028.7 | ESTIMATES |
| Motor | 261 → 140 | 953.2 | motor: (CG at mid-length ASSUMED) |
| **Liftoff / burnout** | **660 / 539** | **730.1 / 680.0** | |

### 0.2 Static margin (gate 1.8 ± 0.2, liftoff only)
CP = **804.7 mm** (Barrowman M0: nose 2.000 @ 76.9, step 0.184 @ 910.7, fairing 0.386 @ 920.8, fins 7.117 @ 1000.2). RocketPy gives 804.6.

| Case (liftoff) | Ballast g | CG mm | ref 41.275 | ref 46.795 |
|---|---|---|---|---|
| Zero ballast, pack on motor | 0 | 807.8 | **−0.08 UNSTABLE** | −0.07 |
| Owner 80 g nose (27.3 ballast), pack on motor | 27.3 | 775.4 | 0.71 FAIL | 0.63 FAIL |
| Owner 80 g nose, pack at OR 457 mm | 27.3 | 736.4 | 1.66 PASS | 1.46 FAIL |
| **Solved 1.8, pack on motor (design value)** | **69.7** | **730.1** | **1.81 PASS** | **1.59 FAIL (low)** |
| Solved 2.0, pack on motor | 78.1 | 722.2 | 2.00 PASS | 1.76 PASS |
| Solved 1.8 / 2.0, pack at OR 457 mm | 32.9 / 40.9 | 730 / 722 | 1.80 / 2.00 | 1.59 / 1.76 |
| 1.8 on the 46.795 ref, pack on motor | 79.8 | — | 2.04 FAIL (high) | 1.80 |

- **Pack position sensitivity:** moving chute + cord from 805.7 to 457 mm is worth **+0.99 cal**, or about 37 g of ballast.
- **On the motor is the case to design for.** A 66.9 g pack in a plain tube has nothing to hold it 18 in from the tip during boost, so it settles on the ring. OR's position only holds if the pack is fixed there.
- **Balance check:** the ready-to-fly CG must be at **730 mm (722–739)**. That holds wherever the pack ends up, because the check measures the real CG.
- **Fin can 120 g vs 84 g:** the rev 5 model cannot reach the owner's 120 g (83.4–85.7 g), so verify FAILS. If the real can were 120 g, the CG would move aft 10.4 mm (−0.25 cal) and need 83.8 g of ballast. The lighter part is the better outcome. Replace the target with 84.0 g; that is a part-library or owner decision.
- **In flight:** the margin is lowest at liftoff (1.81), 1.88 at rail exit, peaks at 3.34 (M 0.74), and is 3.02 at burnout. See `out/sims/l1_cheap_margin_vs_time.png`.

### 0.3 CP versus the owner's OR (836.0 mm, sleeve not modelled)
- Without the sleeve, Barrowman gives **792.8 mm** and RocketPy 792.7 (OR lengths). Adding the sleeve moves the CP 12 mm aft to 804.7.
- OR's 836.0 mm implies a fin CNα of 9.36 instead of 6.97, which is **34 % more fin lift**.
- RocketPy with **4 fins** on the plain tube gives 835.0 (M0) and 837.0 (M 0.3), matching OR to 1 mm. **Check the fin count in the .ork.**
- If OR really has 3 fins, the owner should send its Component Analysis table.
- **Consequence:** if OR's CP is right, the 70 g build sits at 2.57 cal (FAIL high), and 1.8 would need about 40 g of ballast instead of 70 (CG 761.7). Until this is resolved, I use our CP (two independent methods agree), which is the stable-side choice.
- The CG side reconciles: with OR's assumptions (80 g nose, 120 g can, pack at 457 mm) we get CG 750.2 mm, against OR's 750.3.

### 0.4 Flight (pack on motor, 70 g, no wind, vertical)
- Apogee **1233 m (4044 ft)** at **13.59 s**. Burnout is at 2.40 s, so the coast to apogee is **11.19 s**.
- Vmax **250.0 m/s, M 0.737**. Max q 37.3 kPa.
- Rail exit 21.6 m/s (1.5 m rail), 24.0 m/s (1.83 m rail).
- Sensitivity: Cd ×0.7 / 0.85 / 1.3 gives 1509 / 1352 / 1061 m and coasts of 12.96 / 11.97 / 10.01 s. A 4.5 m/s wind gives 1224 m.

| Delay s | Deploy t s | Alt m | Speed m/s (nominal) | Direction | Speed m/s over Cd ×0.7–1.3 |
|---|---|---|---|---|---|
| 14 (undrilled) | 16.40 | 1199 | 21.2 | falling | 10–28 |
| 13 | 15.40 | 1218 | 15.2 | falling | 0–22 |
| **12** | **14.40** | **1230** | **7.9** | falling | **≤ 17** |
| 11 | 13.40 | 1233 | 1.9 | at apogee | ≤ 19 |
| 10 | 12.40 | 1226 | 11.7 | climbing | ≤ 30 |
| 9 | 11.40 | 1209 | 21.8 | climbing | 10–40 |
| 8 | 10.40 | 1182 | 32.3 | climbing | 20–51 |
| 7 | 9.40 | 1144 | 43.5 | climbing | 31–63 |
| 6 | 8.40 | 1095 | 55.8 | climbing | 42–77 |
| 5 | 7.40 | 1032 | 69.5 | climbing | — |
| 4 | 6.40 | 955 | 85.4 | climbing | — |

**Recommendation: DRILL TO 12 s.** It has the lowest worst-case deploy speed over the Cd spread. The pack-position, 80 g-nose, 120 g-can and wind cases all deploy at 5–11 m/s with 12 s.

**Do NOT drill to ~7 s.** The "9.5 s time to apogee → 7.2 s coast" reading is wrong:
- The owner's OR and Monte Carlo fly **H100W_DMS-6**. The chute opens at about 2.3 + 6 = 8.3 s, while the rocket is still climbing, so their 9.4–9.5 s "time to apogee" is cut short by the chute.
- OR's own deploy speed (137 mph = 61 m/s) matches our 6 s row (56 m/s).
- OR's "optimum delay 11.6 s" is the undisturbed coast, and it agrees with our 11.19 s.
- A 7 s delay deploys at 31–63 m/s while climbing. recovery.md puts the knotted-Kevlar limit at about 27 m/s, so that is a zipper or shred risk.

The motor agent should confirm the AeroTech drill steps.

### 0.5 Against the owner's OR and Monte Carlo
- **Vmax:** OR now gives 550 mph (245.9 m/s), M 0.726. We get 250.0 m/s, M 0.737 (+1.7 %). Boost drag and mass agree.
- **Apogee:** OR gives 3327 ft (1014 m); we get 1233 m.
  - If OR's current config still uses the −6 delay, its apogee is cut short. Ours is not: at 6 s we are at 1095 m, still climbing at 56 m/s.
  - The rest of the gap is coast drag. Our Cd comes from aero's ESTIMATE; OR's Cd is unknown. Our Cd ×1.3 gives 1061 m.
- **Monte Carlo:** 1199–1213 m (balsa 3 mm fins, −6 delay) is not comparable to the 6 mm printed fins.
- **Need from the owner:** OR's delay setting and the "optimum delay" for the current config.

---

> **SUPERSEDED (H182R-14A 29 mm layout, 2026-11-20).** Everything below is the old motor and
> layout (fin can rev 1–3, liner, 90.5 g ballast, 12 s on H182R). Kept for history; do not use.

**Status:** Phase 2 integration, rev 3, 2026-11-20.
- Real fin can mass (rev 2).
- Owner decisions (rev 3): the stability band gates **liftoff only**, and motor retention is a
  **friction fit + tape**.
- **PROVISIONAL:** the Quasar-LR payload mass and bay are TBD. The tube, liner, nose, chute, epoxy,
  rail-button and tape masses are estimates (§2).

**Sim.** `sims/l1_cheap.py` (RocketPy 1.13.0) reads every number from `design.yaml` and the shop
constants.
- Each component takes the owning agent's value when it is a number, and falls back to
  `stability.assumptions` otherwise.
- A strict run stops on any TBD. `--allow-tbd` leaves the item out and stamps the run PROVISIONAL.
- If the liftoff margin is ≤ 0, the flight is not simulated, because a tumble is meaningless.
- Fin can: the sim uses `stability.fin_can_model_mass_g` and `fin_can_model_cg_from_aft_mm` when those
  are numbers. Otherwise it falls back to the walls+infill estimate.
- Liner: computed from `fin_can.liner_*` × `assumptions.cardboard_density_g_cm3`.

**Sweeps.** `sims/l1_cheap_sweep.py [mass|payload|cd|nose|target|all]`.

**Margin vs time.** `--margin-plot out/sims/l1_cheap_margin_vs_time.png` prints the key-event table and
writes the plot (§3a).

**Baseline run, used for every result below:**
`.venv/bin/python sims/l1_cheap.py --allow-tbd --set payload.mass_g=0 --set payload.bay_length_mm=0 --margin-plot out/sims/l1_cheap_margin_vs_time.png`

**Rev 3 change.** Retention went from 4 g (screws + inserts) to 2 g (tape). Ballast was re-solved to
**89 g**, giving 1.81 cal at liftoff and 710 g.

**Rev 2 change.** The fin can went from a 197.3 g estimate at 1047.4 mm (weighted CG of the three
estimate items) to 171.1 g at 1047.7 mm (80.3 mm forward of the aft face). The CG barely moved; the
26 g mass cut is what matters. Adding the liner (+10.0 g),
the solved ballast dropped from 96 g to **90 g**, and the liftoff mass from 736 g to 713 g.

## 1. Headline

| Item | Value | vs. target |
|---|---|---|
| Configuration | 165 ogive nose + 863 mm BT-1.52 (uncut) + 100 mm exposed fin can, span 40, **89 g nose ballast** | |
| Length / liftoff / burnout mass | 1128 mm / 710 g / 595 g | |
| CP (Barrowman, M≈0) | 845.5 mm (RocketPy 845.4; 856.6 from M 0.8 up) | |
| CG liftoff / burnout | 770.8 / 721.4 mm | |
| **Static margin, liftoff (the gate)** | **1.81 cal** | **PASS** (1.8 ± 0.2) |
| Margin at rail exit / min in flight / max in flight | 1.90 / **1.81 (at liftoff)** / 3.28 (burnout) | reported |
| Static margin, burnout (M 0) | 3.01 cal | reported, not gated (owner 2026-11-20) |

**Why burnout is high.** The burn removes 115 g of propellant from about 256 mm aft of the CG. That
adds **+0.8 to +1.2 cal** in every practical configuration (§4).

**Without ballast the rocket is unstable:** −0.63 cal at liftoff.

## 2. Mass budget (no payload; x from the nose tip)

| Item | g | x (mm) | Basis |
|---|---|---|---|
| Nose cone | 52.7 | 119.9 | nosecone.md, ESTIMATE |
| Ballast | 89 | 74.6 | stability. Fill tip→100 mm (27.2 cm³) needs ≥ 3.27 g/cm³ packed |
| BT-1.52 tube, 863 mm | 93.6 | 596.5 | **ESTIMATE** 0.1085 g/mm = shop wall area 159.6 mm² × 0.68 g/cm³ (OpenRocket cardboard) |
| **Fin can incl. fins (rev 1 model)** | **171.1** | **1047.7** | verify mass model at 25 % infill (170.5–173.0 over 0–100 %). Solid-mesh CG 80.3 mm forward of the aft face |
| Motor liner MMT-1.14, 203 mm | 10.0 | 1026.5 | **ESTIMATE** π/4 (30.5² − 28.956²) × 203 × 0.68 g/cm³. **OD 30.5 is a placeholder**. Placed at the motor midpoint |
| Parachute, 40 in | 57 | 865.0 | recovery's ≤57 g estimate |
| Kevlar, 3.68 m × 2.91 g/m | 10.7 | 865.0 | owner; 3 × 1128 + 0.3 m allowance (estimate) |
| Wadding | 2 | 915.0 | **ESTIMATE** |
| Epoxy | 10 | 976.5 | **ESTIMATE** |
| Rail buttons | 5 | 828.0 | **ESTIMATE** |
| Retention: friction fit + tape | 2 | 1126.0 | **ESTIMATE** (owner chose tape, 2026-11-20; not weighed). Placed at the aft face (conservative) |
| **Structure** | **503.1** | **665.6** | |
| Motor, loaded / dry | 207 / 92 | 1026.5 | motor.md. CG assumed at mid-length |

The recovery pack is placed resting on the motor's forward end, its most aft (conservative) position.

## 3. Flight (nominal Cd, vertical, no wind, standard atmosphere)

Cd is aero.md's table, held at 0.83 above M 0.7 with no transonic rise (assumption).
- **Apogee:** 1285 m (4214 ft) at 13.87 s.
- **Burnout:** 1.235 s. **Coast to apogee:** 12.64 s.
- **Vmax:** 283.1 m/s (**M 0.83**). Max q 48.3 kPa.
- **Rail exit:** **25.6 m/s** on the 1.5 m rail, **28.4 m/s** on the 1.83 m rail. Rail-button geometry is
  not modelled.

**Deployment vs. delay** (timed from burnout; recovery flags: ≤ 20 m/s preferred, ≤ 27 m/s limit)

| Delay (s) | 14 | 13 | 12 | 11 | 10 | 9 | 8 | 6 | 4 |
|---|---|---|---|---|---|---|---|---|---|
| Altitude AGL (m) | 1276 | 1284 | 1283 | 1271 | 1250 | 1219 | 1176 | 1054 | 873 |
| Speed (m/s) | 12.9↓ | 3.6↓ | 6.2↑ | 16.1↑ | 26.3↑ | 37.0 | 48.3 | 74.4 | 108.9 |
| Flag | pref. | pref. | pref. | pref. | limit | too fast | too fast | too fast | too fast |

**Cd sensitivity at 12 / 13 / 14 s delay** (90 g run; the 89 g run differs by ≤ 0.2 m/s)

| Cd scale | Coast to apogee | 12 s | 13 s | 14 s |
|---|---|---|---|---|
| × 0.85 | 13.48 s | 14.6 m/s | 4.8 m/s | 5.0 m/s |
| × 1.15 | 11.95 s | 0.5 m/s | 10.2 m/s | 17.2 m/s |
| × 1.30 | 11.36 s | 6.2 m/s | 14.6 m/s | 22.0 m/s |

**Recommended delay: 12 s.** It stays ≤ 14.6 m/s across Cd × 0.85–1.3. 13 s is equally good if the
AeroTech tool offers it. 14 s goes over 20 m/s at Cd × 1.3.

## 3a. Static margin in flight (liftoff → apogee)

**How it is computed.** SM(t) = (CP(Mach(t)) − CG(t)) / d.
- **CP(M):** RocketPy's Mach-dependent Barrowman. It rises from 845.4 mm at M 0 to 856.6 mm at M 0.8.
  RocketPy caps its compressibility factor at M 0.8, so CP is flat above that.
- **Propellant m(t):** RocketPy's impulse-proportional model. It matches the RSE file's m(t) points
  (115 → 0 g over 1.235 s) within **0.05 g** at every point. The RSE has `auto-calc-mass="1"`, so it is
  computed by the same method, not measured. Propellant CG is at the motor midpoint, as in the RSE
  (cg 101.6 of 203.2 mm).
- **Delay grain + ejection charge:** the mass they burn is **unpublished**. The 92 g burnout mass
  treats it as 0 (ASSUMPTION). The sensitivity cases are 0 / 5 / 10 g, burning linearly over the 12 s
  delay at the motor's forward end.

![margin vs time](../../out/sims/l1_cheap_margin_vs_time.png)
`out/sims/l1_cheap_margin_vs_time.png`, 1.83 m rail, 89 g ballast.

| Event | t (s) | Mach | CP (mm) | CG (mm) | Mass (g) | SM, +0 g (cal) | SM, +10 g (cal) |
|---|---|---|---|---|---|---|---|
| Liftoff | 0 | 0 | 845.4 | 770.8 | 710.1 | **1.81** (minimum) | 1.81 |
| Rail exit (1.83 m) | 0.141 | 0.08 | 845.5 | 766.7 | 698.9 | 1.91 | 1.91 |
| Max q = Vmax | 1.193 | 0.83 | 856.6 | 721.6 | 595.6 | 3.27 | 3.27 |
| Burnout | 1.235 | 0.83 | 856.6 | 721.4 | 595.1 | **3.28** (max) | 3.28 |
| Coast, M 0.5 | 3.06 | 0.50 | 849.6 | 721.4 | 595.1 | 3.11 | 3.12 |
| Coast, M 0.3 | 5.63 | 0.30 | 846.9 | 721.4 | 595.1 | 3.04 | 3.07 |
| Apogee | 13.87 | 0 | 845.4 | 721.4 | 595.1 | 3.01 | 3.09 |

- **The minimum in-flight margin is at liftoff.** During boost the CP moves aft with Mach and the CG
  moves forward as propellant burns, so the margin only rises. The liftoff static margin is therefore
  the number to aim for.
- The delay/ejection loss sits aft of the CG. Losing it *raises* the coast margin, by ≤ 0.08 cal at
  10 g. It doesn't matter for safety.

## 3b. Liftoff caliber to aim for

**Guidance.** All three sources below were accessed 2026-11-20.
- The rule of thumb is **1–2 cal**, and above 2 cal counts as "over-stable": it tends to weathercock
  ([RocketReviews, over-stability](https://rocketreviews.com/over-stability-230702231653.html);
  [MIT Rocket Team wiki](https://wikis.mit.edu/confluence/x/JGf_Bg), which calls it a design suggestion).
- NASA Student Launch: "desirable 1.5 to 2.0", and "over stable if … 3.0 or greater". SL itself requires
  ≥ 2.0 on the pad
  ([NASA SL "Rocketry by the Numbers", 2023](https://www.nasa.gov/wp-content/uploads/2023/09/nasa-sl-2024-arw-rocketry-by-the-numbers-508.pdf)).

**Floor I use:** minimum in-flight margin ≥ **1.0 cal** (bottom of the rule of thumb), with
**1.5 cal** preferred (NASA's lower "desirable" value).

**Liftoff target sweep** (`sims/l1_cheap_sweep.py target`; 1.83 m rail; the wind is a sample
4.5 m/s = 10 mph, vertical rail)

| Liftoff aim | Ballast | Liftoff | SM rail exit | SM burnout (M 0) | SM max | Vmax / Mach | Apogee | v @ 12 s | Apogee / drift in 4.5 m/s wind |
|---|---|---|---|---|---|---|---|---|---|
| 1.0 | 56.5 g | 678 g | 1.09 | 2.10 | 2.37 | 294.9 / 0.868 | 1288 | 4.8 | 1284 / 67 m |
| 1.3 | 68.2 g | 689 g | 1.39 | 2.44 | 2.71 | 290.6 / 0.856 | 1287 | 5.4 | 1282 / 70 m |
| 1.5 | 76.2 g | 697 g | 1.60 | 2.66 | 2.93 | 287.6 / 0.847 | 1286 | 5.7 | 1281 / 72 m |
| 1.6 | 80.3 g | 701 g | 1.70 | 2.77 | 3.05 | 286.2 / 0.843 | 1286 | 5.9 | 1281 / 73 m |
| **1.8** | **88.6 g** | **710 g** | **1.90** | **3.00** | **3.27** | **283.3 / 0.834** | **1285** | **6.2** | **1279 / 75 m** |
| 2.0 | 97.1 g | 718 g | 2.10 | 3.22 | 3.49 | 280.4 / 0.826 | 1283 | 6.5 | 1278 / 77 m |

**Recommendation: aim for 1.8 cal at liftoff, and accept 1.6–2.0.**
- **Why 1.8.**
  - It is the owner's band centre, and the minimum in flight (it occurs at liftoff).
  - Even a −0.2 cal build error leaves 1.6, above NASA's 1.5 "desirable" floor and well above the
    1.0 rule-of-thumb minimum.
  - Rail exit adds +0.1 cal.
- **Why not lower.** Aiming at 1.5 is defensible on the 1.0 floor, but it buys very little: −12 g of
  ballast, +4 m/s Vmax, +1 m apogee. A −0.2 cal build error would then drop it to 1.3, below the 1.5
  preference.
- **Over-stability.**
  - Every target in the table goes past 2 cal in coast. The burn adds about 1.2 cal regardless.
  - Aiming 1.8 gives 3.0 at burnout, right at NASA's "≥ 3.0 over-stable" line.
  - **But** the rail exit speed is 28 m/s, so the 4.5 m/s wind angle at rail exit is only about 9°.
    Going from 1.0 to 2.0 cal costs just 4–6 m of apogee and +10 m of drift (sample wind, vertical rail).
  - So weathercocking is not a strong reason to go lower on this rocket.
- **Number to verify: ready-to-fly balance point 771 ± 8 mm from the nose tip.**
  - Ready to fly means motor loaded, chute/cord/wadding packed, ballast in, no payload.
  - ±8 mm = ±0.2 cal. If the balance point is aft of 779 mm, add about 1 g of nose ballast per mm.
  - CP 845.5 mm is calculated, not measured; a swing test checks that CP qualitatively.
  - Re-derive this number when the payload bay is added.

## 4. Mass trade: subsonic vs. light (owner decides)

*§4–6 are rev 2 runs (4 g screw retention). The tape change shifts their ballast by about 1 g, and nothing else visibly.*

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
- Stability guidance: [RocketReviews over-stability](https://rocketreviews.com/over-stability-230702231653.html),
  [MIT Rocket Team wiki](https://wikis.mit.edu/confluence/x/JGf_Bg),
  [NASA SL Rocketry by the Numbers (2023)](https://www.nasa.gov/wp-content/uploads/2023/09/nasa-sl-2024-arw-rocketry-by-the-numbers-508.pdf)
- Motor m(t): `projects/l1-cheap/motor/AeroTech_HP-H182R.rse` (owner, ThrustCurve).
- Wadding: [hobbyetc](https://store.hobbyetc.com/parts/view/123056). Chute: recovery (the-rocketman.com/?p=3121).
  Kevlar: owner.
- Fin can mass and CG: `out/fin_can/rev1/` (verify mass model, solid-mesh CG). Liner ID: `fin_can.liner_id_mm`.

## 9. Open questions for the owner

1. Ballast density: it needs ≥ 3.27 g/cm³ packed to fit tip→100 mm.
2. Rail length, the minimum rail-exit speed you want, and whether the RSO tilts the rail.
3. Light (s50, M 0.89) or heavier (s40 + ballast, M 0.83)?
4. Measure the liner OD. Weigh the tube, chute, nose and Kevlar, then do the 771 ± 8 mm balance check.
5. If you can find it, the delay-grain/ejection mass for the H182R; today it is an assumption (0, sensitivity 5/10 g).
