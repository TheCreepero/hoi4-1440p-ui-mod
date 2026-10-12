# Phase E2: Officers

One row per general and admiral with a service record the mod keeps, a card for the chosen officer, and decorations the player awards. The second page of [the Records](../Roleplay-Pages.md). Status: built and checked in game on 2026-10-12; awaiting the tester's judgement. Not seen: a battle counted, and an officer's record after a save and a load. How each value was checked is in [Scripted GUIs](../Scripted-GUIs.md), "The Records".

## Scope

- **Vanilla has:** the general's portrait, skills and traits in the selection list and on the army badge, one officer at a time. No table of all officers, no record of what an officer did, no date of anything. The Armies list of Army Readiness (D6) shows generals with troops and what they command today.
- **The page:** every officer in one table that sorts, with what the mod wrote down about him since it has been active.
- **Out of scope:** a portrait (none can be read); a trait by name (the page shows how many of each kind; see "Later"); selecting the officer's army (a row cannot select); renaming (no text field).

## The page

| Part | Size | Holds |
|---|---|---|
| Filter row | 1640x40 | All, Army, Navy, With a command, Decorated, Former |
| Table | 1010 wide, rows 40 high, 27 in sight | one row per officer; a click on a column head sorts, a second click turns the order; a click on a row chooses the officer |
| Card | 610 wide, beside the table | the chosen officer |

| Column | Width | Source |
|---|---|---|
| Name | 290 | `[THIS.GetName]` (X10) |
| Rank | 130 | Field Marshal, General or Admiral: three texts on the row, each shown by a `_visible` trigger on `is_field_marshal`, `is_corps_commander` or `is_navy_leader` (X39). `GetRank` is empty for every officer (X42) |
| Skill | 50 | `skill_level` (X21) |
| Attack, Defence, Planning, Logistics | 4 x 45 | `attack_level`, `defense_level`, `planning_level`, `logistics_level` (X21); for an admiral `maneuvering_level` and `coordination_level` take the last two |
| Traits | 50 | `num_traits` (X21) |
| Command | 70 | `num_units` or `num_ships` |
| Won, Lost | 2 x 55 | the record |
| Decorations | 120 | up to five small medal icons |

**The card** of the chosen officer:

- Name, rank, skill, the four levels.
- Traits by kind: basic, personality, terrain, status, assigned of the most he can take (`num_basic_traits` and its siblings, `num_max_traits`).
- Command today: divisions, battalions, divisions fighting, by kind (as the Armies list), or ships.
- Record: commissioned on (or "before the record began"), promoted on, last skill level on, battles won and lost, states taken under him.
- Decorations with their dates, and the buttons Award (one per grade) and Take back the last.
- His lines of the War Diary, newest first: the log filtered by subject.

## The record

Written by hooks into the officer himself. A general, an admiral and an advisor each keep variables of the mod, also through a promotion and a retirement (X32):

| Name | Written by | When |
|---|---|---|
| `mod1440_of_since` | `on_unit_leader_created` (the leader, FROM the country) | the date; officers of the start of a game get none and read "before the record began" |
| `mod1440_of_prom` | `on_army_leader_promoted` | the date |
| `mod1440_of_lvl` | `on_unit_leader_level_up` (ROOT the leader, FROM the country) | the date of the last level |
| `mod1440_of_won`, `mod1440_of_lost` | `on_army_leader_won_combat`, `on_army_leader_lost_combat`, and the two navy hooks | plus one |
| `mod1440_of_states` | `on_state_control_changed`, for the general with the most divisions in the state: `num_units_in_state@var:<the state>` in each general's scope (X44) | plus one |
| `mod1440_of_dec_1` to `_5` | the Award button | the date; cleared by Take back |

- **Seen firing:** the hooks of creation, promotion and skill level, each in the officer's scope with FROM his country (X43). An officer the game starts with gets no "commissioned" date, as planned.
- **Not seen:** the four battle hooks. They need fighting, so the two counts are checked in play.
- **What a battle is:** the hook does not say where or against whom, so the page counts and does not list. Whether a field marshal is counted with his general is seen only in play.
- **A retired officer keeps his record** (X34): he leaves the game's list of officers and stays readable from a list of the mod. The page keeps its own array of every officer it has seen, and a filter "Former" shows those no longer serving.
- **Through a save and a load:** not tested, because no check saves. It is the one thing the whole page rests on that has not been seen.

## Decorations

A decoration is a record of the mod: five dates on the officer. It gives no bonus and changes nothing the game works with.

- **Five grades**, awarded in any order by the player, each at most once. A line goes into the War Diary.
- **Names and icons (decision 5 of the Records):** either five neutral names with frames of the game's default medal strip (`GFX_medal_icon_default`), or the game's own medals of the country: vanilla has 103 unit medals in national sets, with names and icons. The second needs a table of sets per country in the tool and follows the vanilla triggers that say which country has which set. Start with the first; the second is an addition.
- **Not planned:** a cost in command power or political power for a decoration. It could be added; then it is a real spending and is said so in the tooltip.

## Data and script

A section `officers()` of `tools/build_managers.py`.

| Name | What |
|---|---|
| `mod1440_of_known` | every officer the page has seen, serving or not: `army_leaders` and `navy_leaders` are added to it once a day |
| `mod1440_of_list` | the officers of the chosen filter in the chosen order, sorted with key arrays as the States page sorts (X22). The list is scoped to the officer, so a row reads his values and his record directly; an array of the country in a row needs `ROOT.` before its name (X36) |
| `mod1440_of_sel` | the chosen officer, held by the country: a row's click runs `ROOT = { set_variable = { mod1440_of_sel = PREV } }` (X33, seen). The card's name is `[?mod1440_of_sel.GetName]`, his record `[?mod1440_of_sel:<variable>]`, and his game values (skill, command) are copied by an effect that enters `var:mod1440_of_sel` |
| `mod1440_of_card` (effect) | fills the card and its diary lines; runs on a row click, on Award and once a day while the page is open |
| `mod1440_of_award_<n>_click`, `mod1440_of_takeback_click` | the decoration buttons |

Commands new to the test's list: `is_field_marshal`, `is_corps_commander`, `is_navy_leader`, `is_assigned`, `is_in_array`, `var:` scopes, and loops over the two arrays. The record is variables of the mod on a character, which the rule allows; no command that writes to the game is needed.

## What the probe settled

| Question | Answer | For this page |
|---|---|---|
| A variable on a general | yes (X32) | the record lives on the officer; flags are not needed |
| The country holds a general | yes (X33) | the card of the chosen officer, and officer lines in the diary |
| A held general once he is gone | everything stays readable (X34) | former officers keep their row and their lines |
| `_visible` per row | yes (X39) | the rank as a word |
| `navy_leaders` in a list | yes, like generals (X42) | admirals in the table |
| Troops in a state held by a variable | yes, `@var:` (X44) | "states taken" per general |

## Checks

1. **Paused, by effects:** promote a general (`promote_leader`), give a skill level, create one: the three dates are today's. Award and take back each grade. Sort by every column; the order is compared with the numbers.
2. **Values against the game:** skill and the four levels against the army badge (as X21); traits against the general's tooltip; command against the army's division count.
3. **Needs time:** battles won and lost, states taken. A week of fighting in the user's game, or decision 3 of the Records; the hooks log to `game.log` until seen.
4. **A retired general** (`retire`): the table, the card and the diary after it. The probe saw his name, skill and variables stay readable; a general who dies in the field is still to be seen.
5. **A save and a load,** if the user allows a check to save under a file name of its own, or in the user's own game: the record of an officer after loading.

## Later

- **Traits by name.** A text per vanilla trait through `has_trait`, joined in the card's tooltip. About a hundred traits typed into the tool; other mods' traits would not appear.
- **A portrait frame** with the rank's insignia, if a vanilla sprite suits.

## Decisions

- 2026-10-12: planned.
- 2026-10-12, the user: decorations are the game's own national medals. Built so: the 103 unit medals of the game with the game's own conditions (`tools/unit_medals_table.py`); a country is offered those it has, twelve at most, by name and icon.
- A medal can be awarded to an officer once. No cost, no bonus.
- The card shows seven decorations and seven diary lines; an officer with more keeps them, and the page shows the first seven.
- The rank column reads Marshal, General or Admiral: "Field Marshal" did not fit its 84 px.

- 2026-10-12, the user: "a round of improving the UI ... really polished and fit their purpose really well", with free hands. Done the same day: striped rows with the chosen officer's row marked, numbers under the middle of their heads, and the card as a file: the name in the title font, rank and service in a line, four figures as tiles, the medals side by side at full size with name and date in the tooltip, the medals on offer with their own icon and an "awarded" mark on a button that no longer answers. Checked in game and from a cold start (`scratch/checks/crop_p_*.png`, `reference/mod/`).

## Game checks

| # | Date | Build | Checked | Result | Screenshot | Taught |
|---|---|---|---|---|---|---|
| 1 | 2026-10-12 | `1a08bb3` +dirty | the page as Germany: 27 officers; a click on a row; Award twice; the Former filter after a retirement by effect | the table and the card as planned; Iron Cross and Knight's Cross listed with the date; the retired general under Former as "no longer serving" | `scratch/checks/crop_e1_5.png`, `crop_e1_6.png`, `crop_e1_18.png` | X51 |
| 2 | 2026-10-12 | the same game | nine days at war with one army under a general | no battle was fought: Won, Lost and the states taken stayed 0 | - | X55 |


## Close

- [x] Engine Facts rows; `wiki/Scripted-GUIs.md`
- [x] README and Workshop description
- [x] Scene file and recipe (`tools/scenes/officers.json`), reference capture
- [ ] Battles won and lost seen counting in a game with fighting
- [ ] An officer's record after a save and a load, in the tester's game
- [ ] The tester's judgement
