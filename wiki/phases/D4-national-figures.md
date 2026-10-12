# Phases D4 and D5: National Figures and History, opened from Politics

Two pages in one window beside the politics panel: the country's summed modifiers and figures today, and twelve of its figures month by month. Status: done on 2026-10-12, awaiting the tester's judgement; the monthly recording of D5 has not been seen running. The pages are described in [Scripted GUIs](../Scripted-GUIs.md).

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

- A second month: `on_monthly` has not run in a check.
- A month dropped after ten years by the real recording (the made-up months did drop: 130 written, 120 kept).
- A modifier that changes while the page is open.

## Close

- [x] Roadmap status and link
- [x] README and Workshop description
- [x] Scene files (`tools/scenes/national_figures.json`, `history.json`, written by the tool)
- [x] Finished pages stored under `reference/mod/`
- [ ] The tester's judgement: which modifiers belong on the page, which figures on the graph
- [ ] The tester's look after 1 February of a game: a second column
