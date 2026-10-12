# HOI4 1440p UI Mod

High-resolution UI mod for Hearts of Iron IV that redesigns screens for 1440p (2560x1440) and higher displays, and adds manager pages that fill the free width with tables and figures of your country.

## Overview

- **Game**: Hearts of Iron IV
- **Supported Version**: `1.19.*`
- **Mod Version**: `1.5`
- **Tags**: Graphics, Utilities, Fixes
- **Requires**: 2560x1440 or higher at 100% UI scale
- **Ironman & Achievements**: Not compatible since version 1.5. The manager pages are scripted GUIs, and their script under `common/` changes the game checksum. In multiplayer every player needs the mod. The pages show values and change nothing in the game.
- **Status**: In development, one screen at a time. See [wiki/Roadmap.md](wiki/Roadmap.md).
- **Tested with**: the vanilla game only. Behaviour next to other mods is untested.

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

## Manager Pages

Pages of the mod's own that stand beside a vanilla panel and use the width of the screen for values the game shows nowhere in one place. `Shift+M` shows and hides the page of the open tab. They show values of your own country and change nothing in the game.

- **Army Readiness** (beside Recruit & Deploy, open by default):
  - Manpower: free, in training, in the army, navy and air force, needed by garrisons.
  - Equipment: for sixteen kinds of land equipment the stock, what the divisions in the field hold and what they need, with a bar. A shortage is red.
  - Army: divisions, battalions, army experience, divisions below 75% strength and below 50% organisation.
  - Armies: one row per general with troops: divisions, battalions, divisions fighting, planning, the worst equipped kind of equipment, divisions by kind.
- **States** (beside Construction, opened with `Shift+M`):
  - One row per state you control: free building slots, the levels of nine buildings, seven resources, population, and compliance and resistance for occupied states.
  - A click on a column head sorts, a second click turns the order. Three choices narrow the list: cores, occupied, with free slots.
  - A click on a state moves the camera there and hides the page.
- **National Figures** (opened from Politics with `Shift+M` or the button in its title strip):
  - The summed modifiers of your country, 93 of them in six groups: what all laws, spirits, advisors and technologies together add to factory output, construction speed, research speed, organisation and so on. A modifier that is zero is left blank.
  - Factories and how many are free, fuel, party popularity, and a table of resources: balance, produced, used, imported, exported.
- **History** (the second page of National Figures):
  - Twelve figures of your country month by month as a column graph, ten years at most: manpower, divisions, factories, stability, war support, fuel and others. The mod writes them down on the first of each month, from the day it is active in a game.

Limits: the game gives script no list of templates, training lines, production lines or queues, so the pages have none; an army without a commander is not listed; equipment, buildings and resources that another mod adds do not appear.

---

## Directory Architecture

This repository adheres to the standard single-root Hearts of Iron IV mod architecture:

```
C:\dev\hoi4-1440p-ui-mod/
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

# Write every file of the manager pages (scripted GUIs) from the tables in the tool; a running game redraws them
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

Unit tests are written with [Pester](https://pester.dev) and located in `tests/`. Execute tests using:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\tests\Run-Tests.ps1
```

---

## Author & License

- **Author**: TheCreepero