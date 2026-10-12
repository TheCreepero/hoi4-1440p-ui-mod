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

## Close

- [x] Roadmap status and link
- [x] README and Workshop description
- [x] Scene file (`tools/scenes/states.json`, written by the tool)
- [x] Finished page stored under `reference/mod/`
- [ ] The tester's judgement: the columns, the default order, hidden by default
