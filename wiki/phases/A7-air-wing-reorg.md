# Phase A7: air wing reorganisation

The window an airbase's "Add new Air Wing" button opens (and the reorganisation of an existing wing): planes in reserve on the left, the new wing on the right. Status of the redesign (2026-10-16): built and checked by render and tests; not seen in game. The first build (2026-10-14) was checked by the harness; see "Game checks". Override file: `interface/zz_1440p_air_wing_reorg.gui`.

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
- 2026-10-16: the redesign approved by the user: 1180 high, ten cards of 86 at a pitch of 90; totals at the head of the wing column; the arrow on a reserve card; the caption Reinforcements before the set-all buttons; the picture centred in its well (see "Redesign build").

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

## Redesign build (2026-10-16)

The user approved the redesign proposal (review page of the redesign pass) and chose every decision: 1180 high with ten cards of 86 at a pitch of 90, the wing's totals at the head of the wing column, the arrow on a reserve card, the caption Reinforcements before the set-all buttons, the plane picture centred in its well.

What was built:

- Window 1240x1180, centred (`position = { x=-620 y=-590 }`): 130 px free above and below, as C2. Title strip 1228x40 (`mod1440_aw_title`), `action_name` 700 wide, `close_button` at the strip's right end.
- Two columns of 608 at x 8 and 624, each with a header strip 608x36 at y 52, a band 608x70 at y 92 and its list 608x932 at y 166. Captions `AIR_WAREHOUSE_LABEL` ("Reserves") and `REINFORCEMENT` ("Reinforcements"), vanilla keys.
- Reserves band: `plane_filters` with `plane_type_grid` 590x62, slots of 96x31, six to a row. The code adds the filters with the grid's next-slot add, so a seventh role starts a second row [GUL-045]; the grid has no `max_slots_vertical`, which would drop the filters that do not fit. Two rows hold twelve roles; the plane strip has nine.
- Wing band: `prio_container` is the band; three plates of the mod (`mod1440_aw_total_planes`, `_manpower`, `_flag`, 220x56, 220x56 and 136x56) with the captions `AIR_SORT_PLANES` and `MANPOWER`; `current_plane_count` and `current_manpower_right` in `hoi_24header`; the flag of `manpower_dropdown` centred on the third plate, its list opening downward over the wing list (`show_position` -142,60). The two vanilla boxes `current_plane_coun_background` and `generic_w_box_right` are declared before the plates and covered by them.
- The set-all strip: `reinforcement_preferences_position` at 1103,50, so the strip should land at the wing header's right end.
- `manpower_icon_left` and `current_manpower_left` at the right end of the Reserves header (shown by the code only when an existing wing is reorganised).
- Lists: `margin` 10 top and bottom, both grids at x 10 with `format = "UPPER_LEFT"`, slot 572x90, `scroll_wheel_factor` 90. Ten cards before the list scrolls; the slider has the 26 px right of the cards. Both grids are now in `tools/gui-links.json`.
- Plane card, both entries 572x86: `bg` on `GFX_1440p_AW_card` (`aw_card.dds`, `equipment_item_large_02.dds` grown by copies to 572x86, two frames; `tools/stretch_background.py`), the old `aw_equipment_entry.dds` and its sprite removed. Picture well `mod1440_aw_well` 160x74 at 6,6; `equipment_icon` centred at 86,43; `design_team_icon` at 134,10; `niche_icon` at 148,64 (now `UPPER_LEFT`); `carrier_capable_icon` at 24,64; `type` `hoi_18mbs` 220 fixed at 180,8; `count` `hoi_24header` right-aligned in 400-470; `name` 280 fixed at 180,34; `missions` at 178,58 (`upper_left`). Reserve card: `mod1440_aw_arrow` (`GFX_transfer_all_btn`, `alwaystransparent`) at 510,28. Wing card: `reinforcement_preference_dropdown` centred at 524,43.
- Footer strip 1228x64 at y 1104 with `confirm_btn` alone.
- Every plate is an icon behind widgets that stay direct children of their window (A9 method); nothing is wrapped, so the window works on an unpatched `hoi4.exe`.
- New sprites in `interface/1440p_ui.gfx`: `GFX_1440p_AW_card`, `_title`, `_column_header`, `_footer`, `_total`, `_total_flag`, `_well`.
- Scene: the grids placed at 10,10; the left manpower and the card badges hidden in the 1936 state; the set-all strip drawn as the window `reinforce_preferences`; a capture `moved` (the first reserve card clicked twice) and a renderer-only state `midgame` (a made-up 1940 air force: ten types, three in the wing, seven filters, every badge).

Deviations from the design: none in the layout. The well sprite is named `GFX_1440p_AW_well` and the plates `mod1440_aw_total_*` as the design says; the flag plate has its own sprite (`GFX_1440p_AW_total_flag`, 136x56), because a cornered tile has one size.

Not seen in game:

- Whether `centerposition = yes` centres the picture the code puts on `equipment_icon` (fallback: `centerposition` off and the icon at 12,22, left-aligned in the well).
- Where the set-all strip lands for 1103,50 (fallback: move the point by what the capture shows; the strip must stay inside the header strip, y 52 to 88).
- The flag dropdown's list opened at its new place.
- The left manpower when an existing wing is reorganised; a carrier-capable type; a designer plane with role and company icons; more than ten types (the slider); the second row of filters (the code wraps them, GUL-045, but no 1936 force has seven roles).
- The card's second frame on hover, and whether a click on the arrow reaches `bg`.
- The renderer shows neither the code-set plane pictures and flag nor the Ok button's text (`text =` on a button); the game does.

Game check, when the user allows it:

    tools/Invoke-GameCheck.ps1 air_wing_reorg

Tester's checklist (also the scene's `checklist`):

1. The window, 1240x1180 centred, 130 px free above and below: is that too much for this window?
2. Both columns start with their caption: Reserves on the left, Reinforcements on the right with the four set-all buttons at the header's right end, inside the header strip.
3. The plane picture sits centred in the dark well of each card; a company icon at the well's top right.
4. Click a reserve card, on the arrow and elsewhere: the whole type goes into the wing. Hover a card: the second frame shows.
5. In the wing column the Planes and Manpower totals change with every card moved; the flag dropdown opens downward over the wing list.
6. The reinforcement dropdown at a wing card's dark end opens to the left and sets the type's preference; the set-all buttons set every type.
7. Tooltips of the set-all buttons, the reinforcement dropdown and (on a carrier type) the carrier icon.
8. If possible: reorganise an existing wing, an air force with seven roles or more, more than ten types.

## Close

- [x] Roadmap status and link
- [x] README "Reworked screens"
- [x] Workshop description
- [x] `version` in `descriptor.mod` (1.7)
- [x] Engine Facts rows confirmed or added
- [x] Scene file (`tools/scenes/air_wing_reorg.json`)
- [x] Finished screen stored under `reference/mod/`
- [ ] The tester's judgement
