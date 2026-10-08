# Roadmap

The mod is built one screen at a time. Each phase reworks one screen for 2560x1440 and can be tested and released on its own. The rules every phase follows are in [Design Rules](Design-Rules.md).

## Decisions

- **Baseline:** vanilla 1.19 only, for now. Every screen is built and checked in a playset that contains just this mod. Behaviour next to other mods is not tested and not worked on until a compatibility checkpoint (see "Compatibility checkpoints").
- **Design target:** 2560x1440 at 100% UI scale. The mod does not fit smaller resolutions or a higher UI scale.
- **Depth:** a redesign per screen, not only an enlargement. Each screen is re-laid out around what the player wants to see at once: regrouped panels, a place of its own for every value the screen already has, larger fonts and backgrounds, fixed captions, and hotkeys for buttons that have none. New live values and new working buttons are not possible; the limits are in [Design Rules](Design-Rules.md), "What a redesign can add".
- **Checksum:** untouched. Scripted GUIs, the game's way to add new values and buttons, live in `common/` and are not used.
- **Art:** no AI-generated images. Backgrounds are built from vanilla game assets.
- **Priority:** military lists, then designers, then the backlog.

## Status

Status values: Not started, In progress, Done. Each phase keeps its inventory, decisions and game-check log in `wiki/phases/` ([A1](phases/A1-air-selection.md), [A2](phases/A2-army-selection.md); template: [Phase Template](Phase-Template.md)); what the launches taught about the engine is in [Engine Facts](Engine-Facts.md).

| Phase | Scope | Status |
|---|---|---|
| 0 | Foundation: scaffold fixes, tools, generic tests, docs | Done |
| 1 | Pilot screen (A1) and the single-window override test | Done |

## Phase 1: pilot

Screen A1, air wings and airbases. Its backgrounds are tiled, popular overhaul mods leave it alone, and it contains a 74-line popup that suits the override test.

1. **Override test.** Done. A window redefined in a separate file takes effect when that file sorts after the vanilla file, so each screen ships as `interface/zz_1440p_<screen>.gui`. The evidence and the two cases still untested are in [Design Rules](Design-Rules.md).
   - Deferred to the first compatibility checkpoint: the same test against a mod that replaces the whole vanilla file.
2. **Rework the screen.** Done (`interface/zz_1440p_air_selection.gui`). The selection list holds 20 rows instead of 9, rows are 671 wide instead of 548 so wing names fit, texts are one font size larger, the two toolbars and the list form one block without gaps, and the quick deploy popup is taller. It took three game checks: the first build left the real list frame (`unassigned_airwings_view`) at vanilla size, the second left gaps between the panels.
   - Not seen in game: gun emplacement and rocket rows. They were changed the same way as the wing rows but do not appear in a 1936 start.
3. **Lock the shared rules.** Done for the override method, the font steps used in A1 and the height of docked panels. The size limit for centred windows stays provisional until B1. What A1 taught about the engine is in [Design Rules](Design-Rules.md).

## Milestone A: military lists

Phases are independent after Phase 1 and can be reordered.

| # | Screen | Vanilla file and main windows | Vanilla size | Background | Also changed by | Status |
|---|---|---|---|---|---|---|
| A1 | Air wings and airbases (pilot) | `airselectionview.gui`: `air_selection_view`, `unassigned_airwings_view` | 502x430, 582x430 | tiled panel, bitmap rows | none found | Done |
| A2 | Selected army: badge and division list | `unitview.gui`: `armies_view`, `army_badge_view`, `army_division_list_view`, `army_division_view` | list 422x430 | tiled, small bitmaps | RBM's GFX Overhaul | Done |
| A3 | Division and ship details | `unitview.gui`: `army_division_stats_view`, `ship_stats_window` | 856x522, 557x407 | bitmap | RBM's GFX Overhaul | Not started |
| A4 | Navy and fleet view | `naviesview.gui`: `naviesview_window`, fleet and task force rows, composition editor, base picker | 500 wide, 86% high | tiled, bitmap rows | RBM's GFX Overhaul, Vanilla Navy Rework | Not started |
| A5 | Recruit and deploy | `countrydeploymentview.gui`: `countrydeploymentview`, `templatedeploymentwindow` | 550 and 375 wide, full height | tiled | RBM's GFX Overhaul | Not started |
| A6 | Army overview tab | `countryarmyview.gui`: `countryarmyview` | 550 wide, full height | tiled | none found | Not started |
| A7 | Air wing reorganisation | `airwingreorganization.gui`: `air_wing_reorganization` | 1000x515 | tiled | none found | Not started |
| A8 | Theatre bar at the bottom | `theatreselector.gui` | 760 wide | tiled | RBM's GFX Overhaul | Not started |

- A1 was first built 768 wide, before A2 showed how width is judged. It was narrowed to 705 afterwards. That is as narrow as it goes while the three blocks stay aligned: the mission bar is 703 wide at vanilla spacing with 15 missions. Wing and airbase names still fit; the status line "On Mission in <region>" is cut for the nine regions with the longest names.
  - The narrowing passed its game check. The same check found that an air group had always broken the layout: with a group selected the rows sit in a second list (`air_groups_view`) that was still 580 wide. That list and the air group badge are now 705 and 704 wide (`interface/zz_1440p_air_group.gui`). Confirmed by the tester in game, without a screenshot.
- A2 already put `army_division_stats_view` (the A3 window) into its override file, with only the template dropdown widened. A3 continues in that file.
- A3 is the first screen with a bitmap background, so the background options in [Design Rules](Design-Rules.md) are first tried there.
- A8 is the riskiest: much of its layout is positioned by the engine. Do it last, or drop it if little can move.

### A2: selected army

1. **Division list.** Done (`interface/zz_1440p_army_selection.gui`).
   - The list is 670 wide instead of 422 and reads as a table: organisation and strength as two lying bars, warnings in a block of their own, names in full in a larger font, captions on four sort buttons, and the toolbar's right-hand buttons at the right edge.
   - The change-template dropdown shows 12 templates instead of 6, with names on one line. The same entry fills the HQ deploy dropdown and the dropdown in the division details window, so those were widened with it.
   - `shift+u` unassigns and `shift+c` consolidates.
   - It took four game checks. The bars column (90 px) and then the warnings column (96 px) were judged too wide, and the template dropdown too narrow.
   - Not seen in game: combat icons; the low supply, attrition and exile markers; the HQ deploy bar; `shift+c`; and the raised height limit of the list (760). With two armies selected the game shows badges only, so that limit was not in play.
2. **Army badge.** Done. The badge goes from 437 to 685 wide so it covers the list frame, which runs behind it. Its painted areas (name field, commander box, stats box, right area) are each widened, and the contents follow them.
   - It took one game check. The layout was agreed on a mock-up composed from a screenshot before anything was built.
   - Not seen in game: commander traits and the preferred tactic icon in the right area, and the scrollbar of a long badge stack. The army group badge was checked by the tester without a screenshot.

## Milestone B: designers

| # | Screen | Vanilla file | Vanilla size | Background | Also changed by | Status |
|---|---|---|---|---|---|---|
| B1 | Division designer | `divisiondesignerview.gui`: `countrydivisiondesignerview` | 1200x720 | bitmap | RBM's GFX Overhaul | Not started |
| B2 | Tank designer | `tank_designer_view.gui` | 1091x542 | bitmap | RBM's GFX Overhaul | Not started |
| B3 | Plane designer | `plane_designer_view.gui` | 1091x542 | bitmap | RBM's GFX Overhaul | Not started |
| B4 | Ship designer and refit | `equipmentdesignerview.gui`, plus `ship_refit_equipment_view` in `naviesview.gui` | 1097x542 | bitmap | RBM's GFX Overhaul, Vanilla Navy Rework | Not started |

- B1 takes over the namelist dropdown from the Larger Selector addon (popup 340x440, slot width 304, scroll factor 60) and replaces that addon.
- B2 and B3 share one structure, so B3 mostly reuses the B2 layout.
- In B2 to B4 the hull and slot area keeps its vanilla size. Module slot positions are defined per hull in `interface/equipmentdesigner/` (253 tank files, 8 plane files, 6 ship files).

## Milestone C: backlog (not scheduled)

- **Selection popups:** general and admiral selection (`unitleaderwindow.gui`, 550x590, bitmap), advisor and law selection (`political_ideas_window`, 500x590, tiled).
- **Info windows:** events, technology and focus detail popups (550x550), land and naval combat, trade offer, war overview.
- **Side panels** (550 wide, already full height): production, construction, logistics, decisions, politics, diplomacy.
- **Newer screens in subfolders:** military industrial organisations, international market, special projects, factions.
- **Front end:** game setup and country selection.
- **Companion mod with scripted GUIs:** country-level panels, for example extra numbers in the top bar or the production tab. It would be a separate, optional mod, because it changes the checksum and so loses Ironman achievements. Not decided.

## Compatibility checkpoints

Until a checkpoint, nothing is tested or built for use next to other mods. After Milestone A and again after Milestone B, decide whether to build a patch for RBM's GFX Overhaul (and later Road to 56) covering the screens finished so far.

The first checkpoint starts with the test deferred from Phase 1: how a single-window override behaves next to a mod that replaces the whole vanilla file. Its result shows how much of a patch is needed.

## Risks

- **Single-window override next to other mods.** The override works against vanilla. How it behaves next to a mod that replaces the whole vanilla file is still untested.
- **Engine-positioned widgets.** Some layouts (regiment grid, hull slots, combat width bars) cannot be moved from `.gui` files. The inventory step of each phase finds them before a layout is promised.
- **A redesign that promises more than the engine gives.** The game fills only the widgets its code asks for. `tools/Show-CodeNames.ps1` lists them during the inventory, before a layout is proposed.
- **Bitmap backgrounds with painted-in frames.** If no background option gives a clean result, the window keeps its vanilla size and only its lists and fonts are reworked.
- **Game updates.** A new game version can change windows the mod overrides. Re-running `tools/Export-VanillaBaseline.ps1` shows which ones.
