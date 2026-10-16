# Phase C2: general selection

The window "Select Commander" that the portrait of an army badge opens. Status: built on 2026-10-16 and checked by render and tests; no game check yet. Override file: `interface/zz_1440p_leader_selection.gui`.

## Scope

- Vanilla file and windows, in `unitleaderwindow.gui`: `armyleaderwindow` and its row `armyleaderentry`.
- What the vanilla screen crams or hides: five generals before the list scrolls, portraits of 68x87, the sort buttons in a row above a list whose columns they do not match.
- Out of scope: the admiral, operative, captured and division commander windows (`navyleaderwindow` and the others), which use rows of their own. The same treatment suits them once this one is judged.

## Inventory

- Vanilla reference: `reference/vanilla/leader_selection.jpg` (the window is in the full frame; the scene's crop was wrong and is corrected).
- Window bindings: the row's code fills portrait, title, name, skill, the four stats, traits, capacity, advisor role, the two buttons, and the faction commander's figures. Nothing more could be shown, so the window got smaller rather than fuller (user, 2026-10-16).
- The portrait is a button the code puts the general's portrait on; vanilla draws it at `scale = 0.42` (68x87 of a 156x210 texture). The mod sets 0.55: 86x116.
- Bitmaps (option 4, jobs `ls_*`): the window, 550x607 to 800x1180 (columns right of the painted search field, rows across the plain middle); a row, 510x98 to 760x124 (the portrait box 32 wider, the paper 218, 26 rows in the plain band).
- No mod of the user's playset changes `unitleaderwindow.gui`.

## Proposal

Agreed on mock-ups (design page, round 2, 2026-10-16).

| Part | Vanilla | Built |
|---|---|---|
| Window | 550x590 | 800x1180, centred |
| Row | 510x98 | 760x124, 128 apart |
| Generals before the list scrolls | 5 | 8 |
| Portrait | 68x87 | 86x116 |
| The four skills | at 308-418 | 78 px further right, under their sort buttons |
| Details, Promote | beside the traits | on the second line of the row |

## Decisions

- 2026-10-16: 800x1180 is the right size (user).

## Game checks

| # | Date | Build | Checked | Result | Screenshot | Taught |
|---|---|---|---|---|---|---|
| 1 | 2026-10-16 | working tree | the tester, in a 1944 game as the United States | no bugs, no change asked | - | - |

## Close

- [ ] Roadmap status and link
- [ ] README "Reworked screens"
- [ ] Workshop description
- [ ] `version` in `descriptor.mod`
- [ ] Engine Facts rows confirmed or added
- [x] Scene file (`tools/scenes/leader_selection.json`)
- [ ] Finished screen stored under `reference/mod/`
