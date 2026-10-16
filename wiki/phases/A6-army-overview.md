# Phase A6: army overview tab

The panel the `o`, `p` and `l` keys open: Division Overview, Navy Overview and Air Forces Overview, three tabs of one window. Status: redesigned on 2026-10-16 (banner and rail of cards, see "Redesign build"): built and checked by render and tests; not seen in game. The first build (2026-10-14) was checked by the harness. Override file: `interface/zz_1440p_army_overview.gui`.

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

## Redesign build (2026-10-16)

The user approved the redesign proposal of the redesign pass (review page of 2026-10-16) and chose: the panel stays 900 wide; cards as `mod1440_*` containers that own their widgets (patched executable only, W34); the rail at the right; `shift+l` on Sunk Ships. Built while the user was away, without a game launch.

What was built:

- **Banner** `mod1440_ao_banner` in `info` at 14,48 (872x59): the tab's picture strip (`army_overview_top`), `unit_count` (`hoi_20b`) and `battalion_count` at x 168, the special forces at x 330, `filter_title`, the 320 px plate and the 300 px filter box at the right. `theatres_count` stands at x 330 of the banner (window 344,56, 190 px) in a card of its own, `mod1440_ao_theatres`, because its vanilla parent is `countryarmyview` and the test suite allows only `mod1440_*` containers between a widget and its vanilla parent. The plate under the list (`overview_bottom`) is parked at x -2000.
- **Sort header** at y 112 over the list only (x 13 to 751), vanilla captions: divisions Type 0-166, Name 164-428, Theater 426-594, Army 592-738; fleets 0-217, 215-489, 487-679, 677-738; wings 0-187, 185-453, 451-587, 585-738 (row coordinates).
- **Lists** `army_units`, `navy_units`, `air_units` at 0,138, 776 wide, margin 13/13/12/25, slot 738x35: rows start at window y 156 (screen 234), 34 division rows in view instead of 30. The scrollbars stay on the lists.
- **Rows** of 738, rebuilt by `tools/stretch_background.py` from the vanilla row art (jobs `ao_army_entry`, `ao_navy_entry`, `ao_air_entry`; constant `OVERVIEW_ROW`): division olive 164 | name 262 | gap 6 | theatre 160 | gap 6 | army 140, name at 170 (254), theatre at 434 (152), shield at 600 and army name at 636 (98) in one box; fleet name at 222 (262), region at 500 (176), count and mission at the end; wing name at 189 (260), base centred at 455 (126), area `assigned_region` at 591,1 in `hoi_16mbs` (145) over the four mission icons at y 15, 26 apart.
- **Rail** at x 780, 108 wide, from y 112, cards on `GFX_tiled_plain_bg_small` with `clipping = yes` and a caption strip (`GFX_1440p_AO_card_head`, the vanilla unit list header at 104x24). Per tab `mod1440_ao_<tab>_mods` holds `modifiers_grid` (slot 100x32, one column, `max_slots_vertical = 14`) and `mod1440_ao_<tab>_types` 6 below it, down to y 1350, holds the counts by type (slot 100x31, one column; 23 chips fit on the army and air tabs, 27 on the navy tab). Captions: `MOD1440_AO_MODIFIERS` ("Modifiers", new, written by `tools/build_managers.py`, `screen_texts()`), `ARMY_TAB`, `naval_equipment`, `AIR_SORT_PLANES`. The Modifiers card holds 14 tiles on the army and air tabs and 10 on the navy tab.
- **Tiles and chips**: `modifier_entry` 100x32 (plate `ao_modifier_bg` widened to 100, icon at 4,4, value right-aligned in 56 px at x 40, `hoi_18mbs`). The three chip windows `army_view_subunit_entry`, `navy_view_ship_entry`, `air_view_plane_entry` joined the override file with baselines, 100x29, on `GFX_1440p_AO_filter_entry` and its highlight (vanilla 90 px chips widened to 100): count at the left, type icon at the right (army 0.7 centred at x 74, ship 0.9 centred, plane 0.9 centred at x 70; the plane icon's orientation is upper left now, since vanilla's upper right was measured from a 60 px window).
- **Hotkey** `shift+l` on `destroyed_ships_open`. Free in vanilla, in the mod and in the user's playset (`tools/check_playset.py`, 2026-10-16).
- Equipment Details and Sunk Ships unchanged at x 890; Equipment Details now stands next to the rail.

Read in the executable on 2026-10-16 (GUL-044): the modifier and count fills add items slot by slot by the grid's settings, so one column works, but an item past `max_slots_vertical` is dropped. The four modifier fills add 14, 14, 10 and 9 items; vanilla's navy grid (7 x 1) showed 7, so the navy card may now show two or three modifiers vanilla dropped. Every modifier grid therefore has `max_slots_vertical = 14`.

Deviations from the design:

- `theatres_count` stands in its own card over the banner instead of inside `mod1440_ao_banner` (see above); it sits at x 330 on every tab, also on the navy and air tabs, where the mock-ups drew it under the count.
- The caption key is `MOD1440_AO_MODIFIERS`, the generator's form, instead of `mod1440_ao_modifiers`.
- The navy Modifiers card holds 10 tiles (the design: 7), after GUL-044.
- `max_slots_vertical` of the count grids is what the card holds (23, 27) instead of 24.
- The header containers' right margin is 0 (was 25), so the rail at x 780 to 888 is not cut by the margin.

Fallbacks, if the game check shows:

- the tiles or chips in a row instead of a column (against GUL-044): go back to the build of 2026-10-14's two header rows over the list (modifiers 7 a row, counts 10 a row) and the list at y 257;
- the banner, the rail or `theatres_count` empty (`hoi4.exe` not patched, `Set-HoiRecursiveLookups.ps1 -Status`): patch again, or plates behind widgets left where they are (as A9);
- the cards not clipping a long list of types: they have `clipping = yes`; otherwise lower `max_slots_vertical` to the count that fits;
- the navy card with 9 modifiers: the card is one tile too high; lower it to 9 tiles.

Not seen in game: everything above. In particular whether the 14/10 tiles and the chips stack in one column, the navy's modifier count, the banner's widgets filled and the filter typed in, chip filtering at 100 px, `shift+l` on the navy tab and on the tabs where the button is hidden, tooltips at the new places, a wing with a mission (region over the icons), a division in combat, a list scrolled to its end, and the playset's sprites (RT56's 174 px unknown ship icon is clipped by the type card).

Game check (with the user's permission): `tools/Invoke-GameCheck.ps1 army_overview`, then the same with the playset (`tools/Invoke-GameSteps.ps1 -Start -Playset`). Tester's checklist: the scene's `checklist` in `tools/scenes/army_overview.json`.

## Close

- [x] Roadmap status and link
- [x] README "Reworked screens"
- [x] Workshop description
- [x] `version` in `descriptor.mod` (1.7, with A7 and A8)
- [x] Engine Facts rows confirmed or added
- [x] Scene file (`tools/scenes/army_overview.json`); the move `select_fleet` clicks the first fleet row by name
- [x] Finished screen stored under `reference/mod/`
- [ ] The tester's judgement
