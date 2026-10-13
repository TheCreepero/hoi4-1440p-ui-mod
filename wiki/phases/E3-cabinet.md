# Phase E3: Government

Who rules and who serves: the head of government, the parties and their leaders, the cabinet, the high command, the laws in force, the faction and the intelligence service, with the date each took office. A page of [the Records](../Roleplay-Pages.md). Status: built and checked in game on 2026-10-12; awaiting the tester's judgement. How each value was checked is in [Scripted GUIs](../Scripted-GUIs.md), "The Records".

## Scope

- **Vanilla has:** all of these on the politics panel, the diplomacy view and the agency window, as portraits and icons with tooltips. No names side by side, no dates.
- **The page:** the names in one place, and since when.
- **Out of scope:** what an advisor or a spirit does (the game writes such a description only for an advisor named in the file, not for "the one in this row"); national spirits (script has no list of them); portraits; anything of another country beyond its name.

## The page

Seven cards in three columns of about 540.

| Card | Rows | Source |
|---|---|---|
| Head of government | name; ruling party, short and long; ideology; in office since; last election; next election in N days, or "no elections" | `[ROOT.GetLeader]`, `GetRulingParty`, `GetRulingPartyLong`, `GetRulingIdeology`, `GetLastElection` (R2); `days_until_next_election` (-1: never); the date from the mod |
| Parties | four rows: party, its leader, popularity | `Get<Ideology>Party`, `Get<Ideology>Leader` (R2); `party_popularity@<ideology>` (checked in D4) |
| Cabinet | one row per political advisor: name, since | a list over the mod's copy of `political_advisor`, read by row index: `[?mod1440_gv_adv^i.GetName]`. An advisor who is no general has no scope in a row (X42), and no ideology of his own |
| High command | the chiefs of army, navy and air force, the theorist, then one row per member of the high command: name, since | `[?army_chief.GetName]` and its three siblings, each shown only when `any_character = { is_army_chief = yes }` says the office is filled: an empty office prints the country's name (X42). A list over the copy of `high_command`, by index |
| Laws | economy, trade, conscription: the name of the law in force | `has_idea` for each vanilla law, worked out once a day into a text key (P5); the names are the game's own |
| Realm | capital; faction and its leader; members; subjects; overlord; occupied countries; at war with | `[ROOT.Capital.GetName]`, `GetFactionName`, lists over `faction_members`, `subjects`, `occupied_countries`, `enemies` with `GetNameWithFlag` |
| Intelligence | the agency's name; one row per operative: name, code name, where | `[ROOT.GetAgency]`; a list over `operatives`: `GetName`, `GetCodeName`, `operation_country`, `operation_state` |

Stability, war support and political power are on National Figures and are not repeated.

## Since when

- **By comparing.** Once a day `mod1440_ev_daily` (E1) compares `country_leader`, the four single offices and the two advisor arrays with its copy. A new name gets a line in the War Diary ("Appointed", "New head of government") and today's date, kept in an array beside the copy. A name that is gone gets "Dismissed".
- **At the start** of a record every office reads "before the record began".

## Data and script

A section `government()` of `tools/build_managers.py`.

| Name | What |
|---|---|
| `mod1440_gv_adv`, `mod1440_gv_adv_since` | yesterday's political advisors and the date each was first seen |
| `mod1440_gv_hc`, `mod1440_gv_hc_since` | the same for the high command |
| `mod1440_gv_office_<n>`, `mod1440_gv_office_<n>_since` | the head of government and the four single offices |
| `mod1440_gv_law_<n>` | the text key of the law in force, per kind |
| `mod1440_gv_daily` (effect) | the comparison and the laws; called from `mod1440_ev_daily` |

Commands new to the test's list: `has_idea`, `any_character`, `is_army_chief`, `is_navy_chief`, `is_air_chief`, `is_theorist`. Nothing writes to the game.

## What the probe settled

| Question | Answer | For this page |
|---|---|---|
| The texts of the own country | all work: leader, party short and long, ideology, last election, days to the next, faction, agency, capital, four parties with their leaders (X41) | the Head of government, Parties and Realm cards as planned. The last election prints with its hour (" 1:00, 5 March, 1933"); the hour cannot be taken off, so the row gets room for it |
| Advisors and the high command in a list | names by row index, not by the row's scope (X42) | the two lists read the mod's copies; "since" comes from an array beside each copy, as planned |
| The single offices | a name once filled, the country's name before (X42) | each office row is shown by a trigger |
| A text key in a variable | yes (X37) | the laws by the game's own names |
| Countries in a list with flag | yes (X40) | the Realm lists |
| Who is hired at a start | nobody for Germany | the Cabinet and High command cards start empty in most games and say so |
| Operatives | none at a start, so the list was empty | the Intelligence card is still unseen: whether an operative has a scope in a row, and his code name, are looked at when the page is built, with an agency founded by effect |

## Checks

1. **Against the game** (Germany, 1 January 1936): leader, party and ideology against the politics panel; the four parties against the same panel (popularity as in D4); the laws against the three law slots; the faction and capital against the diplomacy view.
2. **Paused, by effects:** hire advisors with `activate_advisor` from a throwaway effect (the probe hired four this way), then run the daily effect from the console with nothing selected (X49): the rows appear with today's date and the diary has "Appointed". The same for a dismissal.
3. **Other countries** through `tag`: the Soviet Union (elections never), the United States (an election date), a country in a faction.
4. **Needs time:** the daily comparison running by itself; an election.

## Decisions

- 2026-10-12: planned.
- Built without a list of operatives: the card gives the agency's name and how many operatives there are. A list waits for a check with an agency.
- "At war with" and the occupied countries are left to the Wars page.

- 2026-10-12, the user: "a round of improving the UI ... really polished and fit their purpose really well", with free hands. Done the same day: three columns that run the whole height: the head of government's name in the title font, a bar for each party's support, four figures of the record; cabinet and high command as striped lists; the faction's name in the title font over its members, and the subjects. Checked in game and from a cold start (`scratch/checks/crop_p_*.png`, `reference/mod/`).

## Additions of 2026-10-13: the flag and the portrait

The user had installed the build of 2026-10-12, played a war with it and wrote on 2026-10-13: "Overall I'm very happy with the results. I just want more graphical details", with three wishes: an officer's portrait in his file and in the list; a record, in the officer's file and in the War Diary, of each battle over a victory point won or lost and of each state captured; a file for a war as there is one for a general, with the flags and maybe the leaders of each side and some statistics.

- The card of the head of government has the country's flag beside the name (`[ROOT.GetFlag]` as the image of an icon, Engine Facts X59) and the leader's portrait at 125x168 beside the party and the dates. The portrait is looked up when another leader rules (`mod1440_p_leader`, the 663 heads of government of `tools/portraits_table.py`). The card is 280 px high instead of 234.
- **Fixed:** an office whose holder was replaced on the same day, or who returned after a vacancy, was not written down. The test read `NOT = { has = 1 holder = <he> }`, which the game takes as "neither"; it is now "not both" ([Script Reference](../Script-Reference.md)).
- **Checked in game on 2026-10-13** (checks 3 and 4 below).
- **After the check:** a head of government's portrait is looked up once per leader and kept on his country (`mod1440_ld_p`), so that the file of a war does not go through the table each time it is drawn.

- **Places (2026-10-13):** an advisor and a head of government are kept as their place in the game's list of characters, which moves when the game's character files change (Engine Facts X67). Each holder now carries his place on himself (`mod1440_gv_marks`, once a day), and when the places have moved the copies are put right with everything else (`mod1440_ch_remap`); if a holder cannot be found the copies are taken again without lines. Before, such a change would have written every office as left and filled again. Seen: the page as the USA after the change (Roosevelt with portrait and flag, the parties, the faction and its subject); the repair itself was seen for officers only ([E2 notes](E2-officer-records.md), check 6).

**Left unseen:** the page as another country in a game of its own (`tag ITA`, `tag SOV`); a country whose leader the table does not know (the unknown leader: seen for a general, and for no head of government); an office through a real change of the character files.

## Game checks

| # | Date | Build | Checked | Result | Screenshot | Taught |
|---|---|---|---|---|---|---|
| 1 | 2026-10-12 | `1a08bb3` +dirty | the page as Germany on 1 January 1936, after four advisors were hired and Denmark made a subject by effect | leader, party, ideology and elections as the politics panel has them; parties 40, 35, 10, 15; the three laws of the start by their game names; Todt and Neurath in the cabinet, Fritsch chief of the army, Rundstedt in the high command, each "since 1936.1.1"; Axis with its two members | `scratch/checks/crop_e1_7.png`, `crop_e1_16.png` | - |
| 2 | 2026-10-12 | the same game | the first night of the time run | the game had dropped three of the advisors; the page and the diary followed | `scratch/checks/crop_e1_15.png` | X53 |
| 3 | 2026-10-13 | `9c832ae` +dirty | live session: the page as Germany | the flag beside the name and Hitler's portrait at 125x168 beside the party and the dates | `scratch/checks/gv1-*` | X58, X59 |
| 4 | 2026-10-13 | the same build, cold start through `tools/Invoke-GameCheck.ps1` with ten other scenes | the page in a new game; `error.log` | the card 280 px high with flag and portrait; every expected widget found where the layout puts it; no line names the mod | `reference/mod/government-panel.png` | - |

- **2026-10-13, with the user's playset:** a party name of Road to 56 took two lines and stood on the leader's name. The name's box has a fixed size of one line now and is cut with dots (W28; `M.text(..., fixed=True)`). The laws of other mods read "another law" and stay so: a condition on an idea the game does not know logs an error each time (X71). [Compatibility](../Compatibility.md).


## Close

- [x] Engine Facts rows; `wiki/Scripted-GUIs.md`
- [x] README and Workshop description
- [x] Scene file and recipe (`tools/scenes/government.json`), reference capture
- [ ] The tester's judgement
