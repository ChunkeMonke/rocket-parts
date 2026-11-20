# l1-cheap — Payload & Avionics (Phase 2 scoping)

**Status:** Phase 2 · 2026-11-20 · payload agent

> **SUPERSEDED (owner update 2026-11-20):** there WILL be a payload, a Quasar-LR. See §Quasar-LR at the end. The "no payload" default and add-on table below are kept for the record.

## Default: no payload
The owner has not asked for a payload, and feasibility.md plans motor ejection with no
electronics. So the design carries **nothing**: `contents: none (pending owner confirmation)`,
`mass_g: 0`, `bay_length_mm: 0`. No bay, no sled, no static vent holes.
An L1 cert flight needs no altimeter or tracker (feasibility.md §1 lists none).

## Optional add-ons (owner decides; none added)

Budget room from feasibility.md §4: **$21.01 (high case) to $41.16 (low case)** is left for
lines that are still TBD (tube $9.30 now chosen, rail buttons, wadding, non-hazmat shipping).

| Option | What it buys on an L1 flight | Price (source, date looked up 2026-11-20) | Mass | Power | Budget effect |
|---|---|---|---|---|---|
| **A1. Eggtimer Apogee** (kit, you solder it) | Beeps out the peak altitude after landing. It is also a deploy controller, but you would fly it as an altimeter only, with no charge wired. | $15 list + $5 battery (required) = **$20**. Price from a [Rocketry Forum post](https://www.rocketryforum.com/goto/post?id=2051607), date unknown; check eggtimerrocketry.com. Assembled: [Contrail $39.99](https://contrailrockets.com/product/eggtimer-apogee-altimeter) | TBD (not found) | Eggtimer battery (in price) | -$20; fits the low case, uses about all of the high case |
| **A2. Estes Altimeter 2246** | Peak altitude on its display, stores 10 flights | [$43.99 Estes](https://estesrockets.com/product/002246-estes-altimeter/) | 11.8 g (0.415 oz, [Estes EDU](https://edu.estesrockets.com/products/altimeter)) | replaceable battery, included | -$44; **over budget** in both cases |
| **A3. Jolly Logic AltimeterOne** | Peak altitude, speed, rechargeable | [$59.95 LOC Precision](https://locprecision.com/products/jolly-logic-altimeterone); [$50.00 Aerocon](https://aeroconsystems.com/product/altimeter-one-by-jolly-logic) | 9.9 g ([LOC](https://locprecision.com/products/jolly-logic-altimeterone)) | built-in LiPo, USB charge | -$50 to -$60; **over budget** |
| **B. Sonic beeper**, e.g. Lucid RB02 | Loud tone (about 108 dB at 10 cm) that helps you find the rocket in brush or trees | **TBD**, no unit price found. Spare battery $6.00 ([Lucid](https://lucidtechnologies.info/rb02_11.htm), undated) | 9.75 g without battery ([Lucid](https://lucidtechnologies.info/rb02_11.htm)) | 150 mAh LiPo | TBD |

Notes:
- Only **A1** fits the $100 cap, and only if the other TBD lines come in low. The cert gains
  nothing from it. What you get is your real altitude next to the sim's prediction.
- Palm Bay is flat, open ground. A beeper helps most if the rocket might land in palmetto
  or tall grass. Whether that applies to this field is for the owner or club to say.
- **If one is chosen:** with single deploy there is no avionics bay. A small altimeter
  would ride in the nose cone or be tied to the shock cord in a padded pouch. Either way it
  shares space with the recovery agent and the nosecone agent, and gets static vent holes
  sized by the maker's instructions. I will not size the holes until a model is chosen and
  its manual is in hand.

## Open questions for the owner
1. Confirm **no payload** for this flight.
2. If you want one: altimeter (A1 is the only one that fits the budget), beeper, or both?
3. If A1: are you OK soldering a through-hole kit before 2026-12-14?

---

## Quasar-LR (owner update 2026-11-20)

### Identification (owner to confirm)
Most likely the **Eggtimer Rocketry Quasar-LR**. Eggtimer says the original Quasar "has been
replaced by the Eggtimer Quasar-LR, which uses a LoRa radio module", and that it needs the new
**LCD-LR receiver**; the old Eggfinder LCD will not work
([Eggtimer Quasar FAQ](https://eggtimerrocketry.com/quasar/), via search 2026-11-20).
What it is: a barometric **recording altimeter + GPS tracker + telemetry radio**, with 3
deployment outputs, set up over WiFi from a phone
([User's Guide 1.02S](https://eggtimerrocketry.com/wp-content/uploads/2024/02/Eggtimer-Quasar-1_02s.pdf)).
On this rocket the outputs stay **unwired**, because the motor ejection does the deploy.
I could not open eggtimerrocketry.com from this session (proxy 403), so everything below comes
from search snippets. **Please send the Quasar-LR manual PDF**, or measure the board.

### Specs found (mostly for the ORIGINAL Quasar; LR values TBD)
| Item | Value | Source |
|---|---|---|
| Board | ~140 × 27.7 × 12.5 mm (original) | Eggtimer FAQ |
| LR board | same hole layout, but **stacked** (about 6 mm between boards), so taller than 12.5 mm; actual height TBD | Eggtimer owner, [Rocketry Forum](https://www.rocketryforum.com/threads/the-eggtimer-quasar-a-wifi-enabled-gps-altimeter.175766/) |
| Mass | ~28 g (original, no battery); LR TBD | Eggtimer FAQ |
| Battery | 2S 7.4 V LiPo, 500 mAh or more (original); its mass and size depend on the pack you choose, so TBD | Eggtimer FAQ |
| Price | kit $100 (original Quasar listing; LR price not confirmed) + LCD-LR receiver TBD + battery TBD | Eggtimer FAQ |
| Vents | 1/4 in hole area per 100 in³ of bay volume, 3 holes preferred; size "not terribly critical"; don't put the sensor directly across from a hole | User's Guide 1.02S |
| Antenna | no guidance found; TBD from the LR manual | — |

### Fit check: nose cone (from nosecone.md: ogive L 165, R 20.64, wall 2.2, shoulder ID 34.155, 5 mm aft bulkhead)
Script: `/tmp/claude-0/-home-user/c895d01b-a099-5773-be20-859042f2dc61/scratchpad/fit.py`.
- The original board's cross-section has a 30.4 mm diagonal. The cone's inner diameter only
  reaches that 99.3 mm from the tip.
- That leaves **100.7 mm** to the bulkhead, against **140 mm** needed, before adding the battery.
- With the taller stacked LR, it gets worse: at an assumed 18.5 mm height, only 83.7 mm is usable.
- **Verdict: it does not fit in the nose cone.** The nose cone also has a sealed, integral
  bulkhead, which leaves no access.

### Proposal: a short tube bay that rides with the nose
- Cut a section from the 34 in BT-1.52, about 140 mm board + battery + bulkhead; length TBD.
  The nose shoulder plugs into its forward end.
- The aft end gets a sealed bulkhead carrying the shock-cord eye. It keeps ejection gas off
  the board and ties the bay to the recovery harness. The deploy split stays at the booster joint.
- The board goes on a printed sled, flat across the tube. The tube ID of 38.735 allows a stack
  up to about 27 mm tall at 27.7 mm wide: √(38.735² − 27.7²) = 27.1 mm, minus the sled.
- GPS/LoRa: PETG and paper are non-metallic, so I expect little RF blockage (judgement, not a
  cited source). Keep the antenna away from any metal ballast.
- Vents: the Eggtimer rule gives 3 holes of about 1.20–1.39 mm for a 150–200 mm bay.
  **Provisional: 3 × ~1.3 mm**, spaced 120° apart and not facing the sensor.
- The pouch-on-shock-cord option is rejected. The board would sit in ejection gas and pressure,
  which corrupts the baro data, and a loose ~28 g+ board would whip around on the cord.

### Budget flag
Even half of a $100 kit is **$50**. That is more than the $21–41 feasibility left, before the
receiver and battery. The owner must say whether the Quasar is counted inside the $100 cap.

### Open questions
1. Is it the Eggtimer Quasar-LR? Please send its manual.
2. Battery pack model or mass? Do you already own an LCD-LR receiver?
3. Cost split, and is it inside or outside the $100 cap?
4. Does the other co-owner need it back intact by a set date?
