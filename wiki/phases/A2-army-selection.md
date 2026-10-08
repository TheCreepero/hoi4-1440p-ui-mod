# Phase A2: selected army (badge and division list)

Reconstructed from the Roadmap after the phase closed. Status: Done.

## Scope

- Vanilla file and windows: `unitview.gui`: `army_badge_view`, `army_division_list_view`, `army_division_view`, `unit_template_entry`; `army_division_stats_view` only for its template dropdown (A3 continues there).
- What the vanilla screen crams or hides: organisation and strength as two 6 px upright bars, warnings stacked on the template icon, names cut at 175 px, sort buttons without captions, a template dropdown with 6 rows and wrapped names.

## Inventory

- `tools/Show-CodeNames.ps1 unitview.gui army_division_view`: no unused widgets; `entry` and `army_division_list` unexplained (Engine Facts W4).
- Lists and their rows: `divisions_window` (a container the code fills) holds `army_division_view` 33 px apart; `divisions_grid` and `templates_grid` are filled with `unit_template_entry`. In `tools/gui-links.json` and the scene.
- Bitmap backgrounds: row (`unit_entry_bg.dds`, periodic and spread), footer plate (mirror), army and army group badges (mirror per painted area).

## Proposal

The list is 670 wide and reads as a table: two lying bars, a warnings block, full names in `hoi_20b`, captions on four sort buttons, right-hand buttons at the right edge. The template dropdown shows 12 templates on one line each. The badge goes to 685 wide so it covers the list frame behind it. `shift+u` unassigns, `shift+c` consolidates.

## Decisions

- Bars column 90 px and warnings column 96 px sent back as too wide: a column gets the width its content needs, saved width goes back to the map.
- Template dropdown sent back as too narrow.
- Badge layout agreed on a mock-up composed from the screenshot; one check.

## Game checks

| # | Date | Build | Checked | Result | Screenshot | Taught |
|---|---|---|---|---|---|---|
| 1 | 2026-10-08 | list, build 1 | list | bars column too wide | - | width is judged first (Design Rules) |
| 2 | 2026-10-08 | build 2 | list | warnings column too wide | - | |
| 3 | 2026-10-08 | build 3 | list, dropdown | dropdown too narrow | - | one entry fills three lists (Design Rules, Lists) |
| 4 | 2026-10-08 | build 4 | list, dropdown | accepted | `hoi4_8.png` | rows at y 242 + 33n, frame content starts at 181 (S3, S7) |
| 5 | 2026-10-08 | badge | badge | accepted | - | G6, S13 |
| 6 | 2026-10-08 | working tree | Army 1 with all 30 divisions and the template dropdown, unattended run, plus the vanilla reference | matches the accepted layout; with one army the list runs to y 1230 without a scrollbar, so the 760 limit is not what ends it | `scratch/checks/army_selection-*-crop.png` | H3: no reload; H12: the clicks that bring the screen up |

Not seen in game: combat icons; low supply, attrition and exile markers; the HQ deploy bar; `shift+c`; the raised list height (760); commander traits and the preferred tactic icon; the scrollbar of a long badge stack.

## Close

- [x] Roadmap, README, Workshop description, `version`
- [x] Scene file `tools/scenes/army_selection.json` (positions measured on `hoi4_8.png`)
