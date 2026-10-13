# Phases D4 and D5: National Figures and History, opened from Politics

Two pages in one window beside the politics panel: the country's summed modifiers and figures today, and twelve of its figures month by month. Status: done on 2026-10-12. The user after playing: "This is good, everything seems to be working, including the history ticks", so the monthly recording of D5 runs. The pages are described in [Scripted GUIs](../Scripted-GUIs.md).

## Scope

- Tab: Politics (`Q`). The vanilla window `countrypoliticsview` is not overridden. It clips, so the page is a window of the mod's own at 556,78; a button in the title strip of the politics panel (`parent_window_token = politics_tab`) and Shift+M open and close it.
- What the vanilla game does not show: the sum of a modifier over all its sources. It shows each source (a law, a spirit, an advisor) with its own numbers, and the sum only in the tooltip of whatever the modifier acts on. And no history of any figure but the stock of an equipment kind (logistics tab).
- Out of scope: other countries; where a sum comes from (script reads the sum, not its parts).

## Inventory

- `modifier@<name>` in country scope (documented as "a modifier stored in country scope"; The New Order shows such values in its ledger tooltips). The page has 93 modifier rows, and all 93 names are in the game's `modifiers_documentation.md`.
- Labels: the game's text key `MODIFIER_<NAME>` for 82 of them. A few keys are not named after their modifier (`industrial_capacity_factory` is `MODIFIER_INDUSTRIAL_CAPACITY_FACTOR`, `conscription` is `MODIFIER_CONSCRIPTION_FACTOR`). Eleven rows have a label of the mod: nine for which no key was found (division attack and defence, the three experience gains and others), two to tell a modifier from the value of the same name.
- Real values beside the modifiers: `political_power_daily`, `stability`, `has_war_support`, `command_power_daily`, `party_popularity@<ideology>`, the factory counts, `fuel_k`, `resource@`, `resource_produced@`, `resource_consumed@`, `resource_imported@`, `resource_exported@`.
- For the graph: arrays of the country, one per figure, filled by `mod1440_h_record`; a list that runs sideways (X10) of progress bars filled through `frame` (X17).

## Decisions

- A value of 0 is blank. Of 93 modifiers most are 0 for any one country, and what applies should stand out.
- Costs and penalties are coloured the other way round (the format `-`): a rise of consumer goods or supply consumption is red.
- "Stability now" and "War support now" are the values; the two modifier rows under them carry labels of the mod, because the game calls the modifiers "Stability" and "War Support" as well.
- History is a page of the same window, not a window of its own: the History and Figures buttons sit on the same spot and switch.
- Monthly, ten years, twelve figures: 1560 numbers per player country in a save at most. Every country gets its first month at the start of a game, so that whichever the player takes has it.
- A column graph. Lines between the months would need a shader of the mod's own (The New Order has one); not done.

## Game checks

| # | Build | Checked | Result | Screenshot | Taught |
|---|---|---|---|---|---|
| 1 | first build, added to a running game | the page | "Undefined GUI_TYPE": a `.gui` file added while the game runs is not read | - | X27 |
| 2 | after a restart | the page as Germany; the History page; made-up months through the console (`effect mod1440_h_test`, a throwaway effect) | eight cards, zeros blank, colours right; one column on 1 January 1936; 120 made-up months drawn as columns with the scale beside them; the tooltip of a column gives date and value | `scratch/checks/nf_3-*`, `nf_5-*`, `h_1-*` to `h_4-*` | X28, X30 |
| 3 | the same game | a changed label | did not show until every scripted GUI file had a new time stamp and the window was opened again | `scratch/checks/nf_6-*` to `nf_8-*` | X27 |
| 4 | final, cold start through `tools/Invoke-GameCheck.ps1` | both recipes, the expected buttons | found where the layout puts them | `reference/mod/national_figures.jpg`, `reference/mod/history.jpg` | - |

Values compared with the game's own numbers (Germany, 1 January 1936): party popularity 40, 35, 10, 15 (politics panel); factories 35, 28, 10 (top bar 73); consumer goods 25.0% and -2.4% (15 factories on the construction tab); recruitable population 2.50% and resources to market 25.0% (the two laws of the start); the resource balances 3, 104, -5, 3, 177, 1, 195 (logistics tab). The other modifiers were not compared one by one.

Not seen in game:

- A second month in a check: `on_monthly` has not run in one. It runs in the user's game ("everything seems to be working, including the history ticks", 2026-10-12).
- A month dropped after ten years by the real recording (the made-up months did drop: 130 written, 120 kept).
- A modifier that changes while the page is open.

## Rework of the look (2026-10-12)

Part of the pass the user asked for after the Records had been polished ([D2 notes](D2-army-readiness.md), same section).

National Figures:

- **What changed.** What the country has today moved out of the cards into a band across the top: ten tiles (the three kinds of factories with their icon and, in grey, how many are free or idle; research slots, technologies, states, convoys, trains, ships, planes), and under them stability, war support and fuel as wide bars and the four parties as small ones. The modifiers stand in eight cards instead of six: Economy went into the tiles, "Manpower, Research, Intelligence" was split, and Occupation and Diplomacy is new (eight modifiers: compliance growth, resistance target, growth and decay, required garrisons, surrender limit, guarantee cost, volunteer divisions). A modifier of 0 keeps its name in grey; before, only its value was missing. Every second row is on a darker band. The resource table has heads of its own (its title ran into them) and the icon of each resource.
- **Decided:** "Stability now" and "War support now" are bars, not rows. The bars are filled by an effect (`mod1440_nf_bars`) when the page opens and each day; the numbers beside them stay live. The grey name is a second text under the white one, which a trigger shows when the modifier is not 0.

History:

- **What changed.** The twelve buttons became a table: the figure, its newest month, and the change in a month and in a year in green or red. The graph has its own card with five tiles (newest, highest, lowest, change since the first month, months on record), four bands for the quarters of the scale with five numbers beside them, the year under the first column of each year, and a Zoom in switch that lets the columns start at the lowest month. The page is as wide as National Figures (1664 px); a column is 6 px wide instead of 9.
- **Decided:** numbers are written with the decimals of their figure (30 divisions, 1332.6 thousand men): two texts per number, one of which a trigger shows. The lowest month is found with a loop of the page's own, because no script of the game uses `find_lowest_in_array`. The year marks are texts of the page that script moves (as the arrow of a sorted column), not a text in each column: a column is 8 px wide and would cut it. A record carries its year from now on; older months get no mark.
- A page left open in a saved game is drawn again by the daily hook (it is drawn only when its `dirty` variable changes).

Both: **not checked in game on 2026-10-12** (the launch was refused that session, see D2). The user installed the build on 2026-10-13 and played with it: "Overall I'm very happy with the results"; the error log of that session names the mod nowhere.

**Checked in game on 2026-10-13**, cold start through `tools/Invoke-GameCheck.ps1` (`reference/mod/national_figures-panel.png`, `history-panel.png`):

- National Figures as the renderer drew it. The bars agree with the numbers beside them: stability 81.0%, war support 35.0%, fuel 297K of 371K, the parties 40, 35, 10, 15. The tiles: 35, 28 and 10 factories with their icons and "20 free", "8 idle", "0 idle" in grey. A modifier of 0 has a grey name, one with a value a white name. The resource table reads 3, 104, -5, 3, 177, 1, 195, as in the first check. Occupation and Diplomacy: compliance growth -2.0%, resistance target +5.0%, surrender limit -9.0%, the other five grey; not compared with a tooltip of the game.
- History with the one month of a new game: the table of twelve figures with the newest month (free manpower 1332.6, 30 divisions, 35, 28 and 10 factories, stability 81.0), the band of the chosen row, the five tiles, the scale with its four bands, one column, the date under each end of the graph.

**Checked with made-up months the same day** (`python -I scratch/h_test.py`, then `effect mod1440_h_test`, `_old` and `_few` in the console; `scratch/checks/b_h1-*` to `b_h4-*`): 120 columns after 130 months were written (the oldest ten forgotten); the year marks 1937 to 1946 under the first column of each year; the table with the change in a month and in a year in green and red, for casualties the other way round; the tiles (highest 25641.0, lowest 9100.0, +16541.0 since the first month, 120 months); Zoom in with the scale from 9100.0; seven months, where the four bands of the scale show; and the months of an older save without years (no marks, nothing else amiss). `python -I tools/build_managers.py` wrote the effects file back.

**Left unseen:** a month written by `on_monthly` with its year in a check. It runs in the user's game.

## Close

- [x] The rework of 2026-10-12 seen in game, and `reference/mod/national_figures*` and `history*` stored again (2026-10-13)
- [x] Roadmap status and link
- [x] README and Workshop description
- [x] Scene files (`tools/scenes/national_figures.json`, `history.json`, written by the tool)
- [x] Finished pages stored under `reference/mod/`
- [ ] The tester's judgement: which modifiers belong on the page, which figures on the graph
- [x] The tester's look after 1 February of a game: the columns appear (reported 2026-10-12)
