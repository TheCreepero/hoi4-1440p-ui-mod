# Workflow: who does what in a phase

A phase is run by several agents with one human. This page says who does each step, what each hands to the next and where the user decides. The steps themselves stay in [Design Rules](Design-Rules.md), "Recipe for a screen phase"; this page only assigns them. Adopted by the user on 2026-10-16 after the redesign pass of the same day had run this way with briefs written for the occasion (`scratch/redesign/BRIEF.md`, `BUILD-BRIEF.md`, `FIX-BRIEF.md`, `CONTRACTS.md`, not in the repository).

In Claude Code the roles are the agent definitions under `.claude/agents/` and the runbook is the skill `/phase <id> [<scene> ...]` (`.claude/skills/phase/SKILL.md`, with an identical copy under `.agents/skills/phase/` so that Antigravity loads it too). Another tool, or a person, follows the same roles in the same order by reading those files.

## Roles and models

| Role | Who | May | May not |
|---|---|---|---|
| **Orchestrator** | the interactive session (Claude Fable 5.1) | open the phase, write the contracts, brief and continue the agents, review every handoff, publish the design page, ask the user at the gates, read the captures itself, write the knowledge register, close the phase | build or design in the agents' place; start the game without the user's grant; commit |
| **Designer** | agent `designer` (Claude Opus 5.5) | read everything; run the read-only tools and the renderer; write under `scratch/phases/<id>/` | edit anything else in the repository; start the game; write the register; commit |
| **Builder** | agent `builder-screen` (Claude Sonnet 5.5) for a vanilla screen (`interface/zz_1440p_*.gui`, `.gfx`, textures); agent `builder-script` (Claude Opus 5.5) for a scripted page (`tools/build_managers.py`, `tools/build_records.py`, script, localisation) and for a fix round whose cause is unknown | edit the mod's files, the scene, `tools/gui-links.json`, the tests' lists and its own phase notes; run the renderer and the tests | start the game; write the register; commit; change `wiki/Roadmap.md`, `README.md`, `descriptor.mod`, `GEMINI.md` |
| **Game checker** | agent `game-checker` (Claude Opus 5.5) | start the game through the harness once the user has granted the launches; read the captures and `error.log`; write `scratch/phases/<id>/checks/` and the rows of the "Game checks" table in the phase notes | edit any other file; fix anything; let more than ten days pass; save |
| **The user** | the human (called "the tester" in older phase notes) | approve the design, grant the launches, test in their own game, commit | |

A fix round goes back to the **same builder agent**, continued with the findings, not to a new one: it still holds the design and its own decisions. A builder is spawned anew only when the first one is gone.

## The stages

Recipe steps are those of [Design Rules](Design-Rules.md). Every handoff file lives in `scratch/phases/<id>/` (git-ignored); the durable record is `wiki/phases/<id>.md` and the published design page.

1. **Open** (orchestrator). Copy [Phase Template](Phase-Template.md) to `wiki/phases/<id>.md` and fill Scope. Create `scratch/phases/<id>/`. Write `contracts.md`: hotkeys already taken (`grep -rn 'shortcut = "' interface/ tools/build_managers.py tools/build_records.py`) and the new ones, shared rows and windows, shared files and who owns each, frames two pages share. Choose the builder by kind. One screen: work in the main tree. Several screens at once: one worktree per builder ([Contributing](Contributing.md), "Several screens at once").
2. **Design** (designer): recipe steps 1 and 2. Hands back `design.json`, the mock-ups and their scripts, and a reply of at most 15 lines.
3. **Design review, gate A** (orchestrator). The design passes when:
   - every addition names the row of "What a redesign can add" or the register id that makes it possible, and the window bindings report backs every value shown;
   - every figure group has the vanilla capture, the current state and the proposal at the same scale and the same crop box;
   - the contracts are kept, or a deviation is written down;
   - what only the game can show is under `openInGame`, not promised;
   - `python -I tools/check_playset.py` has been read for the files the design touches, and a text another mod can lengthen has a box of fixed size.
   What fails goes back to the same designer. What passes becomes the design page: an HTML page with the images embedded, published as an artifact when the tool can (link into the phase notes), else `scratch/phases/<id>/design.html`.
4. **User gate 1: the design.** The user marks the page up and answers the `decisions`. The orchestrator writes each answer, dated, under "Decisions" in the phase notes and into `decisions-final.json`. Nothing is built before this gate.
5. **Build** (builder): recipe steps 3 to 6. Hands back `build/build.json`, `build/build-<group>.png` for every figure group, the phase notes section "Build (<date>)" and a reply of at most 20 lines. The gate inside: `build.ps1 -Check <scene>` green, every render looked at.
6. **Build review, gate B** (orchestrator). Read the whole output of `tools/Compare-Baseline.ps1 <file> -Group`: only intended changes. Compare each build render with its mock-up. Read the deviations: each one has a reason the design or the rules back. Add the build renders to the design page. What fails goes back to the same builder.
7. **User gate 2: the launches.** The orchestrator asks once for the phase, naming the scenes, how many launches, and that a check stays paused on 1 January 1936 or runs at most ten days with the autosave copied first. A vague grant has not got a launch through; the grant names the launches. The user's own screen and mouse are taken while the harness runs.
8. **Game check** (game checker): recipe step 7. `tools/Invoke-GameCheck.ps1 <scene> [...]` with this mod alone, then with a mod of the playset where [Game Recipes](Game-Recipes.md) asks for it (pages that read characters, leaders, states or equipment). Works through the scene's `checklist` item by item on the crops, diffs `error.log`, reads the clock. Hands back `checks/check-<n>.json`, one row per launch in the "Game checks" table, and a reply of at most 20 lines: defects first.
9. **Capture review** (orchestrator). Reads the same crops itself: the checker's findings are a list to confirm, not a verdict. Decides which are defects, which are the renderer's known blind spots ([Contributing](Contributing.md), "What the renderer does not show") and which only the user can settle. Defects go to the same builder as a fix round; the checker re-runs only the scenes a fix touched. Each round adds "Fix round <n>" lines to the phase notes: issue, cause, fix, what the re-test should look at.
10. **Report, user gate 3.** When the checks are clean, the orchestrator reports to the user: what was built, the design page with the build renders beside the mock-ups, what the checks showed and with which mods loaded, and the numbered list of what only a human can settle: tooltips, click targets, states a 1936 start does not show, whether a width is too much. The user tests in their own game and playset, and commits.
11. **Close** (orchestrator): recipe step 8. The candidate facts of every handoff (`newFacts`) go to the knowledge register with `Add-HoiKnowledge.ps1`, or are dropped with a reason; then `Export-HoiKnowledge.ps1 -Repo hoi4-1440p-ui-mod`. The register is written by the orchestrator only.

The user's own in-game issues (a list and screenshots, as `screenshots/` and `FOUND_ISSUES.txt` on 2026-10-16) enter at stage 9 as findings.

## Handoff files

All under `scratch/phases/<id>/`. JSON is UTF-8; strings are plain text with `\n\n` between paragraphs, `**bold**` and `` `code` `` the only markup. Every file a `figures` entry names must exist.

**`contracts.md`** (orchestrator, stage 1): hotkeys, shared rows and windows, shared files and their owners, frames shared by pages, what the agents do not change. The pattern is `scratch/redesign/CONTRACTS.md`.

**`design.json`** (designer, stage 2):

```json
{
  "id": "A3",
  "title": "Short name of the component",
  "kind": "screen | page",
  "scenes": ["division_details"],
  "files": ["interface/zz_1440p_unit_details.gui"],
  "verdict": "rework | refine | keep",
  "summary": "Two to four sentences: what the proposal does and why it is better.",
  "current": "What the vanilla screen, or the current build, does badly.",
  "knowledge": [{"fact": "What a register fact or an executable report opens or closes here", "ids": ["W34"]}],
  "proposal": [{"heading": "Part of the screen", "body": "What it becomes, with sizes."}],
  "table": {"columns": ["Part", "Vanilla", "Current", "Proposed"], "rows": [["Panel", "502x430", "", "..."]]},
  "additions": [{"what": "A caption / hotkey / card / scripted value", "how": "The row of 'What a redesign can add', or the register id"}],
  "figures": [
    {"file": "vanilla-main.png", "kind": "vanilla", "group": "main", "caption": "..."},
    {"file": "current-main.png", "kind": "current", "group": "main", "caption": "..."},
    {"file": "proposed-main.png", "kind": "proposed", "group": "main", "caption": "..."}
  ],
  "decisions": [{"question": "A choice that is the user's", "options": ["A", "B"], "recommendation": "A, because ..."}],
  "openInGame": ["What only a game check can settle"],
  "risks": ["Other mods, code-placed widgets, patched executable only, ..."],
  "effort": "S | M | L, and one sentence on what the build involves",
  "newFacts": ["Engine facts not in the register yet, with the evidence"]
}
```

**`decisions-final.json`** (orchestrator, stage 4): one entry per question of `design.json`, `{"question": "...", "chosen": "...", "by": "user | agent recommendation", "note": "..."}`. Where `by` is "agent recommendation" the builder follows the recommendation.

**`build/build.json`** (builder, stage 5):

```json
{
  "id": "A3",
  "agent": "builder-screen",
  "worktree": "C:\\dev\\hoi4-1440p-ui-mod",
  "summary": "What was built, two to four sentences.",
  "figures": [{"file": "build-main.png", "group": "main", "caption": "..."}],
  "deviations": [{"what": "Where the build differs from the design", "why": "..."}],
  "fallbacks": [{"if": "What the game check might show", "then": "What to change"}],
  "notSeenInGame": ["..."],
  "gameCheck": "tools/Invoke-GameCheck.ps1 division_details",
  "checklist": ["Numbered items for the game checker"],
  "sharedFiles": ["interface/1440p_ui.gfx"],
  "tests": "build.ps1 -Check division_details: 412 passed, 0 failed",
  "newFacts": ["Candidate engine facts with evidence"]
}
```

**`checks/check-<n>.json`** (game checker, stage 8), one per round:

```json
{
  "id": "A3",
  "round": 1,
  "date": "2026-10-17",
  "build": "80e628d+dirty",
  "playset": "this mod only | Reordered Pack (USA)",
  "launches": [{"command": "tools/Invoke-GameCheck.ps1 division_details", "captures": ["scratch/checks/division_details_crop.png"], "clock": "1 Jan 1936", "errorLog": ["lines the vanilla baseline does not have"]}],
  "checklist": [{"item": 1, "result": "pass | fail | cannot see", "evidence": "scratch/checks/...png", "note": "..."}],
  "defects": [{"what": "...", "where": "scene/widget", "evidence": "..."}],
  "forTheUser": ["What a crop cannot settle"],
  "autosave": "unchanged | not touched | hash differs",
  "newFacts": ["..."]
}
```

## Several screens at once

The orchestrator may run several designers in parallel, and several builders each in its own worktree; the rules for the worktrees, the merge and the shared files are in [Contributing](Contributing.md), "Several screens at once". The contracts are written before the first agent starts. One design page carries every proposal, one report every check.
