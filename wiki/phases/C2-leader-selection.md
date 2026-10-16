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

## Fix round 1 (2026-10-16)

From the user's in-game test (`found_issues_16102026.txt`, `fieldmarshal_selection.png`: Italy, the commander selection of an army group). Not seen in game yet.

- The army group's list was "visually broken": every row showed a 510x98 vanilla background in the 760x124 row, so Details and Promote stood outside the paper. Cause (hoi4.exe 1.19.3, `FUN_141ad3580`, called from the row's update `FUN_141ad0cd0`): the code swaps the row's `Background` sprite by name for every state but the plain general's, which the constructor `FUN_141ab8b30` starts in: field marshal `GFX_marshal_selection_entry_bg` (assigned: `_active_`), a general who cannot take the command (an army group's list) `GFX_leader_selection_unavailable_entry_bg`, the assigned general `GFX_leader_selection_active_entry_bg` (and `_unavailable_active_`), a faction commander row the `_faction` pair. So an army's list showed it only on its assigned commander and on field marshals, an army group's list on every row. Fix: the seven names declared again at 760x124 in `interface/zz_1440p_vanilla_sprites.gfx` [LOAD-012], built by `tools/stretch_background.py` (jobs `ls_entry_*`: the plain-paper states take the paper's new columns from the plain row so the star stays single; the striped states grow by whole stripe periods with the seal lifted out and laid back) and listed in `tests/GuiInvariants.Tests.ps1`. Re-test: an army group's commander list (field marshals gold with the banner, generals grey), an army's list with its assigned commander (striped), and the faction commander window if the DLC is there.
- Left as it is: `GFX_leader_selection_entry_bg` (the plain state) is also the vanilla background of `divisionleaderentry` and `advisorroleselectionview`, so it cannot be widened; a row that goes back to the plain state while the window is open (a general unassigned) would get the narrow vanilla paper until the list is rebuilt. And the code puts `GFX_leader_selection_active_entry_bg` on a captured general's row (`capturedarmyleaderentry`, 510 wide, `FUN_141ad5c40`), where it now runs 250 px past the row. Re-test both if they come up.

## Close

- [ ] Roadmap status and link
- [ ] README "Reworked screens"
- [ ] Workshop description
- [ ] `version` in `descriptor.mod`
- [ ] Engine Facts rows confirmed or added
- [x] Scene file (`tools/scenes/leader_selection.json`)
- [ ] Finished screen stored under `reference/mod/`
