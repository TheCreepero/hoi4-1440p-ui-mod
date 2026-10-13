# Phase E1: War Diary

A dated log of the campaign, written by the mod as the game goes: wars, peace, capitulations, territory, landings, changes of government, promotions. It is the first page of [the Records](../Roleplay-Pages.md), and this phase also builds the Records window and the recording that the other pages use. Status: built and checked in game on 2026-10-12; awaiting the tester's judgement. Not seen: a capitulation, a landing, an ace. What the page shows and how each value was checked is in [Scripted GUIs](../Scripted-GUIs.md), "The Records".

## Scope

- **Vanilla has:** pop-ups at the moment of an event, and nothing to read them in afterwards. A division has a history (By Blood Alone); the country has none.
- **The page:** one line per event with its date, newest first, filtered by kind. A line about a state moves the camera there.
- **Out of scope:** events the game has no hook for (a finished focus or research, a lost division or ship, where a battle was fought); events of other countries the player is not part of; a note typed by the player (no text field exists).

## The page

The Records window is about 1680x1220 at 440,100. Under its title strip (page buttons, Close) the diary has a filter row and the list.

| Part | Size | Holds |
|---|---|---|
| Filter row | 1640x40 | All, War and peace, Territory, Government, Officers, Air and sea; beside them "Older" and "Newer" (pages of 200 lines) and the number of lines kept |
| List | 1640x1080, rows 34 high, 31 in sight | the lines, newest first, scrolled with the vanilla scrollbar |

| Column | Width | Text | Source |
|---|---|---|---|
| Date | 150 | 1939.9.1 | the stored date, `GetDateStringNoHour` (X35) |
| Icon | 40 | one frame per family of events | an icon strip of the mod built from vanilla icons; `frame` from the row's value (X10) |
| Event | 380 | "War declared on", "Capital taken", "Promoted to field marshal" | a text key held by the line (X37). The fetched text is plain words: a name cannot stand inside it, which is why subject and other party have columns of their own |
| Subject | 560 | the country (with its flag), the state or the officer | `GetName` or `GetNameWithFlag` of the stored scope (X18, X33, X40) |
| Other party | 400 | "France", "Germany" under a column head that fits the filter | the second stored scope |
| Go | 60 | a camera button, on lines about a state | `goto_state` (X13); shown per row by a `_visible` trigger (X39) |

- **A line keeps its name.** A retired general and an annexed country still give their names from the log (X34).
- **State names follow the holder:** the probe's Danzig read "Gdańsk" once Poland held it again. A line shows the name of today.

## What gets a line

Each hook runs for every country, so its first line asks whether a human country is involved; the line is written for that country. The scopes of the hooks marked "seen" were logged in the probe (X43); the others are those of the vanilla comments (R5).

| Family | Event | Found by | Subject, other party |
|---|---|---|---|
| Record | The record begins | the first run in a game (`on_startup`, or the first day with the mod) | - |
| War and peace | War declared on, War declared by | `on_war_relation_added` (ROOT attacker, FROM defender): seen | the other country |
| | Peace with | the daily comparison of `enemies` with the mod's copy (`on_peace` fires, seen, but does not say with whom) | the country |
| | Capitulated (an enemy), We capitulated | `on_capitulation` (ROOT the capitulated, FROM the winner): not seen, needs fighting | the country, the winner |
| | Annexed | `on_annex` (ROOT the annexer, FROM the annexed): seen | the country |
| | Made a subject, Released | the daily comparison of `subjects`: `on_puppet` did not fire for the effect `puppet`, and may fire only from a peace conference | the country |
| | Joined, left, founded a faction | `on_join_faction`, `on_leave_faction`, `on_create_faction` | the faction leader |
| Territory | State taken, State lost; Capital taken, Capital lost when `is_capital` | `on_state_control_changed` (ROOT new controller, FROM old, FROM.FROM the state): seen. It also fires for the states of an annexed country and for a state handed back in a peace, so many lines can come on one day | the state, the other country |
| | Landing in, Airborne landing in | `on_naval_invasion`, `on_units_paradropped_in_state`; one line per state and day | the state |
| | Nuclear strike | `on_nuke_drop` (ROOT the country that drops; the target is read at build) | the state or country |
| Government | Government changed, Ruling party changed, Election held, Coup, Civil war ended | `on_government_change`, `on_ruling_party_change`, `on_new_term_election`, `on_coup_succeeded`, `on_civil_war_end` | - |
| | New head of government | the daily comparison of `country_leader` | the character |
| Officers | Commissioned, Promoted to field marshal, Gained a skill level | `on_unit_leader_created`, `on_army_leader_promoted`, `on_unit_leader_level_up` (the officer, FROM his country): all three seen. The first does not fire for the officers a game starts with | the officer |
| | Decorated | the Award button of [E2](E2-officer-records.md) | the officer |
| Air and sea | Pride of the fleet sunk (ours, theirs) | `on_pride_of_the_fleet_sunk` (ROOT the owner, FROM the sinker) | the other country |
| | Ace promoted, Ace lost | the ace hooks (not seen: `add_ace` does not fire them) | no name, until play shows that an ace can be kept ([E5](E5-aces-roll.md)) |
| | Operative captured, Operative lost | `on_operative_captured`, `on_operative_death` | the operative |

- **Not every battle.** A general's battles are counted on his record (E2), not listed here: a front makes hundreds.
- **Territory** goes into its own log, so a large offensive does not push out the rest. The All view shows capitals only; the Territory filter shows every state (decision 4 of the Records).

## Data and script

Written by a new section `records()` and `war_diary()` of `tools/build_managers.py`.

| Name | What |
|---|---|
| `mod1440_ev_date`, `_day`, `_kind`, `_a`, `_b` | the log: five arrays of the country, 500 lines. `_date` is a `global.date` for the text, `_day` a `global.num_days` for counting days (X35), `_kind` a text key (X37) |
| `mod1440_tr_date`, `_day`, `_kind`, `_a`, `_b` | the territory log, 500 lines |
| `mod1440_ev_add` (effect) | appends the line held in the temporary variables `ev_kind`, `ev_a`, `ev_b` with today's date, drops the oldest beyond 500, raises `mod1440_wd_dirty` |
| `mod1440_ev_daily` (effect) | compares `enemies` and `country_leader` with `mod1440_ev_enemies` and `mod1440_ev_leader`, writes the lines, takes the new copy |
| `mod1440_wd_list` (effect) | copies the lines of the chosen filter and page, newest first, into `mod1440_wd_date`, `_kind`, `_a`, `_b`; runs when the page opens, on a filter or page button and once a day while it is open |
| `mod1440_rec_open`, `mod1440_rec_page`, `mod1440_wd_filter`, `mod1440_wd_from` | what the window shows |
| `on_actions` | one entry per hook of the table, each a few lines that end in `mod1440_ev_add`; `on_daily` gets `mod1440_ev_daily` for human countries |

Commands new to the test's list: `is_in_array`, `has_war_with`, `is_capital`, `every_enemy_country` or a loop over `enemies`, `var:` scopes. None writes to the game.

## Part C: the state card

A small strip in the vanilla state view: "Taken from France on 1940.6.14, held for 312 days", from variables the territory hook leaves on the state. The probe showed such a card: it appears while a state is selected, its scope is the state, and it may stand inside the state view or beside it (X47). Where it stands is chosen with a mock-up when the phase starts; [E6](E6-unit-honours.md) puts its Cite button on it.

## What the probe settled

| Question | Answer | For this page |
|---|---|---|
| A date in an array | yes (X35) | the date column as planned; a day number is stored beside it |
| A text key in a variable | yes, plain words (X37) | the Event column; no scripted localisation, so no fifth folder under `common/` |
| A held general, also once he is gone | yes (X33, X34) | officer lines carry the name for good |
| A country in an array | yes, with its flag (X40) | the subject and other party columns |
| The hooks | eleven seen; `on_puppet` not by effect (X43) | subjects by the daily comparison; capitulation, landings and aces still to be seen in play |
| A long log | no cost to speak of (X48) | 500 lines, pages of 200 |
| A scoped row and the country's arrays | need `ROOT.` (X36) | the diary's list is not scoped: its rows read the arrays by index |

## Checks

1. **Paused, by effects** (a throwaway effect file, as History's made-up months): a declared war, a state taken with `set_state_controller`, an annexation, a promotion, a new general. The probe fired all of these this way. Each line is compared with what was done: date, words, names. 600 made-up lines: the oldest 100 are gone. The console runs an effect in the scope of what is selected (X49): deselect first.
2. **Values against the game:** the date of a line against the clock; a state's name against the map; the enemy list after `declare_war_on` against the diplomacy view.
3. **Needs time** (the user's play, or decision 3 of the Records): peace found by the daily comparison, a state taken by fighting, a capitulation, a landing. Until seen, each hook also writes `log = "mod1440 <hook> ..."` to `game.log`.
4. **Cost:** the time of `on_state_control_changed` for a country that is not human (it should leave at its first line), measured as X22 was.

## Decisions

- 2026-10-12: planned.
- 2026-10-12, the user: one Records window opened from the top bar ("the window is better"); capitals in the main view and every state under the Territory filter ("sounds good"); a check may run up to ten days inside January 1936 with a copy of the autosave made first.
- Built without an icon column: the words of the Event column proved enough, and an icon strip would have been a new texture.
- Capitulation is found by the daily comparison (`has_capitulated` of each enemy), not by `on_capitulation`: the comparison needs no scope the probe could not see.
- Faction, subjects and the head of government are found by the daily comparison as well.
- Not built: lines for operatives and for a nuclear strike.

- 2026-10-12, the user: "a round of improving the UI ... really polished and fit their purpose really well", with free hands. Done the same day: striped rows under a bar of heads, dates written out, the family's text icon before each line, names in yellow with flags, a country beside its event when the line has no state or person, and the record in twelve figures beside the list, with the switch of the battle honours and its explanation. Checked in game and from a cold start (`scratch/checks/crop_p_*.png`, `reference/mod/`).

## Additions of 2026-10-13: officers on the lines, victory points, All through both logs

The user had installed the build of 2026-10-12, played a war with it and wrote on 2026-10-13: "Overall I'm very happy with the results. I just want more graphical details", with three wishes: an officer's portrait in his file and in the list; a record, in the officer's file and in the War Diary, of each battle over a victory point won or lost and of each state captured; a file for a war as there is one for a general, with the flags and maybe the leaders of each side and some statistics.

- **A line has an officer.** A line about a state names the general who had the most divisions in the state when it changed hands (the search E2 used for its count, now the effect `mod1440_of_best`). The log got four parts: `c` and `sc` (the officer), `p` (the state of a victory point, for the camera) and `x` (the line stands in the other log too). A game saved before gets zeros for the lines that are there (`mod1440_ev_grow`), and its capitals in the territory log the mark `x`.
- **Victory points.** "A battle over a victory point won or lost" cannot be had from the battle hooks: they give the general and his country, not the place. What can be had is the place changing hands: once a day while the country is at war, `mod1440_vp_scan` reads `global.province_controllers` for each of the game's 1495 victory points (`tools/victory_points_table.py`) and compares with the copy of the day before. A point that passed between the country and an enemy is a line "Victory point taken" or "Victory point lost" with its name (the game's text `VICTORY_POINTS_<province>`), the enemy and the general on the spot; its button moves the camera to its state. The copy is taken again without lines on the first day of a war and when the list of points changes.
  - **Decided:** every point, also the small ones (the wish said "a victory point"). A point worth 15 or more (107 of them) stands in the main log too, as a capital does. No line when the old holder has capitulated or is gone: those points were not fought for. A battle won without the place changing hands leaves only its count on the officer.
  - **Cost:** 1495 comparisons a day at war; by Engine Facts X22 a few milliseconds. Not measured.
- **All means all.** The All view goes through both logs together, by day, the main log first on the same day; a line that stands in both is shown once (`merged()` in `tools/build_records.py`). This replaces the user's choice of 2026-10-12 (single states under the Territory filter only): the new wish asked for captures in the diary.
- **The page:** the list is 1270 px wide instead of 1190 for a fifth column, Officer; the pane beside it is narrower and has fourteen figures (victory points taken and lost are new).
- **Checked in game on 2026-10-13** (checks 3 and 4 below), after the user allowed the launch ("Yes, start it now"). Two faults showed and were mended in the open game:
  - **No war closed.** The effect that writes a line kept the officer in the temporary variables `ev_c` and `ev_sc`; `ev_c` is also the country in the loops of the daily comparison, and a temporary variable is one for the whole run (Engine Facts X64). The officer now has `ev_o` and `ev_so`.
  - **An error line per unknown character.** `is_character` wrote "is not a valid character" to `error.log` for a character no country has recruited. Each test now asks the country `has_character` first (X60).

**Left unseen:** a state or a victory point taken by troops in a running game (the lines here were caused by effect while paused); a real save of the build of 2026-10-12 (check 5 took the newer parts away in a new game, which is the same to the script).

## Game checks

| # | Date | Build | Checked | Result | Screenshot | Taught |
|---|---|---|---|---|---|---|
| 1 | 2026-10-12 | `1a08bb3` +dirty | the page in a new game; events caused by effects while paused (war on Poland, Danzig and Brandenburg taken, Luxembourg annexed, Denmark a subject, a promotion, a new general, four advisors); the filters; the state button | every line with the right date, words, name and flag; Territory lists the single states; the button moved the camera to Berlin and closed the window | `scratch/checks/crop_e1_2.png`, `crop_e1_4.png`, `view_e1_3.png` | X50, X52 |
| 2 | 2026-10-12 | the same game | nine days of game time, 1 to 9 January, as Germany at war with Poland | the daily comparison ran each night: three advisors the game had dropped read "Left office"; two states Poland walked into read "State lost to"; the autosave was not written | `scratch/checks/crop_e1_14.png`, `crop_e1_17a.png` | X53, X54, X55 |
| 3 | 2026-10-13 | `9c832ae` +dirty | live session, paused on 1 January 1936, events by the throwaway effects of `scratch/check_f.py`: war on Poland; Toruń, Kraków and Breslau handed over (`set_province_controller`) and the comparison run; Niederschlesien lost and taken back with Rundstedt's army in it; a white peace; war on Czechoslovakia and its annexation; 400 comparisons between two lines of `game.log` | every victory point line with its name, the enemy and the right word; Kraków (20 points) in both logs and once in the All view, Toruń (5) and Breslau (10) in the territory log; Rundstedt on the lines of Niederschlesien and Breslau, nobody on Kraków's; the button of a point moved the camera to its state; the figures followed (3 wars begun and ended, 12 states taken, 2 lost, 3 points taken, 1 lost, 1 capital, 1 annexation); 400 comparisons inside a second. The two faults above | `scratch/checks/wd1-*`, `wd2-*`, `wd3-*` | X60 to X64 |
| 4 | 2026-10-13 | the same build, cold start through `tools/Invoke-GameCheck.ps1` with ten other scenes | the page in a new game; `error.log` | the list 1270 px wide with its fifth column and the fourteen figures; every expected widget found where the layout puts it; no line names the mod | `reference/mod/war_diary-panel.png` | - |
| 5 | 2026-10-13 | the same build, second live session (allowed by the user: "Yes, start it now") | a game as an older build left it: a war, a victory point and a state by effect, then the four newer parts of both logs and the two newer counts of the wars cleared (`mod1440_chk_old` of `scratch/check_f.py`); the Records opened; another victory point lost | the newer parts were 0 long beside 3 and 4 lines, and 3 and 4 again once the Records had opened; the list read as before, without officers; the next lines went in at the right place (6 of 6 in every part); the war's counts were padded when it was next written to, and its file read 1 point lost; no line of `error.log` names the mod | `scratch/checks/b_wd2-*`, `b_wd3-*`, `b_wr1-*` | X57 (`add_to_array` with `index`) |
| 6 | 2026-10-13 | the finished build with the mod "Add USA Generals AI REWORK", cold start, 1 to 4 January | the lines for officers no hook tells of (their command came by an effect) | eight "Commissioned" with names on the day the daily round met them, then "More officers commissioned"; a person kept by his place stayed right through a change of places made up by effect ([E2 notes](E2-officer-records.md), checks 5 to 7) | `scratch/checks/d_wd-*` | X66, X67 |


## Close

- [x] Engine Facts rows for what the checks taught (X50 to X55)
- [x] `wiki/Scripted-GUIs.md`: the page, its values and gaps
- [x] README and Workshop description; `version` 1.6 in `descriptor.mod`
- [x] Scene file and recipe (`tools/scenes/war_diary.json`), reference capture
- [ ] The `log` lines of the landing, airborne and ace hooks taken out once each was seen in a game
- [ ] The tester's judgement
