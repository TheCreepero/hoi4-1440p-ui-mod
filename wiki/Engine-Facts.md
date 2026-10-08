# Engine Facts

Everything the mod relies on about how the Clausewitz engine treats `.gui` files, one row per fact, with how sure we are. [Design Rules](Design-Rules.md) explains the rules that follow from these facts; this page is the register an agent scans before proposing a layout or asking for a launch.

Status values:

- **confirmed**: seen in game, with the phase and launch that showed it.
- **provisional**: used in a shipped screen but judged only once, or judged from a screenshot rather than a dedicated check.
- **untested**: assumed from the files or from a tool, not yet seen in game.
- **disproved**: tried and found wrong; kept so nobody tries it again.

Add a row when a launch or an experiment teaches something, and move a row up when a check confirms it. `tools/render_gui.py` draws what the **confirmed** and **provisional** rows describe; the "Renderer" column says whether it does.

## Loading and overriding

| # | Fact | Status | Evidence | Renderer |
|---|---|---|---|---|
| L1 | A window redefined in `interface/zz_*.gui` replaces the vanilla window of the same name; `.gui` files load in file name order and the last definition wins. | confirmed | Phase 1 override test, game 1.19.3 | yes (mod file first) |
| L2 | A redefinition in a file that sorts before the vanilla file (`aa_*.gui`) does not take effect. | confirmed | Phase 1 override test | - |
| L3 | A redefinition in a subfolder of `interface/` (`interface/1440p_ui/x.gui`) takes effect. | confirmed | Phase 1 override test | - |
| L4 | Windows whose vanilla file sits in a subfolder of `interface/` can be overridden from the root the same way. | untested | first screen in a subfolder (factions, market) | - |
| L5 | Duplicate window definitions produce no line in `error.log`. | confirmed | Phase 1 | - |
| L6 | File-level `@variables` do not travel with a window: an override file must define the ones it uses. | untested | `@equipment_entry_heigth` in `airselectionview.gui` | yes (warns when undefined) |
| L7 | Next to a mod that replaces the whole vanilla file, the single-window override wins or loses by file name order only. | untested | deferred to the first compatibility checkpoint | - |
| L8 | `interface/` and `gfx/` are outside the checksum; `localisation/` is too. | confirmed | `checksum_manifest.txt` | - |

## Widgets and data

| # | Fact | Status | Evidence | Renderer |
|---|---|---|---|---|
| W1 | The code fills widgets by `name`, looked up inside their parent; a renamed or moved widget stays empty. | confirmed | A1, A2 | n/a (test suite) |
| W2 | A widget with a name the code does not know stays empty and does nothing when clicked. | confirmed | A2 captions (`mod1440_*`) | yes (blank unless a sample or literal text) |
| W3 | The names the code asks for are stored as text in `hoi4.exe`, grouped per source file; `tools/Show-CodeNames.ps1` lists them. | confirmed | A2 inventory | - |
| W4 | `entry` (division row) and `army_division_list` (division list frame) are stored with the window names but defined in no vanilla file. | untested | Show-CodeNames | - |
| W5 | A `shortcut` line on a button the code knows adds a hotkey; a key, `ctrl+x` or a chord `ctrl+g+s`. | confirmed | A2: `shift+u` | n/a |
| W6 | A window cannot carry a `shortcut`; vanilla uses an off-screen button at -1000,-1000. | confirmed | vanilla `select_hq_shortcut_anchor` | drawn off canvas |
| W7 | Two visible buttons sharing a key. | untested | - | - |
| W8 | A text box with `text = "<key>"` shows that key's text; vanilla keys need no file. | confirmed | A2 sort captions | yes (English localisation) |
| W9 | A mod localisation file must be UTF-8 **with** BOM and must be packaged. | untested | not used yet | - |
| W10 | A text wider than `maxWidth` on a one-line box is cut off with an ellipsis. | provisional | hoi4_8.png: "Kavallerie-Kommando Inst..." | yes |
| W11 | Text width is the sum of the `xadvance` values of `gfx/fonts/<font>.fnt`. | confirmed | A2: 199 px (`hoi_18`), 231 px (`hoi_20b`) | yes (`Measure-GuiText`, `BitmapFont.width`) |

## Sizes and containers

| # | Fact | Status | Evidence | Renderer |
|---|---|---|---|---|
| S1 | A size commented "set in code" is a maximum; the engine shrinks the window to its content. | confirmed | A1 list height, A2 list height | note only: scene `height` sets what is drawn |
| S2 | A child container commented "set in code to match the window size" takes the parent's height. | provisional | A2 `content_window`, `divisions_window` | yes |
| S3 | The rows of the division list are inserted by code into `divisions_window` (a container), 33 px apart. | confirmed | hoi4_8.png rows at y 242, 275, 308 | yes (`listRows` in the scene) |
| S4 | The air wing rows are inserted into `air_wings_list` in `unassigned_airwings_view`, 48 px apart. | confirmed | A1; hoi4_7.png pitch 48 | yes |
| S5 | A list box (`smoothListBoxType`, `listboxType`) cuts off anything wider than itself; its frame needs the scrollbar gutter (26 px on `GFX_tiled_window_1b_thin_border`). | confirmed | A1 launch 1 | yes (clips to the list) |
| S6 | `slotsize.width` of a grid equals the width of its entry window. | confirmed | A2 | yes |
| S7 | A window can run behind its neighbour: the division list frame starts at the top of the army badge (y 83) while its content starts below the badge (y 181). | confirmed | A2 | partly: the scene puts the frame at 181 |
| S8 | `positionType` entries are alternative positions the code applies in another state; they move with their widget. | confirmed | A2 badge `*_army_group_position` | shown in --bounds |
| S9 | The mission toolbar width is slots x `slotsize.width` plus twice the grid's `position.x`; it depends on DLC. | confirmed | A1 | no (grid filled by code) |
| S10 | `clipping = no` is written on most vanilla containers; what a container without the line does. | untested | - | option `--clip-default` |
| S11 | An `expandedWindow` opens at `show_position` relative to its dropdown and draws above the rest of the window. | provisional | A2 template dropdown | yes (`--expand`) |
| S12 | `hq_window` of the division list shows only when an HQ can be deployed; `bottom_window` only for the unassigned list. | provisional | hoi4_8.png | scene `hide` |
| S13 | `rotation = 1.5708` turns a bar 90 degrees anticlockwise about its top-left corner, so it stands up from its anchor. | provisional | badge bars fit their 36 px box only this way | yes |
| S14 | Centred windows should leave 100 px free above and below (at most about 1240 px high). | provisional | not judged before B1 | - |
| S15 | Panels docked top left may run down to about y 1130; the A1 maxima end at 1133 and 1139 (the test suite allows 1140). | confirmed | A1 | - |
| S16 | Vanilla stores plain parameters in `positionType` blocks too (`divisions_summary_max_item_count`: `position.x` is a count); only blocks named `*_position` are alternative positions. | confirmed | A2 badge | - |

## Sprites and textures

| # | Fact | Status | Evidence | Renderer |
|---|---|---|---|---|
| G1 | Tiled sprites (`corneredTileSpriteType`) take the size of the window they are the background of; `borderSize` is kept, the centre tiles or stretches. | confirmed | A1 | yes (9-slice) |
| G2 | A plain sprite as a window background is drawn at its own texture size. | confirmed | A2 footer plate | yes |
| G3 | An `iconType` draws a tiled sprite at the sprite's own `size`. | confirmed | A2 header plate | yes |
| G4 | A tiled sprite replacing a plain one as a window `background`. | untested | - | - |
| G5 | Tiled panels look smaller than their size: `GFX_tiled_plain_bg_small` about 3 px inside, `GFX_tiled_window_1b_thin_border` 4 px at the top and 5 px at the right. | confirmed | A1 launch 2 | yes (the real texture is drawn) |
| G6 | A `progressbartype` takes any `size`; the gradient textures stretch. | confirmed | A2 bars | yes (70 % filled) |
| G7 | `noOfFrames` splits a texture horizontally; a background button switches frame when selected. | confirmed | A1 wing rows | yes (`--frame 2`) |
| G8 | A tiled sprite on a texture with decorations away from the corners or a repeating pattern breaks. | confirmed | A1 option 2 | yes (visible in the render) |
| G9 | Pillow writes an uncompressed 32-bit DDS the game loads. | confirmed | A1 | - |
| G10 | Making a patterned bitmap taller. | untested | - | - |
| G11 | A sprite name that no `.gfx` file declares draws nothing and logs nothing. | provisional | vanilla placeholder names (`GFX_idea_HOL_wilhelmina`) | warns |

## Fonts

| # | Fact | Status | Evidence | Renderer |
|---|---|---|---|---|
| F1 | `hoi_16mbs` to `hoi_18mbs` for row text, `hoi_18` to `hoi_20b` for a row heading, keep the row height. | confirmed | A1 | yes |
| F2 | `hoi_18` to `hoi_20b` for division names and in an edit box; `hoi_18mbs` to `hoi_20b` for a count. | confirmed | A2 | yes |
| F3 | Text inside a fixed-size box (count badge) keeps its vanilla font. | confirmed | A2 | - |
| F4 | Every other step in the font table of the Design Rules. | provisional | - | yes |

## Driving the game (harness)

Settled on 2026-10-08, game 1.19.3, by one supervised run and three unattended ones. `tools/GameHarness.ps1` and `tools/Invoke-GameCheck.ps1` are built on these rows.

| # | Fact | Status | Evidence | Harness |
|---|---|---|---|---|
| H1 | `hoi4.exe -debug -gdpr-compliant` started from the game folder reads `dlc_load.json` and loads the mods listed there, without the launcher. An empty `enabled_mods` list gives vanilla. | confirmed | `system.log`: "Active Mod: HOI4 1440p UI Mod"; vanilla run shows the 422 px list | `Start-Hoi4`, `Set-HoiPlayset` |
| H2 | The console opens and closes with the key left of 1 (scan code 0x29) on a Finnish layout in exclusive fullscreen, and `SendInput` keys and clicks reach the game. Text typed through `VkKeyScan` arrives intact, including `_` and spaces. | confirmed | `console_history.txt` holds each command as typed | `Send-HoiConsole`, `Send-HoiClick` |
| H3 | **The game re-reads no `.gui` file while it runs.** `reloadinterface` answers "Interface reloaded." and `reload <file>.gui` answers "<file> reloaded!", but an overridden window keeps its old values: when it is open, when it is reopened, after `tag` to another country and back, and in a new game started from the main menu of the same process. | disproved | edits to `selected_division_count` and `unit_name` positions, five captures | every check restarts the game |
| H4 | `reload_textures` reports "30277 textures were reloaded." but a changed mod DDS keeps its old look; with a file name as filter it reports 0. | disproved | tinted `av_wing_entry_bg.dds`, two captures | every check restarts the game |
| H5 | `guibounds` draws two guide rectangles, 1280x720 and 1600x900, not the bounds of widgets. | disproved | capture with the guides | not used; `render_gui.py --bounds` outlines widgets offline |
| H6 | F11 writes `Screenshots\hoi4_<n>.png` at full resolution in a running game, not in the menus. A copy of the primary screen (`Graphics.CopyFromScreen`) works in exclusive fullscreen everywhere, menus included. | confirmed | menu and map captures | `Save-HoiScreenshot` (screen copy by default, `-F11` for the key) |
| H7 | `-continuelastsave`, `-start_tag=GER`, `-hands_off`: not tried. The menu is clicked through instead, which avoids loading a save of the user. | untested | - | `Start-HoiNewGame` |
| H8 | `-windowed`: not tried; everything works in exclusive fullscreen. The `fullscreen` console command was sent once in the supervised run and input was lost afterwards. | untested | supervised run, Q7 | not used |
| H9 | A vanilla launch logs about 50 `error.log` lines; `baseline/error.log.vanilla` holds them. The game keeps its logs open for writing: read them with shared access. | confirmed | 53 lines, none naming the mod | `Compare-HoiErrorLog`, `Read-HoiSharedLines` |
| H10 | The game rewrites `console_history.txt` in its folder after every command it runs. A command that is missing there did not reach the console. | confirmed | file time matches each command | `Send-HoiConsole` checks it |
| H11 | A click only reaches the game while its window is in front, and a background process may take the foreground only after attaching to the thread that holds it. A key sent while another window is in front lands there. | confirmed | supervised run: one key press went to the terminal and left the console open, so the next command acted as hotkeys | `Set-HoiForeground`, checked before every key and click |
| H12 | From process start to a paused 1936 game as Germany takes about 92 s: 55 s to the main menu, 12 s until it takes clicks, seven menu clicks, 50 s of loading. | confirmed | every unattended run | `Start-HoiNewGame` |
| H13 | `resign` leads to the end screen; its Quit button returns to the main menu in the same process. | confirmed | capture | not used (H3: a new session does not reload either) |
| H14 | With the cursor on another monitor the map scrolls at that edge (`corner_scrolling`). | provisional | supervised run: the map ended up over Siberia | the cursor is parked over the map before a capture |
| H15 | Escape closes one window or selection per press; with nothing left it opens the game menu, which dims the whole screen, and one more Escape closes that. Counting presses until the top bar dims is a reliable way back to an empty screen. | confirmed | reset after two open panels gave a capture equal to the clean one | `Reset-HoiState` |
| H16 | Home puts the camera on the capital at a fixed zoom, the same every time, and not the view a new game opens with. Map positions are repeatable only when measured in the Home view. | confirmed | two Home captures differ by 1.8 of 255; start view against Home view by 28 | `Reset-HoiState`; map steps in `tools/moves.json` |
| H17 | Opening the navy or air overview switches the map mode, and the bottom bar then lists fleets or air theatres where the army portraits were. F1 restores the land mode and the army portraits. | confirmed | a click on the army portrait selected a submarine fleet after `p` | `Reset-HoiState` presses F1 |
| H18 | Every top bar screen opens with its vanilla hotkey sent as a scan code: q, shift+q, w, e, r, t, y, u, i, o, p, l, shift+e, shift+w, ctrl+q. | confirmed | fifteen captures | `open_*` moves |
| H19 | A widget's position computed by the renderer from the scene's `at` is accurate enough to click it: template button, division info button, leader portrait, create-air-group and new-wing buttons were all hit by name. | confirmed | captures of the opened windows | `clickWidget` steps, `render_gui.py --locate` |
| H20 | A widget drawn by the renderer can be found in a game capture by comparing pixels within 20 px of its layout position; buttons and icons with their own sprite match with a mean difference under 25 of 255, text and code-recoloured sprites do not. | confirmed | `army_selection`: three widgets found at 0 to 3 px | `render_gui.py --verify`, scene `expect` |
| H21 | Selecting an army by its bottom bar portrait pans the camera to it; the air map mode after selecting an airbase shows the map further out. Both are undone by the reset. | provisional | captures | reset before every scene |
| H22 | A centred window sits exactly where its own `position`, `orientation` and `origo` put it on a 2560x1440 screen: the division, tank, plane and ship designers and the air wing reorganisation were found at 0 to 1 px from the layout, with and without the mod. | confirmed | `render_gui.py --verify` on ten captures | scenes without `at` |
| H23 | A window the code docks next to others moves with their sizes: the wing list frame is at 2,168 with the mod and at 2,197 in vanilla, and an air group badge pushes it further down. | confirmed | `--verify` on mod and vanilla captures | `at` and `atVanilla` in the scene |
| H24 | The "Add new Air Wing" button of an airbase (`new_btn`, hotkey n) is disabled while no planes are in reserve; its tooltip says so. Disbanding wings (toolbar `btn_delete`, then Enter on the confirmation) fills the reserve. | confirmed | tooltip capture; the window opened after the disband | move `planes_into_reserve` |
| H26 | Windows Defender treats a PowerShell script that copies the screen and also encodes JPEG as `HackTool:PowerShell/EmpireGetScreenshot` and deletes the file; screen copy to PNG together with simulated input is accepted. | confirmed | 2026-10-08: `tools/GameHarness.ps1` was removed and rebuilt without the encoder | the harness saves PNG only; `tools/save_reference.py` converts |
| H25 | Creating an army from a box selection works once per game: afterwards the divisions are assigned, the same box selects the army instead, and the green + is not where it was. | confirmed | the second run of the old move opened a state view | move `prepare_game`, run once by the harness |
