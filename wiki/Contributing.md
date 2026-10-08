# Contributing to HOI4 1440p UI Mod

## Development Workflow
1. Clone the repository.
2. Run `build.ps1 -DevLink` to link the mod directly to your Hearts of Iron IV launcher.
3. Read the [Roadmap](Roadmap.md) for what is being worked on and the [Design Rules](Design-Rules.md) for the rules every screen follows.
4. Make your modifications, following the recipe in the Design Rules. Keep `tools/gui-links.json` and `tools/scenes/<screen>.json` current.
5. Run `build.ps1 -Check <screen>`: validation, the Pester suites and the scene render (`scratch/previews/`). Python 3 with Pillow is needed for the render.
6. Check in the game with `tools/Invoke-GameCheck.ps1 <screen>`: it restarts the game, brings the screen up and writes a capture and a crop to `scratch/checks/` in about two minutes, without a human. Log the launch in `wiki/phases/<screen>.md`.
