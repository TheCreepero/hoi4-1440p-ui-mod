# Roadmap

The mod is built one screen at a time. Each phase reworks one screen for 2560x1440 and can be tested and released on its own. The rules every phase follows are in [Design Rules](Design-Rules.md).

## Decisions

- **Baseline:** vanilla 1.19. Every screen is built and checked in a playset that contains just this mod, and then looked at in the user's own playset at a compatibility checkpoint (see "Compatibility checkpoints"). The first was on 2026-10-13.
- **Design target:** 2560x1440 at 100% UI scale. The mod does not fit smaller resolutions or a higher UI scale.
- **Depth:** a redesign per screen, not only an enlargement. Each screen is re-laid out around what the player wants to see at once: regrouped panels, a place of its own for every value the screen already has, larger fonts and backgrounds, fixed captions, and hotkeys for buttons that have none. New live values and new working buttons are not possible in a vanilla window; the limits are in [Design Rules](Design-Rules.md), "What a redesign can add". The manager pages of Milestone D add both, as scripted GUIs beside the vanilla panels.
- **Checksum:** changed since phase D2. The reworked screens (Milestones A and B) are interface and texture files, outside the checksum. The manager pages of Milestone D are scripted GUIs, the game's way to add new values and buttons; their script lives in `common/` and changes the checksum, so the mod no longer works with Ironman and achievements, and in multiplayer every player needs it. The user decided on 2026-10-12 that this is acceptable. Only four folders under `common/` are used, and the tests hold that line.
- **What a page of the mod may write:** its own records, and lines the game keeps for show (a division's history). Nothing the game charges for. Until 2026-10-12 a page changed nothing in the game; the user loosened this for the role-play pages of Milestone E ([Roleplay Pages](Roleplay-Pages.md)).
- **Art:** no AI-generated images. Backgrounds are built from vanilla game assets.
- **Priority:** military lists, then designers, then the backlog.

## Status

Status values: Not started, In progress, Done. Each phase keeps its inventory, decisions and game-check log in `wiki/phases/` ([A1](phases/A1-air-selection.md), [A2](phases/A2-army-selection.md), [A3](phases/A3-unit-details.md), [A4](phases/A4-fleet.md), [A5](phases/A5-recruit-deploy.md), [D0](phases/D0-manager-feasibility.md), [D2](phases/D2-army-readiness.md), [D3](phases/D3-states.md), [D4 and D5](phases/D4-national-figures.md), and the plans of Milestone E: [E0](phases/E0-roleplay-probe.md) to [E6](phases/E6-unit-honours.md); template: [Phase Template](Phase-Template.md)); what the launches taught about the engine is in [Engine Facts](Engine-Facts.md).

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
  - Polish (2026-10-12), seen in game on 2026-10-13: the text of a stat tile stands 5 px inside its plate, and the adjusters row of the division window has a card as the stats have. The other four reworked screens were looked over at full size and left as they are.
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
| D2 | Army Readiness, docked to Recruit & Deploy | Opened with a probe of two launches that settled the open engine questions (rows X6 to X25 of [Engine Facts](Engine-Facts.md)). Then the foundation, paid once: the tool that writes every file of a page (`tools/build_managers.py`), the tests (`tests/ScriptedGuis.Tests.ps1`), the changed checksum rule, the renderer and the harness reading a scripted page. The page: manpower, the army's counts, a table of land equipment (stock, in the field, needed, a bar). [Notes](phases/D2-army-readiness.md) | Done |
| D3 | States, docked to Construction | One row per controlled state, sorted by any column, a click moves the camera there. The vanilla Construction window needs no override: it already lets a page stand beside it. [Notes](phases/D3-states.md) | Done |
| D4 | National Figures, opened from Politics | The country's summed modifiers (93, in six groups), factories, fuel, party popularity, resources. A window of its own: the vanilla Politics window would have to be overridden to dock a page. [Notes](phases/D4-national-figures.md) | Done |
| D5 | History, the second page of National Figures | Twelve figures written down on the first of each month and drawn as columns. The graph is checked with made-up months. The monthly recording runs: no check lets time pass, and the user reported it after playing (2026-10-12). [Notes](phases/D4-national-figures.md) | Done |
| D6 | Armies, on the Army Readiness page | One row per general with troops: divisions, battalions, fighting, planning, the worst equipped kind, divisions by kind. Built with D2. | Done |
| D7 | Top bar strip | Numbers the top bar hides in tooltips, in the 930 px that are free at 1440p. | Not started (the user: later) |

What each page shows, the rules they follow and how to work on them: [Scripted GUIs](Scripted-GUIs.md). What the user chose on 2026-10-12: all four managers and graphs over time, pages docked to their tab, values of the own country only, the top bar strip later.

- **Look reworked on 2026-10-12, seen in game on 2026-10-13.** After the Records had been polished the user asked for "a similar UI polishing pass on every other feature". Army Readiness, States, National Figures and History were rebuilt in the look of the Records: figures as tiles, tables under a bar of heads with banded rows, shares as bars, grey for what does not apply. New on the pages: what each kind of equipment is short of, the totals of the listed states, a card of occupation and diplomacy modifiers, and for History a table of the twelve figures with their change in a month and in a year, a zoom and year marks. A cold start on 2026-10-13 showed all four as the renderer had drawn them. A second check the same day showed what a new game of 1936 does not: History over ten years of made-up months, and the orange bars and the Short column as the Soviet Union.

- **Asked of the tester, and answered on 2026-10-12:** a few days and a month of game time with the mod, because no check lets time pass (the user's autosave is monthly, and a check that let a month pass would overwrite it). The user: "This is good, everything seems to be working, including the history ticks."
- **Not built, and why:** a table of other countries (own country only); anything per template, per training line or per production line (script has no list of them).
- A layout D0 showed to work and nobody has asked for: the template panel at the right edge of the screen, the divisions in training at the left, the map between them.

## Milestone E: role-play pages

The idea (user, 2026-10-12): "I like to treat Hoi4 as a role-playing game. That means giving accurate names to units, keeping track of characters." The manager pages show what the country has today; these pages keep a record of the campaign as it is played. The game keeps almost no history that script can read, so the mod writes it down itself, from the day it is active in a game. What script can and cannot reach, the Records window that holds the pages, the recording they share and the decisions still open: [Roleplay Pages](Roleplay-Pages.md).

The user asked for each page to be planned in detail and written down before anything is built. The plans were written, the probe ran and corrected them, the user answered the open decisions, and on 2026-10-12 the pages were built: version 1.6. What each shows and how each value was checked: [Scripted GUIs](Scripted-GUIs.md), "The Records".

| # | Phase | Scope | Status |
|---|---|---|---|
| E0 | Probe | One launch on 2026-10-12, seventeen questions the documentation left open. Answered: a general keeps a record and the country can hold him, also once he has retired; dates, text keys and words chosen per row work in a list; eleven hooks fire with the scopes the vanilla comments give; a line of the mod shows in a division's history with the state's name; a card shows in the state view. Not answered: an ace. Rows X32 to X49 of [Engine Facts](Engine-Facts.md). [Notes](phases/E0-roleplay-probe.md) | Done |
| E1 | War Diary | A dated log: wars, peace, capitulations, territory, landings, government, promotions. Builds the Records window (a button in the top bar, Shift+J), the recording and the card in the state view. [Notes](phases/E1-war-diary.md) | Built and checked in game on 2026-10-12, awaiting the tester's judgement |
| E2 | Officers | Every general and admiral in one table, with a service record the mod keeps (commissioned, promoted, battles won and lost, states taken) and decorations the player awards: the game's own medals of the country, as a record with no effect. [Notes](phases/E2-officer-records.md) | Built and checked in game on 2026-10-12, awaiting the tester's judgement; battles not seen counting |
| E3 | Government | Head of government, parties, cabinet, high command, laws, faction, operatives, by name and with the date each took office. Operatives are a number only. [Notes](phases/E3-cabinet.md) | Built and checked in game on 2026-10-12, awaiting the tester's judgement |
| E4 | Wars | One row per enemy and per finished war: dates, days, losses, states taken and lost, outcome. [Notes](phases/E4-war-ledger.md) | Built and checked in game on 2026-10-12, awaiting the tester's judgement; totals not seen above zero |
| E5 | Aces | A roll of the air force's aces, if one can be kept. The probe could not ask: no effect fires the ace hooks. Three counters on the Wars page until an air war answers. [Notes](phases/E5-aces-roll.md) | Counters built; the roll waits |
| E6 | Unit honours | Lines in a division's own history: written by the mod when a capital falls, or for the divisions of a state on the player's click. The one part that writes into the game's records. [Notes](phases/E6-unit-honours.md) | Built and checked in game on 2026-10-12, awaiting the tester's judgement |

- **Order:** E1, E2, E4, E3, E6, E5.
- **Seen in a check that ran nine days:** the daily comparison running by itself, states lost to enemy troops, and that the monthly autosave is not written inside a month. No battle happened in those days.
- **Not possible, and why:** typing a note or a name (no text field); a division's or a ship's name on a page (script has none); the portrait of a general the game made up (nothing reads it); a list of battles with place and enemy (the hook gives neither).
- **Added on 2026-10-13, at the user's wish for "more graphical details", and checked in game the same day:** portraits (in the Officers list, in an officer's file, of the head of government, in the file of a war) and flags; a line in the War Diary and in the officer's file for each victory point that passes between the country and an enemy, and the general on the spot on every line about a state; the All view of the diary through both logs; a file for each war with the two flags, the two heads of government, figures and lines. [Scripted GUIs](Scripted-GUIs.md), "The Records".
- **Officers other mods add (2026-10-13).** The user's test with a mod that adds generals showed them missing from the Officers list: a leader whose command comes by an effect has no number a variable can hold. They are kept by their place in the game's list of characters now, listed with the others, and shown with their own portraits for the mods of the user's playset. Checked in game with that mod. [Scripted GUIs](Scripted-GUIs.md), "The Records"; [E2 notes](phases/E2-officer-records.md).
- **Decided by the user on 2026-10-12:** the rule as worded, one Records window, capitals in the main view and every state under a filter, the game's national medals as decorations, unit honours written by the mod itself, version 1.6, and time in a check: up to ten days inside January 1936 with a copy of the autosave made first.
- **Asked of the tester:** a war. Battles won and lost per general, a capitulation, casualties, a landing and an ace have not been seen; and a save and a load, after which an officer's record should still be there.

## Milestone C: backlog (not scheduled)

- **Selection popups:** general and admiral selection (`unitleaderwindow.gui`, 550x590, bitmap), advisor and law selection (`political_ideas_window`, 500x590, tiled).
- **Info windows:** events, technology and focus detail popups (550x550), land and naval combat, trade offer, war overview.
- **Side panels** (550 wide, already full height): production, construction, logistics, decisions, politics, diplomacy.
- **Newer screens in subfolders:** military industrial organisations, international market, special projects, factions.
- **Front end:** game setup and country selection.
- **Companion mod with scripted GUIs:** country-level panels, for example extra numbers in the top bar or the production tab. It was planned as a separate, optional mod, because it changes the checksum and so loses Ironman achievements. Decided on 2026-10-12: scripted GUIs go into this mod (Milestone D).

## Compatibility checkpoints

A checkpoint looks at the mod in the playset the user plays with: from the files with `tools/check_playset.py`, then in the game with that playset loaded. The method and every finding are in [Compatibility](Compatibility.md).

- **Checkpoint 1, 2026-10-13, done.** The playset "Reordered Pack (USA)": 55 mods, among them Road to 56 with Vanilla Navy Rework, RBM's GFX Overhaul and the Better Mechanics mods. The question deferred from Phase 1 is answered: next to a mod that replaces the whole vanilla file the mod's windows win by file name, without a line in the log. No patch mod is needed. Seven things were fixed in the mod itself: the victory points of Road to 56's map, a medal sprite that mod drops, a button on another mod's button, two texts that other mods make longer, the place of a wider insignia, and an error line of the state card.
- **Checkpoint 2: after Milestone B**, or when the playset changes much. The designers are the screens RBM's GFX Overhaul and Vanilla Navy Rework change most.

## Risks

- **Other mods.** The single-window override holds next to a mod that replaces the whole vanilla file (checkpoint 1). What a playset can still break is listed in [Compatibility](Compatibility.md): sprites a mod drops or resizes, texts it makes longer, a second scripted GUI on the same spot, and a map or characters the mod's tables do not know.
- **Engine-positioned widgets.** Some layouts (regiment grid, hull slots, combat width bars) cannot be moved from `.gui` files. The inventory step of each phase finds them before a layout is promised.
- **A redesign that promises more than the engine gives.** The game fills only the widgets its code asks for. `tools/Show-CodeNames.ps1` lists them during the inventory, before a layout is proposed.
- **Bitmap backgrounds with painted-in frames.** If no background option gives a clean result, the window keeps its vanilla size and only its lists and fonts are reworked.
- **Game updates.** A new game version can change windows the mod overrides. Re-running `tools/Export-VanillaBaseline.ps1` shows which ones.
