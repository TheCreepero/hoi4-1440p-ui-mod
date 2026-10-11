# Phase A3: unit details windows

Division, ship, air wing and railway gun details. Status: built and checked by the harness; awaiting the tester's judgement on sizes and the manual list below.

## Scope

- Vanilla files and windows:
  - `unitview.gui`: `army_division_stats_view`, `ship_stats_window`, and the rows `stat_entry`, `stat_archetype_header_list_entry`, `stat_equipment_entry`, `army_history_entry`, `unit_hq_modifier_entry`, `ship_stats_air_wing_entry`.
  - `airwingdetails.gui`: `air_wing_stats_window`, `air_wing_details_equipment_entry`.
  - `railway_gun.gui`: `railway_gun_stats_view`.
- Override file: `interface/zz_1440p_unit_details.gui`. `army_division_stats_view` moved here from the A2 file.
- What the vanilla screens cram or hide: stats in a 16 px typewriter font, a label cut by its value ("Trickleback & War"), equipment names on two lines, terrain adjusters behind a scrollbar, a division window that opens on top of the army panel.
- Out of scope: showing Stats and Template together (the code shows one tab at a time), any new value (see Inventory), hotkeys (the windows have only tabs, Promote and Delete).

## Inventory

- Vanilla references: `reference/vanilla/division_details*`, `ship_details*`, `air_wing_details*`. New recipes: History and Template tabs, both dropdowns, a tank and a motorised division (sort by name, rows 1 and 2), a British carrier (`tag ENG`, Home Fleet, first ship; undone by the scene's `teardown`), air wing details.
- `Show-CodeNames`: no window has an unused widget. `cavalry` and `category_special_forces` are marked `+` and are not widget names.
- **One row fills four windows.** `stat_entry` is named in the executable next to the division, ship, air wing and railway gun windows. A larger stat font therefore meant reworking all four.
- Lists and rows (in the scenes; `stats_grid` names four grids per window, so the scenes use `parent/list`):
  - `base_stats/stats_grid`, `combat_stats/stats_grid`, `misc_stats/stats_grid`: `stat_entry`.
  - `equipment_list`: `stat_archetype_header_list_entry` and `stat_equipment_entry` in turn.
  - `history_entry_grid`, `history_grid`: `army_history_entry`.
  - `air_wings/list`: `ship_stats_air_wing_entry`; `equipment/list` of the air wing window: `air_wing_details_equipment_entry`.
  - `adjuster_stats/stats_grid` and `terrain_grid`: adjuster entries of other vanilla files, not overridden.
- Bitmap backgrounds: all of them. Option 4 of the Design Rules throughout (`tools/stretch_background.py`, outputs `ud_*.dds`).
- Where the windows sit: the division and ship windows are placed by code (Engine Facts S17); the air wing window sits where its file puts it (1005,485).

## Proposal and what was built

| Part | Vanilla | Built | Why |
|---|---|---|---|
| Division window frame | 856x497 | 1180x587 | sum of the parts below |
| Ship and air wing frames | 856x409 | 1180x475 | the same stat paper |
| Stat text | `hoi4_typewriter16` | superseded by the redo below: tiles in `hoi_16mbs` and `hoi_20b` | first build: `hoi4_typewriter22` |
| Stat column | 155 wide | 233 wide | longest label 173 px plus longest value 82 px |
| Stat row | 20 high | 28 high | 22 px font |
| Terrain adjusters (division) | 5 per row, scrolls | 7 per row | 11 terrain types in two rows |
| Sea terrain adjusters (ship) | 2 by 2, scrollbar | 5 per row | four types in one row |
| Side panel | 303 wide | 393 wide | equipment names on one line |
| Equipment list (division) | 359 high | 449 high | follows the frame |
| Division name | 242 px box, `hoi_16mbs` | 476 px box, `hoi_20b` | the font of the division list |
| History list | 522x315, text 16 px | 756x405, text 22 px | follows the frame |
| Template board | 548x423 | 782x513, regiment columns 131 px apart | fills the frame; icons keep their size |
| Where the division window opens | x 180 to 660, on the army panel | x 685 to 1165, beside it | see Decisions |

One label stays cut: "Trickleback & War Support Protection:" is 357 px in the 22 px font. It is listed under `knownCuts` in the scene.

## Decisions

- 2026-10-08: plan approved with four windows instead of two, because of the shared stat row.
- 2026-10-08: **the division window opens beside the army panel.** The game ignores the window's file position, so its rectangle is made 10x10 and the background and every widget are placed 505 px to the right (Engine Facts S17 to S20). A first attempt with a transparent strip in the texture was dropped: the strip swallowed clicks on the division list.
- 2026-10-08: **the ship window keeps its side panel always drawn**, as in vanilla. The plan proposed to show it only for a ship with a captain or air wings. That needs two backgrounds that stack correctly in four combinations, and the captain state cannot be brought up in a 1936 start to check it. Not done; open for A4, when the fleet panel is reworked.
- 2026-10-08: the manpower, fuel, delete and close widgets of the ship window stay in the side header for the same reason.
- 2026-10-08: paper and metal are enlarged by many single-line copies spread over an area, not by one mirrored insert. A mirrored insert of 78 columns showed every stain twice.

## Game checks

| # | Date | Build | Checked | Result | Screenshot | Taught |
|---|---|---|---|---|---|---|
| 1 | 2026-10-08 | vanilla | new recipes; where further windows open | Notepad with `error.log` covered the game, and the clicks went into it | `scratch/checks/a3_*` | H27; the harness now minimises it and refuses a click that would land in another window |
| 2 | 2026-10-08 | vanilla | every state, stored as reference | 12 captures | `reference/vanilla/` | S17 (first three positions) |
| 3 | 2026-10-08 | 52c3e50+dirty | file position +200 on the division window; background position on the ship window | no change at all | `scratch/checks/a3x_*` | nothing: the game was loading a stale copy of the mod (see 5) |
| 4 | 2026-10-08 | 52c3e50+dirty | first build of the division window | vanilla window on screen, `expect` failed | - | - |
| 5 | 2026-10-08 | 52c3e50+dirty | the same, after `build.ps1 -DevLink` | division window correct on all tabs; ship window with garbled stats (shared row, not yet adapted) | `scratch/checks/a3v1_*` | H28: the launcher file pointed at a deployed copy; the harness now refuses that |
| 6 | 2026-10-08 | 52c3e50+dirty | click and drag tests on the window with an offset background | the window's rectangle swallows clicks, the background takes the drag | `scratch/checks/hit_*` | S18, S19; S17 in full |
| 7 | 2026-10-08 | 52c3e50+dirty | 10x10 window rectangle, content 505 px right | rows beside the window can be clicked; tabs, drag, click to front and Escape work | `scratch/checks/a3u_*` | S20 |
| 8 | 2026-10-08 | 52c3e50+dirty | all four windows: division (three tabs, two dropdowns, tank, motorised), ship, carrier, air wing | as rendered; `error.log` clean | `scratch/checks/a3v2_*` | - |
| 9 | 2026-10-08 | 52c3e50+dirty | the same scenes, stored as reference | see `reference/mod/` | `reference/mod/` | - |

Not seen in game (states a 1936 start does not show):

- Railway gun details. Laid out with the same numbers as the ship window; rendered only.
- A ship captain, and a carrier with a captain.
- History entries and medals, on the division and the ship window.
- An HQ division's Template tab (rendered as state `template-hq`).
- A foreign, colonial or exiled division's flags in the header strip.
- The Design tab of the ship window opens the ship designer (B4) and was not changed.

## A3 redo: cards and tiles (2026-10-09 to 2026-10-11)

The first build only enlarged the vanilla layout. The redo regroups the Stats tab of all four windows as dark cards of stat tiles. Engine experiments first ([Engine Facts](../Engine-Facts.md) W14 to W21): duplicates, reparenting and two tabs at once do not work; tiles from a grid with several columns, wrapped labels and tab hotkeys do.

- **Stat row as a tile** (`stat_entry`, shared by all four windows): 126x52, label in `hoi_16mbs` over a value in `hoi_20b`, background `GFX_1440p_UD_stat_tile` (built from the vanilla header bar by `tools/stretch_background.py`). The long label "Trickleback & War Support Protection" wraps to two lines (107 and 115 px in a 121 px box); the first build's 116 px box left no margin and was widened after the tester reported an overlap with the value (`FOUND_ISSUES.txt`, seen in the earlier typewriter build).
- **Division window:** Base and Combat cards (3 tile columns) side by side, Misc card (6 columns) below, no parchment on the Stats tab; adjusters in two rows of seven; tab hotkeys `shift+a`, `shift+h`, `shift+t` worked in the experiment but are NOT in the shipped file yet (next phase).
- **Ship, air wing and railway gun windows:** same cards (194 and 142 px high); the paper of `ud_ship_bg.dds` and `ud_air_wing_bg.dds` grew by 111 rows (586 px high), every widget under the paper moved down 111 px, window height 473 to 584.
- **Game check 10 (2026-10-11, build 52c3e50+dirty):** division (all tabs, both dropdowns, tank, motorised), ship (stats, history, carrier) and air wing. `error.log` clean. Stats tiles, the wrapped "Trickleback & War / Support Protection:" label (no overlap with its value), all adjusters and the shifted lower panels came out as rendered. It found one fault: the ship History paper (container 376 px) ran 40 px over the lower panel; shortened to 334 (grid 307, scrollbar 312) and re-rendered, not yet launched again.
- **Game check 11 (2026-10-11):** tab hotkeys `shift+a`, `shift+h`, `shift+t` (division) and `shift+a`, `shift+h` (ship) switch the tabs; the shortened ship History ends above the lower panel; `error.log` clean; `reference/mod/` refreshed with `-SaveReference` (65 captures).
- **Not checked in game:** railway gun details. `rg` creates no gun in a release build (Engine Facts H29) and no recipe was found; the window has the same layout numbers as the ship window and is render-only. Promote hotkey not added (needs a commander to test).

## Left for the tester

1. Tooltips on stat rows, terrain adjusters and equipment rows.
2. Renaming a division and a ship; Promote; Delete.
3. Whether 1180 px is too wide, and whether the first window's place (x 1005) suits.
4. The cut "Trickleback & War..." label: acceptable, or widen the first column further.

## Close

- [x] Roadmap status and link
- [x] README "Reworked screens"
- [x] Workshop description
- [x] `version` in `descriptor.mod`
- [x] Engine Facts rows confirmed or added
- [x] Scene files final (`division_details`, `ship_details`, `air_wing_details`)
- [x] Finished screens stored under `reference/mod/`
