# Phase A5: recruit and deploy

The two panels the `u` key opens: Recruit & Deploy (equipment priorities and the divisions in training) and Division Templates beside it. Status: done. Built and checked by the harness on 2026-10-11; the tester tried it in game on 2026-10-12 and found it good. The redesign of 2026-10-16 (below): built and checked by render and tests; not seen in game. Override file: `interface/zz_1440p_recruit_deploy.gui`.

## Scope

- Vanilla file and windows, all in `countrydeploymentview.gui`:
  - `countrydeploymentview` (the left panel) with the rows of its one list: `deploy_entry` and `supply_deploy_entry` (the six priority rows), `military_deployment_conveyor_view` (the card of a template in training), `military_deployment_conveyor_summary_view` (the row under the card), `military_deployment_line_view` (a division in training), `military_deployment_conveyor_end_view` (the closing line), and `division_name_dropdown_entry` (the name list of a line).
  - `templatedeploymentwindow` (the right panel) with `named_division_template_entry` and `foreign_template_item`.
- What the vanilla screen crams or hides:
  - The name of a division in training has about 165 px in `hoi_16mbs`: "29. Infanterie-Division (mot.)" (169 px) is cut.
  - Equipment and training of a line are two bars of 68 px, told apart by an 18 px icon.
  - A template takes two lines of a 72 px row, and its name wraps at 198 px ("Vozdushno-Desantnaya Brigada" is 212 px in `hoi_18mbs`). Italy's 14 templates fill 1008 px; 17 fit before the list scrolls.
  - The six priority rows take 282 px for a 72 px bar each.
  - No button of either panel has a hotkey, apart from Escape on Close.
- Out of scope: the division designer that Edit opens (out of scope, Roadmap Milestone B), the army HQ templates (`countryofficercorpview.gui`), any new value (see Inventory).

## Inventory

- Vanilla references: `reference/vanilla/recruit_deploy*` (three templates in training with six lines, the name list of a line, the symbol picker, and Italy's 14 templates with the decommissioned ones shown).
- States of the screen:
  - **Nothing in training:** the six priority rows only (a new game).
  - **In training:** per template a card, a summary row, one row per division and a closing line. The summary's button folds the rows away.
  - **Symbol picker:** a click on a template's icon lays `div_templ_custom_icon_view` over the template list.
  - **Foreign templates:** the dropdown left of the special forces count. Germany has no subject in 1936 and the button opened nothing; not captured.
  - **Ready to deploy:** needs time to pass, which the harness never does; not captured.
- Where the windows sit, with and without the mod so far: `countrydeploymentview` at -6,78 and `templatedeploymentwindow` at 538,78, their `show_position`. Both are as high as the screen (`100%%`), so they cover the left end of the bottom bar: the army portraits start at about x 1150.
- One list holds every row of the left panel: `deployments_list_gridbox`, a grid with a slot of 1x1. The code stacks its rows by the height of each row window and honours the row window's own `position` (the summary sits 15 px left of the card, a line 13 px). The scrolling container's top margin of 13 px moves the first row down. Checked on a vanilla capture: 13 widgets at 0 px ([Engine Facts](../Engine-Facts.md) S27).
- `templates_grid` has a slot of 355x1 and stacks its rows the same way, 72 px apart.
- `Show-GuiOutline -Comments`: no size is set in code.
- `Show-CodeNames`: no window has a widget the code would fill and vanilla leaves out, as far as the names show. `subject_templates_icon` is stored with the template panel's names and is in no vanilla file; `deploy_time`, `deploy_time_icon` and `cp_icon` are stored next to the template row's names but belong to the army HQ template row of `countryofficercorpview.gui`. Neither was tried.
- Lists and rows: `templates_grid` and the name list `grid` are entry pairs in `tools/gui-links.json`. The mixed list `deployments_list_gridbox` is the scene's `listRows`, a sequence of row windows: an entry pair would demand one row width for its slot of 1 px.
- Bitmap backgrounds: every row (`deploy_reinforcements_entry.dds` 493x57, `military_deployment_conveyor_bg.dds` 490x84, `military_deployment_add_line_bg.dds` 518x40, `military_deployment_line_bg.dds` 514x40, `military_deployment_end_line.dds` 516x11, `deployment_named_division_bg.dds` 346x78 and its brown twin), the location button (223x31, two frames), the two panel headers and the strip under the left one. Option 4 of the Design Rules for all. The panels themselves are tiled.
- **The code swaps the background of a priority row** for a vanilla sprite per kind of row (`GFX_deploy_upgrades_entry`, `GFX_deploy_supply_entry`, `GFX_deploy_operations_entry`, `GFX_deploy_garrisons_entry`), and the icon with it. Found in `countrydeploymentview.gfx` after the proposal; a wider background on these rows would not stay ([Engine Facts](../Engine-Facts.md) G16). The file also declares `GFX_deployment_entry_stalled_progressbar`, so the bars of a line may be swapped the same way; they keep their vanilla sprite.
- Vanilla keys for captions, should a layout want them: `DEPLOYMENT_DIVISION_LABEL` ("Division"), `DEPLOYMENT_PROGRESS_LABEL` ("Progress"), `DEPLOYMENT_PRIORITY_LABEL` ("Priority"), `DEPLOYMENT_DEPLOY_LABEL` ("Deploy").
- Recipes that clicked into these panels with a raw position: the move `open_division_designer` (Edit of the first template). It is a `clickWidget` now.
- Engine facts this screen depends on that are still untested: two visible buttons sharing a hotkey (W7), should Train or Add Unit get one.

## Proposal

What the player should see at once: every division in training with its whole name and how far its equipment and training are, and every template with its whole name, without scrolling either list in a mid-game country.

Three layouts were put to the user on 2026-10-11, who chose A. Widths are both panels together; vanilla is 913.

| | Left panel | Templates | Total | The bottom bar |
|---|---|---|---|---|
| A | 640: line names whole, wider bars | 590: one template per line of 46 px | about 1220 | the template panel ends above it |
| B | 640, as in A | 375, vanilla rows with the name in a larger font | about 1005 | free, as in vanilla |
| C | 550, larger fonts only | 590, as in A | about 1130 | free, just |

What was built (layout A). Both panels together are 1246 px wide: the left panel 640 from x -6, the template panel 618 from x 628.

| Panel or column | Vanilla | Built | Why |
|---|---|---|---|
| Left panel | 550 wide | 640 wide | the growth of 90 px goes to the name of a line |
| Line name | 150 px box, `hoi_16mbs` | 240 px box, `hoi_18mbs` | "3. SS-Panzer-Division 'Totenkopf'" is 225 px |
| Equipment and training bar of a line | 68 px each | 68 px each, 90 px further right | the code may swap their sprite |
| Series of a line, count of a card | `hoi_16mbs` | `hoi_18mbs` | |
| Card of a template in training | 488 wide, name 200 px in `hoi_18b` | 578 wide, name 290 px in `hoi_20b` | the name of the template whole |
| Location button of a card | 223 px | 313 px | fills the row beside Add Unit |
| Priority row | 493 wide at the left | 493 wide, in the middle of the list; name in `hoi_18mbs` | the code swaps its background (see Inventory) |
| Template row | 341x72: name over Train and Edit | 581x48: icon, name, cap, Train, Edit, toggles on one line | 22 templates before the list scrolls instead of 17 |
| Template name | 198 px, centred, wraps | 218 px, from the left, one line, `hoi_18mbs` | "Vozdushno-Desantnaya Brigada" is 212 px |
| Template panel | 375 wide, the whole screen high | 618 wide, ends at y 1288 | the army portraits of the bottom bar stay free |
| Symbol picker | four symbols per row | seven per row | the wider panel |
| Name list of a line | 250x300, ten names in `hoi_16mbs` | 340x434, fourteen names in `hoi_18mbs` | |
| List of foreign templates | opens at x 335 of the panel | at x 578 | beside the wider panel; not seen in game |

Additions, each with the row of "What a redesign can add" that allows it:

- Hotkey `shift+f` on Division Designer (`open_designer_button`): "Hotkeys". Pressed in check 3: the designer opened.
- Tried and dropped: `deploy_time` and `deploy_time_icon` in the template row. The code does not fill them there ([Engine Facts](../Engine-Facts.md) W25).

## Decisions

- 2026-10-11: the scene's default state is three templates in training, not the empty panel: the redesign is about the lines. The scene's `teardown` cancels them again.
- 2026-10-11: **layout A**, chosen by the user from three text mock-ups and a frame with the three widths drawn on it (`scratch/previews/a5_width_options.png`).
- 2026-10-11: **the priority rows stay 493 wide.** The proposal had them 583 wide with a 150 px bar. The code sets their background to a vanilla sprite per kind of row, so they keep their vanilla look and sit in the middle of the list, 45 px in.
- 2026-10-11: a template row is 48 px high, not the 46 proposed: the priority mark of a template is a strip of 52 px with its chevrons at the two ends, and at 48 they stay within 2 px of the row.
- 2026-10-11: the template name keeps `hoi_18mbs`. Beside the cap, Train, Edit and the toggles the name has 218 px; in `hoi_20b` "Vozdushno-Desantnaya Brigada" (224 px) would be cut, in `hoi_18mbs` (212 px) it is whole. The row is 581 px, 21 more than proposed, for the same reason.
- 2026-10-11: both panels together are 1246 px, not "about 1220" as put to the user: the 21 px of the template row and a 5 px slip in the estimate. With the template panel ending at y 1288 the list holds 22 rows, not the 26 named in the question, which counted the whole screen height.
- 2026-10-11: Train and Edit sit in the dark name box, where the metal strip under it was. The strip is gone with the second line.
- 2026-10-12: **the tester judged the phase finished.** The width of 1246 px is fine, the narrower priority rows are fine and stay as they are, and everything on the list under "Left for the tester" works: tooltips, the clicks, a line becoming ready and a long list. The tester also opened the list of foreign templates, which the harness could not reach, and it works.
- 2026-10-16: **step 2, the priority rows as wide as the training cards** (user, after a mock-up on the design page). Roadmap F3 showed that the code draws a row at the size of the sprite it puts there, so the six row sprites are declared again under their vanilla names with textures 575 wide (`interface/zz_1440p_vanilla_sprites.gfx`, jobs `rd_*_entry`; only Recruit & Deploy uses them). The rows stand at x 2 of the list, from 22 to 597 on the screen like the cards; the label plate is 211 px (159), the equipment meter 148 (108) with a bar of 112 (72) on new `GFX_1440p_RD_` sprites; the priority dots keep their place from the right end. The meter's bar is `GFX_deployment_progressbar`, named in the file, so the bars of the training lines keep their vanilla length. Built and rendered; no game check yet. Open for it: each of the six rows in its own colour, the label of the longest priority in each language whole.

## Redesign build (2026-10-16)

The redesign agreed on the design page of 2026-10-16 (one card per template in training, stacked bars, wider template names, the checkbox in the tool strip, the symbol picker over both panels; every decision as recommended). Layout script: `scratch/a5/layout_a5r.py` (absolute values; kept beside the design under `scratch/redesign/a5-recruit/`).

What was built:

- **One card per template in training on the 575 px spine.** Head, band, lines and foot all stand at x 2 of the list, 575 wide, like the step-2 priority rows. Their backgrounds are one frame, `tiles/tiled_window2_1b_border.dds` drawn at 575 and cut into four slices (`card_slice` in `tools/stretch_background.py`, same sprite and file names as before): the head 575x84 with a transparent gap of 6 on top, the band 575x32, a line 575x40 and the foot 575x9 (the rim). Band and line are rows of the frame's plain inside, so they join in any order and a folded card (band on foot) stays closed. Per card: 125 + 40 per line.
- **Head:** symbol tile 78x66 at 8,12 (`GFX_1440p_RD_card_icon_tile`), the symbol at 9,24 with its marks; title strip 475x32 at 92,12 (`GFX_1440p_RD_card_title`, the unit list header tile) with the name (290, `hoi_20b`), series - amount + at 404 to 503 and the three priority dots at 508, 528, 548; action strip at y 48: location button 283x31 at 92 (was 313) with the group button in its left end, Add Unit at 384, deploy and cancel at 505 and 536.
- **Band:** 32 high (was 40) on a dark strip 559x28 (`GFX_1440p_RD_card_band`): order arrows at 12 and 41, the count left-aligned at 82 (200 px), the card's equipment icon and bar at 306 and 332, straight above the bars of the lines, fold at 539.
- **Line:** name field 292x30 at 8,5 (`GFX_1440p_RD_line_name_field`) holding the dropdown, edit box 262x22 at 14,9 and the expand button at 278; a bar holder 156x36 at 302,2 (`GFX_1440p_RD_line_bars`) with equipment over training: `army_equipment` 306,3 and `equipment_progressbar` 332,6; `army_training` 308,20 at `scale = 0.67` and `training_progressbar` 332,23. Series 44 px at 458, deploy at 512, cancel at 542.
- **Bars of 120 px:** `GFX_deployment_entry_progressbar` and `GFX_deployment_entry_stalled_progressbar` declared again at 120x12 on their vanilla textures in `interface/zz_1440p_vanilla_sprites.gfx` and listed in `tests/GuiInvariants.Tests.ps1`. The code puts them on the line bars and the band's bar [SPR-015]; only `countrydeploymentview.gui` names them in vanilla, and no mod of the playset declares them.
- **Template row (581x48):** the plate and the symbol's tile are one bitmap per state, so that the code's swap of `Background` and `Background_obsolete` swaps the tile too: `GFX_1440p_RD_template_plate` (tiled_plain_bg_small with the 84x40 tile of the priority rows at 3,4) and `GFX_1440p_RD_template_plate_obsolete` (the brown `deployment_item_bg` frame with the copper symbol box of the vanilla decommissioned row), both made by `template_plate` in `tools/stretch_background.py`. Name field 306x36 at 92,6, the name at 100 with 258 px (was 218), the cap 38 px at 356 inside the field, Train and Edit 56x26 at 404 and 462 on `GFX_1440p_RD_button_56` (the 71x26 button's texture tiled), the decommission toggle at 524, delete at 548. The old one-line bitmaps (`GFX_1440p_RD_template_entry`, `_obsolete`) stay declared as the fallback.
- **One tool strip:** `show_decommissioned_templates_window` 276x44 at 144,52 on a transparent background, its checkbox at 0,6 with **`shift+v`** and its text at 38,13 in `hoi_16mbs`, fixed 236 px; the special forces icon and count at 62 and 92; Division Designer at 434. The list starts at y 96 (was 138) and is 1110 high: 23 templates before it scrolls. `tools/check_playset.py` reports no other user of `shift+v`.
- **Symbol picker:** `div_templ_custom_icon_view` 1252x1114 at -634,96 of the template panel (screen -6 to 1246, y 174 to 1288), Back and Default symbol side by side at 374 and 630, `symbols_grid` at 38,47 with 14 slots a row (1176 wide): 21 rows, 294 symbols on screen.
- Both panels still end at x 1246, with `clipping = no` on both; Army Readiness keeps its x of 1256.

Deviations from the design:

- Every second line is not 16 % darker: all lines are one row window, which the code repeats, so a line cannot know its place.
- The location button is 283 px, not 284: its chevron frame repeats every 15 columns, so it grows by 60.
- The template row's icon tile is part of the two plate bitmaps, not an icon on a tiled plate: an icon would lie above `Background_obsolete` and hide the copper box that marks a decommissioned template (the mock-up took that box from a capture).
- The symbol picker starts at y 174 as designed, so the upper 36 px of the first priority row stay visible above it (the mock-up drew the left panel without its rows).

Not seen in game:

- Whether the code draws the redeclared bar sprites at 120x12 on the line bars and the band, normal and stalled; whether `scale = 0.67` on `army_training` survives the code setting its frame (Better Mechanics' `GFX_unit_level` has 10 frames, RT56's 21, all 27 px).
- The card frame across head, band, lines and foot with lines added, a card folded, a line ready to deploy and a card with a location set.
- The picker drawn left of the template panel: whether it lies above the Recruit & Deploy panel and takes clicks there, Back and Escape.
- The tooltips of the two stacked bars; the checkbox text in the tool strip in other languages; `shift+v` and the moved checkbox window toggling the list; the brown plate and the 56 px buttons of a decommissioned template (View).

Game check, when the user allows a launch:

    tools/Invoke-GameCheck.ps1 recruit_deploy

The tester's checklist (the scene's `checklist` in `tools/scenes/recruit_deploy.json`):

1. Width: both panels together are 1246 px (vanilla 913); the template panel ends above the army portraits
2. Cards (redesign 2026-10-16): every template in training is one frame from its head to its foot on the 575 px spine of the priority rows; no seam between head, band, lines and foot, also with lines added and with a card folded (band right on the foot)
3. Bars: equipment over training, 120 px each, on every line and the card's bar in the band; the stalled (red) bar is 120 too; the training icon is small (scale 0.67) and shows the right level
4. A line: rename it in its box (262 px), pick a name from the list (it opens under the name field), the deploy and cancel buttons
5. A card: set a location (the 283 px button, then the map; the chevron frame), assign an order, the series - and +, the three priority dots, fold and unfold, the two order arrows
6. A template: Train (and Shift+click for five), Edit or View (56 px buttons), the decommission toggle, delete on a template of your own; the brown plate of a decommissioned template
7. Tool strip: Show decommissioned templates sits between the special forces count and Division Designer; Shift+V ticks and unticks it and the list follows; 23 templates fit before the list scrolls
8. The symbol picker: it opens over the template panel with 7 symbols a row (Back and Default symbol side by side), nothing of it under the Recruit & Deploy panel; pick a symbol, Default symbol, Back, Escape
9. Shift+F opens the division designer
10. Priority rows (step 2): six rows as wide as the cards under them, each in its own colour, label and meter whole, the three dots

### Fix round 1

- 2026-10-16, the symbol picker partly under Recruit & Deploy (user's test, `template_icons.png`): the game draws the Recruit & Deploy panel above the picker where the picker reaches left of its own panel, so the left half (and Back) was hidden. The design's fallback: `div_templ_custom_icon_view` 612x1111 at 6,95 (the left panel ends 6 px into the template panel), `symbols_grid` 7 a row at 4,47; Back and Default symbol stay side by side (54 and 310), so the grid starts at 47 instead of 88. Re-test: the whole picker visible and clickable, 7 a row, Back.

## Game checks

| # | Date | Build | Checked | Result | Screenshot | Taught |
|---|---|---|---|---|---|---|
| 0 | 2026-10-11 | vanilla | exploration: Train, Add Unit, the name list, the foreign templates button, the symbol picker, a folded card, the Soviet and Italian template lists | all captured but the foreign templates list, which did not open | `scratch/checks/a5_van_*` | S27 |
| 1 | 2026-10-11 | vanilla | the scene's recipe from a cold start, stored as reference | verified, four captures; the teardown left the panel as a new game has it | `reference/vanilla/recruit_deploy*` | H32 |
| 2 | 2026-10-11 | 5a25450+dirty | first build: three templates in training, the name list, the symbol picker, Italy's templates; the division designer through the move that clicks Edit by name; the `deploy_time` experiment | all as rendered, every expected widget at 0 px, `error.log` clean. The priority rows keep their colours 45 px in; "X1" of the experiment stayed on every row | `scratch/checks/recruit_deploy-*-2022*`, `a5_m1_*` | S27 with the mod's sizes, G16, W25, S28 |
| 3 | 2026-10-11 | 5a25450+dirty | the same without the experiment, stored as reference; then `u` and `shift+f` | verified; the division designer opened on the hotkey | `reference/mod/recruit_deploy*`, `scratch/checks/a5_hk_designer-*` | W26 |
| 4 | 2026-10-12 | 5a25450+dirty | by the tester, in a game of their own: the eight items under "Left for the tester" and the foreign templates list | all work; width and priority rows accepted | none | - |

Not seen by the harness (states a paused 1936 start does not show). The tester covered them in check 4, without screenshots:

- A line that is ready to deploy, a card with a location set, a card assigned to an order.
- The foreign templates list, and a template with a foreign, colonial or exile flag.
- A list long enough to scroll: more than 22 templates, or more lines than the left panel holds.
- A template with the HQ, paratrooper or special forces mark beside a priority mark (Italy shows the special forces and priority marks one at a time), and a template whose Delete is enabled.
- The chevron frame of the location button, and the limit number on Add Unit.

## Left for the tester

1. Whether 1246 px for both panels is too much (vanilla: 913), and whether the template panel should end above the army portraits as it does now.
2. Whether the six priority rows, narrower than the cards under them and centred, look right.
3. Tooltips on a line's two bars, on a card and on a template row.
4. A line: rename it in its box, pick a name from the list, deploy and cancel.
5. A card: set a location (the button, then the map), assign an order, the series - and +, the priority dots, fold and unfold, the two order arrows.
6. A template: Train (and Shift+click for five), Edit, the decommission toggle, delete.
7. The symbol picker: pick a symbol, Default symbol, Back.
8. With time running: a line that becomes ready, and a long list scrolled to the end.

## Close

- [x] Roadmap status and link
- [x] README "Reworked screens"
- [x] Workshop description
- [x] `version` in `descriptor.mod` (1.4)
- [x] Engine Facts rows confirmed or added
- [x] Scene file (`tools/scenes/recruit_deploy.json`); the move `open_division_designer` clicks by name
- [x] Finished screen stored under `reference/mod/`
- [x] The tester's judgement: finished, 2026-10-12
