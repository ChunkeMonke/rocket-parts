# Project: l1-cheap — Phase 1 Feasibility & Certification

**Status:** Phase 1 — awaiting owner review · researched 2026-11-20
**Verdict:** **Conditional GO.** $100 works if the motor is bought at the launch (no hazmat
shipping) and the tube plus small parts come to about $40 or less.

## 1. Certification gate (Tripoli L1)

From secondary sources. tripoli.org was unreachable from this session, so **check
each item on tripoli.org/Level1 before buying**.

| Requirement | Status | Source |
|---|---|---|
| Tripoli member | ✅ owner | owner |
| Age 18+ | ✅ owner confirmed | [BYU Rocketry](https://rocketry.byu.edu/join-us/level-1-cert) |
| Rocket built by the flyer | ✅ plan | [TRA rules 2009](https://laulima.hawaii.edu/access/content/group/7f13b953-c1b5-4532-00fe-072e1311e8a4/uslipub/USLI%20KFC%20Editor/DOCUMENTS/ROCKETRY%20RELATED/TRA_Certification_Rules_2009.pdf) |
| Single certified H or I motor, 160.01–640 N·s | ✅ plan (29 mm H) | TRA rules 2009 |
| Avg thrust > 80 N, no Vmax | ⚠️ forum claim only | [Rocketry Forum](https://www.rocketryforum.com/goto/post?id=1926841) |
| Witnesses: 2× L1 or 1× L2/L3; form to prefect before the flight | ✅ arrange at launch | [BYU Rocketry](https://rocketry.byu.edu/join-us/level-1-cert) |
| Safe recovery, rocket flyable again | design for it | general |

## 2. Motor options (29 mm H)

| Option | Motor cost | Extra hardware | Avg thrust | Fit |
|---|---|---|---|---|
| **A. AeroTech H182R-14A DMS (single-use)** | $42.29–$56.40 | none | 182 N (in name) | **Recommended.** Often sold out, so reserve one with the launch vendor. |
| B. H128W / H180W / H220T reload | $34.99–$39.49 | RMS-29/180 set, $108.79–$152.99 | 128–220 N | Only works if you **borrow a case**; buying one blows the budget. |
| ✗ H13ST DMS | $52.19–$57.99 | none | ~13 N | Excluded: fails the >80 N claim, and a long, slow burn is a poor cert flight. |

Prices:
- H182R:
  - [Sirius $42.29](https://www.siriusrocketry.biz/ishop/aerotech-high-power-h182r-14a-29mm-dms-hazmat-1509.html)
  - [Apogee $50.28](https://www.apogeerockets.com/Rocket_Motors/AeroTech_Motors/29mm_Motors_Single_Use/Aerotech_29mm_Motor_H182R-14A_SU)
  - [rocket.supplies $46.99, list $56.40](https://rocket.supplies/proddetail.php?prod=A081814)
- H128W:
  - [AeroTech $39.49](https://aerotech-rocketry.com/products/product_2df7f4ec-4f83-4bb0-01ce-b9a1932c0541)
  - [Wildman $34.99](https://wildmanrocketry.com/products/h128w)
- RMS-29/180 case set:
  - [AeroTech $135.99](https://aerotech-rocketry.com/collections/a-rms-29-hardware)
  - [RouseTech $108.79](https://rousetech.net/collections/hardware/rms-29-mm/)
- H13ST:
  - [AeroTech](https://aerotech-rocketry.com/products/product_b7697119-7d82-3db0-694e-7de6ea74dd90)

Notes on the H182R-14A:
- "-14A" means a 14 s delay that can be shortened (Adjustable). Phase 2 picks the delay from
  the sim; the cut is made with AeroTech's delay tool, which you can borrow at the field.
- The standard DMS appears to come with a thrust ring; inferred from AeroTech also selling
  a "no thrust ring" version. If so, the fin can's motor mount bears on that ring. Confirm on
  the motor in hand.

## 3. Hazmat shipping

The H182R is listed as HAZMAT. Motors with propellant grains over 30 g ship as 1.4C and
carry a hazmat fee on top of ground shipping
([NAR shipping doc](https://thisistheoldsite.nar.org/wp-content/uploads/2014/05/Shipping-Rocket-Motors.pdf)).
I found no current fee amount; forum reports are anecdotal. **Plan: buy the motor from the
club's launch-day vendor** and reserve it ahead.

## 4. Rough budget check (not the Phase 4 budget)

| Line | Low | High | Basis |
|---|---|---|---|
| Motor H182R | 42.29 | 56.40 | listings above |
| 24" nylon chute | 10.25 | 14.99 | [Estes rip-stop](https://edu.estesrockets.com/products/rip-stop-parachute-24-inch), [Estes Pro II](https://estesrockets.com/products/pro-series-ii-24-inch-nylon-parachute) |
| PETG, fin can + nose cone | ~1.30 | ~2.60 | **estimate:** 100–200 g × $13/kg; firmed up after Phase 2 masses |
| Kevlar, epoxy | 0 | 0 | owned |
| 38 mm tube | TBD | TBD | price search failed; Phase 3 |
| Rail buttons, wadding/chute protector, shipping on non-hazmat parts | TBD | TBD | Phase 3 |
| **Subtotal (known)** | **53.84** | **73.99** | |
| **Spendable (100 − 5 %)** | **95.00** | **95.00** | |
| **Left for TBD lines** | **41.16** | **21.01** | |

**Lever if it's tight:** print the airframe in PETG, in sections no longer than 256 mm,
instead of buying the tube. That removes the tube price and its shipping. Trade-off: more
print time, and the joints need care.

## 5. Difficulty & risk

- **Overall difficulty: 3 / 5.** Printed structural fin can, epoxy joints, single deploy on the
  motor's own ejection charge. Not min-diameter, no electronics.
- Main risks:
  - H182R stock.
  - Hazmat fee if the motor is shipped.
  - Ejection delay chosen wrong, which Phase 2's sim fixes.
  - The PETG fin can taking motor thrust through its layers. Phase 2 will orient it so
    thrust pushes the layers together rather than sliding them apart.

## 6. Open items for the owner
1. Confirm you are 18 or older.
2. Which club or launch, and when? This decides the rail size, the motor vendor, case
   borrowing and witnesses.
3. Option A (H182R) or B (borrowed case + reload)?
4. Buy the 38 mm tube, or print the airframe?
5. The planner reads your stability tolerance as ±0.2 cal; you wrote "±2". Confirm.

## 7. Decisions (2026-11-20)
- Owner is 18 or older. Launch: Palm Bay, FL, 2026-12-14.
- Airframe tube: see the recommendation in chat on 2026-11-20. **Buy the LOC BT-1.52 (34", $9.30)**
  ([Wildman](https://wildmanrocketry.com/products/bt-1-52), [CS Rocketry](https://www.csrocketry.com/building-supplies/loc-precision/cardboard-airframes/1.52-loc-airframe-38mm.html),
  [LOC](https://locprecision.com/products/cardboard-airframes)). Printed PETG tube is the fallback if
  shipping makes the tube cost too much.
- Still open: H182R vs borrowed case; club rail size, launch-day motor vendor, waiver altitude.
