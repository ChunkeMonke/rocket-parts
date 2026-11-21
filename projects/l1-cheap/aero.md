# Project: l1-cheap — Phase 2 Aerodynamics

## 0. Fin optimisation, min-diameter H100W (2026-11-21) — supersedes sections 1–5 for fin geometry

**Owner request:** "Optimize the shape of the fins for maximum stability and update the fin can model."
**Reading:** the owner's band is 1.8 ± 0.2 cal at liftoff only (`design.yaml owner.stability_*`). So I design for the top of
the band, **2.0 cal with zero nose ballast**, at minimum drag and mass. A build error of −0.2 cal then still lands at 1.8 or more.

### 0.1 Constraints used
- **Body:** 165 mm tangent ogive (`nosecone:`), 863 mm tube (`stability.body_tube_length_mm`), OD 41.275 (shop).
  - fin_can_md rev 3 sleeve: OD 46.795, lip 2.67, 20 mm fairing (46.795 → 43.135), step down to the tube.
  - The aft face is 165 + 863 + 2.67 = **1030.67 mm** from the tip.
- **Printing:** the fin can prints aft face down with the TE flush on the bed and no overhang. The TE is therefore straight at the aft face, and **sweep = Cr − Ct is forced**, not a free variable.
  - Z = max(Cr, sleeve 100) + 20 ≤ 256.
  - XY extent ≈ √3·(23.40 + s) + t/2 ≤ 256, so **s ≤ 122.7 mm**. This was checked against rev 3: 112.3 calc vs 112.4 model.
  - Tip chord ≥ 4t (t/c ≤ 25 %) is my choice.
  - TE 0.84 mm (shop: 2 outer-wall lines).
- **Sleeve overlap:** I assumed it stays at 100 mm when Cr < 100. That keeps the joint length; the call belongs to fin_can_md.

### 0.2 Mass table and CG (liftoff, zero ballast)
| Item | g | CG from tip, mm | Basis |
|---|---|---|---|
| Nose | 52.7 | 119.9 | nosecone ESTIMATE |
| Tube 863 mm | 93.6 | 596.5 | ESTIMATE, 0.1085 g/mm |
| Chute 57 + Kevlar 10.7 + wadding 2 | 69.7 | 815.7 | ESTIMATES. Pack rests on the motor's forward end (stability assumption; 120 mm pack) |
| Rail buttons | 5 | 730.7 | ESTIMATE, 300 mm from aft |
| Retention 3 × M3 | 5 | 1026.7 | ESTIMATE |
| Motor H100W loaded | 261 | 953.2 | `motor:`; CG at mid-length ASSUMED, aft end flush with the aft face |
| Sleeve + lip + fairing + bosses | 58.1 | 977.9 | CadQuery (rev 3 geometry without fins, solid PETG 1.27) |
| Epoxy | 10 | 980.7 | ESTIMATE |
| 3 fins, 50/30/77/6 | 52.4 | 1007.8 | Analytic: section area = c(0.6746t + 0.42) mm², NACA + TE blend. CadQuery with fillets/bosses: **50.6 g** |
| **Total** | **607.6** | **816.5** | |

Rev 3 model mass with these fins: **108.7 g** (CadQuery, solid). That is the new verify target candidate.

### 0.3 Barrowman CP, M ≈ 0, reference d = 41.275
- Components (CNα @ x, mm):
  - Nose: 2.000 @ 76.9 (k = 0.466).
  - Step 41.275 → 43.135: 2[(43.135/d)² − 1] = 0.184 @ 910.7.
  - Fairing cone 43.135 → 46.795: 0.386 @ 920.8, using x = L/3·[1 + (1 − d₁/d₂)/(1 − (d₁/d₂)²)].
  - Fins: K = 1 + 23.40/(s + 23.40). CNα = K·4N(s/d)²/[1 + √(1 + (2l_m/(Cr+Ct))²)]. For 50/30/77: K = 1.233, l_m = 77.65, **16.175 @ 1000.0**.
- **CP = 899.0 mm. RocketPy 1.13 gives 899.1** (single-cone tail model), 905.4 at M 0.5 and 917.4 at M 0.8. The CP only moves aft in flight.
- **The rev 3 fins (100/40/40/5) give CP 782.3 against CG 811.3, which is −0.70 cal: UNSTABLE.**
- **The owner's OR fins**, read off p.14 at a 1:1 scale bar (≈102/40/46/60, labelled read-off), give **≈ 0.0 cal** with this mass table.
  - The owner's OR shows 2.12 cal because its CG is 747 mm: nose 80 g, tube 151 g, chute drawn about 350 mm from the tip (read off p.1).
  - The owner's OR CP is 834.7 mm. My Barrowman for the same fins on the plain tube is ≈ 803. The difference is unexplained, so check it in OR.

### 0.4 Sweep and Pareto
I swept Cr 40–240, Ct 4t–Cr, and t 3/4/5/6. For each set, s was solved for the target margin.
- **Flutter:** NACA TN 4197 / Apogee PoF #291 form (section 4), at ISA sea level (P 101.3 kPa, a 340.3).
  - G_req = (V/a)²·1.337·AR³·P·(1+λ)/(2(AR+2)(t/Cr)³).
- **Drag:** fin ΔCd from the OpenRocket tech-doc method (ESTIMATE): friction Cf 0.0046 (60 µm roughness) × (1 + 2t/c̄) × wetted area, plus rounded-LE ((1−M²)^−0.417 − 1)cos²Γ, plus 0.84 mm TE base.
- **Root σ:** α 5°, q 44.0 kPa (268 m/s), one fin carries 2/3 of the set's CNα, Z = Cr·t²/6.
- **What the sweep shows:**
  - Every set at 2.0 cal needs **s ≈ 76–80 mm**. Drag differs by only about ±0.01 between planforms.
  - G_req ∝ (Cr/t)³ favours short, thick roots. Root σ favours longer roots.
  - Fin mass sits aft, so bigger fins also move the CG aft.

| Set (Cr/Ct/s/t, sweep = Cr−Ct) | Margin, d 41.3 (46.8) | Fins g | Fin ΔCd M0.5 (M0.8) | G_req MPa @268 / 291 / 402 | Root σ MPa @268/402 | XY mm | Δapogee est. |
|---|---|---|---|---|---|---|---|
| rev 3: 100/40/40/5 | −0.70 | 40.5 | 0.092 (0.147) | 34 / 40 / 77 | 1.0 / 2.2 | 112×100 | unstable |
| **1.8-cal: 50/30/71/6** | 1.79 (1.58) | 48.3 | 0.205 (0.565) | 58 / 68 / 130 | 5.4 / 12.1 | 167×148 | +13 m |
| **REC 2.0-cal: 50/30/77/6** | **2.00 (1.76)** | 52.4 | 0.224 (0.618) | **71 / 83 / 159** | 6.5 / 14.7 | 177×153 (model) | 0 |
| 2.0-cal, t 5: 50/25/76/5 | 2.00 | 41.2 | 0.190 (0.504) | 130 / 154 / 293 | 8.5 / 19.1 | 175×154 | +25 m |
| 2.0-cal, t 4: 50/20/76/4 | 2.01 | 31.6 | 0.161 (0.402) | 282 / 332 / 634 | 12.3 / 27.6 | 174×153 | +47 m |
| Lowest G: 40/40/76/6 | 2.00 | 51.9 | 0.230 | 44 / – / 100 | 8.7 / – | 176×156 | −4 m |
| Largest printable: 50/30/122.7/6 | 2.77 (2.44) | 83.5 | 0.365 (0.847) | 222 / 261 / 499 | 18.6 / 41.9 | 256×225 | ≈ −97 m |

- **Δapogee (ESTIMATE):** from the owner's own Monte Carlo regression (500 runs, R² 0.94):
  - −545 m per +100 % drag, and −236 m per +100 % mass (649 g).
  - With Cd ≈ 0.89 at M 0.5, that is ≈ −6 m per +0.01 Cd and −0.36 m/g.
  - Against the owner's thin balsa fins (ΔCd 0.096), the recommended set costs ≈ −78 m, so expect less than the OR's 1198 m.
- **Margin ceiling:** no printable 3-fin set gets past about 2.8 cal at t = 6, or 3.1 cal at t = 3 (35–40 mm chord, 123 mm span).
  - A maximum-area 236 × 122.7 fin is **unstable (−0.43 cal)**. Its fin mass and its forward LE outweigh the extra lift.
- **Over-stability costs:** above about 2 cal, a rocket weathercocks into the wind, giving a lower apogee and a longer, flatter trajectory.
  - Sources: [RocketReviews "Over-stability"](https://rocketreviews.com/over-stability-230702231653.html) and [NASA GRC Rocket stability](https://www1.grc.nasa.gov/beginners-guide-to-aeronautics/rocket-stability/), both searched 2026-11-21.
  - The extra drag and mass are quantified above.

### 0.5 Recommendation: **3 fins, Cr 50, Ct 30, s 77, sweep 20, t 6 (NACA, TE 0.84)**
- **Why:** lowest-G family at only +0.01 Cd over the drag minimum. It gives 2.00 cal with zero ballast, and 1.80 even after a −0.2 cal error.
- **Root σ:** 6.5 MPa within the layers.
  - Fallback 40/40/76/6 needs the least G (44/100 MPa) but has σ 8.7.
  - If the owner's PETG G is ≥ 300 MPa, t 5 (ΔCd −0.034, +25 m) is enough. If it is ≥ 640, t 4 is enough (1.5 × 268 m/s rule).
- **Layers:** spanwise root bending is radial, in XY, so it runs **within the layers**.
  - In-plane fin loads cross the layers in tension/shear. These are tip strikes on landing and the drag couple.
  - The 77 mm span makes landing the main risk to the printed fins.
- **Rail:** with 3 fins, a button centred between two fins puts each fin root 23.4·sin 60° = 20.3 mm off the rail centreline. That clears a 1010 rail (12.7 mm half-width) and a 1515 rail (19.05 mm). Rail size and button standoff are TBD.
  - The sleeve stands 2.76 mm proud of the tube. An aft button on the tube needs more standoff than that.

### 0.6 Caveats (read before printing)
1. **Zero-ballast margin rests on mass ESTIMATES.** Each of these changes the margin:
   - +10 g nose → +0.27 cal.
   - +10 g tube → +0.09 cal.
   - Tube 151 g (OR "LOC avg") → +0.46 cal.
   - Pack held at the nose shoulder instead of on the motor → **+1.53 cal**.
   - **Weigh the tube, nose and chute, and fix the pack position, before printing rev 4.** Ballast only raises the margin, so it cannot pull an over-margin back down.
2. **Caliber reference:** 2.00 cal on the 41.275 tube equals 1.76 cal on the 46.795 sleeve. If OR references the maximum diameter (unconfirmed, [forum](https://www.rocketryforum.com/threads/caliber.185262/)), the owner's OR will read it lower.
3. **No H100W thrust curve:** Vmax comes from the owner's OR (268 m/s; MC P95 291, max 310). Bigger fins lower Vmax, which is conservative for flutter.


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
