# Reference captures

One capture of every screen the mod works on or plans to, taken by `tools/Invoke-GameCheck.ps1 -SaveReference` at 2560x1440 in a paused 1936 game as Germany. Use them to plan a redesign, to compare before and after, and to see what a game update changed.

- `vanilla/` is the game without the mod. `mod/` is the screen as the mod last left it, for the screens it has reworked.
- `<screen>.jpg` is the whole frame, compressed: what is beside the panel and where it could grow.
- `<screen>-panel.png` is the panel region at 1:1 without loss: read text and measure edges here, never in the JPEG.
- `harness/` holds the menu screens the harness clicks through; the click positions are in `tools/GameHarness.ps1`.
- `manifest.csv` records the game version and date of each capture. This file is rewritten from it; do not edit it by hand.

How each screen is brought up is in [wiki/Game-Recipes.md](../wiki/Game-Recipes.md). To refresh, for example after a game update:

```powershell
.\tools\Invoke-GameCheck.ps1 -All -Vanilla -SaveReference        # every screen without the mod, about six minutes
.\tools\Invoke-GameCheck.ps1 army_selection -SaveReference        # one screen with the mod, when its phase closes
```

`python -I tools\render_gui.py --scene <screen> --over` draws a proposal on top of the vanilla frame.

## Vanilla

| Phase | Screen | Frame | Panel | Game | Date |
|---|---|---|---|---|---|
| A1 | air groups panel | [air_group.jpg](vanilla/air_group.jpg) | [air_group-panel.png](vanilla/air_group-panel.png) | 1.19.3.0 | 2026-10-08 |
| A1 | air wings and airbases screen | [air_selection.jpg](vanilla/air_selection.jpg) | [air_selection-panel.png](vanilla/air_selection-panel.png) | 1.19.3.0 | 2026-10-08 |
| A2 | selected-army screen | [army_selection.jpg](vanilla/army_selection.jpg) | [army_selection-panel.png](vanilla/army_selection-panel.png) | 1.19.3.0 | 2026-10-08 |
| A2 | selected-army screen, template-dropdown | [army_selection-template-dropdown.jpg](vanilla/army_selection-template-dropdown.jpg) | [army_selection-template-dropdown-panel.png](vanilla/army_selection-template-dropdown-panel.png) | 1.19.3.0 | 2026-10-08 |
| A3 | air wing details window | [air_wing_details.jpg](vanilla/air_wing_details.jpg) | [air_wing_details-panel.png](vanilla/air_wing_details-panel.png) | 1.19.3.0 | 2026-10-08 |
| A3 | division details window (Unit Details) | [division_details.jpg](vanilla/division_details.jpg) | [division_details-panel.png](vanilla/division_details-panel.png) | 1.19.3.0 | 2026-10-08 |
| A3 | division details window (Unit Details), history | [division_details-history.jpg](vanilla/division_details-history.jpg) | [division_details-history-panel.png](vanilla/division_details-history-panel.png) | 1.19.3.0 | 2026-10-08 |
| A3 | division details window (Unit Details), motorised | [division_details-motorised.jpg](vanilla/division_details-motorised.jpg) | [division_details-motorised-panel.png](vanilla/division_details-motorised-panel.png) | 1.19.3.0 | 2026-10-08 |
| A3 | division details window (Unit Details), name-dropdown | [division_details-name-dropdown.jpg](vanilla/division_details-name-dropdown.jpg) | [division_details-name-dropdown-panel.png](vanilla/division_details-name-dropdown-panel.png) | 1.19.3.0 | 2026-10-08 |
| A3 | division details window (Unit Details), tank | [division_details-tank.jpg](vanilla/division_details-tank.jpg) | [division_details-tank-panel.png](vanilla/division_details-tank-panel.png) | 1.19.3.0 | 2026-10-08 |
| A3 | division details window (Unit Details), tank-template | [division_details-tank-template.jpg](vanilla/division_details-tank-template.jpg) | [division_details-tank-template-panel.png](vanilla/division_details-tank-template-panel.png) | 1.19.3.0 | 2026-10-08 |
| A3 | division details window (Unit Details), template | [division_details-template.jpg](vanilla/division_details-template.jpg) | [division_details-template-panel.png](vanilla/division_details-template-panel.png) | 1.19.3.0 | 2026-10-08 |
| A3 | division details window (Unit Details), template-dropdown | [division_details-template-dropdown.jpg](vanilla/division_details-template-dropdown.jpg) | [division_details-template-dropdown-panel.png](vanilla/division_details-template-dropdown-panel.png) | 1.19.3.0 | 2026-10-08 |
| A3 | ship details window | [ship_details.jpg](vanilla/ship_details.jpg) | [ship_details-panel.png](vanilla/ship_details-panel.png) | 1.19.3.0 | 2026-10-08 |
| A3 | ship details window, carrier | [ship_details-carrier.jpg](vanilla/ship_details-carrier.jpg) | [ship_details-carrier-panel.png](vanilla/ship_details-carrier-panel.png) | 1.19.3.0 | 2026-10-08 |
| A3 | ship details window, history | [ship_details-history.jpg](vanilla/ship_details-history.jpg) | [ship_details-history-panel.png](vanilla/ship_details-history-panel.png) | 1.19.3.0 | 2026-10-08 |
| A4 | navy and fleet panel | [fleet.jpg](vanilla/fleet.jpg) | [fleet-panel.png](vanilla/fleet-panel.png) | 1.19.3.0 | 2026-10-08 |
| A4 | navy and fleet panel, composition | [fleet-composition.jpg](vanilla/fleet-composition.jpg) | [fleet-composition-panel.png](vanilla/fleet-composition-panel.png) | 1.19.3.0 | 2026-10-08 |
| A4 | navy and fleet panel, home-base | [fleet-home-base.jpg](vanilla/fleet-home-base.jpg) | [fleet-home-base-panel.png](vanilla/fleet-home-base-panel.png) | 1.19.3.0 | 2026-10-08 |
| A5 | Recruit & Deploy and Division Templates panels | [recruit_deploy.jpg](vanilla/recruit_deploy.jpg) | [recruit_deploy-panel.png](vanilla/recruit_deploy-panel.png) | 1.19.3.0 | 2026-10-08 |
| A6 | army overview tab | [army_overview.jpg](vanilla/army_overview.jpg) | [army_overview-panel.png](vanilla/army_overview-panel.png) | 1.19.3.0 | 2026-10-08 |
| A6 | army overview tab, air | [army_overview-air.jpg](vanilla/army_overview-air.jpg) | [army_overview-air-panel.png](vanilla/army_overview-air-panel.png) | 1.19.3.0 | 2026-10-08 |
| A6 | army overview tab, navy | [army_overview-navy.jpg](vanilla/army_overview-navy.jpg) | [army_overview-navy-panel.png](vanilla/army_overview-navy-panel.png) | 1.19.3.0 | 2026-10-08 |
| A7 | air wing reorganisation window | [air_wing_reorg.jpg](vanilla/air_wing_reorg.jpg) | [air_wing_reorg-panel.png](vanilla/air_wing_reorg-panel.png) | 1.19.3.0 | 2026-10-08 |
| A8 | theatre bar at the bottom | [theatre_bar.jpg](vanilla/theatre_bar.jpg) | [theatre_bar-panel.png](vanilla/theatre_bar-panel.png) | 1.19.3.0 | 2026-10-08 |
| B1 | division designer | [division_designer.jpg](vanilla/division_designer.jpg) | [division_designer-panel.png](vanilla/division_designer-panel.png) | 1.19.3.0 | 2026-10-08 |
| B2 | tank designer | [tank_designer.jpg](vanilla/tank_designer.jpg) | [tank_designer-panel.png](vanilla/tank_designer-panel.png) | 1.19.3.0 | 2026-10-08 |
| B3 | plane designer | [plane_designer.jpg](vanilla/plane_designer.jpg) | [plane_designer-panel.png](vanilla/plane_designer-panel.png) | 1.19.3.0 | 2026-10-08 |
| B4 | ship designer | [ship_designer.jpg](vanilla/ship_designer.jpg) | [ship_designer-panel.png](vanilla/ship_designer-panel.png) | 1.19.3.0 | 2026-10-08 |
| C | advisor selection popup | [advisor_selection.jpg](vanilla/advisor_selection.jpg) | [advisor_selection-panel.png](vanilla/advisor_selection-panel.png) | 1.19.3.0 | 2026-10-08 |
| C | construction panel | [construction.jpg](vanilla/construction.jpg) | [construction-panel.png](vanilla/construction-panel.png) | 1.19.3.0 | 2026-10-08 |
| C | events and decisions panel | [decisions.jpg](vanilla/decisions.jpg) | [decisions-panel.png](vanilla/decisions-panel.png) | 1.19.3.0 | 2026-10-08 |
| C | faction panel | [faction.jpg](vanilla/faction.jpg) | [faction-panel.png](vanilla/faction-panel.png) | 1.19.3.0 | 2026-10-08 |
| C | national focus tree | [focus_tree.jpg](vanilla/focus_tree.jpg) | [focus_tree-panel.png](vanilla/focus_tree-panel.png) | 1.19.3.0 | 2026-10-08 |
| C | intelligence agency panel | [intelligence.jpg](vanilla/intelligence.jpg) | [intelligence-panel.png](vanilla/intelligence-panel.png) | 1.19.3.0 | 2026-10-08 |
| C | international market panel | [international_market.jpg](vanilla/international_market.jpg) | [international_market-panel.png](vanilla/international_market-panel.png) | 1.19.3.0 | 2026-10-08 |
| C | general selection popup | [leader_selection.jpg](vanilla/leader_selection.jpg) | [leader_selection-panel.png](vanilla/leader_selection-panel.png) | 1.19.3.0 | 2026-10-08 |
| C | logistics panel | [logistics.jpg](vanilla/logistics.jpg) | [logistics-panel.png](vanilla/logistics-panel.png) | 1.19.3.0 | 2026-10-08 |
| C | officer corps panel | [officer_corps.jpg](vanilla/officer_corps.jpg) | [officer_corps-panel.png](vanilla/officer_corps-panel.png) | 1.19.3.0 | 2026-10-08 |
| C | politics panel | [politics.jpg](vanilla/politics.jpg) | [politics-panel.png](vanilla/politics-panel.png) | 1.19.3.0 | 2026-10-08 |
| C | production panel | [production.jpg](vanilla/production.jpg) | [production-panel.png](vanilla/production-panel.png) | 1.19.3.0 | 2026-10-08 |
| C | research panel | [research.jpg](vanilla/research.jpg) | [research-panel.png](vanilla/research-panel.png) | 1.19.3.0 | 2026-10-08 |
| C | technology tree | [tech_tree.jpg](vanilla/tech_tree.jpg) | [tech_tree-panel.png](vanilla/tech_tree-panel.png) | 1.19.3.0 | 2026-10-08 |
| C | trade panel | [trade.jpg](vanilla/trade.jpg) | [trade-panel.png](vanilla/trade-panel.png) | 1.19.3.0 | 2026-10-08 |

## With the mod

| Phase | Screen | Frame | Panel | Game | Mod | Date |
|---|---|---|---|---|---|---|
| A1 | air groups panel | [air_group.jpg](mod/air_group.jpg) | [air_group-panel.png](mod/air_group-panel.png) | 1.19.3.0 | 1.1 | 2026-10-08 |
| A1 | air wings and airbases screen | [air_selection.jpg](mod/air_selection.jpg) | [air_selection-panel.png](mod/air_selection-panel.png) | 1.19.3.0 | 1.1 | 2026-10-08 |
| A2 | selected-army screen | [army_selection.jpg](mod/army_selection.jpg) | [army_selection-panel.png](mod/army_selection-panel.png) | 1.19.3.0 | 1.2 | 2026-10-09 |
| A2 | selected-army screen, template-dropdown | [army_selection-template-dropdown.jpg](mod/army_selection-template-dropdown.jpg) | [army_selection-template-dropdown-panel.png](mod/army_selection-template-dropdown-panel.png) | 1.19.3.0 | 1.2 | 2026-10-09 |
| A3 | air wing details window | [air_wing_details.jpg](mod/air_wing_details.jpg) | [air_wing_details-panel.png](mod/air_wing_details-panel.png) | 1.19.3.0 | 1.2 | 2026-10-09 |
| A3 | division details window (Unit Details) | [division_details.jpg](mod/division_details.jpg) | [division_details-panel.png](mod/division_details-panel.png) | 1.19.3.0 | 1.2 | 2026-10-09 |
| A3 | division details window (Unit Details), history | [division_details-history.jpg](mod/division_details-history.jpg) | [division_details-history-panel.png](mod/division_details-history-panel.png) | 1.19.3.0 | 1.2 | 2026-10-09 |
| A3 | division details window (Unit Details), motorised | [division_details-motorised.jpg](mod/division_details-motorised.jpg) | [division_details-motorised-panel.png](mod/division_details-motorised-panel.png) | 1.19.3.0 | 1.2 | 2026-10-09 |
| A3 | division details window (Unit Details), name-dropdown | [division_details-name-dropdown.jpg](mod/division_details-name-dropdown.jpg) | [division_details-name-dropdown-panel.png](mod/division_details-name-dropdown-panel.png) | 1.19.3.0 | 1.2 | 2026-10-09 |
| A3 | division details window (Unit Details), tank | [division_details-tank.jpg](mod/division_details-tank.jpg) | [division_details-tank-panel.png](mod/division_details-tank-panel.png) | 1.19.3.0 | 1.2 | 2026-10-09 |
| A3 | division details window (Unit Details), tank-template | [division_details-tank-template.jpg](mod/division_details-tank-template.jpg) | [division_details-tank-template-panel.png](mod/division_details-tank-template-panel.png) | 1.19.3.0 | 1.2 | 2026-10-09 |
| A3 | division details window (Unit Details), template | [division_details-template.jpg](mod/division_details-template.jpg) | [division_details-template-panel.png](mod/division_details-template-panel.png) | 1.19.3.0 | 1.2 | 2026-10-09 |
| A3 | division details window (Unit Details), template-dropdown | [division_details-template-dropdown.jpg](mod/division_details-template-dropdown.jpg) | [division_details-template-dropdown-panel.png](mod/division_details-template-dropdown-panel.png) | 1.19.3.0 | 1.2 | 2026-10-09 |
| A3 | ship details window | [ship_details.jpg](mod/ship_details.jpg) | [ship_details-panel.png](mod/ship_details-panel.png) | 1.19.3.0 | 1.2 | 2026-10-09 |
| A3 | ship details window, carrier | [ship_details-carrier.jpg](mod/ship_details-carrier.jpg) | [ship_details-carrier-panel.png](mod/ship_details-carrier-panel.png) | 1.19.3.0 | 1.2 | 2026-10-09 |
| A3 | ship details window, history | [ship_details-history.jpg](mod/ship_details-history.jpg) | [ship_details-history-panel.png](mod/ship_details-history-panel.png) | 1.19.3.0 | 1.2 | 2026-10-09 |
