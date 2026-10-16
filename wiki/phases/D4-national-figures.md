# Phases D4 and D5: National Figures and History, opened from Politics

Two pages in one window beside the politics panel: the country's summed modifiers and figures today, and twelve of its figures month by month. Status: done on 2026-10-12; redesigned on 2026-10-16 into one page docked to Politics, built and checked by render and tests, not seen in game (see "Redesign build" at the end). The user after playing: "This is good, everything seems to be working, including the history ticks", so the monthly recording of D5 runs. The pages are described in [Scripted GUIs](../Scripted-GUIs.md).

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

- **2026-10-13, with the user's playset:** the button in the title strip of Politics stood on the "Economy Status" button of Better Mechanics: Production (x 230 to 356). It is 92 px wide now (`GFX_1440p_SG_button_92`, the game's 148 px button as a tile), reads "Figures" and stands at x 359, before the game's own button at 454. The tooltip gives the full name. [Compatibility](../Compatibility.md).

## Close

- [x] The rework of 2026-10-12 seen in game, and `reference/mod/national_figures*` and `history*` stored again (2026-10-13)
- [x] Roadmap status and link
- [x] README and Workshop description
- [x] Scene files (`tools/scenes/national_figures.json`, `history.json`, written by the tool)
- [x] Finished pages stored under `reference/mod/`
- [ ] The tester's judgement: which modifiers belong on the page, which figures on the graph
- [x] The tester's look after 1 February of a game: the columns appear (reported 2026-10-12)

## Redesign build (2026-10-16)

Status: **built and checked by render and tests; not seen in game.** The user approved proposal d4-figures of the redesign pass and chose every decision (review page of 2026-10-16): docked to Politics, the ideology kept and moved, What applies by default, all twenty figures recorded, party popularity left to the panel.

What was built:

- **One page, docked.** National Figures and History are one page, `mod1440_figures`, 1680x1210, attached to `politics_tab` at 556,0 (screen 550,78 to 2230,1288, short of the theatre box). It opens and closes with Politics, is hidden by default and remembers per country whether it was open (`mod1440_nf_open`). Shift+M and the Figures button in the title strip of Politics (92 px at 359, beside Better Mechanics' button) fold it, and so does its own close button; Escape is left to the game, which closes Politics and the page with it. The History page, its window `mod1440_history` and its switch buttons are gone.
- **The override of Politics:** `interface/zz_1440p_politics.gui` holds `countrypoliticsview` as vanilla has it (baseline under `baseline/countrypoliticsview/`), with `clipping = no` on the window so that the page is drawn beside it [SGUI-005]. Three more values, all read with `tools/Compare-Baseline.ps1 zz_1440p_politics.gui -Group`: the `ideology` text of `ruling_party_info` one line lower (y 8 to 27), the `elections` text under it (y 29 to 45, maxHeight 32 to 18), and `scroll_wheel_factor` of `ideas` 40 to 106 (a whole row of idea categories, as the tests ask of every list).
- **The ideology and Road to 56.** The render found no free spot of a whole line inside the plate of 255x60 as vanilla lays it out: RT56's sub-ideology takes the first line (9,8, 155 px), the election text the rest, and the pie chart starts 19 px right of the plate. So the plate has three lines now: line 1 is left to RT56's `[GetSubIdeology]`, line 2 holds the ideology, line 3 the election text, which fits one line ("Next Election 1940.11.10" is 145 of 155 px). Without RT56 the first line is empty. The decision's fallback (moving `ideology` to y 600 and naming the ideology in the page's title strip) was not needed.
- **Twenty tiles that choose the graph** (two rows, two groups of five, 155x62): civilian factories (with how many are free), military factories and dockyards (idle), research slots, technologies; political power and command power with their daily gain; stability and war support with their bars; states; free manpower, manpower in the field, divisions, infantry equipment, casualties; fuel with its bar; convoys, trains, ships, planes. Every tile is a button (its sprite is the plate) and the chosen one has the lighter pick plate; under the value stands the change in a month, green or red (red for a rise of casualties), or "no change".
- **The graph across the page:** the chosen figure's name and unit, six plates (latest, in a month, in a year, highest, lowest, since the first month), the months on record and Zoom in; 120 columns of 10 px on 12 px steps, 240 high (one step per pixel), on two darker quarter bands; the scale, the year marks and the two dates as before.
- **Four lists of modifiers** (cards of 404x576): Politics and Diplomacy, Industry with the live resource table under it, Army and Manpower, Navy, Air and Research. Each card is a scrolling list (`dynamic_lists`) of arrays of the country: a head per group ("Politics", "6 of 12") and one row per modifier. The effect `mod1440_nf_fill` makes them when the page opens, when the view changes and each day while the page is open: per group a head, then every modifier that is not 0, or in the All view every one, with its label as a text key held in an array [SCR-015] and a copy of its value. A row shows one of seven ways of writing a value by a `_visible` trigger on its kind [SGUI-021], and a white label or, for 0, a grey one. The card titles count what applies ("9 of 20 apply").
- **The two views,** What applies (default) and All modifiers, are two buttons in the title strip; the chosen one has the second frame and a yellow caption.
- **Twenty figures written down monthly.** The first twelve keep their arrays `mod1440_h_0` to `_11`; the eight new ones are `mod1440_h_12` to `_19` (research slots, technologies, command power, states, convoys, trains, ships, planes). A save of the build before has twelve: `mod1440_h_record` and `mod1440_h_draw` put -1 in front of a newer series for every month it was not written down. A -1 is drawn as no column (the column's `_visible` trigger) and counts for neither the highest, the lowest, the first month nor the changes. At most 2400 numbers per player country.
- **No `dirty`:** the tiles and the resource table are live texts, so the page is drawn every tick, as the old National Figures was [SGUI-039]; the lists and the graph come from arrays that the effects make.
- `tools/check_effects.py` fills all twenty figures, and its new `mod1440_chk_months_twelve` fills the first twelve only, as a save of the build before has them.

Deviations from the design:

- The view buttons are `GFX_sort_button_140x29` at 330 and 480, not `GFX_button_123x34`: the game's 123 px button has one frame, so it could not show which view is chosen.
- The ideology moved one line down inside the plate and the election text with it (above); the design left the spot to the render.
- The labels of the mod that script holds as tokens (the group names and the eleven labels of the mod) have keys in lower case (`mod1440_nf_grp_politics`, `mod1440_nf_politics_0`), as the Records' tokens do. The game's own modifier keys are upper case (`MODIFIER_POLITICAL_POWER_FACTOR`), as the game defines them.

Not seen in game:

- That the page shows beside the panel and takes clicks there with `clipping = no` on `countrypoliticsview` (expected from SGUI-005, seen on Recruit & Deploy).
- That the advisor and law picker opens above the docked page.
- The labels fetched with `GetTokenLocalizedKey` from the game's upper-case `MODIFIER_*` keys, and the two whose text starts with a text icon (`£prod_eff`, `£prod_eff_cap`).
- Every value against the game: the list values against the tooltips of their sources; command power and its gain against the top bar; the changes under the tiles after two months.
- The padding of a save made by the build before (the check effect `mod1440_chk_months_twelve` makes one up); the eight new series in the user's game after a month.
- With the user's playset: RT56's sub-ideology on line 1 of the plate, Better Mechanics' button and container at 0,0 of the tab, the page over the RT56 interface.

Game check, when the user allows a launch:

```
tools/Invoke-GameCheck.ps1 national_figures history politics
```

Checklist for the tester:

1. Politics (Q): the panel as vanilla but for the ruling party plate, where the ideology stands on the second line and the election text on the third.
2. Shift+M, the Figures button and the page's close button open and fold the page beside the panel; it takes clicks; Escape closes Politics and the page; Politics opened again shows the page as it was left.
3. An advisor slot of the panel: the picker stands above the page.
4. What applies lists only the modifiers that are not 0 (Germany 1936: about 28 rows and 8 heads); All modifiers lists all 103, those that are 0 in grey, and the long lists scroll. The counts in the heads and the card titles agree with the rows.
5. The labels: every row has its name, also the two production efficiency rows of Industry (is the icon drawn?).
6. Three modifiers against the tooltip of their source (a law, a spirit, an advisor); command power and its daily gain against the top bar.
7. A click on a tile draws its figure; the chosen tile has the lighter plate; the six plates and the scale against the columns; Zoom in.
8. `effect mod1440_chk_months` and `effect mod1440_chk_months_twelve` (after `python -I tools/check_effects.py`): 120 columns for every figure; with the second, the eight new figures without columns ("Nothing is written down for this figure yet").
9. With the playset (`tools/Invoke-GameSteps.ps1 -Start -Playset`): RT56's sub-ideology on the first line of the plate, the ideology under it.
