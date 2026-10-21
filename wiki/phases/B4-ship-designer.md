# Phase B4: Ship designer

Reopened on 2026-10-20: the user asked for "a VNR and RBM compatible design of the ship designer" and said they had changed their mind about leaving the designers alone (Roadmap, Decisions, 2026-10-14). They also proposed a separate mod for this and any later equipment designer; that choice is decision 1 of the design page. The Manager's plan `docs/mod-plans/1440p-designers-on-rbm.md` is the general plan.

## Scope

- Vanilla file and windows: `interface/equipmentdesignerview.gui`, ten top-level windows: `countryequipmentdesignerview` (1097x542, centred), `designer_equipment_entry`, `designer_creator_entry`, `equipment_designer_name_group_entry`, `equipment_module_category_entry`, `equipment_module_entry`, `equipment_designer_3d_model_entry`, `equipment_designer_sprite_entry`, `equipment_designer_niche_icon_entry`, `equipment_designer_module_slot_entry`.
- The window the playset loads is not vanilla's: the VNR - RBM Compatibility Patch (`mods/vnr-rbm-compatibility-patch/interface/equipmentdesignerview.gui`, VNR's copy, Workshop 3811729942) sorts after RBM's GFX Overhaul and wins. It is 1097x783 at y 80, adds a fourth row of fixed module slots (`pos_fixed_module_slot_window_7` to `_10` on `@extra_fixed_btn_mod_row`), mirrors the slot columns, makes the role icon picker 750x365 with a 12-column grid of 43 px slots and an intro text, the module selector 538x600, moves the historical, save-to-file, design team and MIO buttons, and drops the five stat icons of `equipment_module_entry`. RBM's own designer changes (model selector in one column, `hoi_20bs` stat headings, `GFX_division_3d_bg`) are lost under the patch already. Full widget diff: `scratch/phases/B4/playset-diff.txt`.
- Sprites: RBM redeclares ten sprites the designer names (`GFX_division_3d_*`, `GFX_locked_icon`, `GFX_naval_dominance_texticon`, `GFX_ship_designer_popup_bg`, ...) and replaces four textures; VNR declares `rework_ship_icon_bg` and the role icon strips with 86 frames, which the patch re-declares last. The hull blueprints under `interface/equipmentdesigner/ships/` are VNR's (through RT56 - VNR - UTT Standalone v14); the code places the slots on them and they are out of scope.
- What the vanilla screen crams or hides (from the screenshot): the stats in three columns of 20 px typewriter text on a 532x270 paper, the module strip of seven 70 px slots in two rows, the name field of 164 px, the role icon picker reached through a click, the class list in a 220 px popup, no hotkey on Save, Reset, Duplicate or Close.
- Out of scope: `ship_refit_equipment_view` (already reworked in A4, `interface/zz_1440p_fleet.gui`); the hull blueprint windows; the tank, plane and division designers (later phases of the same mod, B1 to B3); any rule or cost.

## Roles and handoffs

- Handoff folder: `scratch/phases/B4/` (not in the repository): `contracts.md`, `playset-diff.txt`, `window-bindings-ship-designer.md` (made with the Manager's `report_window_bindings.py` on 2026-10-20, since the Artifacts reports do not cover this file).
- Builder: `builder-screen` (a vanilla screen, interface files only).
- Design page: https://claude.ai/artifact/B5v3tM5qsMpnbZdr7RKMTw (round 1, 2026-10-20; eight decisions, the first of them the separate mod; the "playset now" figures are renders until a capture exists)
- Contracts written (hotkeys, shared rows, shared files): yes, `scratch/phases/B4/contracts.md`
- Worktrees (several screens at once): main tree for the design; the build tree depends on decision 1 (a separate mod under `mods/`)

## Inventory

- Vanilla reference: `reference/vanilla/ship_designer.jpg` and `-panel.png` exist (Scharnhorst class, 1936 Germany). They show vanilla's window, not the playset's: a capture of the designer with the playset loaded needs one launch, asked of the user at gate A.
- Where each window sits (`at`, measured with `render_gui.py --verify`) and the `expect` widgets: centred, no `at` needed (H22); `expect` `close_button` and `duplicate_button` (scene `ship_designer`).
- `tools/Show-GuiOutline.ps1 <file> <window> -All` done for: (designer)
- `tools/Show-GuiOutline.ps1 <file> <window> -Comments`: line 127, the tooltip of one button set in code
- Code bindings: `scratch/phases/B4/window-bindings-ship-designer.md`
- Lists and their rows (added to `tools/gui-links.json`): (designer)
- Bitmap backgrounds and which option of the Design Rules applies: (designer)
- Engine facts this screen depends on that are still **untested** in [Engine Facts](../Engine-Facts.md): file-level `@variables` must be defined again in the override file (L6, untested); VNR's `@fixed_btn_mod_col_*`, `@custom_btn_mod_row`, `@extra_fixed_btn_mod_row` are such variables.

## Proposal

Designer's round 1 (2026-10-20), passed gate A: verdict rework. 1124x681 centred, steel cards on near-black; nothing on the blueprint (VNR's row variables 0 / 319 / 372, columns kept); stats as three banded tables of 180 px with hoi_20b head bars and 12 rows of 24 (the rows stay RBM's shared `designer_stat_entry`); module picker one column of 516x47 with category head bars (249 of 250 playset module names fit 330 px); role picker inside the window, 86 icons at 46 px, legend beside; compared design over the hull card; variants list beside the window at x 1120; six ctrl+ hotkeys. Every texture from vanilla assets. Full figures and numbers: `scratch/phases/B4/design.json`, `proposed_b4.py`; the design page above.

Corrections to the Scope: VNR's slot variables are defined inside `equipment_modules`, not at file level, so they travel with the copied window (LOAD-009); the comparison card under the patch keeps vanilla's paper while the rows are RBM's white text.

| Panel or column | Vanilla | Proposed | Why |
|---|---|---|---|
| | | | |

Additions, each with the row of "What a redesign can add" that allows it:

- 

## Decisions

- 2026-10-20: the user reopened the ship designer, asking for a design compatible with VNR and RBM, and proposed a separate mod for the designers. Phase opened as B4; the separate mod is decision 1 of the design page.

## Build (<date>)

Status: not started.

## Game checks

| # | Date | Build | By | Checked | Result | Screenshot | Taught |
|---|---|---|---|---|---|---|---|

Not seen in game (states the save did not show):

- 

## Fix rounds

## Close

- [ ] Roadmap status and link
- [ ] README "Reworked screens"
- [ ] Workshop description
- [ ] `version` in `descriptor.mod`
- [ ] Engine Facts rows confirmed or added
- [ ] Scene file final (`tools/scenes/ship_designer.json`)
- [ ] Finished screen stored: `tools/Invoke-GameCheck.ps1 ship_designer -SaveReference` (`reference/mod/`)
