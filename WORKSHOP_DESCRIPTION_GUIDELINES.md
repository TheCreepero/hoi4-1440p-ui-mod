# Steam Workshop Description Guidelines & Reference

This document provides formatting rules, length limits, and reference templates for maintaining the Steam Workshop listing for **HOI4 1440p UI Mod**.

---

## Core Rules & Invariants

1. **No Emojis**: Strictly avoid emojis anywhere in the description text.
2. **Character Limits**: Steam Workshop descriptions have a max limit of ~17,000 raw BBCode characters. Keep bullet points concise and direct.
3. **No Planned Section**: Do not include speculative 'Planned' sections in the public description. List a screen under "Reworked screens", or a page under "Manager pages", only when its phase is marked Done in `wiki/Roadmap.md`.
4. **Valid Steam BBCode**:
   - Headers: `[h1]Title[/h1]`
   - Bold: `[b]Text[/b]`
   - Italics: `[i]Text[/i]`
   - Links: `[url=https://...]Text[/url]`
   - Bullets: Standard hyphen (`- Item`)

5. **Before publishing 1.5**: two sentences of the template rest on hooks no automated check has seen run, because no check lets game time pass (`wiki/Scripted-GUIs.md`, "Known gaps"). Play a few days and past the first of a month first: the date beside "Count again" on Army Readiness should be the day's, and History should have a second column. If not, fix the hooks or take "fill in after a day" and "month by month" out.

---

## Template Description

```bbcode
Hearts of Iron IV screens re-laid out for 2560x1440 displays: larger windows, longer lists and larger text. New manager pages beside the vanilla panels fill the free width with tables and figures of your country.

Check out my other mods:
- [url=https://steamcommunity.com/sharedfiles/filedetails/?id=2967389401]Immersive Namelists Expanded[/url]
- [url=https://steamcommunity.com/sharedfiles/filedetails/?id=3807415216]Immersive Ship Names Expanded[/url]

[h1]Requirements:[/h1]
- A resolution of 2560x1440 or higher with the in-game UI scale at 100%. At a lower resolution or a higher UI scale the windows do not fit on screen.

[h1]Info:[/h1]
- [b]Not compatible with Ironman and achievements[/b] since version 1.5: the manager pages need script files, which change the game checksum. The pages only show values; they change nothing in your game.
- [b]Multiplayer:[/b] every player needs the mod.
- [b]Save Game Compatible:[/b] Can be added to or removed from ongoing games. Added to a running game, the manager pages fill in after a day and the History graph starts on the first of the next month.
- Built for Hearts of Iron IV version 1.19.*.

[h1]Manager pages:[/h1]
Shift+M shows and hides the page of the open tab.
- [b]Army Readiness[/b] (beside Recruit & Deploy): manpower free, in training, in the field and needed by garrisons. For sixteen kinds of land equipment the stock, what your divisions hold and what they need, with a bar, shortages in red. Divisions below 75% strength and below 50% organisation. One row per general with troops: divisions, battalions, divisions fighting, planning and the worst equipped kind of equipment.
- [b]States[/b] (beside Construction): every state you control as a table: free building slots, building levels, resources, population, compliance and resistance. Click a column head to sort. Click a state and the camera goes there.
- [b]National Figures[/b] (from Politics): the summed modifiers of your country, 93 of them: what all your laws, spirits, advisors and technologies together add to factory output, construction speed, research speed, organisation and the rest. With factories, fuel, party popularity and a table of resources.
- [b]History[/b] (in National Figures): twelve figures of your country month by month as a graph: manpower, divisions, factories, stability, war support, fuel and more.
- The pages show your own country only. Equipment, buildings and resources added by other mods do not appear in them.

[h1]Reworked screens:[/h1]
- [b]Air wings and airbases:[/b] The selection panel shows 20 rows before it scrolls instead of 9. Rows are wider, so wing names appear in full, and the text is larger.
- [b]Selected army:[/b] The division list is a table. Organisation and strength are two lying bars, warnings have a block of their own, division names appear in full in a larger font, and the sort buttons have captions. The change-template dropdown shows 12 templates instead of 6. The army badge has a longer name field and shows the commander's name in full.
- [b]New hotkeys:[/b] Shift+U unassigns the selected divisions, Shift+C consolidates them.
- [b]Unit details:[/b] The windows that open from the icon of a division, ship or air wing show their stats as dark cards of tiles (Base, Combat, Misc), each with a small label over a large value, so long labels wrap instead of being cut. The division window opens beside the army panel instead of on top of it. Equipment names fit on one line.
- [b]Fleet panel:[/b] The ship list is a table with one line per ship: organisation and strength as two lying bars, the name in a larger font and the class name in full beside it. Task force cards are lower, so a fleet of twelve task forces fits on the screen without scrolling. Fleet, task force and home base names appear in full. New hotkeys for selected ships: Shift+N new task force, Shift+R to reserve, Shift+O balance, Shift+G upgrade, Shift+P repair now. The ship class picker of the composition editor shows every class without scrolling, and the home base picker and the transfer window are wider with larger text.
- [b]Recruit & Deploy:[/b] A division in training shows its whole name in a larger font. The template list is a table with one template per line: the name in full with Train, Edit and the toggles beside it, so 22 templates fit before the list scrolls instead of 17. The template panel ends above the bottom bar. New hotkey: Shift+F opens the division designer.

[h1]Compatibility:[/h1]
- Built and tested against the vanilla game only.
- Not tested with other mods. Mods that change the same screens may conflict.

[h1]Feedback & Contributions:[/h1]
Please report issues, suggestions, or feedback in the Steam Workshop discussion threads.
```