# Design Rules

Rules every reworked screen follows. Items marked **provisional** are fixed at the end of Phase 1 (see [Roadmap](Roadmap.md)), once they have been judged in game.

## Target

- 2560x1440 at 100% UI scale (`gui_scale=1.0`).
- No `size` may exceed 2560x1440. The test suite enforces this.
- **Provisional:** centred windows leave at least 100 px free above and below, so they are at most about 1240 px high.

## Overriding vanilla windows

- **Method: provisional.** Preferred: one small file per screen under `interface/` that contains only the reworked top-level windows. Fallback: a full copy of the vanilla file, edited in place. The Phase 1 override test decides, and also sets the file naming rule.
- **Widget names stay.** The engine binds data to widgets by `name`, looked up inside their parent. A reworked window keeps every named vanilla widget, with the same element type, under the same named parent. Position, size, font and sprite are free to change.
- **Export the baseline first.** Before reworking a vanilla window, run `tools/Export-VanillaBaseline.ps1 <file.gui> <window>`. It saves the vanilla text under `baseline/`; the test suite compares the mod's window against it.
- **Mod-only windows** (no vanilla counterpart) are named `mod1440_*`.
- **Nothing under `common/`, `events/`, `history/` or `map/`.** Those folders are part of the game checksum; `interface/` and `gfx/` are not.

## Fonts

Larger text means choosing a larger font that vanilla already ships. Sizes in use in vanilla GUI files:

| Use | Vanilla fonts |
|---|---|
| Body text | `hoi_16mbs`, `hoi_18mbs` |
| Emphasis | `hoi_18b`, `hoi_20b`, `hoi_20bs` |
| Headers | `hoi_22tech`, `hoi_24header`, `hoi_30header`, `hoi_33`, `hoi_36header` |

**Provisional:** move each text one step up within its row of the table. The final mapping is set in Phase 1.

## Lists and scrolling

- `slotsize.width` of a grid equals the width of the entry window that fills it. The link between a grid and its entry window lives in game code, so add the pair to `$entryPairCases` in `tests/GuiInvariants.Tests.ps1`.
- `scroll_wheel_factor` is a whole multiple of the row height. The test suite enforces this for every scroll container with one grid.
- Dropdowns set `expandedOnTop = yes`.

## Sprites and backgrounds

- New sprites are named `GFX_1440p_*` and declared in `interface/1440p_ui.gfx`. Vanilla sprite names are never redefined, because that changes every screen that uses them.
- **No AI-generated images.** Every image is built from vanilla game assets.
- For a window that needs a larger background, use the first option that gives a clean result:
  1. An existing vanilla tiled window sprite, used as it is (for example `GFX_tiled_window_1b_thin_border`).
  2. A new tiled sprite declared in `interface/1440p_ui.gfx` that points at an existing vanilla texture file. No new image file.
  3. A background composed from several vanilla sprites: a tiled base plus vanilla frames, header bars and boxes placed as separate icons.
  4. A script that copies bands of pixels from the vanilla bitmap into a larger texture, repeating the plain areas. Output goes to `gfx/interface/1440p_ui/`.
- If none of the four looks clean, the window keeps its vanilla size and only its lists and fonts are reworked.

## Recipe for a screen phase

1. **Inventory.** `tools/Show-GuiOutline.ps1 <file.gui>` lists the windows; add a window name and `-All` for its widgets, fonts and sprites. Note which backgrounds are bitmaps and which widgets the engine positions itself.
2. **Layout proposal.** Target sizes, panel regions, row heights and font choices as a short text mock-up, agreed before any file is written.
3. **Baseline.** `tools/Export-VanillaBaseline.ps1 <file.gui> <window> [<window> ...]`.
4. **Background.** Only for bitmap backgrounds: work down the four options above and declare the sprite.
5. **Build** the `.gui` file.
6. **Static checks.** `build.ps1 -ValidateOnly` and `build.ps1 -Test`.
7. **Game check.** Vanilla playset with only this mod, launched with `-debug`, at 2560x1440. Open the screen with a late-game save, scroll every list to the end, open every dropdown, check tooltips and click targets. No line in `logs/error.log` may name a mod file.
8. **Close.** Update the status in [Roadmap](Roadmap.md), the README and the Workshop description; raise `version` in `descriptor.mod`.
