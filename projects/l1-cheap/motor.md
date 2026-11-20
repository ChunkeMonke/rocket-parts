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

**Thrust curve file:** `projects/l1-cheap/motor/H182R_digitized.eng`.
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

## 4. Open questions for the owner
1. Formally confirm the H182R-14A, or choose option B.
2. Measure the case OD, and the thrust ring OD and thickness, on a motor in hand (for example the vendor's stock).
3. What diametral clearance should the motor bore have?
4. What thresholds should we use for minimum thrust-to-weight and rail-exit velocity?
5. Retention: screws and inserts, or the AT 19002 retainer? Which screw size, and do you have inserts?
6. Can you download the thrustcurve.org HP-H182R `.eng` file?
7. Who at the Palm Bay launch has the AeroTech delay tool?

## 5. Hand-offs
- **Stability:** masses 207 / 92 g, length 203 mm, and the digitized `.eng`. Please send me the time from burnout to apogee so I can set the delay.
- **Aerodynamics:** the `.eng` file.
- **Recovery:** the delay will be cut down from 14 s with the AeroTech tool. The ejection charge size is not published (TBD).
- **Part library:** the bore and the aft thrust face, once the measurements are in.
