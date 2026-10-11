# Design Rules

Rules every reworked screen follows, what a redesign can and cannot add, and what the first screens taught us about the engine. Items marked **provisional** have not been judged in game yet; the register of every engine fact with its status is [Engine Facts](Engine-Facts.md), and each phase keeps its own notes under `wiki/phases/` (template: [Phase Template](Phase-Template.md)).

## Target

- 2560x1440 at 100% UI scale (`gui_scale=1.0`).
- No `size` may exceed 2560x1440. The test suite enforces this.
- Panels docked at the top left may run down to about y 1130. The A1 list ends there and leaves the bottom bar free.
- **Provisional:** centred windows leave at least 100 px free above and below, so they are at most about 1240 px high. First judged in B1.

## What a redesign can add

A screen is re-laid out around what the player wants to see at once, not only enlarged. The engine limits what "new" can mean. Checked on game 1.19.3.

| Change | Possible | How, and the limit |
|---|---|---|
| Move, resize and regroup panels; dock windows side by side | Yes | Values in the `.gui` file |
| Give each existing value its own place: full names, a column per status, larger bars | Yes | Larger art is built from vanilla assets |
| Hotkeys, including key chords | Yes | A `shortcut` line on a button the game already has |
| Fixed text and icons: column captions, legends, static tooltips | Yes | A vanilla text key needs no file; new text needs a file under `localisation/` |
| Stat rows as tiles: a grid with two or more columns, a wrapped label over a larger value | Yes | `max_slots_horizontal` and `slotsize` of the grid, layout of the row window ([Engine Facts](Engine-Facts.md) W16); labels that vanilla cuts can be shown whole |
| Tab hotkeys | Yes | `shortcut` on the tab buttons (W19) |
| Cards, panels, grouped headers | Yes, as sibling backgrounds | A background drawn behind the widgets; the widgets stay under their vanilla parent (W15) |
| New live values the screen does not show today | No | The game fills only the widgets its code asks for |
| A value shown in two places | No | A second widget with the same name is dropped (W14) |
| Wrapping widgets in a new container (cards that own their content) | No | The code finds a widget only among the children of its vanilla parent (W15) |
| Showing two tabs at once | No | Duplicate tab containers are dropped (W14), and the code hides the other tab's container |
| New buttons that do something | No | Same reason |

- **The game fills only the widgets its code asks for, by name.** A widget with a name the code does not know stays empty and does nothing when clicked. The names are stored as text in `hoi4.exe`, so they can be listed.
  - `tools/Show-CodeNames.ps1 <file.gui> <window>` prints the names stored together with a window's widget names and marks where vanilla defines each one. A name marked `+` is in no vanilla `.gui` file: it is either a widget the code would fill if the window had it, or not a widget name at all.
  - No `+` names means the window already shows every value the code can give it.
  - Checked so far: the division row, the division list frame, the air wing row and the airbase row have no unused widgets. Two `+` names are unexplained and untested: `entry` (division row) and `army_division_list` (division list frame).
  - The executable stores each distinct name once, so a name shared by several windows shows up with only one of them. The tool lists the names it did not find with the others.
- **Hotkeys.** A button takes one `shortcut` line per key: a single key (`"h"`), a combination (`"ctrl+b"`) or a chord (`"ctrl+g+s"`).
  - A window cannot carry a hotkey. Where vanilla wants one without a visible button, it places a button the code knows off screen (`select_hq_shortcut_anchor` at -1000,-1000).
  - `tools/Show-GuiOutline.ps1 <file.gui> <window> -All` shows each button's keys, so buttons without one stand out.
  - Before assigning a key, search the vanilla `interface/` folder for it. Vanilla has 483 `shortcut` lines in 105 files and reuses keys between screens (`h` is "hold" in both the army and the air panel).
  - Every single letter is taken by some vanilla screen. Free on 1.19.3 are most `shift+` and `ctrl+` combinations with a letter.
  - **Confirmed in game (A2):** `shift+u`, added by the mod to the unassign button of the division list, works.
  - **Not yet tested:** two visible buttons sharing a key.
- **Fixed text.** A text box with `text = "<key>"` shows that key's text in the game language.
  - **Confirmed in game (A2):** captions on the sort buttons of the division list, using vanilla keys such as `ARMY_SORT_NAME` ("Name"). A vanilla key needs no localisation file. Search `localisation/english/` for a key whose whole text is the word needed.
  - Name an added widget `mod1440_*` and give it `alwaystransparent = yes`, so clicks reach the button under it.
  - Text of the mod's own needs a file under `localisation/`. That folder is not in the game's `checksum_manifest.txt`, so it keeps the mod checksum-neutral. Vanilla localisation files are UTF-8 **with** BOM, the opposite of the rule for `.gui` files. Not used yet; the first use must also check that `build.ps1` packages the folder.
- **Scripted GUIs are not used.** They are the game's way to add new values and buttons, described in `common/scripted_guis/_documentation.md` in the game folder.
  - They live in `common/`, so they change the checksum.
  - They attach to the top bar, the side tabs, the focus tree, the country and state views and the ledgers. The selected army, air wings, navy and the designers are not among the attach points.
  - They work on a country or a state, never on the selected army, division, wing or fleet.

## Overriding vanilla windows

- **Method:** one file per screen, `interface/zz_1440p_<screen>.gui`, containing only the reworked top-level windows. The vanilla file is not copied or replaced.
- **Why the `zz_` prefix:** when two loaded files define a window with the same name, the game uses the definition it loads last, and it loads `.gui` files in `interface/` in file name order. The mod's file must therefore sort after the vanilla file.
- **Evidence** (override test, game 1.19.3, vanilla playset): a redefinition in `interface/zz_*.gui` took effect, one in `interface/aa_*.gui` did not, and one in `interface/1440p_ui/override_test.gui` did. `error.log` had no line about the duplicates.
- **Not yet tested:**
  - Windows whose vanilla file sits in a subfolder of `interface/` (factions, international market and similar). The subfolder result fits two load orders (subfolders after the root, or sorting by bare file name), so repeat the test before the first such screen.
  - Another mod that replaces the whole vanilla file. Deferred to the first compatibility checkpoint in the [Roadmap](Roadmap.md); until then the mod is built and checked against vanilla only.
- **How to test an override:** copy the vanilla window into a test file and add one extra icon and text box near the top (for example sprite `GFX_header_bg` and text "OVERRIDE TEST A"). If the marker shows in game, that file won. Use windows that open from a top bar tab, so the check takes seconds.
- **Widget names stay.** The engine binds data to widgets by `name`, looked up inside their parent. A reworked window keeps every named vanilla widget, with the same element type, under the same named parent. Position, size, font and sprite are free to change.
- **Every overridden window has a baseline.** The vanilla text of the window is saved under `baseline/`, and the test suite compares the mod's window against it. `tools/New-OverrideFile.ps1` exports it when it starts a screen file. `tools/Export-VanillaBaseline.ps1 <file.gui> <window>` exports one on its own, for example to refresh it after a game update.
- **Each window is overridden in one file only.** With two definitions the file that loads last wins silently. The test suite enforces this.
- **File-level `@variables` do not travel with a window.** If a vanilla window uses one (for example `@equipment_entry_heigth` in `airselectionview.gui`), define it in the override file too before overriding that window. Untested, so check it in game the first time.
- **Mod-only windows** (no vanilla counterpart) are named `mod1440_*`.
- **Nothing under `common/`, `events/`, `history/` or `map/`.** Those folders are part of the game checksum; `interface/` and `gfx/` are not.

## How the engine treats sizes and containers

The `.gui` files do not state these outright, and the static tests cannot catch them. Each one cost a game launch to find.

- **Find the window that holds a list by its looks, not its name.** The link between a list and its rows is made in game code. The air wing rows sit in `unassigned_airwings_view` (a frame on `GFX_tiled_window_1b_thin_border` around a `clipping = yes` list), not in the `air_selection` list of `air_selection_view`. Match the frame in a screenshot to a background sprite and a clipping list of the right size before changing a row size.
- **The same rows can sit in a different list in another state of the screen.** With an air group selected, the game puts the group badge and the whole wing list frame into `air_groups_view`, a list from another vanilla file (`airgroupview.gui`). It was left at 580 px, so the wider rows were cut off there, and nobody saw it until a tester created an air group. During the inventory, list the states of the screen (nothing grouped, a group selected, several selected) and ask for a screenshot of each.
- **A clipping list cuts off anything wider than itself.** A list box (`smoothListBoxType`, `listBoxType`) has no slot size. Its `size.x` must be at least the row width, and its parent frame must be wider by the scrollbar gutter (26 px on `GFX_tiled_window_1b_thin_border`). Once a list and its rows are known, the pair goes into `$listRowCases` in `tests/GuiInvariants.Tests.ps1`; the suite then fails if a row outgrows its list or the list's window is not overridden with it.
- **Sizes "set in code" are maximums.** A vanilla comment such as `height set in code, but initial value here is used for max allowed height` means the engine shrinks the window to its content and treats the written size as the limit. Raising it is how a list gets more visible rows. Search the vanilla windows for "set in code" during the inventory.
- **A window can run behind its neighbour.** The division list frame starts at the top of the army badges and continues behind them. A badge narrower than the list leaves the empty top of the frame showing beside it, so badge and list need the same width.
- **Alternative positions are widgets too.** A window can hold `positionType` entries that the game applies in another state, for example `select_all_button_army_group_position` on the army badge. When a widget moves, its alternative positions move by the same amount.
- **Some widths are computed from a grid.** The mission toolbar is as wide as the number of slots times `slotsize.width`, plus twice the grid's `position.x`. Vanilla marks this with the comment "X value becomes spacing on both sides of the window". The result depends on how many entries the player's DLC and mods add, so it cannot be made to fit for everyone.
  - Such a width is the floor for a block of aligned panels. The air wing panel is 705 wide because the mission bar is 703 at vanilla spacing; the rows would need less.
- **Tiled panels look smaller than their `size`.** Tiled sprites have a soft, partly transparent edge. Panels placed edge to edge therefore show the map between them, and panels of equal width do not end at the same visible edge.
  - `GFX_tiled_plain_bg_small`: visible area starts about 3 px inside the box on each side.
  - `GFX_tiled_window_1b_thin_border`: about 4 px at the top, 5 px at the right.
  - Values that gave touching, aligned panels in A1: place a `plain_bg_small` panel 6 px into the `plain_bg_small` panel above it, place a `thin_border` frame 8 px into the `plain_bg_small` panel above it, and make the `plain_bg_small` panel 2 px narrower than the frame.

## Fonts

Larger text means choosing a larger font that vanilla already ships. Sizes in use in vanilla GUI files:

| Use | Vanilla fonts |
|---|---|
| Body text | `hoi_16mbs`, `hoi_18mbs` |
| Emphasis | `hoi_18`, `hoi_18b`, `hoi_20b`, `hoi_20bs` |
| Headers | `hoi_22tech`, `hoi_24header`, `hoi_30header`, `hoi_33`, `hoi_36header` |

- **Confirmed in game (A1):** `hoi_16mbs` to `hoi_18mbs` for row text, and `hoi_18` to `hoi_20b` for a row heading.
- Two 18 px lines fit a 48 px row at y 4 and y 22 (vanilla has 16 px lines at y 7 and y 23), so a larger font does not force a taller row.
- **Confirmed in game (A2):**
  - `hoi_18` to `hoi_20b` for division names, and `hoi_18mbs` to `hoi_20b` for the "30 Selected" count.
  - `hoi_16mbs` to `hoi_18mbs` for the commander's title, name and stat numbers on the army badge.
  - `hoi_18` to `hoi_20b` in an edit box (the army name), together with a wider box.
- Text inside a fixed-size box, such as a count badge, keeps its vanilla font.
- **Provisional:** every other step up in the table.
- **A text's width can be worked out before a launch.** The `xadvance` values in `gfx/fonts/<font>.fnt` add up to its width in pixels. For "Kavallerie-Kommando Insterburg" this gives 199 px in `hoi_18`, which vanilla cuts off at 175, and 231 px in `hoi_20b`; both matched the game. Use it to size name columns and to check that a caption fits its button.

## Lists and scrolling

- `slotsize.width` of a grid equals the width of the entry window that fills it. The link between a grid and its entry window lives in game code, so add the pair to `$entryPairCases` in `tests/GuiInvariants.Tests.ps1`.
- `scroll_wheel_factor` is a whole multiple of the row height. The test suite enforces this for every scroll container with one grid. Vanilla breaks the rule in places (45 for 30 px rows in the division name dropdown), so a window copied into an override file can fail the test until the value is rounded.
- **One entry window can fill several lists.** `unit_template_entry` fills three template dropdowns: two in the division list and one in the division details window. Widening an entry means widening every list that shows it, even in a window that is otherwise left alone; a scrolling list cuts off a wider entry. The code names near the entry (`tools/Show-CodeNames.ps1`) and a search for grids with the same slot size help to find the lists.
- Dropdowns set `expandedOnTop = yes`.

## Sprites and backgrounds

- New sprites are named `GFX_1440p_*` and declared in `interface/1440p_ui.gfx`. Vanilla sprite names are never redefined, because that changes every screen that uses them.
- **No AI-generated images.** Every image is built from vanilla game assets.
- For a window or row that needs a larger background, use the first option that gives a clean result:
  1. An existing vanilla tiled window sprite, used as it is (for example `GFX_tiled_window_1b_thin_border`).
  2. A new tiled sprite declared in `interface/1440p_ui.gfx` that points at an existing vanilla texture file. No new image file.
  3. A background composed from several vanilla sprites: a tiled base plus vanilla frames, header bars and boxes placed as separate icons.
  4. A script that copies pixels from the vanilla bitmap into a larger texture. Output goes to `gfx/interface/1440p_ui/`.
- If none of the four looks clean, the window keeps its vanilla size and only its lists and fonts are reworked.
- **Judge each option in a preview image before it goes into the game.** Simulate option 2 by repeating the centre strip between the two border strips; `tools/stretch_background.py --preview <dir>` writes vanilla and widened frames side by side for option 4. This settled the A1 backgrounds without a game launch.

What A1 showed about the options:

- **Option 2 works for a texture with a plain middle.** Declare a `corneredTileSpriteType` with `size` equal to the texture size, a `borderSize` and `tilingCenter = yes`. On a button, use `quadTextureSprite` and `size = { x = .. y = .. }` instead of `spriteType`. Confirmed in game for the airbase row.
- **Option 2 fails when the texture has decorations away from its corners or a repeating pattern.** A tiled centre repeats or cuts the decorations, and the pattern breaks wherever the centre strip is not a whole number of pattern periods.
- **A background button with several frames needs the same number of frames.** The wing row is a two-frame button, striped when unselected and red when selected, and the engine switches the frame. The two frames repeat at different intervals (73 and 62 px), so no single border size tiles both.
- **Option 4, widening a patterned bitmap:** `widen_periodic` in `tools/stretch_background.py` keeps the left part, continues the inner pattern by repeating one period, and copies the border rows, edge bars and corner rivets back from the vanilla right end.
  - Find the period by comparing the texture with itself shifted by 1 to 96 columns; the shift with the smallest difference is the period.
  - Find border rows, bars and rivets by printing pixel values along a plain column and a decorated column.
- **Pillow writes a DDS the game loads:** uncompressed 32-bit, the pixel format of the vanilla interface textures. Confirmed in game.
- **Not attempted:** making a patterned bitmap taller. A1 kept the vanilla row height of 48 to avoid it.

What A2 showed (division list), confirmed in game unless noted:

- **A progress bar takes any size.** Declare a new `progressbartype` on the vanilla textures with a larger `size`; the gradient textures stretch cleanly. Vanilla draws its small bars upright with `rotation = 1.5708`; without that line the bar lies down and fills from the left.
- **An icon draws a tiled sprite at the sprite's own `size`.** An `iconType` has no size of its own, so declare the `corneredTileSpriteType` at the size wanted. This widened the toolbar plate without a new image.
- **Two more ways to widen a bitmap** in `tools/stretch_background.py`:
  - `widen_spread` for a smooth gradient without a pattern: the middle columns are spread over the new width. Used for the selected row frame.
  - `widen_mirror` for an irregular texture: a plain section is inserted mirrored and then the right way round, so every join is between a column and its copy. Used for the footer plate.
- **A bitmap with several painted areas is widened area by area.** The army badge is painted with a name field, a commander box, a stats box and a plain right area. `widen_mirror_multi` puts one mirrored insert inside each area, so the art follows the layout and no single area becomes a large blank.
  - Find the edges of the areas by listing, along a few rows, the columns where the brightness jumps.
  - Each insert takes its columns from inside one area, clear of every edge.
- **Width is the first thing to be judged in game.** The first build had 90 px bars and a 96 px warnings column; both were sent back as too wide. A column gets the width its content needs and no more, and width that is saved goes back to the map, not to another column.
- **Untested: a tiled sprite replacing a plain one as a window `background`.** The footer plate is a plain sprite drawn at its own size. A tiled sprite normally takes the window's size, which here is set in code, so the plate got a widened texture instead.

What A3 showed (unit details windows), confirmed in game:

- **A row can be shared between vanilla files.** Before enlarging a row, run `tools/Show-CodeNames.ps1` on every window that could use it and look for the row's name; `stat_entry` turned two windows into four.
- **A window the code places can still be moved.** Give the window a 10x10 rectangle and put the background (with a `position`) and every widget where the window should appear. The division details window opens 505 px further right this way, clear of the army panel in each of the places the game picks for it ([Engine Facts](Engine-Facts.md) S17 to S20).
  - Do not pad the texture with a transparent strip instead: the strip swallows clicks on whatever lies under it.
  - Give children that were sized in per cent of the window an explicit size.
- **Bitmaps with painted areas grow band by band.** `grow_bands` in `tools/stretch_background.py` gives each band of rows its own column inserts, and `grow` adds rows between printed lines. Find the plain ranges of each band first: the columns without an edge in any row of the band.
  - Paper, scratched metal: many single-line copies spread over the area (`stretched`).
  - A hatch or dotted line: copies of one period (`spread` with the period).
  - A plain bar: one mirrored insert.
- **Move widgets by name, with a script.** `tools/guiedit.py` sets positions, sizes, fonts and sprites by widget path and leaves the rest of the file alone. A layout is then a short script of numbers that can be run again with other numbers.
- **States a scene cannot reach are still rendered.** A scene's `captures` and `states` can carry `hide`, `rows`, `samples` and `expand`; `render_gui.py --scene <screen> --state <name>` draws them. A sample can be a list, one text per row.
- **A text the design cuts on purpose is listed.** `knownCuts` in the scene names the widget, the text and the reason; the tests then accept it.

What A4 showed (fleet panel), confirmed in game:

- **Look for the row a card does not need.** The vanilla task force card kept a whole row for a few small counters. At 740 px the counters fit beside the mission text, the card went from 125 to 86 px, and 12 task forces fit where 8 did. The code places cards, rows and counters by the size of their entry window ([Engine Facts](Engine-Facts.md) S21), so a lower card needs no other change.
- **Two lines become a table row when the width allows it.** Name and class of a ship side by side took 248 px more width and gave four more ships on the screen, and the class column could be wider than vanilla's.
- **A sample text is not the longest text.** The class name that vanilla cuts was assumed to end where the cut began; the real one was 35 px longer, which cost a launch. Bring up the fullest state the harness can reach (`tag ENG` for a large navy) before settling a column width.
- **A bitmap can lose rows** (`cut` in `tools/stretch_background.py`): spans of one pattern period out of a mesh, or a whole painted band.
- **A window that widens pushes its neighbours.** List what opens beside the panel during the inventory: one follows a button (the composition editor), one has a file position (the home base picker), one is placed by code and needs the 10x10 treatment (the ship details window).
- **Keep a layout script absolute.** A script that adds to the current value moves the widget again on every run; write the vanilla value plus the growth.
- **A pop-up gets a scene of its own.** The composition editor, the home base picker and the transfer window each have a recipe, an `expect` list and references, apart from the panel that opens them. A window the code places is measured twice, with the mod and without it (`at`, `atVanilla`).
- **What cannot be brought up stays close to vanilla.** The template list of the composition editor never opened in a check, so it got the width its dropdown needs and kept its vanilla height.
- **Two vanilla windows can share a grid name.** `templates_grid` and `ships_grid` each exist twice; an entry pair in `tools/gui-links.json` names its window then.
- **Recipes break with the panel they click into.** When a raw recipe step clicks into a panel that is being reworked, turn it into a `clickWidget` step in the same change; three shared moves and the carrier capture of the ship details scene clicked into the fleet panel.

## Recipe for a screen phase

1. **Inventory.**
   - Start from the vanilla screen at 2560x1440: `reference/vanilla/<screen>.jpg` is the whole frame and `<screen>-panel.png` the panel at 1:1 without loss (index in `reference/README.md`). A screen that is not there yet needs a recipe first ([Game Recipes](Game-Recipes.md)), then `tools/Invoke-GameCheck.ps1 <screen> -Vanilla -SaveReference`. Ask the user for a screenshot only for a state a 1936 start cannot show.
   - `tools/Show-GuiOutline.ps1 <file.gui>` lists the windows; add a window name and `-All` for its widgets, fonts and sprites.
   - Note which backgrounds are bitmaps, which sizes are "set in code", which widths come from a grid, and which window really holds each list (see "How the engine treats sizes and containers").
   - List what the vanilla screen crams or hides: values stacked on one spot, text that is cut off, things reached only through a click or a tooltip, and buttons without a hotkey.
   - `tools/Show-CodeNames.ps1 <file.gui> <window>` for each window shows whether the code asks for a widget vanilla leaves out (see "What a redesign can add").
2. **Layout proposal.** Start from what the player should see at once on this screen, then give target sizes, row heights and font choices as a short text mock-up, agreed before any file is written. The mock-up is a render: fill in `tools/scenes/<screen>.json` (positions from the screenshot, sample texts, rows per list) and run `python -I tools/render_gui.py --scene <screen> --over` to draw the proposal over the vanilla screenshot.
   - Cover every panel that is on screen together, not only the ones being resized: say where each panel's visible edges end up and whether each gap between panels stays or closes.
   - Name each addition (a column, a caption, a hotkey) and the row of the table in "What a redesign can add" that makes it possible.
   - Where width or empty space is a matter of judgement, add a mock-up composed from the screenshot: draw the widened background and paste the screenshot's own widgets at their new positions. In A2 the badge was agreed on a mock-up and needed one game check; the division list was agreed on a table of numbers and needed four.
3. **Baseline and starting file.** `tools/New-OverrideFile.ps1 <screen> <file.gui> <window> [<window> ...]` exports the missing baselines and creates `interface/zz_1440p_<screen>.gui` with untouched vanilla copies of the windows. Run it again to add windows later; it never overwrites existing content.
4. **Background.** Only for bitmap backgrounds: work down the four options, judge them in previews, declare the sprite.
5. **Build.** Edit values in the override file; leave names and nesting alone. Add each list and its row window to `tools/gui-links.json`. Then run `tools/Compare-Baseline.ps1 zz_1440p_<screen>.gui` (`-Group` for one line per widget) and read every changed value before the game check.
6. **Static checks and render.** `build.ps1 -Check <screen>` runs the validation, the whole test suite and the scene render, and prints which texts fit their boxes. Look at `scratch/previews/<screen>_crop.png` (and `--bounds` for widget outlines, `--expand <dropdown>` for an opened dropdown) and fix what the render shows. No game check is requested before the render has been looked at.
7. **Game check.** Vanilla playset with only this mod, at 2560x1440. The game re-reads no interface file while it runs ([Engine Facts](Engine-Facts.md) H3, H4), so each check is a fresh start, and `tools/Invoke-GameCheck.ps1 <screen>` does it without a human in about two minutes: launch, a new 1936 game as Germany, the scene's `setup` clicks, a capture and a 2x crop in `scratch/checks/`, the `error.log` diff, exit. Read the crop; the human judges only what a crop cannot settle (tooltips, click targets, states a 1936 start does not show, and whether a width is too much).
   - Give the tester one numbered list per launch that covers everything changed: every list scrolled to the end, every dropdown opened, both states of selectable rows, tooltips and click targets, and every state of the screen (for example with and without a group selected).
   - Screenshots taken with F11 land in `Documents\Paradox Interactive\Hearts of Iron IV\Screenshots\hoi4_<n>.png` at full resolution. Crop the panel and enlarge it 2x to inspect it and to measure edges.
   - `Documents\Paradox Interactive\Hearts of Iron IV\logs\error.log` is rewritten on every launch. A run without the mod already logs about 50 lines on 1.19.3 (DLC, equipment icon and entity messages). Search it for the mod's file names, window names and `GFX_1440p`.
8. **Close.** Store the finished screen with `tools/Invoke-GameCheck.ps1 <screen> -SaveReference` (it goes to `reference/mod/`, beside the vanilla frame). Fill the game-check log in `wiki/phases/<screen>.md`, move the [Engine Facts](Engine-Facts.md) rows the checks confirmed, update the status in [Roadmap](Roadmap.md), the README and the Workshop description; raise `version` in `descriptor.mod`.
