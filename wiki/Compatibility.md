# Compatibility with other mods

The mod is built against the plain game. The user plays it in a playset of about 56 mods, and what holds against the plain game does not always hold there. This page says where two mods meet, how a playset is checked, and what each checkpoint found.

## Where mods meet

| Where | The rule | What goes wrong |
|---|---|---|
| A window both mods define | The game takes the definition of the file that comes last by name. `zz_1440p_*` comes after a mod's copy of the game's file, so this mod's window wins ([Engine Facts](Engine-Facts.md) L7). | What the other mod changed in that window is lost. |
| A game `.gfx` file a mod brings under the same name | The mod's copy takes the place of the whole file. A sprite the game's copy has and the mod's lacks is gone (L10). | Every icon that names it logs "Could not find sprite type". The line names neither mod nor file. |
| A sprite a mod defines again, or a picture it replaces | By name, or by path. Another size or number of frames comes through to every window that uses the sprite. | A wider picture runs into its neighbour or out of the panel. |
| A text a mod makes longer | A label wraps into as many lines as it needs unless its box has a fixed size (W28). | The extra line stands on what is below it. |
| Scripted GUIs on the same tab | Each mod places its own, and nobody knows of the others. | Two buttons on one spot: the upper one hides the lower. |
| Hotkeys | A key two mods use fires both when both widgets are up. | An action nobody asked for. |
| Content a page names | Script cannot ask the game for a portrait, a victory point, a law in a slot or a medal's picture, so the mod carries tables made from the plain game ([Scripted GUIs](Scripted-GUIs.md)). | A mod with another map, other characters or other laws is not in the tables. |

## Checking a playset

1. **From the files.** `python -I tools/check_playset.py` reads the launcher's active playset and reports each of the rows above: `playset windows sprites fonts hotkeys guis content` (name one or more for a part), `--window <name>` for what a mod changed in one window. It takes seconds and needs no game.
2. **The tables.** `python -I tools/make_game_tables.py --mods`, then `python -I tools/build_managers.py`: the officers the playset adds, and the victory points when the playset has a map of its own.
3. **In the game.** `.\tools\Invoke-GameSteps.ps1 -Start -Playset -AfterLoad tools\playsets\<name>.json` starts the game with the playset as it is, this mod last ([Game Recipes](Game-Recipes.md), "With the user's playset"). Then:
   - the load's `error.log`: `Compare-HoiErrorLog` lists the lines that name the mod or a sprite its windows name;
   - every recipe: `.\tools\Invoke-GameCheck.ps1 <scene> ... -NoRestart`, each crop beside its picture in `reference/mod/`;
   - the tabs other mods also stand on (step 1 lists them), and the state view;
   - the pages as the country the user plays (`tag <TAG>`), and a run of time inside the ten days.
4. **Without this mod**, when a crop shows something odd: the same screen with the playset alone tells whose it is. Not needed so far; the files told (the item window of the unit type counts is the same in the game and in RBM's file).

## Checkpoint 1: 13 October 2026, "Reordered Pack (USA)"

55 mods beside this one. Those that meet it: **RT56 - VNR - UTT Standalone v14** (a local mod: Road to 56 with Vanilla Navy Rework and the Ultimate Tech Tree), **RBM's GFX Overhaul**, **VNR - RBM Compatibility Patch**, **Better Mechanics** (22 mods; here Production, Economic Scales, Medals, Civilian and Military Laws, Training and Experience), **Anozin's USA Reimagined**, **Add German / Soviet / USA Generals AI REWORK**, **Toolpack without the Errors**, **Landlord**.

Three starts of the game with the playset (87 s to the menu, 17 s into the new game), as Germany and as the United States, with a run from 1 to 11 January 1936. The autosave was copied first and has the same hash afterwards.

### Found and fixed

| Found | Cause | Done | Seen in game |
|---|---|---|---|
| Of the 1495 victory points the mod follows, 223 were in another state, 252 had another value and 220 were no victory points on this map; 597 of the map's own were not followed | Road to 56 replaces `history/states`: 1143 states for the game's 1081, and other numbers for many | A second table for that map (`tools/victory_points_mods_table.py`, 1860 points). Script counts the states of the loaded game and takes the table with that number ([Engine Facts](Engine-Facts.md) X72) | "1143 states, table 1"; as the United States at war with Mexico: lines for Monterrey (a state and a value that differ), for Tampico and Eureka (points only that map has), the war's file with 2 taken and 1 lost |
| 19 lines "Could not find sprite type [GFX_medal_icon_eth_large]" at every load | Road to 56 brings `interface/medals.gfx` without the set for Ethiopia; the Officers page named that sprite | The medal strips are sprites of this mod on the game's pictures (`GFX_1440p_medal_<set>`, made with `tools/list_medals.py --sprites`) | 0 such lines at the next two loads; an officer's file shows the medals |
| On the Politics tab the National Figures button covered another mod's button | Better Mechanics: Production puts "Economy Status" and an arrow button at x 230 to 356 of the title strip | The button is 92 px wide with the caption "Figures", at x 359, between that and the game's own button at 454 | all four stand clear of each other |
| In the unit details the label "Trickleback & War Support Protection:" stood on its value | RBM's GFX Overhaul puts a text icon before each stat label, which makes this one three lines | The label's box has a fixed size of two lines; a third line is cut with dots (W28) | "Trickleback & / War Support Prote…", the two-line labels whole |
| On the Government page a party name stood on the party leader's name | Road to 56 has longer party names ("Kommunistische Partei Deutschlands - Kommunistische Partei Deutschlands (Opposition)") | The name's box has a fixed size of one line | cut with dots, the leader's name free |
| The fleet insignia at the end of a ship row stood 8 px outside the panel | RBM's insignia are 43 px wide, the game's 33 | Placed 8 px further left | ends at the panel's edge |
| "invalid scope for var. Key mod1440_sr_from" each time a state nobody took was selected | Not from another mod: the line of the state card names a country the state does not hold (X73). Found here because every line of the log was read | Every state gets a country once, where the record is set up | 1 line before the daily round, none for three selections after it. The last move of that step, from the daily round into the set-up effect, was made after the game was closed |
| Generals the mods add | Fixed earlier that day (X66) | - | 29 officers, and 102 after the mod's own event on 10 January |

### Looked at and left

- **Windows.** RBM's `unitview.gui` and `countrydeploymentview.gui` and the patch's `naviesview.gui` define nine windows this mod reworks. This mod's win. Lost: RBM's wider picker of division symbols (this mod's shows seven across over the full height, which serves RBM's many symbols as well), a button of an older game version, and a few pixels for RBM's own backgrounds.
- **The unit type counts in an army's header** overlap with RBM's larger small icons. The row's item window is the same in the game and in RBM's file, and this mod gives the row more room than the game does: it is how the playset looks without this mod too.
- **The state view.** Landlord's two buttons and the card of this mod do not touch.
- **The top bar.** The Records button stands free.
- **The Construction tab.** Road to 56's construction speed control is inside the tab; the States page begins right of it.
- **Building icons of the States table.** Road to 56 has longer strips of building pictures; the nine frames the table uses are the same buildings.
- **`error.log`.** About 9000 lines at the load come from the playset. None names this mod after the fixes.

### Not solved

Left as they are for now (user, 2026-10-13).

- **Portraits given as a file.** Road to 56 names 1451 portraits by their file (`large = "gfx/leaders/GER/r56_portrait_...dds"`) and not by a sprite. Script can show a sprite only, so these officers have the outline of an unknown leader (six of the first 23 German generals). The mod could declare a sprite for each file, but then the game logs a missing texture for each of them for every player without Road to 56. The user's country in this playset, the United States, has sprites throughout (one of 29 officers without).
- **Laws of other mods read "another law".** A condition on an idea the game does not know logs an error each time it is tested (X71), so the laws of the playset cannot be named the way its officers are. In this playset: 17 economy, 3 trade and 9 conscription laws of Road to 56 and one economy law of USA Reimagined.
- **Not in the pages:** 27 kinds of land equipment of Road to 56 and Better Mechanics, 13 buildings of Road to 56, 76 medals of Road to 56 and Better Mechanics: Medals, the 24 kinds of law of Better Mechanics: Civilian and Military Laws. The pages name the game's own (rule 6 of [Scripted GUIs](Scripted-GUIs.md)).
- **64 characters of the game** have another portrait in Road to 56 (none of the United States). The Records show the game's.
- **Shift+G** is the fleet's Upgrade here and the GDP button of Better Mechanics: Economic Scales, which is always on screen: with a fleet open the key does both. Six more keys of this mod are also keys of Toolpack, which only count while a Toolpack window is open (Shift+A, C, F, R, T, U).
- **Not looked at in a check with the playset:** the pages after a save and a load, a war fought by divisions, and the screens of Milestone C, which the mod does not rework yet. The designers (Milestone B) are out of scope: RBM's GFX Overhaul and the navy mods of the playset rework them.

### The user's own play

After the check the user played a while with the mod in this playset, a few wars among it, and noticed no issue (2026-10-13). That is play, not a check: no value was compared and no log was read.
