---
name: hoi4-gui-modding
description: >-
  Syntax rules, layout model, element templates and the tools for reworking Hearts of Iron IV
  (Clausewitz engine) interface files (.gui, .gfx) in this mod. Use when creating, editing,
  positioning or troubleshooting windows, buttons, text boxes, lists, grids and dropdowns, and when
  deciding what a redesign can and cannot change.
---

# Hearts of Iron IV GUI Modding Skill

Facts here carry the id of their row in `wiki/Engine-Facts.md` where one exists (for example "L1"); a fact without an id is file syntax, which the parser checks. Anything the register marks **untested** is a guess until a launch confirms it.

## 1. What this mod changes, and what it cannot

- Only `interface/*.gui`, `interface/*.gfx` and `gfx/` textures (L8). No `common/` (scripted GUIs change the checksum and are not used).
- One override file per screen, `interface/zz_1440p_<screen>.gui`, holding reworked copies of single top-level windows; the vanilla file stays (L1, L2, L3).
- Every named vanilla widget stays, with its element type, under its vanilla parent (W1). Position, size, font and sprite are free.
- The code fills widgets by name; a new name stays empty (W2). A redesign can move, resize, regroup, caption (`text = "<vanilla key>"`, W8), and add hotkeys (`shortcut`, W5), but not add live values or working buttons. `tools/Show-CodeNames.ps1 <file> <window>` lists what the code asks for (W3).
- Links the code makes (which row fills which list or grid, which `@variables` a window needs) go into `tools/gui-links.json` (S3, S4, S6, L6).

## 2. Graphic declarations (`interface/*.gfx`)

```pdx
spriteTypes = {
    spriteType = {                         # plain image, drawn at its texture size (G2)
        name = "GFX_1440p_UV_unit_entry_bg"
        texturefile = "gfx/interface/1440p_ui/uv_unit_entry_bg.dds"
        noOfFrames = 2                     # frames side by side; a background button switches frame when selected (G7)
    }
    corneredTileSpriteType = {             # nine-slice: takes the window's size, keeps borderSize, tiles the centre (G1, G3)
        name = "GFX_1440p_UV_unit_list_header"
        size = { x = 640 y = 35 }          # the size an iconType draws it at
        textureFile = "gfx/interface/unitcontrol/unit_list_header.dds"
        borderSize = { x = 24 y = 12 }
        tilingCenter = yes
    }
    progressbartype = {                    # any size; the gradient textures stretch (G6)
        name = "GFX_1440p_UV_bar_org"
        textureFile1 = "gfx/interface/navieslist_bar_org.dds"
        textureFile2 = "gfx/interface/navieslist_bar_bg.dds"
        size = { x = 48 y = 9 }
        effectFile = "gfx/FX/progress.lua"
        horizontal = yes
    }
}
```

- New sprites are named `GFX_1440p_*` and declared in `interface/1440p_ui.gfx`; vanilla sprite names are never redefined.
- Textures: uncompressed 32-bit DDS written by Pillow loads (G9). Every image is built from vanilla assets with `tools/stretch_background.py`; the order of options is in `wiki/Design-Rules.md`.
- A tiled sprite on a texture with decorations away from its corners, or a repeating pattern, breaks (G8). Tiled panels look 3 to 5 px smaller than their size because of their soft edge (G5).

## 3. Layout model (`interface/*.gui`)

Every widget is placed inside its parent's rectangle:

- `position = { x y }` is the offset from the anchor point of the parent chosen by `orientation` (`UPPER_LEFT` default, `UPPER_RIGHT`, `LOWER_LEFT`, `LOWER_RIGHT`, `CENTER`, `CENTER_UP`, `CENTER_DOWN`, `CENTER_LEFT`, `CENTER_RIGHT`); `origo` picks which point of the widget sits on the anchor (`upper_left` default, `center`, ...).
- `size = { width height }` for windows and text boxes, `size = { x y }` for list boxes and tiled buttons; `100%` means the parent's extent.
- A size commented `set in code` is a maximum: the engine sizes the window to its content (S1), and a child commented "set in code to match the window size" takes the parent's height (S2).
- `clipping = yes` cuts children at the edge; a list box always cuts off anything wider than itself, and its frame needs the scrollbar gutter (S5).
- `positionType` blocks are alternative positions the code applies in another state; they move with their widget (S8).
- `rotation = 1.5708` turns a bar 90 degrees anticlockwise about its top-left corner (S13).
- Widths computed from a grid (`slotsize.width` times the slots plus twice the grid's `position.x`) depend on the player's DLC (S9).

### Element templates

```pdx
containerWindowType = {
    name = "army_division_list_view"
    position = { x = 1 y = 2 }
    size = { width = 670 height = 760 }        # height set in code, but initial value here is used for max allowed height
    Orientation = upper_left
    clipping = no
    background = { name = "Background" quadTextureSprite = "GFX_tiled_window_1b_thin_border" }
}

instantTextBoxType = {
    name = "unit_name"
    position = { x = 311 y = 3 }
    font = "hoi_20b"                           # vanilla fonts only; sizes in wiki/Design-Rules.md
    maxWidth = 259                             # wider text is cut off with an ellipsis (W10); width = sum of xadvance (W11)
    maxHeight = 25
    format = left                              # left, center, right
    fixedsize = yes
}

buttonType = {
    name = "btn_unassign"
    position = { x = 610 y = 0 }
    spriteType = "GFX_UV_btn_unassign"
    clicksound = click_default
    shortcut = "shift+u"                       # one line per key; a key, ctrl+x, or a chord ctrl+g+s (W5)
    pdx_tooltip = "UNASSIGN_TOOLTIP"
}

iconType = {
    name = "bar_org"
    spriteType = "GFX_1440p_UV_bar_org"
    position = { x = 8 y = 6 }
    frame = 1
    alwaystransparent = yes                    # clicks pass through, for a caption over a button
}

gridBoxType = {
    name = "divisions_grid"
    position = { x = 8 y = 0 }
    size = { width = 351 height = 100% }
    slotsize = { width = 350 height = 50 }     # width equals the entry window's width (S6)
    max_slots_horizontal = 1
    format = "UPPER_LEFT"
}

dropDownBoxType = {
    name = "divisions"
    position = { x = 37 y = 2 }
    size = { width = 200 height = 30 }
    expandButton = { name = "expand_button" position = { x = 0 y = -2 } spriteType = "GFX_change_template_button" }
    expandedWindow = {                         # opens at show_position, above the rest of the window (S11)
        name = "expanded_window"
        position = { x = 0 y = -600 }
        show_position = { x = 0 y = 18 }
        size = { width = 382 height = 615 }
        verticalScrollbar = "right_vertical_slider"
        scroll_wheel_factor = 50               # a whole multiple of slotsize.height
        margin = { top = 7 bottom = 7 right = 6 }
        background = { name = "Background" quadTextureSprite = "GFX_tiled_window_1b_thin_border" }
        gridBoxType = { name = "divisions_grid" ... }
    }
}
```

Rules the test suite enforces: UTF-8 without BOM, balanced braces and quotes, no size over 2560x1440, `scroll_wheel_factor` a multiple of the row height, slot width equal to the entry width, rows no wider or taller than their list, every `@variable` defined, every `GFX_1440p_*` sprite declared, a baseline for every overridden window, no vanilla widget missing or moved, texts that fit their `maxWidth`, hotkeys that collide with nothing on the same screen.

## 4. Seeing a layout

| Step | Command |
|---|---|
| Outline a vanilla or mod window | `tools/Show-GuiOutline.ps1 <file> <window> -All`; `-Comments` for sizes set in code |
| What the code fills | `tools/Show-CodeNames.ps1 <file> <window>` |
| Start a screen (baseline, override file, scene file) | `tools/New-OverrideFile.ps1 <screen> <file> <window> ...` |
| What changed against vanilla | `tools/Compare-Baseline.ps1 zz_1440p_<screen>.gui [-Group]` |
| Draw a window or a screen with real textures and fonts | `python -I tools/render_gui.py <window> --bounds`, `--scene <screen> --over`, `--expand <dropdown>` |
| Everything before a game check | `build.ps1 -Check <screen>` |
| Check in the game, unattended (restart, new game, recipe, capture, crop) | `tools/Invoke-GameCheck.ps1 <screen> [-Vanilla] [-KeepRunning]`, `-All` for every scene |
| Where a named widget sits on the screen | `python -I tools/render_gui.py --scene <screen> --locate <window>/<widget>` |
| Is a widget visible in a capture, and how far off is the layout | `python -I tools/render_gui.py --scene <screen> --verify <capture.png>` |
| What a screen looks like, vanilla or reworked | `reference/vanilla/<screen>.jpg` (frame) and `-panel.png` (lossless panel); index in `reference/README.md` |
| Find the recipe for a new screen | `tools/Invoke-GameSteps.ps1 -Start`, then `-Steps '<json>' [-Region x,y,w,h]`; method in `wiki/Game-Recipes.md` |

The renderer draws what the engine facts marked confirmed or provisional describe; widgets the code positions are drawn where the file puts them, and the scene file's `hide` and `place` lists correct the known cases.

## 5. In the game (needs `-debug`)

The game re-reads no `.gui`, `.gfx` or texture file while it runs, so a change is seen only after a restart (H3, H4). `tools/Invoke-GameCheck.ps1` does the restart and the capture without a human.

| Command or key | Effect |
|---|---|
| `reloadinterface`, `reload <file>.gui` | answer "reloaded" but change no overridden window (H3) |
| `reload_textures [filter]` | reports a count but a changed mod texture keeps its old look (H4) |
| `guibounds` (alias `gui`) | draws 1280x720 and 1600x900 guide rectangles, not widget bounds (H5) |
| `tag <TAG>` | switches the played country |
| `resign` | end screen, then Quit returns to the main menu (H13) |
| F11 | writes `Documents\Paradox Interactive\Hearts of Iron IV\Screenshots\hoi4_<n>.png`, in a running game only (H6) |
| `console_history.txt` in the game folder | every command the console ran, rewritten at once (H10) |
| `error.log` | `Documents\Paradox Interactive\Hearts of Iron IV\logs\error.log`, rewritten per launch; about 50 vanilla lines (H9) |
