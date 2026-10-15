# Phase A7: air wing reorganisation

The window an airbase's "Add new Air Wing" button opens (and the reorganisation of an existing wing): planes in reserve on the left, the new wing on the right. Status: built and checked by the harness on 2026-10-14, while the user was away; awaiting the tester's judgement. Override file: `interface/zz_1440p_air_wing_reorg.gui`.

## Scope

- Vanilla file and windows, in `airwingreorganization.gui`: `air_wing_reorganization` (the window) and its two kinds of entry, `air_wing_reorganization_equipment_entry_left` and `_right`.
- What the vanilla screen crams or hides:
  - Each list shows four plane types before it scrolls (341 px of rows of 80).
  - The equipment name of a type has 150 px in `hoi_16mbs` on the left: "Inter-War Medium Airfr...", "Inter-War Transport Pl...".
- Out of scope: the split window (`strategicair_split_wnd`), the reinforcement preference strip, the manpower dropdown's list.

## Inventory

- Vanilla reference: `reference/vanilla/air_wing_reorg*`. The recipe disbands the Brandenburg wings first, so the scene runs last (`changesState`).
- Where the window sits: centred in its file (`orientation = center`), found where the file puts it (H22). The mod's window is centred the same way.
- `Show-CodeNames`: nothing the code would fill that vanilla leaves out.
- **The left list centres its entries** (S31): its grid has no `format` line, and a slot of 265 in a list of 498 puts an entry about 117 px in, its background another 102 to the left. The mod grows list and slot by the same 120 px, so the offset stays; the scene places the grid there, which the renderer cannot know.
- The right list's grid has a slot as wide as the list (`100%`), so its entries start at the grid's x of 15.
- Bitmap background of an entry: `equipment_item_large_02.dds`, two frames of 458x80, plain olive from column 60 to 360. Option 4 (`aw_equipment_entry.dds`).
- `scroll_wheel_factor` was 40 on rows of 80: the test suite asks for whole rows, now 80.

## Proposal

Built without a proposal round (the user asked for A6 to A8 while away). What the player should see at once: every plane type in reserve and every type in the new wing, names whole, without scrolling in a mid-game air force.

| Panel or column | Vanilla | Built | Why |
|---|---|---|---|
| Window | 1000x515 | 1240x995, centred | |
| Each list | 498x341: four types | 618x821: ten types | a 1942 air force has a dozen types or more |
| An entry | background 458 | background 578 | |
| Equipment name, left | 150 px | 270 px | "Inter-War Close Air Support Airframe" (playset), 218 px |
| Plane picture, left | x 30 | x 150 | clear of a long name |
| Count, icons and the reinforcement preference | | 120 px further right with the entry's end | |

## Decisions

- 2026-10-14: ten rows a list, decided without the user. The window is 995 high: 222 px free above and 223 below, inside the provisional limit of S14 (1240).
- 2026-10-14: the plane picture of a left entry moved 120 px, not 60 as first built: in the user's playset "Inter-War Close Air Support Airframe" ran over it (check 3).

## Game checks

| # | Date | Build | Checked | Result | Screenshot | Taught |
|---|---|---|---|---|---|---|
| 1 | 2026-10-14 | b34ad34+dirty | first build | verified; entries centred where the scene put them, names whole | `scratch/checks/air_wing_reorg-20261014-163719*` | S31 |
| 2 | 2026-10-14 | b34ad34+dirty | two types moved into the new wing | the right list's entries in place, the reinforcement preference at the entry's end, totals at the bottom | `scratch/checks/a7_right-*` | - |
| 3 | 2026-10-14 | b34ad34+dirty | with the user's playset | verified; the longer name of the playset ran over the picture | `scratch/checks/air_wing_reorg-20261014-165905*` | - |
| 4 | 2026-10-14 | b34ad34+dirty | the picture 120 px in; stored as reference | verified | `reference/mod/air_wing_reorg*` | - |

Not seen in game:

- More than ten types in a list (the scrollbar), a carrier-capable type, a design company icon on a type of the right list.
- Reorganising an existing wing (the left manpower box shows then).
- The manpower dropdown opened.

## Left for the tester

1. Whether 1240x995 is too much for this window; it is the first centred window the mod reworks (S14).
2. Moving types left and right, the reinforcement preference of a type, Ok.
3. Reorganising an existing wing.

## Close

- [x] Roadmap status and link
- [x] README "Reworked screens"
- [x] Workshop description
- [x] `version` in `descriptor.mod` (1.7)
- [x] Engine Facts rows confirmed or added
- [x] Scene file (`tools/scenes/air_wing_reorg.json`)
- [x] Finished screen stored under `reference/mod/`
- [ ] The tester's judgement
