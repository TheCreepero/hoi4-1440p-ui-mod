# Phase <id>: <screen name>

Copy this file to `wiki/phases/<screen>.md` when a phase starts (stage 1 of [Workflow](Workflow.md)) and fill it in as the phase goes: the orchestrator writes Scope, Roles and handoffs, Decisions and Close; the designer's work lands in Inventory and Proposal; the builder writes Build and the Fix rounds; the game checker adds the rows of Game checks. The [Roadmap](Roadmap.md) keeps only the status and a link here.

## Scope

- Vanilla file and windows:
- What the vanilla screen crams or hides (from the screenshot):
- Out of scope:

## Roles and handoffs

- Handoff folder: `scratch/phases/<id>/` (not in the repository)
- Builder: `builder-screen` or `builder-script`, and why
- Design page: link, and the date of each round
- Contracts written (hotkeys, shared rows, shared files): yes / none needed
- Worktrees (several screens at once): paths, or "main tree"

## Inventory

- Vanilla reference: `reference/vanilla/<screen>.jpg` and `-panel.png` exist and show the state the redesign is about. If not: the recipe in `tools/scenes/<screen>.json` ([Game Recipes](Game-Recipes.md)), then `tools/Invoke-GameCheck.ps1 <screen> -Vanilla -SaveReference`:
- Where each window sits (`at`, measured with `render_gui.py --verify`) and the `expect` widgets:
- `tools/Show-GuiOutline.ps1 <file> <window> -All` done for:
- `tools/Show-GuiOutline.ps1 <file> <window> -Comments`: sizes set in code, grid-computed widths:
- `tools/Show-CodeNames.ps1 <file> <window>`: names marked `+` (data the code could fill):
- Lists and their rows (added to `tools/gui-links.json`):
- Bitmap backgrounds and which option of the Design Rules applies:
- Engine facts this screen depends on that are still **untested** in [Engine Facts](../Engine-Facts.md):

## Proposal

What the player should see at once, then the numbers: panel sizes, row heights, column widths, fonts. Attach the scene render (`python -I tools/render_gui.py --scene <screen>`) and, for width judgements, the render over the vanilla screenshot (`--over`).

| Panel or column | Vanilla | Proposed | Why |
|---|---|---|---|
| | | | |

Additions, each with the row of "What a redesign can add" that allows it:

- 

## Decisions

Dated, one line each: what was agreed, what was sent back and why. The user's answers to the design page's questions go here, with the date (they are also in `decisions-final.json`).

- 

## Build (<date>)

Status: built and checked by render and tests; not seen in game.

- What was built:
- Deviations from the design, each with its reason:
- Not seen in game (what only a launch can show, and the fallback if it fails):
- Game check: `tools/Invoke-GameCheck.ps1 <scene> [...]`
- Checklist for the game checker (also in `tools/scenes/<scene>.json`):
  1. 

## Game checks

One row per launch. Build = `git rev-parse --short HEAD` plus "+dirty" when uncommitted, or the file hash. By = `game-checker`, the orchestrator, or the user (their own game and playset).

| # | Date | Build | By | Checked | Result | Screenshot | Taught |
|---|---|---|---|---|---|---|---|
| 1 | | | | | | `scratch/checks/...` | |

Not seen in game (states the save did not show):

- 

## Fix rounds

One line per fix, under a heading per round: issue, cause, fix, what the re-test should look at. Findings from the user's own game name their screenshot.

### Fix round 1 (<date>)

- 

## Close

- [ ] Roadmap status and link
- [ ] README "Reworked screens"
- [ ] Workshop description
- [ ] `version` in `descriptor.mod`
- [ ] Engine Facts rows confirmed or added
- [ ] Scene file final (`tools/scenes/<screen>.json`)
- [ ] Finished screen stored: `tools/Invoke-GameCheck.ps1 <screen> -SaveReference` (`reference/mod/`)
