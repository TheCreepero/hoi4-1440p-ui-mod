# Scripted GUIs: the manager pages

Milestone D of the [Roadmap](Roadmap.md) adds pages of the mod's own beside the vanilla panels: values the game has and shows nowhere in one place, as cards and tables that use the width of a 2560x1440 screen. They are scripted GUIs, the game's way to add widgets that script fills. This page holds the rules for them, what each page shows and how to work on them. What the script language offers is in [Script Reference](Script-Reference.md); what the engine does with a scripted GUI is rows X1 to X31 of [Engine Facts](Engine-Facts.md).

- **Cost:** script lives under `common/` and changes the game's checksum. The mod no longer works with Ironman and achievements, and in multiplayer every player needs it. Decided by the user on 2026-10-12.
- **Planned with the user on 2026-10-12:** all four managers and graphs over time; pages docked to their tab; values of the own country only; a top bar strip later.

## Rules

1. **Show and navigate, never change the game.** A scripted button changes its page (hide, sort, choose) or moves the camera. No effect that builds, adds, removes or changes a rule. `tests/ScriptedGuis.Tests.ps1` holds the list of commands the mod's script may use.
2. **Own country only.** Every scripted GUI is `player_context`. Script could read any country's real numbers, also where the game's intelligence system hides them; the mod does not.
3. **Every value is checked against the game's own number** before a page ships, and the check is logged in the phase notes. A name does not always mean what it seems to: `num_armies` counts divisions, `max_available_manpower_k` is not the free manpower.
4. **The map is one key away.** Shift+M hides and shows the page of the open tab. A page remembers per country whether it is open.
5. **No loop in anything drawn every tick.** Counting runs on a click, once a day or once a month; a long list is updated through `dirty`.
6. **Vanilla content only.** Equipment kinds, buildings, resources and modifiers are named in the mod's files, so what another mod adds does not appear. Tank rows use the chassis of No Step Back.
7. **Names** carry the prefix `mod1440_` (windows, files, variables, effects), sprites `GFX_1440p_SG_*`, and the art is vanilla sprites and textures.
8. **The AI never looks:** `ai_enabled = { always = no }` on every one.

## How a page stands on the screen

| Form | Where | Why |
|---|---|---|
| Docked to its tab: it opens and closes with the tab | Recruit & Deploy (Army Readiness), Construction (States) | A container attached with `parent_window_token` is cut off at the tab's window unless that window has `clipping = no` (X6). The mod's own Recruit & Deploy window has it since D2; the vanilla Construction window has it already. Trade has it too and has no page yet. |
| A window of its own, opened by a button in the tab's title strip | Politics (National Figures, History) | The vanilla Politics window clips. Overriding it for one line would put a vanilla copy of that window in front of every other mod that changes it. The page closes with Escape or the same key and stays open if the tab is closed first. |

Shift+M is the key on every tab: only the button of the open tab exists, so one key serves them all. No vanilla screen and no reworked screen of the mod uses it.

## The pages

| Page | Phase | Opens with | Shows | Status |
|---|---|---|---|---|
| Army Readiness | D2, D6 | Recruit & Deploy (`U`); open by default | manpower free, in training, in the three branches and needed by garrisons; divisions, battalions, army experience, divisions below 75% strength and below 50% organisation; per kind of land equipment the stock, what the divisions hold and what they need, with a bar; one row per general with troops | built, checked in game |
| States | D3 | Construction (`T`), then Shift+M; hidden by default | one row per state the player controls: free building slots, nine building levels, seven resources, population, compliance and resistance; sorted by any column; a click moves the camera to the state and hides the page | built, checked in game |
| National Figures | D4 | Politics (`Q`), then Shift+M | the country's summed modifiers in six groups (93 of them, blank where nothing applies), factories, fuel, counts, party popularity and a resource table | built, checked in game |
| History | D5 | the History button of National Figures | twelve figures month by month as a column graph, ten years at most | built; the graph checked with made-up months, the monthly recording not seen running |
| Top bar strip | D7 | - | a few numbers the top bar hides in tooltips | not started |

All texts are English. The names of equipment, buildings, resources, ideologies and most modifiers are the game's own text keys and follow the player's language.

### Army Readiness

File `interface/mod1440_army_readiness.gui`, docked 975 px wide beside the template panel, from under the top bar to above the army portraits. It stops short of the theatre box under the clock.

| Value | Script name | Checked against |
|---|---|---|
| Free manpower | `manpower_k` | the top bar (1332.6 for 1.33M) |
| In training | `amount_manpower_in_deployment_queue` | rose by 9600 per infantry division queued |
| In the army, navy, air force | `deployed_army_manpower_k` and its two siblings | not compared with a vanilla number |
| Needed by garrisons | `garrison_manpower_need` | 0 in a 1936 start: not seen above 0 |
| Divisions, battalions | `num_divisions`, `num_battalions` | the army's 30 divisions |
| Below 75% strength, below 50% organisation | counted by `mod1440_ar_count` with `unit_strength` and `unit_organization` | 0 in a 1936 start: the loop counted right with other limits (X22) |
| Stock, in the field, needed, per kind | `num_equipment@`, `num_equipment_in_armies@`, `num_target_equipment_in_armies@` | the stock column of the logistics tab; the Soviet Union's shortages show red with bars around 76% |
| General: skill, divisions, battalions | `skill_level`, `num_units`, `num_battalions` in the general's scope | the army badge |
| General: fighting, planning, by kind | `num_units_in_combat`, `avg_unit_planning_ratio`, `num_infantry`, `num_armored`, `num_motorized` | 26, 3 and 1 of Germany's 30 divisions; the first two not seen above 0 |
| General: equipment | the lowest of have / need over the sixteen kinds, worked out by `mod1440_ar_count` | 100% for a fully equipped army |

- **Live and counted.** Texts that hold a value of the game follow it at once, also while paused. The two division counts, the bars and the list of generals are counted: at the start of a game for every country, each day for a player, and on Count again. The date beside the button says when.
- **Not in the numbers:** divisions in training. "Needed" is what the divisions in the field ask for (queueing two divisions left it unchanged).
- **Not listed:** an army without a commander. Script reaches armies through their generals only.

### States

File `interface/mod1440_states.gui`, docked 1422 px wide beside the building column of Construction.

- **Columns:** free slots, infrastructure, civilian and military factories, dockyards, refineries, fuel silos, air bases, anti-air, radar; oil, aluminium, rubber, tungsten, steel, chromium, coal; population; compliance and resistance for a state that is not a core. A cell that would read 0 is left empty.
- **Free slots** are found with the trigger `free_building_slots` for a civilian factory, asked five times per state (16 or more? 8 or more? ...), because the trigger takes a written number only (X20). Checked: Hessen read 6, and its state view said 9 unlocked slots with 3 buildings. The state's `modifier@local_building_slots` would have said 8.
- **The list is made** when the page opens, on a sort, a choice or Refresh, and each day while it is open. The numbers of a row are from that moment (`dirty`).
- **Sorting:** a click on a column head sorts largest first, a second click turns the order, the State head gives the game's order back. 152 Soviet states sort in a few milliseconds (X22).
- **Not seen in game:** the Occupied choice and the two occupation columns with real values (a 1936 start has no occupied state); forts and naval bases, which stand in provinces and are left out.

### National Figures

File `interface/mod1440_figures.gui`, a window 1664 px wide beside the politics panel.

- **Modifiers** come from `modifier@<name>`: the sum the game itself works with, over every law, spirit, advisor, technology and focus. A value of 0 is left blank, so what applies stands out. A gain is green and a loss red; for costs and penalties (consumer goods, supply consumption, training time) it is the other way round.
- **Labels** are the game's own modifier names for 82 of the 93 rows (`MODIFIER_<NAME>`), so they are the words of the tooltips. All 93 modifier names are in the game's `modifiers_documentation.md`.
- **Checked:** party popularity against the politics panel (40, 35, 10, 15); factories against the top bar; consumer goods (25.0% and -2.4%, which is the 15 factories the construction tab shows); conscription 2.5% and resources to market 25% against the two laws of the start; the resource table against the resource row of the logistics tab, all seven. The other modifiers are the game's sums under the game's names and were not compared one by one.

### History

In the same file, on the same spot as National Figures; the History and Figures buttons switch between them.

- **What is written down:** free manpower, manpower in the field, divisions, the three kinds of factories, stability, war support, fuel, infantry equipment in stock, casualties, political power.
- **When:** at the start of a game for every country, then on the first of each month for a player. After ten years the oldest month is dropped. A game that gets the mod after its start has no column until the first of the next month, and the page says so.
- **The graph** is a row of 120 columns, each a progress bar that script fills to the month's share of the highest month (X17). The tooltip of a column gives its date and value.
- **Vanilla has a history of its own for one thing:** the logistics tab draws the stock of an equipment kind over time. The twelve figures here have none.

## What cannot be shown or done

- **No list of templates, training lines, production lines, the construction queue, the research queue, air wings or fleets.** Script has no array of any of them.
- **No order of the player.** No effect queues a division or a building, sets a priority or a deploy location. Effects that put a unit or a building on the map skip its cost: cheats, which rule 1 keeps out.
- **A row cannot select its army or its state.** `goto_state` moves the camera; the click on the map stays with the player.
- **A page cannot know which tab is open.** A docked page shows with its tab because it is a child of that tab; a window of its own cannot close when its tab does.

## Working on a page

- **One tool writes everything:** `python -I tools/build_managers.py`. The tables at the top of each section of that file are the pages: change them there. `--check` fails when the files on disk differ, and the test suite runs it.
- **Live:** start the game once with `tools\Invoke-GameSteps.ps1 -Start`, change the tool, run it, and the page is redrawn a few seconds later: script, texts and layout (X23). `error.log` gets "Reloading Database" and any parse error. A new `.gui` file and a new sprite need a restart (X27).
- **Reading a value without a text box:** `log = "... [?variable]"` in an effect writes to `game.log`.
- **Running an effect without a button:** the console command `effect <name of a scripted effect>`.
- **Scenes:** the tool also writes `tools/scenes/<page>.json` with a sample for every value, so `python -I tools/render_gui.py --scene <page>` draws the page and `tools\Invoke-GameCheck.ps1 <page>` brings it up and finds its buttons.
- **Tests:** `tests/ScriptedGuis.Tests.ps1`. Files up to date; every effect, trigger and property names a widget that exists; only listed commands; `player_context`; no AI; every name after `@` listed as a token; every text key defined.

## Known gaps

- **The daily and monthly hooks have not been seen running.** No check runs time: the user's autosave is monthly, and a check that let a month pass would overwrite it. `on_startup` was seen (the counts and the first column are there on 1 January 1936). `on_daily` and `on_monthly` are written the way vanilla writes `on_weekly` and `on_monthly` and The New Order writes `on_daily`. To look for after some days of play: the date beside Count again is today's, and History gets a second column on 1 February.
- **Not seen above zero:** garrison need, divisions below strength or organisation, divisions fighting, planning, occupied states.
- **Shift and control clicks** are not used; the harness cannot make them.
- **Other mods:** equipment, buildings and resources they add do not appear (rule 6). A mod that replaces the Recruit & Deploy window takes the docking of Army Readiness with it.
