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

5. **Sentences that rest on game time** (manager pages): "fill in after a day" and "month by month" rest on hooks no automated check sees run, because no check lets game time pass (`wiki/Scripted-GUIs.md`, "Known gaps"). The user played past the first of a month and reported them working on 2026-10-12. A new page that records over time (Milestone E) is played the same way before its sentence goes into the template.
6. **What the mod writes** is said in the Info lines since 1.6: unit honours are the one thing (`wiki/phases/E6-unit-honours.md`).
7. **Before publishing 1.6**: "battles won and lost" under Officers rests on four hooks no check has seen fire (nine days of a test war brought no battle), and "capitulations" on a daily comparison never seen finding one. Play a war first; if the Won and Lost columns stay empty after battles, take the phrase out or fix the hooks (`wiki/Scripted-GUIs.md`, "Known gaps").

---

## Template Description

```bbcode
Hearts of Iron IV screens re-laid out for 2560x1440 displays: larger windows, longer lists and larger text. Manager pages beside the vanilla panels fill the free width with tables and figures of your country, and a Records window keeps a war diary, your officers, your government and your wars for those who play the game as a story.

Check out my other mods:
- [url=https://steamcommunity.com/sharedfiles/filedetails/?id=2967389401]Immersive Namelists Expanded[/url]
- [url=https://steamcommunity.com/sharedfiles/filedetails/?id=3807415216]Immersive Ship Names Expanded[/url]

[h1]Requirements:[/h1]
- A resolution of 2560x1440 or higher with the in-game UI scale at 100%. At a lower resolution or a higher UI scale the windows do not fit on screen.

[h1]Info:[/h1]
- [b]Not compatible with Ironman and achievements[/b] since version 1.5: the pages need script files, which change the game checksum. They show values and keep records of their own. The one thing written into your game is a line in a division's history (unit honours, below), which you can switch off.
- [b]Multiplayer:[/b] every player needs the mod.
- [b]Save Game Compatible:[/b] Can be added to or removed from ongoing games. Added to a running game, the manager pages fill in after a day, the History graph starts on the first of the next month, and the Records begin on that day.
- Built for Hearts of Iron IV version 1.19.*.

[h1]Manager pages:[/h1]
Shift+M shows and hides the page of the open tab.
- [b]Army Readiness[/b] (beside Recruit & Deploy): manpower free, in training, in the field and needed by garrisons, and divisions below 75% strength and below 50% organisation, as tiles. For sixteen kinds of land equipment the stock, what your divisions hold, what they need and what they are short of, with a bar, shortages in red. One row per general with troops: divisions, battalions, divisions fighting, planning and the worst equipped kind of equipment.
- [b]States[/b] (beside Construction): every state you control as a table: free building slots, building levels, resources, population, compliance and resistance. Click a column head to sort. Click a state and the camera goes there. The totals of the listed states stand under the list.
- [b]National Figures[/b] (from Politics): the summed modifiers of your country, 101 of them: what all your laws, spirits, advisors and technologies together add to factory output, construction speed, research speed, organisation, compliance and the rest; what does not apply is grey. With factories, stability, war support, fuel and party popularity as tiles and bars, and a table of resources.
- [b]History[/b] (in National Figures): twelve figures of your country month by month: manpower, divisions, factories, stability, war support, fuel and more. A table with the change in a month and in a year, and a graph of the one you click, with a zoom.
- The pages show your own country only. Equipment, buildings and resources added by other mods do not appear in them.

[h1]The Records:[/h1]
The Records button of the top bar or Shift+J opens a window that writes your campaign down as you play.
- [b]War Diary:[/b] a dated log of wars, peace, capitulations, annexations, subjects, your faction, every state and victory point taken or lost with the general on the spot, changes of government and your officers' careers. Filters by kind; a button on a line about a place moves the camera there.
- [b]Officers:[/b] every general and admiral with his portrait in a table you can sort, and a file for each: commissioned, promoted, battles won and lost, states and victory points taken under him. A retired officer keeps his record. Award him your country's medals from the game, by name and icon: for an officer a record only, with no bonus and no cost.
- Officers that other mods add are listed as well. Their portraits show for the mods this build knows; from other mods they show the unknown leader.
- [b]Government:[/b] head of government, parties and their leaders, laws, cabinet, high command, faction and subjects, each name with the day it took office.
- [b]Wars:[/b] one row per enemy and per finished war, and a file for the war you click: the flags and heads of government of both sides, days, your casualties, states and victory points taken and lost, how it ended.
- [b]Unit honours[/b] (By Blood Alone): your divisions that stand in an enemy capital when it falls get a line in their own history. A button beside the state view cites the divisions in a state the same way. The Battle honours switch on the War Diary turns the automatic line off.
- The record starts on the day the mod is first active in a game. Nothing can be typed into a page, and the game gives no page the name of a division or a ship.

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
- Checked in October 2026 in a playset with Road to 56, Vanilla Navy Rework, RBM's GFX Overhaul and the Better Mechanics mods: the reworked screens and the pages work there. The victory points of Road to 56's map are followed. Where another mod changes a screen this mod reworks, this mod's version is shown.
- Known with those mods: laws, equipment, buildings and medals they add are not in the pages (a law of theirs reads "another law"), and officers whose portrait Road to 56 gives as a picture file show the unknown leader.
- Other mods that change the same screens may still conflict.

[h1]Feedback & Contributions:[/h1]
Please report issues, suggestions, or feedback in the Steam Workshop discussion threads.
```