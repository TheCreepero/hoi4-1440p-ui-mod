# Phase A6: army overview tab

The panel the `o`, `p` and `l` keys open: Division Overview, Navy Overview and Air Forces Overview, three tabs of one window. Status: built and checked by the harness on 2026-10-14, while the user was away; awaiting the tester's judgement. Override file: `interface/zz_1440p_army_overview.gui`.

## Scope

- Vanilla file and windows, all in `countryarmyview.gui`: `countryarmyview` (the panel, with the header and list of each tab), the rows `armyview_army_entry`, `armyview_navy_entry` and `armyview_air_entry`, and `modifier_entry` (one modifier of the header). Two windows that slide in beside the panel: `equipment_overview_window` (`equipmentoverview.gui`, Equipment Details) and `navallosseswindow` (`naval_losses.gui`, Sunk Ships).
- What the vanilla screen crams or hides:
  - A row is 511 px: a division's name has 170 px in `hoi_18` ("Kavallerie-Kommando Inst..."), a fleet's 148 ("I. U-Boots Flottille We..."), a wing's 130 ("Küstenfliegergrupp..."); the region of a fleet has 122 ("North-West Germ...").
  - Theatre and army share one box on two lines; the army column holds only the army's shield.
  - Organisation and strength are two bars of 6x28 px, standing up.
  - The panel is 550 px wide; the area column of the air tab starts at x 397 and is mostly off the panel's visible part.
  - No button has a hotkey but Close.
- Out of scope: the windows the rows open (division, ship and wing details, A3), the naval HQ window (centred, unaffected), any new value (see Inventory).

## Inventory

- Vanilla references: `reference/vanilla/army_overview*` (the three tabs, Sunk Ships, Equipment Details, and what a row's details button does), refreshed on 2026-10-14.
- Where the window sits: `countryarmyview` at -6,78 (its `show_position`), as high as the screen. The scene marks it `sidePanel`.
- `Show-CodeNames`: no window has a widget the code would fill and vanilla leaves out (`mission_icon_` is the prefix of `mission_icon_1` to `_4`).
- The code shows one tab's header container and list and hides the other two. The scene's default state is the army tab; the captures `navy` and `air` hide the others.
- Lists: `army_units/item_grid`, `navy_units/item_grid` and `air_units/item_grid`, three grids of one name in one window, each with a real slot of 511x35. Entry pairs in `tools/gui-links.json` as `container/grid`, which the test suite and the renderer now read.
- The header containers (`info`, `army_header`, `navy_header`, `air_header`) and the lists have a margin of 13 left and top. The renderer does not model margins: the mod's header containers have none, and their children carry the 13 px; the lists keep theirs and the scene places their grids (`place`).
- Bitmap backgrounds: the three rows (`armyoverview_entry_bg.dds` and its navy and air twins, 509x35, olive parts and dark boxes), the title bar (`header_bg.dds`), the picture strip (`overview_top_strip.dds`, three frames the code switches per tab), the filter box, the plate under the list (`trade_header.dds`) and a modifier's plate. Option 4 for all: `tools/stretch_background.py`, jobs `ao_*`.
- Names measured with the fonts (`scratch/a6/measure.py`): of 27 485 division names in `names_divisions`, 90 % are at most 224 px and 99 % at most 291 px in `hoi_18mbs`; strategic regions at most 187, states at most 157.

## Proposal

Built without a proposal round: the user asked on 2026-10-14 for A6 to A8 to be done while they were away. What the player should see at once: every division, fleet and wing with its whole name and every column on one line, so the list reads as a table.

| Panel or column | Vanilla | Built | Why |
|---|---|---|---|
| Panel | 550 wide | 900 wide | rows of 861 |
| Division row | 511: name 170, theatre and army on two lines in 140 | 861: name 280, theatre 160, army 138, each on one line | names whole; one line per row |
| Fleet row | name 148, region 122 | name 360, region 196 | |
| Air wing row | name 130, base 124, region 120 with the missions under it | name 278, base 138, region 130 with the four mission icons beside it | "Kampfgeschwader 253 'General Wever'" (258 px) of the user's playset |
| Bars of a row | 6x28 standing | 48x9 lying, the division list's sprites (A2) | |
| Row font | `hoi_18` | `hoi_18mbs` | |
| Modifiers | tiles of 74 | tiles of 122, value in `hoi_18mbs` | seven fill the width |
| Counts by type (sub-units, ships, planes) | six a row | ten a row | |
| Sort buttons | vanilla widths | over the new columns | |
| Filter box | 177 px | 300 px, at the right of the picture strip | |
| Air list | starts at y 292 | at y 257, as the army list | one more row |
| Equipment Details, Sunk Ships | slide in at x 540 | at x 890 | at 540 they open under the wider panel |

Additions, each with the row of "What a redesign can add" that allows it:

- Hotkey `shift+i` on Equipment Details (`details_open`): "Hotkeys". Pressed in check 3: the window opened. Free in vanilla and in the user's playset.

## Decisions

- 2026-10-14: **900 px**, decided without the user (they had stepped away and asked for the work to go ahead). The width is what one line per column needs at the measured name lengths; whether it is too much is for the tester.
- 2026-10-14: the theatre and the army get a box each instead of two lines in one. The army's shield stays at the row's end.
- 2026-10-14: the counts by type stay two rows high (the code fills at most two), so the header is as high as vanilla's; the extra width gives ten types a row.
- 2026-10-14: the air name column was 250 px and cut "Kampfgeschwader 253 'General Wever'" in the user's playset (check 4); it is 278 now, from the base and region columns, which stay wider than vanilla's.
- 2026-10-14: Equipment Details and Sunk Ships open at x 890. Sunk Ships also opens from the logbook button of a sea region's view at the lower left, where it now stands 350 px further right than in vanilla.
- 2026-10-14: `army_view_subunit_entry` was copied into the file and left unchanged, so it was taken out again.

## Game checks

| # | Date | Build | Checked | Result | Screenshot | Taught |
|---|---|---|---|---|---|---|
| 1 | 2026-10-14 | b34ad34+dirty | first build: the three tabs | the army tab as rendered, the sort buttons and row icons at 0 px; Army 1 was not made in this start, so the rows said "Unassigned"; the tab captures were skipped after the expect list failed (it named the row's details button, which is mostly transparent) | `scratch/checks/army_overview-20261014-163649*` | H37 |
| 2 | 2026-10-14 | b34ad34+dirty | the same with the sort buttons as expect widgets, kept open; Shift+I and a click on Equipment Details | verified; the three tabs as rendered. Shift+I and the button showed nothing: the window opened under the panel | `army_overview-*-20261014-1640*`, `a6_hk-*`, `a6_det*` | S32 |
| 3 | 2026-10-14 | b34ad34+dirty | Equipment Details and Sunk Ships at x 890, a row's details button; stored as reference | verified; both windows beside the panel; Shift+I opens Equipment Details; the details button selects the division and closes the overview | `reference/mod/army_overview*` | W29, W30 |
| 4 | 2026-10-14 | vanilla | the same recipes without the mod, stored as reference | vanilla's details button does the same | `reference/vanilla/army_overview*` | W30 |
| 5 | 2026-10-14 | b34ad34+dirty | with the user's playset (55 mods, this one last) | verified; "1. Infanterie-Division (mot.) 'Königsberg'" whole; "Kampfgeschwader 253 'General W..." cut | `scratch/checks/army_overview-*-20261014-1658*` | - |
| 6 | 2026-10-14 | b34ad34+dirty | the air name column at 278; stored as reference | verified, the long wing name whole in the render (the vanilla game names it "Kampfgeschwader 253") | `reference/mod/army_overview*` | - |

Not seen in game (states a paused 1936 start does not show):

- A division in combat, with a decommissioned template, an expeditionary or exile flag; a wing with an ace, a mission or on a carrier; a fleet on a mission or in combat.
- More than ten types of division, ship or plane (a second row of counts).
- Typing into the filter box; the sort buttons clicked.
- A list long enough to scroll to its end.

## Left for the tester

1. Whether 900 px is too much for this panel (vanilla 550).
2. Tooltips on the bars, the level icon, the army shield and the modifiers.
3. The sort buttons, and typing a name into the filter.
4. A division in combat and a wing on a mission: the battle icon and the four mission icons beside the area.
5. Sunk Ships from a sea region's logbook button: it opens at x 890 now.

## Close

- [x] Roadmap status and link
- [x] README "Reworked screens"
- [x] Workshop description
- [x] `version` in `descriptor.mod` (1.7, with A7 and A8)
- [x] Engine Facts rows confirmed or added
- [x] Scene file (`tools/scenes/army_overview.json`); the move `select_fleet` clicks the first fleet row by name
- [x] Finished screen stored under `reference/mod/`
- [ ] The tester's judgement
