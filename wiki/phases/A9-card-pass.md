# Phase A9: card pass on the army badge and the navy header

The army badge of A2 and the fleet card of A4, each regrouped into a title strip and cards: the commander, the units, the orders or the base. Status: built on 2026-10-16 and checked by render and tests; no game check yet. Files: `interface/zz_1440p_army_selection.gui` (`army_badge_view`), `interface/zz_1440p_fleet.gui` (`fleet_view_header`).

## Scope

- Army badge: 685x97 to 685x128. Navy header: 740x166, unchanged.
- Out of scope: the task force card (it already has the three parts), the unit details headers.

## How the cards are built

- Each card is an icon of the mod (`mod1440_cp_*`) drawn behind the widgets, a vanilla tile at the card's size (`GFX_1440p_CP_*`). The vanilla widgets stay children of their window and move onto their card.
- Not containers that own their widgets, although the patched executable would find widgets in them [GUW-033]: the orders buttons of the army badge have alternative places for an army group's badge (`positionType`), which only the window's own lookups find, and the plates work on an unpatched game too.
- No widget can run out of its card: names have a `maxWidth` inside the card; the division counters are an `OverlappingElementsBoxType` that fits its items into its width (seven of 31 px side by side, more overlap; `divisions_summary_max_item_count` caps them at 16); the ship counters of the navy header have 400 px, eight classes of 50.
- Captions are vanilla text keys: `DIVISIONS`, `naval_equipment` ("Ships"), `AIR_SORT_BASE` ("Base").

## Layout

| Part | Army badge | Navy header |
|---|---|---|
| Title strip | count shield, name, supply and fuel, division count, close | insignia, name (230 px), pride, fuel, carrier base, Select All, count, colour, close |
| Commander card | 6-356: portrait, title and name (160 px), traits, skill, four stats in two rows, preferred tactic | 6-326: portrait, title and name (128 px), traits, skill, four stats in two rows |
| Strength | strength card 362-406 x 37-124: organisation and strength standing 70 px high | - |
| Units | divisions card 412-684 x 37-79: caption, counters (182 px: six side by side) | ships card 330-736 x 42-98: caption, counters |
| Orders or base | orders card 412-684 x 83-124: the five buttons | base card 330-736 x 102-160: caption, regions, home base |

## Decisions

- 2026-10-16: a 30 px taller army badge is acceptable; nothing may overflow its card in the game (user).
- 2026-10-16: plates behind widgets instead of wrapping containers (see "How the cards are built").

## Open for the next game check

- The bars under their median marks (moved after check 2; the renderer cannot show it).

## Seen in check 1

- The division list starts under the taller badge: the code places it under the badge stack [GUL-042].
- The navy toolbar stands where it did, under the header of unchanged height.
- Not seen: an army group's badge (the buttons at their army group places, the group background tile).

## Game checks

| # | Date | Build | Checked | Result | Screenshot | Taught |
|---|---|---|---|---|---|---|
| 1 | 2026-10-16 | working tree | the tester, in a 1944 game as the United States | no bugs; the division list starts under the taller badge, the navy toolbar where it was. Note: the organisation and strength bars were small in the divisions card; they now stand 70 px high (vanilla 28) in a card of their own between the commander and the divisions | `Screenshots/hoi4_22.png`, `hoi4_23.png` | - |
| 2 | 2026-10-16 | working tree | the tester, the same game | the median marks were right, the bars stood left of them: a rotated bar is drawn from 8 px left to 2 px right of its anchor in the game, which the renderer does not show. Each anchor moved 6 px past its mark | `Screenshots/hoi4_25.png` | - |
| 3 | 2026-10-16 | working tree | the tester | the bars stood under their marks, but a mark could sit above a full bar: the bars were 70 tall with their foot cut off by the container. Rule found: the bar covers y - 60 to y + 10 of its anchor, and the code draws the mark at its file y less median x 70, so the mark's file y must be the bar's foot (as vanilla). Bars at y 68, marks at 78 | `Screenshots/hoi4_26.png` | [GUL-013] |
| 4 | 2026-10-16 | working tree | the tester | bars and marks aligned; the pair stood about 2 px right of the card's middle: bars at 16 and 28, marks at 8 and 20 | (tester's note; measured on `hoi4_26.png`) | - |
