# HOI4 1440p UI Mod

High-resolution UI mod for Hearts of Iron IV that redesigns screens for 1440p (2560x1440) and higher displays, adds manager pages that fill the free width with tables and figures of your country, and keeps a record of your campaign for role-play: a war diary, your officers, your government and your wars.

## Overview

- **Game**: Hearts of Iron IV
- **Supported Version**: `1.19.*`
- **Mod Version**: `1.9`
- **Tags**: Graphics, Utilities, Fixes
- **Requires**: 2560x1440 or higher at 100% UI scale
- **Ironman & Achievements**: Not compatible since version 1.5. The manager pages are scripted GUIs, and their script under `common/` changes the game checksum. In multiplayer every player needs the mod. The pages show values and keep records of their own; the one thing they write into the game is a line in a division's history (unit honours, see The Records).
- **Status**: In development, one screen at a time. Not published on the Steam Workshop, and local from the first screen that wraps vanilla widgets in containers of its own: that needs `hoi4.exe` patched with the Modding Manager's `Scripts\Executable\Set-HoiRecursiveLookups.ps1` (decided 2026-10-15). See [wiki/Roadmap.md](wiki/Roadmap.md), Decisions and Milestone F.
- **Tested with**: the vanilla game, and on 13 October 2026 in a playset of 55 other mods with Road to 56, Vanilla Navy Rework, RBM's GFX Overhaul and the Better Mechanics mods; the army overview, the air wing reorganisation and the theatre boxes in the same playset on 14 October. What was found and fixed there, and what is not solved: `wiki/Compatibility.md`.

## Reworked Screens

- **Air wings and airbases** (the panel shown when airbases, air wings or an air group are selected): 20 rows before the list scrolls instead of 9, wider rows that show wing names in full, larger text, and the mission bar, toolbar, air group badge and list joined into one block of the same width.
- **Selected army** (the badge and division list shown when an army is selected):
  - The division list reads as a table: organisation and strength as two lying bars, warnings in a block of their own instead of on the template icon, division names in full in a larger font, and captions on the sort buttons.
  - The change-template dropdown shows 12 templates instead of 6, with names on one line.
  - The army badge has a longer name field, the commander's name in full in a larger font, and the four commander stats spaced apart.
  - New hotkeys: `Shift+U` unassigns the selected divisions, `Shift+C` consolidates them.
- **Unit details** (the windows that open from the icon of a division, ship or air wing):
  - The Stats tab of all four windows is regrouped into dark cards (Base, Combat, Misc) of stat tiles: a small label over a large value. Long labels such as "Trickleback & War Support Protection" wrap instead of being cut. The ship, air wing and railway gun windows are taller to fit the cards.
  - The division window opens beside the army panel instead of on top of it, and its Template and History tabs fill the larger frame.
  - Equipment and plane names on one line, and the terrain adjusters visible without scrolling where they fit.
- **Fleet panel** (the panel shown when a fleet or task force is selected):
  - The ship list reads as a table: one line per ship with organisation and strength as two lying bars, the name in a larger font and the class name in full beside it, so more ships fit on the screen.
  - Task force cards are lower, with the ship counts on the mission line, so a fleet of twelve task forces fits on the screen without scrolling.
  - Fleet and task force names, the home base name and the commander's name have room to show in full, and the toolbar buttons are in four groups.
  - New hotkeys with ships selected: `Shift+N` makes a new task force of them, `Shift+R` moves them to the reserve fleet, `Shift+O` balances task forces, `Shift+G` upgrades, `Shift+P` repairs now.
  - The home base picker and the ship details window open beside the wider panel.
  - Pop-ups: the ship class picker of the composition editor shows all nine classes without scrolling, the composition editor and the home base picker are wider with names in a larger font, and "Select Ships to Transfer" lists one ship per line.
- **Recruit & Deploy and Division Templates** (the two panels the `U` key opens):
  - A division in training shows its whole name in a larger font, and its name list shows 14 names instead of 10.
  - The template list is a table: one template per line with its name in full, the cap, Train, Edit and the two toggles beside it, so 22 templates fit before the list scrolls instead of 17.
  - The template panel ends above the bottom bar, so the army portraits stay in reach; the symbol picker shows seven symbols per row.
  - New hotkey: `Shift+F` opens the division designer.
- **Army overview** (the panel the `O`, `P` and `L` keys open: divisions, fleets, air wings):
  - Every division, fleet and air wing takes one line with each column in full: names in a larger font (a division's name has 280 px instead of 170), theatre and army in a box each instead of two lines in one, organisation and strength as two lying bars.
  - The panel is 900 px wide instead of 550. The modifier tiles fill its width, the counts by type run ten a row, the filter box is wider, and the air list starts as high as the division list.
  - Equipment Details and Sunk Ships open beside the wider panel. New hotkey: `Shift+I` opens Equipment Details.
- **Air wing reorganisation** (the window "Add new Air Wing" opens): 1240x995 instead of 1000x515, so each list shows ten plane types before it scrolls instead of four, and equipment names such as "Inter-War Medium Airframe" appear in full.
- **Theatre boxes** (top right of the map): each theatre box and the rows under it are 420 px wide instead of 300, growing to the left: the theatre's name has more room, about twelve army shields fit side by side instead of eight, and the counts of the fleet rows no longer run into the next icon.
- **Air region details** (the window that opens on a click on a strategic air region in the air map mode):
  - The graph is 800x276 instead of 380x150, with thicker lines on a dark plot. Its grid lines sit on the two upper labels (the largest value shown and half of it), and the axis reads 30 to 0, days ago, as the newest day is at the right.
  - The 24 statistics are one table: one row per kind (fighters lost, troops bombed and so on), Our and Enemy side by side, each with its tick box, the colour of its line and its number. A ticked cell lights up.
  - The twelve numbers at the top are a captioned table: fighters, bombers, close air support planes, anti-air, air detection and efficiency, Our against Enemy. The air superiority bar has a caption, and the mission buttons sit in a bar above the cloud picture.
- **Production** (the panel the production tab opens):
  - Every production line is a card of riveted steel on a near-black panel: line names, the factory count and the ready date in the large title font, and the line's materials in a row in its head.
  - Factory slots sit in a grid of boxes beside the progress bar, and one notch of the mouse wheel scrolls one card.
  - The factories, the material stock and the production and efficiency figures stand in three cards across the top, with the filters in a row under them.

## Manager Pages

Pages of the mod's own that stand beside a vanilla panel and use the width of the screen for values the game shows nowhere in one place. `Shift+M` shows and hides the page of the open tab. They show values of your own country and change nothing in the game.

- **Army Readiness** (beside Recruit & Deploy, open by default):
  - Eleven figures as tiles across the top: manpower free, in training, in the army, navy and air force and asked for by garrisons; divisions, battalions, army experience, divisions under strength (below 75%) and low on organisation (below 50%).
  - Equipment: for sixteen kinds of land equipment the stock, what the divisions in the field hold, what they need and what they are short of, with a bar and its percentage. A shortage is red, a bar below 75% orange, a kind you neither have nor need grey.
  - Armies: one row per commander with troops: rank, skill, divisions, battalions, divisions fighting, planning, the worst equipped kind of equipment, divisions by kind.
- **States** (beside Construction, opened with `Shift+M`):
  - One row per state you control: free building slots, the levels of nine buildings, seven resources, population, and compliance and resistance for occupied states.
  - A click on a column head sorts, a second click turns the order. Three choices narrow the list: cores, occupied, with free slots.
  - A bar under the list holds the totals of every column over the states that are listed.
  - A click on a state moves the camera there and hides the page.
- **National Figures** (opened from Politics with `Shift+M` or the button in its title strip):
  - Across the top, what your country has today: factories and how many are free, research slots, technologies, states, convoys, trains, ships and planes as tiles; stability, war support, fuel and the four parties as bars.
  - The summed modifiers of your country, 101 of them in eight groups: what all laws, spirits, advisors and technologies together add to factory output, construction speed, research speed, organisation, compliance and so on. A modifier that is zero has a grey name and no value, so what applies stands out.
  - A table of resources: balance, produced, used, imported, exported.
- **History** (the second page of National Figures):
  - Twelve figures of your country month by month, ten years at most: manpower, divisions, factories, stability, war support, fuel and others. The mod writes them down on the first of each month, from the day it is active in a game.
  - A table lists the twelve with their newest month and the change in a month and in a year; a click on one draws it as a column graph with its highest and lowest month, the years under it, and a zoom that lets the columns start at the lowest month.

- **Top bar strip** (on every screen, in the empty middle of the top bar):
  - Chips drawn like the vanilla values: by default political power and command power per day, stability and war support per week, civilian factories with how many are free, military factories and dockyards with how many are idle, and fuel in store of capacity. The label is the tooltip.
  - An edit button beside the Records button opens a panel where you choose among eighteen values (consumer goods, manpower in the field and in training, the seven resource balances too). What does not fit is refused; Default brings the eight back; the choice is kept with your country.

Limits: the game gives script no list of templates, training lines, production lines or queues, so the pages have none; an army without a commander is not listed; equipment, buildings and resources that another mod adds do not appear.

## The Records

A window for playing the game as a story: the mod writes down what happens in your campaign, from the day it is active in a game. The Records button of the top bar or `Shift+J` opens it, `Escape` closes it.

- **War Diary**: a dated log. Wars declared and ended, capitulations, annexations, subjects, your faction, every state and every victory point taken or lost, changes of government, officers commissioned, promoted and decorated. Beside it the record in figures: how many wars, states, victory points, capitals, promotions and decorations since it began.
  - A line about a state or a victory point names the enemy and the general who had the most divisions there, and its button moves the camera to the place.
  - Six filters: everything, or one kind of line.
- **Officers**: every general and admiral with his portrait in one table that sorts by any column: skill, the four levels, traits, command, battles won and lost.
  - A click on an officer opens his file: his portrait, when he was commissioned and promoted, his battles, the states and victory points taken under him, his lines of the diary. An officer who has retired keeps his record.
  - Portraits are the game's own, for the named characters of the game. A general the game makes up when you recruit one shows the unknown leader: nothing lets a mod read his portrait.
  - Generals and admirals that other mods add are listed too, also those a mod or a focus gives their command later in the game. Their portraits show for the mods the build was made with (`tools/portraits_mods_table.py`); from any other mod they show the unknown leader.
  - **Decorations**: his medals side by side on his file. Award him the medals your country has in the game (Iron Cross and Knight's Cross for Germany, Victoria Cross for Britain and so on), by name and icon. For an officer they are a record only: no bonus and no cost.
- **Government**: the head of government with portrait and flag, the parties with their leaders and support, the laws in force, the cabinet, the high command, your faction with its members, your subjects. Each name with the day it took office.
- **Wars**: one row per enemy and one per finished war: since when, for how many days, a bar for the enemy's surrender progress, how it ended. Totals for all wars, and counters for aces.
  - A click on a war opens its file: the flags of both sides, the two heads of government with their portraits and parties, the days, your casualties, the states and victory points taken and lost, how close each side is to giving up, and the lines of the diary about that enemy.
- **State card**: beside the state view of a state you control: when it was taken and from whom.
- **Unit honours** (By Blood Alone): your divisions that stand in an enemy capital when it falls get a line in their own history, "Took part in the capture of ...". The Battle honours switch on the War Diary turns this off. The state card's button cites the divisions in a state the same way; for a citation the game lets you award a medal at its usual price. A division takes one such line a day.

Limits: no page can take typed text, so nothing can be renamed or annotated there; the game gives script no name of a division or a ship; a record starts when the mod is first active in a game; a line found by the daily comparison (a peace, a capitulation, an office, a victory point) carries the date of the day that ended; a battle that is won without the place changing hands is counted for the officer but has no line, because the game does not say where it was fought. Not yet seen in a test: battles counted per officer, a capitulation, landings and aces.

---

## Directory Architecture

This repository adheres to the standard single-root Hearts of Iron IV mod architecture:

```
hoi4-1440p-ui-mod/
|-- .git/                           # Git repository root
|-- descriptor.mod                  # Clausewitz engine descriptor
|-- thumbnail.png                   # Steam Workshop thumbnail (512x512)
|-- build.ps1                       # Core build and lifecycle engine
|-- assets/                         # Raw graphics and master art assets
|-- artifacts/                      # Packaged release archives (git-ignored)
|-- baseline/                       # Vanilla reference copies of overridden windows (dev-only)
|-- reference/                      # Captures of every screen, vanilla and reworked (dev-only)
|-- common/                         # Script of the manager pages only (generated; changes the checksum)
|-- gfx/                            # Textures built from vanilla assets
|-- interface/                      # GUI layout (.gui) and sprite (.gfx) files; mod1440_*.gui are generated
|-- localisation/                   # Texts of the manager pages (generated, one file per game language)
|-- tests/                          # Automated Pester test suites
|-- tools/                          # GUI inspection and baseline scripts (dev-only)
\-- wiki/                           # GitHub documentation wiki (roadmap, design rules)
```

---

## Development & Automation Commands

All lifecycle tasks are managed through `build.ps1`:

```powershell
# 1. Deploy mod to local Paradox Interactive Hearts of Iron IV mod folder
.\build.ps1 -Deploy

# 2. Configure zero-copy DevLink (instant hot-reload for live testing)
.\build.ps1 -DevLink

# 3. Validate syntax and bracket balance without deploying
.\build.ps1 -ValidateOnly

# 4. Run automated test suites (Pester)
.\build.ps1 -Test

# 5. Package clean release zip archive
.\build.ps1 -Package

# 6. Publish to Steam Workshop (Dry Run preview)
.\build.ps1 -PublishSteam -DryRun

# 7. Clean deployed mod files and temporary archives
.\build.ps1 -Clean
```

Screen work uses the scripts in `tools/`:

```powershell
# List the windows of a vanilla GUI file, or outline one window
.\tools\Show-GuiOutline.ps1 airselectionview.gui
.\tools\Show-GuiOutline.ps1 airselectionview.gui air_selection_view -All

# List the widget names the game code asks for around a window (shows whether it could display more data)
.\tools\Show-CodeNames.ps1 unitview.gui army_division_view

# Start (or extend) a screen's override file with untouched vanilla windows; saves their baselines
.\tools\New-OverrideFile.ps1 air_selection airselectionview.gui air_selection_view, airwing_selection_item

# List every value the mod changed, compared with the vanilla baseline
.\tools\Compare-Baseline.ps1 zz_1440p_air_selection.gui

# Refresh the baseline of a window, for example after a game update
.\tools\Export-VanillaBaseline.ps1 airselectionview.gui air_selection_view

# Write every file of the manager pages and the Records window (scripted GUIs) from the tables in the tools; a running game redraws them
python -I tools\build_managers.py
python -I tools\build_managers.py --check   # fails when a generated file was edited by hand or is stale

# Rebuild the textures that are enlarged copies of vanilla ones (needs Python with Pillow)
python tools\stretch_background.py
python tools\stretch_background.py --only ud_ --preview scratch\previews   # some of them, with before/after images

# Draw a window, or a whole screen (tools\scenes\<screen>.json), before any launch; output in scratch\previews
python -I tools\render_gui.py army_division_view --bounds
python -I tools\render_gui.py --scene army_selection --over
python -I tools\render_gui.py --scene division_details --state template   # another tab, or an opened dropdown

# Validation, tests and the scene render in one go (-InGame adds the unattended game check)
.\build.ps1 -Check army_selection

# Check in the game without a human, about two minutes: launch, new 1936 game, bring the screens up,
# capture and crop into scratch\checks, diff error.log, exit. It takes over the main screen meanwhile.
.\tools\Invoke-GameCheck.ps1 army_selection, air_selection
.\tools\Invoke-GameCheck.ps1 army_selection -Vanilla       # the same screen without the mod
.\tools\Invoke-GameCheck.ps1 army_selection -KeepRunning   # leave the game open to try tooltips and clicks
.\tools\Invoke-GameCheck.ps1 -All -Vanilla -SaveReference   # every known screen, stored under reference\vanilla (after a game update)
.\tools\Invoke-GameCheck.ps1 army_selection -SaveReference  # a finished screen, stored under reference\mod

# Find the recipe for a new screen: run a few steps in the open game and look at the capture (wiki\Game-Recipes.md)
.\tools\Invoke-GameSteps.ps1 -Start
.\tools\Invoke-GameSteps.ps1 -Reset -Steps '[{"key":"y","wait":1.2}]' -Region 0,60,560,420
.\tools\Invoke-GameSteps.ps1 -Stop
```

How each screen is brought up (the recipes in `tools/scenes/` and `tools/moves.json`) is described in [wiki/Game-Recipes.md](wiki/Game-Recipes.md).

Python 3 with Pillow is needed for the renderer and the texture script (`python -m pip install pillow`).

---

## Automated Testing

Unit tests are written with [Pester](https://pester.dev) and located in `tests/`. The render tests draw every window and scene in one `python -I tools/render_gui.py --batch` process and write the images to `scratch/test-renders/`; decoded textures are kept under `scratch/cache/textures/`. Execute tests using:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\tests\Run-Tests.ps1
```

---

## Author & License

- **Author**: TheCreepero