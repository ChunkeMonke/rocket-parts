---
title: "Pepto B. #2"
subtitle: "Level 1 Minimum-Diameter Rocket · Design, Analysis & Flight Readiness"
docnumber: "L1C-EDR-001"
revision: "D"
date: "2026-11-23"
status: "Released for build — ballast decision and open items in §10"
prepared_for: "Project owner — Tripoli Level 1 certification flight, Palm Bay FL, 2026-12-14"
prepared_by: "l1-cheap design team (rocket-parts)"
revisions:
  - {rev: "D", date: "2026-11-23", description: "Professional restructure; owner SolidWorks design basis; slicer masses; corrected CG and ballast recommendation"}
  - {rev: "C", date: "2026-11-23", description: "Fin can rev 8/9, owner-model CFD, OpenRocket v2/v3 review, flight simulation"}
  - {rev: "B", date: "2026-11-22", description: "3D CFD, 65 g nose, 28 in parachute"}
  - {rev: "A", date: "2026-11-21", description: "Fin can rev 7, FEA validation against ANSYS"}
---

# Executive Summary {.unnumbered}

This report documents the design and analysis of **Pepto B. #2**, a minimum-diameter rocket built to fly the
Tripoli Level 1 certification flight on an AeroTech H100W-14A at Palm Bay, Florida, on 14 December 2026, within a
$100 budget. It covers the vehicle configuration, aerodynamics, structures, stability, flight performance and
recovery, and closes with the actions required before flight.

The vehicle is 1077 mm long and built around a LOC BT-1.52 body tube (41.275 mm). It carries a 165 mm PETG
tangent-ogive nose cone with a screw-on ballast cap and Kevlar attachment, and the project owner's SolidWorks
PETG fin can: three swept fins of 46.1 mm span and a screw-on tail cone that also retains the motor. Recovery is
by motor ejection, with the delay drilled to 12 s, on a 28 in ripstop parachute.

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

## Key findings {.unnumbered}

1. **Structure is adequate.** The reference fin can (rev 9) passes all four structural load cases. The largest
   failure index is 0.34 against an allowable of 0.50. The printed 2.5 mm-pitch thread was proven by a test print.
2. **Stability is below the 1.8 cal target.** With the owner's slicer masses the liftoff CG is 763 mm from
   the nose tip [ESTIMATE]{.tag}. The margin is 1.13 cal on the owner-geometry CFD centre of pressure
   [UNCONFIRMED]{.tag} and 1.55 cal on the reference-design CFD [PROVISIONAL]{.tag}. Both are above the 1.0 cal
   minimum.
3. **The OpenRocket model overstates stability.** It reports 2.38 cal on the same CG because its fins sit 15 mm
   too far aft and its fairing is modelled as solid plastic.
4. **Performance meets the mission.** The simulated apogee is 1337 m. The 12 s delay deploys the parachute
   0.4 s after apogee, at near-zero speed.

## Recommendations {.unnumbered}

::: decision
**Recommended before flight**

1. Add **≈ 25 g of nose ballast** (nose ≈ 90 g). This reaches 1.8 cal on the conservative CFD basis. Re-run the flight simulation to confirm apogee.
2. Hold the parachute pack **≈ 300 mm from the nose tip**. If it slides onto the motor, the margin collapses.
3. Correct the OpenRocket model: fin offset −0.59 in, hollow fairing, 12 s delay, 0.143 lb nose, Kevlar cord.
4. Fit-check the sleeve and collar against the actual tube and motor at assembly. The design uses published nominal dimensions.
5. Perform the ready-to-fly balance check: CG at or forward of **736 mm** from the nose tip.
:::

# Stability & Flight Performance {#sec-stab}

::: summary
**Summary**
The corrected liftoff CG is 763 mm from the nose tip. Static margin ranges from 1.13 to 1.55 cal depending on the
centre-of-pressure basis, below the 1.8 cal target, so nose ballast is recommended. The simulated flight reaches
1337 m with parachute deployment at apogee.
:::

## Mass properties

The OpenRocket v4 mass model was corrected by replacing its printed-part masses (156 g, with the fairing modelled
as solid) with the measured slicer masses at their CAD centroids, and by setting the nose to its 65 g flight mass.

| Item | OpenRocket v4 | Corrected | Basis |
|---|---|---|---|
| Fin can (sleeve, fins, fairing) | 146.1 g | **97 g** | Slicer, owner [VALIDATED]{.tag .ok} |
| Tail cone | 10.0 g | **15 g** | Slicer, owner |
| Nose cone (incl. 2 g ballast) | 59.9 g | **65 g** | Owner decision |
| Liftoff mass | 649 g | **610 g** | [ESTIMATE]{.tag} |
| CG from nose tip | 774.8 mm | **763.3 mm** | [ESTIMATE]{.tag} |

Table: Liftoff mass properties, OpenRocket v4 and corrected.

## Static margin

| Centre-of-pressure basis | CP from tip | Margin | Ballast for 1.8 cal |
|---|---|---|---|
| CFD, owner geometry [UNCONFIRMED]{.tag} | 809.9 mm | **1.13 cal** | +25.5 g |
| CFD, reference rev 9 [PROVISIONAL]{.tag} | 827.4 mm | **1.55 cal** | +9.1 g |
| OpenRocket v4 (fins 15 mm aft) | 861.5 mm | 2.38 cal | — (not used) |

Table: Static margin at liftoff on the corrected CG (reference diameter 41.275 mm).

::: warning
**Recovery pack position**
The margins above assume the parachute pack is held about 300 mm from the nose tip, as in the OpenRocket model.
If the pack slides aft onto the motor, the in-house model predicts 0.15 cal, which is unstable. Secure the pack
with a bulkhead or by firm packing.
:::

![Flight simulation at T+1.0 s, during boost: 90 m altitude, 187 m/s. Trajectory, altitude and speed histories on the right.](figures/flight_video_boost.png){width=92%}
