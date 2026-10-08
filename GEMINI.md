# HOI4 1440p UI Mod - Development & Agent Rules

## 1. Mod Architecture & Workspace Layout
- **Mod Role**: High-resolution UI optimization mod expanding Hearts of Iron IV windows, grids, and dropdowns for 1440p (`2560x1440`) and higher displays.
- **Checksum Invariant**: Mod content lives only in `interface/` (`.gui`, `.gfx`) and `gfx/` (textures). Neither is part of the gameplay checksum, which keeps the mod 100% compatible with Ironman, achievements, and multiplayer. `common/`, `events/`, `history/` and `map/` stay empty.
- **Phased Work**: The mod is built one screen per phase. Before starting or continuing a phase, read `wiki/Roadmap.md` (phase list, status, risks) and `wiki/Design-Rules.md` (size limits, fonts, backgrounds, the per-screen recipe).
- This project follows a unified single-root mod layout:
  - **Workspace & Git root**: `C:\dev\hoi4-1440p-ui-mod` (Git repository root containing `.git/`)
  - All mod descriptors (`descriptor.mod`), build tools (`build.ps1`), interface definitions (`interface/`), content (`common/`), tests (`tests/`), and agent configurations (`GEMINI.md`) reside at the project root.
  - `tools/` (inspection and baseline scripts) and `baseline/` (vanilla reference copies of overridden windows) are dev-only and excluded from packages.
  - Release archives (`artifacts/`) and scratch scripts (`scratch/`) are git-ignored.

## 2. Clausewitz GUI & File Format Invariants
- **UTF-8 Without BOM**: All Clausewitz script and interface files (`.mod`, `.txt`, `.gui`, `.gfx`) must be saved in UTF-8 without BOM. Never use standard Windows PowerShell `Set-Content -Encoding UTF8` because it writes a BOM (`\ufeff`). Always write text files using:
  `[System.IO.File]::WriteAllText($path, $content, [System.Text.UTF8Encoding]::new($false))`
- **Hardcoded C++ Widget Bindings**: The Clausewitz engine binds gameplay data exclusively to predefined widget `name = "..."` attributes. Never rename vanilla element names inside overridden windows, and keep each named widget under its vanilla parent.
- **One Override File Per Screen**: Put a screen's reworked top-level windows in `interface/zz_1440p_<screen>.gui` and leave the vanilla file alone. The game uses the last loaded definition of a window name and loads `.gui` files in name order, so the `zz_` prefix is what makes the override win.
- **Baseline Before Rework**: Before reworking a vanilla window, save its vanilla text with `tools/Export-VanillaBaseline.ps1 <file.gui> <window>`. The test suite fails for an overridden window without a baseline, and for any named vanilla widget that is missing or moved.
- **Sprite Naming**: Name new sprites `GFX_1440p_*` and declare them in `interface/1440p_ui.gfx`. Leave vanilla sprite names untouched.
- **Art From Vanilla Assets**: Build every image from vanilla game assets, following the order of options in `wiki/Design-Rules.md`. AI-generated images are not allowed anywhere in the mod.
- **Key-Value Syntax**: `descriptor.mod` must strictly follow `key="value"` without spaces around the `=` operator.
- **Bracket Balance**: Curly braces `{}` and double quotes `""` must always be strictly balanced.
- **Usable Slot Width & Scroll Math**: In scrollable windows with `verticalScrollbar = "right_vertical_slider"`, match `slotsize.width` to the entry `containerWindowType.width`, and set `scroll_wheel_factor` to an integer multiple of `slotsize.height`.
- **In-Game Live Reloading**: Launch the game with `-debug` and use `reload gui` or `reload interface/<name>.gui` in the in-game console (`~`) to hot-reload layout changes without restarting.
- **Vanilla Lookups**: Inspect vanilla `.gui` structure with `tools/Show-GuiOutline.ps1 <file.gui> [<window>] [-All]` instead of guessing. For `.gui`/`.gfx` syntax and element templates, read `.agents/skills/hoi4-gui-modding/SKILL.md`. For other vanilla facts, use the user-level `hoi4-vanilla-lookup` skill.

## 3. Build & Automation Protocol
- Always run pre-flight syntax and descriptor checks before declaring work complete:
  `powershell -File .\build.ps1 -ValidateOnly`
- Run the full automated Pester test suite:
  `powershell -File .\build.ps1 -Test`
- Use `.\build.ps1 -DevLink` for zero-copy live editing directly from the repository.
- Use `.\build.ps1 -Package` to verify that release packaging strictly excludes `.git`, `.github`, `.vscode`, `tests`, `wiki`, and developer scripts.

## 4. Git & Commit Guidelines
- Do not commit to the Git repository unless explicitly instructed by the user. The user prefers to review changes before committing.
- **Git Verification Invariant**: After completing changes, always verify `git status` to ensure the working tree reflects expected changes.