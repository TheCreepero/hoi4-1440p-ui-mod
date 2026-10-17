# Phase A10: Air region details

## Scope

- Vanilla file and windows: `strategicairview.gui`: `strategicairview` (552x327), with its details panel `details_wnd` (the line chart `linechart`, a `LineChartType` sprite `GFX_strategicair_linechart` of 380x150, the Days / Months / Years buttons and 24 channel rows `channel_1` to `channel_24`). The window opens when the player clicks a strategic air region on the map.
- What the user asked for (2026-10-17, with a screenshot of Western Poland): "Redesign this air region details view (including the graph). The graph has always felt useless and difficult to read. The rest of the view is a bit messy as well."
- What the vanilla screen crams or hides (from the screenshot): a chart 380x150 with a line width of 1.5 and no scale but max / average / min, two lines at a time picked by tiny check boxes in a list of 24 rows; values in the list as "Our fighters lost: 136" with the number in a coloured run-on text; the header packs eight counts and four percentages into icons without captions; the mission area is a large picture of clouds with three small mission buttons.
- Out of scope: the air wing selection panel (A1), the air wing details (A3), the mission tooltip, and any scripted page.

## Roles and handoffs

- Handoff folder: `scratch/phases/A10/` (not in the repository)
- Builder: `builder-screen`: a vanilla screen in `interface/zz_1440p_air_region.gui`
- Design page: https://claude.ai/artifact/QJpjSQ53DsLaq9LKD5PEvM (round 1, 2026-10-17; the designer's handoff `scratch/phases/A10/design.json`, eight figures and an alternative, `mock_a10.py`, the executable reads under `work/`)
- Contracts written (hotkeys, shared rows, shared files): yes, `scratch/phases/A10/contracts.md` (2026-10-17)
- Worktrees (several screens at once): main tree

## Inventory

- Vanilla reference: none yet. No scene or recipe opens this view (`tools/scenes/`, [Game Recipes](../Game-Recipes.md)); the user's screenshot of 2026-10-17 is the only capture. The recipe and `-Vanilla -SaveReference` go with the launches of gate 2.
- The executable's bindings report (`window-bindings-1440p*.md` of the Modding Manager) has no section for `strategicairview`; the register has no record of `LineChartType` beyond its keys. The designer read the code in Ghidra (2026-10-17, `scratch/phases/A10/work/fn1.c`, `fn2.c`, `fn3.c`, `su1.c`, `off1520.c`); the four findings are candidate facts of `design.json` (`newFacts`), status executable, to be registered at close:
  - the chart is drawn at its sprite's `size`; `linewidth` is read as the line's width; a line holds at most 40 points;
  - any number of the 24 channels draw at once, in colours compiled in (Our 1-12 red to orange, Enemy 13-24 yellow to yellow-green); `btn_channel_<n>` gets frame 2 when ticked;
  - `max_value` is the largest ticked value, `avg_value` half of it, `min_value` always 0, the plot's top 1.05 times the largest; points run oldest to newest from the left, `min_x_value` is "0" and `max_x_value` the number of points;
  - every widget the code looks up is a direct child of its vanilla parent (`strategicairview`, `details_wnd`, `channel_<n>`, `air_combat_wnd`, `mission_btn_win`) except `crypto_broken_icon`, found recursively.
- Wing type widgets 1 to 4 are fighters, bombers, close air support and anti-air (frames of `GFX_wing_types_own`, keys `AIR_RESERVES_TYPE_1..3`), checked by the orchestrator.
- `python -I tools/check_playset.py` (2026-10-17): no mod of the playset defines `strategicairview` or redeclares a sprite the design uses.

## Proposal

Designer, 2026-10-17; the design page holds the figures. The window is 580x718 at 712,300, Details docked at its right at 914x718 (1500 px wide open), in cards, head bars and banded tables. Title strip with the region name in a fixed box of 370 (W28); a sky card with the weather picture and a captioned air superiority bar of 284; the twelve top numbers as a six-row Our | what | Enemy table with vanilla captions; the mission toggles in a head bar over the cloud picture. The chart: `GFX_strategicair_linechart` declared again at 800x276 with `linewidth = 3` [LOAD-012] on a dark plot, dotted grid lines at the heights of `max_value` and `avg_value`, labels 64 wide (vanilla's 30 cut "191.0"), the x labels swapped to read "30 ... 0". The channels: twelve banded rows, a caption, then Our and Enemy cells with tick box, colour and value (option B, a localisation file giving `AIRVIEW_DETAILS_CHANNEL_1..24` again) or the game's whole texts in cells of 400 (option A).

| Panel or column | Vanilla | Proposed | Why |
|---|---|---|---|
| Window | 552x327 at 1004,500 | 580x718 at 712,300 | room for captions; clear of A1 and the theatre boxes |
| Details | 513x515 | 914x718 | a chart that can be read |
| Chart | 380x150, 1.5 px, parchment 13x6 grid | 800x276, 3 px, dark, grid at the labels | the user's ask |
| Channels | 24 run-on buttons, boxes at the edges | 12 rows, Our and Enemy side by side | a pair in one row; numbers in columns |
| Top numbers | 12 icons without captions | 6 captioned rows | what each counts is visible |

## Decisions

- 2026-10-17, gate A passed (orchestrator): the five points of stage 3 hold; the figures read pair by pair; the caption of each wing type checked against the vanilla frames and keys. Noted on the page: option B of decision 2 rests on giving vanilla text keys again, which the register has no record of; option A is the fallback with the same rows.
- 2026-10-17, the user answered "As recommended": 1. full size (window 580x718, Details 914x718, chart 800x276); 2. option B, a caption column and value-only cells through a localisation file giving `AIRVIEW_DETAILS_CHANNEL_1..24` again, with A as the fallback; 3. the cloud picture kept under a head bar; 4. no hotkey. Written to `scratch/phases/A10/decisions-final.json`.
- 2026-10-18, gate B passed (orchestrator): `tools/Compare-Baseline.ps1 zz_1440p_air_region.gui -Group` read whole (437 changes: positions, sizes, fonts, sprites, `mod1440_ar_*` plates; nothing renamed, retyped or dropped; the combat widgets move only with `air_combat_wnd`); the four build renders read beside the mock-ups, and the renderer's own crop (no chart lines, no swatches: the code draws those); the five deviations of `build.json` accepted; `build.ps1 -Check air_region` run by the orchestrator: 663 passed, 0 failed, 60 skipped. Build renders added to the design page (same link). Noted: the option A fallback's layout half (`apply_a10.py`, `pristine.gui`) lives under `scratch/phases/A10/build/`, which is git-ignored; it is kept until the game check settles option B.

## Build (2026-10-17)

Status: built and checked by render and tests; tested by the user in their own campaign on 2026-10-18 and judged working (Game checks, row 1).

**What was built.** `interface/zz_1440p_air_region.gui` (made by `tools/New-OverrideFile.ps1 air_region strategicairview.gui strategicairview`, then laid out by `scratch/phases/A10/build/apply_a10.py` from the designer's numbers, `mock_a10.py`): the window 580x718 at 712,300 (`position = { x = -568 y = -420 }`, centred) with the details panel 914x718 docked at 586,0; cards, head bars and bands as plates `mod1440_ar_*` drawn right after the background, so every widget the code looks up is still a direct child of its vanilla parent (no lookup patch needed). Title strip with the region name in a fixed box (`hoi_30header`, 370x32, `fixedsize`, W28); sky card with a captioned 284 px superiority bar; the forces table (six rows, Our | what | Enemy, `hoi_20b` values, vanilla captions); the mission head bar holding the three controls over the sky piece with the combat widgets at their vanilla offsets (air_combat_wnd at 18,379; the two tooltip boxes at 28,430 and 28,534); the chart card (Days / Months / Years in the head bar, 800x276 plot, dotted grid lines at 73 and 205, zero line at 336, y labels 64 wide on the lines, x labels swapped to read `30 ... Days ... 0`); the channel table (12 rows of 24, a caption column, Our cell at 334 and Enemy cell at 617, each with tick box, swatch and the value alone).

**Files.** `interface/1440p_ui.gfx` block `# --- A10 ---` (21 sprites `GFX_1440p_AR_*`: tiles of vanilla textures, the superiority bar and frame, the plot, the two line tiles, the sky, the channel cell and its 400 wide twin for option A, a transparent sprite); `interface/zz_1440p_vanilla_sprites.gfx` block `# --- A10 ---` (`GFX_strategicair_linechart` again as `LineChartType`, 800x276, linewidth 3, [LOAD-012]); `tests/GuiInvariants.Tests.ps1` (the name in the list, and `LineChartType` skipped by the "no texturefile" check, since a chart has no texture); `tools/stretch_background.py` block A10 (three textures in `gfx/interface/1440p_ui/`: `ar_sky.dds` cut from `strategic_air_bg.dds`, `ar_channel_cell.dds` and `ar_channel_cell_400.dds`, two frames each: transparent and the pick band; re-run with `python -I tools/stretch_background.py --only ar_`); `tools/build_managers.py` section A10 (12 caption keys `MOD1440_AR_CH_1..12` in `mod1440_l_<language>.yml` and, under every language, `localisation/<language>/replace/mod1440_ar_l_<language>.yml` giving `AIRVIEW_DETAILS_CHANNEL_1..24` again as `$VAL|R1$` and the like); `tools/scenes/air_region.json` (written by `scratch/phases/A10/build/make_scene.py`).

**Decisions as built** (decisions-final.json): 1 full size; 2 option B (value-only cells through the replace files; option A is a switch, below); 3 the cloud picture kept as its own card under a head bar; 4 no hotkey.

**Deviations.**
- The friendly-presence marks (`wing_type_friendly_left_n`) keep their own vanilla offset to the wing icon per mark (+1, -1, -1, -2 in y), not one common +1 (design item 3 said "+0,+1").
- The four `*_text_bg` number plates are not drawn behind their values; they get the transparent sprite `GFX_1440p_AR_hidden` (the design offered both; the mock-up has no plates).
- The 24 vanilla keys are given with the English formats under every language: Brazilian Portuguese, Japanese and Polish have `G1` on channels 10 and 11 and French `R0` on channel 3 in the game, which are typos of those files (colour or decimals differ from the other languages).
- `GuiInvariants.Tests.ps1` got one more small edit than the list: a `LineChartType` has no texture, so the "points every declared sprite at a texture" test skips it.
- The plot ground is one `black_bg_tile` layer (the mock-up drew it twice, so it was a shade darker).

**Not seen in game** (design `openInGame` 1-10, in the order of the checklist): the chart drawn at 800x276 with 3 px lines from the redeclared sprite; the largest value at the upper grid line and its half at the middle one; the right end of the line is today; a click on a value cell ticks the channel; the replace folder wins over the game's `core_l_<language>.yml` (the register has no record of giving a vanilla key again); frame 2 of the cell sprite on a ticked channel and frame 1 (transparent) taking the click; the window opening at its file position; Months and Years; the mission card in a war; the click on a region in the recipe (see below).

**The recipe.** `{"move":"select_airbase"}`, `{"key":"escape"}`, then a raw `{"click":[1485,922]}` on an empty spot of Eastern Germany between Berlin and Silesia: this position is an ESTIMATE read off `reference/mod/air_selection.jpg`, not measured; the first launch measures it (`tools/Invoke-GameSteps.ps1 -Region` on a grid capture) and turns it into a note. The capture `details` clicks `strategicairview/details_open`. In a paused 1936 peace every count is 0 and the chart is empty, so the chart with data is the user's own game.

**Fallbacks.**
- If the replace files do not win (the cells show the game's whole texts, or a bare key): first move them to `localisation/replace/<language>/` (the folder the renderer also reads); if that fails too, option A: set `AR_CHANNEL_VALUE_ONLY = False` in `tools/build_managers.py`, run `python -I tools/build_managers.py` (it stops writing the captions and the replace files; delete the old ones under `localisation/*/replace/` by hand) and `python -I scratch/phases/A10/build/apply_a10.py A` (cells of 400 on `GFX_1440p_AR_channel_cell_400`, no caption column, the game's whole texts), then restart the game.
- If the chart stays 380x150 (the sprite is not redeclared from the later file), the grid lines and the plot are 276 high: lower the plot to the chart's size (`GFX_1440p_AR_plot` 380x150 and the grid at its label heights) in `apply_a10.py`.

**Game check.** `tools/Invoke-GameCheck.ps1 air_region` (one launch: the window with Details closed, then the capture `details`). Checklist: the twelve items of `tools/scenes/air_region.json`.

**Tests.** `build.ps1 -Check air_region`: 663 passed, 0 failed, 60 skipped; `build_managers.py --check` up to date; `Compare-Baseline.ps1 zz_1440p_air_region.gui -Group`: 437 changes, all positions, sizes, fonts, sprites and the new `mod1440_ar_*` plates (no widget renamed, retyped or dropped).

## Game checks

| # | Date | Build | By | Checked | Result | Screenshot | Taught |
|---|---|---|---|---|---|---|---|
| 1 | 2026-10-18 | c15c451+dirty | the user (their ongoing campaign and playset) | the view in their ongoing campaign | "Everything seems to work and I didn't find any bugs." | none | the redeclared chart sprite and the replace localisation work (SPR-025, LOC-013) |

The harness made no launch in this phase: the user tested the build in their own game before the launches of gate 2 were granted, and that verdict is the game check. So the recipe's click on a region was never measured, and `reference/` has no capture of this view, vanilla or reworked.

Not seen in game by the orchestrator (the user's verdict covers them without a screenshot): the label heights against the grid lines, Months and Years, a click on a value cell, a long region name, other languages than the user's.

## Fix rounds

None: the user found no defects.

## Close

2026-10-18, closed by the orchestrator at the user's word ("At this point you can commit the changes and mark this as done").

- [x] Roadmap status and link
- [x] README "Reworked screens"
- [x] Workshop description: not published on the Workshop; nothing to update
- [x] `version` in `descriptor.mod`: 1.9 (the README had stayed at 1.7 since D7 raised it to 1.8)
- [x] Engine Facts rows added: W44 = SPR-025 (a `LineChartType` sets the chart's size and line width, 40 points at most; confirmed), W45 = GUW-041 (the channels, their colours and the labels; executable), W46 = GUW-042 (what the code looks up; executable), L12 = LOC-013 (a file under `localisation/<language>/replace/` gives a vanilla key again; provisional, the user's verdict without a screenshot). Dropped: GUW-009 for the vanilla labels of 30 px (already the record's subject), the test's `LineChartType` skip (tooling, not engine), the typos of four languages' channel keys (game data, kept in the body of LOC-013).
- [ ] Scene file final (`tools/scenes/air_region.json`): the click on a region is still the estimate 1485,922; measure it at the next launch that runs this scene.
- [ ] Finished screen stored: `tools/Invoke-GameCheck.ps1 air_region -SaveReference` and `-Vanilla -SaveReference`: needs a launch the user grants; none was made.
- The option A fallback (`scratch/phases/A10/build/apply_a10.py`) is no longer needed; `AR_CHANNEL_VALUE_ONLY` in `tools/build_managers.py` stays as the switch.
