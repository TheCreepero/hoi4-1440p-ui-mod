# Phase C1: production

The panel the production tab opens: the factories and filters at the top, one card per production line under them. Status: done. Round 2 (bold variant) built on 2026-10-20 and checked by the user in their own game on 2026-10-21 after one fix (wheel scrolling); round 1 built 2026-10-16, checked in the user's game. Override file: `interface/zz_1440p_production.gui`.

## Scope

- Vanilla file and windows, all in `countryproductionlineview.gui`: `countryproductionlineview` (the panel), the ten kinds of line (`production_military_line_entry`, `production_naval_line_entry`, `production_ship_refit_line_entry`, `production_railway_gun_line_entry`, each also `_collapsed`, and the two `_new_line_entry`), `production_consumergoods_line_entry`; five windows that slide in beside the panel: `production_equipment_window_military`, `production_equipment_window`, `production_deployment_window`, `ship_name_list_window`, `navy_repair_window`.
- What the vanilla screen crams or hides:
  - A line is 500 to 513 px and 111 high; seven lines fit on the screen.
  - The top takes 253 px in six bands: resources, efficiency, factories, two rows of filters.
  - The ship picture is drawn at about 220 px; the hull textures are 273 to 332.
- Out of scope: the windows of military-industrial organisations (centred, in a subfolder), the trade and construction tabs.

## Inventory

- Vanilla reference: `reference/vanilla/production*` (the naval tab of a 1936 start).
- Window bindings (the Manager's `window-bindings-1440p-backlog.md`): every lookup of the panel and its lines searches direct children, so the layout keeps the vanilla nesting. Nothing the code would fill that vanilla leaves out.
- Sprites the code sets (`code-set-sprites.md`): `GFX_production_item` and `GFX_naval_production_item_bg_strip` (the line backgrounds), the progress bars, the glows and the factory icons. The two backgrounds are declared again under their vanilla names with the wider textures (`interface/zz_1440p_vanilla_sprites.gfx`); only the production panel uses them.
- The naval background has three frames, one per row of factory slots (5, 10, 15); the code picks the frame.
- File variables `@prod_icon_pos_x`, `@prod_sub_pos_x`, `@prod_add_pos_x`, `@prod_nof_pos_x` place the factories-in-use group; the override file defines them (L6).
- Lists: `item_grid` of `production_lines` (slot height 1: the code stacks lines by their height), entry pairs in `tools/gui-links.json`. The resource strip of the top is filled with `resource_strip_item`; the scene names it for the renderer.
- Bitmaps (option 4, `tools/stretch_background.py`, jobs `pd_*`): the lines grow by 142 columns in the plain middle of the equipment plate and 347 in the dark gap after it; the plates, collapsed strips and outdated overlays by the 142; the top is cut into its four bands and laid out as two rows (`production_header`).
- Vanilla Navy Rework, in the user's playset, overrides the naval line windows and the equipment picker; this mod's windows win by file name and replace them (user's decision, 2026-10-16).

## Proposal

Agreed on mock-ups on 2026-10-15 and 2026-10-16 (round 2 of the design page): taller lines than round 1, the factory grid kept, larger ship pictures.

| Panel or column | Vanilla | Built | Why |
|---|---|---|---|
| Panel | 550 | 820 (round 1: 1044) | lines of 780 |
| Top | 253 px, six bands | 126 px, three rows: resources and factories in use; add-line buttons and the six efficiency figures; the twelve filters in one row | three more lines on the screen |
| A line | 500-513 x 111 | 780 x 111 | |
| Equipment plate | 278 | 298 (first build 420) | the code draws the picture at a fixed place; 20 free on each side |
| Column after the plate | 37 px gap | 221 px from 16 after the plate: manufacturer and deploy location (185 px button) or efficiency; the ready date bar across it | the header band kept only the name |
| Line name | 150 px | 370 px | |
| Factory slots, amount, resources | | moved with the right end | |
| Lines on the screen | 7 | 10 | |

## Decisions

- 2026-10-16: Production first; keep the factory grid, taller lines and larger pictures; override Vanilla Navy Rework's naval rows (user).
- 2026-10-16: the line backgrounds the code sets are declared again under their vanilla names (user, with the priority rows of A5).
- 2026-10-16: the equipment lists scroll by whole rows (80 instead of 40), as in A7.

## Open for the first game check

- ~~Whether the game draws the ship picture larger in the wider plate~~: it does not; it draws it at a fixed place (check 1).
- Land lines, collapsed lines, refit and railway gun lines: the render shows them only in their file state.

## Game checks

| # | Date | Build | Checked | Result | Screenshot | Taught |
|---|---|---|---|---|---|---|
| 1 | 2026-10-16 | working tree | the tester, in a 1944 game as the United States | no bugs. Two notes: the ship picture is not centred in its plate and has too much room. Measured on the screenshot: the code draws the picture at a fixed place ending at column 277 whatever the plate's width, so the 142 added columns stayed empty. The plate now grows by 20 (298), the column after it by 469 | `Screenshots/hoi4_21.png` | [GUL-041]; Spacing (Design Rules) |
| 2 | 2026-10-16 | working tree | the tester, the same game | the plate fits the picture now, but the panel is too wide and has too much empty space (a column of about 300 px in each line, empty space under the factories). A redesign at 820 px is proposed on a design page (round 3) | `Screenshots/hoi4_24.png` | - |
| - | 2026-10-16 | working tree | round 3 on the design page | the user: much better; the manufacturer, deploy location and date were bunched together in their column. Built at 820 px with the deploy location button 185 wide (the fleet name whole) and the date bar across the column (221, the three bar sprites declared again) | (design page) | - |
| 3 | 2026-10-16 | working tree | the tester, the user's playset | looks very good. RBM's GFX Overhaul draws the fleet insignia on the deploy button about 40 px wide, over the start of the fleet name: the name moved 12 px right (maxWidth 138) | `Screenshots/hoi4_27.png` | - |

## Round 2: redesign (opened 2026-10-17)

The user, 2026-10-17: "I am still a bit unhappy with the production window. In game it doesn't feel much better to use than in vanilla, and it doesn't look any better either." The first build kept the vanilla textures and stretched them; this round asks for a redesign of how the panel is used and how it looks, run by the workflow of `wiki/Workflow.md`.

### Roles and handoffs

- Orchestrator: the interactive session. Designer: agent `designer`. Builder: `builder-screen` (vanilla screen). Game checker: `game-checker`.
- Handoffs: `scratch/phases/C1/` (`contracts.md`, `design.json`, mock-ups, `decisions-final.json`, `build/`, `checks/`).
- Design page: https://claude.ai/artifact/8ebSX87ogb4owqPeCKy1Sg (published 2026-10-17; designer's proposal `scratch/phases/C1/design.json`, gate A passed with one question added by the orchestrator: whether the look goes far enough)

### Decisions (round 2)

- 2026-10-17: the user approved the proposal on the design page.
- 2026-10-20 (user, on the design page): the look does not go far enough, so a bolder variant is drawn before anything is built. Approved: new dark cards from vanilla tiles; materials in a row of up to four in the head bar; the cost-per-unit experiment; wheel step 116; the five slide-in windows kept; panel width 820. Against the recommendation, the close button stays at the panel's right edge, where the top bar's alerts can cover it (ESCAPE closes it either way). Recorded in `scratch/phases/C1/decisions-final.json`.
- 2026-10-20: the designer drew the bold variant (steel cards on near-black, `hoi_24header` names, factory count and date; `scratch/phases/C1/design.json`, the first proposal kept as `design-r2a.json`). Published on the same design page beside the first proposal, with four new decisions and the question of which look to build; the page keeps the answers under the review id `C1-bold`.
- 2026-10-20 (user, on the design page): build the bold variant; names, factory count and date in `hoi_24header`; light steel head band; the blue (naval) and green (land) picture plates kept; near-black background. The builder settles the material amounts' font so three digits fit the 46 px slot (gate A finding). Build handed to `builder-screen`.
- 2026-10-20: `contracts.md` now names the tree's new place, `C:\dev\Hearts of Iron IV Modding Manager\mods\hoi4-1440p-ui-mod`.
- 2026-10-21 (user, in their own game, which counts as the game check): everything works except the mouse wheel over the line list; dragging the scrollbar handle works. Cause: the build gave `production_lines` two Background blocks with `GFX_1440p_PD_none`, a transparent sprite declared `alwaystransparent = yes`, so the list had no background that takes the mouse (the register's fact that a scrolling container without a background does not scroll on the wheel). Fixed by the orchestrator: both blocks now use `GFX_1440p_PD_black_tile`, the panel's own near-black tile, as round 1's visible tiles did. The render matches the earlier one except for the tile's faint edge; `build.ps1 -Check production` passes (685 passed, 0 failed). Not yet confirmed in game.
- 2026-10-21 (user, in their own game): the wheel scrolls the list; everything else works. Phase closed. Engine fact recorded as GUW-045 (alias `1440p:W47`); the user's screenshot stored as `reference/mod/production.jpg` and `production-panel.png`.

## Build (2026-10-20)

Round 2, bold variant (`scratch/phases/C1/design.json`, mock-up script `mock_c1r2b.py`), built by `builder-screen`. Status: built and checked by render and tests; not seen in game.

**What was built.** Every card of the panel is cut from vanilla's gunmetal steel bar (`tiled_frontend_upper_bar`), recoloured only, by `tools/stretch_background.py` (block `# --- C1 ---`: `steel_plate`, `line_card`, `top_*`, jobs `pd_*`): head band x1.9 with rule and groove, graphite body x0.8, near-black insets of `tiled_window_thin_border`, slot boxes of `factory_item_bg`. The line cards are 780x110 plus 6 transparent rows (window 116; collapsed 60 + 6 = 66), so the 6 px gap and the wheel step of 116 come from the textures and the file. The panel stays 820 wide on a near-black ground (`GFX_1440p_PD_black_tile`, the vanilla tile with a border of 8). Title strip 816x46 (`GFX_1440p_PD_title`, on `production_header_bg`), the factory figures in `hoi_24header` at panel 260/394/528, the close button at the strip's right edge (ESCAPE kept). Top: three steel cards (materials 500x92 with seven black insets of 68x32 and the five add-line buttons in one row at panel y 96; the Production | Efficiency table 306x92 whose head band is the table's head bar, black bands on rows 1 and 3, values `hoi_20b` right-aligned; filters 812x36 with the twelve vanilla cells). `military_tab` and `production_win_top` now stand at panel (0,0), so the top's widgets take panel coordinates; the list container is at panel y 147 (first card at 188). Lines: head 27 high in every kind (badge, name `hoi_24header` in a fixed 356 box, manufacturer at 394, materials in a row at 428 (`resources_grid` 184x27, four slots of 46), factories - n + `hoi_24header` at 620-742, delete at 748); body as designed (production inset at 306,29: deploy target 266x32 at 310,31, bar 266x24 with the date in `hoi_24header`, cost box at 312,92; amount column at 582; factory inset at 618,29 with the grid at 623,34, slot 30x23, name list button at 622,82). Land lines: efficiency icon, bar and need in row 1, x10 / x5 at 579. Collapsed lines: the same head, the strip cut to 301, the bar at 310,31, land need at 586/618, the naval amount in the body (494/520/551) after a 180 bar, the deploy target 194 wide at 582,27. The bars `GFX_prod_progress_bar2` (_red, _yellow) are 266x24; the selection overlay is a 2 px light steel outline of the card's shape; the manufacturer tint covers the head band only. New: the cost-per-unit experiment (`production_cost`, `naval_production_cost`, empty text boxes), the top's two windows `resource_strip_item` and `production_resource_item` (added to the override file), nine `resources_grid` pairs in `tools/gui-links.json`, the scene's captures `land` and `collapsed` and its `checklist`. The five slide-in windows are unchanged.

**Deviations from the design.**
- **Material amounts (gate A finding):** `hoi_18b` (a digit is 7 px) with the strip icon at scale 0.8 (22 px) at (0,3) and the amount at (23,5) in a 23 px box: three digits end at 44 of the 46 px slot (the design's `hoi_20b` at x 26 needs 53), two digits at 37. Slot width and the four slots in a row are as designed.
- The vanilla `Background` blocks of `production_win_top` and `production_lines` stay in the file (the name-parity test counts them as widgets); they draw `GFX_1440p_PD_none` (a transparent 4x4, new job `pd_none`). The cards are `mod1440_top_*` icons behind the widgets, as in the A9 method.
- The steel texture keeps 24 columns at each side instead of 12: with 12 the bar's right-hand rivet pair was repeated into the middle of every head, onto the second material.
- The near-black panel is a cornered tile sprite (the design allowed it), no bitmap job.
- Collapsed land line: the design leaves the efficiency widgets (vanilla puts them in the head) without a place; they stand in the right part of the equipment strip (icon 158,32, frame 181,35, bar 185,36, 93 wide, ends at 278).
- Refit lines have no equipment button of their own, so the plate (expanded) and the strip (collapsed) behind the picture are decorative icons `mod1440_plate` and `mod1440_strip`; the railway gun's collapsed line uses `GFX_1440p_PD_item_collapsed` (298 wide) instead of the vanilla wide strip; the railway gun's deploy text stands at 316,37 (it has no button).
- Close button `x = -36` from the right edge, `y = 7` (a 32x33 sprite, ends at panel 816); the design says panel 784,7, the same place.
- The manufacturer tint is a flat warm colour (205,150,55) at alpha 85/255 shaped by the head band's own alpha: the one piece of art that is not a recoloured vanilla pixel texture.
- `GFX_1440p_PD_naval_line_selected` and `GFX_1440p_PD_line_selected` share `pd_line_selected.dds`; `pd_naval_line_selected.dds` and `pd_header.dds` are gone.
- The deploy buttons are the vanilla `naval_deploy_button` grown by pixel copies (266 and 194 wide), not the mock-up's mirrored widening of round 1's button.
- A land line's three rows of slot boxes are all painted into `GFX_production_item` (the code picks no frame for it), as in round 1.

**Not seen in game** (the design's `openInGame` plus): `hoi_24header` in the 27 px head (no clipped glyph, the baseline); the steel textures at 1:1 against white text; the date in `hoi_24header` on the green, yellow and red bar at 266x24; a red amount (short) in the head row, four items, three digits inside 46; the collapsed naval bar given `size = 180x24` by the file (a size on a progress-bar icon); the amount buttons' clicks over the inset; the manufacturer button at 394 with its tooltip and the tint (`has_mio_background` now has a `size`); the close button at the strip's edge and under the alerts; `production_cost` / `naval_production_cost` filled or empty; the collapsed strip at 301 and where the code draws the small picture; the grid at 623,34 against the painted boxes (icons 3 px off?); the collapsed land line's efficiency bar in the strip; the new-line entries; `production_win_top` at panel (0,0) (clicks of the add-line buttons and filters, the close button above it); 40+ lines scrolled by the wheel; the land tab (no capture exists).

**Fallbacks.**
- Name or factory count clipped by `hoi_24header` in the head: names in `hoi_20b` (decision 1's second option), y 3.
- The collapsed naval bar ignores `size` and draws 266 wide: keep the 266 bar as in the other collapsed lines, amount - infinity + at 582-640 and the short deploy button at 646-776 (name 80 px).
- The manufacturer tint covers the whole card: draw it as an `iconType` with `spriteType` (texture size) instead of the quad.
- Slot icons sit off their painted boxes: move `factories_grid` by the measured offset (naval and land alike).
- The close button does not take clicks under `production_win_top`: move the three factory figures out of that container or raise the button.
- `production_cost` stays empty after the check: delete the two text boxes.
- The efficiency bar of a collapsed land line is cut or crosses the small picture: drop it from the collapsed card.

**Fix round 1 (gate B).** Issue: the factory column of every line card was plain black, the slot boxes missing. Cause: the boxes were composited from `factory_item_bg.dds`, whose alpha is 3 (invisible on the black inset). Fix: `slot_box()` in `tools/stretch_background.py` turns one cell of the mesh of vanilla's three-row slot tray (`naval_production_item_slots_strip`, last frame) grey, lightens it x2.1 and frames it (28x22); painted at 623+30c, 34+23r: `pd_naval_line.dds` frames 1, 2, 3 hold one, two, three rows (the vanilla strip's frame order), `pd_line.dds` three rows; `factories_grid` stays at 623,34 (slot 30x23). Re-test should look at: the slot icons the code draws sit inside the boxes (not 3 px off), and the code picks the right frame by dockyard capacity. The dark knob at the left end of the deploy button is the vanilla button's badge (the deploy icon is drawn on it in game, the renderer hides it); left in. Tests: 678 passed, 0 failed.

**Tests.** `build.ps1 -Check production`: 678 passed, 0 failed, 59 skipped; the scene renders (`python -I tools/render_gui.py --scene production`, and every line window one by one) were looked at; `tools/Compare-Baseline.ps1 interface/zz_1440p_production.gui -Group` shows only the intended changes (new widgets: `mod1440_*`, `production_cost`, `naval_production_cost`).

**Game check** (needs the user's grant): `tools/Invoke-GameCheck.ps1 production`, once with this mod alone, then once with the playset (`tools/Invoke-GameSteps.ps1 -Start -Playset`: RBM's insignia and Vanilla Navy Rework's naval rows). The scene's captures `land` (ship filters switched off) and `collapsed` (the first line's expand arrow) bring the other kinds up.

**Checklist for the checker** (also `checklist` in `tools/scenes/production.json`):
1. Panel 820 px on a near-black ground; ten expanded cards 116 apart fit the screen under the title strip and the three top cards.
2. Title strip: the three factory figures in `hoi_24header` with their tooltips; the close button at the strip's right edge (under the top bar's alerts while a request is pending); ESCAPE closes the panel.
3. Top: seven materials (a four-digit amount whole), the five add-line buttons each opening its picker, the Production / Efficiency table, the twelve filters each clickable with its count.
4. A naval line: head (badge and arrows, name whole, manufacturer, up to four materials with three-digit amounts inside their slots, dockyards - n +, delete), the picture on its plate, the deploy target beside RBM's insignia, the date on the bar in all three colours, the cost box, amount + infinity -, slot icons inside their boxes, the next ship's name.
5. A land line (ships filtered off): efficiency bar, need, date bar, x10 / x5, fifteen slots, the cost box.
6. Collapsed lines (land, naval with the 180 bar and - amount +, refit, railway gun): the same head, the date in the same column as the expanded lines, the land line's efficiency bar in the strip.
7. States: selected line (2 px outline), a line with a manufacturer (tint of the head only), outdated equipment, refit line, railway gun line, consumer goods line, the new-line entries.
8. Every list scrolled to its end; one card per wheel notch; drag and drop and the priority arrows.
9. The five slide-in windows open beside the panel (x 809-814).
10. Both states of every factory button.

## Close

- [x] Roadmap status and link
- [x] README "Reworked screens"
- [ ] Workshop description
- [ ] `version` in `descriptor.mod`
- [x] Engine Facts rows confirmed or added (W47)
- [x] Scene file (`tools/scenes/production.json`)
- [x] Finished screen stored under `reference/mod/`
