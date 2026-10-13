# Phase D2: Army Readiness, with the probe and the foundation of the scripted GUIs

The first scripted GUI of the mod, docked to Recruit & Deploy. The phase opened with a probe that settled the open engine questions and paid the one-time costs of every later page. D6 (the armies table) was built into the same page. Status: done on 2026-10-12, awaiting the tester's judgement. The page itself is described in [Scripted GUIs](../Scripted-GUIs.md).

## Scope

- Tab: Recruit & Deploy, the two panels of [A5](A5-recruit-deploy.md). The page is a container of the mod's own attached to the tab (`parent_window_token = deployment_tab`).
- What the vanilla screen does not show: how much manpower and equipment the country has left to recruit with, and how well the army in the field is equipped. The numbers sit in a top bar tooltip, on the logistics tab and in the army view.
- Out of scope: anything per template or per division in training. Script has no list of either (D0).

## Decisions

- 2026-10-12, user: all four managers (army readiness, states, armies, national figures) and graphs over time; pages docked to their tab; values of the own country only; a top bar strip later.
- 2026-10-12, user: "I am going away from my computer now so you can freely proceed with the implementation and testing." Taken as leave to start the game while the user was away; every launch is in the table below.
- A page changes nothing in the game: its buttons hide it, count again, sort or move the camera. A test holds the list of commands the mod's script may use.
- 975 px wide: the page stops short of the theatre box under the clock. The first build was 1216 wide and covered it.
- Counted values (two division counts, the equipment bars, the list of generals) carry the date of the count and a Count again button. Values of the game are live.
- One generator (`tools/build_managers.py`) writes every file of every page. Rows such as the sixteen kinds of equipment are tables in that file.
- No check runs time (the user's autosave is monthly). The daily and monthly hooks are asked of the tester.

## The probe

A throwaway build (`scratch/apply_probe2.py`, removed again) with one scripted GUI per question. What it showed is rows X6 to X25 of [Engine Facts](../Engine-Facts.md). In short:

| Question | Answer |
|---|---|
| A page docked beside its tab | Only if the tab's window has `clipping = no`; then it is drawn and clickable there |
| A window of its own, a hotkey, Escape | All work; the window takes the clicks inside its rectangle and takes Escape before the tab does |
| A list from an array: numbers, states, generals | Works, with the row's own values in each row; sideways too; the vanilla scrollbar scrolls it |
| A click in a row | Runs with the row's state as THIS and the country as ROOT; `ROOT = { goto_state = PREV }` moves the camera |
| Greyed buttons, right click, tooltips | Work |
| Hiding a group of widgets | Not through a nested container; a group is a scripted GUI of its own |
| `dirty` | Works, also for the first drawing |
| A progress bar filled by script | Works: the way to bars and to the columns of a graph |
| Sorting, a loop over every division | A few milliseconds for 152 states and 138 divisions |
| Values against the game's numbers | See X19 to X21 |
| Reload without a restart | Script, texts and layout of a scripted GUI are read again within seconds |

## What was built

- `interface/zz_1440p_recruit_deploy.gui`: `clipping = no` on `countrydeploymentview`, the one change to a vanilla window.
- `interface/mod1440_army_readiness.gui`, `common/scripted_guis/mod1440_army_readiness.txt`: the page, its handle, the row of the armies list.
- `common/scripted_effects/mod1440_effects.txt` (`mod1440_ar_count`), `common/on_actions/mod1440_on_actions.txt` (start of a game, each day), `common/synchronized_dynamic_tokens/mod1440_tokens.txt`, `localisation/<language>/mod1440_l_<language>.yml`.
- `interface/1440p_ui.gfx`: `GFX_1440p_SG_bar`, a bar from the vanilla organisation bar; `GFX_1440p_SG_column` and five `GFX_1440p_SG_head_*` for the later pages.
- Tools: `tools/build_managers.py`; `tools/render_gui.py` stacks the rows of a scripted list; `tools/GameHarness.ps1` counts `mod1440_` lines of `error.log` as the mod's.
- Tests: `tests/ScriptedGuis.Tests.ps1` (new); the checksum test of `tests/GuiInvariants.Tests.ps1` now allows the four script folders and nothing else; the text test of `tests/ScreenInvariants.Tests.ps1` measures the mod's own captions, and the recipe test skips the vanilla layout for a page that exists in the mod only.

## Game checks

Build: `8d5502c` plus uncommitted work, all on 2026-10-12.

| # | Build | Checked | Result | Screenshot | Taught |
|---|---|---|---|---|---|
| 1 | probe, first form | docked panels at x 1256, top bar button, window, `dirty` | the docked panels did not show; the rest worked | `scratch/checks/p_*-20261012-1614*` to `-1616*` | X6 to X9, X16 |
| 2 | probe, second form, then live changes | docking with `clipping = no`, lists, buttons, tooltips, camera, sort and loop as the Soviet Union, a general assigned, reload | all as in the table above | `scratch/checks/q_*-20261012-162*`, `-163*` | X6, X10 to X25 |
| 3 | first build of the page, then live changes | values against top bar and logistics; a math expression as bar fill | page up at 1216 px; the expression broke the file | `scratch/checks/ar_1-*`, `ar_3-*` | X26 |
| 4 | page at 975 px, new bar sprite | start-up count, training two divisions, hide and show, tooltips, the Soviet Union and Ethiopia | all work; shortages red, bars at their share | `scratch/checks/ar_4-*` to `ar_11-*` | X28, X29 |
| 5 | with the states table and the armies list | the armies list after assigning a general | Rundstedt: 30 divisions, 315 battalions, 100%, 26 / 3 / 1 | `scratch/checks/al_2-*` | X21 in use |
| 6 | with National Figures and History | see [D4](D4-national-figures.md) | - | - | X27 |
| 7 | final, cold start through `tools/Invoke-GameCheck.ps1` | Recruit & Deploy and the four pages, `error.log` | every expected widget found where the layout puts it; no line names the mod | `reference/mod/army_readiness.jpg`, `scratch/checks/*-20261012-173*`, `-174*` | the renderer lays a scripted page out to the pixel |

Not seen in game:

- A day or a month passing: the daily count and the monthly recording (X28).
- Garrison need above 0, a division below 75% strength or 50% organisation, a division fighting, planning above 0%.
- Shift, control and alt clicks.

## Rework of the look (2026-10-12)

The user, after the Records had been polished: "run a similar UI polishing pass on every other feature that has been implemented so far ... you may also add new visuals and reorganize elements where it is possible and make sense", to completion without their input.

- **What changed.** The two cards of label and value rows on the left are gone: their eleven figures are tiles in two rows across the top, with Count again and the date of the count in the twelfth place. The equipment table has the whole width for it, under a bar of column heads and with every second row on a darker band; it gained a column "Short" (needed less in the field, red) and the percentage beside a longer bar, which is orange below 75%. A kind the country neither has nor needs has a grey name. The armies table has the same heads and bands, the commander's rank (Marshal, General), his name in the highlight yellow and the percentage beside his bar.
- **Decided:** "Below 75% strength" and "Below 50% organisation" became "Under strength" and "Low organisation" to fit a tile; the thresholds are in the tooltips. A count above zero is yellow. The armies list shows ten rows before it scrolls (it showed seventeen): the equipment table took the height.
- **What it rests on.** Tiles, heads, bands, bars, colour codes and text icons as on the Records pages, which a game check saw (Engine Facts X56). New: row X57.
- **Not checked in game on 2026-10-12:** the launch was refused by the permission system of the assistant's tool that session ("Don't start the game without asking my permission first" stands; the user was away). The user installed the build on 2026-10-13 and played with it: "Overall I'm very happy with the results"; the error log of that session names the mod nowhere.
- **Checked in game on 2026-10-13**, cold start through `tools/Invoke-GameCheck.ps1` after the user allowed a launch: the page as the renderer drew it (`reference/mod/army_readiness-panel.png`). Eleven tiles (free manpower 1332K, as History's 1332.6; 269K, 19K and 37K in the three branches; 30 divisions, 315 battalions); five kinds of equipment with needed equal to in the field and a full green bar at 100%, the Short column empty; eleven kinds Germany neither has nor needs in grey; "No army has a commander yet". No line of `error.log` names the mod.
- **Checked as the Soviet Union the same day** (`tag SOV`, then Count again; `scratch/checks/b_ar1-*`, `b_ar2-*`): 138 divisions, 1231 battalions; five kinds short with the number in the field in red; the bar orange at 70% (support equipment) and 69% (light tanks), green at 76%, 78% and 91%.
  - **A fault:** Short read 1 less than needed less in the field for three kinds (27032 for 114750 and 87717). A text cuts the fraction of a number off, and equipment in the field has one (Engine Facts X65). The gap is now rounded up in script (`round_temp_variable`, a command new to the list of `tests/ScriptedGuis.Tests.ps1`); counted again in the open game it read 27033, 170, 218, 147 and 1000.
- **Changed on 2026-10-13 after the user's test with a mod that adds generals:** the armies list takes its commanders from the game's own loop (`every_army_leader`) and keeps each through `mod1440_of_me`, because the game's array `army_leaders` holds nothing for a general whose command came by an effect ([E2 notes](E2-officer-records.md), "Officers other mods add"; Engine Facts X66). The page was seen again as the USA with that mod loaded: counted on 4 January, no army with a commander.
- **Left unseen:** the rank and the band of a commander's row in the new look (the armies list was seen with a general before the rework); a commander without a number in that list.

## Close

- [x] The rework of 2026-10-12 seen in game, and `reference/mod/army_readiness*` stored again (2026-10-13)
- [x] Roadmap status and link
- [x] README and Workshop description: the pages, and that Ironman and achievements no longer work
- [x] `version` in `descriptor.mod` (1.5)
- [x] Engine Facts rows X6 to X31
- [x] Scene files (`tools/scenes/army_readiness.json`, written by the tool)
- [x] Finished page stored under `reference/mod/`
- [ ] The tester's judgement: width, what the page shows, the look of the cards
- [ ] The tester's look after a few days of game time
