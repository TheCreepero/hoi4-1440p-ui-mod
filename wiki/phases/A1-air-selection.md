# Phase A1: air wings and airbases

Reconstructed from the Roadmap after the phase closed; later phases keep this file as they go. Status: Done, with the narrowing to 705 awaiting its game check.

## Scope

- Vanilla file and windows: `airselectionview.gui`: `air_selection_view`, `unassigned_airwings_view`, the four row windows, `quick_wing_deployment_selection_window` and its entry.
- What the vanilla screen crams or hides: 9 rows before the list scrolls, wing names cut at 548 px rows, toolbars and list with gaps between them, a short quick deploy popup.
- Out of scope: the mission toolbar's width (computed from the number of missions, Engine Facts S9).

## Inventory

- Lists and their rows: `air_wings_list` in `unassigned_airwings_view` holds `airbase_selection_item`, `airwing_selection_item`, `gun_emplacement_selection_item`, `rocket_selection_item`; `plane_selection_items_list` holds `quick_wing_deploy_plane_type_entry_item`. In `tools/gui-links.json`.
- Bitmap backgrounds: wing rows (`wing_entry_bg.dds`, two frames, widened with `widen_periodic`), airbase rows (tiled, option 2).
- Engine facts learned: L1, L2, L3, L5, S4, S5, G1, G5, G7, G8, G9, F1.

## Proposal

The selection list holds 20 rows instead of 9, rows are wider so wing names fit, texts are one font size larger, the two toolbars and the list form one block without gaps, and the quick deploy popup is taller. Built before the depth changed from enlargement to redesign.

## Decisions

- Panel first built 768 wide; narrowed to 705 after A2 showed how width is judged. 703 is as narrow as the mission bar goes at vanilla spacing with 15 missions.

## Game checks

| # | Date | Build | Checked | Result | Screenshot | Taught |
|---|---|---|---|---|---|---|
| 1 | 2026-10-08 | air rework, build 1 | list, rows | rows cut off at 556 px | - | the rows sit in `unassigned_airwings_view`, not in `air_selection`: the frame holding a list is found by its looks (S5) |
| 2 | 2026-10-08 | build 2 | panels | gaps between the panels | - | tiled sprites have soft edges; overlap values in Design Rules (G5) |
| 3 | 2026-10-08 | build 3 | all | accepted | `hoi4_7.png` | font steps F1 |
| 4 | 2026-10-08 | 705 wide, working tree | airbase with three wings, unattended run | toolbars and list end at the same right edge; the width is not judged by the user yet | `scratch/checks/air_selection-*-crop.png` | the harness facts H1-H14 |

Not seen in game: gun emplacement and rocket rows (none in a 1936 start).

## Close

- [x] Roadmap, README, Workshop description, `version`
- [x] Scene file `tools/scenes/air_selection.json` (positions measured on `hoi4_7.png`)
