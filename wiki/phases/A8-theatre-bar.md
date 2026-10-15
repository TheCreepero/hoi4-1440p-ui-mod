# Phase A8: theatre boxes

The boxes at the top right of the map: an army theatre with its army shields, a navy theatre with its fleet rows, the air theatres, the button for a new theatre and the strategic region under the cursor. The roadmap called this "the theatre bar at the bottom"; `theatreselector.gui`, the file it named, holds the boxes at the top right, and the army portraits at the bottom are another file (`leadergroups.gui`, not reworked). Status: built and checked by the harness on 2026-10-14, while the user was away; awaiting the tester's judgement. Override file: `interface/zz_1440p_theatre_bar.gui`.

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

## Close

- [x] Roadmap status and link
- [x] README "Reworked screens"
- [x] Workshop description
- [x] `version` in `descriptor.mod` (1.7)
- [x] Engine Facts rows confirmed or added
- [x] Scene file (`tools/scenes/theatre_bar.json`)
- [x] Finished screen stored under `reference/mod/`
- [ ] The tester's judgement
