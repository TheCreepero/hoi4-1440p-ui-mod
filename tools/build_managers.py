"""Writes the mod's scripted GUIs (the "managers" of Milestone D) from the tables in this file.

    python -I tools/build_managers.py          write the files
    python -I tools/build_managers.py --check  exit 1 when a file on disk differs from what would be written

Everything it writes is generated: change this file, not its output. The game reads the output again while it
runs (wiki/Engine-Facts.md, X23), so a change here shows a few seconds after the script has run.

    interface/mod1440_<manager>.gui                         the containers
    common/scripted_guis/mod1440_<manager>.txt              what shows when, and what the buttons do
    common/scripted_effects/mod1440_effects.txt             the counting a click or a new day asks for
    common/on_actions/mod1440_on_actions.txt                the hooks that run the counting
    common/synchronized_dynamic_tokens/mod1440_tokens.txt   every name used after "@" (Engine Facts X24)
    localisation/<language>/mod1440_l_<language>.yml        the texts (UTF-8 with BOM), English under every language
    tools/scenes/<page>.json                                where each page stands, its recipe and sample values

Rules the output follows (wiki/Scripted-GUIs.md): a button changes the panel or moves the camera and nothing
else; own country only; names carry the prefix mod1440_; no loop in anything drawn every tick.
"""
import io
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

FONT_TITLE = "hoi_36header"
FONT_CARD = "hoi_24header"
FONT_LABEL = "hoi_18mbs"
FONT_VALUE = "hoi_20b"
FONT_SMALL = "hoi_16mbs"

PAGE_BG = "GFX_tiled_window_1b_thin_border"
CARD_BG = "GFX_tiled_plain_bg_small"

# the languages the game ships (the folders of its localisation directory)
LANGUAGES = ["english", "braz_por", "french", "german", "japanese", "korean", "polish", "russian", "simp_chinese", "spanish"]


# ---------------------------------------------------------------- output collectors

class Build:
    def __init__(self):
        self.loc = {}       # key -> text
        self.files = {}     # relative path -> content

    def key(self, name, value):
        """Registers a text of the mod and returns its localisation key."""
        key = "MOD1440_" + name.upper()
        if key in self.loc and self.loc[key] != value:
            raise ValueError("two texts for " + key)
        self.loc[key] = value
        return key


B = Build()


# ---------------------------------------------------------------- .gui pieces

def indent(text_block, tabs=1):
    return "".join(("\t" * tabs + line if line.strip() else line) for line in text_block.splitlines(True))


def text(name, x, y, width, key, font=FONT_LABEL, fmt="left", height=24, tooltip=None):
    tip = ' pdx_tooltip = "%s"' % tooltip if tooltip else ""
    return ('instantTextboxType = { name = "%s" position = { x = %d y = %d } font = "%s" text = "%s" '
            'maxWidth = %d maxHeight = %d format = %s%s }\n' % (name, x, y, font, key, width, height, fmt, tip))


def icon(name, x, y, sprite):
    return 'iconType = { name = "%s" position = { x = %d y = %d } spriteType = "%s" }\n' % (name, x, y, sprite)


def button(name, x, y, sprite, key=None, font=FONT_SMALL, shortcut=None, tooltip=None):
    extra = ""
    if key:
        extra += ' buttonFont = "%s" buttonText = "%s"' % (font, key)
    if shortcut:
        extra += ' shortcut = "%s"' % shortcut
    if tooltip:
        extra += ' pdx_tooltip = "%s"' % tooltip
    return ('buttonType = { name = "%s" position = { x = %d y = %d } quadTextureSprite = "%s" '
            'clicksound = click_default%s }\n' % (name, x, y, sprite, extra))


def box(name, x, y, width, height, body, background=None):
    bg = '\tbackground = { name = "Background" quadTextureSprite = "%s" }\n' % background if background else ""
    return ('containerWindowType = {\n\tname = "%s"\n\tposition = { x = %d y = %d }\n'
            '\tsize = { width = %d height = %d }\n%s%s}\n' % (name, x, y, width, height, bg, indent(body)))


# ---------------------------------------------------------------- script pieces

def block(name, body):
    return "%s = {\n%s}\n" % (name, indent(body))


def scripted_gui(name, window, parent=None, visible="always = yes\n", effects="", triggers="", properties="",
                 lists="", dirty=None):
    body = 'context_type = player_context\nwindow_name = "%s"\n' % window
    if parent:
        body += "parent_window_token = %s\n" % parent
    body += "\n" + block("visible", visible)
    if dirty:
        body += "\ndirty = %s\n" % dirty
    for key, part in (("dynamic_lists", lists), ("properties", properties), ("effects", effects), ("triggers", triggers)):
        if part:
            body += "\n" + block(key, part)
    # the panel is for the player's eyes: the AI never looks at it
    body += "\n" + block("ai_enabled", "always = no\n")
    return block(name, body)


def more_than_zero(variable):
    return "check_variable = { %s > 0 }\n" % variable


# ---------------------------------------------------------------- Army readiness (D2), docked to Recruit & Deploy

# Land equipment in the order of the logistics tab. The name of each row is the game's own text for the
# archetype, so it follows the player's language. Tank rows use the chassis of No Step Back.
EQUIPMENT = [
    "infantry_equipment", "support_equipment", "artillery_equipment", "anti_tank_equipment", "anti_air_equipment",
    "rocket_artillery_equipment", "motorized_equipment", "mechanized_equipment", "armored_car_equipment",
    "motorized_rocket_equipment", "light_tank_chassis", "medium_tank_chassis", "heavy_tank_chassis",
    "modern_tank_chassis", "amphibious_tank_chassis", "amphibious_mechanized_equipment",
]

# From the corner of the Recruit & Deploy panel (screen -6,78): beside the template panel, which ends at 1246.
# 975 wide: it stops short of the theatre box under the clock (screen x 2234).
AR_X, AR_Y, AR_W = 1256, 0, 975
AR_H = 1210                     # ends where the template panel ends, above the army portraits of the bottom bar
AR_LEFT = 290                   # width of the two cards on the left
AR_HEAD = 60                    # height of the title strip
ROW = 30


def value_rows(prefix, rows, width, label_width):
    """Label on the left, value on the right. A row is (name, label, value) or, for a value that reads "0.0"
    at zero, (name, label, value, variable): the value then shows only above zero, and a plain 0 otherwise."""
    out, triggers = "", ""
    for i, row in enumerate(rows):
        name, label, value = row[:3]
        y = 46 + i * ROW
        out += text("%s_label_%s" % (prefix, name), 16, y, label_width, B.key("%s_%s" % (prefix, name), label))
        out += text("%s_value_%s" % (prefix, name), width - 16 - 100, y - 1, 100,
                    B.key("%s_%s_v" % (prefix, name), value), FONT_VALUE, "right")
        if len(row) > 3:
            out += text("%s_zero_%s" % (prefix, name), width - 16 - 100, y - 1, 100, "0", FONT_VALUE, "right")
            triggers += block("%s_value_%s_visible" % (prefix, name), more_than_zero(row[3]))
            triggers += block("%s_zero_%s_visible" % (prefix, name), "NOT = { %s }\n" % more_than_zero(row[3]).strip())
    return out, triggers


def army_readiness():
    effects = ""
    triggers = ""
    properties = ""
    counted = more_than_zero("mod1440_ar_counted")

    # ---- title strip
    body = box("ar_head", 3, 3, AR_W - 6, 50, "", "GFX_tiled_header")
    body += text("ar_title", 22, 8, 500, B.key("ar_title", "Army Readiness"), FONT_TITLE, height=40)
    body += text("ar_hint", AR_W - 330, 18, 250, B.key("ar_hint", "Shift+M hides this page"), FONT_SMALL, "right")
    body += button("ar_fold", AR_W - 66, 10, "GFX_closebutton", shortcut="shift+m",
                   tooltip=B.key("ar_fold_tt", "Hide this page and give the map back"))
    effects += block("ar_fold_click", "set_variable = { mod1440_ar_folded = 1 }\n")

    # ---- manpower
    rows = [
        ("free", "Free", "[?manpower_k|0]K"),
        ("training", "In training", "[?amount_manpower_in_deployment_queue|*1]", "amount_manpower_in_deployment_queue"),
        ("army", "In the army", "[?deployed_army_manpower_k|0]K"),
        ("navy", "In the navy", "[?deployed_navy_manpower_k|0]K"),
        ("air", "In the air force", "[?deployed_airforce_manpower_k|0]K"),
        ("garrison", "Needed by garrisons", "[?garrison_manpower_need|*1]", "garrison_manpower_need"),
    ]
    card = text("ar_mp_title", 14, 8, AR_LEFT - 28, B.key("ar_mp_title", "Manpower"), FONT_CARD, height=30)
    part, more = value_rows("ar_mp", rows, AR_LEFT, 180)
    card += part
    triggers += more
    manpower_h = 46 + len(rows) * ROW + 14
    body += box("ar_manpower", 14, AR_HEAD, AR_LEFT, manpower_h, card, CARD_BG)

    # ---- army: two values of the game, two counts of the mod
    rows = [
        ("divisions", "Divisions", "[?num_divisions|0]"),
        ("battalions", "Battalions", "[?num_battalions|0]"),
        ("xp", "Army experience", "[?army_experience|0]"),
        ("low_str", "Below 75% strength", "[?mod1440_ar_low_str|0]"),
        ("low_org", "Below 50% organisation", "[?mod1440_ar_low_org|0]"),
    ]
    card = text("ar_army_title", 14, 8, AR_LEFT - 28, B.key("ar_army_title", "Army"), FONT_CARD, height=30)
    part, more = value_rows("ar_army", rows, AR_LEFT, 200)
    card += part
    y = 46 + len(rows) * ROW + 8
    card += button("ar_count", 14, y, "GFX_button_123x34", B.key("ar_count", "Count again"), tooltip=B.key(
        "ar_count_tt", "Goes through every division once. The two counts above and the bars on the right are from the last time this ran: at the start of each day, and on this button."))
    card += text("ar_counted", 140, y + 8, AR_LEFT - 140 - 16, B.key("ar_counted", "[?mod1440_ar_counted.GetDateStringNoHour]"), FONT_SMALL, "right")
    effects += block("ar_count_click", "mod1440_ar_count = yes\n")
    for name in ("ar_army_value_low_str", "ar_army_value_low_org", "ar_counted"):
        triggers += block(name + "_visible", counted)
    body += box("ar_army", 14, AR_HEAD + manpower_h + 12, AR_LEFT, y + 34 + 14, card, CARD_BG)

    # ---- equipment: a table with one row per kind
    x0 = 14 + AR_LEFT + 12
    width = AR_W - x0 - 14
    col_stock, col_field, col_need, col_bar = 330, 420, 510, 526      # right edges of the numbers, left edge of the bar
    card = text("ar_eq_title", 14, 8, 220, B.key("ar_eq_title", "Equipment"), FONT_CARD, height=30)
    for name, x, label, tip in (
            ("stock", col_stock, "In stock", "Equipment in the stockpile that no division and no training has taken: the number of the logistics tab."),
            ("field", col_field, "In the field", "Equipment in the hands of the divisions in the field. Red when it is less than they need."),
            ("need", col_need, "Needed", "What the templates of the divisions in the field ask for. Divisions in training are not counted.")):
        card += text("ar_eq_head_%s" % name, x - 90, 16, 90, B.key("ar_eq_head_%s" % name, label), FONT_SMALL, "right",
                     tooltip=B.key("ar_eq_head_%s_tt" % name, tip))
    card += text("ar_eq_head_bar", col_bar, 16, 105, B.key("ar_eq_head_bar", "Equipped"), FONT_SMALL,
                 tooltip=B.key("ar_eq_head_bar_tt", "In the field as a share of needed, as of the last count."))
    for i, eq in enumerate(EQUIPMENT):
        y = 46 + i * ROW
        stock, field, need = "num_equipment@" + eq, "num_equipment_in_armies@" + eq, "num_target_equipment_in_armies@" + eq
        used = block("OR", more_than_zero(stock) + more_than_zero(need))
        short = "check_variable = { var = %s value = %s compare = less_than }\n" % (field, need)
        card += text("ar_eq_name_%d" % i, 16, y, 246, eq)        # the game's own name of the archetype
        card += text("ar_eq_stock_%d" % i, col_stock - 84, y - 1, 84, B.key("ar_eq_stock_%d" % i, "[?%s|0]" % stock), FONT_VALUE, "right")
        card += text("ar_eq_field_%d" % i, col_field - 84, y - 1, 84, B.key("ar_eq_field_%d" % i, "[?%s|0]" % field), FONT_VALUE, "right")
        card += text("ar_eq_short_%d" % i, col_field - 84, y - 1, 84, B.key("ar_eq_short_%d" % i, "[?%s|R0]" % field), FONT_VALUE, "right")
        card += text("ar_eq_need_%d" % i, col_need - 84, y - 1, 84, B.key("ar_eq_need_%d" % i, "[?%s|0]" % need), FONT_VALUE, "right")
        card += icon("ar_eq_bar_%d" % i, col_bar, y + 6, "GFX_1440p_SG_bar")
        triggers += block("ar_eq_stock_%d_visible" % i, used)
        triggers += block("ar_eq_need_%d_visible" % i, used)
        triggers += block("ar_eq_field_%d_visible" % i, used + "NOT = { %s }\n" % short.strip())
        triggers += block("ar_eq_short_%d_visible" % i, short)
        triggers += block("ar_eq_bar_%d_visible" % i, more_than_zero(need) + counted)
        # a math expression is not accepted as a property ("Window not found" on reload): the fill is a variable
        properties += block("ar_eq_bar_%d" % i, "frame = mod1440_ar_fill_%d\n" % i)
    equipment_h = 46 + len(EQUIPMENT) * ROW + 14
    body += box("ar_equipment", x0, AR_HEAD, width, equipment_h, card, CARD_BG)

    # ---- armies: one row per general who has troops
    armies_y = AR_HEAD + equipment_h + 12
    armies_h = AR_H - armies_y - 14
    row_w = AR_W - 28 - 30
    # (name, caption, right edge or left edge for the first, width, value, tip, hide at zero)
    columns = [
        ("name", "General", 10, 220, "[THIS.GetName]", "A general or field marshal who commands troops. An army without a commander cannot be listed.", False),
        ("skill", "Skill", 290, 50, "[?skill_level|0]", "The general's skill level.", False),
        ("divisions", "Divisions", 372, 76, "[?num_units|0]", "Divisions under this commander.", False),
        ("battalions", "Battalions", 462, 84, "[?num_battalions|0]", "Battalions under this commander.", False),
        ("fighting", "Fighting", 540, 72, "[?num_units_in_combat|0]", "Divisions of this commander that are in combat now.", True),
        ("planning", "Planning", 628, 82, "[?avg_unit_planning_ratio|%0]", "The planning bonus the divisions have built up, as a share of the most they can have.", False),
        ("fill", "Equipment", 800, 46, "[?mod1440_al_fill|0]%", "The worst equipped kind of equipment of this army: what it has as a share of what its templates ask for, as of the last count.", False),
        ("inf", "Inf", 838, 36, "[?num_infantry|0]", "Divisions that are mostly infantry.", True),
        ("arm", "Arm", 876, 36, "[?num_armored|0]", "Divisions that are mostly armour.", True),
        ("mot", "Mot", 914, 36, "[?num_motorized|0]", "Divisions that are mostly motorised.", True),
    ]
    zero_test = {"fighting": "num_units_in_combat", "inf": "num_infantry", "arm": "num_armored", "mot": "num_motorized"}
    card = text("ar_al_title", 14, 8, 220, B.key("ar_al_title", "Armies"), FONT_CARD, height=30)
    row = ""
    row_triggers = ""
    for name, caption, edge, w, value, tip, hide in columns:
        left = edge if name == "name" else edge - w
        align = "left" if name == "name" else "right"
        # heads sit over their column; "Equipment" is wider than its number and reaches over the bar
        wider = 30 if name == "fill" else 0
        card += text("ar_al_head_%s" % name, 14 + left - wider, 40, w + wider,
                     B.key("ar_al_head_%s" % name, caption), FONT_SMALL, align, tooltip=B.key("ar_al_head_%s_tt" % name, tip))
        row += text("ar_row_%s" % name, left, 4, w, B.key("ar_row_%s" % name, value), FONT_LABEL, align, 22)
        if hide:
            row_triggers += block("ar_row_%s_visible" % name, more_than_zero(zero_test[name]))
    row += icon("ar_row_bar", 644, 10, "GFX_1440p_SG_bar")
    properties += block("ar_row_bar", "frame = mod1440_al_fill\n")
    card += text("ar_al_none", 24, 70, 700, B.key("ar_al_none", "No army has a commander yet. An army is listed here once it has one."), FONT_SMALL)
    triggers += block("ar_al_none_visible", "check_variable = { mod1440_ar_leaders^num < 1 }\n")
    grid = ('gridboxtype = {\n\tname = "ar_al_grid"\n\tposition = { x = 0 y = 0 }\n\tsize = { width = %d height = 100%%%% }\n'
            '\tslotsize = { width = 1 height = 1 }\n\tadd_horizontal = no\n\tformat = "UPPER_LEFT"\n}\n' % row_w)
    card += ('containerWindowType = {\n\tname = "ar_al_list"\n\tposition = { x = 14 y = 64 }\n\tsize = { width = %d height = %d }\n'
             '\tverticalScrollbar = "right_vertical_slider"\n\tscroll_wheel_factor = %d\n\tsmooth_scrolling = yes\n%s}\n'
             % (row_w + 30 - 14, armies_h - 64 - 14, ROW * 3, indent(grid)))
    body += box("ar_armies", 14, armies_y, AR_W - 28, armies_h, card, CARD_BG)
    triggers += row_triggers

    gui = box("mod1440_army_readiness", AR_X, AR_Y, AR_W, AR_H, body, PAGE_BG)
    gui += ('containerWindowType = {\n\tname = "mod1440_army_readiness_row"\n\tsize = { width = %d height = %d }\n%s}\n'
            % (row_w, ROW, indent(row)))

    # ---- the handle that brings a hidden page back
    handle = button("ar_unfold", 0, 0, "GFX_button_148x34", B.key("ar_unfold", "Army Readiness"), shortcut="shift+m",
                    tooltip=B.key("ar_unfold_tt", "Show the Army Readiness page"))
    gui += box("mod1440_army_readiness_handle", AR_X, 8, 148, 34, handle)

    script = scripted_gui(
        "mod1440_army_readiness", "mod1440_army_readiness", "deployment_tab",
        visible="NOT = { check_variable = { mod1440_ar_folded = 1 } }\n",
        lists=block("ar_al_grid", 'array = mod1440_ar_leaders\nchange_scope = yes\nentry_container = "mod1440_army_readiness_row"\n'),
        effects=effects, triggers=triggers, properties=properties)
    script += "\n" + scripted_gui(
        "mod1440_army_readiness_handle", "mod1440_army_readiness_handle", "deployment_tab",
        visible="check_variable = { mod1440_ar_folded = 1 }\n",
        effects=block("ar_unfold_click", "set_variable = { mod1440_ar_folded = 0 }\nmod1440_ar_count = yes\n"))

    # A share is worked out as have / need * 100, dividing first: the product of a large stock and 100 is
    # more than a script number is sure to hold.
    fills = ""
    for i, eq in enumerate(EQUIPMENT):
        fills += "set_variable = { mod1440_ar_fill_%d = 0 }\n" % i + block("if", (
            "limit = { check_variable = { num_target_equipment_in_armies@%s > 0 } }\n"
            "set_variable = { mod1440_ar_fill_%d = num_equipment_in_armies@%s }\n"
            "divide_variable = { mod1440_ar_fill_%d = num_target_equipment_in_armies@%s }\n"
            "multiply_variable = { mod1440_ar_fill_%d = 100 }\n"
            "clamp_variable = { var = mod1440_ar_fill_%d min = 0 max = 100 }\n" % (eq, i, eq, i, eq, i, i)))
    worst = "set_variable = { mod1440_al_fill = 100 }\n"
    for eq in EQUIPMENT:
        worst += block("if", (
            "limit = { check_variable = { num_target_equipment@%s > 0 } }\n"
            "set_temp_variable = { al_share = num_equipment@%s }\n"
            "divide_temp_variable = { al_share = num_target_equipment@%s }\n"
            "multiply_temp_variable = { al_share = 100 }\n" % (eq, eq, eq)
            + block("if", "limit = { check_variable = { al_share < mod1440_al_fill } }\nset_variable = { mod1440_al_fill = al_share }\n")))
    leaders = ("clear_array = mod1440_ar_leaders\n" + block("for_each_scope_loop", (
        "array = army_leaders\n" + block("if", (
            "limit = { check_variable = { num_units > 0 } }\n" + worst
            + "add_to_array = { PREV.mod1440_ar_leaders = THIS }\n")))))
    count = (
        "# Army Readiness: the two division counts, the fill of the equipment bars and the list of generals with\n"
        "# troops, for the country in scope. Runs at the start of a game for every country, each day for a\n"
        "# player, and on a click.\n"
        + block("mod1440_ar_count",
                "set_variable = { mod1440_ar_low_str = 0 }\nset_variable = { mod1440_ar_low_org = 0 }\n"
                + block("every_country_division", "limit = { unit_strength < 0.75 }\nadd_to_variable = { PREV.mod1440_ar_low_str = 1 }\n")
                + block("every_country_division", "limit = { unit_organization < 0.5 }\nadd_to_variable = { PREV.mod1440_ar_low_org = 1 }\n")
                + fills + leaders
                + "set_variable = { mod1440_ar_counted = global.date }\n"))
    return gui, script, count


# ---------------------------------------------------------------- States (D3), docked to Construction

# One row per state the player controls. A column is (name, value of the state, width, head, tip): the head is
# ("text", caption), ("building", frame of GFX_buildings_strip) or ("resource", frame of GFX_resources_strip);
# the tip is a text of the game ("$key$") or of the mod.
STATE_COLUMNS = [
    ("free", "mod1440_st_free", 60, ("text", "Free"), "Free building slots for factories and the other buildings that share slots, counted when the list was made."),
    ("infra", "infrastructure_level", 52, ("building", 3), "$infrastructure$"),
    ("civ", "industrial_complex_level", 52, ("building", 1), "$industrial_complex$"),
    ("mil", "arms_factory_level", 52, ("building", 2), "$arms_factory$"),
    ("dock", "building_level@dockyard", 52, ("building", 4), "$dockyard$"),
    ("refinery", "building_level@synthetic_refinery", 52, ("building", 10), "$synthetic_refinery$"),
    ("silo", "building_level@fuel_silo", 52, ("building", 14), "$fuel_silo$"),
    ("air", "building_level@air_base", 52, ("building", 5), "$air_base$"),
    ("aa", "building_level@anti_air_building", 52, ("building", 9), "$anti_air_building$"),
    ("radar", "building_level@radar_station", 52, ("building", 11), "$radar_station$"),
    ("oil", "resource@oil", 56, ("resource", 1), "$PRODUCTION_MATERIALS_OIL$"),
    ("aluminium", "resource@aluminium", 56, ("resource", 2), "$PRODUCTION_MATERIALS_ALUMINIUM$"),
    ("rubber", "resource@rubber", 56, ("resource", 3), "$PRODUCTION_MATERIALS_RUBBER$"),
    ("tungsten", "resource@tungsten", 56, ("resource", 4), "$PRODUCTION_MATERIALS_TUNGSTEN$"),
    ("steel", "resource@steel", 56, ("resource", 5), "$PRODUCTION_MATERIALS_STEEL$"),
    ("chromium", "resource@chromium", 56, ("resource", 6), "$PRODUCTION_MATERIALS_CHROMIUM$"),
    ("coal", "resource@coal", 56, ("resource", 7), "$PRODUCTION_MATERIALS_COAL$"),
    ("pop", "state_population_k", 84, ("text", "People"), "Population of the state, in thousands."),
    ("compliance", "compliance", 60, ("text", "Compl."), "$COMPLIANCE$, for a state that is not a core of yours."),
    ("resistance", "resistance", 60, ("text", "Resist."), "$RESISTANCE$, for a state that is not a core of yours."),
]
HEAD_SPRITES = {52: "GFX_1440p_SG_head_52", 56: "GFX_1440p_SG_head_56", 60: "GFX_1440p_SG_head_60",
                84: "GFX_1440p_SG_head_84", 240: "GFX_1440p_SG_head_240"}

# From the corner of the construction panel (screen -9,78), whose building column ends at x 700.
ST_X, ST_Y = 712, 0
ST_NAME = 240
ST_ROWS_W = ST_NAME + sum(c[2] for c in STATE_COLUMNS)      # width of one row
ST_W = 14 + ST_ROWS_W + 30 + 14                             # the page: margins, rows, scrollbar
ST_H = 1210                                                 # ends above the army portraits of the bottom bar
ST_LIST_Y = 136
ST_ROW = 30


def free_slot_tree(low, high):
    """Script that finds how many shared building slots are free in the state in scope, between low and high.
    The trigger takes a written number only (Engine Facts X20), so the search is written out: five questions."""
    if low == high:
        return "set_variable = { mod1440_st_free = %d }\n" % low
    middle = (low + high) // 2
    question = block("free_building_slots", "building = industrial_complex\nsize > %d\ninclude_locked = no\n" % middle)
    return block("if", block("limit", question) + free_slot_tree(middle + 1, high)) + block("else", free_slot_tree(low, middle))


def states_table():
    effects = ""
    triggers = ""
    properties = ""

    # ---- title strip
    body = box("st_head", 3, 3, ST_W - 6, 50, "", "GFX_tiled_header")
    body += text("st_title", 22, 8, 400, B.key("st_title", "States"), FONT_TITLE, height=40)
    body += text("st_count", 330, 18, 300, B.key("st_count", "[?mod1440_st_rows^num|0] listed"), FONT_SMALL)
    body += text("st_hint", ST_W - 560, 18, 480, B.key("st_hint", "Click a state to see it on the map. Shift+M hides the page."), FONT_SMALL, "right")
    body += button("st_fold", ST_W - 66, 10, "GFX_closebutton", shortcut="shift+m",
                   tooltip=B.key("st_fold_tt", "Hide this page and give the map back"))
    effects += block("st_fold_click", "set_variable = { mod1440_st_open = 0 }\nadd_to_variable = { mod1440_st_dirty = 1 }\n")

    # ---- which states: three choices and a switch, each a button with a second frame for "chosen"
    choices = [("all", "All", 0, "Every state you control."), ("core", "Cores", 1, "Only the states that are cores of yours."),
               ("other", "Occupied", 2, "Only the states that are not cores of yours.")]
    for i, (name, label, value, tip) in enumerate(choices):
        body += button("st_show_%s" % name, 16 + i * 104, 62, "GFX_sort_button_100x29", B.key("st_show_%s" % name, label),
                       tooltip=B.key("st_show_%s_tt" % name, tip))
        effects += block("st_show_%s_click" % name, "set_variable = { mod1440_st_show = %d }\nmod1440_st_list = yes\n" % value)
        properties += block("st_show_%s" % name, "frame = mod1440_st_frame_%d\n" % value)
    body += button("st_only_free", 16 + 3 * 104 + 20, 62, "GFX_sort_button_140x29", B.key("st_only_free", "With free slots"),
                   tooltip=B.key("st_only_free_tt", "Only the states with a free slot for a factory."))
    effects += block("st_only_free_click", block("if", "limit = { check_variable = { mod1440_st_only_free = 1 } }\nset_variable = { mod1440_st_only_free = 0 }\n")
                     + block("else", "set_variable = { mod1440_st_only_free = 1 }\n") + "mod1440_st_list = yes\n")
    properties += block("st_only_free", "frame = mod1440_st_frame_free\n")
    body += button("st_refresh", 16 + 3 * 104 + 20 + 160, 62, "GFX_sort_button_100x29", B.key("st_refresh", "Refresh"),
                   tooltip=B.key("st_refresh_tt", "Makes the list again. It is made when the page opens, when you sort or choose, and at the start of each day while the page is open. The numbers of a row are from that moment."))
    effects += block("st_refresh_click", "mod1440_st_list = yes\n")

    # ---- column heads: a click sorts, a second click turns the order
    x = 14
    body += button("st_sort_name", x, 100, HEAD_SPRITES[ST_NAME], B.key("st_sort_name", "State"),
                   tooltip=B.key("st_sort_name_tt", "Back to the order of the game."))
    effects += block("st_sort_name_click", "set_variable = { mod1440_st_sort_by = 0 }\nmod1440_st_list = yes\n")
    x += ST_NAME
    keys = ""
    row = button("st_row", 0, 0, HEAD_SPRITES[ST_NAME], tooltip=B.key("st_row_tt", "Show this state on the map"))
    row += ('instantTextboxType = { name = "st_row_name" position = { x = 10 y = 4 } font = "%s" text = "%s" '
            'maxWidth = %d maxHeight = 22 format = left alwaystransparent = yes }\n'
            % (FONT_LABEL, B.key("st_row_name", "[THIS.GetName]"), ST_NAME - 16))
    row_triggers = ""
    rx = ST_NAME
    for number, (name, value, width, head, tip) in enumerate(STATE_COLUMNS, start=1):
        tip_key = B.key("st_sort_%s_tt" % name, tip + "\\nClick to sort, click again to turn the order.")
        if head[0] == "text":
            body += button("st_sort_%s" % name, x, 100, HEAD_SPRITES[width], B.key("st_sort_%s" % name, head[1]), tooltip=tip_key)
        else:
            body += button("st_sort_%s" % name, x, 100, HEAD_SPRITES[width], tooltip=tip_key)
            sprite, scale, dx, dy = (("GFX_buildings_strip", 0.6, 12, 1) if head[0] == "building" else ("GFX_resources_strip", 0.9, 16, 3))
            body += ('iconType = { name = "st_icon_%s" position = { x = %d y = %d } spriteType = "%s" frame = %d scale = %s '
                     'alwaystransparent = yes }\n' % (name, x + dx, 100 + dy, sprite, head[1], scale))
        effects += block("st_sort_%s_click" % name, (
            block("if", "limit = { check_variable = { mod1440_st_sort_by = %d } }\n" % number
                  + block("if", "limit = { check_variable = { mod1440_st_up = 1 } }\nset_variable = { mod1440_st_up = 0 }\n")
                  + block("else", "set_variable = { mod1440_st_up = 1 }\n"))
            + block("else", "set_variable = { mod1440_st_sort_by = %d }\nset_variable = { mod1440_st_up = 0 }\n" % number)
            + "set_variable = { mod1440_st_arrow_x = %d }\nmod1440_st_list = yes\n" % (x + width - 21)))
        keys += block("if" if number == 1 else "else_if",
                      "limit = { check_variable = { ROOT.mod1440_st_sort_by = %d } }\nset_temp_variable = { st_key = %s }\n" % (number, value))
        fmt = "|0]K" if name == "pop" else "|0]"
        row += text("st_cell_%s" % name, rx + 2, 4, width - 10, B.key("st_cell_%s" % name, "[?%s%s" % (value, fmt)), FONT_LABEL, "right", 22)
        if name in ("compliance", "resistance"):
            row_triggers += block("st_cell_%s_visible" % name, "NOT = { is_core_of = ROOT }\n")
        elif name != "pop":
            row_triggers += block("st_cell_%s_visible" % name, more_than_zero(value))
        x += width
        rx += width
    # the arrow that marks the sorted column: script moves it there
    body += icon("st_arrow_down", 0, 111, "GFX_arrow_down_small")
    body += icon("st_arrow_up", 0, 111, "GFX_arrow_up_small")
    properties += block("st_arrow_down", "x = mod1440_st_arrow_x\n") + block("st_arrow_up", "x = mod1440_st_arrow_x\n")
    triggers += block("st_arrow_down_visible", more_than_zero("mod1440_st_sort_by") + "NOT = { check_variable = { mod1440_st_up = 1 } }\n")
    triggers += block("st_arrow_up_visible", more_than_zero("mod1440_st_sort_by") + "check_variable = { mod1440_st_up = 1 }\n")

    # ---- the list
    grid = ('gridboxtype = {\n\tname = "st_grid"\n\tposition = { x = 0 y = 0 }\n\tsize = { width = %d height = 100%%%% }\n'
            '\tslotsize = { width = 1 height = 1 }\n\tadd_horizontal = no\n\tformat = "UPPER_LEFT"\n}\n' % ST_ROWS_W)
    listing = ('containerWindowType = {\n\tname = "st_list"\n\tposition = { x = 14 y = %d }\n\tsize = { width = %d height = %d }\n'
               '\tverticalScrollbar = "right_vertical_slider"\n\tscroll_wheel_factor = %d\n\tsmooth_scrolling = yes\n'
               '\tbackground = { name = "Background" quadTextureSprite = "%s" }\n%s}\n'
               % (ST_LIST_Y, ST_ROWS_W + 30, ST_H - ST_LIST_Y - 14, ST_ROW * 3, CARD_BG, indent(grid)))
    body += listing
    effects += block("st_row_click", block("ROOT", "goto_state = PREV\nset_variable = { mod1440_st_open = 0 }\nadd_to_variable = { mod1440_st_dirty = 1 }\n"))

    gui = box("mod1440_states", ST_X, ST_Y, ST_W, ST_H, body, PAGE_BG)
    gui += ('containerWindowType = {\n\tname = "mod1440_states_row"\n\tsize = { width = %d height = %d }\n%s}\n'
            % (ST_ROWS_W, ST_ROW, indent(row)))
    handle = button("st_unfold", 0, 0, "GFX_button_148x34", B.key("st_unfold", "States"), shortcut="shift+m",
                    tooltip=B.key("st_unfold_tt", "Show every state you control as a table"))
    gui += box("mod1440_states_handle", ST_X, 8, 148, 34, handle)

    script = scripted_gui(
        "mod1440_states", "mod1440_states", "construction_tab",
        visible="check_variable = { mod1440_st_open = 1 }\n", dirty="mod1440_st_dirty",
        lists=block("st_grid", 'array = mod1440_st_rows\nchange_scope = yes\nentry_container = "mod1440_states_row"\n'),
        effects=effects, triggers=triggers + row_triggers, properties=properties)
    script += "\n" + scripted_gui(
        "mod1440_states_handle", "mod1440_states_handle", "construction_tab",
        visible="NOT = { check_variable = { mod1440_st_open = 1 } }\n",
        effects=block("st_unfold_click", "set_variable = { mod1440_st_open = 1 }\nmod1440_st_list = yes\n"))

    frames = "".join("set_variable = { mod1440_st_frame_%s = 1 }\n" % n for n in ("0", "1", "2", "free"))
    frames += "".join(block("if", "limit = { check_variable = { mod1440_st_show = %d } }\nset_variable = { mod1440_st_frame_%d = 2 }\n" % (v, v))
                      for v in (0, 1, 2))
    frames += block("if", "limit = { check_variable = { mod1440_st_only_free = 1 } }\nset_variable = { mod1440_st_frame_free = 2 }\n")
    listing = (
        "# States: makes the list of the page again, for the country in scope. For each state it controls: count the\n"
        "# free shared slots, keep the state if the choices of the page want it, then sort.\n"
        + block("mod1440_st_list", (
            "clear_array = mod1440_st_rows\n"
            + block("for_each_scope_loop", (
                "array = controlled_states\n"
                + free_slot_tree(0, 31)
                + "set_temp_variable = { st_keep = 1 }\n"
                + block("if", block("limit", "check_variable = { ROOT.mod1440_st_show = 1 }\nNOT = { is_core_of = ROOT }\n") + "set_temp_variable = { st_keep = 0 }\n")
                + block("if", block("limit", "check_variable = { ROOT.mod1440_st_show = 2 }\nis_core_of = ROOT\n") + "set_temp_variable = { st_keep = 0 }\n")
                + block("if", block("limit", "check_variable = { ROOT.mod1440_st_only_free = 1 }\ncheck_variable = { mod1440_st_free < 1 }\n") + "set_temp_variable = { st_keep = 0 }\n")
                + block("if", "limit = { check_variable = { st_keep = 1 } }\nadd_to_array = { ROOT.mod1440_st_rows = THIS }\n")))
            + "mod1440_st_sort = yes\n" + frames
            + "add_to_variable = { mod1440_st_dirty = 1 }\n"))
        + "\n# States: puts the list into the order of the chosen column, largest first, or smallest first when turned.\n"
        "# The search for the next largest is the game's own loop, so 150 states take a few milliseconds (X22).\n"
        + block("mod1440_st_sort", block("if", (
            "limit = { check_variable = { mod1440_st_sort_by > 0 } }\n"
            "clear_array = mod1440_st_keys\n"
            + block("for_each_scope_loop", (
                "array = mod1440_st_rows\nset_temp_variable = { st_key = 0 }\n" + keys
                + block("if", "limit = { check_variable = { ROOT.mod1440_st_up = 1 } }\nmultiply_temp_variable = { st_key = -1 }\n")
                + "add_to_array = { ROOT.mod1440_st_keys = st_key }\n"))
            + "clear_array = mod1440_st_sorted\n"
            + block("for_loop_effect", (
                "start = 0\nend = mod1440_st_rows^num\nvalue = st_step\n"
                + block("find_highest_in_array", "array = mod1440_st_keys\nvalue = st_high\nindex = st_at\n")
                + "add_to_array = { mod1440_st_sorted = mod1440_st_rows^st_at }\n"
                "set_variable = { mod1440_st_keys^st_at = -2000000 }\n"))
            + "clear_array = mod1440_st_rows\n"
            + block("for_each_loop", "array = mod1440_st_sorted\nvalue = st_copy\nadd_to_array = { mod1440_st_rows = st_copy }\n")))))
    daily = block("if", "limit = { check_variable = { mod1440_st_open = 1 } }\nmod1440_st_list = yes\n")
    return gui, script, listing, daily


# ---------------------------------------------------------------- National Figures (D4), opened from Politics

# A row is (label, value, format): the label is a text key of the game (it then follows the player's language)
# or a text of the mod; the value is a variable of the country; the format is what follows the bar in
# "[?value|format]". "+" colours a gain green, "-" colours a gain red (for costs and penalties), "=" adds
# the sign. A value from "modifier@" is the country's summed modifier, the number the game works with.
def modifier_row(key, token, fmt="+=%1"):
    return (key, "modifier@" + token, fmt)


FIGURES = [
    ("politics", "Politics", 0, [
        ("Political power per day", "political_power_daily", "+=2"),
        modifier_row("MODIFIER_POLITICAL_POWER_FACTOR", "political_power_factor"),
        ("Stability now", "stability", "%1"),
        modifier_row("MODIFIER_STABILITY_WEEKLY", "stability_weekly", "+=%2"),
        ("Stability from modifiers", "modifier@stability_factor", "+=%1"),
        ("War support now", "has_war_support", "%1"),
        modifier_row("MODIFIER_WAR_SUPPORT_WEEKLY", "war_support_weekly", "+=%2"),
        ("War support from modifiers", "modifier@war_support_factor", "+=%1"),
        modifier_row("MODIFIER_DRIFT_DEFENCE_FACTOR", "drift_defence_factor"),
        ("Command power per day", "command_power_daily", "+=2"),
        modifier_row("MODIFIER_MAX_COMMAND_POWER", "max_command_power", "+=0"),
        modifier_row("MODIFIER_OPINION_GAIN_MONTHLY_FACTOR", "opinion_gain_monthly_factor"),
        modifier_row("MODIFIER_TRADE_OPINION_FACTOR", "trade_opinion_factor"),
        modifier_row("MODIFIER_JUSTIFY_WAR_GOAL_TIME", "justify_war_goal_time", "-=%1"),
        ("fascism", "party_popularity@fascism", "%0"),
        ("democratic", "party_popularity@democratic", "%0"),
        ("communism", "party_popularity@communism", "%0"),
        ("neutrality", "party_popularity@neutrality", "%0"),
    ]),
    ("economy", "Economy", 0, [
        ("Civilian factories", "num_of_civilian_factories", "0"),
        ("Free for construction", "num_of_civilian_factories_available_for_projects", "0"),
        ("Military factories", "num_of_military_factories", "0"),
        ("Without a production line", "num_of_available_military_factories", "0"),
        ("Dockyards", "num_of_naval_factories", "0"),
        ("Without a production line ", "num_of_available_naval_factories", "0"),
        ("Fuel, thousands", "fuel_k", "1"),
        ("Fuel capacity, thousands", "max_fuel_k", "1"),
        ("Convoys in stock", "num_equipment@convoy", "0"),
        ("Trains in stock", "num_equipment@train_equipment", "0"),
        ("Ships", "num_ships", "0"),
        ("Planes on airfields", "num_deployed_planes", "0"),
        ("States controlled", "num_controlled_states", "0"),
    ]),
    ("industry", "Industry", 1, [
        modifier_row("MODIFIER_INDUSTRIAL_CAPACITY_FACTOR", "industrial_capacity_factory"),
        modifier_row("MODIFIER_INDUSTRIAL_CAPACITY_DOCKYARD_FACTOR", "industrial_capacity_dockyard"),
        modifier_row("MODIFIER_PRODUCTION_FACTORY_MAX_EFFICIENCY_FACTOR", "production_factory_max_efficiency_factor"),
        modifier_row("MODIFIER_PRODUCTION_FACTORY_EFFICIENCY_GAIN_FACTOR", "production_factory_efficiency_gain_factor"),
        modifier_row("MODIFIER_PRODUCTION_FACTORY_START_EFFICIENCY_FACTOR", "production_factory_start_efficiency_factor"),
        modifier_row("MODIFIER_LINE_CHANGE_PRODUCTION_EFFICIENCY_FACTOR", "line_change_production_efficiency_factor"),
        modifier_row("MODIFIER_PRODUCTION_SPEED_BUILDINGS_FACTOR", "production_speed_buildings_factor"),
        modifier_row("MODIFIER_GLOBAL_BUILDING_SLOTS_FACTOR", "global_building_slots_factor"),
        ("Share of factories on consumer goods", "modifier@consumer_goods_expected_value", "%1"),
        modifier_row("MODIFIER_CONSUMER_GOODS_FACTOR", "consumer_goods_factor", "-=%1"),
        ("Civilian to military conversion cost", "modifier@conversion_cost_civ_to_mil_factor", "-=%1"),
        modifier_row("MODIFIER_INDUSTRY_REPAIR_FACTOR", "industry_repair_factor"),
        modifier_row("MODIFIER_LOCAL_RESOURCES_FACTOR", "local_resources_factor"),
        modifier_row("MODIFIER_MIN_EXPORT_FACTOR", "min_export", "%1"),
        modifier_row("MODIFIER_PRODUCTION_LACK_OF_RESOURCE_PENALTY_FACTOR", "production_lack_of_resource_penalty_factor", "-=%1"),
        modifier_row("MODIFIER_FUEL_GAIN_FACTOR", "fuel_gain_factor"),
        modifier_row("MODIFIER_MAX_FUEL_FACTOR", "max_fuel_factor"),
        modifier_row("MODIFIER_PRODUCTION_OIL_FACTOR", "production_oil_factor"),
        modifier_row("MODIFIER_EQUIPMENT_CAPTURE", "equipment_capture"),
    ]),
    ("people", "Manpower, Research, Intelligence", 1, [
        modifier_row("MODIFIER_CONSCRIPTION_FACTOR", "conscription", "%2"),
        modifier_row("MODIFIER_CONSCRIPTION_TOTAL_FACTOR", "conscription_factor"),
        modifier_row("MODIFIER_WEEKLY_MANPOWER", "weekly_manpower", "+=0"),
        modifier_row("MODIFIER_GLOBAL_MONTHLY_POPULATION", "monthly_population"),
        modifier_row("MODIFIER_GLOBAL_NON_CORE_MANPOWER", "non_core_manpower"),
        modifier_row("MODIFIER_MOBILIZATION_SPEED", "mobilization_speed"),
        modifier_row("MODIFIER_TRAINING_TIME_ARMY_FACTOR", "training_time_army_factor", "-=%1"),
        modifier_row("MODIFIER_SPECIAL_FORCES_CAP", "special_forces_cap"),
        modifier_row("MODIFIER_RESEARCH_SPEED_FACTOR", "research_speed_factor"),
        ("Research slots", "amount_research_slots", "0"),
        ("Technologies researched", "num_researched_technologies", "0"),
        modifier_row("MODIFIER_DECRYPTION_FACTOR", "decryption_factor"),
        modifier_row("MODIFIER_ENCRYPTION_FACTOR", "encryption_factor"),
        modifier_row("MODIFIER_OPERATIVE_SLOT", "operative_slot", "+=0"),
        modifier_row("MODIFIER_INTELLIGENCE_AGENCY_DEFENSE", "intelligence_agency_defense"),
        modifier_row("MODIFIER_INTEL_NETWORK_GAIN_FACTOR", "intel_network_gain_factor"),
    ]),
    ("army", "Army", 2, [
        modifier_row("MODIFIER_ARMY_ORG_FACTOR", "army_org_factor"),
        modifier_row("MODIFIER_ARMY_MORALE_FACTOR", "army_morale_factor"),
        ("Division attack", "modifier@army_attack_factor", "+=%1"),
        ("Division defense", "modifier@army_defence_factor", "+=%1"),
        ("Attack on core territory", "modifier@army_core_attack_factor", "+=%1"),
        ("Defense on core territory", "modifier@army_core_defence_factor", "+=%1"),
        modifier_row("MODIFIER_ARMY_INFANTRY_ATTACK_FACTOR", "army_infantry_attack_factor"),
        modifier_row("MODIFIER_ARMY_ARMOR_ATTACK_FACTOR", "army_armor_attack_factor"),
        modifier_row("MODIFIER_BREAKTHROUGH", "breakthrough_factor"),
        modifier_row("MODIFIER_ARMY_SPEED_FACTOR", "army_speed_factor"),
        modifier_row("MODIFIER_PLANNING_SPEED", "planning_speed"),
        modifier_row("MODIFIER_MAX_PLANNING", "max_planning"),
        modifier_row("MODIFIER_DIG_IN_SPEED_FACTOR", "dig_in_speed_factor"),
        modifier_row("MODIFIER_MAX_DIG_IN_FACTOR", "max_dig_in_factor"),
        modifier_row("MODIFIER_LAND_REINFORCE_RATE", "land_reinforce_rate"),
        modifier_row("MODIFIER_SUPPLY_CONSUMPTION_FACTOR", "supply_consumption_factor", "-=%1"),
        modifier_row("MODIFIER_ATTRITION", "attrition", "-=%1"),
        modifier_row("MODIFIER_OUT_OF_SUPPLY_FACTOR", "out_of_supply_factor", "-=%1"),
        ("Army experience gain", "modifier@experience_gain_army_factor", "+=%1"),
    ]),
    ("navy", "Navy", 3, [
        modifier_row("MODIFIER_NAVY_ORG_FACTOR", "navy_org_factor"),
        modifier_row("MODIFIER_NAVAL_MORALE_FACTOR", "naval_morale_factor"),
        modifier_row("MODIFIER_NAVAL_SPEED_FACTOR", "naval_speed_factor"),
        modifier_row("MODIFIER_NAVY_MAX_RANGE_FACTOR", "navy_max_range_factor"),
        modifier_row("MODIFIER_NAVAL_HIT_CHANCE", "naval_hit_chance"),
        modifier_row("MODIFIER_NAVAL_DAMAGE_FACTOR", "naval_damage_factor"),
        modifier_row("MODIFIER_NAVAL_DEFENSE_FACTOR", "naval_defense_factor"),
        modifier_row("MODIFIER_POSITIONING", "positioning"),
        modifier_row("MODIFIER_NAVAL_COORDINATION", "naval_coordination"),
        modifier_row("MODIFIER_SPOTTING_CHANCE", "spotting_chance"),
        modifier_row("MODIFIER_CONVOY_RAIDING_EFFICIENCY_FACTOR", "convoy_raiding_efficiency_factor"),
        modifier_row("MODIFIER_MISSION_CONVOY_ESCORT_EFFICIENCY", "convoy_escort_efficiency"),
        modifier_row("MODIFIER_STAT_CARRIER_SORTIE_EFFICIENCY", "sortie_efficiency"),
        modifier_row("MODIFIER_NAVY_FUEL_CONSUMPTION_FACTOR", "navy_fuel_consumption_factor", "-=%1"),
        ("Navy experience gain", "modifier@experience_gain_navy_factor", "+=%1"),
    ]),
    ("air", "Air Force", 3, [
        modifier_row("MODIFIER_AIR_ATTACK_FACTOR", "air_attack_factor"),
        modifier_row("MODIFIER_AIR_DEFENCE_FACTOR", "air_defence_factor"),
        modifier_row("MODIFIER_AIR_AGILITY_FACTOR", "air_agility_factor"),
        modifier_row("MODIFIER_AIR_RANGE_FACTOR", "air_range_factor"),
        modifier_row("MODIFIER_AIR_MISSION_EFFICIENCY", "air_mission_efficiency"),
        modifier_row("MODIFIER_AIR_SUPERIORITY_EFFICIENCY", "air_superiority_efficiency"),
        modifier_row("MODIFIER_AIR_CAS_EFFICIENCY", "air_cas_efficiency"),
        modifier_row("MODIFIER_STRATEGIC_BOMBER_BOMBING_FACTOR", "air_strategic_bomber_bombing_factor"),
        modifier_row("MODIFIER_AIR_BOMBING_TARGETTING", "air_bombing_targetting"),
        modifier_row("MODIFIER_AIR_DETECTION", "air_detection"),
        modifier_row("MODIFIER_AIR_ACE_GENERATION_CHANCE_FACTOR", "air_ace_generation_chance_factor"),
        modifier_row("MODIFIER_AIR_ACCIDENTS_FACTOR", "air_accidents_factor", "-=%1"),
        modifier_row("MODIFIER_AIR_WEATHER_PENALTY", "air_weather_penalty", "-=%1"),
        modifier_row("MODIFIER_AIR_NIGHT_PENALTY", "air_night_penalty", "-=%1"),
        modifier_row("MODIFIER_AIR_FUEL_CONSUMPTION_FACTOR", "air_fuel_consumption_factor", "-=%1"),
        ("Air experience gain", "modifier@experience_gain_air_factor", "+=%1"),
    ]),
]
RESOURCES = ["oil", "aluminium", "rubber", "tungsten", "steel", "chromium", "coal"]

NF_X, NF_Y = 556, 78            # on the screen: beside the politics panel, which is 550 wide
NF_COL = 400
NF_W = 14 + 4 * NF_COL + 3 * 12 + 14
NF_ROW = 26


def national_figures():
    triggers = ""
    body = box("nf_head", 3, 3, NF_W - 6, 50, "", "GFX_tiled_header")
    body += text("nf_title", 22, 8, 500, B.key("nf_title", "National Figures"), FONT_TITLE, height=40)
    body += text("nf_hint", NF_W - 780, 18, 700, B.key(
        "nf_hint", "Your country's modifiers, summed over every law, spirit, advisor and technology. A blank is no change."), FONT_SMALL, "right")
    body += button("nf_close", NF_W - 66, 10, "GFX_closebutton", shortcut="ESCAPE", tooltip=B.key("nf_close_tt", "Close"))

    bottoms = [AR_HEAD, AR_HEAD, AR_HEAD, AR_HEAD]
    for name, title, column, rows in FIGURES:
        card = text("nf_%s_title" % name, 14, 8, NF_COL - 28, B.key("nf_%s_title" % name, title), FONT_CARD, height=30)
        for i, (label, value, fmt) in enumerate(rows):
            y = 44 + i * NF_ROW
            # a label in capitals, or the name of an ideology, is a text key of the game
            game_key = re.match(r"^[A-Z][A-Z0-9_]*$", label) or label in ("fascism", "democratic", "communism", "neutrality")
            key = label if game_key else B.key("nf_%s_%d" % (name, i), label.strip())
            card += text("nf_%s_label_%d" % (name, i), 16, y, NF_COL - 16 - 16 - 84, key, FONT_SMALL, height=22)
            card += text("nf_%s_value_%d" % (name, i), NF_COL - 16 - 100, y - 2, 100,
                         B.key("nf_%s_%d_v" % (name, i), "[?%s|%s]" % (value, fmt)), FONT_LABEL, "right", 22)
            if value.startswith("modifier@"):
                triggers += block("nf_%s_value_%d_visible" % (name, i), "NOT = { check_variable = { %s = 0 } }\n" % value)
        height = 44 + len(rows) * NF_ROW + 14
        body += box("nf_%s" % name, 14 + column * (NF_COL + 12), bottoms[column], NF_COL, height, card, CARD_BG)
        bottoms[column] += height + 12

    # resources: a small table under the army card
    cols = [("balance", "Balance", "resource", "+=0", "What is left after your own use and your exports."),
            ("made", "Made", "resource_produced", "0", "Produced in your states."),
            ("used", "Used", "resource_consumed", "0", "Used by your production lines."),
            ("in", "Import", "resource_imported", "0", "Bought from other countries."),
            ("out", "Export", "resource_exported", "0", "Sold to other countries.")]
    card = text("nf_res_title", 14, 8, 200, B.key("nf_res_title", "Resources"), FONT_CARD, height=30)
    for c, (cname, caption, variable, fmt, tip) in enumerate(cols):
        edge = 104 + (c + 1) * 56
        card += text("nf_res_head_%s" % cname, edge - 56, 22, 56, B.key("nf_res_head_%s" % cname, caption), FONT_SMALL, "right", 20,
                     tooltip=B.key("nf_res_head_%s_tt" % cname, tip))
    for r, resource in enumerate(RESOURCES):
        y = 48 + r * NF_ROW
        card += text("nf_res_name_%d" % r, 16, y, 96, "PRODUCTION_MATERIALS_" + resource.upper(), FONT_SMALL, height=22)
        for c, (cname, caption, variable, fmt, tip) in enumerate(cols):
            edge = 104 + (c + 1) * 56
            card += text("nf_res_%s_%d" % (cname, r), edge - 50, y - 2, 50,
                         B.key("nf_res_%s_%d" % (cname, r), "[?%s@%s|%s]" % (variable, resource, fmt)), FONT_LABEL, "right", 22)
            if cname != "balance":
                triggers += block("nf_res_%s_%d_visible" % (cname, r), more_than_zero("%s@%s" % (variable, resource)))
    height = 48 + len(RESOURCES) * NF_ROW + 14
    body += box("nf_res", 14 + 2 * (NF_COL + 12), bottoms[2], NF_COL, height, card, CARD_BG)
    bottoms[2] += height + 12

    body += button("nf_history", 330, 12, "GFX_button_123x34", B.key("nf_history", "History"),
                   tooltip=B.key("nf_history_tt", "How twelve figures of your country have moved, month by month"))
    gui = box("mod1440_figures", NF_X, NF_Y, NF_W, max(bottoms) + 2, body, PAGE_BG)
    # the button that opens it sits in the title strip of the politics panel, between the title and the icons
    handle = button("nf_toggle", 0, 0, "GFX_button_148x34", B.key("nf_toggle", "National Figures"), shortcut="shift+m",
                    tooltip=B.key("nf_toggle_tt", "Show or hide the summed modifiers and figures of your country"))
    gui += box("mod1440_figures_handle", 262, 12, 148, 34, handle)

    toggle = (block("if", "limit = { check_variable = { mod1440_nf_open = 1 } }\nset_variable = { mod1440_nf_open = 0 }\n")
              + block("else", "set_variable = { mod1440_nf_open = 1 }\n"))
    script = scripted_gui("mod1440_figures", "mod1440_figures",
                          visible="check_variable = { mod1440_nf_open = 1 }\nNOT = { check_variable = { mod1440_nf_page = 1 } }\n",
                          effects=(block("nf_close_click", "set_variable = { mod1440_nf_open = 0 }\n")
                                   + block("nf_history_click", "set_variable = { mod1440_nf_page = 1 }\nmod1440_h_draw = yes\n")),
                          triggers=triggers)
    script += "\n" + scripted_gui("mod1440_figures_handle", "mod1440_figures_handle", "politics_tab",
                                  effects=block("nf_toggle_click", toggle + "mod1440_h_draw = yes\n"))
    return gui, script


# ---------------------------------------------------------------- History (D5), the second page of National Figures

# A series is (caption, value of the country, factor): the value is written down on the first of each month,
# times the factor (100 turns a 0 to 1 share into a percentage).
SERIES = [
    ("Free manpower", "manpower_k", 1, "thousands"),
    ("Manpower in the field", "deployed_total_manpower_k", 1, "thousands"),
    ("Divisions", "num_divisions", 1, ""),
    ("Civilian factories", "num_of_civilian_factories", 1, ""),
    ("Military factories", "num_of_military_factories", 1, ""),
    ("Dockyards", "num_of_naval_factories", 1, ""),
    ("Stability", "stability", 100, "percent"),
    ("War support", "has_war_support", 100, "percent"),
    ("Fuel", "fuel_k", 1, "thousands"),
    ("Infantry equipment in stock", "num_equipment@infantry_equipment", 1, ""),
    ("Casualties", "casualties_k", 1, "thousands"),
    ("Political power", "political_power", 1, ""),
]
H_KEEP = 120            # months on the graph: ten years
H_STEPS = 200           # heights a column can have (the "steps" of GFX_1440p_SG_column)
H_COLUMN = 11           # px from one column to the next
H_CHART_X, H_CHART_Y, H_CHART_H = 340, 110, 300


def history():
    effects = ""
    triggers = ""
    properties = ""
    width = H_CHART_X + H_KEEP * H_COLUMN + 30
    body = box("h_head", 3, 3, width - 6, 50, "", "GFX_tiled_header")
    body += text("h_title", 22, 8, 300, B.key("h_title", "History"), FONT_TITLE, height=40)
    body += button("h_figures", 330, 12, "GFX_button_123x34", B.key("h_figures", "Figures"),
                   tooltip=B.key("h_figures_tt", "Back to the figures of today"))
    body += text("h_hint", width - 760, 18, 680, B.key(
        "h_hint", "Written down on the first of each month since [?mod1440_h_first.GetDateStringNoHour], ten years at most."), FONT_SMALL, "right")
    body += button("h_close", width - 66, 10, "GFX_closebutton", shortcut="ESCAPE", tooltip=B.key("h_close_tt", "Close"))
    effects += block("h_close_click", "set_variable = { mod1440_nf_open = 0 }\nadd_to_variable = { mod1440_h_dirty = 1 }\n")
    effects += block("h_figures_click", "set_variable = { mod1440_nf_page = 0 }\nadd_to_variable = { mod1440_h_dirty = 1 }\n")

    copies = ""
    for n, (caption, value, factor, unit) in enumerate(SERIES):
        body += button("h_series_%d" % n, 16, 66 + n * 32, "GFX_sort_button_202x29", B.key("h_series_%d" % n, caption))
        effects += block("h_series_%d_click" % n, "set_variable = { mod1440_h_series = %d }\nmod1440_h_draw = yes\n" % n)
        properties += block("h_series_%d" % n, "frame = mod1440_h_frame_%d\n" % n)
        title = caption + (", " + unit if unit else "")
        body += text("h_name_%d" % n, 240, 70, 700, B.key("h_name_%d" % n, title), FONT_CARD, height=30)
        triggers += block("h_name_%d_visible" % n, "check_variable = { mod1440_h_series = %d }\n" % n)
        copies += block("if" if n == 0 else "else_if", (
            "limit = { check_variable = { mod1440_h_series = %d } }\n" % n
            + block("for_each_loop", "array = mod1440_h_%d\nvalue = h_v\nadd_to_array = { mod1440_h_now = h_v }\n" % n)))
    # the scale on the left, the dates below
    body += text("h_top", 240, H_CHART_Y - 8, 90, B.key("h_top", "[?mod1440_h_max|1]"), FONT_SMALL, "right", 20)
    body += text("h_half", 240, H_CHART_Y + H_CHART_H // 2 - 8, 90, B.key("h_half", "[?mod1440_h_half|1]"), FONT_SMALL, "right", 20)
    body += text("h_zero", 240, H_CHART_Y + H_CHART_H - 12, 90, "0", FONT_SMALL, "right", 20)
    body += text("h_from", H_CHART_X, H_CHART_Y + H_CHART_H + 8, 300, B.key("h_from", "[?mod1440_h_first.GetDateStringNoHour]"), FONT_SMALL)
    body += text("h_to", H_CHART_X + H_KEEP * H_COLUMN - 300, H_CHART_Y + H_CHART_H + 8, 300,
                 B.key("h_to", "[?mod1440_h_last.GetDateStringNoHour]"), FONT_SMALL, "right")
    body += text("h_latest", 960, 74, 400, B.key("h_latest", "now [?mod1440_h_latest|1], highest [?mod1440_h_max|1]"), FONT_LABEL, "right")
    # a game that got the mod after its start has nothing written down until the first of the next month
    body += text("h_none", H_CHART_X + 20, H_CHART_Y + 130, 900, B.key(
        "h_none", "Nothing is written down yet. The first column comes on the first of next month."), FONT_LABEL)
    some = more_than_zero("mod1440_h_date^num")
    triggers += block("h_none_visible", "NOT = { %s }\n" % some.strip())
    for name in ("h_hint", "h_top", "h_half", "h_zero", "h_from", "h_to", "h_latest"):
        triggers += block(name + "_visible", some)
    grid = ('gridboxtype = {\n\tname = "h_grid"\n\tposition = { x = 0 y = 0 }\n\tsize = { width = %d height = %d }\n'
            '\tslotsize = { width = %d height = %d }\n\tadd_horizontal = yes\n\tmax_slots_horizontal = %d\n\tformat = "UPPER_LEFT"\n}\n'
            % (H_KEEP * H_COLUMN, H_CHART_H, H_COLUMN, H_CHART_H, H_KEEP))
    body += box("h_chart", H_CHART_X, H_CHART_Y, H_KEEP * H_COLUMN, H_CHART_H, grid, CARD_BG)

    gui = box("mod1440_history", NF_X, NF_Y, width, H_CHART_Y + H_CHART_H + 44, body, PAGE_BG)
    column = ('iconType = { name = "h_bar" position = { x = 1 y = 0 } spriteType = "GFX_1440p_SG_column" pdx_tooltip = "%s" }\n'
              % B.key("h_bar_tt", "[?mod1440_h_date^i.GetDateStringNoHour]: [?mod1440_h_now^i|1]"))
    gui += ('containerWindowType = {\n\tname = "mod1440_history_column"\n\tsize = { width = %d height = %d }\n%s}\n'
            % (H_COLUMN, H_CHART_H, indent(column)))
    properties += block("h_bar", "frame = v\n")

    script = scripted_gui(
        "mod1440_history", "mod1440_history",
        visible="check_variable = { mod1440_nf_open = 1 }\ncheck_variable = { mod1440_nf_page = 1 }\n", dirty="mod1440_h_dirty",
        lists=block("h_grid", 'array = mod1440_h_bars\nentry_container = "mod1440_history_column"\n'),
        effects=effects, triggers=triggers, properties=properties)

    record = "".join(
        ("add_to_array = { mod1440_h_%d = %s }\n" % (n, value)) if factor == 1 else (
            "set_temp_variable = { h_v = %s }\nmultiply_temp_variable = { h_v = %d }\nadd_to_array = { mod1440_h_%d = h_v }\n" % (value, factor, n))
        for n, (caption, value, factor, unit) in enumerate(SERIES))
    forget = "".join("remove_from_array = { array = mod1440_h_%d index = 0 }\n" % n for n in range(len(SERIES)))
    frames = "".join("set_variable = { mod1440_h_frame_%d = 1 }\n" % n for n in range(len(SERIES)))
    frames += "".join(block("if", "limit = { check_variable = { mod1440_h_series = %d } }\nset_variable = { mod1440_h_frame_%d = 2 }\n" % (n, n))
                      for n in range(len(SERIES)))
    script_effects = (
        "# History: writes today's figures of the country in scope down, and forgets the oldest month past ten years.\n"
        "# Runs at the start of a game for every country and on the first of each month for a player.\n"
        + block("mod1440_h_record", (
            record + "add_to_array = { mod1440_h_date = global.date }\n"
            + block("if", "limit = { check_variable = { mod1440_h_date^num > %d } }\n" % H_KEEP + forget
                    + "remove_from_array = { array = mod1440_h_date index = 0 }\n")
            + block("if", "limit = { check_variable = { mod1440_nf_page = 1 } }\nmod1440_h_draw = yes\n")))
        + "\n# History: turns the chosen figure into column heights, 0 to %d, the highest month the tallest.\n" % H_STEPS
        + block("mod1440_h_draw", (
            "clear_array = mod1440_h_now\n" + copies
            + "set_temp_variable = { h_max = 0 }\n"
            + block("find_highest_in_array", "array = mod1440_h_now\nvalue = h_max\nindex = h_at\n")
            + "set_variable = { mod1440_h_max = h_max }\nset_variable = { mod1440_h_half = h_max }\ndivide_variable = { mod1440_h_half = 2 }\n"
            + "clear_array = mod1440_h_bars\n"
            + block("for_each_loop", (
                "array = mod1440_h_now\nvalue = h_v\nset_temp_variable = { h_bar = 0 }\n"
                + block("if", "limit = { check_variable = { h_max > 0 } }\nset_temp_variable = { h_bar = h_v }\n"
                        "divide_temp_variable = { h_bar = h_max }\nmultiply_temp_variable = { h_bar = %d }\n" % H_STEPS)
                + "add_to_array = { mod1440_h_bars = h_bar }\nset_variable = { mod1440_h_latest = h_v }\n"))
            + "set_variable = { mod1440_h_first = mod1440_h_date^0 }\n"
            + "set_temp_variable = { h_end = mod1440_h_date^num }\nsubtract_from_temp_variable = { h_end = 1 }\n"
            + "set_variable = { mod1440_h_last = mod1440_h_date^h_end }\n"
            + frames + "add_to_variable = { mod1440_h_dirty = 1 }\n")))
    monthly = "mod1440_h_record = yes\n"
    return gui, script, script_effects, monthly


# ---------------------------------------------------------------- scenes: what the renderer and the harness need

# One scene per page (tools/scenes/<name>.json, see wiki/Game-Recipes.md): where the page stands on the screen,
# the recipe that brings it up, the widgets that prove it is up, and a sample for every text that holds a
# value, so that the renderer draws numbers and the tests measure them against their boxes.
SCENES = {
    "army_readiness": {
        "phase": "D2", "file": "mod1440_army_readiness.gui", "screenshot": "reference/vanilla/recruit_deploy.jpg",
        "windows": [
            {"name": "mod1440_army_readiness", "at": [1250, 78], "sidePanel": True,
             "rows": {"ar_al_grid": 4}, "listRows": {"ar_al_grid": "mod1440_army_readiness_row"},
             "hide": ["ar_mp_zero_training", "ar_mp_zero_garrison", "ar_al_none"] + ["ar_eq_short_%d" % i for i in range(len(EQUIPMENT))],
             "_note": "Docked to Recruit & Deploy: the tab's corner at -6,78 plus the container's 1256,0. Hidden here: the twin of a value that script shows in its place (a plain 0, a red number)."},
            {"name": "mod1440_army_readiness_row", "skip": True},
        ],
        "setup": [{"move": "open_recruit_deploy"}],
        "expect": ["mod1440_army_readiness/ar_fold", "mod1440_army_readiness/ar_count"],
        "crop": [1240, 70, 1000, 1230],
        "manual": ["The page after a day has passed: the counts and the bars come from a daily hook, which no check runs"],
        "checklist": [
            "Shift+M hides the page and brings it back; the handle beside the template panel does the same",
            "Train a division: In training rises, In stock falls",
            "Assign a general to an army, press Count again: the general is listed under Armies",
            "After a few days of game time the date beside Count again is today's",
        ],
    },
    "states": {
        "phase": "D3", "file": "mod1440_states.gui", "screenshot": "reference/vanilla/construction.jpg",
        "windows": [
            {"name": "mod1440_states", "at": [703, 78], "sidePanel": True,
             "rows": {"st_grid": 24}, "listRows": {"st_grid": "mod1440_states_row"},
             "hide": ["st_arrow_up", "st_arrow_down"],
             "_note": "Docked to Construction: the tab's corner at -9,78 plus the container's 712,0. The vanilla window has clipping = no."},
            {"name": "mod1440_states_row", "skip": True},
        ],
        "setup": [{"move": "open_construction"}, {"key": "shift+m", "wait": 1.5, "_note": "the page is hidden until asked for"}],
        "teardown": [{"key": "shift+m", "wait": 0.8, "_note": "hide it again: the page remembers per country whether it is open"}],
        "expect": ["mod1440_states/st_fold", "mod1440_states/st_refresh"],
        "crop": [690, 70, 1460, 1230],
        "manual": ["A country with occupied states: the Occupied choice, compliance and resistance"],
        "checklist": [
            "A click on a column head sorts, a second click turns the order; State gives the game's order back",
            "A click on a state moves the camera there and hides the page",
            "Free slots of a state against its state view (unlocked slots minus buildings)",
        ],
    },
    "national_figures": {
        "phase": "D4", "file": "mod1440_figures.gui", "screenshot": "reference/vanilla/politics.jpg",
        "windows": [{"name": "mod1440_figures", "at": [NF_X, NF_Y], "sidePanel": True,
                     "_note": "A window of its own beside the politics panel, opened from the button in that panel's title strip."}],
        "setup": [{"move": "open_politics"}, {"key": "shift+m", "wait": 1.5}],
        "teardown": [{"key": "shift+m", "wait": 0.8}],
        "expect": ["mod1440_figures/nf_close", "mod1440_figures/nf_history"],
        "crop": [546, 70, 1700, 1180],
        "manual": [],
        "checklist": ["A modifier against the tooltip of its source: a law, a spirit or an advisor", "Escape closes the page and leaves Politics open"],
    },
    "history": {
        "phase": "D5", "file": "mod1440_figures.gui", "screenshot": "reference/vanilla/politics.jpg",
        "windows": [
            {"name": "mod1440_history", "at": [NF_X, NF_Y], "rows": {"h_grid": 36}, "listRows": {"h_grid": "mod1440_history_column"},
             "hide": ["h_name_%d" % n for n in range(1, 12)] + ["h_none"],
             "_note": "The title of the chosen figure shows, the eleven others are hidden by script."},
            {"name": "mod1440_history_column", "skip": True},
        ],
        "setup": [{"move": "open_politics"}, {"key": "shift+m", "wait": 1.5},
                  {"clickWidget": "mod1440_figures/nf_history", "scene": "national_figures", "wait": 1.2}],
        "teardown": [{"clickWidget": "mod1440_history/h_figures", "wait": 0.8}, {"key": "shift+m", "wait": 0.8}],
        "expect": ["mod1440_history/h_close", "mod1440_history/h_figures"],
        "crop": [546, 70, 1700, 480],
        "manual": ["More than one month: the graph gets a column on the first of each month, which no check lets pass"],
        "checklist": ["After some months of game time each figure has one column per month", "The tooltip of a column gives its month and value"],
    },
}

SAMPLE_VALUES = {
    "manpower_k": "12500", "deployed_army_manpower_k": "4300", "deployed_navy_manpower_k": "310", "deployed_airforce_manpower_k": "275",
    "num_divisions": "350", "num_battalions": "3400", "army_experience": "500", "mod1440_ar_low_str": "24", "mod1440_ar_low_org": "17",
    "skill_level": "4", "num_units": "24", "num_units_in_combat": "12", "num_infantry": "20", "num_armored": "3", "num_motorized": "1",
    "mod1440_al_fill": "87", "mod1440_st_free": "12", "state_population_k": "12500", "compliance": "45", "resistance": "20",
    "mod1440_st_rows^num": "152", "mod1440_h_max": "1332.6", "mod1440_h_half": "666.3", "mod1440_h_latest": "1250.4",
    "fuel_k": "297.2", "max_fuel_k": "371.5", "num_ships": "38", "num_deployed_planes": "992", "num_controlled_states": "24",
    "amount_research_slots": "4", "num_researched_technologies": "55",
}


def sample_for(window, text_value):
    """A text with its values written in, as wide as the game will make it."""
    def one(match):
        inside = match.group(1)
        if "GetName" in inside:
            return "Gerd von Rundstedt" if "army_readiness" in window else "Niederschlesien"
        if "GetDateString" in inside:
            return "1936.1.1"
        if not inside.startswith("?"):
            return ""
        variable, _, fmt = inside[1:].partition("|")
        if "%" in fmt:
            return ("+" if "=" in fmt else "") + ("100%" if fmt.endswith("0") else "25.0%")
        if "*" in fmt:
            return "128.8K"
        if "=" in fmt:
            return "+2.32" if fmt.endswith("2") else "+104"
        if variable in SAMPLE_VALUES:
            return SAMPLE_VALUES[variable]
        if variable.startswith(("building_level", "infrastructure", "industrial", "arms_factory")):
            return "20"
        if variable.startswith("resource"):
            return "250"
        if variable.startswith("num_of_"):
            return "128"
        return "1250000" if "equipment" in variable else "12500"
    return re.sub(r"\[([^\]]+)\]", one, text_value)


def scene_files(gui_by_file):
    """tools/scenes/<name>.json for every page, with a sample for each text of its windows that holds a value."""
    import json
    samples_by_window = {}
    for content in gui_by_file.values():
        starts = [(m.start(), m.group(1)) for m in re.finditer(r'^\tcontainerWindowType = \{\n\t\tname = "(mod1440_\w+)"', content, re.M)]
        for index, (start, window) in enumerate(starts):
            end = starts[index + 1][0] if index + 1 < len(starts) else len(content)
            for m in re.finditer(r'instantTextboxType = \{ name = "(\w+)"[^\n]*? text = "([^"]*)"', content[start:end]):
                value = B.loc.get(m.group(2), m.group(2))
                if "[" in value:
                    samples_by_window.setdefault(window, {})[m.group(1)] = sample_for(window, value)
    out = {}
    for name, scene in SCENES.items():
        windows = [w["name"] for w in scene["windows"]]
        document = {
            "_comment": "Generated by tools/build_managers.py: change the scene there. Keys are explained in wiki/Game-Recipes.md and in tools/scenes/recruit_deploy.json.",
            "screen": name, "phase": scene["phase"], "file": scene["file"], "screenshot": scene["screenshot"],
            "modOnly": True,
            "windows": scene["windows"],
            "samples": {w: samples_by_window[w] for w in windows if w in samples_by_window},
            "setup": scene["setup"], "captures": [], "expect": scene["expect"], "crop": scene["crop"],
            "manual": scene["manual"], "checklist": scene["checklist"],
        }
        if "teardown" in scene:
            document["teardown"] = scene["teardown"]
        out["tools/scenes/%s.json" % name] = json.dumps(document, indent=2, ensure_ascii=True) + "\n"
    return out


# ---------------------------------------------------------------- assembling the files

HEADER_GUI = "# Generated by tools/build_managers.py. Scripted GUI containers of the mod (wiki/Scripted-GUIs.md).\n"
HEADER_TXT = "# Generated by tools/build_managers.py.\n"


def build():
    gui, script, count = army_readiness()
    B.files["interface/mod1440_army_readiness.gui"] = HEADER_GUI + "guiTypes = {\n" + indent(gui) + "}\n"
    B.files["common/scripted_guis/mod1440_army_readiness.txt"] = HEADER_TXT + block("scripted_gui", script)
    gui, script, listing, states_daily = states_table()
    B.files["interface/mod1440_states.gui"] = HEADER_GUI + "guiTypes = {\n" + indent(gui) + "}\n"
    B.files["common/scripted_guis/mod1440_states.txt"] = HEADER_TXT + block("scripted_gui", script)
    gui, script = national_figures()
    history_gui, history_script, recording, monthly = history()
    B.files["interface/mod1440_figures.gui"] = HEADER_GUI + "guiTypes = {\n" + indent(gui + history_gui) + "}\n"
    B.files["common/scripted_guis/mod1440_figures.txt"] = HEADER_TXT + block("scripted_gui", script + "\n" + history_script)
    B.files["common/scripted_effects/mod1440_effects.txt"] = HEADER_TXT + count + "\n" + listing + "\n" + recording
    # The hooks. A new game: count and write down once for every country, so that whichever country the
    # player takes has its numbers from the first day. After that only a player's country costs time.
    B.files["common/on_actions/mod1440_on_actions.txt"] = HEADER_TXT + block("on_actions", (
        block("on_startup", block("effect", block("every_country", "mod1440_ar_count = yes\n" + monthly)))
        + block("on_daily", block("effect", block("if", "limit = { is_ai = no }\nmod1440_ar_count = yes\n" + states_daily)))
        + block("on_monthly", block("effect", block("if", "limit = { is_ai = no }\n" + monthly)))))

    everything = "".join(B.files.values()) + "".join(B.loc.values())
    B.files.update(scene_files({rel: content for rel, content in B.files.items() if rel.endswith(".gui")}))
    tokens = sorted(set(re.findall(r"@([A-Za-z_][A-Za-z0-9_]*)", everything)))
    B.files["common/synchronized_dynamic_tokens/mod1440_tokens.txt"] = "".join(t + "\n" for t in tokens)
    # The texts are English. Every other language of the game gets the same file under its own header:
    # without one the game shows the bare key. The names taken from the game ($key$ and plain keys such as
    # infantry_equipment) follow the player's language by themselves.
    entries = "".join(' %s:0 "%s"\n' % (key, value) for key, value in sorted(B.loc.items()))
    for language in LANGUAGES:
        B.files["localisation/%s/mod1440_l_%s.yml" % (language, language)] = "\ufeffl_%s:\n" % language + entries
    for rel, content in B.files.items():
        if rel.endswith((".gui", ".txt")) and content.count("{") != content.count("}"):
            raise ValueError("unbalanced braces in " + rel)


def main(argv):
    build()
    stale = []
    for rel, content in sorted(B.files.items()):
        path = os.path.join(ROOT, rel)
        current = io.open(path, encoding="utf-8", newline="").read() if os.path.isfile(path) else None
        if current == content:
            continue
        stale.append(rel)
        if "--check" not in argv:
            os.makedirs(os.path.dirname(path), exist_ok=True)
            io.open(path, "w", encoding="utf-8", newline="\n").write(content)
            print("wrote", rel)
    if "--check" in argv and stale:
        print("out of date (run python -I tools/build_managers.py): " + ", ".join(stale))
        return 1
    if not stale:
        print("all files are up to date")
    else:
        # A running game reads a changed localisation file with any reload of common/scripted_guis, and a
        # changed .gui file only for the scripted GUIs whose own file it reads again (Engine Facts X23).
        # So every file there gets a new time stamp, written or not.
        for rel in sorted(B.files):
            if rel.startswith("common/scripted_guis/") and rel not in stale:
                os.utime(os.path.join(ROOT, rel), None)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
