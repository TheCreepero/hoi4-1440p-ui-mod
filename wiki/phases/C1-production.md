# Phase C1: production

The panel the production tab opens: the factories and filters at the top, one card per production line under them. Status: built on 2026-10-16 and checked by render and tests; no game check yet. Override file: `interface/zz_1440p_production.gui`.

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

## Close

- [ ] Roadmap status and link
- [ ] README "Reworked screens"
- [ ] Workshop description
- [ ] `version` in `descriptor.mod`
- [ ] Engine Facts rows confirmed or added
- [x] Scene file (`tools/scenes/production.json`)
- [ ] Finished screen stored under `reference/mod/`
