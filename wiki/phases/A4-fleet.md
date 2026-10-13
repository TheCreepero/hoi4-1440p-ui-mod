# Phase A4: navy and fleet view

The panel of a selected fleet: fleet card, toolbar, task force cards and the ship list. Status: done. Both steps are built and checked by the harness, and the tester tried the deployed build in game on 2026-10-11 and found it good.

## Scope

- Vanilla file and windows, all in `naviesview.gui`:
  - Step 1: `naviesview_window` (frame, fleet list, toolbar), `fleet_view_header`, `taskforce_view_entry`, `ship_entry_detailed`, `ship_entry_compact`; `home_base_selection_window` and `ship_refit_equipment_view` for their position only.
  - Step 2: `task_force_composition_editor_window` with `task_force_composition_editor_entry`, `task_force_composition_editor_new_entry` and `task_force_template_entry`; the ship class picker `task_force_composition_editor_sub_unit_selection_window` with `task_force_composition_editor_sub_unit_entry_window`; `home_base_selection_window` with `naval_base_selection_item`; and "Select Ships to Transfer", `move_ships_window` with `move_ship_entry`.
- Override file: `interface/zz_1440p_fleet.gui`. `ship_stats_window` in `interface/zz_1440p_unit_details.gui` (A3) moved with the panel.
- What the vanilla screen crams or hides:
  - A ship takes two lines of a 41 px row, and the class name is cut at 272 px: "Converted Battleship (Courageous Class ..." hides the "Mk. I" that tells two classes apart.
  - The home base name has a 90 px box: "Wilhelmshaven" (91 px) is cut.
  - A task force card is 125 px high, a third of it a tray with a few small counters, so 8 of the 12 task forces of the British Home Command fit on the screen.
  - Organisation and strength of a ship are two upright bars 6 px wide.
  - The commander's four stats sit 18 px apart, and 15 toolbar buttons form one run, 3 of them with a hotkey.
- Out of scope: the navy overview list (A6), the mission bar at the bottom of the screen (`action_bar_window`, `target_bar_window`), the ship designer (B4), any new value (see Inventory).

## Inventory

- Vanilla references: `reference/vanilla/fleet*` (a task force opened to its ship list, a selected ship, the task force list, the home base picker, the composition editor, and the British Home Fleet with 33 ships and Home Command with 12 task forces).
- States of the screen:
  - **Task forces:** fleet card, toolbar, one card per task force.
  - **Ships:** Select on a card shows that card alone with its ships below it (`ships_detailed`); Back returns.
  - **Several fleets selected:** one fleet card each in `detailed_fleet_box`. Not captured: the harness has no shift-click, and one attempt by hand missed. The cards stack by the grid's slot height, which the file sets.
- Where the windows sit, the same with and without the mod: `naviesview_window` at 0,82 (its `show_position`); the fleet card is the row of `detailed_fleet_box`; the toolbar 168 px below the top with one fleet; the first task force card at 0,293.
- `Show-GuiOutline -Comments`: `detailed_fleet_list` "height adapted in code"; the toolbar's "vertical position controlled by code"; `ship_button` "Y is centered in code"; `ship_type` "maxWidth is shrinked in code when necessary"; `damaged_part_report` and `btn_repair_now` "moved in code".
- `Show-CodeNames`: no window has a widget the code would fill and vanilla leaves out. The names marked `+` are fragments of sprite names (`small_icon_`, `icon_`, `_icon_medium_black`, `btn_target_`, `_warn`), `btn_mission`, `naval_dominance_texticon`, `taskforce_insigna` and `real_task_force_insignia`: none was tried.
- Lists and rows (in `tools/gui-links.json` and the scene):
  - `detailed_fleet_box` (grid): `fleet_view_header`. Its slot width was `100%%` and is now written out as 740.
  - `ships_detailed` (container of the task force card): `ship_entry_detailed`, one below the other.
  - `ships_compact` (container of the fleet card and of the task force card): `ship_entry_compact`, side by side. The scene key `rowsAcross` tells the renderer.
- Bitmap backgrounds: all of them, option 4 of the Design Rules (`tools/stretch_background.py`, outputs `fl_*.dds`). The ship row is the first bitmap that got lower (`cut`).
- `@nv_tb_btn_y` is defined inside the toolbar, not at file level, so it came along with the window; `@buttons_height` of the composition editor likewise.
- Step 2:
  - Scenes of their own: `fleet_composition`, `fleet_home_base`, `fleet_transfer`, each with a vanilla and a mod reference.
  - The transfer window opens when a ship counter of one task force is dragged onto another task force. The harness got a `dragWidget` step for it.
  - The game has nine ship classes (`common/units`); the vanilla class picker shows seven and scrolls.
  - No pop-up row is used by another vanilla file (`countryproductionlineview.gui` uses the same row sprite in windows of its own). Two vanilla windows have a grid named `templates_grid` and two one named `ships_grid`, so an entry pair in `tools/gui-links.json` can now name its window.
  - `Show-CodeNames`: nothing the code would fill and vanilla leaves out.

## Proposal and what was built

Agreed on 2026-10-11 from three text mock-ups: one line per ship as a table, in a panel of about 740 px (the other two were the same table at 705 px with cut class names, and two-line rows at 705 px).

| Part | Vanilla | Built | Why |
|---|---|---|---|
| Panel width | 492 | 740 | one line per ship with the class name whole |
| Ship row | 460x41, name over class | 708x35, name and class side by side | 22 ships on the screen become about 26 |
| Ship name | `hoi_18mbs`, 272 px | `hoi_20b`, 170 px | the font of the division list |
| Class name | `hoi_18`, 272 px | `hoi_18`, 284 px | "Converted Battleship (Courageous Class Mk. I)" is 281 px |
| Organisation and strength | upright, 6x28 | lying, 46x8, one above the other | as in the division list (A2) |
| Task force card | 492x125: title, mission, tray | 740x86: title, mission with the counters in it | all 12 task forces of Home Command on the screen instead of 8 |
| Mission text | `hoi_16mbs`, 269 px | `hoi_18mbs`, 232 px, a second line when longer | "Docked in Scottish Highlands" with its flag is 228 px |
| Fuel and dominance icons of a task force | in the mission box | in the title bar, left of the fleet insignia | room for the counters |
| Composition editor button | in the tray | first in the box of the three order buttons | the tray is gone |
| Composition counter | 46 wide, count in `hoi_16mbs` | 50 wide, count in `hoi_18mbs` | six fit beside the mission text |
| Fleet and task force name | 212 px, `hoi_18` | 360 px, `hoi_20b` | the name plate grew by 148 px |
| Commander | name 140 px, stats 18 px apart, `hoi_16mbs` | name 192 px, stats 22 px apart, `hoi_18mbs`, skill in `hoi_20b` | a box each for name and stats |
| Traits | from x 302 | from x 430, room for 12 | |
| Home base | button 124, name 90 px | button 184, name 150 px | "Wilhelmshaven" whole |
| Toolbar | one run, 30 px steps | four groups, 40 px steps: delete; organise; upkeep; standing orders | |
| Home base picker | x 490 | x 738 | beside the panel |
| Refit window | x 510 | x 758 | beside the panel; not seen in game |
| Ship details window | at the code's 500,100 | drawn 258 px right of it | beside the panel (10x10 rectangle, as the division window) |

Step 2, agreed on 2026-10-11 ("rework all three"):

| Part | Vanilla | Built | Why |
|---|---|---|---|
| Composition editor | 524 wide, rows 460 | 604 wide, rows 540 | class names in `hoi_20b`, counts in `hoi_18mbs` |
| Template dropdown | 324, name 268 px | 404, name 348 px | longer template names |
| Ship class picker | 400x370, seven classes, scrolls | 400x450, all nine classes | nothing to scroll; class names in `hoi_20b` |
| Home base picker | 375 wide, rows 335, name in `hoi_18b` | 455 wide, rows 415, name in `hoi_20b` | long base names with their count |
| Transfer window | 535 wide, rows 460x46, name over class | 695 wide, rows 620x35, name and class side by side | as the ship list; 10 rows before it scrolls instead of 7 |

Additions, each with the row of "What a redesign can add" that allows it:

- Hotkeys: `shift+n` new task force from the selection, `shift+r` to reserve, `shift+o` balance task forces, `shift+g` upgrade, `shift+p` repair now. The first two were pressed in game check 6 and work; the other three were not pressed.

## Decisions

- 2026-10-11: table rows in a panel of about 740 px, chosen by the user from three mock-ups.
- 2026-10-11: **the task force card lost its tray.** Game check 1 showed the tray two thirds empty on every card. The counters went into the mission box and the status icons into the title bar; the code places the cards by their height, so the lower card needed nothing else (Engine Facts S21).
- 2026-10-11: six counters fit beside the mission text. A task force with seven ship types (carriers and submarines together) would run its seventh counter into the order buttons; not seen.
- 2026-10-11: the ship name box is 170 px, less than vanilla's 272, to give the class name its 284. Ship names over 170 px in `hoi_20b` are cut ("Oktyabrskaya Revolutsiya", 182 px); none is in the samples.
- 2026-10-11: the ship row window was tried 730 wide on the guess that the code limits the class name by the window width. Wrong: the class name was longer than assumed. Back at 708.
- 2026-10-11: **the tester judged the width of 740 px good**, from the captures in `reference/mod/`.
- 2026-10-11: step 2 as "rework all three", chosen by the user over fonts only and over skipping it.
- 2026-10-11: the transfer window is 695 wide, not the panel's 740: its rows have no bars, level or insignia.
- 2026-10-11: the opened template list keeps its vanilla height (15 templates). It was to show 21, but the list could not be brought up in a check, so only its width follows the wider dropdown.
- 2026-10-11: the tester tried the deployed build (version 1.3) in their own playset and judged everything good. Which items of the list under "Left for the tester" were covered is not recorded.
- 2026-10-11: the frame keeps its vanilla height of 86 % of the screen (1238 px), so a long ship list runs below y 1140 as it does in vanilla; the bottom bar is not in that corner. The scene draws it down to 1140.

## Game checks

| # | Date | Build | Checked | Result | Screenshot | Taught |
|---|---|---|---|---|---|---|
| 0 | 2026-10-11 | vanilla | the task force list state; a shift-click for several fleets | list captured; the shift-click missed | `scratch/checks/a4_vanilla_*` | the two states of the panel |
| 1 | 2026-10-11 | 4c027ac+dirty | first build: German fleet (ships, task forces), home base picker, composition editor, British Home Fleet and Home Command | rows, cards, counters and both docked windows as rendered; `error.log` clean. The tray of every task force card mostly empty; a long class name still cut | `scratch/checks/fleet-*-1505*`, `-1506*` | S21, S22, S23, L9 |
| 2 | 2026-10-11 | 4c027ac+dirty | task force card 86 high with the counters in the mission box; ship row window 730 wide | cards 84 px apart, 12 on the screen; "Docked in Scottish Highlands" wrapped in 200 px; the class name cut exactly as before | `scratch/checks/fleet-*-1513*`, `-1514*` | S21 for a changed height; the window width does not limit the class name |
| 3 | 2026-10-11 | 4c027ac+dirty | class name 284 px, mission text 232 px, counters 50 px, a selected ship, ship details 258 px right | all as rendered; "Converted Battleship (Courageous Class Mk. I)" whole; the selected row's frame and outline fit; the first ship window opens at x 758, the second 50 px left of it over the panel's last 32 px | `scratch/checks/fleet-*-1521*`, `ship_details-*-1522*` | W22, G14; S17 for the ship window |
| 4 | 2026-10-11 | vanilla | every state, stored as reference | 7 captures | `reference/vanilla/fleet*` | - |
| 5 | 2026-10-11 | 4c027ac+dirty | the same with the mod, and the ship details scene, stored as reference | as check 3; `error.log` clean | `reference/mod/fleet*`, `reference/mod/ship_details*` | - |
| 6 | 2026-10-11 | 4c027ac+dirty | `shift+n` and `shift+r` with the first ship selected | a new task force of one ship; then that ship in the reserve fleet | `scratch/checks/a4_hk_*` | W23 |
| 7 | 2026-10-11 | 4c027ac+dirty | exploration: a counter dragged onto another task force; the template dropdown | the transfer window opened; the dropdown showed no list | `scratch/checks/a4s2_*` | H31 |
| 8 | 2026-10-11 | 4c027ac+dirty | first build of the three pop-ups | all as rendered; `error.log` clean. Save template did nothing, so the template list stayed closed | `scratch/checks/fleet_composition-*-1814*`, `fleet_home_base-*`, `fleet_transfer-*-1815*` | S25, S26 |
| 9 | 2026-10-11 | vanilla | the same scenes, to measure where vanilla puts the windows | editor at 520,292, transfer window at 508,415 | `scratch/checks/fleet_*-vanilla-1818*` | S26 |
| 10 | 2026-10-11 | vanilla | the three scenes, stored as reference | verified | `reference/vanilla/fleet_composition*`, `fleet_home_base*`, `fleet_transfer*` | - |
| 11 | 2026-10-11 | 4c027ac+dirty | the fleet scene and the three pop-up scenes, stored as reference | every expected widget found at 0 to 2 px; `error.log` clean | `reference/mod/fleet*` | - |

Not seen in game (states a 1936 start does not show, or the harness cannot reach):

- Several fleets selected at once.
- A commander: name, skill, stats and traits on the fleet card (rendered with samples).
- A damaged ship: the repair symbol, the damage report, the repair and refit buttons; and the refit window.
- A task force on a mission in several regions (the second line of the mission text), the replenishment and fuel warning icons.
- A task force with a composition template (the divider and the required count in a counter), and one with seven ship types.
- Medals, the history report button, exile and foreign flags on a ship row.
- The three toolbar dropdowns opened, and the hotkeys `shift+o`, `shift+g` and `shift+p`.
- The template list of the composition editor (rendered as state `templates`), and the role picker of an editor row.
- A home base picker with more bases than fit, and its supply icon.
- A transfer window with more ships than fit.

- **2026-10-13, with the user's playset:** RBM's insignia are 43 px wide, the game's 33, and the one at the end of a ship row stood 8 px outside the panel. `task_force_insignia` of `ship_entry_detailed` moved from x 705 to 697. The ship count on a task force's insignia overlaps RBM's wider picture; it is the insignia button's own text, drawn by the game, and looks the same without this mod. The role icons of Vanilla Navy Rework (43 px, 86 frames) fit the row. [Compatibility](../Compatibility.md).

## Left for the tester

1. Whether the lying bars (46x8) are too heavy. (The width was judged good on 2026-10-11.)
2. Tooltips on ship rows, counters, the status icons in the title bar and the toolbar.
3. Clicks: select a ship, drag a ship onto another task force, rename a fleet and a task force, the three toolbar dropdowns.
4. Hotkeys `shift+o` (balance), `shift+g` (upgrade) and `shift+p` (repair now); `shift+n` and `shift+r` are confirmed.
5. Scroll a long ship list and a long task force list to the end.
6. Composition editor: save a template, open the template list, load and delete one; add a class from the picker; the role picker of a row.
7. Home base picker: the three filters, and a country with many bases.
8. Transfer window: pick one ship, and "All ..." of a class.

## Close

- [x] Roadmap status and link
- [x] README "Reworked screens"
- [x] Workshop description
- [x] `version` in `descriptor.mod` (1.3)
- [x] Engine Facts rows confirmed or added
- [x] Scene files (`tools/scenes/fleet.json`, `fleet_composition.json`, `fleet_home_base.json`, `fleet_transfer.json`); the moves that click into the panel are clicks by name
- [x] Both steps stored under `reference/mod/`
