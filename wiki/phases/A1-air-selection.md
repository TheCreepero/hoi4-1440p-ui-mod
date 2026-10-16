# Phase A1: air wings and airbases

Reconstructed from the Roadmap after the phase closed; later phases keep this file as they go. Status: the 705 px build was done; the redesign of 2026-10-16 (820 px, cards) is built and checked by render and tests, not seen in game (section "Redesign build").

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

## Redesign build (2026-10-16)

Status: built and checked by render and tests; not seen in game.

Built from the approved redesign `a1-air` (decisions: 820 px, 52 px mission slots, `shift+n` on create air group, only the captions "Capacity" and "Air Wings").

What was built:

- `air_selection_view` is an 820 px stack of cards. Header plate `mod1440_cp_header` (818x108 where it shows) at 2,2 with the Missions card `mod1440_cp_missions` (806x46) and five toolbar plates (selection 8-256, organise 262-414, settings 420-572, select 578-730, close 741-814, 44 high at y 60). The plates are icons drawn before the vanilla windows, so every vanilla widget stays a direct child of its vanilla window and nothing needs the patched executable.
- `mission_toolbar` at 8,6 on a transparent background, `missions_grid` at x 16 with 52 px slots: 15 missions end at the panel edge (8 + 15 x 52 + 32 = 820) [GUL-009].
- `air_wing_toolbar` 816x44 at 2,60 on a transparent background; buttons 36 apart, 8 into each plate; `count_selected` re-sprited as a 196x32 title tile with `wings_count` in `hoi_20b`; `btn_close` at 753 (screen 755), the column of every row's close button. Hotkeys `shift+n` (create air group) and `shift+u` (unassign).
- List frame `unassigned_airwings_view` 818x951, list 786x949: 19 rows of 48. `air_selection` at y 104, so the frame is expected at 2,181, 6 px into the header plate.
- Airbase row 784x48: `base_name` 220 px in `hoi_20b`, caption `mod1440_cp_capacity_caption` ("Capacity", key `UNIT_LEADER_CAPACITY_SORT`) at 300, `capacity` 364, sticky area 458/489, permission box 522, quick deploy 676 (buttons grow left), `new_btn` 712, `btn_close` 747.
- Wing row 784x48 on the wing texture widened to 784 (`tools/stretch_background.py`): aircraft cluster 0-207 as before, efficiency strip 210, `unit_name` (`hoi_20b`) and `mission_state` (`hoi_18mbs`) at 240 with 282 px, `mission_grid` 530, army shield 640, aggressiveness 674, day/night 709, close 747. The longest status of the game and Road to 56 (279 px) and the playset's longest wing name (278 px) fit.
- Gun emplacement and rocket rows on the same columns: text at 240 (282), mission background and icon at 530/532, `nuclear_button` 536, `mission_targets` 576, `btn_hold` 674, close 747; the rocket `count` at 140, `select_wing_desc` at 240, y 13.
- Air group badge `air_group_view_entry` 818 wide: badge tile `background_sprite` (`GFX_1440p_AV_group_bg`), title strip `mod1440_cp_title` 806x32 with `insigna` 10, `unit_name` 56 (`hoi_20b`, 300 wide), fuel icons 378/383, `select_btn` 658, `deselect_btn` 753; wings card `mod1440_cp_wings` 806x46 with the caption `mod1440_cp_wings_caption` ("Air Wings", key `AIR_WINGS`) and `wings_compact` at 94, 690 wide, `wings_compact_number_of_elements` 15 [GUL-038]. `air_groups_view` and its list 818 wide [GUL-035]. The widened bitmap `av_air_group_bg.dds`, its sprite and its stretch job are gone.

Deviations from the design:

- The header plate is 818x112 and the badge tile 818x100: 4 px more than they show, under the list frame. The edge of `tiled_plain_bg` and the top of the frame's tile are soft shadows about 5 px deep each, and with the 6 px overlap of the design a 3 px line of half-dark map showed between them in the render on a magenta ground.
- `air_group_view_entry` is 90 high (the badge shows 96): the code stacks the rows of `air_groups_view` by the entry's height [GUL-020], so the wing frame drawn after the badge covers its last 6 px, the A1 overlap rule.
- `air_groups_view` max height 951 instead of 1000 (vanilla): docked at y 181 it ends at 1132 with the frame, above the bottom bar (the test of docked windows).
- The airbase row's tile is 781x45 at 3,3 (was the row's width at 3,3), so it ends with the wing rows at 784x48 as in the mock-up.
- `shift+u` on `btn_unassign` is in the design's additions; the build brief named only `shift+n`. Built, as the user approved the design as a whole.

Fallbacks:

- The frame docks elsewhere than 2,181: set `air_selection` y so that frame y = 77 + `air_selection.position.y` lands 6 px into the header plate.
- `mission_toolbar` draws a background anyway, or the code sizes it from the file: put `GFX_tiled_plain_bg_small` back and narrow the Missions card to the bar.
- The two text lines touch the row's bottom border: `unit_name` y 2 and `mission_state` y 23, or status back to `hoi_16mbs` (longest 246).
- `shift+n` also fires the airbase row's `n` (new wing): drop the key from `btn_create_air_group`.
- The compact wings wrap or consolidate before 15: set `wings_compact_number_of_elements` back to 12 and the grid to 552.
- `air_groups_view` docks at 0,77 (over the header): set its `position` y or move the badge down by the header height.

Not seen in game: everything above. The render cannot show the mission buttons (the code builds them) or the compact wings.

Game check (with the user's permission): `tools/Invoke-GameCheck.ps1 air_selection air_group`, then once with the playset (`tools/Invoke-GameSteps.ps1 -Start -Playset`) for RBM's shields.

Tester's checklist:

1. Header: the mission buttons sit on the Missions card, 52 px apart; with 15 missions the bar ends at the panel edge; the toolbar buttons sit on five plates; no map shows between the cards.
2. The list frame starts 6 px into the header plate (expected y 181), 818 wide, 19 rows before it scrolls.
3. Wing rows: name in `hoi_20b` and status in `hoi_18mbs`, both whole; the two lines clear the row's bottom border.
4. The close buttons of the toolbar, the airbase row and the wing rows stand in one column.
5. Airbase row: name, "Capacity", capacity, quick deploy buttons growing left of the edit button.
6. Give a wing a mission: the mission icons start right of the longest status, the efficiency strip shows.
7. Strategic air priorities opens above the mission bar as before.
8. `shift+n` creates an air group (and no new wing); `shift+u` unassigns the selected wings.
9. With a group selected: badge 818 wide with title strip and wings card, "Air Wings" caption, the frame under it as wide; no map between badge and frame.
10. Scroll the list to the end; open the quick deploy popup and scroll it.

## Close

- [x] Roadmap, README, Workshop description, `version`
- [x] Scene file `tools/scenes/air_selection.json` (positions measured on `hoi4_7.png`)
