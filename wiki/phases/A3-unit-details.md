# Phase A3: unit details windows

Division, ship, air wing and railway gun details. Status: redesign of 2026-10-16 built and checked by render and tests; not seen in game (see "Redesign build (2026-10-16)" at the end).

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
| 10 | 2026-10-13 | 9c832ae+dirty | the polish of 2026-10-12, cold start through `tools/Invoke-GameCheck.ps1`: the eleven division scenes, the five ship scenes and the air wing | as rendered; every expected widget found; no line of `error.log` names the mod | `reference/mod/division_details*`, `ship_details*`, `air_wing_details*` | W27 |

Not seen in game (states a 1936 start does not show):

- Railway gun details. Laid out with the same numbers as the ship window; rendered only.
- A ship captain, and a carrier with a captain.
- History entries and medals, on the division and the ship window.
- An HQ division's Template tab (rendered as state `template-hq`).
- A foreign, colonial or exiled division's flags in the header strip.
- The Design tab of the ship window opens the ship designer, which is out of scope (Roadmap, Milestone B), and was not changed.

## A3 redo: cards and tiles (2026-10-09 to 2026-10-11)

The first build only enlarged the vanilla layout. The redo regroups the Stats tab of all four windows as dark cards of stat tiles. Engine experiments first ([Engine Facts](../Engine-Facts.md) W14 to W21): duplicates, reparenting and two tabs at once do not work; tiles from a grid with several columns, wrapped labels and tab hotkeys do.

- **Stat row as a tile** (`stat_entry`, shared by all four windows): 126x52, label in `hoi_16mbs` over a value in `hoi_20b`, background `GFX_1440p_UD_stat_tile` (built from the vanilla header bar by `tools/stretch_background.py`). The long label "Trickleback & War Support Protection" wraps to two lines (107 and 115 px in a 121 px box); the first build's 116 px box left no margin and was widened after the tester reported an overlap with the value (`FOUND_ISSUES.txt`, seen in the earlier typewriter build).
- **Division window:** Base and Combat cards (3 tile columns) side by side, Misc card (6 columns) below, no parchment on the Stats tab; adjusters in two rows of seven; tab hotkeys `shift+a`, `shift+h`, `shift+t` worked in the experiment but are NOT in the shipped file yet (next phase).
- **Ship, air wing and railway gun windows:** same cards (194 and 142 px high); the paper of `ud_ship_bg.dds` and `ud_air_wing_bg.dds` grew by 111 rows (586 px high), every widget under the paper moved down 111 px, window height 473 to 584.
- **Game check 10 (2026-10-11, build 52c3e50+dirty):** division (all tabs, both dropdowns, tank, motorised), ship (stats, history, carrier) and air wing. `error.log` clean. Stats tiles, the wrapped "Trickleback & War / Support Protection:" label (no overlap with its value), all adjusters and the shifted lower panels came out as rendered. It found one fault: the ship History paper (container 376 px) ran 40 px over the lower panel; shortened to 334 (grid 307, scrollbar 312) and re-rendered, not yet launched again.
- **Game check 11 (2026-10-11):** tab hotkeys `shift+a`, `shift+h`, `shift+t` (division) and `shift+a`, `shift+h` (ship) switch the tabs; the shortened ship History ends above the lower panel; `error.log` clean; `reference/mod/` refreshed with `-SaveReference` (65 captures).
- **Not checked in game:** railway gun details. `rg` creates no gun in a release build (Engine Facts H29) and no recipe was found; the window has the same layout numbers as the ship window and is render-only. Promote hotkey not added (needs a commander to test).

## Polish of 2026-10-12

Part of the pass the user asked for after the Records had been polished ("run a similar UI polishing pass on every other feature"). The five reworked screens were looked over at full size in `reference/mod/`; the air panel, the division list, the fleet panel and Recruit & Deploy were left as they are, and the unit details windows got two changes.

- **The text of a stat tile stands 3 px inside its plate** (`stat_entry`: label and value at x 5 instead of 4, still 121 px wide). The first form of this change (x 7, 118 px) was taken back on 2026-10-13: 118 px is less than "Support Protection: " needs with the space the game's text ends on (about 119), and a 116 px box was what made the label run into its value in the build the user reported on (`FOUND_ISSUES.txt`). **The build the user installed on 2026-10-13 has the 118 px form**: if the label overlaps there, this is why.
- **A card behind the adjusters row of the division window** (`mod1440_card_adjusters`, sprite `GFX_1440p_UD_card_adjusters`, 772x147 at 515,419): the label, the hardness bar and the terrain adjusters stand on a card as the stats above them. It is a sibling icon between `info` and `adjuster_container` in the file, drawn above the first and below the second because siblings are drawn in file order ([Engine Facts](../Engine-Facts.md) W27, confirmed by this card).
- **Checked in game on 2026-10-13** (check 10 above), after the launch of 2026-10-12 had been refused by the permission system of the assistant's tool: the card lies behind the label, the hardness bar and the seven adjusters; "Trickleback & War Support Protection:" stands on two lines, clear of its value.

- **2026-10-13, with the user's playset:** RBM's GFX Overhaul puts a text icon before every stat label, and "Trickleback & War Support Protection:" then took three lines, the third on the value. The label of `stat_entry` has a fixed size now, 34 px for two lines of 16 (W28): a third line is cut with dots. Seen with the playset: "Trickleback & / War Support Prote…", the two-line labels whole. [Compatibility](../Compatibility.md).

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

## Redesign build (2026-10-16)

Status: built and checked by render and tests; not seen in game.

The redesign of the 2026-10-16 pass (design and decisions in `scratch/redesign/a3-unit-details/`, approved by the user with every recommendation taken). Cards are plates behind widgets that stay where the code looks them up, or the backgrounds of vanilla containers the code already shows and hides; nothing is wrapped, so the windows also work on an unpatched executable.

What was built (`interface/zz_1440p_unit_details.gui`, sprites in the a3-unit-details block of `interface/1440p_ui.gfx`, textures from `tools/stretch_background.py`, layout script `scratch/a3_layout.py` of the worktree):

- **One frame for four windows.** The window is the dark plain tile (`ud_division_bg.dds` 1186x609 and `ud_ship_bg.dds` 794x580, the tile laid out at the window's size, because both windows have a 10x10 rectangle; the air wing and railway gun windows take `GFX_tiled_plain_bg` as their Background [SPR-001]). A title strip of 1178 or 786 on `unit_list_header.dds` carries the title at the left and, from the right end, close, delete and the strength values in `hoi_20b` (division: manpower, equipment ratio; ship: manpower, fuel; air wing: equipment ratio). Under it the identity card 782x44 with a name field (the vanilla name field widened to 506) and, on the division and ship, an experience field (the vanilla one, 118 wide).
- **Division window 1186x609.** Officer card 386x108 (caption bar `GFX_1440p_UD_caption_bar` as the Background of `commanding_officer_header_list_entry`, Promote at its right end, portrait and chevrons, the name in `hoi_20b` 294x44, two lines, fixed size [GUW-027]); equipment card 386x447 with the caption "Equipment" (`DIVISION_EQUIPMENT`) and the list 380x413 under it. Tabs hang under the frame at y 599.
- **The Adjusters card bug is fixed.** `mod1440_card_adjusters` is now the first child of `adjuster_container`, so the code hides it with the adjusters; it no longer covers the History list and the Regimental Support row. The card is 772x152 (was 147) so that the second row of adjusters of a tank division ends inside it.
- **Stats tab:** the cards as built, 11 px from the left and 92 from the top; `info` lost its own plate.
- **History tab (division and ship), dark:** summary card 782x84 (division: "Command History", the two counts, Honors with the nine medal slots at x 300; ship: Honors and the captain's experience); list card under it with `army_history_entry` 744x48 rows on `GFX_1440p_UD_history_row` (the stat tile's metal widened), date in `hoi_18mbs` with `text_color_code = "Y"` (100 px), text in `hoi_18mbs` 576x40 (two lines). Division: 8.4 rows visible (list 405 high), ship 7.8 (376). The three vanilla backgrounds of `history_entry_container` are kept by name and drawn transparent.
- **Template tab:** the board as built, at 6,90; the Regimental Support row shows again.
- **Ship window 794x580, side cards only with content.** `captain_window` is 386x110 at 1058,0 with `GFX_tiled_plain_bg` as its Background (caption bar, Promote, portrait, name in `hoi_20b` two lines); `air_wings` is 386x320 (six rows of 46 before `list_window` scrolls) with the same Background, at `carrier_air_wings_list_position` 1058,0 and `taog_carrier_air_wings_list_position` 1058,116. The picture band (`GFX_1440p_UD_class_band`, cut from the first build's bitmap) is the first child of `equipment`, which moved to the top of the window, so the band hides with the class picture on the History tab and the pride button, dominance, support and sea terrain stand on it.
- **Air wing window 794x590:** the side column is gone; the Base card is one row (380x84) and the plane type rows have a card of 380x104 under it (`equipment` 370x90, two rows of 45). Picture band `GFX_1440p_UD_air_band` 772x144. The air wing code fills no `experience` or `unit_level` [GUW-039]; none was added.
- **Railway gun window 794x580:** own frame, no phantom side panel; the ship's picture band holds manpower, the fort adjuster and the gun. Render-only (H29).
- **Promote hotkey `shift+z`** on `promote_officer` and `promote_captain`. The contract named `shift+k`, but vanilla uses `shift+k` on the exercise button of the battle plan tools (up whenever an army is selected, so beside the division window), on fleet mission 7 of the navy panel and in the air panel. `shift+y` and `shift+z` are used by no vanilla file, by no mod of the Workshop folder and by no other key of this mod; `shift+z` was taken.
- **HQ division:** `GFX_army_hq_dropdown_button` is put on `unit_template_entry` of the HQ slot's deploy dropdown and on `designer_division_entry`, not on a widget of this window [GUW-037]; the identity card needs no room for it. The open item closes without a launch.
- Unused now and removed: `GFX_1440p_UD_air_wing_bg`, `GFX_1440p_UD_history_divider`, `GFX_1440p_UD_medal_strip` and their textures; the old `division_details` compose of `tools/stretch_background.py`.

Deviations from the design:

- Promote is `shift+z`, not `shift+l` (design) or `shift+k` (contract): see above.
- The equipment card of the division is a plate with the caption as a window child, and `equipment` sits inside it from y 30, instead of the card being the container's own Background: a caption inside a scrolling container would scroll away with the rows.
- History rows are 744 wide, not 748, so that the list keeps vanilla's 7 px between the row and its listbox edge, where the slider and `scrollbar_background` stand.
- The template change mark (`template_change_icon`, 32 px at scale 0.6) stands at the right end of the identity card after the experience field: there is no room for it between the name field and the experience.
- Name and experience fields on the identity card: the mock-up showed the fields of the first build's bitmap, which the plain window no longer has; they are now plates of their own from the vanilla fields.
- The counts of the History summary are 270 px wide (design 200), the medal label 60.
- The adjusters card is 152 high (design 147).

Not seen in game:

- Everything above: the build was not launched.
- A ship captain: the captain card, that `captain_window` is hidden without one, and which positionType the code takes for `air_wings` when the ship also has a captain.
- History rows and medals with real texts, the medal dropdown on a row of 48, and whether `text_color_code = "Y"` colours the date (the code may put its own colour codes into the text).
- That the windows still drag by their Background with the new textures and that clicks reach the side cards outside the 10x10 rectangle (S19, S20).
- `shift+z` on Promote, and with both the division and the ship window open (W7).
- The railway gun window as a whole.

Game check, when the user allows a launch:

`tools/Invoke-GameCheck.ps1 division_details ship_details air_wing_details`

Checklist for the tester:

1. Division Stats tab: one title strip (title, manpower, equipment, delete, close), the identity card with template button, name field and experience, the officer card, the equipment card with its caption; nothing else beside the window.
2. Every stat on its tile; the Adjusters card behind the label, the hardness bar and the adjusters (two rows for the tank division, both inside the card).
3. History tab: no Adjusters card; the summary card and the dark list card; the list reaches the bottom of its card.
4. Template tab: the Regimental Support row with its five slots and its label is visible.
5. `shift+z` presses Promote of the front division window (capture `hk-promote`).
6. Both dropdowns open over the window; the name can still be edited.
7. The window drags by its background; a division row in the strip between list and window can be clicked.
8. Ship (Deutschland): 794 wide, nothing beside it; the picture band with class picture, pride button, dominance, support and the four sea terrain adjusters; History tab without the band.
9. Carrier (HMS Furious): the Air Wings card beside the panel at the top, rows inside it; the card drags the window.
10. Air wing: 794 wide, no side column; the plane type row on its card under the Base card; the picture band.
11. `error.log`: no line that names the mod, no "Could not find" for these windows.
