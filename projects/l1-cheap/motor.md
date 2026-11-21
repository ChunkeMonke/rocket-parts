# Project: l1-cheap — Phase 2 Motor (propulsion)

**Status:** 2026-11-21. Motor = **AeroTech H100W-14A DMS (38 mm, single-use)**, owner change. The rocket is now
**minimum-diameter**: the motor slides into the aft end of the LOC BT-1.52 (ID 38.735 mm measured). A printed sleeve
fits over the tube's aft end, and the thrust ring bears on the sleeve's aft lip.

## A. H100W-14A data (searched 2026-11-21)

All values were read through WebSearch because direct fetches return 403. No manufacturer cert sheet was readable.

| Item | Value used | Other sources | Source |
|---|---|---|---|
| Total impulse | 226.8 N·s | 234 (QA, manufacturer listing); 223.9 (RR) | [ThrustCurve](https://www.thrustcurve.org/motors/AeroTech/H100W_DMS) ("calculated"), [Wildman](https://wildmanrocketry.com/products/h100w) |
| Average thrust | 97.7 N | 100 (QA); 93.4 (RR) | Wildman labels 97.7 as the average; check: 226.8 / 2.32 = 97.8 |
| Max thrust | 137.8 N (structural value) | 131 (QA, unit misprinted "N-sec"); 130.2 (RR) | Wildman labels 137.75 as the max |
| ThrustCurve "116.1 N" | **unresolved** | — | The search snippet has no label for it. It is not avg (97.7) and not max (137.8). Check when the file arrives |
| Burn time | 2.32 s | 2.3 (TC, QA); 2.40 (RR) | Wildman |
| Loaded / propellant mass | 261 / 121 g | all agree | TC, [Quest (QA)](https://questaerospace.com/products/product_f89c2d4d-4c3c-9a99-bfd8-b2d0b1dcef8a) |
| Burnout mass | 140 g | — | derived: 261 − 121. Ignores the delay and ejection mass lost |
| Length | 155 mm | 153 (TC); 157.5 (RR) | AT/QA product name "38mm x 155mm"; QA 6.12 in |
| Delay | 14 s max, owner drills it shorter | a search summary attributes "6, 8, 10 s" to TC (unverified) | QA: "set ... using the Universal Delay Drilling Tool (UDDT), Not Included" |
| HAZMAT | **yes** | — | QA: "Requires HAZMAT shipping via UPS or FEDEX" |
| Price | **$54.99** | eRockets $54.99, out of stock | [Wildman](https://wildmanrocketry.com/products/h100w), QA, [AT catalog 03.26.25](https://cdn.shopify.com/s/files/1/0615/7592/1878/files/Model_and_HP_03.26.25.pdf), [eRockets](https://www.erockets.biz/aerotech-38mm-composite-model-rocket-motor-dms-h100w-14a-1pk-aer-081014-required-to-pay-for-ups-ground-shipping-requires-level-1-certification/) |
| MESS failures | 3 reported | — | TC (quoted); details are on motorcato.org and were not seen |

RR = [RocketReviews](https://www.pirate.rocketreviews.com/h100w.html).
Budget: $54.99 is $12.70 more than the H182R low price ($42.29).

**Thrust curve:** `motor/H100W.eng` is **TBD and not present**. The owner must download the ThrustCurve
H100W_DMS RSE or ENG file and add it to `projects/l1-cheap/motor/`, as they did for the H182R. Until then the
sim stops on the missing file. `design.yaml` points at that path on purpose, so no curve gets guessed.

## B. Tripoli L1 check (rules as in feasibility.md)

| Rule | H100W | Result |
|---|---|---|
| 160.01–640 N·s | 223.9–234 N·s, depending on source | pass |
| Single motor | yes | pass |
| Avg thrust > 80 N (forum claim only) | 93.4–100 N | pass, with only 13–20 N margin. Verify the rule on tripoli.org/Level1 |

## C. Case OD and thrust ring (critical for min-diameter)

- **Case OD: TBD.** No measurement is published. Rocketry Forum threads ask for it with no answer:
  [OD thread](https://www.rocketryforum.com/threads/can-someone-measure-the-od-of-a-38mm-dms-motor-for-me.145958/),
  [ring thread](https://www.rocketryforum.com/threads/38mm-aerotech-dms-thrust-ring-dimensions.146365/),
  [drawings thread](https://www.rocketryforum.com/threads/aerotech-dms-dimensional-drawings.181755/).
  The only figure found is AeroTech's I500T DMS page, which gives a nominal "1.500 in (38mm)" = 38.10 mm.
  If that held, the case would have 0.64 mm diametral clearance in the 38.735 tube. Labels and glue can eat that.
- **Thrust ring:** it is "built-in" ([AT DMS data sheet](https://cdn.shopify.com/s/files/1/0615/7592/1878/files/genericdms_1648304178571.pdf))
  and factory-glued. Its OD and thickness are **TBD**. One forum post says rings are "usually 3/8 in long", which is informal.
- **Advisory risk:** AeroTech's DMS thrust-ring advisory (04/2014) says to check the glued ring and to add a CA fillet or a masking-tape ring
  ([NAR notices](https://nar.org/?p=16459)). The 2017 notice applies to 54 mm only. Apogee reportedly flags the issue on its 38 mm DMS pages.
  - In this layout the factory glue joint carries all of the thrust (137.8 N).
  - A tape ring forward of the factory ring won't fit into the tube.
  - A CA fillet on the forward face would also spoil the flat bearing face.
  - **Proposal:** add a forward motor stop inside the tube (for example a printed or plywood ring epoxied at motor length). It acts as a backup thrust path. Owner decision.

**Measurement request (motor in hand, calipers):**
1. Case OD at the label, in 3 places.
2. Ring OD.
3. Ring axial thickness.
4. Ring-to-nozzle-exit offset.
5. Overall length.

## D. Thrust bearing on the sleeve lip

- **Load path:** the ring sits aft of the lip. The ring's **forward** face bears on the lip's **aft** face.
- **Lip dimensions:** lip ID ≥ case OD + clearance, so the motor can pass through. Lip ID < ring OD.
- **Print orientation:** sleeve axis vertical, lip on the bed. Thrust then acts along Z and loads the layers in **compression**. The tube's aft end butts against the lip, so the load goes straight into the tube with no PETG interlayer shear.
- **Bearing stress:** σ = F / A, with F = 137.8 N and A = π/4 (ring OD² − lip ID²), which is TBD.
  - Area that would reach the 15 MPa reference: 137.8 / 15 = 9.2 mm².
  - Example only: ring 41 mm, lip ID 39 mm → 125.7 mm² → 1.1 MPa.
- **Heat:** the paper tube now touches the case directly. The case and nozzle are hot when the ejection charge fires.

## E. Retention (proposal only)

- **Concept:** 3 × M3 screw and washer over the thrust ring, into heat-set inserts in the sleeve's fin-root bosses. This is rev 2 Option A carried over.
  - The insert axes sit outside the tube OD (≥ 41.3 mm dia), so the washers must reach inward over the ring.
  - Overlap rule: washer OD/2 − (insert radius − ring OD/2) ≥ 2 mm.
- **Ejection kick (estimate):**
  - 15 psi = 0.1034 MPa.
  - Face area: the case OD is TBD, so use the tube ID 38.735 as the upper bound → 1178.4 mm². That gives **122 N**.
  - × 3 margin → **366 N** design load. With the 38 mm class diameter instead: 117 N / 352 N.
- **Capacity:** 3 × 269 N (rev 2 knocked-down insert pull-out) = 807 N, so **SF 2.2**.
  - Insert pull-out runs along Z, which loads the interlayer bond in shear and tension (the weak direction).
- **Alternative:** a commercial 38 mm retainer won't fit, because there is no motor tube to mount it on in this layout.
- **Washers and screws:** length TBD.

## F. Open questions
1. Measure the case and ring (list in §C).
2. Do you approve the forward backup stop?
3. Thresholds for min thrust-to-weight and rail-exit velocity.
4. The ThrustCurve H100W file.
5. Your UDDT (Universal Delay Drilling Tool) step sizes.

---

# SUPERSEDED 2026-11-21: H182R-14A (29 mm) material below, kept for history


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
