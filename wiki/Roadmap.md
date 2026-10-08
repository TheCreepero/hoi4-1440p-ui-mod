# Roadmap

The mod is built one screen at a time. Each phase reworks one screen for 2560x1440 and can be tested and released on its own. The rules every phase follows are in [Design Rules](Design-Rules.md).

## Decisions

- **Baseline:** vanilla 1.19 first. Compatibility patches for other mods come later (see "Compatibility checkpoints").
- **Design target:** 2560x1440 at 100% UI scale. The mod does not fit smaller resolutions or a higher UI scale.
- **Depth:** full rework per screen: larger windows, repositioned panels, larger fonts, larger backgrounds.
- **Art:** no AI-generated images. Backgrounds are built from vanilla game assets.
- **Priority:** military lists, then designers, then the backlog.

## Status

Status values: Not started, In progress, Done.

| Phase | Scope | Status |
|---|---|---|
| 0 | Foundation: scaffold fixes, tools, generic tests, docs | Done |
| 1 | Pilot screen (A1) and the single-window override test | Not started |

## Phase 1: pilot

Screen A1, air wings and airbases. Its backgrounds are tiled, popular overhaul mods leave it alone, and it contains a 74-line popup that suits the override test.

1. **Override test** on `quick_wing_deployment_selection_window` (`airselectionview.gui`, 500x515).
   - Put a visibly changed copy in a separate small file. Check in game that it wins and that `error.log` stays clean.
   - Try file names and folders that sort before and after the vanilla file.
   - Repeat with a mod that replaces the whole vanilla file, to learn how load order interacts.
   - Outcome: the override method and file naming rule, recorded in [Design Rules](Design-Rules.md).
2. **Rework the screen:** `air_selection_view`, `unassigned_airwings_view`, the selection item rows and the quick deploy popup.
3. **Lock the shared rules** that are still marked provisional in [Design Rules](Design-Rules.md): font mapping, row heights, maximum window sizes.

## Milestone A: military lists

Phases are independent after Phase 1 and can be reordered.

| # | Screen | Vanilla file and main windows | Vanilla size | Background | Also changed by | Status |
|---|---|---|---|---|---|---|
| A1 | Air wings and airbases (pilot) | `airselectionview.gui`: `air_selection_view`, `unassigned_airwings_view` | 502x430, 582x430 | tiled | none found | Not started |
| A2 | Selected army: badge and division list | `unitview.gui`: `armies_view`, `army_badge_view`, `army_division_list_view`, `expeditionary_force_container` | list 422x430 | tiled, small bitmaps | RBM's GFX Overhaul | Not started |
| A3 | Division and ship details | `unitview.gui`: `army_division_stats_view`, `ship_stats_window` | 856x522, 557x407 | bitmap | RBM's GFX Overhaul | Not started |
| A4 | Navy and fleet view | `naviesview.gui`: `naviesview_window`, fleet and task force rows, composition editor, base picker | 500 wide, 86% high | tiled, bitmap rows | RBM's GFX Overhaul, Vanilla Navy Rework | Not started |
| A5 | Recruit and deploy | `countrydeploymentview.gui`: `countrydeploymentview`, `templatedeploymentwindow` | 550 and 375 wide, full height | tiled | RBM's GFX Overhaul | Not started |
| A6 | Army overview tab | `countryarmyview.gui`: `countryarmyview` | 550 wide, full height | tiled | none found | Not started |
| A7 | Air wing reorganisation | `airwingreorganization.gui`: `air_wing_reorganization` | 1000x515 | tiled | none found | Not started |
| A8 | Theatre bar at the bottom | `theatreselector.gui` | 760 wide | tiled | RBM's GFX Overhaul | Not started |

- A3 is the first screen with a bitmap background, so the background options in [Design Rules](Design-Rules.md) are first tried there.
- A8 is the riskiest: much of its layout is positioned by the engine. Do it last, or drop it if little can move.

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

## Compatibility checkpoints

After Milestone A and again after Milestone B, decide whether to build a patch for RBM's GFX Overhaul (and later Road to 56) covering the screens finished so far. The Phase 1 override test shows how much of such a patch is needed.

## Risks

- **Single-window override fails or depends on load order.** The fallback is full copies of the vanilla files, which means more merge work after each game update.
- **Engine-positioned widgets.** Some layouts (regiment grid, hull slots, combat width bars) cannot be moved from `.gui` files. The inventory step of each phase finds them before a layout is promised.
- **Bitmap backgrounds with painted-in frames.** If no background option gives a clean result, the window keeps its vanilla size and only its lists and fonts are reworked.
- **Game updates.** A new game version can change windows the mod overrides. Re-running `tools/Export-VanillaBaseline.ps1` shows which ones.
