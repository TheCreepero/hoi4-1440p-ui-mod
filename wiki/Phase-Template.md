# Phase <id>: <screen name>

Copy this file to `wiki/phases/<screen>.md` when a phase starts and fill it in as the phase goes. The [Roadmap](../Roadmap.md) keeps only the status and a link here.

## Scope

- Vanilla file and windows:
- What the vanilla screen crams or hides (from the screenshot):
- Out of scope:

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

Dated, one line each: what was agreed, what was sent back and why.

- 

## Game checks

One row per launch. Build = `git rev-parse --short HEAD` plus "+dirty" when uncommitted, or the file hash.

| # | Date | Build | Checked | Result | Screenshot | Taught |
|---|---|---|---|---|---|---|
| 1 | | | | | `scratch/checks/...` | |

Not seen in game (states the save did not show):

- 

## Close

- [ ] Roadmap status and link
- [ ] README "Reworked screens"
- [ ] Workshop description
- [ ] `version` in `descriptor.mod`
- [ ] Engine Facts rows confirmed or added
- [ ] Scene file final (`tools/scenes/<screen>.json`)
- [ ] Finished screen stored: `tools/Invoke-GameCheck.ps1 <screen> -SaveReference` (`reference/mod/`)
