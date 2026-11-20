# Project: l1-cheap — Phase 2 Motor (propulsion)

**Status:** Phase 2 draft, 2026-11-20. **Motor = working assumption** (owner has not formally chosen).

## 1. Motor data: AeroTech H182R-14A, 29 mm DMS single-use

Primary source: **AeroTech DMS H182R-14A spec sheet, supplied by owner 2026-11-20**.
I cross-checked it against search results quoting [ThrustCurve HP-H182R](https://www.thrustcurve.org/motors/AeroTech/HP-H182R)
and [AeroTech's product page](https://aerotech-rocketry.com/products/product_907feaa5-d1fd-0d12-e28f-37e0cfa3bb8f),
both read through WebSearch on 2026-11-20 because direct fetches are blocked. All three agree.

| Item | Value | Source |
|---|---|---|
| Total impulse | 218 N·s (49.0 lb·s) | spec sheet |
| Burn time | 1.2 s | spec sheet |
| Average thrust | 182 N | derived: 218 / 1.2. ThrustCurve also lists a calculated 175.4 N |
| Peak thrust, stated | 43 lb = 192 N | spec sheet |
| Peak thrust, plotted | about 46 lb = 205 N at about 1.18 s | spec-sheet plot, read by eye. **This disagrees with the stated peak.** The structure calc uses 205 N |
| Loaded mass | 207 g | spec sheet |
| Propellant mass | 115 g | spec sheet |
| Burnout mass | 92 g | derived: 207 − 115. Estimate: ignores the delay and ejection mass that is also lost |
| Size | 29 mm × 203 mm (1.13 in × 8.00 in) | spec sheet. 29 mm is the class, not a measured case OD |
| Delay | 14 s max, can be shortened | spec sheet |
| Certification | TRA certified, 18+ only | spec sheet |
| Thrust ring | **TBD**. Not on the sheet, and no published OD or thickness found | Phase 1 inferred a ring exists, because AeroTech also sells a "no thrust ring" variant |
| Case OD | **TBD**. Not published | measure the motor |

**Thrust curve file:** `projects/l1-cheap/motor/H182R.eng`, converted from the owner's ThrustCurve RSE file (`AeroTech_HP-H182R.rse`, AT DMS data May 2014): 216.1 N·s, peak 200.8 N, avg 175.0 N, burn 1.235 s. **Superseded (2026-11-20):** the digitized curve below was deleted.
- It is **digitized from the spec-sheet plot** (6 points) and scaled by 0.954 so the curve totals 218 N·s.
- After scaling, its peak is 195 N, so the file understates the plotted 205 N spike. Do not use the file's peak for structural sizing.
- RocketPy 1.13 reads it as 218.0 N·s total, 1.25 s burn and 92 g dry mass.
- **Replace it with the thrustcurve.org HP-H182R file.**

## 2. Tripoli L1 check (rules as recorded in feasibility.md)

| Rule | H182R | Result |
|---|---|---|
| Total impulse 160.01–640 N·s | 218 N·s | pass |
| Single motor | yes | pass |
| Average thrust > 80 N (forum claim only) | 182 N | pass, with margin |

## 3. Motor mount concept, inside the printed PETG fin can

- **Bore.** A 29 mm bore is printed into the fin can and runs along the motor axis. Its diameter is the measured case OD plus a slip clearance. The shop constants have no fit for a motor bore, so that clearance has to come from the owner.
- **Thrust bearing.** The motor's thrust ring bears on the fin can's **aft face**, an annulus around the bore.
  - The part is printed with its axis vertical and the aft end on the bed.
  - Thrust then acts along Z, which presses the layers together (compression). It does not shear them.
  - From the can, the load runs forward through the walls in Z compression, then into the airframe tube through the epoxy joint on the shoulder.
  - If the owner confirms the ring is missing, the fallback is to bear on the motor's forward closure against a printed forward stop. That load also crosses the layers in compression.
- **Retention (proposal).** Two small machine screws, each with a washer, go into heat-set inserts in the aft face. The washers overlap the thrust ring.
  - The ejection kick pulls the screws straight aft, which puts the inserts in pull-out across the layers, a weak direction for the layer bond. That is why I chose heat-set inserts over self-tapping into plastic.
  - The size of the ejection load is **TBD**; no published charge figure was found.
  - Alternative: the AeroTech 29 mm retainer, part 19002. It needs a 1.235 in OD mount body; price TBD.
- **Bearing stress.** σ = F / A, with F = 205 N.
  - The real annulus area is **TBD** until the ring OD and the bore are measured.
  - Example only, not a chosen dimension: a bore of 29 mm and a ring of 31 mm OD give A = π/4 × (31² − 29²) = 94.2 mm², so σ = **2.2 MPa**.
  - The area at which stress would reach 15 MPa is 205 / 15 = 13.7 mm².
  - 15 MPa is the shop's interlayer *shear* figure. I use it only as a conservative reference, since the shop constants have no compressive allowable for PETG.

## 3a. Retention sizing (update 2026-11-20; owner chose screws + heat-set inserts)

The proposal is **2 × M3 brass heat-set inserts**, set axially into the fin can's aft face. A screw and washer in each one overlaps the thrust ring.

### Design load (estimate)

- **Load case.** The ejection charge pushes the motor aft. AeroTech does not publish the charge size.
- **Assumed pressure: 15 psi = 0.103 MPa.** This is the top of the 10–15 psi range that charge-sizing guides treat as typical:
  - [ejection-charge calc page](https://tonuonu.github.io/MyLevel1Peregrine/calculations/ejection-charges)
  - [NAU capstone report](https://ceias.nau.edu/capstone/projects/ME/2026/F25toSp26_Rocket/files/AislinnJoyGacayan-ME476C-001-EjectionChargeandParachuteAnalysis.pdf)
- **Area.** The pressure acts on the motor's forward face, taken as π/4 × 29² = 660.5 mm² (29 mm class diameter).
- **Force.** F = 0.103 MPa × 660.5 mm² = **68 N**.
- **Margin.** I applied ×3 because the motor's fixed charge in this small bay could exceed 15 psi. **Design load = 205 N.**

### Pull-out capacity (calculated)

- I found no confirmed PETG pull-out figure for M3 inserts:
  - The [3D People white paper](https://felix-manley-n4jm.squarespace.com/s/Threaded-Inserts-White-Paper-V1.pdf) has PETG data, but I could not read the PDF; search snippets did not show which material its M3 average of 1304 N belongs to.
  - [Sculpteo's tests](https://www.sculpteo.com/en/3d-learning-hub/design-guidelines/pull-out-resistance-of-threaded-inserts-testing-and-results/) are in PA12, not PETG.
- **Calculation.** Treat the plug around each insert as failing in shear, using the 15 MPa interlayer shear figure: 15 × π × 4.0 × 5.7 = **1074 N per insert**.
- **Knock-down.** SPIROL says installation accounts for up to 75 % of insert performance ([source](https://www.spirol.com/resources/white-papers/performance-expectations-for-threaded-inserts-in-plastic-assemblies/)). Keeping 25 % gives **269 N each, 537 N for two**, so the safety factor is **2.6** on 205 N.
- **Layer direction.** The insert axis runs along Z, so pull-out loads the layer bond in shear and tension. That is the weak direction, which is why I size from 15 MPa.
- **M4 is not needed.** It also takes a 5.61 mm hole ([McMaster](https://www.mcmaster.com/products/threaded-inserts/performance~any-orientation/)), which leaves less wall beside the bore.

### Hole and boss

| Dimension | Value | Source |
|---|---|---|
| Hole diameter | 4.0 mm | [accu-components chart](https://accu-components.com/p/488-threaded-insert-hole-size-charts-for-3d-printing-pla-petg-resin), for non-flanged M3; insert OD up to 4.4 mm |
| Insert length | 5.7 mm | [Prusa / CNC Kitchen listing](https://www.prusa3d.com/en/product/heat-set-inserts-m3-standard-100-pcs/) |
| Minimum material | 4.2 mm | [McMaster 94459A769](https://www.mcmaster.com/product/94459A769/), a different insert |
| Hole depth | at least 5.7 mm | insert length |
| Boss wall | TBD | the insert maker's drawing was not readable |

### Cost (searched 2026-11-20)

- Inserts:
  - [Prusa / CNC Kitchen M3 standard, 100 pcs: $10.99](https://www.prusa3d.com/en/product/heat-set-inserts-m3-standard-100-pcs/), possibly out of stock.
  - [Zoro 94459A130, 50 pcs](https://zoro.com/bsc-preferred-heat-set-inserts-for-plastic-brass-m3-x-05-mm-43-mm-installed-length-50pk-94459a130/i/G111638281): price TBD.
- M3 screws and washers: price TBD.

### Washer geometry

- Put the insert axes at radius R outside the ring, so the screw head stays clear of the ring.
- Required overlap: washer OD/2 − (R − ring OD/2) ≥ 2 mm. The 2 mm is my proposal; the owner should confirm it.
- The washer bears on the ring's aft face. If there is no ring, it bears on the motor's aft rim.
- All dimensions are TBD until the ring is measured.

## 4. Open questions for the owner
1. Formally confirm the H182R-14A, or choose option B.
2. Measure the case OD, and the thrust ring OD and thickness, on a motor in hand (for example the vendor's stock).
3. What diametral clearance should the motor bore have?
4. What thresholds should we use for minimum thrust-to-weight and rail-exit velocity?
5. Retention: screws and inserts, or the AT 19002 retainer? Which screw size, and do you have inserts?
6. Can you download the thrustcurve.org HP-H182R `.eng` file?
7. Who at the Palm Bay launch has the AeroTech delay tool?

## 5. Hand-offs
- **Stability:** masses 207 / 92 g, length 203 mm, and `motor/H182R.eng`. Please send me the time from burnout to apogee so I can set the delay.
- **Aerodynamics:** the `.eng` file.
- **Recovery:** the delay will be cut down from 14 s with the AeroTech tool. The ejection charge size is not published (TBD).
- **Part library:** the bore and the aft thrust face, once the measurements are in.
