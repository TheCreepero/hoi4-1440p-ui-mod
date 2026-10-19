---
name: phase
description: Run or continue a phase of the HOI4 1440p UI Mod as its orchestrator, through the stages of wiki/Workflow.md: brief the designer, review the design, publish the design page, get the user's approval, brief the builder, review the build, get the user's grant for the launches, brief the game checker, review the captures, run fix rounds, report to the user, close. Use when the user says /phase <id>, asks to start, continue or finish a phase, or to design, build or check a screen or page.
---

# /phase <id> [<scene> ...] [from <stage>]

You are the orchestrator of one phase (`<id>` is the roadmap id, such as `A3` or `E2`; the scenes are the `tools/scenes/*.json` names it touches). Invoking this skill is the user's standing request to spawn the agents named below; spawn no other kind. Read `wiki/Workflow.md` first, then `AGENTS.md` and `wiki/Working-Rules.md` (the long form of the rules: GUI invariants, scripted GUI rules, how a result is seen and checked, the roles), then the phase's row in `wiki/Roadmap.md` and its notes in `wiki/phases/<id>.md`; the recipe steps are in `wiki/Design-Rules.md`. For a scripted page add `wiki/Scripted-GUIs.md`, `wiki/Roleplay-Pages.md` and `wiki/Script-Reference.md`. Look `wiki/Engine-Facts.md` up by row (W34, X66) when a rule cites one; do not read it whole.

Find where the phase stands before doing anything: `wiki/phases/<id>.md` (its sections and the last dated line), `scratch/phases/<id>/` (which handoff files exist), `git status`. Continue from there; `from <stage>` overrides.

## Stage checklist

Tick each stage in your own working notes as it closes. Never skip a user gate.

1. **Open.** Phase notes from `wiki/Phase-Template.md` if missing (fill Scope and "Roles and handoffs"). `scratch/phases/<id>/` created. `contracts.md` written: taken hotkeys (`grep -rn 'shortcut = "' interface/ tools/build_managers.py tools/build_records.py`), new hotkeys, shared rows and windows, shared files and owners, shared frames. Builder chosen: `builder-screen` for a vanilla screen, `builder-script` for a scripted page. One screen: main tree; several: one worktree per builder, made as `wiki/Contributing.md` says.
2. **Design.** Spawn `designer` with: the id, the scenes, the output folder, the contracts path, what the user asked for in their own words, and the reply length. Background it; do other preparation meanwhile.
3. **Gate A.** Check `design.json` and the figures against the five points of `wiki/Workflow.md`, stage 3. Open every PNG with the Read tool. Send what fails back to the same designer with `SendMessage`, naming each point. Then build the design page (HTML, images embedded, vanilla beside mock-up at the same scale, what changes and why, the decisions with recommendations, what is open) and publish it with the Artifact tool; put the link into the phase notes under "Roles and handoffs".
4. **User gate 1.** Give the user the link and the numbered decisions. Stop here until they answer. Then write the answers, dated, under "Decisions" in the phase notes and into `decisions-final.json`.
5. **Build.** Spawn the chosen builder with: the id, the tree to work in, the paths of `design.json`, `decisions-final.json`, `contracts.md`, the scenes, and the reply length. Background it.
6. **Gate B.** Run `tools/Compare-Baseline.ps1 <file> -Group` yourself and read every line. Open every `build-<group>.png` beside its mock-up. Read the deviations and `build.json`. Run `powershell -File .\build.ps1 -Check <scene>` yourself once if the builder's report does not show a green run. Send what fails back to the same builder. Add the build renders to the design page (same artifact URL).
7. **User gate 2.** Ask for the launches in one message: the scenes, the number of launches, whether time will run (ten days at most, autosave copied) and whether a playset mod will be loaded. Stop until the user grants it. A vague grant is not a grant: ask again naming the launches.
8. **Check.** Spawn `game-checker` with the user's grant quoted, the id, the `gameCheck` line and the scenes, the round number, and whether `-DevLink` is in place. Wait for it; nothing else uses the screen meanwhile.
9. **Capture review.** Read every crop in `scratch/checks/` yourself and the checker's `check-<n>.json`. Decide per finding: defect, renderer blind spot that the game settled, or the user's to judge. Defects go to the same builder (`SendMessage`), with the capture paths; a cause nobody knows goes to `builder-script` even for a screen. After the fix, gate B again, then the checker again for the scenes the fix touched (within the grant, or ask again). Repeat until clean.
10. **Report, user gate 3.** One message: what was built; the design page link, now with build renders; the checks (how many, with which mods loaded, what they showed); the numbered list of what only the user can settle (tooltips, click targets, states a 1936 start does not show, widths); the files changed, uncommitted. Stop. The user tests in their own game and commits.
11. **Close**, when the user says the phase is done: recipe step 8 of `wiki/Design-Rules.md`; `newFacts` of every handoff into the knowledge register with `Add-HoiKnowledge.ps1` or dropped with a reason; `Export-HoiKnowledge.ps1 -Repo hoi4-1440p-ui-mod`; `-SaveReference` with the user's grant; Roadmap, README, Workshop text, `version`.

## Rules for the orchestrator

- Continue an agent with `SendMessage` while it exists; spawn a new one only when it is gone. Each agent starts cold, so the brief names every file it needs and nothing it does not.
- Never start the game yourself and never let an agent start it without the user's grant for exactly those launches. Never commit; the user does.
- Review means reading the artefact, not the agent's summary of it: the JSON, every PNG, the baseline diff, the test output.
- You alone write the knowledge register and `wiki/Roadmap.md`, `README.md`, `descriptor.mod`, `AGENTS.md`.
- Log every launch and every decision in `wiki/phases/<id>.md` the day it happens; the handoff files under `scratch/` are not in the repository.
- When the user brings issues from their own game (a list, screenshots), enter at stage 9 with them as findings.
