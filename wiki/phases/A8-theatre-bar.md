# Phase A8: theatre boxes

The boxes at the top right of the map: an army theatre with its army shields, a navy theatre with its fleet rows, the air theatres, the button for a new theatre and the strategic region under the cursor. The roadmap called this "the theatre bar at the bottom"; `theatreselector.gui`, the file it named, holds the boxes at the top right, and the army portraits at the bottom are another file (`leadergroups.gui`, not reworked). Status: redesigned as cards on 2026-10-16 (see "Redesign build"): built and checked by render and tests; not seen in game. The first build (2026-10-14) was checked by the harness. Override file: `interface/zz_1440p_theatre_bar.gui`.

## Scope

- Vanilla file and windows, in `theatreselector.gui`: the boxes `theater_group_item`, `navy_theater_group_item`, `reserve_navy_theater_group_item`, `air_theatre_free_wings_item`, `air_theatre_item`, `new_theater_group_item`, `strategic_region_item`, and the rows under a box: `army_group_box`, `fleet_row_item_box`, `reserve_fleet_row_item_box`, `air_theatre_group_row_item`.
- What the vanilla screen crams or hides:
  - A box is 300 px: the name field has 145 px, and the shields of the armies (or fleets, or air groups) share 260 px before they overlap.
  - In the rows under a navy box the count of one fleet runs into the next icon.
- Out of scope: `theatre_selection_window`, which holds the boxes (RBM's GFX Overhaul moves it; see Decisions), the shields themselves (`orders_group_item` and its navy and air twins, which RBM redraws larger), the settings pop-up of a theatre.

## Inventory

- Vanilla references: `reference/vanilla/theatre_bar*` (army, navy and air), refreshed on 2026-10-14 with the crop moved to the top right.
- Where the boxes sit (S34): the window is 760 wide at the right edge, y 117, as high as the screen less 240; its grid stacks the boxes and honours each box's own x of 430. The mod's boxes are 120 wider at x 310, so their right edge stays.
- `Show-CodeNames`: nothing the code would fill that vanilla leaves out.
- Bitmap backgrounds, all option 4 (`ts_*`): the box (`theater_group_bg.dds`, five frames), the strip along its bottom (`assign_group_button.dds`, four), the frame of the chosen box, the rows under it (`theatre_dropdown_middle.dds` and `_bottom.dds`, four each), the new theatre button and the strategic region row (three frames).
- The alerts beside a box stand at x -430 from its right edge; with the wider box they are at -550, so they stay left of it.

## Proposal

Built without a proposal round (the user asked for A6 to A8 while away).

| Panel or column | Vanilla | Built | Why |
|---|---|---|---|
| A box | 300x80 at x 430 | 420x80 at x 310 | right edge unchanged |
| Name field | 145 px | 265 px | |
| Shields of a box | 260 px | 380 px | about 12 army shields before they overlap instead of 8 |
| Rows under a box | 300 px | 420 px | |
| Gaps between shields | 8 | 12 (armies), 20 (fleet rows) | RBM's values; see Decisions |
| Strategic region row | name 155 px | name 275 px | |

## Decisions

- 2026-10-14: the boxes grow to the left, so nothing at the right edge of the screen moves.
- 2026-10-14: **the window that holds the boxes is not overridden.** RBM's GFX Overhaul moves it 24 px up (y 93); left alone it keeps that in the user's playset.
- 2026-10-14: **the gaps between shields are RBM's**: 12 between army shields, 20 between the ships of a fleet row (vanilla 8 for both). RBM's shields are larger, and with vanilla's gaps the count of one fleet runs into the next icon even in vanilla. RBM's gaps for the air rows (2 and 0) suit its own wing icons, so the air rows keep vanilla's 8.

## Game checks

| # | Date | Build | Checked | Result | Screenshot | Taught |
|---|---|---|---|---|---|---|
| 1 | 2026-10-14 | b34ad34+dirty | first build | not seen: this start made no army, so no box came up (H37); a strategic region row showed at 420 | `scratch/checks/theatre_bar-20261014-163659*` | H37 |
| 2 | 2026-10-14 | b34ad34+dirty | the army box; navy and air (a fleet, an airbase selected) | verified; the army box, the navy box with its fleet rows and the reserve row, the unassigned wings and the new theatre button, all 420 | `scratch/checks/theatre_bar-*-20261014-1640*` | S34 |
| 3 | 2026-10-14 | b34ad34+dirty | with the user's playset | the box 24 px higher than the scene expects (RBM); RBM's larger shield fits; the casualty counter of "Better Mechanics: Devastation Overhaul" covers the box's right end (see Compatibility) | `scratch/checks/theatre_bar-20261014-165846*` | - |
| 4 | 2026-10-14 | b34ad34+dirty | RBM's gaps; stored as reference | verified; the fleet counts clear of the next icon | `reference/mod/theatre_bar*` | - |

Not seen in game:

- An army group with its rows of armies (`army_group_box`), an air theatre with air groups, a theatre in combat (the attack and defence counts), alerts beside a box.
- Many armies in one theatre, where the shields overlap.

## Left for the tester

1. A theatre with more armies than fit, and an army group opened under its box.
2. The settings button, renaming a theatre in its box, the combat log button.
3. In the user's playset: the casualty counter over the box's right end, which this mod does not cause (the right edge is vanilla's).

## Redesign build (2026-10-16)

The user approved the redesign "Theatre cards at the top right" and its three decisions (battle chip left of the name, 420x80, plates behind the widgets; review page of 2026-10-16). Better Mechanics' casualty counter can be moved in game, so the layout is not drawn around it; the battle chip stays left of the name by the user's choice.

What was built, in `interface/zz_1440p_theatre_bar.gui`:

- Every box is a card of 424x78 over its 420x80 window, still at x 310 (right edge 2530): `GFX_1440p_TS_card`, five frames in the order of `theater_group_bg.dds` (army gold, grey, navy, reserve, air), composed by `theatre_card()` in `tools/stretch_background.py` from `tiled_plain_bg_small.dds`, a 6 px stripe copied from each vanilla frame, and `unit_list_header.dds` as the title plate.
- The units band (`assign_button`, `unmoveable_assign_button`): `GFX_1440p_TS_band`, 404x35 at (12,38), four frames (`theatre_band()`).
- Army box: gear (17,8), supply priority (42,8), the battle chip `mod1440_ts_battle_plate` 126x28 at (62,6) with the combat log (scale 0.72), attack (0.8) and its count at (121,11), defence and its count at (169,11); the name (196,8) 212x24; the shields in 338 px at (18,44), spacing 12; the division count on `mod1440_ts_count_plate` 48x28 at (362,42).
- Navy box: name (22,8) 330x24, the fleet priority (scale 0.85) on a chip at (364,6), fleets in 338 px, the ship count on the count chip. Reserve box: gear, name at (46,10), the combat log on a chip at (362,6). Air theatre: name (22,8) 300x24, the three priorities at x 338, 362, 386 on an 82x28 chip, wings in 338 px, the count on the chip. Ungrouped wings: the same without a count, the wings across 392 px.
- Rows under a box: 424 wide, the card's sides and stripe running on in the row's own frame colour, the vanilla dropdown frame spread to 404 as the plate (`theatre_drawer()`). The last row closes the card. `armies_box`, `navy_box`, `air_box` at (18,-6), 338 px; the reserve row's icon at (18,-7) and its ships at (52,-6), 304 px; the split-off button at (369,-8), its count at (361,4).
- The selected frame and the New Theater button (420x34 at x 2, window 420x36) are tiles of vanilla textures; the region row's plate is a tile of `unit_list_header.dds` at 338x39 with `buttonstate.lua`.
- Scenes: `tools/scenes/theatre_bar.json` (an army box; state `combat` for the battle counts) and the new `tools/scenes/theatre_bar-navy.json` (the navy box with two fleet rows, the reserve row and New Theater; its capture keeps the reference name `theatre_bar-navy`, so the `navy` capture left `theatre_bar.json`).
- Retired: `GFX_1440p_TS_group_bg`, `_assign_button`, `_dropdown_middle`, `_dropdown_bottom`, `_new_group_button` and their textures. `GFX_1440p_TS_region_bg` stays declared as the fallback of the region plate.

Deviations from the design:

- **Only `GFX_theatre_dropdown_bottom` is declared again** (in `interface/zz_1440p_vanilla_sprites.gfx`). The design took both row pieces to be used by `theatreselector.gui` alone, but vanilla `interface/military_raids/country_raids_view.gui` puts `GFX_theatre_dropdown_middle` on `raid_instance_entry` (299 wide), and a sprite is declared again only when no other screen shows it (project rules, section 2). The middle rows name the mod's `GFX_1440p_TS_drawer_middle` (the same texture); the code was seen leaving the mod's sprite on the fleet rows (game check 4).
- **No chip behind the split-off button** of a row: the code shows that button only now and then, and a plate cannot hide with it, so an empty chip would stand in every row. The design's own mock-up drew none.
- **The count chip is 48x28** (design 48x30) and the chips use a tile border of 16x14, so that the tile's edge rows and columns do not repeat inside a chip as lines.
- No `tools/gui-links.json` entries: `elements_list` is in `theatre_selection_window`, which the mod does not override, and the rows of `fleets_row_box` are 23 wide in a 420 slot; the test of each kind of link would fail on them. The scenes carry the rows.

Not seen in game: everything above. In particular the rows of an army group, the frames 2 and 4 of the card, a theatre in combat, the scaled battle buttons and their click areas, clicks on the band through the count chip, the tile sprites of the New Theater button and the region row (hover, press, the region's three states), and the cards in the user's playset (RBM's 43 px shields).

Fallbacks, ready:

- The rows of an army group come out 301 px (the code puts the vanilla middle sprite on them): declare `GFX_theatre_dropdown_middle` again too, on `ts_drawer_middle.dds`, and decide what the raids view may show (its row would draw the left 299 px of the drawer).
- The region row shows no hover or press, or the wrong state: put `GFX_1440p_TS_region_bg` (the widened bitmap, three frames) back on `strategic_region_item/background`.
- A click on the band does not go through the count chip: move the chip below `assign_button` in the file, or drop it.
- The combat log button at 0.72 is too small to hit: scale 0.8 at (64,3), and the chip 130 wide.

Game check: `tools/Invoke-GameCheck.ps1 theatre_bar theatre_bar-navy`

Checklist for the tester:

1. The army box is a dark card with a gold stripe down its left side, as wide as before, its right edge where it was.
2. Title strip from the left: gear, supply priority, the battle chip (combat log, attack, defence), the name. The gear opens the theatre settings, the name can be renamed, the combat log icon opens the combat log.
3. In a theatre at war: the attack and defence counts stand beside their icons and the icons open the battles.
4. The units band: shields at the left, the division count on its own chip at the right. Clicking the band and the chip assigns the selected divisions.
5. The selected theatre's frame goes around the whole card.
6. An army group's rows under its box are as wide as the card; the last row closes it.
7. Navy (select a fleet): the blue card, the fleet priority on its chip (click changes it), the ship count on its chip, the fleet rows and the reserve row as drawers in their own colours, New Theater below, centred.
8. Air (select an airbase): the red card, the three priorities on a chip, the wings across the band.
9. With the user's playset: RBM's shields fit in the band.

### Fix round 1

- 2026-10-16, the division count off its chip (user's test, `theater_card.png`): the count was right-aligned to x 404 on a 48 px chip at 362, so it stood on the chip's right studs. `armies_count_box`, `ship_count_box` and `air_wing_count_box` are now centred over the whole chip (maxWidth 48, `format = centre`).
- 2026-10-16, the battle chip taller than its row: the title plate (`unit_list_header` laid out at 32) is grey only on rows 8-29 of the card, so the 28 px chip at y 6 stood out 2 px above and 5 below. The plate is 40 high (`CARD_TITLE`, grey 8-37), the card 424x86 over a 420x88 window (frames and their order unchanged), the selected frame 86; title widgets +3 (chips at y 9), band widgets +8 (band at 46), the row grids at y 88, the navy scene's box 187. Re-test: the chips inside the grey of the title, the boxes stacked without overlap or gap (the code is expected to take the 88 from the window), the rows of a fleet, an air group and an army group right under their card.

## Close

- [x] Roadmap status and link
- [x] README "Reworked screens"
- [x] Workshop description
- [x] `version` in `descriptor.mod` (1.7)
- [x] Engine Facts rows confirmed or added
- [x] Scene file (`tools/scenes/theatre_bar.json`)
- [x] Finished screen stored under `reference/mod/`
- [ ] The tester's judgement
