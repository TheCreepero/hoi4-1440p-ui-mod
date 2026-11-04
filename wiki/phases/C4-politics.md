# Phase C4: Politics panel

The orchestrator writes Scope, Roles and handoffs, Decisions and Close; the designer's work lands in Inventory and Proposal; the builder writes Build and the Fix rounds; the game checker adds the rows of Game checks. The [Roadmap](../Roadmap.md) keeps only the status and a link here.

## Scope

- Asked by the user on 2026-10-22 (with `/phase` and a screenshot of their own game, USA May 1944 in their playset): "I'd like a redesign of the politics view. In my opinion it could be slightly wider, and the arrangement of its various elements should be considered to take advantage of the extra space."
- Vanilla file and windows: `countrypoliticsview.gui`: the side panel `countrypoliticsview` (550 wide, full height; overridden since D4 in `interface/zz_1440p_politics.gui` with three small changes: the ideology and election texts of `ruling_party_info` moved, the wheel step of `ideas`), and the rows the code fills into `idea_categories_grid` (`country_politics_idea_category_entry` and its idea slots). Not in scope unless the design needs it: `political_ideas_window` (the advisor and law picker, 500x590).
- What the vanilla screen crams or hides (from the screenshot): a 550 px column where the leader, focus, spirits, faction, ruling party and party list share about 330 px of height in small fonts (party names in about 14 px, the ideology and election date overlapping); the national spirits in a small grid that scrolls in the user's game (19 spirits); the idea categories one per row with six slots each, so the user's eight categories (Better Mechanics adds five to vanilla's three) take the full height.
- The user's playset: RT56 (Road to 56, VNR, UTT standalone) replaces `countrypoliticsview.gui` with two changed attributes in `countrypoliticsview` (`python -I tools/check_playset.py`); Better Mechanics: Civilian and Military Laws adds idea categories. HOI4 Manager Pages docks its Figures handle (`mod1440_figures_handle`, 92x34 at 359,12, Shift+M) into this panel with `parent_window_token = politics_tab`.
- Out of scope: the diplomacy and faction views (they share `ruling_party_info`, `chart` and `faction` names, but in their own windows); the Figures page itself (HOI4 Manager Pages).

## Roles and handoffs

- Orchestrator: the interactive session. Designer: agent `designer`. Builder: `builder-screen` (vanilla screen). Game checker: `game-checker`. Full path (a moving window and a changed list: not the short path).
- Handoff folder: `scratch/phases/C4/` (not in the repository); the user's screenshot is `scratch/phases/C4/screenshot-user.jpg`.
- Layout file: `scratch/phases/C4/layout.json`.
- Contracts written: `scratch/phases/C4/contracts.md` (2026-10-22).
- Worktrees: main tree.
- Design page: https://claude.ai/artifact/8CobAqLK3uXcefwpAq7oTu (published 2026-10-22; gate A passed on the first round: linter 0 errors and 2 warnings, the spirit box being its own card; contrast 0 of 11 under the floor).

## Inventory

- Vanilla reference: `reference/vanilla/politics.jpg` and `politics-panel.png` (Germany 1936, three idea categories).

## Proposal

Generated from `scratch/phases/C4/design.json` by `python -I tools/phase_notes.py C4` (the orchestrator runs it at every gate). Write under the markers only what the design file cannot hold.

<!-- generated: proposal (tools/phase_notes.py; edit the handoff file, not this) -->
The panel grows from 550 to **760 px** and is rebuilt in the steel look as five cards: the leader with the ruling ideology, the elections and the popularity pie beside the portrait; the focus, the national spirits and the faction with the balance of power in a column at the right; the parties as a banded table beside the three management buttons; and the idea categories as one compact row each, a steel tab with the name and the slots beside it, 72 px instead of 106.

In the user's game the eight categories take 576 px instead of 848, all 19 spirits show without scrolling (20 fit), the ideology and the election date each get their own line in larger type, and the party names go from 16 px rows in `hoi_16mbs` to 24 px rows in `hoi_18mbs` with room for Road to 56's long names. Verdict: rework; effort: M: one override file: the panel's vanilla widgets moved and resized by apply_layout (no new container), two row windows and their grids resized, five slide-in windows' show_position, and, if agreed, Road to 56's window copied; six steel bitmaps and three insets from the layout, no texture of its own.

What vanilla does badly: Vanilla's 550 px column, which the mod overrides today only to move the ideology and election texts down (D4). In the user's playset (USA, May 1944):

- the ideology ("Democratic") and "Next Election November 1944" overlap, because Road to 56 docks its own sub-ideology line ("Liberalism") at 97,313 of the panel, where vanilla's ideology stood, and the election date wraps into two lines of a one-line box;
- the parties are four 16 px rows in `hoi_16mbs` with names cut at 175 px;
- 19 national spirits are drawn as small icons, 10 per row, in a 74 px box that cuts the second row in half and scrolls;
- eight idea categories (Better Mechanics adds five to vanilla's three) take 106 px each, 848 px in all, so the panel is mostly the idea list;
- the leader's name, the ideology and the party names are in `hoi_16mbs` and `hoi_18mbs`, the smallest fonts of the screen.

**Panel and title strip.** 760 px wide, 100%% high, at -6,78 as vanilla (hidden position -816). Steel title strip 756x46 at 2,2; "Political" in `hoi_36header` at 18,6 in a fixed 200 px box. x 230 to 451 stays free for Better Mechanics' Economy Status (230 to 356) and HOI4 Manager Pages' Figures handle (92x34 at 359,12, unchanged). The rules icon at 676,5 and the close button at 718,8 (ESCAPE), 8 inside the strip's right edge.

**Leader card (6,54, 361x319).** The portrait (156x210) in an inset of 180x226; the leader's name under it in `hoi_24header`, centred in a fixed 180x52 box (two lines: "Franklin Delano / Roosevelt"). Beside the portrait a column 149 px wide at x 210: the ideology emblem on an inset, the ideology in `hoi_24header` (vanilla `hoi_18mbs`), the election date in `hoi_18mbs` in a fixed 149x44 box (two lines, on its own, no overlap), Road to 56's sub-ideology line under it, and the popularity pie on an inset at the foot of the column. `ruling_party_info` moves to 210,150 and keeps its children, so the faction and the balance of power, which are its children, move with explicit offsets.

**Focus, spirits, faction (right column, 373 to 754).** **Focus** (381x107): the focus plate as vanilla draws it, at 381,60.

**National Spirit** (381x129, head band 27): the vanilla title "National Spirit" in the band; the scrolling box grows from 364x74 to 365x90. Up to six spirits: one row of large pictures as vanilla. Seven and more: the small pictures, 10 per row, now two full rows, so 20 show without scrolling (the user has 19); more scroll.

**Faction** (381x71): vanilla's faction button with its view and dismantle buttons at the left, the balance of power (129x57) at the right end, where vanilla also has it beside the faction.

**Government card (6,379, 748x164, head band 27).** Head: "Government" (vanilla key `GOVERNMENT`). The parties as a banded table at 14,426: four rows of 24 (vanilla 16), the colour swatch, the name and popularity in `hoi_18mbs` (vanilla `hoi_16mbs`) in a fixed 500 px box (vanilla 175), the leading party on vanilla's highlight scaled 1.6. `political_party_info_entry` becomes 540x24, `parties_grid`'s slot 540x24. The three buttons stand stacked at the right (574, y 414, 457, 500), top to bottom in vanilla's left-to-right order, still between the head block and the ideas.

**Idea categories (6,549, 748x807).** The scrolling `ideas` box on the steel ground, margin 8, wheel step 72. Each category is one row 692x72 (vanilla 550x100 at a 106 pitch): a steel tab 260x66 with the category icon at 8,19 and the name in `hoi_24header` in a fixed 190x52 box (one or two lines, centred), and the slots beside it at 272,6, seven slots of 60 (vanilla 80; the picture is 53 wide). Vanilla's three categories take 216 px, the playset's eight 576 px; eleven fit before the box scrolls. Vanilla's brown header bar (`category_header`) is parked off screen. The autonomy bar of a subject stays where vanilla has it relative to the ideas: 5 below their top.

**Windows that open beside the panel.** `show_position` x: `political_ideas_window` 540 to 750, `manage_subjects_window`, `exiles_window`, `manage_occupied_window` 537 to 747, `powerbalanceview` (of `powerbalanceview.gui`, overridden in the same file) 545 to 755, so each still opens beside the panel and not under it.

**Road to 56.** Road to 56's copy of `countrypoliticsview.gui` changes two things, both lost under any override of the panel: it corrects vanilla's typo `y = 1s` on the pie chart's overlay (kept: the layout writes `y = 1`), and it moves vanilla's `ideology` to y 600 because its own scripted window `countrypoliticsview_ideology_info` (docked into `politics_tab`) shows the sub-ideology at 97,313. The proposal shows both, the ideology and under it the sub-ideology, by copying Road to 56's window into the override file at a new position (210,226 for its text); it is never shown without Road to 56. A decision for the user.

| Part | Vanilla | Current | Proposed |
|---|---|---|---|
| Panel | 550 x full height | 550 x full height | 760 x full height (210 more over the map) |
| Title strip | header plate, close at -42 | the same | steel 756x46, close 718,8; x 230 to 451 free |
| Leader name | hoi_18mbs, 155x36 | the same | hoi_24header, fixed 180x52 |
| Ideology / elections | hoi_18mbs 155x20 / hoi_16mbs 155x32 | moved 19 down; overlap with Road to 56's line | hoi_24header 149x26 / hoi_18mbs 149x44, each on its own line; Road to 56's line under them |
| Spirits shown | 6 large, or 10 small per row in a 74 px box (1.5 rows) | the same | 6 large, or 2 full rows of 10 small (20) in a 90 px box |
| Party rows | 16 px, hoi_16mbs, name 175 px | the same | 24 px banded, hoi_18mbs, name 500 px |
| Management buttons | a row of three at y 390 | the same | stacked at the right of the party table |
| Idea category row | 550x106 pitch, name hoi_20b above six slots of 80 | the same | 692x72 pitch, steel tab with the name in hoi_24header beside seven slots of 60 |
| Eight categories | 848 px | 848 px | 576 px |
| Slide-in windows | x 537 to 545 | the same | x 747 to 755 |

Additions, each with the row of "What a redesign can add" or the register id that allows it:

- Wider panel; leader, ideology, elections and pie in one card; focus, spirits and faction in a column; the buttons beside the parties ("Move, resize and regroup panels")
- Larger fonts by role and wider, fixed boxes (leader name, ideology, elections, party names, category names) ("Give each existing value its own place"; fixed boxes [W28])
- Steel cards, insets, the party bands and the category tabs ("Cards, panels, grouped headers": plates drawn behind widgets that stay with their vanilla parents, no new container)
- Caption "Government" in the head band ("Fixed text and icons", the vanilla key `GOVERNMENT` (no new text))
- Category rows at 72 px, party rows at 24 px, spirit box of two rows (The grids' slot sizes, which these grids follow [S37])
- Slide-in windows opened further right ("Move, resize and regroup panels" on their show_position; the reason is [S32])
- Road to 56's sub-ideology line under the ideology (Overriding a window of another mod's interface file: the file loaded last wins [L1, L2]; only on the user's word (decisions))
- No hotkey (The frequent actions are clicks on code-filled slots, which carry no key; the three buttons are rare (decisions))

Open until the game shows it:

- Whether `idea_categories_grid` stands the category rows at the new 72 px slot (vanilla's rows stand at the 106 px slot, not at the row window's 100) and whether `ideas_grid` keeps seven slots in 420 px.
- Whether `parties_grid` stands the party rows at 24 px, and how vanilla's leading-party highlight looks scaled 1.6 behind a 540 px row.
- Whether the small spirit pictures stand about 15 px right and 17 px down in their slot as in the user's capture, so that two full rows fit the 90 px box; whether `national_spirit_container` keeps the size the file gives.
- A subject's autonomy bar (`autonomy_progress_view`): vanilla puts it 5 px under the top of the ideas; whether the code pushes the ideas down when it shows (a 1936 Germany start does not show it).
- Where the picker, the three management windows and the balance of power window open: beside the panel at 747 to 755, not under it; whether `command_character_view_window` (x 540) opens beside this panel too.
- `pol_view_bg` parked at -1000,-1000: that it stays off screen with the panel's default clipping.
- In the playset: Road to 56's sub-ideology line at its new place, Better Mechanics' Economy Status and the Figures handle free in the title strip.

Figure groups of the design page: panel, playset, top.
<!-- end generated: proposal -->

## Decisions

Dated, one line each: what was agreed, what was sent back and why. The user's answers to the design page's questions go here, with the date (they are also in `decisions-final.json`).

- 2026-10-22: phase opened as C4 (the next free id of Milestone C) on the user's request; designer briefed.

## Build

Generated from `scratch/phases/C4/build/build.json`: what was built, deviations, fallbacks, not seen in game, the game check line and the checker's checklist, the tests.

<!-- generated: build (tools/phase_notes.py; edit the handoff file, not this) -->
<!-- end generated: build -->

## Game checks

One row per launch, generated from `scratch/phases/C4/checks/check-<n>.json` (columns | # | Date | Build | By | Checked | Result | Screenshot | Taught |; By = `game-checker`). The user's own tests (their game and playset) are added by hand under the markers: date, what they looked at, their words, their screenshots, and the play verdict ([Design Language](../Design-Language.md), "Review questions"): what they looked for and did not find; what they misread; what they still opened another screen or vanilla's window for.

<!-- generated: game checks (tools/phase_notes.py; edit the handoff file, not this) -->
<!-- end generated: game checks -->

## Fix rounds

Generated from `scratch/phases/C4/fixes.json`: one line per fix under a heading per round (issue, cause, fix, what the re-test should look at). Findings from the user's own game name their screenshot.

<!-- generated: fix rounds (tools/phase_notes.py; edit the handoff file, not this) -->
<!-- end generated: fix rounds -->

## Close

- [ ] Roadmap status and link
- [ ] README "Reworked screens"
- [ ] Workshop description
- [ ] `version` in `descriptor.mod`
- [ ] Engine Facts rows confirmed or added
- [ ] Scene file final (`tools/scenes/politics.json`)
- [ ] Finished screen stored: `tools/Invoke-GameCheck.ps1 politics -SaveReference` (`reference/mod/`)
