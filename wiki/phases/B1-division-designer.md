# Phase B1: Division designer

Reopened on 2026-10-21: the user asked to resume the dropped Milestone B with "a redesign of the Division designer, while ensuring compatibility with RBM, which has its own designer redesign. Its version should be used as a starting point for our version." The ship designer (B4) was reopened the day before on the same terms; the Manager's plan `docs/mod-plans/1440p-designers-on-rbm.md` covers both.

## Scope

- Vanilla file and windows: `interface/divisiondesignerview.gui`, eighteen top-level windows: `countrydivisiondesignerview` (centred) and its rows `niche_selection_widget`, `div_template_3d_model_entry`, `division_equipment_archetype_entry`, `division_equipment_type_entry`, `division_equipment_entry`, `button_wrapper_container`, `div_templ_custom_icon_button`, `designer_division_regiment_slot_entry`, `designer_division_support_slot_entry`, `designer_subunit_category_entry`, `designer_subunit_entry`, `designer_division_entry`, `designer_div_name_group_entry`, `designer_stat_entry`, `designer_hq_modifier_entry`, `designer_adjuster_entry`, `designer_adjuster_entry_with_modifier`.
- The window the playset loads is RBM's GFX Overhaul's (frozen copy `frozen_3496134789_2026-10-17`), the only mod of the playset that defines the file. In `countrydivisiondesignerview` it drops 17 background icons and changes 40 widgets: the template icon picker on `GFX_divisiondesigner_popup_bg` with 8 columns of 76 px (vanilla 7 of 84), the 3D model selector in one column, the adjuster stats in 4 columns, the stat rows in `hoi_16mbs`. Full widget diff: `scratch/phases/B1/playset-diff.txt`. The redesign starts from RBM's window.
- NATO Counters Expanded and RBM Insignia Expanded add template icons to the picker; the designers plan names the picker's size as what the division designer needs most.
- `designer_stat_entry` and `designer_adjuster_entry_with_modifier` are shared with the tank, plane and ship designers; B4 leaves them as RBM has them.
- Out of scope: the regiment and support grids' slot positions (placed by the code, GUL-037); the rules and costs; the tank, plane and ship designers (B2, B3, B4); the Larger Selector addon's namelist dropdown.

## Roles and handoffs

- Handoff folder: `scratch/phases/B1/` (not in the repository): `contracts.md`, `playset-diff.txt`, `playset_diff.py`.
- Builder: `builder-screen` (a vanilla screen, interface files only).
- Design page: https://claude.ai/artifact/8G5z3LRD13TfUpxQJufMaR (round 1, 2026-10-21; passed gate A; seven decisions, the first follows B4's decision 1)
- Layout file: `scratch/phases/B1/layout.json`
- Contracts written (hotkeys, shared rows, shared files): yes, `scratch/phases/B1/contracts.md`
- Worktrees (several screens at once): main tree for the design; the build tree depends on the separate-mod question (B4's decision 1)
- Bindings: `window-bindings-all.md`, section `countrydivisiondesignerview` (line 6953 on 2026-10-21) and its rows; no regeneration needed.

## Inventory

- Vanilla reference: `reference/vanilla/division_designer.jpg` and `-panel.png` exist (vanilla's window, not RBM's).
- Where each window sits and the `expect` widgets: centred, no `at` needed; `expect` `close_button` and `reset_button` (scene `division_designer`).

## Proposal

<!-- generated: proposal (tools/phase_notes.py; edit the handoff file, not this) -->
RBM's designer becomes the ship designer's sibling: steel cards on a near-black window, 1260x715, centred. The template header (icon, name, name list, role, Equipment, priority) is one card; the composition is one card with a head band, the four composition values in a strip and the tree with its slots below; the stats are three banded tables of 12 rows of 24 px, each its own card with the table name in the head band; terrain adjusters and the 3D model share a card; Reset, Duplicate, experience, cost and Save sit in one bottom bar.

The template icon picker, which the playset fills with **2712 icons** (RBM's 1080, NATO Counters Expanded's 1632), opens over the whole window body with **14 columns of 84 px**: 151 icons at once instead of RBM's 82, 194 rows instead of 339. The subunit picker opens the same way with three columns of 400 px entries whose names get 300 px: every one of the playset's 214 land subunit names fits, where RBM's 160 px cut 86 of them. Every RBM widget and sprite is kept at its size; RBM's own bitmaps are replaced by vanilla-made steel and a piece of vanilla's background (the composition tree), so the build carries nothing of RBM's. Verdict: rework; effort: M: the layout applies to RBM's file with tools/apply_layout.py (dry run on a scratch copy: 0 differences), plus three textures (the tree piece, two pop-up steel backgrounds), seven block lines by hand, the baseline taken from RBM's window, and the scene's crop grown to the new window.

What vanilla does badly: **Vanilla** (the capture): 1200x720, stats in 16 px typewriter on paper in three columns of 172 px with 20 px rows; terrain adjusters 3 a row; the icon picker 7 columns of 84 px over the left half (70 icons at once); the subunit picker 2 columns of 250 px entries whose names get 160 px.

**Current, RBM's GFX Overhaul** (its divisiondesignerview.gui, the only file of the playset that defines the window; rendered with the playset's sprites, no in-game capture yet): the same 1200x720 with the panels painted into one bitmap (divisiondesignerbg.dds); stats white hoi_16mbs on flat dark, the heads in standard_22 on blue, red and yellow bars baked into the bitmap; 20 px rows, no bands, "Trickleback & Wasted Manpower" cut at 130 px. The icon picker is 8 columns of 76 px in 637x556 (82 icons at once, icons touching) for 2712 icons: 339 rows to scroll. The template name editbox is 294 px inside a 220 px dropdown, its arrow pushed outside the field (x 100 from the right edge). The subunit picker keeps vanilla's 2 x 250 px entries, so Extended Units Light's and the game's long names ("Medium Tank Command Company" 221 px, "Self-Propelled Super-Heavy Artillery" 241 px) are cut. Cost and resources stand in two separate boxes of the bottom strip. No hotkey but ESCAPE and RETURN.

**Window.** 1260x715, centred (RBM's orientation CENTER, origo center, position 0,0; screen 650-1910 x 362-1077), on GFX_1440p_steel_ground in place of RBM's divisiondesignerbg.dds. Steel title strip (2,2) 1256x46 with division_title and hq_title hoi_36header at (18,8), left-aligned, maxWidth 600; close_button (RBM's GFX_closebutton_rbm 34x34) at (1220,8), written UPPER_LEFT (RBM: UPPER_RIGHT at -40, the same place). Cards 6 apart: left column x 6, 664 wide; right column x 676, 578 wide; bottom bar y 657.

**Template card (6,54) 664x128.** Row 1: icon inset (14,62) 100x56 with div_templ_symbol_button (26,69), division_priority_icon (96,66), colonial flag and frame (21,93)/(22,86), hq_badge (88,92); division_template_icon (124,66); name field inset (150,62) 368x32 with `divisions` (156,63) 356x30, its editbox `name` (25,5) 300x22 (RBM 294x20 in a 220 dropdown), expand_button (-9,5) inside the field; equipment_warning (516,67); division_equipment_btn (538,61) 123x34. Row 2: niche_icon_bg (28,124) with niche_button (37,128) and niche_icon_disabled (36,149); name list inset (150,136) 368x32 with division_names (168,137) 338x30, `name` maxWidth 290 fixed (RBM 185); priority_button_1-3 at (552,134), 36 apart. The template list opens 360x420 with rows of 338x50 (designer_division_entry, `name` maxWidth 278 fixed, RBM 138); the name list opens 360x300 with rows of 330x30 (`name` 310, RBM 170). The role picker (niche_icon_selector) opens at (88,124). hq_view's copies stand at the same places.

**Composition card (6,188) 664x463.** Head band 27: composition_icon (16,191), division_composition_label hoi_18mbs (46,192) maxWidth 300; can_paradrop_icon (604,193) and special_forces_icon (632,191) at the right of the head (RBM: beside the name list). A near-black strip (14,221) 648x36 holds hardness_stat, org_stat, strength_stat and speed_stat at x 22, 182, 342, 502, y 227 (RBM's insides kept). The tree plate (22,263) 632x378, a piece of vanilla's background with the lines, the wings and the combat width ring, carries `subunits` at (6,205) and combat_width_view at (296,265) (RBM: 0,170 and 290,230): the 5 x 5 regiment slots, the support column and the regimental support row stand where the code puts them, on the tree. HQ templates: subunits_hq at (6,205) and the HQ overlays moved by the same (+6, +35); hq_header_background on the template card (8,56).

**Stats: three table cards (676,54).** Base Stats (676,54) 184x327, Combat Stats (866,54) 184x327, Equipment Cost (1056,54) 198x327, each a steel card whose 27 px head band holds the vanilla label (base_stats_label and the others) in hoi_18mbs, left at card x 8 (RBM: standard_22 centred on painted colour bars). `info` stands at (676,54); base_stats (8,31) 176x288, combat_stats (198,31) 176x288, equipment_stats (388,31) 190x288; each stats_grid at x 5 with slotsize 155x24 (RBM 20): 12 rows, every second one banded (fixed plates at the slot pitch). Rows are RBM's designer_stat_entry unchanged (hoi_16mbs, label 130 fixed, value right-aligned to 164). Base holds its 12 rows and Combat its 11 without scrolling; Equipment Cost shows 4 rows and 8 equipment types before its scrollbar (190 wide so the bar clears the values).

**Terrain and 3D card (676,387) 578x264.** adjuster_stats at (688,399) (info-relative 12,345), 296x240, RBM's grid of 4 columns of 69x70 unchanged: 12 terrains without scrolling. toggle_model_selector_button and select_model at (1006,399), RBM's 240x240 on a near-black inset (1002,395) 248x248. RBM's 3D model selector (div_template_select_model, 531x605 with its bitmap at x -16) opens at (692,54) over the right column.

**Bottom bar (6,657) 1248x52.** reset_button (18,665), duplicate_button (150,665), experience (290,672) maxWidth 100, production_resources (420,672) maxWidth 200, production_value (630,672) maxWidth 380 ("Estimated Production Cost: 553 to 617" is 312 px), save_button (1021,665) 221x34; save_and_deploy_button (788,665) and the HQ deploy time and cost (420,668)/(510,668) for HQ templates. All were LOWER_LEFT in RBM and are written UPPER_LEFT at window coordinates. Buttons keep their sprites and RBM's hoi_18mbs.

**Template icon picker.** div_templ_custom_icon_view over the window body (6,54) 1248x597 on a steel background of its size (GFX_1440p_dd_picker; RBM: GFX_divisiondesigner_popup_bg 637x560): back (16,10), default (147,10); symbols_grid (16,56) 1176 wide, slotsize 84x50, max_slots_horizontal 14 (RBM 8 x 76); div_templ_custom_icon_button 84x50 with the 76x42 icon at x 4 (vanilla's width; RBM 76). 14 x 10.8 rows = 151 icons at once (RBM 82, vanilla 70); the playset's 2712 icons in 194 rows (RBM 339). RBM's scrollbar div_templ_custom_icon_view_slider and its wheel step of one row (50) stay.

**Subunit picker.** designerregimentswindow over the window body (6,54) 1248x597 on a steel background (GFX_1440p_dd_subunits; RBM: GFX_tiled_window_1b_border 660x580 over the left half): regiment_desc_title (18,12) maxWidth 600, cancel_button (1113,8) with RETURN; designer_regiments_grid (16,52) 1216x536, slotsize 404x69, max_slots_horizontal 3 (RBM 2 x 256): 7.8 rows, 23 entries at once (RBM 13). designer_subunit_entry and designer_subunit_category_entry 400x66 (RBM 250): `name` and `cost` hoi_18mbs maxWidth 300 fixed (RBM 160, not fixed); special_forces_icon (366,10), can_paradrop_icon (366,35). The playset's widest land subunit name is 267 px ("Northern Territory Reconnaissance Unit"); 86 of 214 are wider than RBM's 160.

**Equipment and other pop-ups.** division_equipment_view (RBM's 642x566 on its own bitmap) opens at (20,60) over the left column; its rows stay. niche_icon_selector, the two dropdown lists and the 3D selector as above.

**Hotkeys.** save_button ctrl+s, reset_button ctrl+z, duplicate_button ctrl+d (B4's keys for the same actions), division_equipment_btn ctrl+e, div_templ_symbol_button ctrl+i (the icon picker). close_button ESCAPE and cancel_button RETURN stay. Free in vanilla interface/ and in the 1440p mod; in the playset ctrl+s and ctrl+d are also bound by the Toolpack's tool windows, which are scripted GUIs shown only while a tool is open (decision 4).

| Part | Vanilla | RBM (current) | Proposed |
|---|---|---|---|
| Window | 1200x720, centred, painted bitmap | 1200x720, flat dark bitmap (divisiondesignerbg.dds) | 1260x715 centred, steel cards on near-black |
| Template name | editbox 185 in a 220 dropdown | editbox 294, arrow outside the 220 field | editbox 300 in a 368 field, arrow inside; template list rows 338 (name 278) |
| Name list | name 185 | name 185 | name 290 fixed; list rows 330 (name 310) |
| Composition | values strip, tree in the bitmap | the same, flat | head band, values strip, vanilla tree plate; slots where the code puts them |
| Stats | 3 x 172, typewriter on paper, 20 px rows | 3 x 172/198, hoi_16mbs white, standard_22 heads on colour bars, 20 px rows | 3 table cards (184/184/198), head bands hoi_18mbs, 12 banded rows of 24 |
| Terrain | 3 a row, 77x72 | 4 a row, 69x70, 273x240 | RBM's 4 a row, 296x240, in a card with the 3D model |
| 3D model | 249x249 | 240x240 | 240x240 on an inset |
| Cost | bottom strip, right | two boxes of the bottom strip | one bottom bar: resources 200, cost 380, Save |
| Icon picker | 7 x 84 in 639x555: 70 at once | 8 x 76 in 637x556: 82 at once, 339 rows for 2712 | 14 x 84 in 1248x597: 151 at once, 194 rows |
| Subunit picker | 2 x 256 in 660x580, names 160 | the same, names 160 (86 of 214 cut) | 3 x 404 in 1248x597, names 300 fixed (none cut), 23 at once |
| Hotkeys | ESCAPE, RETURN | ESCAPE, RETURN | + ctrl+s Save, ctrl+z Reset, ctrl+d Duplicate, ctrl+e Equipment, ctrl+i Icon |

Additions, each with the row of "What a redesign can add" or the register id that allows it:

- Steel cards, title strip, bottom bar, insets (fields, values strip, 3D frame) as `mod1440_dd_*` plates behind the widgets (Cards, panels, grouped headers (plates behind widgets that keep their parents, A9's method) [GUW-030])
- Banded stat rows: a fixed band plate on every second 24 px row behind each stats_grid (Cards, panels, grouped headers; Design Language, Tables (bands of a code-filled grid are fixed plates at its slot pitch) [GUL-037])
- The composition tree as a plate (GFX_1440p_dd_tree, a 632x378 piece of vanilla's background) and the composition block moved with it (Move, resize and regroup panels; larger art from vanilla assets (Give each existing value its own place))
- Stats tables 12 rows of 24 px, terrain and 3D in one card, cost in the bottom bar (Move, resize and regroup panels)
- Icon picker of 14 columns of 84 over the window body (Move, resize and regroup panels; the picker computes its slots from max_slots_horizontal [GUL-037], entry as wide as the slot [GUL-006])
- Subunit picker of 3 columns of 400 px entries with names to 300 px (Give each existing value its own place: full names; columns by max_slots_horizontal as vanilla's 2 [GUL-037])
- Wider template name field and wider template and name list rows (Give each existing value its own place: full names)
- ctrl+s on save_button (Hotkeys, including key chords)
- ctrl+z on reset_button (Hotkeys, including key chords)
- ctrl+d on duplicate_button (Hotkeys, including key chords)
- ctrl+e on division_equipment_btn (non_hq_view and hq_view) (Hotkeys, including key chords [GUW-007 for the pair never shown together])
- ctrl+i on div_templ_symbol_button (non_hq_view and hq_view) (Hotkeys, including key chords [GUW-007 for the pair never shown together])

Open until the game shows it:

- The picker takes 14 columns from max_slots_horizontal (a code read, never game-checked) and scrolls to NATO Counters Expanded's last icon (2711) on the patched executable; on an unpatched game it ends at 1023.
- designer_regiments_grid fills 3 columns from max_slots_horizontal = 3 (vanilla's 2 suggest the fill reads it).
- The stats grids lay rows 24 apart from slotsize, and the Equipment Cost container scrolls past 12 rows.
- The composition slots land on the tree plate's lines (same offset as RBM's and vanilla's bitmaps, moved by +6, +35).
- The bottom widgets, now UPPER_LEFT at window coordinates, stand where drawn; the close button the same.
- The picker's Back and Default keep RBM's size 504x23 and still draw at their sprites' size.
- The template list (opens upward in RBM, position y -300) and the name list open inside the window at their new widths.
- ctrl+ hotkeys while the template name editbox has focus, and with the Toolpack's windows closed.
- An HQ template (subunits_hq, the HQ overlays, Save and Deploy) is moved but not drawn here: no capture of that state.
- RBM's 3D model selector and equipment view at their new places over the cards; no new line in error.log.

Figure groups of the design page: main, picker, stats, subunits.
<!-- end generated: proposal -->

## Decisions

- 2026-10-21: the user reopened the division designer, RBM compatible, starting from RBM's version. Phase opened as B1.

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
- [ ] Scene file final (`tools/scenes/division_designer.json`)
- [ ] Finished screen stored: `tools/Invoke-GameCheck.ps1 division_designer -SaveReference` (`reference/mod/`)
