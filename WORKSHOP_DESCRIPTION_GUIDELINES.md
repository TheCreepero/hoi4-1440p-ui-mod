# Steam Workshop Description Guidelines & Reference

This document provides formatting rules, length limits, and reference templates for maintaining the Steam Workshop listing for **HOI4 1440p UI Mod**.

---

## Core Rules & Invariants

1. **No Emojis**: Strictly avoid emojis anywhere in the description text.
2. **Character Limits**: Steam Workshop descriptions have a max limit of ~17,000 raw BBCode characters. Keep bullet points concise and direct.
3. **No Planned Section**: Do not include speculative 'Planned' sections in the public description. List a screen under "Reworked screens" only when its phase is marked Done in `wiki/Roadmap.md`.
4. **Valid Steam BBCode**:
   - Headers: `[h1]Title[/h1]`
   - Bold: `[b]Text[/b]`
   - Italics: `[i]Text[/i]`
   - Links: `[url=https://...]Text[/url]`
   - Bullets: Standard hyphen (`- Item`)

5. **The pages moved out on 2026-10-21**: the manager pages and the Records are the mod HOI4 Manager Pages (`mods/hoi4-manager-pages`). This description names it as the companion and says that this mod keeps Ironman and achievements again (version 2.0).

---

## Template Description

```bbcode
Hearts of Iron IV screens re-laid out for 2560x1440 displays: larger windows, longer lists and larger text. Interface and texture files only, so Ironman and achievements stay available.

The manager pages and the Records window that shipped in versions 1.5 to 1.9 are now the companion mod HOI4 Manager Pages: it stands on its own and works with or without this one.

Check out my other mods:
- [url=https://steamcommunity.com/sharedfiles/filedetails/?id=2967389401]Immersive Namelists Expanded[/url]
- [url=https://steamcommunity.com/sharedfiles/filedetails/?id=3807415216]Immersive Ship Names Expanded[/url]

[h1]Requirements:[/h1]
- A resolution of 2560x1440 or higher with the in-game UI scale at 100%. At a lower resolution or a higher UI scale the windows do not fit on screen.

[h1]Info:[/h1]
- [b]Ironman and achievements compatible[/b] since version 2.0: the mod has no script files and leaves the game checksum alone.
- [b]Save Game Compatible:[/b] Can be added to or removed from ongoing games.
- Built for Hearts of Iron IV version 1.19.*.

[h1]Reworked screens:[/h1]
- [b]Air wings and airbases:[/b] The selection panel shows 20 rows before it scrolls instead of 9. Rows are wider, so wing names appear in full, and the text is larger.
- [b]Selected army:[/b] The division list is a table. Organisation and strength are two lying bars, warnings have a block of their own, division names appear in full in a larger font, and the sort buttons have captions. The change-template dropdown shows 12 templates instead of 6. The army badge has a longer name field and shows the commander's name in full.
- [b]New hotkeys:[/b] Shift+U unassigns the selected divisions, Shift+C consolidates them.
- [b]Unit details:[/b] The windows that open from the icon of a division, ship or air wing show their stats as dark cards of tiles (Base, Combat, Misc), each with a small label over a large value, so long labels wrap instead of being cut. The division window opens beside the army panel instead of on top of it. Equipment names fit on one line.
- [b]Fleet panel:[/b] The ship list is a table with one line per ship: organisation and strength as two lying bars, the name in a larger font and the class name in full beside it. Task force cards are lower, so a fleet of twelve task forces fits on the screen without scrolling. Fleet, task force and home base names appear in full. New hotkeys for selected ships: Shift+N new task force, Shift+R to reserve, Shift+O balance, Shift+G upgrade, Shift+P repair now. The ship class picker of the composition editor shows every class without scrolling, and the home base picker and the transfer window are wider with larger text.
- [b]Recruit & Deploy:[/b] A division in training shows its whole name in a larger font. The template list is a table with one template per line: the name in full with Train, Edit and the toggles beside it, so 22 templates fit before the list scrolls instead of 17. The template panel ends above the bottom bar. New hotkey: Shift+F opens the division designer.
- [b]Army overview:[/b] The O, P and L panels list every division, fleet and air wing on one line with each column in full: names in a larger font, theatre and army side by side, organisation and strength as two lying bars. The panel is 900 px wide; Equipment Details and Sunk Ships open beside it. New hotkey: Shift+I opens Equipment Details.
- [b]Air wing reorganisation:[/b] The window shows ten plane types per list before it scrolls instead of four, with equipment names in full.
- [b]Theatre boxes:[/b] Each theatre box at the top right is wider, so the theatre's name and about twelve army shields fit, and the fleet rows under a navy theatre are easier to read.

[h1]Compatibility:[/h1]
- Built against the vanilla game.
- Checked in October 2026 in a playset with Road to 56, Vanilla Navy Rework, RBM's GFX Overhaul and the Better Mechanics mods: the reworked screens work there. Where another mod changes a screen this mod reworks, this mod's version is shown.
- Other mods that change the same screens may still conflict.

[h1]Feedback & Contributions:[/h1]
Please report issues, suggestions, or feedback in the Steam Workshop discussion threads.
```