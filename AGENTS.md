# HOI4 1440p UI Mod - Agent Rules

Shared rules for every mod in this tree (file encodings, build commands, engine knowledge, git) are in the Modding Manager's `../../AGENTS.md`; `CLAUDE.md` and `GEMINI.md` import this file. This file holds the short form of the rules that always apply; `wiki/Working-Rules.md` is the long form, and the `/phase` skill reads the pages a phase needs at its start.

## What this mod is
- A high-resolution UI mod that redesigns Hearts of Iron IV screens for 1440p and higher: larger and regrouped panels, a place for every value a screen already has, larger text, hotkeys for existing buttons. Interface and texture files only (`interface/`, `gfx/`, the texts of its captions under `localisation/`), outside the game's checksum: Ironman and achievements stay available.
- The manager pages and the Records window (Milestones D and E, versions 1.5 to 1.9 of this mod) were split out on 2026-10-21 into the standalone mod **HOI4 Manager Pages** (`../hoi4-manager-pages`, its own repository; user decision). Nothing of this mod depends on it and nothing of it on this mod; `events/`, `history/`, `map/` and `common/` stay empty, and `tests/GuiInvariants.Tests.ps1` holds the line. That mod reserves Shift+M and Shift+J; no screen here uses them (`tools/hotkeys.json`).
- `tools/` (inspection, render and harness scripts), `baseline/` (vanilla copies of overridden windows), `reference/` (captures of every screen) and `scratch/` (git-ignored) are dev-only and never ship.

## Mod invariants
- The mod is built one screen per phase through the `/phase <id>` skill, with four roles (orchestrator, `designer`, `builder-screen`, `game-checker`, defined under `.claude/agents/`; `builder-script` for a fix round whose cause is not yet known) and the user's three gates: the design page, the launches, the final report (Working-Rules section 7). A small phase (`refine`, effort S) skips the designer: the orchestrator writes the layout itself (Workflow, "The short path"). The notes' Proposal, Build, Game checks and Fix rounds sections are generated from the handoff files by `tools/phase_notes.py`.
- Never rename a vanilla widget or change its element type inside an overridden window: the code binds by `name` [GUW-001]. A vanilla widget may move into a `mod1440_*` container only because this machine's `hoi4.exe` is patched for nested lookups (`wiki/Engine-Facts.md` W34); after a game update run the Manager's `Scripts\Executable\Set-HoiRecursiveLookups.ps1 -Status` and patch again before a game check.
- A redesign adds no live value and no working button: the engine fills only the widgets its code asks for (`wiki/Design-Rules.md`, "What a redesign can add"). Anything that needs script belongs in HOI4 Manager Pages, never here.
- One override file per screen, `interface/zz_1440p_<screen>.gui`, started with `tools/New-OverrideFile.ps1` and laid out from `scratch/phases/<id>/layout.json` by `tools/apply_layout.py` (the mock-up is drawn from the same file); the links the code makes go in `tools/gui-links.json`; every edit is reviewed with `tools/Compare-Baseline.ps1` and nothing but intended changes may appear.
- New sprites are `GFX_1440p_*` in `interface/1440p_ui.gfx`; vanilla sprite names stay, with the one exception of `interface/zz_1440p_vanilla_sprites.gfx` [LOAD-012]. Every image is built from vanilla assets; AI-generated images are not allowed anywhere.
- Captions of the reworked screens are the mod's own text keys (`MOD1440_*`) in `localisation/<lang>/1440p_screens_l_<lang>.yml` (UTF-8 with BOM, every language), and the air region's channel numbers in `localisation/<lang>/replace/1440p_air_region_l_<lang>.yml`; a test checks that every key a `zz_*.gui` file names has an English text.
- Render before asking (`python -I tools/render_gui.py --scene <screen>`), and never start the game, or let an agent start it, without the user's grant for exactly those launches; a check saves nothing, stays in January 1936 and runs at most ten days with `autosave.hoi4` copied and hashed. Log every launch in `wiki/phases/<id>.md`.
- `tools/GameHarness.ps1` simulates input and copies the screen to PNG, nothing more (Windows Defender once flagged it); image conversion belongs in the Python tools. If the antivirus flags a tool, tell the user; never disguise it, add exclusions or restore from quarantine.
- Never change `hoi4.exe` on your own: a patch is the user's decision and goes through the Manager's scripts. What a launch teaches goes into the register with an alias of its Engine-Facts section (`-Alias 1440p:W31`), then `Export-HoiKnowledge.ps1 -Repo hoi4-1440p-ui-mod`.

## Commands beyond build.ps1
- `powershell -File .\build.ps1 -Check <screen>` (validation, the Pester suite and the scene render; `-InGame` adds the unattended game check); `tools/Invoke-GameCheck.ps1`, `tools/Invoke-GameSteps.ps1`, `tools/Show-GuiOutline.ps1`, `tools/Compare-Baseline.ps1`, `tools/New-OverrideFile.ps1`; `python -I tools/render_gui.py`, `tools/mockup.py <layout>` (the mock-up from the layout file), `tools/apply_layout.py <layout> [--compare <file>]` (the override file from it, and the bitmaps of its steel pieces), `tools/lint_layout.py <layout>` (the layout against the ruleset of `wiki/Design-Language.md`), `tools/ux_audit.py <id>` (contrast, fonts, small buttons, squinted figures for the design page), `tools/make_design_page.py <id>` (the design page from the handoff files), `tools/phase_notes.py <id>` (the generated sections of the phase notes), `tools/crop_capture.py` (an evidence cut of a capture), `tools/check_playset.py` (where the launcher's playset meets the reworked screens).

## Read when
| Task | Read |
|---|---|
| Starting or continuing a phase | the `/phase` skill, which reads `wiki/Workflow.md`, `wiki/Roadmap.md`, `wiki/Design-Rules.md`, `wiki/Working-Rules.md` and the phase notes |
| Designing a screen | `wiki/Design-Language.md` (the design ruleset: the steel look, spacing, fonts by role, fixed places, hotkeys; `tools/lint_layout.py` checks a layout against it), `wiki/Workflow.md` "Handoff files" (`layout.json`), the bindings reports by window (`window-bindings-all.md` has every window; never the decompiled code inside a phase) |
| Seeing a result, a game check, a recipe | Working-Rules section 3, `wiki/Game-Recipes.md`, `reference/README.md` |
| Another mod in the user's playset | `wiki/Compatibility.md` |
| What the engine does | `wiki/Engine-Facts.md` by row (W34, X66), or `Find-HoiKnowledge.ps1 -Id <row>` |
| Reading `hoi4.exe` | the Manager's `Scripts\Executable\README.md` |
| A manager page or the Records | the mod HOI4 Manager Pages (`../hoi4-manager-pages`): its `AGENTS.md`, `wiki/Scripted-GUIs.md` and `/pages-phase` skill; this repository holds nothing of them since 2026-10-21 |

## Engine Knowledge
- Engine facts live in the Modding Manager's register, reached through the user-level `hoi4-modding-knowledge` skill: search it before a new kind of file and before asking for a game launch, cite ids here, never write a fact into this repository. This mod's page `wiki/Engine-Facts.md` is generated from the register, and its row ids (W14, X23) are record aliases, so both forms resolve.
- Topics this mod leans on: `gui-widgets`, `gui-layout`, `gui-sprites-and-fonts`, `localisation`, `loading-and-overrides`, `game-automation`, `engine-limits`.
- The interface skill is the user-level `hoi4-gui-modding`; this repository keeps no copy. `tests/Knowledge.Tests.ps1` runs the register's audit; it is a copy the Manager keeps current.
