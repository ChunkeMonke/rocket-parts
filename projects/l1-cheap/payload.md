# l1-cheap — Payload & Avionics (Phase 2 scoping)

**Status:** Phase 2 scoping pass · 2026-11-20 · payload agent

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
