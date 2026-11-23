---
title: "Ms. Piggy"
subtitle: "Level 1 Minimum-Diameter Rocket · Design, Analysis & Flight Readiness"
docnumber: "L1C-EDR-001"
revision: "D"
date: "2026-11-23"
status: "Released for build — ballast decision and open items in §10"
prepared_for: "Tripoli Level 1 certification flight — Palm Bay, FL — 2026-12-14"
prepared_by: ""
revisions:
  - {rev: "D", date: "2026-11-23", description: "Professional restructure; SolidWorks fin can as design basis; slicer masses; corrected CG and ballast recommendation"}
  - {rev: "C", date: "2026-11-23", description: "Fin can rev 8/9, flight-geometry CFD, OpenRocket v2/v3 review, flight simulation"}
  - {rev: "B", date: "2026-11-22", description: "3D CFD, 65 g nose, 28 in parachute"}
  - {rev: "A", date: "2026-11-21", description: "Fin can rev 7, FEA validation against ANSYS"}
---

# Executive Summary {.unnumbered}

This report documents the design and analysis of **Ms. Piggy**, a minimum-diameter rocket intended for a Tripoli
Level 1 certification flight on an AeroTech H100W-14A motor at Palm Bay, Florida, on 14 December 2026, within a
$100 budget. The report covers vehicle configuration, aerodynamics, structures, stability, flight performance and
recovery, and lists the actions required before flight.

The vehicle is 1077 mm long and is built around a LOC BT-1.52 body tube (41.275 mm). It carries a 165 mm PETG
tangent-ogive nose cone with a screw-on ballast cap and a Kevlar attachment point. The PETG fin can, modelled in
SolidWorks, carries three swept fins of 46.1 mm span and a screw-on tail cone that also retains the motor. Recovery
is by motor ejection, with the delay drilled to 12 s, on a 28 in ripstop parachute.

::: kpis
- **1337 m** Predicted apogee *4388 ft · simulation*
- **M 0.79** Maximum speed *269 m/s at burnout*
- **1.13–1.55** Static margin, cal *target 1.8 · before ballast*
- **610 g** Liftoff mass *estimate, slicer masses*
- **24.9 m/s** Rail exit speed *1.83 m rail*
- **5.5 m/s** Landing speed *28 in parachute*
- **0.34** Fin root failure index *FEA, limit 0.50*
- **Validated** Printed thread *2.5 mm pitch, test print*
:::

## Key Findings {.unnumbered}

1. **Structural adequacy.** The reference fin can (rev 9) passes all four structural load cases with a largest
   failure index of 0.34 against an allowable of 0.50. The printed 2.5 mm-pitch thread was proven by test print.
2. **Static margin below target.** With slicer masses, the liftoff CG lies 763 mm from the nose tip
   [ESTIMATE]{.tag}. The margin is 1.13 cal on the CFD centre of pressure of the flight geometry
   [UNCONFIRMED]{.tag} and 1.55 cal on the CFD of the near-identical reference design [PROVISIONAL]{.tag}. Both
   values exceed the 1.0 cal minimum and fall short of the 1.8 cal target.
3. **OpenRocket overstates stability.** The OpenRocket model reports 2.38 cal on the same CG because the fins sit
   15 mm too far aft and the fairing is modelled as solid plastic.
4. **Performance meets the mission.** The simulated apogee is 1337 m. The 12 s delay deploys the parachute 0.4 s
   after apogee, at near-zero speed.

## Recommendations {.unnumbered}

::: decision
**Required before flight**

1. Add **approximately 25 g of nose ballast** (nose mass ≈ 90 g) to reach 1.8 cal on the conservative CFD basis; repeat the flight simulation to confirm apogee.
2. Restrain the parachute pack **approximately 300 mm from the nose tip**. A pack that slides aft onto the motor removes the stability margin.
3. Correct the OpenRocket model: fin offset −0.59 in, hollow fairing, 12 s delay, 0.143 lb nose, Kevlar cord.
4. Fit-check sleeve and collar against the actual tube and motor at assembly; the design uses published nominal dimensions.
5. Perform a ready-to-fly balance check: CG at or forward of **736 mm** from the nose tip.
:::

# Vehicle Configuration {#sec-config}

::: summary
**Summary**
Ms. Piggy is a single-stage, minimum-diameter vehicle of 1077.4 mm overall length. The motor sits directly in the
body tube and is retained by a threaded tail cone. Drawings L1C-GA-001 and L1C-AS-002 define the general
arrangement and the aft-end assembly.
:::

![General arrangement, drawing L1C-GA-001: side elevation with stations, CG and CP, parts list and notes.](figures/drawings/ga_vehicle.png){.drawing}

## Mass Properties

The OpenRocket v4 mass model was corrected by replacing its printed-part masses (156 g, fairing modelled as solid)
with slicer masses placed at their CAD centroids, and by setting the nose to its 65 g flight mass.

| Item | OpenRocket v4 | Corrected | Basis |
|---|---|---|---|
| Fin can (sleeve, fins, fairing) | 146.1 g | **97 g** | Slicer [VALIDATED]{.tag .ok} |
| Tail cone | 10.0 g | **15 g** | Slicer |
| Nose cone (incl. 2 g ballast) | 59.9 g | **65 g** | Design decision |
| Liftoff mass | 649 g | **610 g** | [ESTIMATE]{.tag} |
| CG from nose tip | 774.8 mm | **763.3 mm** | [ESTIMATE]{.tag} |

Table: Liftoff mass properties, OpenRocket v4 and corrected.

## Static Margin

| Centre-of-pressure basis | CP from tip | Margin | Ballast for 1.8 cal |
|---|---|---|---|
| CFD, flight geometry [UNCONFIRMED]{.tag} | 809.9 mm | **1.13 cal** | +25.5 g |
| CFD, reference rev 9 [PROVISIONAL]{.tag} | 827.4 mm | **1.55 cal** | +9.1 g |
| OpenRocket v4 (fins 15 mm aft) | 861.5 mm | 2.38 cal | not used |

Table: Static margin at liftoff on the corrected CG (reference diameter 41.275 mm).

::: warning
**Recovery pack position**
The margins above assume a parachute pack held approximately 300 mm from the nose tip, as in the OpenRocket
model. With the pack against the motor, the in-house model predicts 0.15 cal (unstable). The pack shall be
restrained by a bulkhead or by firm packing.
:::
