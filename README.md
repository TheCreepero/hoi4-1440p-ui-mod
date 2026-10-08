# HOI4 1440p UI Mod

High-resolution UI optimization mod for Hearts of Iron IV targeting 1440p (2560x1440) and higher displays.

## Overview

- **Game**: Hearts of Iron IV
- **Supported Version**: `1.19.*`
- **Mod Version**: `1.0`
- **Tags**: Graphics, Utilities, Fixes
- **Requires**: 2560x1440 or higher at 100% UI scale
- **Ironman & Achievements**: Compatible (only `interface/` and `gfx/` files, which are outside the game checksum)
- **Status**: In development, one screen at a time. See [wiki/Roadmap.md](wiki/Roadmap.md).

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
|-- common/                         # Kept empty: the mod stays checksum-neutral
|-- gfx/                            # Textures built from vanilla assets
|-- interface/                      # GUI layout (.gui) and sprite (.gfx) files
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

Screen work uses two more scripts:

```powershell
# List the windows of a vanilla GUI file, or outline one window
.\tools\Show-GuiOutline.ps1 airselectionview.gui
.\tools\Show-GuiOutline.ps1 airselectionview.gui air_selection_view -All

# Save the vanilla text of a window before reworking it
.\tools\Export-VanillaBaseline.ps1 airselectionview.gui air_selection_view
```

---

## Automated Testing

Unit tests are written with [Pester](https://pester.dev) and located in `tests/`. Execute tests using:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\tests\Run-Tests.ps1
```

---

## Author & License

- **Author**: TheCreepero