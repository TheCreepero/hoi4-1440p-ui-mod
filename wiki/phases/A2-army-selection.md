# Phase A2: selected army (badge and division list)

Reconstructed from the Roadmap after the phase closed. Status: Done (first build). The redesign of the division list, the HQ bar and the template dropdowns (2026-10-16, see "Redesign build"): built and checked by render and tests; not seen in game.

## Scope

- Vanilla file and windows: `unitview.gui`: `army_badge_view`, `army_division_list_view`, `army_division_view`, `unit_template_entry`; `army_division_stats_view` only for its template dropdown (A3 continues there).
- What the vanilla screen crams or hides: organisation and strength as two 6 px upright bars, warnings stacked on the template icon, names cut at 175 px, sort buttons without captions, a template dropdown with 6 rows and wrapped names.

## Inventory

- `tools/Show-CodeNames.ps1 unitview.gui army_division_view`: no unused widgets; `entry` and `army_division_list` unexplained (Engine Facts W4).
- Lists and their rows: `divisions_window` (a container the code fills) holds `army_division_view` 33 px apart; `divisions_grid` and `templates_grid` are filled with `unit_template_entry`. In `tools/gui-links.json` and the scene.
- Bitmap backgrounds: row (`unit_entry_bg.dds`, periodic and spread), footer plate (mirror), army and army group badges (mirror per painted area).

## Proposal

The list is 670 wide and reads as a table: two lying bars, a warnings block, full names in `hoi_20b`, captions on four sort buttons, right-hand buttons at the right edge. The template dropdown shows 12 templates on one line each. The badge goes to 685 wide so it covers the list frame behind it. `shift+u` unassigns, `shift+c` consolidates.

## Decisions

- Bars column 90 px and warnings column 96 px sent back as too wide: a column gets the width its content needs, saved width goes back to the map.
- Template dropdown sent back as too narrow.
- Badge layout agreed on a mock-up composed from the screenshot; one check.

## Game checks

| # | Date | Build | Checked | Result | Screenshot | Taught |
|---|---|---|---|---|---|---|
| 1 | 2026-10-08 | list, build 1 | list | bars column too wide | - | width is judged first (Design Rules) |
| 2 | 2026-10-08 | build 2 | list | warnings column too wide | - | |
| 3 | 2026-10-08 | build 3 | list, dropdown | dropdown too narrow | - | one entry fills three lists (Design Rules, Lists) |
| 4 | 2026-10-08 | build 4 | list, dropdown | accepted | `hoi4_8.png` | rows at y 242 + 33n, frame content starts at 181 (S3, S7) |
| 5 | 2026-10-08 | badge | badge | accepted | - | G6, S13 |
| 6 | 2026-10-08 | working tree | Army 1 with all 30 divisions and the template dropdown, unattended run, plus the vanilla reference | matches the accepted layout; with one army the list runs to y 1230 without a scrollbar, so the 760 limit is not what ends it | `scratch/checks/army_selection-*-crop.png` | H3: no reload; H12: the clicks that bring the screen up |

Not seen in game: combat icons; low supply, attrition and exile markers; the HQ deploy bar; `shift+c`; the raised list height (760); commander traits and the preferred tactic icon; the scrollbar of a long badge stack.

## Close

- [x] Roadmap, README, Workshop description, `version`
- [x] Scene file `tools/scenes/army_selection.json` (positions measured on `hoi4_8.png`)

## Redesign build (2026-10-16)

The user approved the redesign proposal of the redesign pass (review page of 2026-10-16) and chose: 44 px two-line cards (about 22 rows), the dark A9 tile with the vanilla green at about 60 % and a green rail for a selected card, and the first combat entry inside the card. Built while the user was away, without a game launch. The army badge of A9 is unchanged; the list sits under it.

Read in the executable first (GUL-043): the code places the rows one below the other by the height of the `army_division_view` window and takes the visible count, the scrollbar and the scroll step from the first row's height, so `size height = 44` gives 44 px rows.

What was built, in row coordinates (x from the row window, y from its top):

- **The card.** `army_division_view` 44 high (width 180 as vanilla). `btn_bg` at 2,0 on `GFX_1440p_UV_division_card`, two frames of 638x42 built by `tools/stretch_background.py` (job `uv_division_card`) from `tiles/tiled_plain_bg_small.dds` with the inside of the vanilla row over it, 4 px in: frame 1 the row's hatch (each row the one above moved one column, pixel copies), frame 2 the row's green at 150/255 with a 3 px rail of the green's own edge. It replaces `GFX_1440p_UV_unit_entry_bg` and `uv_unit_entry_bg.dds`, which nothing else used.
- **Left block.** `bar_org` and `bar_str` lying at 10,9 and 10,23 on new 54x10 bars (`GFX_1440p_UV_card_bar_org`, `_str`; the 48x9 bars stay for the army overview). The identity tile `unitinfo_button` at 76,6 with `unit_icon` at 75,-1 (inside the card now), `hq_template_frame` 72,2, `unitlist_exiled_icon` 78,21, flag frames 123,18, `foreign_template_flag` 124,23, `flag` 136,23, `fake_unit_icon_indicator` 143,8 (the vanilla offsets from the tile); `unitlist_priority_icon` at the tile's top left (74,1). `unit_level` at 162,3 with `xp_bar` lying under it at 162,33.
- **Line 1.** `unit_name` at 202,3, `hoi_20b`, maxWidth 285.
- **Line 2, the status tray.** `mod1440_lane_tray` (an icon, 194x17 at 309,24, `GFX_1440p_UV_lane_tray`: the identity tile's texture `unitlist_unitinfo_button.dds` as a cornered tile, border 6), drawn right after `btn_bg` and before every marker. Slots: `no_orders` and `invalid_orders` 315,25; `low_supply` 331,25 at scale 0.67; `attrition` 353,24; `obsolete_template` 373,25; `bar_prepare` lying at 409,30; `unitlist_acclimatization` 441,26; `unitlist_fuel_icon` 461,25 at 0.67.
- **Right block.** `available_medals` 495,7; `unitlist_dig_in_icon` and `unitlist_movement_icon` 518,4 with `dig_in_bonus` lying at 515,33; `btn_army` 549,5 in the 44 px slot (RBM's 43 px shields end at 592), `btn_close` 552,7; `unit_land_combat_grid` at 594,4 (slot 46x33, three slots): the first entry ends at 640 with the card, a second and third spill out over the scrollbar onto the map.
- **Sort heads** (`column_heads` sits 3 px right of the rows): organisation/strength 4-66, Template 70-156, Exp. 158-198, Name 200-311, Warning 313-397, Preparation 401-455, Fuel 457-489, Status 509-545, Army 546-592. Captions with vanilla keys on Template, Exp. and Name; legends of the column's own vanilla icon (`mod1440_legend`, `mod1440_legend_supply`, alwaystransparent) on Warning (orders mark and supply icon), Fuel, Status (the spade; its caption `LOGISTICS_STATUS_LABEL` is gone) and Army (the shield).
- **HQ bar.** `hq_window` at 7,-37, 654x42 on `GFX_tiled_plain_bg_small` (was `GFX_army_hq_bg`); `deploy_dropdown` at 8,0; `deploy` on `GFX_1440p_UV_deploy_hq_button` (two frames of 548x42: the vanilla `deploy_army_hq_button.dds` with columns 130-280 of its plain template part spread, job `uv_deploy_hq_button`); `template_icon` 118,-3, `deploy_button_template_name` 196,8 maxWidth 250 (was 85), `deploy_button_cost` 452,8 maxWidth 80 right-aligned, `deploy_button_no_commander_message` 118,8 maxWidth 400; `undeploy` 598,6. The deploy dropdown opens under the template part at x 112: 392x242, five entries.
- **Template entry** `unit_template_entry` (fills the change-template and HQ deploy dropdowns of this list and the division details window's dropdown): 360x44. `Background` 360x42 on `GFX_tiled_plain_bg_small`; a card `mod1440_card` (`GFX_1440p_UV_template_card`, the same tile at 360x42, alwaystransparent) drawn right after it (removed in fix round 2: it left the templates unclickable); `division` icon 4,0; priority chevron 56,0; flag frames 34,28, flag 35,33; `name` 88,11, `hoi_18mbs`, maxWidth 220, maxHeight 22 (one line); `cp_cost_icon` 308,10, `cp_cost_text` 332,12 (26). Grids 361 wide with slots of 360x44 and `scroll_wheel_factor` 44: change-template dropdown 392x586 (13 entries), HQ deploy dropdown 392x242 (5), division details window (`zz_1440p_unit_details.gui`) 392x234 (5, as before).
- **Renderer.** `tools/render_gui.py` reads `frames` (per window in a scene, per window name in a state): the frame the code picks for a widget. The scene draws the selected card (frame 2), the state `every-marker` the hatch.
- **Scenes.** `tools/scenes/army_selection.json`: 22 rows (the names of the 1936 Army 1); `army_division_view` and `unit_template_entry` listed with `skip` for the markers the code hides on a 1936 German division and template; the combat grid filled by `unit_land_combat_entry` (0 rows, 2 in `every-marker`); the capture `template-dropdown` drawn opened; the states `every-marker`, `unassigned`, `hq` and `hq-dropdown`. `tools/scenes/division_details.json`: sample templates and the same hide list for its dropdown.

The HQ plate (GUW-037): in the HQ slot's dropdown the code puts `GFX_army_hq_dropdown_button` (198x58) on `Background`. The card is drawn above `Background`, so every entry looks alike in all three dropdowns; the plate's 16 rows below a card lie under the next card, and below the last one they fall into the dropdown's bottom margin. Clicks pass the card to `Background` (they did not: see fix round 2).

Deviations from the design:

- The template card is a `mod1440_card` icon above `Background` instead of `Background` itself, so that the code's 198x58 HQ plate stays behind it (GUW-037). `Background` carries the same tile and stays the click target.
- The division details dropdown keeps five entries (392x234); the design named only its slot.
- `btn_army` at 549 in the design's 44 px slot at 546: a vanilla 33 px shield sits near the slot's middle and RBM's 43 px shield ends at 592, clear of the combat entry at 594.
- The HQ bar keeps y -37 as designed; where it lands under the 128 px badge is the code's (GUL-012). The render draws it behind the badge; the build figure draws the list 46 px lower, as the design's mock-up does.

Not seen in game: everything above. In particular the row spacing of 44 and the count of cards before the list scrolls; that `btn_bg` switches frames on the card sprite; the HQ bar's place, its dropdown with the HQ plate behind the cards, and the create-HQ-template entry `designer_division_entry` (198x50, not reworked) in a 44 px slot; the combat entries in their slot; low supply, attrition, the exile and colonial frames, the flag, the priority chevron, the medal indicator and the fake-intel indicator in their new places; tooltips and click targets.

Game check (with the user's permission): `tools/Invoke-GameCheck.ps1 army_selection division_details`. Checklist for the tester:

1. Division list: 44 px cards; with Army 1 selected, count the cards before the list scrolls (about 22) and note where the list ends.
2. Scroll to the end: one card per step.
3. Selected card: the dark tile with the green wash and the green rail; ctrl+click a division to deselect it: the hatch.
4. Each card: bars on the left, the template icon inside the card, the level with its bar under it, the name whole on line 1, the tray on line 2 (no-orders mark, acclimatisation, fuel), the spade over its bar, the army shield in its slot.
5. Sort heads: captions Template, Exp., Name; icons on Warning, Fuel, Status and Army; each sorts its column.
6. Change-template dropdown: card entries of 44, names on one line, up to 13 before it scrolls.
7. Division details window: its template dropdown with the same cards.
8. If an HQ can be deployed: the HQ bar at the list's width, the template name whole, the cost at the right end; its dropdown shows cards, with nothing of the HQ plate between them.
9. Tooltips of the moved markers; click targets of the tile, the medal and the shield.
10. With the playset: RBM's 43 px shields inside their slot.

### Fix round 1

From the user's in-game test (`found_issues_16102026.txt`, `army_divisions.png`, a USA save with the full playset). Not seen in game yet.

- The experience bar, the warning marks and the entrenchment bar ran out of the card: the card's hatch or green is inset 4 px, so on a 42 px card it ended at row 38 while those widgets ended at 39-41. Fix as the user asked, taller rather than smaller: `army_division_view` 44 -> 50 (rows 50 apart, GUL-043), `GFX_1440p_UV_division_card` 638x42 -> 638x48 (`DIVISION_CARD` in `tools/stretch_background.py`, job `uv_division_card`), every widget of the row but `btn_bg` 2 px lower; the inside now runs to row 44 and the lowest widget ends at 43. About 19 cards before the list scrolls (scene: 19 rows). Re-test: nothing pokes out of a card, the list steps by one card.
- The preparation bar looked lost in a dark box larger than itself: the status tray (194x17) ran under every marker of line 2, the bar included. Fix: the tray covers only the four warning markers (`GFX_1440p_UV_lane_tray` 86x17, 309-395, under the Warning head); the preparation bar, acclimatisation and fuel stand on the card, the bar on its own vanilla background. Re-test: the bar reads as a bar, the tray holds the warning marks.

### Fix round 2

From the user's report of 2026-10-16: the change-template dropdown of the division list and the template dropdown of the division details window open, but no template in them can be clicked. Re-tested by the user in game the same day: templates can be clicked again in both dropdowns.

- What the two dropdowns share is their row, `unit_template_entry`; the dropdowns themselves changed only in size since the build before the redesign. Read in the executable: `CUnitTemplateItem`'s constructor (`FUN_141696000`) ties the click handler to `Background` alone (`lambda_1`, registered on the button it looked up), then `FUN_1416ba770` enables or disables that button per row. So a click must reach `Background`.
- The redesign laid `mod1440_card` (an `iconType` on the cornered tile `GFX_1440p_UV_template_card`, `alwaystransparent = yes`) over the whole of `Background`. It was the only widget over the click target that vanilla does not have there. Vanilla never puts an icon with a cornered tile sprite over a button that takes clicks, and the cornered sprites it draws over other widgets carry `alwaystransparent` in the sprite declaration, not on the widget. Which of the two the click test reads was not traced to the end, so the cause is likely, not proven.
- Fix: the card and its sprite `GFX_1440p_UV_template_card` are gone. `Background` names `GFX_mini_tooltip`, the sprite the code puts on it in every list but the HQ slot's [GUW-037], so the render shows what the game shows, and covers the whole 360x44 row (it was 42 high, which left a 2 px strip between rows that took no click). Over it lie only vanilla's own widgets, all as vanilla has them.
- What it costs: the template rows look like vanilla's again, the mini-tooltip tile at 360x44 instead of the card tile. In the HQ slot's deploy dropdown each row shows the code's HQ plate (198x58, a sprite of fixed size): 198 px wide in a 360 px row, its lower 14 rows under the next row's plate. On those rows probably only the plate's 198 px take a click, as before the fix (a button on a sprite of fixed size is likely to take that size; not checked). A wider plate would mean declaring `GFX_army_hq_dropdown_button` again [LOAD-012], which also changes the create-HQ-template entry `designer_division_entry`; left for the user to decide.
- Re-test (with the user's permission): `tools/Invoke-GameCheck.ps1 army_selection division_details`, then by hand: (1) division list, select a division, open the change-template dropdown, click a template: the division takes it; (2) the same in the division details window; (3) if an HQ can be deployed, open its deploy dropdown and click a template. If (1) and (2) work, the card can come back as a test: on the cornered sprite with `alwaystransparent = yes` in its declaration; if it then blocks again, the fact goes into the register.
