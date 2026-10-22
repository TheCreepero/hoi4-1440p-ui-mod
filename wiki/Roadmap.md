# Roadmap

The mod is built one screen at a time. Each phase reworks one screen for 2560x1440 and can be tested and released on its own. The rules every phase follows are in [Design Rules](Design-Rules.md); who does each step, and where the user decides, is in [Workflow](Workflow.md).

## Decisions

- **Baseline:** vanilla 1.19. Every screen is built and checked in a playset that contains just this mod, and then looked at in the user's own playset at a compatibility checkpoint (see "Compatibility checkpoints"). The first was on 2026-10-13.
- **Design target:** 2560x1440 at 100% UI scale. The mod does not fit smaller resolutions or a higher UI scale.
- **Depth:** a redesign per screen, not only an enlargement. Each screen is re-laid out around what the player wants to see at once: regrouped panels, a place of its own for every value the screen already has, larger fonts and backgrounds, fixed captions, and hotkeys for buttons that have none. New live values and new working buttons are not possible in a vanilla window; the limits are in [Design Rules](Design-Rules.md), "What a redesign can add". Scripted GUIs can add both; since 2026-10-21 they are the mod HOI4 Manager Pages (`../hoi4-manager-pages`).
- **Checksum:** untouched since version 2.0 (2026-10-21). The reworked screens are interface and texture files, outside the checksum: Ironman and achievements stay available. From phase D2 (2026-10-12) to version 1.9 the mod also carried the manager pages, whose script under `common/` changed the checksum; on 2026-10-21 the user decided to split them into the standalone mod HOI4 Manager Pages (`../hoi4-manager-pages`), so that this mod is checksum-clean again. The tests hold that nothing goes under `common/`.
- **Art:** no AI-generated images. Backgrounds are built from vanilla game assets.
- **Priority:** military lists, then the backlog.
- **Recursive widget lookups** (user, 2026-10-15): `hoi4.exe` on this machine is patched with the Modding Manager's `Scripts\Executable\Set-HoiRecursiveLookups.ps1`, so the game finds a vanilla widget inside a container the mod adds (W34). The design rules allow such cards from now on. The first screen that uses one works only on the patched executable and makes the mod local-only. After a game update, `-Status` tells whether the patch is still in place; patch again before a game check.
- **Designers out of scope** (user, 2026-10-14): the division, tank, plane and ship designers are not reworked. Mods the user plays with already change them: in the playset "Reordered Pack (USA)" RBM's GFX Overhaul defines all four files, and the VNR patch and Road to 56 change the ship designer too. A `zz_1440p_` override would win over them and lose what they did.
- **Workshop and the game executable** (user, 2026-10-15): the mod has not been published on the Steam Workshop. The user accepts keeping it a local mod if changes to the game's executable unlock more for it. Reading `hoi4.exe` with the Modding Manager's Ghidra project changes nothing in the game and comes first (Milestone F). A patch of the executable works only on this machine, so the first feature that needs one makes the mod local-only. The user decides each patch, and the decision is recorded here. The tools and their runbook are in the Manager's `Scripts\Executable`.
- **Local only** (user, 2026-10-15): the mod stays a local mod; screens may rely on the patched executable.
- **Vanilla sprite names** (user, 2026-10-16): where the code puts a sprite on a widget by its vanilla name, the mod may declare that name again with a wider texture, in `interface/zz_1440p_vanilla_sprites.gfx`, when only the reworked screen shows it. Used for the production lines (C1) and the priority rows of Recruit & Deploy (A5, step 2); the test suite holds the list.
- **Orchestrated phases** (user, 2026-10-16): a phase is run by an orchestrator (the interactive Claude Fable 5.1 session) with three kinds of agent: a designer (Claude Opus 5.5), a builder (Claude Sonnet 5.5 for a vanilla screen, Claude Opus 5.5 for a scripted page or a fix whose cause is unknown) and a game checker (Claude Opus 5.5). The orchestrator reviews every handoff and reads the captures itself; the user decides at three gates: the design page, the launches, the final report and their own test. Fix rounds go back to the same builder. The page is [Workflow](Workflow.md); the agent definitions are under `.claude/agents/`. The redesign pass of the same day ran this way before the rule was written.

## Status

Status values: Not started, In progress, Done. Each phase keeps its inventory, decisions and game-check log in `wiki/phases/` ([A1](phases/A1-air-selection.md), [A2](phases/A2-army-selection.md), [A3](phases/A3-unit-details.md), [A4](phases/A4-fleet.md), [A5](phases/A5-recruit-deploy.md), [A6](phases/A6-army-overview.md), [A7](phases/A7-air-wing-reorg.md), [A8](phases/A8-theatre-bar.md), [A9](phases/A9-card-pass.md), [A10](phases/A10-air-region.md), [C1](phases/C1-production.md), [C2](phases/C2-leader-selection.md); the notes of Milestones D and E went with the pages to HOI4 Manager Pages; template: [Phase Template](Phase-Template.md)); what the launches taught about the engine is in [Engine Facts](Engine-Facts.md).

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
3. **Lock the shared rules.** Done for the override method, the font steps used in A1 and the height of docked panels. The size limit for centred windows stays provisional: no centred window has been reworked yet. What A1 taught about the engine is in [Design Rules](Design-Rules.md).

## Milestone A: military lists

Phases are independent after Phase 1 and can be reordered.

| # | Screen | Vanilla file and main windows | Vanilla size | Background | Also changed by | Status |
|---|---|---|---|---|---|---|
| A1 | Air wings and airbases (pilot) | `airselectionview.gui`: `air_selection_view`, `unassigned_airwings_view` | 502x430, 582x430 | tiled panel, bitmap rows | none found | Done |
| A2 | Selected army: badge and division list | `unitview.gui`: `armies_view`, `army_badge_view`, `army_division_list_view`, `army_division_view` | list 422x430 | tiled, small bitmaps | RBM's GFX Overhaul | Done |
| A3 | Unit details: division, ship, air wing, railway gun | `unitview.gui`: `army_division_stats_view`, `ship_stats_window`; `airwingdetails.gui`: `air_wing_stats_window`; `railway_gun.gui`: `railway_gun_stats_view` | 856x497, 856x409 | bitmap | RBM's GFX Overhaul | Done; second redesign (stat tables) built and judged good by the tester in game on 2026-10-16 (railway gun render-only) |
| A4 | Navy and fleet view | `naviesview.gui`: `naviesview_window`, fleet and task force rows, composition editor, base picker | 500 wide, 86% high | bitmap cards and rows | RBM's GFX Overhaul, Vanilla Navy Rework | Done |
| A5 | Recruit and deploy | `countrydeploymentview.gui`: `countrydeploymentview`, `templatedeploymentwindow` | 550 and 375 wide, full height | tiled panels, bitmap rows | RBM's GFX Overhaul | Done |
| A6 | Army overview tab (divisions, fleets, air wings) | `countryarmyview.gui`: `countryarmyview` and its three rows | 550 wide, full height | tiled panel, bitmap rows | none found | Done, awaiting the tester's judgement |
| A7 | Air wing reorganisation | `airwingreorganization.gui`: `air_wing_reorganization` and its two entries | 1000x515 | tiled, bitmap entries | none found | Done, awaiting the tester's judgement |
| A8 | Theatre boxes at the top right | `theatreselector.gui`: the theatre boxes and the rows under them | 300 wide | bitmap | RBM's GFX Overhaul | Done, awaiting the tester's judgement |
| A9 | Card pass on the army badge (A2) and the navy header (A4) | `unitview.gui`: `army_badge_view`; `naviesview.gui`: `fleet_view_header` | 685x97, 740x166 | tiles | RBM's GFX Overhaul | Done; checked by the tester in game on 2026-10-16 (four rounds) |
| A10 | Air region details and its graph | `strategicairview.gui`: `strategicairview` with `details_wnd` | 552x327, details 513x515 | bitmap picture, parchment chart | none found | Done; judged working by the user in their own campaign on 2026-10-18 |

- A1 was first built 768 wide, before A2 showed how width is judged. It was narrowed to 705 afterwards. That is as narrow as it goes while the three blocks stay aligned: the mission bar is 703 wide at vanilla spacing with 15 missions. Wing and airbase names still fit; the status line "On Mission in <region>" is cut for the nine regions with the longest names.
  - The narrowing passed its game check. The same check found that an air group had always broken the layout: with a group selected the rows sit in a second list (`air_groups_view`) that was still 580 wide. That list and the air group badge are now 705 and 704 wide (`interface/zz_1440p_air_group.gui`). Confirmed by the tester in game, without a screenshot.
- A3 grew from two windows to four: the stat row is shared by the division, ship, air wing and railway gun details windows. They are in `interface/zz_1440p_unit_details.gui`; the division window moved there from the A2 file. Notes: [A3](phases/A3-unit-details.md).
  - First build: stats in a 22 px font on rows 28 px apart, in frames 1180 wide; the division window opens beside the army panel.
  - Redo (2026-10-11): the Stats tab of all four windows is dark cards of stat tiles (Base, Combat, Misc). The ship, air wing and railway gun frames grew from 473 to 584 px high. Checked in game for the division, ship, carrier and air wing, with tab hotkeys (`shift+a`, `shift+h`, `shift+t`); not for the railway gun (no recipe, Engine Facts H29). History and Template tabs, header and officer card keep the first build. `reference/mod/` refreshed.
  - Not done: showing the ship window's side panel only when it has content. Open for A4.
  - Not seen in game: railway gun details, a ship captain, history entries, an HQ division.
  - Second redesign (2026-10-16): the user judged the tiles less readable than vanilla. Every stat is one line of a table in the 18 px font, label left, value right, every second row banded, vanilla's three columns in one card (form B of the design page). The division window is 1186x562, the ship 794x462, the air wing 794x584; History rows banded; the Template board 465 high. Built, rendered and judged good by the tester in game the same day. Notes: [A3](phases/A3-unit-details.md), "Second redesign".
  - Polish (2026-10-12), seen in game on 2026-10-13: the text of a stat tile stands 5 px inside its plate, and the adjusters row of the division window has a card as the stats have. The other four reworked screens were looked over at full size and left as they are.
- A4 is done in two steps. Notes: [A4](phases/A4-fleet.md).
  - Step 1, built (`interface/zz_1440p_fleet.gui`): the panel is 740 wide instead of 492. A ship takes one line of 35 px with name and class side by side (about 26 ships on the screen instead of 22, the class name whole), task force cards are 86 px high instead of 125 with the composition counters in the mission box (the 12 task forces of the British Home Command fit on the screen, 8 did), fleet and task force names have 360 px, the home base name is whole, the toolbar is in four groups with five new hotkeys (`shift+n` and `shift+r` confirmed in game). The home base picker and the ship details window open beside the wider panel. It took three game checks: the first showed the task force tray mostly empty and a long class name still cut.
  - Step 2, built: the composition editor is 604 wide instead of 524 with class names in a larger font, the ship class picker shows all nine classes without scrolling (vanilla shows seven), the home base picker is 455 wide instead of 375 with base names in a larger font, and "Select Ships to Transfer" lists a ship per line, 10 before it scrolls instead of 7. One game check, plus one without the mod to measure where vanilla puts the windows.
  - Not seen in game: several fleets selected, a commander with traits, a damaged ship with its repair and refit buttons, the refit window, three of the five hotkeys, the template list of the composition editor.
  - The A3 item "show the ship window's side panel only when it has content" is still open.
- A5 is done (`interface/zz_1440p_recruit_deploy.gui`); the tester judged it finished on 2026-10-12. Notes: [A5](phases/A5-recruit-deploy.md).
  - The left panel is 640 wide instead of 550: a division in training shows its whole name in a larger font, and its name list shows 14 names instead of 10. The template panel is 618 wide instead of 375 and lists one template per line of 48 px, 22 before it scrolls instead of 17; it ends above the army portraits of the bottom bar. `shift+f` opens the division designer. Two game checks with the mod, after one layout chosen from three.
  - The six priority rows kept their vanilla size at first: the code swaps their background per kind of row. Step 2 (2026-10-16) widens them to the width of the cards through those sprite names (F3, Decisions); checked by the tester in game the same day.
  - Not captured by the harness, tried by the tester and found working: a line ready to deploy, a card with a location, the foreign templates list, a list long enough to scroll.
- A6, A7 and A8 were built on 2026-10-14 while the user was away, at their request, without a proposal round; each was checked by the harness with this mod alone and with the user's playset. They make version 1.7. Notes: [A6](phases/A6-army-overview.md), [A7](phases/A7-air-wing-reorg.md), [A8](phases/A8-theatre-bar.md).
  - A6: the panel is 900 wide instead of 550, and a division, a fleet or an air wing takes one line with every column whole: names (280 px for a division instead of 170), theatre and army in a box each instead of two lines in one, bars lying down. Modifier tiles fill the width, counts by type run ten a row, the filter box is 300 px. `shift+i` opens Equipment Details, which now slides in beside the wider panel, as does Sunk Ships.
  - A7: the window is 1240x995 instead of 1000x515: each list shows ten plane types instead of four, and equipment names are whole. It is the first centred window the mod reworks (S14).
  - A8: the file the roadmap named holds the theatre boxes at the top right, not the army portraits at the bottom. Each box and the rows under it are 420 wide instead of 300, growing to the left: the name field has 265 px, the shields 380 before they overlap. The gaps between shields are those of RBM's GFX Overhaul.
- A10 (2026-10-17 to 18, the first phase run with the orchestrated workflow from the start): the window that opens on a click on a strategic air region is 580x718 instead of 552x327, in cards and banded tables, and Details docks at its right at 914x718. The chart is 800x276 instead of 380x150 with 3 px lines on a dark plot (its sprite declared again, SPR-025), grid lines at the heights of its two upper labels and the x axis read as days ago (what the code draws was read in the executable: GUW-041, GUW-042). The 24 statistics are one table of twelve rows with Our and Enemy side by side, values only through replaced vanilla texts (LOC-013); the twelve top numbers are a captioned Our | what | Enemy table. No harness launch: the user tested it in their campaign. Version 1.9. Notes: [A10](phases/A10-air-region.md).
  - Not done: the recipe's click on a region is an estimate, and `reference/` has no capture of this view.

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

## Milestone B: designers (dropped)

Dropped on 2026-10-14 before any phase started, for the reason under "Decisions": mods of the user's playset already rework these screens, and an override would undo their work.

| # | Screen | Vanilla file | Also changed by | Status |
|---|---|---|---|---|
| B1 | Division designer | `divisiondesignerview.gui`: `countrydivisiondesignerview` | RBM's GFX Overhaul | Dropped |
| B2 | Tank designer | `tank_designer_view.gui` | RBM's GFX Overhaul | Dropped |
| B3 | Plane designer | `plane_designer_view.gui` | RBM's GFX Overhaul | Dropped |
| B4 | Ship designer and refit | `equipmentdesignerview.gui`, plus `ship_refit_equipment_view` in `naviesview.gui` | RBM's GFX Overhaul, VNR - RBM Compatibility Patch, Road to 56 (`interface/equipmentdesigner/`) | Dropped |

- What stays: the recipes that open the four designers (`tools/scenes/*_designer.json`, [Game Recipes](Game-Recipes.md)) and their vanilla captures under `reference/vanilla/`. They are dev-only and back [Engine Facts](Engine-Facts.md) H22.
- `shift+f` on Recruit & Deploy (A5) still opens the division designer. It is a hotkey on the mod's own window, not a change to the designer.
- The Larger Selector addon, whose namelist dropdown B1 would have taken over, is not replaced.

## Milestones D and E: the manager pages and the Records (moved)

From 2026-10-12 to 2026-10-21 this mod carried scripted GUIs of its own: the manager pages beside the vanilla panels (Milestone D: feasibility D0, Army Readiness D2, States D3, National Figures and History D4 and D5, the armies rows D6, the top bar strip D7) and the Records window for role-play (Milestone E: the probe E0, the War Diary E1, Officers E2, Government E3, Wars E4, Aces E5, unit honours E6). Their script under `common/` changed the checksum (no Ironman, every multiplayer player needs the mod), which the user had accepted on 2026-10-12.

On 2026-10-21 the user decided to split them out: they are the standalone mod **HOI4 Manager Pages** (`../hoi4-manager-pages`, its own repository, registry and Workshop item), with no dependency either way. Phase D8 "Free pages" made the last two docked pages (National Figures, Army Readiness) windows of their own first, so that no page needs an override of this mod ([D8 notes](phases/D8-free-pages.md) for the split; the notes of D0 to D7 and E0 to E6, the pages' rules and their roadmap live in that repository since the split). This mod is checksum-clean again from version 2.0.

## Milestone F: what the game executable shows

Opened on 2026-10-15, after the Modding Manager analysed `hoi4.exe` 1.19.3 in Ghidra and raised the division icon picker's limit for another mod [LIM-001] [LIM-003]. The decompiled code shows what the interface code does, which this mod has so far learned from game checks. Reading changes nothing in the game; a patch changes only this machine's executable (see Decisions). How to run a script against the saved project, and how a patch is recorded, is in the Manager's `Scripts\Executable\README.md`.

| # | Question | What it can open | Status |
|---|---|---|---|
| F1 | Which widget names does each window's code look up? | **Answered 2026-10-15:** every name the code looks up in the 72 reworked windows is a widget vanilla defines, so no window has a value it does not show yet (W33). `entry` and `army_division_list` are names the code gives objects it inserts at run time (W4). The list per window, with how each widget is searched, is the Manager's `Artifacts/executable/window-bindings-1440p.md`; it replaces the guess of `tools/Show-CodeNames.ps1`. | Done |
| F2 | Which sprites does each window's code set itself? | **Answered 2026-10-15:** the code names 320 sprites itself (G16); for this mod's screens 15 in `countrydeploymentview.gfx` (the priority rows, their icons and progress bars), 7 in `unitview.gfx`, the two theatre dropdown pieces and the plane strip of the army overview. The list per `.gfx` file is the Manager's `Artifacts/executable/code-set-sprites.md`; read it during the inventory. | Done |
| F3 | Can the priority rows of Recruit & Deploy be widened after all? | **Answered 2026-10-15: yes, by their sprites.** A test mod that declared the six row sprites again with textures 560 px wide got every row drawn at the new width, with no `.gui` change (G16). In this mod's panel the scrolling container of the list cuts them off at x 616 of the screen, so a texture has about 548 px of room unless that container grows. Using it means redefining vanilla sprite names, an exception to the Design Rules that is the user's decision. | Done; used by A5 step 2 and C1 (user, 2026-10-16) |
| F4 | Does a widget lookup ever search below the direct children? | **Answered 2026-10-15:** each widget type has two lookups. Those of the window itself search only its direct children (6503 of 7734 lookups), a second set also searches nested containers (1231) (W31). Seen in the game the same day: in the fleet header two directly looked-up texts moved into wrappers kept their placeholders and logged `Could not find`, while the recursively looked-up `home_base_name`, two containers down, still showed the base. **Lifted the same evening by a local patch** (user's decision): every direct lookup with a recursive twin now runs the twin, and the same two texts showed their values (W34). | Done |
| F5 | Where do windows the code docks get their offsets? | **Answered 2026-10-15 in part:** from named `positionType` entries of the windows' files, which the code fetches by name (S38). 111 of the 150 vanilla entries are read this way, as positions, offsets, sizes or counts; the Manager's `Artifacts/executable/position-types.md` lists them with their values. The ship class picker opens at the editor's position plus `sub_unit_selection_window_default_pos`, which this mod already sets to 596, 1. Not read: how the code stacks a frame under its neighbours (the wing list at 2,168, H23). | Done (offsets); stacking open |
| F6 | Why do lists the code fills ignore `max_slots_horizontal`? | **Answered 2026-10-15:** the code that fills `templates_grid` places each row itself at x 0 under the one before, and never reads the grid's slot settings; the icon picker works its slots out from them (S37). A list that the code stacks cannot get columns from a `.gui` file. | Done |
| F7 | Is any limit a single constant? | **Answered 2026-10-15 for the reworked windows:** the 120 functions behind them compare against no count but the icon picker's 1024 (already raised on this machine, LIM-003). The other constants are mission flags, number formatting (1000, 10000, 100000 for K and M) and buffer sizes. A limit found later in another screen is a candidate for a local patch, decided by the user. | Done |

What reading cannot open: a value the code does not give a window, one value in two places (W14), and a panel that narrows by itself. They are how the program works, not numbers in it, and the Manager's tools patch numbers only.

## Milestone C: backlog

Opened on 2026-10-15 with a design round (mock-ups composed from the references, the game's sprites and fonts; user's choices of 2026-10-16). Phases in order of the user's choice:

| # | Screen | Vanilla file and windows | Status |
|---|---|---|---|
| C1 | Production | `countryproductionlineview.gui`: the panel, ten kinds of line, five windows beside it | Done at 820 px; round 2 (steel cards on near-black, the bold variant) checked by the user in game on 2026-10-21 after one fix (wheel scrolling); round 1 checked on 2026-10-16 with the user's playset ([notes](phases/C1-production.md)) |
| C2 | General selection | `unitleaderwindow.gui`: `armyleaderwindow`, `armyleaderentry` | Done; checked by the tester in game on 2026-10-16 ([notes](phases/C2-leader-selection.md)) |

Not scheduled:


- **Selection popups:** general and admiral selection (`unitleaderwindow.gui`, 550x590, bitmap), advisor and law selection (`political_ideas_window`, 500x590, tiled).
- **Info windows:** events, technology and focus detail popups (550x550), land and naval combat, trade offer, war overview.
- **Side panels** (550 wide, already full height): production, construction, logistics, decisions, politics, diplomacy.
- **Newer screens in subfolders:** military industrial organisations, international market, special projects, factions.
- **Front end:** game setup and country selection.
- **What the code binds in these screens** (read 2026-10-15): the Manager's `Artifacts/executable/window-bindings-1440p-backlog.md` lists, for 368 windows of the files above, every widget the code looks up and how. The newer screens look most of their widgets up recursively, so cards that wrap content are possible there; decisions, events and the combat windows look up only direct children (W31). Every name the code looks up there is a widget vanilla defines (some in other capitals, which the lookups ignore, W32), a localisation key or a piece of a name.
- **Companion mod with scripted GUIs:** planned as a separate, optional mod because it changes the checksum; built inside this mod from 2026-10-12 (Milestones D and E); split out again on 2026-10-21 as HOI4 Manager Pages (user decision), see "Milestones D and E" above.

## Compatibility checkpoints

A checkpoint looks at the mod in the playset the user plays with: from the files with `tools/check_playset.py`, then in the game with that playset loaded. The method and every finding are in [Compatibility](Compatibility.md).

- **Checkpoint 1, 2026-10-13, done.** The playset "Reordered Pack (USA)": 55 mods, among them Road to 56 with Vanilla Navy Rework, RBM's GFX Overhaul and the Better Mechanics mods. The question deferred from Phase 1 is answered: next to a mod that replaces the whole vanilla file the mod's windows win by file name, without a line in the log. No patch mod is needed. Seven things were fixed in the mod itself: the victory points of Road to 56's map, a medal sprite that mod drops, a button on another mod's button, two texts that other mods make longer, the place of a wider insignia, and an error line of the state card.
- **Checkpoint 2:** when the playset changes much, or when a phase reworks a screen that a mod of the playset changes too.

## Risks

- **Other mods.** The single-window override holds next to a mod that replaces the whole vanilla file (checkpoint 1). What a playset can still break is listed in [Compatibility](Compatibility.md): sprites a mod drops or resizes, texts it makes longer, a second scripted GUI on the same spot, and a map or characters the mod's tables do not know.
- **Engine-positioned widgets.** Some layouts (regiment grid, hull slots, combat width bars) cannot be moved from `.gui` files. The inventory step of each phase finds them before a layout is promised.
- **A redesign that promises more than the engine gives.** The game fills only the widgets its code asks for. `tools/Show-CodeNames.ps1` lists them during the inventory, before a layout is proposed. Milestone F1 replaces its guess with the list read from the code.
- **Bitmap backgrounds with painted-in frames.** If no background option gives a clean result, the window keeps its vanilla size and only its lists and fonts are reworked.
- **Game updates.** A new game version can change windows the mod overrides. Re-running `tools/Export-VanillaBaseline.ps1` shows which ones.
