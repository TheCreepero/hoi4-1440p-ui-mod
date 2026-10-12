# Roadmap

The mod is built one screen at a time. Each phase reworks one screen for 2560x1440 and can be tested and released on its own. The rules every phase follows are in [Design Rules](Design-Rules.md).

## Decisions

- **Baseline:** vanilla 1.19 only, for now. Every screen is built and checked in a playset that contains just this mod. Behaviour next to other mods is not tested and not worked on until a compatibility checkpoint (see "Compatibility checkpoints").
- **Design target:** 2560x1440 at 100% UI scale. The mod does not fit smaller resolutions or a higher UI scale.
- **Depth:** a redesign per screen, not only an enlargement. Each screen is re-laid out around what the player wants to see at once: regrouped panels, a place of its own for every value the screen already has, larger fonts and backgrounds, fixed captions, and hotkeys for buttons that have none. New live values and new working buttons are not possible in a vanilla window; the limits are in [Design Rules](Design-Rules.md), "What a redesign can add". The manager pages of Milestone D add both, as scripted GUIs beside the vanilla panels.
- **Checksum:** changed since phase D2. The reworked screens (Milestones A and B) are interface and texture files, outside the checksum. The manager pages of Milestone D are scripted GUIs, the game's way to add new values and buttons; their script lives in `common/` and changes the checksum, so the mod no longer works with Ironman and achievements, and in multiplayer every player needs it. The user decided on 2026-10-12 that this is acceptable. Only four folders under `common/` are used, and the tests hold that line.
- **Art:** no AI-generated images. Backgrounds are built from vanilla game assets.
- **Priority:** military lists, then designers, then the backlog.

## Status

Status values: Not started, In progress, Done. Each phase keeps its inventory, decisions and game-check log in `wiki/phases/` ([A1](phases/A1-air-selection.md), [A2](phases/A2-army-selection.md), [A3](phases/A3-unit-details.md), [A4](phases/A4-fleet.md), [A5](phases/A5-recruit-deploy.md), [D0](phases/D0-manager-feasibility.md), [D2](phases/D2-army-readiness.md), [D3](phases/D3-states.md), [D4 and D5](phases/D4-national-figures.md); template: [Phase Template](Phase-Template.md)); what the launches taught about the engine is in [Engine Facts](Engine-Facts.md).

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
| A3 | Unit details: division, ship, air wing, railway gun | `unitview.gui`: `army_division_stats_view`, `ship_stats_window`; `airwingdetails.gui`: `air_wing_stats_window`; `railway_gun.gui`: `railway_gun_stats_view` | 856x497, 856x409 | bitmap | RBM's GFX Overhaul | Done, awaiting the tester's judgement (railway gun render-only) |
| A4 | Navy and fleet view | `naviesview.gui`: `naviesview_window`, fleet and task force rows, composition editor, base picker | 500 wide, 86% high | bitmap cards and rows | RBM's GFX Overhaul, Vanilla Navy Rework | Done |
| A5 | Recruit and deploy | `countrydeploymentview.gui`: `countrydeploymentview`, `templatedeploymentwindow` | 550 and 375 wide, full height | tiled panels, bitmap rows | RBM's GFX Overhaul | Done |
| A6 | Army overview tab | `countryarmyview.gui`: `countryarmyview` | 550 wide, full height | tiled | none found | Not started |
| A7 | Air wing reorganisation | `airwingreorganization.gui`: `air_wing_reorganization` | 1000x515 | tiled | none found | Not started |
| A8 | Theatre bar at the bottom | `theatreselector.gui` | 760 wide | tiled | RBM's GFX Overhaul | Not started |

- A1 was first built 768 wide, before A2 showed how width is judged. It was narrowed to 705 afterwards. That is as narrow as it goes while the three blocks stay aligned: the mission bar is 703 wide at vanilla spacing with 15 missions. Wing and airbase names still fit; the status line "On Mission in <region>" is cut for the nine regions with the longest names.
  - The narrowing passed its game check. The same check found that an air group had always broken the layout: with a group selected the rows sit in a second list (`air_groups_view`) that was still 580 wide. That list and the air group badge are now 705 and 704 wide (`interface/zz_1440p_air_group.gui`). Confirmed by the tester in game, without a screenshot.
- A3 grew from two windows to four: the stat row is shared by the division, ship, air wing and railway gun details windows. They are in `interface/zz_1440p_unit_details.gui`; the division window moved there from the A2 file. Notes: [A3](phases/A3-unit-details.md).
  - First build: stats in a 22 px font on rows 28 px apart, in frames 1180 wide; the division window opens beside the army panel.
  - Redo (2026-10-11): the Stats tab of all four windows is dark cards of stat tiles (Base, Combat, Misc). The ship, air wing and railway gun frames grew from 473 to 584 px high. Checked in game for the division, ship, carrier and air wing, with tab hotkeys (`shift+a`, `shift+h`, `shift+t`); not for the railway gun (no recipe, Engine Facts H29). History and Template tabs, header and officer card keep the first build. `reference/mod/` refreshed.
  - Not done: showing the ship window's side panel only when it has content. Open for A4.
  - Not seen in game: railway gun details, a ship captain, history entries, an HQ division.
- A4 is done in two steps. Notes: [A4](phases/A4-fleet.md).
  - Step 1, built (`interface/zz_1440p_fleet.gui`): the panel is 740 wide instead of 492. A ship takes one line of 35 px with name and class side by side (about 26 ships on the screen instead of 22, the class name whole), task force cards are 86 px high instead of 125 with the composition counters in the mission box (the 12 task forces of the British Home Command fit on the screen, 8 did), fleet and task force names have 360 px, the home base name is whole, the toolbar is in four groups with five new hotkeys (`shift+n` and `shift+r` confirmed in game). The home base picker and the ship details window open beside the wider panel. It took three game checks: the first showed the task force tray mostly empty and a long class name still cut.
  - Step 2, built: the composition editor is 604 wide instead of 524 with class names in a larger font, the ship class picker shows all nine classes without scrolling (vanilla shows seven), the home base picker is 455 wide instead of 375 with base names in a larger font, and "Select Ships to Transfer" lists a ship per line, 10 before it scrolls instead of 7. One game check, plus one without the mod to measure where vanilla puts the windows.
  - Not seen in game: several fleets selected, a commander with traits, a damaged ship with its repair and refit buttons, the refit window, three of the five hotkeys, the template list of the composition editor.
  - The A3 item "show the ship window's side panel only when it has content" is still open.
- A5 is done (`interface/zz_1440p_recruit_deploy.gui`); the tester judged it finished on 2026-10-12. Notes: [A5](phases/A5-recruit-deploy.md).
  - The left panel is 640 wide instead of 550: a division in training shows its whole name in a larger font, and its name list shows 14 names instead of 10. The template panel is 618 wide instead of 375 and lists one template per line of 48 px, 22 before it scrolls instead of 17; it ends above the army portraits of the bottom bar. `shift+f` opens the division designer. Two game checks with the mod, after one layout chosen from three.
  - The six priority rows keep their vanilla size: the code swaps their background per kind of row.
  - Not captured by the harness, tried by the tester and found working: a line ready to deploy, a card with a location, the foreign templates list, a list long enough to scroll.
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

## Milestone D: manager pages

The idea (user, 2026-10-12): a side panel such as Recruit & Deploy becomes a near full screen "manager" with new information and quality of life options, and narrows by itself when the map is needed, for example to pick a deploy location. The feasibility phase D0 was run on 2026-10-12 ([notes](phases/D0-manager-feasibility.md)). The table gives what it found.

| Part of the idea | Possible | How, and the limit |
|---|---|---|
| A panel that fills most of the screen | Yes, but with nothing to fill it | Sizes in the `.gui` file. The lists of Recruit & Deploy do not run in columns: `max_slots_horizontal = 2` on the template list failed in two forms (S29). |
| Narrowing by itself when the map is needed | No | A window has one size in its file, and no file can ask what the player is doing. The code leaves both panels as they are while a deploy location is picked (S30). |
| The map stays usable beside the panels | Yes | The two panels are separate windows and can stand apart: with the template panel at the right edge of the screen, a click on the map between them picked a deploy location (S30). |
| New information on the screen | Yes, with a scripted GUI | Attached to this tab (`parent_window_token = deployment_tab`) it showed values of the country that follow the game while it is paused: queued and available manpower, army experience, number of divisions, equipment in stock (X1, X2). It lives in `common/` and changes the checksum, which the user accepts. |
| Information per division in training or per template | No | Script sees the country, not a line of this list or a template: no array of either exists for a scripted list. |
| New working buttons | Yes, with a scripted GUI, but few are useful here | A scripted button runs its effect, also while the game is paused (X3). No effect queues a division, sets a priority or a deploy location; effects on templates lock them, cap them or change their units. |
| Folding the extra part away on a click | Yes, for the scripted panel | A scripted button set a variable; a text with a `_visible` trigger went away and a widget with an `x` property moved (X4). A vanilla window cannot be resized this way. |

So a manager is not a wider version of the vanilla panels: they have nothing more to show and cannot use the width. It is a scripted panel of the mod's own beside or over them, with values of the country and a fold button, and it gives the map back on a click, not by itself.

| # | Phase | Scope | Status |
|---|---|---|---|
| D0 | Feasibility | Four questions on Recruit & Deploy in one launch: columns in the template list (no), what the code does while a deploy location is picked (nothing), clicks on the map between the panels (they arrive), a scripted GUI on this tab (works). | Done |
| D1 | Recruit & Deploy as a wider arrangement of its vanilla lists | Templates in two or three columns beside the divisions in training. | Dropped: the lists stay one column (D0) |
| D2 | Army Readiness, docked to Recruit & Deploy | Opened with a probe of two launches that settled the open engine questions (rows X6 to X25 of [Engine Facts](Engine-Facts.md)). Then the foundation, paid once: the tool that writes every file of a page (`tools/build_managers.py`), the tests (`tests/ScriptedGuis.Tests.ps1`), the changed checksum rule, the renderer and the harness reading a scripted page. The page: manpower, the army's counts, a table of land equipment (stock, in the field, needed, a bar). [Notes](phases/D2-army-readiness.md) | Done, awaiting the tester's judgement |
| D3 | States, docked to Construction | One row per controlled state, sorted by any column, a click moves the camera there. The vanilla Construction window needs no override: it already lets a page stand beside it. [Notes](phases/D3-states.md) | Done, awaiting the tester's judgement |
| D4 | National Figures, opened from Politics | The country's summed modifiers (93, in six groups), factories, fuel, party popularity, resources. A window of its own: the vanilla Politics window would have to be overridden to dock a page. [Notes](phases/D4-national-figures.md) | Done, awaiting the tester's judgement |
| D5 | History, the second page of National Figures | Twelve figures written down on the first of each month and drawn as columns. The graph is checked with made-up months; the monthly recording has not been seen running, because no check runs time. [Notes](phases/D4-national-figures.md) | Done, awaiting the tester's judgement and a look after a month of play |
| D6 | Armies, on the Army Readiness page | One row per general with troops: divisions, battalions, fighting, planning, the worst equipped kind, divisions by kind. Built with D2. | Done, awaiting the tester's judgement |
| D7 | Top bar strip | Numbers the top bar hides in tooltips, in the 930 px that are free at 1440p. | Not started (the user: later) |

What each page shows, the rules they follow and how to work on them: [Scripted GUIs](Scripted-GUIs.md). What the user chose on 2026-10-12: all four managers and graphs over time, pages docked to their tab, values of the own country only, the top bar strip later.

- **Asked of the tester:** a few days and a month of game time with the mod. The date beside "Count again" on Army Readiness should then be the day's, and History should have a second column on 1 February. No check can show this: the user's autosave is monthly, and a check that let a month pass would overwrite it.
- **Not built, and why:** a table of other countries (own country only); anything per template, per training line or per production line (script has no list of them).
- A layout D0 showed to work and nobody has asked for: the template panel at the right edge of the screen, the divisions in training at the left, the map between them.

## Milestone C: backlog (not scheduled)

- **Selection popups:** general and admiral selection (`unitleaderwindow.gui`, 550x590, bitmap), advisor and law selection (`political_ideas_window`, 500x590, tiled).
- **Info windows:** events, technology and focus detail popups (550x550), land and naval combat, trade offer, war overview.
- **Side panels** (550 wide, already full height): production, construction, logistics, decisions, politics, diplomacy.
- **Newer screens in subfolders:** military industrial organisations, international market, special projects, factions.
- **Front end:** game setup and country selection.
- **Companion mod with scripted GUIs:** country-level panels, for example extra numbers in the top bar or the production tab. It was planned as a separate, optional mod, because it changes the checksum and so loses Ironman achievements. Decided on 2026-10-12: scripted GUIs go into this mod (Milestone D).

## Compatibility checkpoints

Until a checkpoint, nothing is tested or built for use next to other mods. After Milestone A and again after Milestone B, decide whether to build a patch for RBM's GFX Overhaul (and later Road to 56) covering the screens finished so far.

The first checkpoint starts with the test deferred from Phase 1: how a single-window override behaves next to a mod that replaces the whole vanilla file. Its result shows how much of a patch is needed.

## Risks

- **Single-window override next to other mods.** The override works against vanilla. How it behaves next to a mod that replaces the whole vanilla file is still untested.
- **Engine-positioned widgets.** Some layouts (regiment grid, hull slots, combat width bars) cannot be moved from `.gui` files. The inventory step of each phase finds them before a layout is promised.
- **A redesign that promises more than the engine gives.** The game fills only the widgets its code asks for. `tools/Show-CodeNames.ps1` lists them during the inventory, before a layout is proposed.
- **Bitmap backgrounds with painted-in frames.** If no background option gives a clean result, the window keeps its vanilla size and only its lists and fonts are reworked.
- **Game updates.** A new game version can change windows the mod overrides. Re-running `tools/Export-VanillaBaseline.ps1` shows which ones.
