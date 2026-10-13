# Phase D3: States, docked to Construction

A table of every state the player controls, beside the construction panel. Status: done on 2026-10-12, awaiting the tester's judgement. The page is described in [Scripted GUIs](../Scripted-GUIs.md).

## Scope

- Tab: Construction (`T`). The vanilla window `countryconstructionsview` is not overridden: it already has `clipping = no`, so a container attached with `parent_window_token = construction_tab` shows beside it.
- What the vanilla screen does not show: any list of states. Free slots, building levels and resources are read one state at a time, from the map or the state view.
- Out of scope: the construction queue (script has no list of it), queueing a building from the table (no effect does that without skipping the cost), buildings that stand in provinces.

## Inventory

- State values, all documented in the game's `dynamic_variables_documentation.md` and read in the probe (X20): `infrastructure_level`, `industrial_complex_level`, `arms_factory_level`, `building_level@<building>`, `resource@<resource>`, `state_population_k`, `compliance`, `resistance`.
- Free slots: no variable. The trigger `free_building_slots = { building = industrial_complex size > N include_locked = no }` takes a written N only, so a search of five questions is written out per state (`free_slot_tree` in `tools/build_managers.py`).
- The camera: `ROOT = { goto_state = PREV }` in the click effect of a row (X13).
- Icons of the column heads: frames of the vanilla `GFX_buildings_strip` and `GFX_resources_strip`, at 0.6 and 0.9 scale.

## Decisions

- Hidden by default. The construction tab needs the map: the table is a finder. Shift+M or the handle opens it, a click on a state moves the camera there and hides it again.
- 1422 px wide and as high as the screen allows above the bottom bar: 36 states without scrolling.
- A cell that would read 0 stays empty.
- The rows are updated through `dirty`: when the list is made, not every tick. 152 rows with 21 cells each then cost nothing (70 frames a second, as without the page).
- Sorting is an effect: the keys of the chosen column in one array, the game's `find_highest_in_array` picks the next row. A second click on the same head turns the order.

## Game checks

| # | Build | Checked | Result | Screenshot | Taught |
|---|---|---|---|---|---|
| 1 | first build | the handle beside the vanilla panel, the table, free slots | works on the first launch; Hessen reads 6 free, its state view 9 unlocked with 3 built | `scratch/checks/st_1-*`, `st_2-*`, `st_4-*` | X29 |
| 2 | the same game | a click on a row; sorting by population twice; "With free slots"; the Soviet Union | camera to Hessen and the page hidden; largest first, then smallest first with the arrow turned; 152 states at 70 frames a second | `scratch/checks/st_3-*`, `st_5-*` to `st_7-*` | - |
| 3 | final, cold start through `tools/Invoke-GameCheck.ps1` | the recipe (`T`, Shift+M), the two expected buttons | found where the layout puts them | `reference/mod/states.jpg` | - |

Not seen in game:

- The Cores and Occupied choices with different results, compliance and resistance with values: a 1936 start has no occupied state.
- The daily remake of an open list.
- A list longer than the page with the mouse wheel (the probe scrolled a scripted list by dragging the bar).

## Rework of the look (2026-10-12)

Part of the pass the user asked for after the Records had been polished ([D2 notes](D2-army-readiness.md), same section).

- **What changed.** The choices (All, Cores, Occupied, With free slots, Refresh) moved into the title strip, which gave the list a row more. The columns stand in five groups with 10 px between them, and a grey caption names the buildings, the resources and the occupation columns. Every second row is on a darker band. Under the list a bar holds the totals of every column over the states that are listed. Free slots are green; a state that is not a core has its name in another colour.
- **Decided:** 1472 px wide instead of 1422, for the gaps. The totals follow the choice: with "Cores" they are the totals of the cores. Compliance and resistance have no total. The arrow of the sorted column is now placed when the list is made, not by the click, so that a game saved with the old layout shows it over the right column.
- **Not checked in game on 2026-10-12** (the launch was refused that session, see D2). The user installed the build on 2026-10-13 and played with it: "Overall I'm very happy with the results"; the error log of that session names the mod nowhere.
- **Checked in game on 2026-10-13**, cold start through `tools/Invoke-GameCheck.ps1`: the page as the renderer drew it (`reference/mod/states-panel.png`). The totals of the 24 states of Germany's start agree with their columns, added up by hand from the capture: free slots 95, infrastructure 81, civilian factories 35 (the top bar's number), military factories 28, dockyards 10.
- **After the check:** the arrow of the sorted column is the game's small arrow at about half its size on the upper right corner of the head (at its own size it covered part of a narrow head). In the second check of the day it ran into the group caption above it: the game draws that text about 4 px lower than the renderer does. The captions were raised by 5 px in the open game and stand clear, under "Buildings" and under "Occupation" (`scratch/checks/b_st3-*`, `b_st4-*`). `reference/mod/states*` still shows the captions where they were: to be stored again at the next launch.
- **Left unseen:** as the United Kingdom (`tag ENG`) the Occupied choice and the colour of a name.

## Close

- [x] The rework of 2026-10-12 seen in game, and `reference/mod/states*` stored again (2026-10-13)
- [x] Roadmap status and link
- [x] README and Workshop description
- [x] Scene file (`tools/scenes/states.json`, written by the tool)
- [x] Finished page stored under `reference/mod/`
- [ ] The tester's judgement: the columns, the default order, hidden by default
