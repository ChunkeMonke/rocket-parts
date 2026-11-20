# Project: l1-cheap — Phase 2 Aerodynamics

**Status:** Phase 2 draft, 2026-11-20. Initial fin proposal. Masses from the nosecone,
recovery and payload agents are not in yet, so the span is left as a tuning knob for the stability agent.

Inputs:
- Body: LOC BT-1.52, OD 41.275 mm nominal (shop constants), so d = 41.275 mm and r = 20.64 mm. The tube is 863 mm max (feasibility.md).
- Motor: `projects/l1-cheap/motor/H182R.eng`, the ThrustCurve RSE conversion (216.1 N·s, burn 1.235 s). The deleted digitized file was never used.

## 1. Fin set (proposal)

| Item | Value | Reason |
|---|---|---|
| Count | **3** | Less filament, mass and drag than 4, and simpler to print. With 3 fins the Barrowman body-fin interference factor is still large (1.34). |
| Root chord Cr | **100 mm** | Long root, which keeps root bending stress low. Fin can height = 100 mm plus whatever the motor mount needs. It fits under the 256 mm Z limit. |
| Tip chord Ct | **40 mm** | Taper ratio λ = 0.4, which lowers tip mass and helps flutter. |
| Span s | **40 mm** (tuning range 30–50) | Sets the CP. See table 2. Smaller span is also better for flutter. |
| LE sweep xs | **60 mm** (= Cr − Ct) | The trailing edge is square to the axis and flush with the aft face. Printed axis-vertical with the aft end on the bed, the fin has **no overhangs**: the TE sits on the bed and the LE is an upward-facing slope. |
| Thickness t | **5 mm**, provisional | The rocket goes transonic (section 3), so flutter decides this. 5 mm is ≥ 2 × 6 wall loops × 0.42 mm, so the fin prints as solid perimeters. |
| Edges | LE rounded, TE square | Rounded LE lowers pressure drag. A square TE is simplest to print and is what the drag estimate assumes. |

Footprint: 41.3 + 2 × 40 = 121 mm diameter, inside 256 × 256.
Fin volume: 3 × 2800 mm² × 5 mm = 42.0 cm³, so **53 g if solid** (× 1.27 g/cm³). That figure is fins only. The can body and mount are added by whoever models the part.

## 2. Centre of pressure (Barrowman, subsonic)

The reference is the nose tip. Ln = nose length. Lb = body length from the nose base to the aft end, with the fin TE flush at the aft end.

- **Nose:** CNα_n = 2. X_n = k·Ln, with k = 0.466 for a tangent ogive, 0.5 for Haack/VK/parabolic, and 0.666 for a cone.
- **Fins:** CNα_f = K_fb · 4N(s/d)² / [1 + √(1 + (2 l_m/(Cr+Ct))²)], with K_fb = 1 + r/(s+r).
  - Midchord line: l_m = √(s² + (xs + Ct/2 − Cr/2)²) = √(40² + 30²) = **50.0 mm**.
  - 4·3·(40/41.275)² = 11.27.
  - 1 + √(1 + (100/140)²) = 1 + √(1.510) = 2.229.
  - Fins alone: 11.27 / 2.229 = 5.056. K_fb = 1 + 20.64/60.64 = 1.340. So **CNα_f = 6.777**.
- **Fin CP from the root LE:** ΔX_f = xs(Cr+2Ct)/(3(Cr+Ct)) + (1/6)[(Cr+Ct) − CrCt/(Cr+Ct)].
  - First term: 60·180/420 = 25.71 mm.
  - Second term: (1/6)(140 − 28.57) = 18.57 mm.
  - So **ΔX_f = 44.3 mm**, and X_f = Ln + Lb − 100 + 44.3.
- **Total:** CP = (2·X_n + CNα_f·X_f) / (2 + CNα_f), which gives

  **CP = 0.2279·k·Ln + 0.7721·(Ln + Lb − 55.7) mm** (s = 40 fin set)

**Headline:** a 165 mm (4:1) tangent ogive and Lb = 863 mm. This is an assumption; the nosecone agent has not chosen yet.
- X_n = 76.9 mm. X_f = 972.3 mm.
- CP = (153.8 + 6.777·972.3)/8.777 = **768.3 mm**. Total length 1028 mm.
- A 1.8 cal margin needs **CG = 694.0 mm** (67.5 % of length).

**Cross-check:** RocketPy 1.13 with the same geometry gives 768.2 mm at M 0, 772.0 at M 0.5 and 778.3 at M 0.9. The CP moves aft with Mach, so liftoff is the low-margin case.

**Table 1. CP (mm) for s = 40**

| Ln, shape | Lb 600 | 700 | 800 | 863 |
|---|---|---|---|---|
| 125 ogive | 530.1 | 607.3 | 684.5 | 733.1 |
| 165 ogive | 565.2 | 642.4 | 719.6 | 768.3 |
| 200 ogive | 595.9 | 673.1 | 750.4 | 799.0 |
| 165 Haack/VK | 566.5 | 643.7 | 720.9 | 769.5 |
| 165 cone | 572.7 | 649.9 | 727.1 | 775.8 |

**Table 2. Span as the knob** (Ln 165 ogive, Lb 863; Cr, Ct and xs fixed)

| s (mm) | CNα_f | CP (mm) | CG for 1.8 cal |
|---|---|---|---|
| 30 | 4.113 | 679.4 | 605.1 |
| 35 | 5.383 | 729.7 | 655.4 |
| 40 | 6.777 | 768.3 | 694.0 |
| 45 | 8.282 | 798.1 | 723.8 |
| 50 | 9.887 | 821.6 | 747.3 |

For other values: X_f = Ln + Lb − 55.7, and CP = (2kLn + CNα_f·X_f)/(2 + CNα_f).

## 3. Drag and max velocity

**Cd: ESTIMATE**, from a component buildup using the OpenRocket technical-documentation methods.
- Skin friction: Cf = max(turbulent, roughness-limited), with 60 µm roughness (assumption: "regular paint" class) and the (1 + 1/(2f_B)) body correction.
- Base drag: 0.12 + 0.13M².
- Fin LE and TE pressure drag.

| M | friction | base | fin pressure | **total Cd** |
|---|---|---|---|---|
| 0.1 | 0.527 | 0.121 | 0.055 | **0.70** |
| 0.5 | 0.514 | 0.152 | 0.092 | **0.76** |
| 0.7 | 0.502 | 0.184 | 0.142 | **0.83** |

- Cd is high because the fineness ratio is about 25, so friction dominates.
- Not included: rail buttons, nose wave drag and the transonic body drag rise. Vmax is therefore biased **high**, which is the conservative direction for flutter.

**RocketPy** setup, with **ASSUMED masses** (no agent has given them yet):
- Structure without motor: 300, 400 or 500 g, plus the 207 g motor.
- Standard atmosphere, sea level, no wind.
- 1.83 m rail (assumed; the rail size is TBD).

| Structure | Vmax | Mach | Max q | Apogee | Rail exit |
|---|---|---|---|---|---|
| 300 g | 369 m/s | 1.09 | 81.8 kPa | 1275 m | 33.6 m/s |
| 400 g | 324 m/s | 0.95 | 63.0 kPa | 1317 m | 30.7 m/s |
| 500 g | 286 m/s | 0.84 | 49.3 kPa | 1325 m | 28.5 m/s |

**This rocket is transonic.** That matters for the fins (flutter), the nose shape, and the waiver altitude (apogee about 4200–4350 ft).

## 4. Fin flutter: TBD

The method is NACA TN 4197, in the form given in Apogee *Peak of Flight* #291:

Vf = a·√( G / [1.337·AR³·P·(λ+1) / (2(AR+2)(t/Cr)³)] ), where AR = s²/A_fin and the formula is unit-consistent.

**PETG shear modulus G is not in the shop constants, so it stays TBD.** The table below inverts the formula to give the G that would be needed.
- Conditions: worst case Vmax = 369 m/s, a = 339.3 m/s, P = 98.6 kPa.
- The 1.5× column uses a margin I chose; the owner should set the real one.

| s / t | G for Vf = Vmax | G for Vf = 1.5·Vmax |
|---|---|---|
| 40 / 4 mm | 124 MPa | 279 MPa |
| **40 / 5 mm** | **63 MPa** | **143 MPa** |
| 35 / 5 mm | 44 MPa | 98 MPa |
| 30 / 5 mm | 28 MPa | 64 MPa |

Once the owner supplies G, compare it with this table. If it falls short, raise t or cut s. This formula is for isotropic solid fins at subsonic speed, so treat the result as indicative.

## 5. Fin root load path through the layers

**Orientation:** the fin can is printed axis-vertical with the aft end on the bed, the same as the motor-mount proposal.
- Layers are perpendicular to the rocket axis, and each fin is a vertical plate.
- Spanwise root bending stress runs radially, in XY. That is **within the layers**, along the wall perimeters.
- The root section is a vertical plane, so transverse shear acts within the layers too.
- The interlayer bond sees only secondary chordwise bending and twist.

**Load case (my choice, labelled):** α = 5° at the worst max-q of 81.8 kPa. That is about 3× the gust angle from a 20 mph crosswind at Vmax. One fin is normal to the flow.
- Fin CNα at M 0.9 from the Barrowman/Diederich form: 3.670, × K_fb 1.340 = 4.919 /rad (ref area 1338 mm²).
- F = q·S_ref·CNα·α = 81 753 × 1.338e-3 × 4.919 × 0.0873 = **47 N**.
- Spanwise centroid: y = (s/3)(Cr+2Ct)/(Cr+Ct) = 17.1 mm, so M = **0.805 N·m**.
- Root section modulus: Z = Cr·t²/6 = 100·25/6 = 417 mm³. So **σ = 1.93 MPa** at t = 5 mm (3.0 MPa at t = 4).
- Shear: τ = 1.5F/(Cr·t) = 0.14 MPa.

Even if all of σ were taken by the interlayer bond, it is **1.9 MPa against ~15 MPa, a factor of 7.8**. The load is mainly within the layers, so the real margin is higher. Flutter, not static strength, sizes the fins.

## 6. Open questions for the owner
1. PETG shear modulus G (MPa), and the flutter margin you want (for example 1.5×).
2. Which surface finish you plan (sets the roughness, and so the Cd).
3. The launch site's waiver altitude, given a predicted apogee of about 1.3 km.

## 7. Hand-offs
- **Stability:** CP formula and tables 1 and 2. Pick s from table 2 once the CG is known. The CP moves aft by about 10 mm at M 0.9. Fins are about 53 g, solid, sitting at the aft 100 mm.
- **Nosecone:** about Mach 1. An ogive or Haack shape is preferred over a blunt one. Send Ln and the shape.
- **Motor:** fin can root chord is 100 mm, with the TE flush at the aft face. Shared print orientation: axis vertical, aft end down.
