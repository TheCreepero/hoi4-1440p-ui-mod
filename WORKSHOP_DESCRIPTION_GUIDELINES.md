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

---

## Template Description

```bbcode
Hearts of Iron IV screens re-laid out for 2560x1440 displays: larger windows, longer lists and larger text.

Check out my other mods:
- [url=https://steamcommunity.com/sharedfiles/filedetails/?id=2967389401]Immersive Namelists Expanded[/url]
- [url=https://steamcommunity.com/sharedfiles/filedetails/?id=3807415216]Immersive Ship Names Expanded[/url]

[h1]Requirements:[/h1]
- A resolution of 2560x1440 or higher with the in-game UI scale at 100%. At a lower resolution or a higher UI scale the windows do not fit on screen.

[h1]Info:[/h1]
- [b]Ironman and achievement compatible:[/b] Only interface and graphics files are changed, so the game checksum is untouched.
- [b]Multiplayer compatible.[/b]
- [b]Save Game Compatible:[/b] Can be added or removed from ongoing games without issues.
- Built for Hearts of Iron IV version 1.19.*.

[h1]Reworked screens:[/h1]
- (one bullet per finished screen)

[h1]Compatibility:[/h1]
- Built and tested against the vanilla game.
- (fill in after the Phase 1 override test: how the mod behaves next to mods that change the same screens, and the load order to use)

[h1]Feedback & Contributions:[/h1]
Please report issues, suggestions, or feedback in the Steam Workshop discussion threads.
```