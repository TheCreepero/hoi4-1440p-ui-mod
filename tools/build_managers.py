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

The Records window of Milestone E (War Diary, Officers, Government, Wars) is written by tools/build_records.py,
which this file imports: interface/mod1440_records.gui, common/scripted_guis/mod1440_records.txt and
common/scripted_effects/mod1440_records.txt, and its hooks go into the one on_actions file.

Rules the output follows (wiki/Scripted-GUIs.md): a button changes the panel, moves the camera or writes a
record; own country only; names carry the prefix mod1440_; no loop in anything drawn every tick.
"""
import io
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# "python -I" leaves the script's folder off the path; the role-play pages live in a module beside this file
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_records  # noqa: E402

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


def iff(limit, body, keyword="if"):
    return block(keyword, "limit = { %s }\n" % limit + body)


def els(body):
    return block("else", body)


def setv(variable, value):
    return "set_variable = { %s = %s }\n" % (variable, value)


def tmp(variable, value):
    return "set_temp_variable = { %s = %s }\n" % (variable, value)


def is_one(variable):
    return "check_variable = { %s = 1 }" % variable


def flip(variable):
    return iff(is_one(variable), setv(variable, 0)) + els(setv(variable, 1))


# ---------------------------------------------------------------- the look every page shares

# Dark cards on the page; a figure as a tile, a small label over a large value on a plate; every table under a
# bar of column heads, with a darker band on every second row and a lighter one on the chosen row; shares as
# bars. The sprites are tiles of vanilla textures at the sizes the pages use (interface/1440p_ui.gfx).
TILE_W, TILE_H = 156, 64
STRIPE = "GFX_1440p_SG_stripe_%dx%d"        # the darker band of every second row
PICK = "GFX_1440p_SG_pick_%dx%d"            # the lighter band of the chosen row
# The mark of the sorted column: the game's small arrow (22x28) at about half its size, on the upper right corner
# of the head. A head is 30 px high and its text starts 8 px down, so the arrow covers no letter of a narrow head.
ARROW, ARROW_DX, ARROW_DY = 0.55, 13, -9
BAR = {105: "GFX_1440p_SG_bar", 300: "GFX_1440p_SG_bar_wide"}     # other lengths: GFX_1440p_SG_bar_<length>


def tile_sprite(width=TILE_W, height=TILE_H):
    return "GFX_1440p_SG_tile" if (width, height) == (TILE_W, TILE_H) else "GFX_1440p_SG_tile_%dx%d" % (width, height)


def bar_sprite(length, low=False):
    """A lying bar that script fills, 0 to 100: green, or the orange of a strength bar for a low value."""
    if low:
        return "GFX_1440p_SG_bar_low_%d" % length
    return BAR.get(length, "GFX_1440p_SG_bar_%d" % length)


def plain(name, x, y, width, key, font=None, fmt="left", height=24):
    """A text that lets a click through to the button under it."""
    return ('instantTextboxType = { name = "%s" position = { x = %d y = %d } font = "%s" text = "%s" '
            'maxWidth = %d maxHeight = %d format = %s alwaystransparent = yes }\n'
            % (name, x, y, font or FONT_LABEL, key, width, height, fmt))


def scaled(name, x, y, sprite, scale, tooltip=None):
    tip = ' pdx_tooltip = "%s"' % tooltip if tooltip else ""
    return 'iconType = { name = "%s" position = { x = %d y = %d } spriteType = "%s" scale = %s%s }\n' % (name, x, y, sprite, scale, tip)


def listing(name, grid, x, y, width, height, row_height):
    """A list that scrolls: the rows are stacked by their own height (Engine Facts X10)."""
    inner = ('gridboxtype = {\n\tname = "%s"\n\tposition = { x = 0 y = 0 }\n\tsize = { width = %d height = 100%%%% }\n'
             '\tslotsize = { width = 1 height = 1 }\n\tadd_horizontal = no\n\tformat = "UPPER_LEFT"\n}\n' % (grid, width - 30))
    return ('containerWindowType = {\n\tname = "%s"\n\tposition = { x = %d y = %d }\n\tsize = { width = %d height = %d }\n'
            '\tverticalScrollbar = "right_vertical_slider"\n\tscroll_wheel_factor = %d\n\tsmooth_scrolling = yes\n'
            '\tbackground = { name = "Background" quadTextureSprite = "%s" }\n%s}\n'
            % (name, x, y, width, height, row_height * 3, CARD_BG, indent(inner)))


def row(name, width, height, body):
    return 'containerWindowType = {\n\tname = "%s"\n\tsize = { width = %d height = %d }\n%s}\n' % (name, width, height, indent(body))


def heads(name, x, y, width, labels):
    """A bar of column heads over a table: (x, width, text, format, tooltip or None) each."""
    inner = ""
    for n, (lx, lw, label, fmt, tip) in enumerate(labels):
        inner += text("%s_%d" % (name, n), lx, 5, lw, B.key("%s_%d" % (name, n), label), FONT_SMALL, fmt, 20,
                      tooltip=B.key("%s_%d_tt" % (name, n), tip) if tip else None)
    return box(name, x, y, width, 30, inner, HEAD_SPRITES[240])


def tile(name, x, y, label, value, tip=None, when=None, width=TILE_W, zero=None):
    """A figure: a plate with a small label over a large value. Returns the widgets and their triggers.
    when: a trigger for the whole tile. zero: a variable; the value then shows only above zero and a plain 0
    otherwise (some values read "0.0" at zero, and a colour is for a number that says something)."""
    tooltip = B.key(name + "_tt", tip) if tip else None
    out = icon(name + "_bg", x, y, tile_sprite(width))
    out += text(name + "_l", x + 6, y + 7, width - 12, B.key(name + "_l", label), FONT_SMALL, "centre", 20, tooltip=tooltip)
    out += text(name, x + 6, y + 30, width - 12, B.key(name, value), FONT_VALUE, "centre", 26, tooltip=tooltip)
    triggers = "".join(block(part + "_visible", when) for part in (name + "_bg", name + "_l", name)) if when else ""
    if zero:
        out += text(name + "_z", x + 6, y + 30, width - 12, "0", FONT_VALUE, "centre", 26, tooltip=tooltip)
        triggers += block(name + "_visible", more_than_zero(zero))
        triggers += block(name + "_z_visible", "NOT = { %s }\n" % more_than_zero(zero).strip())
    return out, triggers


def card(name, x, y, width, height, title, inner):
    return box(name, x, y, width, height,
               text(name + "_title", 14, 8, width - 28, B.key(name + "_title", title), FONT_CARD, height=30) + inner, CARD_BG)


def stripes(name, x, y, width, row_height, rows):
    """The darker bands of a table whose rows stand in the file: one behind every second row."""
    return "".join(icon("%s_%d" % (name, n), x, y + n * row_height, STRIPE % (width, row_height)) for n in range(1, rows, 2))


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
AR_HEAD = 60                    # height of the title strip
AR_IN = AR_W - 28               # what a card has between the margins of the page
AR_TILE = 148                   # six figures side by side
AR_TABLE = AR_IN - 28           # a table inside a card
AR_ROW = 28                     # a row of the equipment table
ROW = 30                        # a row of a list
LOW = 75                        # a bar is orange below this many percent

# The figures: manpower in the upper row, the army in the lower. (name, label, value, tooltip, variable that
# decides between the value and a plain 0, or None)
AR_FIGURES = [
    ("mp_free", "Free manpower", "[?manpower_k|0]K", "Men you can still call up: the manpower of the top bar.", None),
    ("mp_training", "In training", "[?amount_manpower_in_deployment_queue|*1]",
     "Men of the divisions in training. Queue a division and this rises.", "amount_manpower_in_deployment_queue"),
    ("mp_army", "In the army", "[?deployed_army_manpower_k|0]K", "Men of the divisions in the field.", None),
    ("mp_navy", "In the navy", "[?deployed_navy_manpower_k|0]K", "Men serving on your ships.", None),
    ("mp_air", "In the air force", "[?deployed_airforce_manpower_k|0]K", "Men serving in your air wings.", None),
    ("mp_garrison", "Garrisons need", "[?garrison_manpower_need|*1]", "Men the garrisons of your occupied states ask for.", "garrison_manpower_need"),
    ("divisions", "Divisions", "[?num_divisions|0]", "Divisions in the field.", None),
    ("battalions", "Battalions", "[?num_battalions|0]", "Battalions of the divisions in the field.", None),
    ("xp", "Army experience", "[?army_experience|0]", "Army experience to spend on templates and equipment.", None),
    ("low_str", "Under strength", "[?mod1440_ar_low_str|Y0]", "Divisions below 75% strength, as of the last count.", "mod1440_ar_low_str"),
    ("low_org", "Low organisation", "[?mod1440_ar_low_org|Y0]", "Divisions below 50% organisation, as of the last count.", "mod1440_ar_low_org"),
]


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

    # ---- the figures: two rows of tiles, and in the last place the button that counts again
    band = ""
    step = AR_TILE + 6
    for n, (name, label, value, tip, zero) in enumerate(AR_FIGURES):
        part, more = tile("ar_" + name, 14 + (n % 6) * step, 14 + (n // 6) * (TILE_H + 6), label, value, tip, width=AR_TILE, zero=zero)
        band += part
        triggers += more
    x, y = 14 + 5 * step, 14 + TILE_H + 6
    band += button("ar_count", x + (AR_TILE - 123) // 2, y + 2, "GFX_button_123x34", B.key("ar_count", "Count again"), tooltip=B.key(
        "ar_count_tt", "Goes through every division once. The two counts beside this button, the bars and the list of armies are from the last time this ran: at the start of each day, and on this button."))
    band += text("ar_counted", x, y + 40, AR_TILE, B.key("ar_counted", "[?mod1440_ar_counted.GetDateStringNoHourLong]"), FONT_SMALL, "centre", 20)
    effects += block("ar_count_click", "mod1440_ar_count = yes\n")
    triggers += block("ar_counted_visible", counted)
    band_h = 14 + 2 * TILE_H + 6 + 14
    body += box("ar_figures", 14, AR_HEAD, AR_IN, band_h, band, CARD_BG)

    # ---- equipment: a table with one row per kind
    c_stock, c_field, c_need, c_short, c_bar, c_pct = 360, 470, 580, 670, 690, 905      # right edges; the bar's left edge
    inner = heads("ar_eq_heads", 14, 42, AR_TABLE, [
        (10, 240, "Kind", "left", None),
        (c_stock - 100, 100, "In stock", "right", "Equipment in the stockpile that no division and no training has taken: the number of the logistics tab."),
        (c_field - 100, 100, "In the field", "right", "Equipment in the hands of the divisions in the field. Red when it is less than they need."),
        (c_need - 100, 100, "Needed", "right", "What the templates of the divisions in the field ask for. Divisions in training are not counted."),
        (c_short - 86, 86, "Short", "right", "What the divisions in the field lack: needed less in the field, as of the last count. The stock fills it as far as it goes."),
        (c_bar, 150, "Equipped", "left", "In the field as a share of needed, as of the last count. Orange below %d%%." % LOW),
    ])
    inner += stripes("ar_eq_stripe", 14, 74, AR_TABLE, AR_ROW, len(EQUIPMENT))
    fills = ""
    for i, eq in enumerate(EQUIPMENT):
        y = 74 + i * AR_ROW
        stock, field, need = "num_equipment@" + eq, "num_equipment_in_armies@" + eq, "num_target_equipment_in_armies@" + eq
        fill, lack = "mod1440_ar_fill_%d" % i, "mod1440_ar_short_%d" % i
        used = block("OR", more_than_zero(stock) + more_than_zero(need))
        short = "check_variable = { var = %s value = %s compare = less_than }\n" % (field, need)
        low = "check_variable = { %s < %d }\n" % (fill, LOW)

        def cell(name, edge, width, value, font=FONT_VALUE):
            return text("ar_eq_%s_%d" % (name, i), 14 + edge - width, y + 2, width, B.key("ar_eq_%s_%d" % (name, i), value), font, "right", 24)

        # the game's own name of the archetype: grey while the country neither has nor needs the kind
        inner += text("ar_eq_dim_%d" % i, 24, y + 3, 240, B.key("ar_eq_dim_%d" % i, "§g$%s$§!" % eq), height=22)
        inner += text("ar_eq_name_%d" % i, 24, y + 3, 240, eq, height=22)
        inner += cell("stock", c_stock, 90, "[?%s|0]" % stock) + cell("field", c_field, 90, "[?%s|0]" % field)
        inner += cell("short", c_field, 90, "[?%s|R0]" % field) + cell("need", c_need, 90, "[?%s|0]" % need)
        inner += cell("lack", c_short, 80, "[?%s|R0]" % lack)
        inner += icon("ar_eq_bar_%d" % i, 14 + c_bar, y + 8, bar_sprite(150))
        inner += icon("ar_eq_low_%d" % i, 14 + c_bar, y + 8, bar_sprite(150, low=True))
        inner += cell("pct", c_pct, 56, "[?%s|0]%%" % fill, FONT_LABEL)
        triggers += block("ar_eq_name_%d_visible" % i, used)
        triggers += block("ar_eq_stock_%d_visible" % i, used)
        triggers += block("ar_eq_need_%d_visible" % i, used)
        triggers += block("ar_eq_field_%d_visible" % i, used + "NOT = { %s }\n" % short.strip())
        triggers += block("ar_eq_short_%d_visible" % i, short)
        triggers += block("ar_eq_lack_%d_visible" % i, more_than_zero(lack) + counted)
        triggers += block("ar_eq_bar_%d_visible" % i, more_than_zero(need) + counted + "NOT = { %s }\n" % low.strip())
        triggers += block("ar_eq_low_%d_visible" % i, more_than_zero(need) + counted + low)
        triggers += block("ar_eq_pct_%d_visible" % i, more_than_zero(need) + counted)
        # a math expression is not accepted as a property ("Window not found" on reload): the fill is a variable
        properties += block("ar_eq_bar_%d" % i, "frame = %s\n" % fill) + block("ar_eq_low_%d" % i, "frame = %s\n" % fill)
        # A share is worked out as have / need * 100, dividing first: the product of a large stock and 100 is
        # more than a script number is sure to hold.
        fills += setv(fill, 0) + setv(lack, 0) + iff("check_variable = { %s > 0 }" % need, (
            setv(fill, field) + "divide_variable = { %s = %s }\nmultiply_variable = { %s = 100 }\n" % (fill, need, fill)
            + "clamp_variable = { var = %s min = 0 max = 100 }\n" % fill
            + setv(lack, need) + "subtract_from_variable = { %s = %s }\n" % (lack, field)
            + iff("check_variable = { %s < 0 }" % lack, setv(lack, 0))
            # A text cuts the fraction of a number off, and equipment in the field has one: the gap is rounded up,
            # so that it is what "Needed" less "In the field" gives on the page.
            + tmp("ar_whole", lack) + "round_temp_variable = ar_whole\n"
            + iff("check_variable = { var = ar_whole value = %s compare = less_than }" % lack,
                  "add_to_temp_variable = { ar_whole = 1 }\n")
            + setv(lack, "ar_whole")))
    equipment_h = 74 + len(EQUIPMENT) * AR_ROW + 12
    equipment_y = AR_HEAD + band_h + 12
    body += card("ar_equipment", 14, equipment_y, AR_IN, equipment_h, "Equipment", inner)

    # ---- armies: one row per general who has troops
    armies_y = equipment_y + equipment_h + 12
    armies_h = AR_H - armies_y - 14
    row_w = AR_TABLE - 30
    # (name, caption, left edge, width, format, value, tip, the variable that hides a zero or None)
    columns = [
        ("name", "Commander", 10, 200, "left", "§Y[THIS.GetName]§!", "A general or field marshal who commands troops. An army without a commander cannot be listed.", None),
        ("rank", "Rank", 212, 60, "centre", None, "A field marshal commands an army group, a general an army.", None),
        ("skill", "Skill", 274, 46, "centre", "[?skill_level|0]", "The commander's skill level.", None),
        ("divisions", "Divisions", 322, 70, "centre", "[?num_units|0]", "Divisions under this commander.", None),
        ("battalions", "Battalions", 394, 80, "centre", "[?num_battalions|0]", "Battalions under this commander.", None),
        ("fighting", "Fighting", 476, 66, "centre", "[?num_units_in_combat|Y0]", "Divisions of this commander that are in combat now.", "num_units_in_combat"),
        ("planning", "Planning", 544, 70, "centre", "[?avg_unit_planning_ratio|%0]", "The planning bonus the divisions have built up, as a share of the most they can have.", None),
        ("fill", "Equipment", 614, 155, "left", None, "The worst equipped kind of equipment of this army: what it has as a share of what its templates ask for, as of the last count. Orange below %d%%." % LOW, None),
        ("inf", "Inf", 781, 36, "centre", "[?num_infantry|0]", "Divisions that are mostly infantry.", "num_infantry"),
        ("arm", "Arm", 817, 36, "centre", "[?num_armored|0]", "Divisions that are mostly armour.", "num_armored"),
        ("mot", "Mot", 853, 36, "centre", "[?num_motorized|0]", "Divisions that are mostly motorised.", "num_motorized"),
    ]
    inner = heads("ar_al_heads", 14, 42, AR_TABLE, [(x, w, caption, fmt, tip) for name, caption, x, w, fmt, value, tip, zero in columns])
    entry = icon("ar_row_stripe", 0, 0, STRIPE % (row_w, ROW))
    row_triggers = block("ar_row_stripe_visible", is_one("mod1440_al_odd") + "\n")
    for name, caption, x, w, fmt, value, tip, zero in columns:
        if value:
            entry += text("ar_row_%s" % name, x, 4, w, B.key("ar_row_%s" % name, value), FONT_LABEL, fmt, 22)
        if zero:
            row_triggers += block("ar_row_%s_visible" % name, more_than_zero(zero))
    for rank, label, trigger in (("fm", "Marshal", "is_field_marshal = yes"), ("gen", "General", "is_corps_commander = yes")):
        entry += text("ar_row_%s" % rank, 212, 5, 60, B.key("ar_rank_%s" % rank, label), FONT_SMALL, "centre", 22)
        row_triggers += block("ar_row_%s_visible" % rank, trigger + "\n")
    low = "check_variable = { mod1440_al_fill < %d }\n" % LOW
    entry += icon("ar_row_bar", 614, 10, bar_sprite(105)) + icon("ar_row_low", 614, 10, bar_sprite(105, low=True))
    entry += text("ar_row_pct", 721, 4, 48, B.key("ar_row_pct", "[?mod1440_al_fill|0]%"), FONT_LABEL, "right", 22)
    properties += block("ar_row_bar", "frame = mod1440_al_fill\n") + block("ar_row_low", "frame = mod1440_al_fill\n")
    row_triggers += block("ar_row_bar_visible", "NOT = { %s }\n" % low.strip()) + block("ar_row_low_visible", low)
    inner += listing("ar_al_list", "ar_al_grid", 14, 72, AR_TABLE, armies_h - 72 - 14, ROW)
    inner += text("ar_al_none", 28, 84, 700, B.key("ar_al_none", "No army has a commander yet. An army is listed here once it has one."), FONT_SMALL)
    triggers += block("ar_al_none_visible", "check_variable = { mod1440_ar_leaders^num < 1 }\n")
    body += card("ar_armies", 14, armies_y, AR_IN, armies_h, "Armies", inner)
    triggers += row_triggers

    gui = box("mod1440_army_readiness", AR_X, AR_Y, AR_W, AR_H, body, PAGE_BG)
    gui += row("mod1440_army_readiness_row", row_w, ROW, entry)

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

    worst = "set_variable = { mod1440_al_fill = 100 }\n"
    for eq in EQUIPMENT:
        worst += block("if", (
            "limit = { check_variable = { num_target_equipment@%s > 0 } }\n"
            "set_temp_variable = { al_share = num_equipment@%s }\n"
            "divide_temp_variable = { al_share = num_target_equipment@%s }\n"
            "multiply_temp_variable = { al_share = 100 }\n" % (eq, eq, eq)
            + block("if", "limit = { check_variable = { al_share < mod1440_al_fill } }\nset_variable = { mod1440_al_fill = al_share }\n")))
    # every second commander of the list gets the darker band (the variable is his own)
    # The game's own loop over the leaders: its array army_leaders holds nothing in the place of a general whose
    # command came by an effect, and neither does THIS. mod1440_of_me gives what a variable can hold of him
    # (tools/build_records.py, places()).
    leaders = ("mod1440_of_refs = yes\nclear_array = mod1440_ar_leaders\n" + tmp("al_odd", 0) + block("every_army_leader", (
        "limit = { check_variable = { num_units > 0 } }\nmod1440_of_me = yes\n" + block("if", (
            "limit = { NOT = { check_variable = { of_me = 0 } } }\n" + worst
            + setv("mod1440_al_odd", "al_odd") + iff("check_variable = { al_odd = 0 }", tmp("al_odd", 1)) + els(tmp("al_odd", 0))
            + "add_to_array = { PREV.mod1440_ar_leaders = of_me }\n")))))
    count = (
        "# Army Readiness: the two division counts, the fill of the equipment bars, what is short and the list of\n"
        "# generals with troops, for the country in scope. Runs at the start of a game for every country, each day\n"
        "# for a player, and on a click.\n"
        + block("mod1440_ar_count",
                "set_variable = { mod1440_ar_low_str = 0 }\nset_variable = { mod1440_ar_low_org = 0 }\n"
                + block("every_country_division", "limit = { unit_strength < 0.75 }\nadd_to_variable = { PREV.mod1440_ar_low_str = 1 }\n")
                + block("every_country_division", "limit = { unit_organization < 0.5 }\nadd_to_variable = { PREV.mod1440_ar_low_org = 1 }\n")
                + fills + leaders
                + "set_variable = { mod1440_ar_counted = global.date }\n"))
    return gui, script, count


# ---------------------------------------------------------------- States (D3), docked to Construction

# One row per state the player controls. A column is (name, value of the state, width, head, tip, group): the
# head is ("text", caption), ("building", frame of GFX_buildings_strip) or ("resource", frame of
# GFX_resources_strip); the tip is a text of the game ("$key$") or of the mod; columns of one group stand
# together, with a gap to the next group.
STATE_COLUMNS = [
    ("free", "mod1440_st_free", 60, ("text", "Free"), "Free building slots for factories and the other buildings that share slots, counted when the list was made.", "free"),
    ("infra", "infrastructure_level", 52, ("building", 3), "$infrastructure$", "build"),
    ("civ", "industrial_complex_level", 52, ("building", 1), "$industrial_complex$", "build"),
    ("mil", "arms_factory_level", 52, ("building", 2), "$arms_factory$", "build"),
    ("dock", "building_level@dockyard", 52, ("building", 4), "$dockyard$", "build"),
    ("refinery", "building_level@synthetic_refinery", 52, ("building", 10), "$synthetic_refinery$", "build"),
    ("silo", "building_level@fuel_silo", 52, ("building", 14), "$fuel_silo$", "build"),
    ("air", "building_level@air_base", 52, ("building", 5), "$air_base$", "build"),
    ("aa", "building_level@anti_air_building", 52, ("building", 9), "$anti_air_building$", "build"),
    ("radar", "building_level@radar_station", 52, ("building", 11), "$radar_station$", "build"),
    ("oil", "resource@oil", 56, ("resource", 1), "$PRODUCTION_MATERIALS_OIL$", "res"),
    ("aluminium", "resource@aluminium", 56, ("resource", 2), "$PRODUCTION_MATERIALS_ALUMINIUM$", "res"),
    ("rubber", "resource@rubber", 56, ("resource", 3), "$PRODUCTION_MATERIALS_RUBBER$", "res"),
    ("tungsten", "resource@tungsten", 56, ("resource", 4), "$PRODUCTION_MATERIALS_TUNGSTEN$", "res"),
    ("steel", "resource@steel", 56, ("resource", 5), "$PRODUCTION_MATERIALS_STEEL$", "res"),
    ("chromium", "resource@chromium", 56, ("resource", 6), "$PRODUCTION_MATERIALS_CHROMIUM$", "res"),
    ("coal", "resource@coal", 56, ("resource", 7), "$PRODUCTION_MATERIALS_COAL$", "res"),
    ("pop", "state_population_k", 84, ("text", "People"), "Population of the state, in thousands.", "people"),
    ("compliance", "compliance", 60, ("text", "Compl."), "$COMPLIANCE$, for a state that is not a core of yours.", "occ"),
    ("resistance", "resistance", 60, ("text", "Resist."), "$RESISTANCE$, for a state that is not a core of yours.", "occ"),
]
STATE_GROUPS = [("build", "Buildings"), ("res", "Resources"), ("occ", "Occupation")]
HEAD_SPRITES = {52: "GFX_1440p_SG_head_52", 56: "GFX_1440p_SG_head_56", 60: "GFX_1440p_SG_head_60",
                84: "GFX_1440p_SG_head_84", 240: "GFX_1440p_SG_head_240", 300: "GFX_1440p_SG_head_300"}

# From the corner of the construction panel (screen -9,78), whose building column ends at x 700.
ST_X, ST_Y = 712, 0
ST_NAME = 240
ST_GAP = 10                     # between the groups of columns


def state_layout():
    """The left edge of every column in a row, the width of a row, and what each group spans."""
    x, last = ST_NAME, None
    edges, spans = {}, {}
    for name, value, width, head, tip, group in STATE_COLUMNS:
        if group != last:
            x += ST_GAP
            last = group
        edges[name] = x
        spans[group] = (spans.get(group, (x, x))[0], x + width)
        x += width
    return edges, x, spans


ST_EDGE, ST_ROWS_W, ST_SPAN = state_layout()
ST_W = 14 + ST_ROWS_W + 30 + 14                             # the page: margins, rows, scrollbar
ST_H = 1210                                                 # ends above the army portraits of the bottom bar
# The captions stand clear of the arrow of the sorted column, which reaches 9 px above its head: in the game a
# caption at 60 ran into it (check of 2026-10-13).
ST_CAPTION_Y, ST_HEAD_Y, ST_LIST_Y = 55, 82, 114
ST_ROW = 30
ST_LIST_H = ST_H - ST_LIST_Y - 14 - ST_ROW - 6              # the totals stand under the list


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

    # ---- title strip, with the choices of which states to list: each a button with a second frame for "chosen"
    body = box("st_head", 3, 3, ST_W - 6, 50, "", "GFX_tiled_header")
    body += text("st_title", 22, 8, 170, B.key("st_title", "States"), FONT_TITLE, height=40)
    body += text("st_hint", ST_W - 86 - 480, 18, 480, B.key("st_hint", "Click a state to see it on the map. Shift+M hides the page."), FONT_SMALL, "right")
    body += button("st_fold", ST_W - 66, 10, "GFX_closebutton", shortcut="shift+m",
                   tooltip=B.key("st_fold_tt", "Hide this page and give the map back"))
    effects += block("st_fold_click", "set_variable = { mod1440_st_open = 0 }\nadd_to_variable = { mod1440_st_dirty = 1 }\n")
    choices = [("all", "All", 0, "Every state you control."), ("core", "Cores", 1, "Only the states that are cores of yours."),
               ("other", "Occupied", 2, "Only the states that are not cores of yours.")]
    for i, (name, label, value, tip) in enumerate(choices):
        body += button("st_show_%s" % name, 200 + i * 104, 13, "GFX_sort_button_100x29", B.key("st_show_%s" % name, label),
                       tooltip=B.key("st_show_%s_tt" % name, tip))
        effects += block("st_show_%s_click" % name, "set_variable = { mod1440_st_show = %d }\nmod1440_st_list = yes\n" % value)
        properties += block("st_show_%s" % name, "frame = mod1440_st_frame_%d\n" % value)
    body += button("st_only_free", 200 + 3 * 104 + 16, 13, "GFX_sort_button_140x29", B.key("st_only_free", "With free slots"),
                   tooltip=B.key("st_only_free_tt", "Only the states with a free slot for a factory."))
    effects += block("st_only_free_click", flip("mod1440_st_only_free") + "mod1440_st_list = yes\n")
    properties += block("st_only_free", "frame = mod1440_st_frame_free\n")
    body += button("st_refresh", 200 + 3 * 104 + 16 + 160, 13, "GFX_sort_button_100x29", B.key("st_refresh", "Refresh"),
                   tooltip=B.key("st_refresh_tt", "Makes the list again. It is made when the page opens, when you sort or choose, and at the start of each day while the page is open. The numbers of a row and the totals are from that moment."))
    effects += block("st_refresh_click", "mod1440_st_list = yes\n")

    # ---- a caption over each group of columns
    for group, caption in STATE_GROUPS:
        low, high = ST_SPAN[group]
        body += text("st_group_%s" % group, 14 + low, ST_CAPTION_Y, high - low, B.key("st_group_%s" % group, "§g%s§!" % caption), FONT_SMALL, "centre", 20)

    # ---- column heads: a click sorts, a second click turns the order
    body += button("st_sort_name", 14, ST_HEAD_Y, HEAD_SPRITES[ST_NAME], B.key("st_sort_name", "State"),
                   tooltip=B.key("st_sort_name_tt", "Back to the order of the game."))
    effects += block("st_sort_name_click", "set_variable = { mod1440_st_sort_by = 0 }\nmod1440_st_list = yes\n")
    keys = ""           # script: the value the list is sorted by
    arrows = ""         # script: where the arrow of the sorted column stands
    sums = ""           # script: this state's values added to the totals
    clear = ""          # script: the totals back to zero
    entry = icon("st_row_stripe", 0, 0, STRIPE % (ST_ROWS_W, ST_ROW))
    entry += button("st_row", 0, 0, HEAD_SPRITES[ST_NAME], tooltip=B.key("st_row_tt", "Show this state on the map"))
    # a state that is not a core of yours has its name in another colour
    entry += plain("st_row_name", 10, 4, ST_NAME - 16, B.key("st_row_name", "[THIS.GetName]"), height=22)
    entry += plain("st_row_occ", 10, 4, ST_NAME - 16, B.key("st_row_occ", "§L[THIS.GetName]§!"), height=22)
    row_triggers = block("st_row_stripe_visible", is_one("mod1440_st_odd") + "\n")
    row_triggers += block("st_row_name_visible", "is_core_of = ROOT\n") + block("st_row_occ_visible", "NOT = { is_core_of = ROOT }\n")
    total = text("st_total_label", 10, 5, ST_NAME - 16, B.key("st_total_label", "Total of the [?mod1440_st_rows^num|0] listed"), FONT_SMALL, height=20)
    for number, (name, value, width, head, tip, group) in enumerate(STATE_COLUMNS, start=1):
        x = 14 + ST_EDGE[name]
        tip_key = B.key("st_sort_%s_tt" % name, tip + "\\nClick to sort, click again to turn the order.")
        if head[0] == "text":
            body += button("st_sort_%s" % name, x, ST_HEAD_Y, HEAD_SPRITES[width], B.key("st_sort_%s" % name, head[1]), tooltip=tip_key)
        else:
            body += button("st_sort_%s" % name, x, ST_HEAD_Y, HEAD_SPRITES[width], tooltip=tip_key)
            sprite, scale, dx, dy = (("GFX_buildings_strip", 0.6, 12, 1) if head[0] == "building" else ("GFX_resources_strip", 0.9, 16, 3))
            body += ('iconType = { name = "st_icon_%s" position = { x = %d y = %d } spriteType = "%s" frame = %d scale = %s '
                     'alwaystransparent = yes }\n' % (name, x + dx, ST_HEAD_Y + dy, sprite, head[1], scale))
        effects += block("st_sort_%s_click" % name, (
            iff("check_variable = { mod1440_st_sort_by = %d }" % number, flip("mod1440_st_up"))
            + els(setv("mod1440_st_sort_by", number) + setv("mod1440_st_up", 0))
            + "mod1440_st_list = yes\n"))
        keys += iff("check_variable = { ROOT.mod1440_st_sort_by = %d }" % number, tmp("st_key", value), "if" if number == 1 else "else_if")
        arrows += iff("check_variable = { mod1440_st_sort_by = %d }" % number, setv("mod1440_st_arrow_x", x + width - ARROW_DX),
                      "if" if number == 1 else "else_if")
        fmt = {"pop": "|0]K", "free": "|G0]"}.get(name, "|0]")
        entry += text("st_cell_%s" % name, ST_EDGE[name] + 2, 4, width - 10, B.key("st_cell_%s" % name, "[?%s%s" % (value, fmt)), FONT_LABEL, "right", 22)
        if group == "occ":
            row_triggers += block("st_cell_%s_visible" % name, "NOT = { is_core_of = ROOT }\n")
            continue
        if name != "pop":
            row_triggers += block("st_cell_%s_visible" % name, more_than_zero(value))
        # the total of the column, over the states that are listed
        total += text("st_total_%s" % name, ST_EDGE[name] + 2, 4, width - 10,
                      B.key("st_total_%s" % name, "[?mod1440_st_sum_%s%s" % (name, "|0]K" if name == "pop" else "|0]")), FONT_LABEL, "right", 22)
        triggers += block("st_total_%s_visible" % name, more_than_zero("mod1440_st_sum_%s" % name))
        sums += "add_to_variable = { ROOT.mod1440_st_sum_%s = %s }\n" % (name, value)
        clear += setv("mod1440_st_sum_%s" % name, 0)
    # the arrow that marks the sorted column: script moves it there
    first = 14 + ST_EDGE[STATE_COLUMNS[0][0]] + STATE_COLUMNS[0][2] - ARROW_DX
    body += scaled("st_arrow_down", first, ST_HEAD_Y + ARROW_DY, "GFX_arrow_down_small", ARROW)
    body += scaled("st_arrow_up", first, ST_HEAD_Y + ARROW_DY, "GFX_arrow_up_small", ARROW)
    properties += block("st_arrow_down", "x = mod1440_st_arrow_x\n") + block("st_arrow_up", "x = mod1440_st_arrow_x\n")
    triggers += block("st_arrow_down_visible", more_than_zero("mod1440_st_sort_by") + "NOT = { check_variable = { mod1440_st_up = 1 } }\n")
    triggers += block("st_arrow_up_visible", more_than_zero("mod1440_st_sort_by") + "check_variable = { mod1440_st_up = 1 }\n")

    # ---- the list, and under it the totals
    body += listing("st_list", "st_grid", 14, ST_LIST_Y, ST_ROWS_W + 30, ST_LIST_H, ST_ROW)
    body += box("st_totals", 14, ST_LIST_Y + ST_LIST_H + 6, ST_ROWS_W, ST_ROW, total, HEAD_SPRITES[240])
    effects += block("st_row_click", block("ROOT", "goto_state = PREV\nset_variable = { mod1440_st_open = 0 }\nadd_to_variable = { mod1440_st_dirty = 1 }\n"))

    gui = box("mod1440_states", ST_X, ST_Y, ST_W, ST_H, body, PAGE_BG)
    gui += row("mod1440_states_row", ST_ROWS_W, ST_ROW, entry)
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
    # every second row of the list gets the darker band (the variable is the state's own)
    bands = tmp("st_odd", 0) + block("for_each_scope_loop", (
        "array = mod1440_st_rows\n" + setv("mod1440_st_odd", "st_odd")
        + iff("check_variable = { st_odd = 0 }", tmp("st_odd", 1)) + els(tmp("st_odd", 0))))
    listing_script = (
        "# States: makes the list of the page again, for the country in scope. For each state it controls: count the\n"
        "# free shared slots, keep the state if the choices of the page want it and add it to the totals; then sort.\n"
        + block("mod1440_st_list", (
            "clear_array = mod1440_st_rows\n" + clear
            + block("for_each_scope_loop", (
                "array = controlled_states\n"
                + free_slot_tree(0, 31)
                + "set_temp_variable = { st_keep = 1 }\n"
                + block("if", block("limit", "check_variable = { ROOT.mod1440_st_show = 1 }\nNOT = { is_core_of = ROOT }\n") + "set_temp_variable = { st_keep = 0 }\n")
                + block("if", block("limit", "check_variable = { ROOT.mod1440_st_show = 2 }\nis_core_of = ROOT\n") + "set_temp_variable = { st_keep = 0 }\n")
                + block("if", block("limit", "check_variable = { ROOT.mod1440_st_only_free = 1 }\ncheck_variable = { mod1440_st_free < 1 }\n") + "set_temp_variable = { st_keep = 0 }\n")
                + iff("check_variable = { st_keep = 1 }", "add_to_array = { ROOT.mod1440_st_rows = THIS }\n" + sums)))
            + "mod1440_st_sort = yes\n" + bands + arrows + frames
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
    return gui, script, listing_script, daily


# ---------------------------------------------------------------- National Figures (D4), opened from Politics

# A row is (label, value, format): the label is a text key of the game (it then follows the player's language)
# or a text of the mod; the value is a variable of the country; the format is what follows the bar in
# "[?value|format]". "+" colours a gain green, "-" colours a gain red (for costs and penalties), "=" adds
# the sign. A value from "modifier@" is the country's summed modifier, the number the game works with.
def modifier_row(key, token, fmt="+=%1"):
    return (key, "modifier@" + token, fmt)


# The cards of summed modifiers: (name, title, column, rows).
FIGURES = [
    ("politics", "Politics", 0, [
        ("Political power per day", "political_power_daily", "+=2"),
        modifier_row("MODIFIER_POLITICAL_POWER_FACTOR", "political_power_factor"),
        modifier_row("MODIFIER_STABILITY_WEEKLY", "stability_weekly", "+=%2"),
        ("Stability from modifiers", "modifier@stability_factor", "+=%1"),
        modifier_row("MODIFIER_WAR_SUPPORT_WEEKLY", "war_support_weekly", "+=%2"),
        ("War support from modifiers", "modifier@war_support_factor", "+=%1"),
        modifier_row("MODIFIER_DRIFT_DEFENCE_FACTOR", "drift_defence_factor"),
        ("Command power per day", "command_power_daily", "+=2"),
        modifier_row("MODIFIER_MAX_COMMAND_POWER", "max_command_power", "+=0"),
        modifier_row("MODIFIER_OPINION_GAIN_MONTHLY_FACTOR", "opinion_gain_monthly_factor"),
        modifier_row("MODIFIER_TRADE_OPINION_FACTOR", "trade_opinion_factor"),
        modifier_row("MODIFIER_JUSTIFY_WAR_GOAL_TIME", "justify_war_goal_time", "-=%1"),
    ]),
    ("manpower", "Manpower", 0, [
        modifier_row("MODIFIER_CONSCRIPTION_FACTOR", "conscription", "%2"),
        modifier_row("MODIFIER_CONSCRIPTION_TOTAL_FACTOR", "conscription_factor"),
        modifier_row("MODIFIER_WEEKLY_MANPOWER", "weekly_manpower", "+=0"),
        modifier_row("MODIFIER_GLOBAL_MONTHLY_POPULATION", "monthly_population"),
        modifier_row("MODIFIER_GLOBAL_NON_CORE_MANPOWER", "non_core_manpower"),
        modifier_row("MODIFIER_MOBILIZATION_SPEED", "mobilization_speed"),
        modifier_row("MODIFIER_TRAINING_TIME_ARMY_FACTOR", "training_time_army_factor", "-=%1"),
        modifier_row("MODIFIER_SPECIAL_FORCES_CAP", "special_forces_cap"),
    ]),
    ("occupation", "Occupation and Diplomacy", 0, [
        modifier_row("MODIFIER_COMPLIANCE_GROWTH", "compliance_growth"),
        modifier_row("MODIFIER_RESISTANCE_TARGET", "resistance_target", "-=%1"),
        modifier_row("MODIFIER_RESISTANCE_GROWTH", "resistance_growth", "-=%1"),
        modifier_row("MODIFIER_RESISTANCE_DECAY", "resistance_decay"),
        modifier_row("MODIFIER_REQUIRED_GARRISON_FACTOR", "required_garrison_factor", "-=%1"),
        modifier_row("MODIFIER_SURRENDER_LIMIT", "surrender_limit"),
        modifier_row("MODIFIER_GUARANTEE_COST", "guarantee_cost", "-=%1"),
        modifier_row("MODIFIER_SEND_VOLUNTEER_SIZE", "send_volunteer_size", "+=0"),
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
    ("research", "Research and Intelligence", 2, [
        modifier_row("MODIFIER_RESEARCH_SPEED_FACTOR", "research_speed_factor"),
        modifier_row("MODIFIER_DECRYPTION_FACTOR", "decryption_factor"),
        modifier_row("MODIFIER_ENCRYPTION_FACTOR", "encryption_factor"),
        modifier_row("MODIFIER_OPERATIVE_SLOT", "operative_slot", "+=0"),
        modifier_row("MODIFIER_INTELLIGENCE_AGENCY_DEFENSE", "intelligence_agency_defense"),
        modifier_row("MODIFIER_INTEL_NETWORK_GAIN_FACTOR", "intel_network_gain_factor"),
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
IDEOLOGIES = ["fascism", "democratic", "communism", "neutrality"]

# What the country has today, as tiles across the page: (name, label, value, tooltip). A grey second number
# is the part of the first that is free.
NF_TILES = [
    ("civ", "Civilian factories", "£civ_factory [?num_of_civilian_factories|0]  §g[?num_of_civilian_factories_available_for_projects|0] free§!",
     "Your civilian factories, and how many of them are free for construction once consumer goods and trade have taken theirs."),
    ("mil", "Military factories", "£mil_factory [?num_of_military_factories|0]  §g[?num_of_available_military_factories|0] idle§!",
     "Your military factories, and how many of them have no production line."),
    ("dock", "Dockyards", "£nav_dockyard_texticon [?num_of_naval_factories|0]  §g[?num_of_available_naval_factories|0] idle§!",
     "Your dockyards, and how many of them have no production line."),
    ("slots", "Research slots", "[?amount_research_slots|0]", None),
    ("techs", "Technologies", "[?num_researched_technologies|0]", "Technologies you have researched."),
    ("states", "States controlled", "[?num_controlled_states|0]", None),
    ("convoys", "Convoys in stock", "[?num_equipment@convoy|0]", "Convoys that no trade, supply route or naval invasion uses."),
    ("trains", "Trains in stock", "[?num_equipment@train_equipment|0]", None),
    ("ships", "Ships", "[?num_ships|0]", None),
    ("planes", "Planes on airfields", "[?num_deployed_planes|0]", "Planes in your air wings."),
]

NF_X, NF_Y = 556, 78            # on the screen: beside the politics panel, which is 550 wide
NF_COL = 400
NF_W = 14 + 4 * NF_COL + 3 * 12 + 14
NF_ROW = 26
NF_GAP = 5                      # between the tiles: ten of them fill the page
NF_WIDE = 2 * TILE_W + NF_GAP   # a plate that takes the place of two tiles


def gauge(name, x, y, label, value, variable, tip=None, wide=True):
    """A share on a plate: its name and its value over a bar that script fills from <variable>, 0 to 100.
    A wide gauge has name and value side by side, a narrow one has them one over the other."""
    tooltip = B.key(name + "_tt", tip) if tip else None
    width = NF_WIDE if wide else TILE_W
    out = icon(name + "_bg", x, y, tile_sprite(width))
    if wide:
        out += text(name + "_l", x + 10, y + 9, 110, label, FONT_SMALL, "left", 20, tooltip=tooltip)
        out += text(name, x + 120, y + 6, width - 130, B.key(name, value), FONT_VALUE, "right", 26, tooltip=tooltip)
        out += icon(name + "_bar", x + 8, y + 42, bar_sprite(300))
    else:
        out += text(name + "_l", x + 6, y + 5, width - 12, label, FONT_SMALL, "centre", 20, tooltip=tooltip)
        out += text(name, x + 6, y + 23, width - 12, B.key(name, value), FONT_VALUE, "centre", 24, tooltip=tooltip)
        out += icon(name + "_bar", x + 8, y + 49, bar_sprite(140))
    return out, block(name + "_bar", "frame = %s\n" % variable)


def figure_card(name, title, rows):
    """A card of summed modifiers. A modifier that changes nothing has a grey name and no value, so that
    what applies stands out. Returns the card's inside, its triggers and its height."""
    inner = stripes("nf_%s_stripe" % name, 14, 44, NF_COL - 28, NF_ROW, len(rows))
    triggers = ""
    for i, (label, value, fmt) in enumerate(rows):
        y = 44 + i * NF_ROW
        # a label in capitals is a text key of the game
        game_key = re.match(r"^[A-Z][A-Z0-9_]*$", label)
        key = label if game_key else B.key("nf_%s_%d" % (name, i), label.strip())
        if value.startswith("modifier@"):
            grey = B.key("nf_%s_%d_dim" % (name, i), ("§g$%s$§!" % label) if game_key else ("§g%s§!" % label.strip()))
            inner += text("nf_%s_dim_%d" % (name, i), 22, y + 2, NF_COL - 44 - 80, grey, FONT_SMALL, height=22)
            changed = "NOT = { check_variable = { %s = 0 } }\n" % value
            triggers += block("nf_%s_label_%d_visible" % (name, i), changed) + block("nf_%s_value_%d_visible" % (name, i), changed)
        inner += text("nf_%s_label_%d" % (name, i), 22, y + 2, NF_COL - 44 - 80, key, FONT_SMALL, height=22)
        inner += text("nf_%s_value_%d" % (name, i), NF_COL - 22 - 100, y, 100,
                      B.key("nf_%s_%d_v" % (name, i), "[?%s|%s]" % (value, fmt)), FONT_LABEL, "right", 22)
    return inner, triggers, 44 + len(rows) * NF_ROW + 12


def national_figures():
    triggers = ""
    properties = ""
    body = box("nf_head", 3, 3, NF_W - 6, 50, "", "GFX_tiled_header")
    body += text("nf_title", 22, 8, 300, B.key("nf_title", "National Figures"), FONT_TITLE, height=40)
    body += text("nf_hint", NF_W - 780, 18, 700, B.key(
        "nf_hint", "Your country's modifiers, summed over every law, spirit, advisor and technology. Grey is no change."), FONT_SMALL, "right")
    body += button("nf_close", NF_W - 66, 10, "GFX_closebutton", shortcut="ESCAPE", tooltip=B.key("nf_close_tt", "Close"))

    # ---- what the country has today: ten tiles, and under them the shares as bars
    band = ""
    step = TILE_W + NF_GAP
    for n, (name, label, value, tip) in enumerate(NF_TILES):
        part, more = tile("nf_" + name, 14 + n * step, 14, label, value, tip)
        band += part
        triggers += more
    y = 14 + TILE_H + NF_GAP
    shares = [("stab", "Stability", "[?stability|%1]", "mod1440_nf_stab", None),
              ("ws", "War support", "[?has_war_support|%1]", "mod1440_nf_ws", None),
              ("fuel", "Fuel", "[?fuel_k|0]K of [?max_fuel_k|0]K", "mod1440_nf_fuel", "Fuel in your stockpile, and what the stockpile can hold.")]
    for n, (name, label, value, variable, tip) in enumerate(shares):
        part, more = gauge("nf_" + name, 14 + 2 * n * step, y, B.key("nf_%s_l" % name, label), value, variable, tip)
        band += part
        properties += more
    for n, ideology in enumerate(IDEOLOGIES):
        # the name of an ideology is a text key of the game
        part, more = gauge("nf_party_%d" % n, 14 + (6 + n) * step, y, ideology, "[?party_popularity@%s|%%0]" % ideology,
                           "mod1440_nf_party_%d" % n, wide=False)
        band += part
        properties += more
    band_h = y + TILE_H + 14
    body += box("nf_today", 14, AR_HEAD, NF_W - 28, band_h, band, CARD_BG)

    # ---- the summed modifiers, a card per subject
    top = AR_HEAD + band_h + 12
    bottoms = [top, top, top, top]

    def place(name, title, column, inner, height):
        nonlocal body
        body += card("nf_%s" % name, 14 + column * (NF_COL + 12), bottoms[column], NF_COL, height, title, inner)
        bottoms[column] += height + 12

    for name, title, column, rows in FIGURES:
        inner, more, height = figure_card(name, title, rows)
        triggers += more
        place(name, title, column, inner, height)
        if name == "industry":
            # resources: a small table under the industry card
            cols = [("balance", "Balance", "resource", "+=0", "What is left after your own use and your exports."),
                    ("made", "Made", "resource_produced", "0", "Produced in your states."),
                    ("used", "Used", "resource_consumed", "0", "Used by your production lines."),
                    ("in", "Import", "resource_imported", "0", "Bought from other countries."),
                    ("out", "Export", "resource_exported", "0", "Sold to other countries.")]
            name_w, col_w = 112, 52
            inner = heads("nf_res_heads", 14, 42, NF_COL - 28, [(8, 100, "Resource", "left", None)] + [
                (name_w + c * col_w, col_w - 4, caption, "right", tip) for c, (cname, caption, variable, fmt, tip) in enumerate(cols)])
            inner += stripes("nf_res_stripe", 14, 74, NF_COL - 28, NF_ROW, len(RESOURCES))
            for r, resource in enumerate(RESOURCES):
                y = 74 + r * NF_ROW
                inner += text("nf_res_name_%d" % r, 22, y + 2, name_w - 10, B.key(
                    "nf_res_name_%d" % r, "£resources_strip|%d  $PRODUCTION_MATERIALS_%s$" % (r + 1, resource.upper())), FONT_SMALL, height=22)
                for c, (cname, caption, variable, fmt, tip) in enumerate(cols):
                    inner += text("nf_res_%s_%d" % (cname, r), 14 + name_w + c * col_w, y, col_w - 4,
                                  B.key("nf_res_%s_%d" % (cname, r), "[?%s@%s|%s]" % (variable, resource, fmt)), FONT_LABEL, "right", 22)
                    if cname != "balance":
                        triggers += block("nf_res_%s_%d_visible" % (cname, r), more_than_zero("%s@%s" % (variable, resource)))
            place("res", "Resources", column, inner, 74 + len(RESOURCES) * NF_ROW + 12)

    body += button("nf_history", 330, 12, "GFX_button_123x34", B.key("nf_history", "History"),
                   tooltip=B.key("nf_history_tt", "How twelve figures of your country have moved, month by month"))
    gui = box("mod1440_figures", NF_X, NF_Y, NF_W, max(bottoms) + 2, body, PAGE_BG)
    # the button that opens it sits in the title strip of the politics panel, between the title and the icons
    handle = button("nf_toggle", 0, 0, "GFX_button_148x34", B.key("nf_toggle", "National Figures"), shortcut="shift+m",
                    tooltip=B.key("nf_toggle_tt", "Show or hide the summed modifiers and figures of your country"))
    gui += box("mod1440_figures_handle", 262, 12, 148, 34, handle)

    script = scripted_gui("mod1440_figures", "mod1440_figures",
                          visible="check_variable = { mod1440_nf_open = 1 }\nNOT = { check_variable = { mod1440_nf_page = 1 } }\n",
                          effects=(block("nf_close_click", "set_variable = { mod1440_nf_open = 0 }\n")
                                   + block("nf_history_click", "set_variable = { mod1440_nf_page = 1 }\nmod1440_h_draw = yes\n")),
                          triggers=triggers, properties=properties)
    script += "\n" + scripted_gui("mod1440_figures_handle", "mod1440_figures_handle", "politics_tab",
                                  effects=block("nf_toggle_click", flip("mod1440_nf_open") + "mod1440_nf_bars = yes\nmod1440_h_draw = yes\n"))

    # A bar is filled by a variable and by nothing else (Engine Facts X26), so the shares are worked out here.
    bars = (setv("mod1440_nf_stab", "stability") + "multiply_variable = { mod1440_nf_stab = 100 }\n"
            + setv("mod1440_nf_ws", "has_war_support") + "multiply_variable = { mod1440_nf_ws = 100 }\n"
            + setv("mod1440_nf_fuel", 0) + iff("check_variable = { max_fuel_k > 0 }", (
                setv("mod1440_nf_fuel", "fuel_k") + "divide_variable = { mod1440_nf_fuel = max_fuel_k }\n"
                "multiply_variable = { mod1440_nf_fuel = 100 }\nclamp_variable = { var = mod1440_nf_fuel min = 0 max = 100 }\n"))
            + "".join(setv("mod1440_nf_party_%d" % n, "party_popularity@" + ideology) + "multiply_variable = { mod1440_nf_party_%d = 100 }\n" % n
                      for n, ideology in enumerate(IDEOLOGIES)))
    script_effects = (
        "# National Figures: how far the bars of the page are filled, 0 to 100, for the country in scope. Runs when\n"
        "# the page opens and each day for a player; the numbers beside the bars follow the game by themselves.\n"
        + block("mod1440_nf_bars", bars))
    # Each day, open or not: a few lines of script, and a page left open in a saved game is right again after
    # a day at most.
    daily = "mod1440_nf_bars = yes\n"
    return gui, script, script_effects, daily


# ---------------------------------------------------------------- History (D5), the second page of National Figures

# A series is (caption, value of the country, factor, unit, decimals, rise): the value is written down on the
# first of each month, times the factor (100 turns a 0 to 1 share into a percentage). decimals is how the
# number is written, rise the colour of a change: "+" a rise is green, "-" a rise is red.
SERIES = [
    ("Free manpower", "manpower_k", 1, "thousands", 1, "+"),
    ("Manpower in the field", "deployed_total_manpower_k", 1, "thousands", 1, "+"),
    ("Divisions", "num_divisions", 1, "", 0, "+"),
    ("Civilian factories", "num_of_civilian_factories", 1, "", 0, "+"),
    ("Military factories", "num_of_military_factories", 1, "", 0, "+"),
    ("Dockyards", "num_of_naval_factories", 1, "", 0, "+"),
    ("Stability", "stability", 100, "percent", 1, "+"),
    ("War support", "has_war_support", 100, "percent", 1, "+"),
    ("Fuel", "fuel_k", 1, "thousands", 1, "+"),
    ("Infantry equipment in stock", "num_equipment@infantry_equipment", 1, "", 0, "+"),
    ("Casualties", "casualties_k", 1, "thousands", 1, "-"),
    ("Political power", "political_power", 1, "", 0, "+"),
]
H_KEEP = 120            # months on the graph: ten years
H_STEPS = 200           # heights a column can have (the "steps" of the column sprite)
H_COLUMN = 8            # px from one column to the next
H_W = NF_W              # the page is as wide as National Figures, whose place it takes
H_CHART_W, H_CHART_H = H_KEEP * H_COLUMN, 268
H_AXIS = 20             # under the columns: the years
H_YEARS = 10            # year marks under the graph: ten years have at most ten first months
H_INSET = 4                                         # the columns stand this far inside the frame of the graph
H_GRAPH_W = 14 + 66 + H_CHART_W + 2 * H_INSET + 14  # the card of the graph: margin, scale, columns in their frame, margin
H_TABLE_W = H_W - 14 - 12 - H_GRAPH_W - 14          # the card of the table
H_NAME, H_NUM = 240, 100                            # the table's columns: the figure, and three numbers
H_CARD_H = 74 + len(SERIES) * ROW + 12
H_COLUMN_SPRITE = "GFX_1440p_SG_column_%dx%d" % (H_COLUMN - 2, H_CHART_H)


def history():
    effects = ""
    triggers = ""
    properties = ""
    some = more_than_zero("mod1440_h_date^num")
    body = box("h_head", 3, 3, H_W - 6, 50, "", "GFX_tiled_header")
    body += text("h_title", 22, 8, 300, B.key("h_title", "History"), FONT_TITLE, height=40)
    body += button("h_figures", 330, 12, "GFX_button_123x34", B.key("h_figures", "Figures"),
                   tooltip=B.key("h_figures_tt", "Back to the figures of today"))
    body += text("h_hint", H_W - 860, 18, 780, B.key(
        "h_hint", "Written down on the first of each month since [?mod1440_h_first.GetDateStringNoHourLong], ten years at most."), FONT_SMALL, "right")
    body += button("h_close", H_W - 66, 10, "GFX_closebutton", shortcut="ESCAPE", tooltip=B.key("h_close_tt", "Close"))
    effects += block("h_close_click", "set_variable = { mod1440_nf_open = 0 }\nadd_to_variable = { mod1440_h_dirty = 1 }\n")
    effects += block("h_figures_click", "set_variable = { mod1440_nf_page = 0 }\nmod1440_nf_bars = yes\nadd_to_variable = { mod1440_h_dirty = 1 }\n")

    # ---- the twelve figures as a table: the newest month, and how it moved in a month and in a year
    table_w = H_TABLE_W - 28
    edges = [H_NAME + (k + 1) * H_NUM - 8 for k in range(3)]            # right edges of the three numbers
    inner = heads("h_tab_heads", 14, 42, table_w, [
        (10, H_NAME - 20, "Figure", "left", "Click a figure to see its months."),
        (edges[0] - 90, 90, "Latest", "right", "The newest month written down."),
        (edges[1] - 90, 90, "In a month", "right", "The change since the month before."),
        (edges[2] - 90, 90, "In a year", "right", "The change since twelve months before."),
    ])
    inner += stripes("h_tab_stripe", 14, 74, table_w, ROW, len(SERIES))
    copies = ""         # script: the chosen figure's months
    names = ""          # the name of each figure, to head the graph
    table = ""          # script: the numbers of the table
    for n, (caption, value, factor, unit, decimals, rise) in enumerate(SERIES):
        y = 74 + n * ROW
        chosen = "check_variable = { mod1440_h_series = %d }\n" % n
        inner += icon("h_pick_%d" % n, 14, y, PICK % (table_w, ROW))
        inner += button("h_series_%d" % n, 14, y, HEAD_SPRITES[H_NAME], tooltip=B.key("h_series_tt", "Show the months of this figure"))
        inner += plain("h_series_name_%d" % n, 24, y + 4, H_NAME - 16, B.key("h_series_%d" % n, caption), height=22)
        inner += text("h_tab_now_%d" % n, 14 + edges[0] - 90, y + 4, 90,
                      B.key("h_tab_now_%d" % n, "[?mod1440_h_tab_now^%d|%d]" % (n, decimals)), FONT_LABEL, "right", 22)
        for k, part in ((1, "m"), (2, "y")):
            inner += text("h_tab_%s_%d" % (part, n), 14 + edges[k] - 90, y + 4, 90,
                          B.key("h_tab_%s_%d" % (part, n), "[?mod1440_h_tab_%s^%d|%s=%d]" % (part, n, rise, decimals)), FONT_LABEL, "right", 22)
            triggers += block("h_tab_%s_%d_visible" % (part, n), is_one("mod1440_h_has_" + part) + "\n")
        triggers += block("h_pick_%d_visible" % n, chosen) + block("h_tab_now_%d_visible" % n, some)
        effects += block("h_series_%d_click" % n, "set_variable = { mod1440_h_series = %d }\nmod1440_h_draw = yes\n" % n)
        title = caption + (", " + unit if unit else "")
        copies += iff("check_variable = { mod1440_h_series = %d }" % n, (
            block("for_each_loop", "array = mod1440_h_%d\nvalue = h_v\nadd_to_array = { mod1440_h_now = h_v }\n" % n)
            + setv("mod1440_h_dec", decimals)), "if" if n == 0 else "else_if")
        table += ("add_to_array = { mod1440_h_tab_now = mod1440_h_%d^h_i1 }\n" % n
                  + tmp("h_d", 0) + iff("check_variable = { h_n > 1 }", tmp("h_d", "mod1440_h_%d^h_i1" % n)
                                         + "subtract_from_temp_variable = { h_d = mod1440_h_%d^h_i2 }\n" % n)
                  + "add_to_array = { mod1440_h_tab_m = h_d }\n"
                  + tmp("h_d", 0) + iff("check_variable = { h_n > 12 }", tmp("h_d", "mod1440_h_%d^h_i1" % n)
                                         + "subtract_from_temp_variable = { h_d = mod1440_h_%d^h_i13 }\n" % n)
                  + "add_to_array = { mod1440_h_tab_y = h_d }\n")
        # the name of the chosen figure heads the graph
        triggers += block("h_name_%d_visible" % n, chosen)
        names += text("h_name_%d" % n, 14, 8, 600, B.key("h_name_%d" % n, title), FONT_CARD, height=30)
    body += card("h_table", 14, AR_HEAD, H_TABLE_W, H_CARD_H, "Twelve figures", inner)

    # ---- the graph of the chosen figure
    def number(name, x, y, width, variable, font, fmt, sign=""):
        """A number of the chosen figure, written with its own decimals: one text for each way of writing."""
        out, extra = "", ""
        for decimals in (0, 1):
            widget = "%s_%d" % (name, decimals)
            out += text(widget, x, y, width, B.key(widget, "[?%s|%s%d]" % (variable, sign, decimals)), font, fmt, 24)
            extra += block(widget + "_visible", some + "check_variable = { mod1440_h_dec = %d }\n" % decimals)
        return out, extra

    chart_x, chart_y = 14 + 66, 118
    inner = names
    inner += button("h_zoom", H_GRAPH_W - 14 - 140, 9, "GFX_sort_button_140x29", B.key("h_zoom", "Zoom in"), tooltip=B.key(
        "h_zoom_tt", "The columns start at the lowest month instead of at zero, so that small changes show."))
    effects += block("h_zoom_click", flip("mod1440_h_zoom") + "mod1440_h_draw = yes\n")
    properties += block("h_zoom", "frame = mod1440_h_zoom_frame\n")
    figures = [("latest", "Latest", "mod1440_h_latest", "", "The newest month written down."),
               ("max", "Highest", "mod1440_h_max", "", "The highest month on the graph."),
               ("min", "Lowest", "mod1440_h_min", "", "The lowest month on the graph."),
               ("change", "Since the first month", "mod1440_h_change", "+=", "The newest month less the oldest month on the graph.")]
    for k, (name, label, variable, sign, tip) in enumerate(figures):
        x = 14 + k * (TILE_W + 8)
        tooltip = B.key("h_%s_tt" % name, tip)
        inner += icon("h_%s_bg" % name, x, 44, tile_sprite())
        inner += text("h_%s_l" % name, x + 6, 51, TILE_W - 12, B.key("h_%s_l" % name, label), FONT_SMALL, "centre", 20, tooltip=tooltip)
        part, more = number("h_" + name, x + 6, 74, TILE_W - 12, variable, FONT_VALUE, "centre", sign)
        inner += part
        triggers += more
    part, more = tile("h_months", 14 + 4 * (TILE_W + 8), 44, "Months on record", "[?mod1440_h_date^num|0]", "Months written down, 120 at most.")
    inner += part
    # the scale on the left: five heights, from the foot of the columns to the highest month
    for k in range(5):
        part, more = number("h_scale_%d" % k, 14, chart_y + H_CHART_H - k * (H_CHART_H // 4) - 10, 60, "mod1440_h_s%d" % k, FONT_SMALL, "right")
        inner += part
        triggers += more
    # the columns stand on bands a quarter of the height each, and have the years under them
    bands = "".join(icon("h_band_%d" % k, H_INSET, k * (H_CHART_H // 4), STRIPE % (H_CHART_W, H_CHART_H // 4)) for k in (1, 3))
    grid = ('gridboxtype = {\n\tname = "h_grid"\n\tposition = { x = %d y = 0 }\n\tsize = { width = %d height = %d }\n'
            '\tslotsize = { width = %d height = %d }\n\tadd_horizontal = yes\n\tmax_slots_horizontal = %d\n\tformat = "UPPER_LEFT"\n}\n'
            % (H_INSET, H_CHART_W, H_CHART_H + H_AXIS, H_COLUMN, H_CHART_H + H_AXIS, H_KEEP))
    inner += box("h_chart", chart_x, chart_y, H_CHART_W + 2 * H_INSET, H_CHART_H + H_AXIS, bands + grid, CARD_BG)
    inner += text("h_from", chart_x + H_INSET, chart_y + H_CHART_H + H_AXIS + 4, 300, B.key("h_from", "[?mod1440_h_first.GetDateStringNoHourLong]"), FONT_SMALL, height=20)
    inner += text("h_to", chart_x + H_INSET + H_CHART_W - 300, chart_y + H_CHART_H + H_AXIS + 4, 300,
                  B.key("h_to", "[?mod1440_h_last.GetDateStringNoHourLong]"), FONT_SMALL, "right", 20)
    # a game that got the mod after its start has nothing written down until the first of the next month
    inner += text("h_none", chart_x + 20, chart_y + 120, 900, B.key(
        "h_none", "Nothing is written down yet. The first column comes on the first of next month."), FONT_LABEL)
    triggers += block("h_none_visible", "NOT = { %s }\n" % some.strip())
    for name in ("h_hint", "h_from", "h_to"):
        triggers += block(name + "_visible", some)
    body += box("h_graph", 14 + H_TABLE_W + 12, AR_HEAD, H_GRAPH_W, H_CARD_H, inner, CARD_BG)
    # Under the columns, the year at each first month written down in a new year. The texts belong to the
    # page and script moves them (the x property, as the arrow of a sorted column: Engine Facts X4).
    marks = ""          # script: the k-th year mark gets its year and its place
    first_x = 14 + H_TABLE_W + 12 + chart_x + H_INSET + H_COLUMN // 2 - 20
    for k in range(H_YEARS):
        body += text("h_year_%d" % k, first_x, AR_HEAD + chart_y + H_CHART_H + 1, 40,
                     B.key("h_year_%d" % k, "[?mod1440_h_yl_%d|0]" % k), FONT_SMALL, "centre", 18)
        properties += block("h_year_%d" % k, "x = mod1440_h_yx_%d\n" % k)
        triggers += block("h_year_%d_visible" % k, more_than_zero("mod1440_h_yl_%d" % k))
        marks += iff("check_variable = { h_slot = %d }" % k, setv("mod1440_h_yl_%d" % k, "h_y") + setv("mod1440_h_yx_%d" % k, "h_x"),
                     "if" if k == 0 else "else_if")

    gui = box("mod1440_history", NF_X, NF_Y, H_W, AR_HEAD + H_CARD_H + 14, body, PAGE_BG)
    column = ('iconType = { name = "h_bar" position = { x = 1 y = 0 } spriteType = "%s" pdx_tooltip = "%s" }\n'
              % (H_COLUMN_SPRITE, B.key("h_bar_tt", "[?mod1440_h_date^i.GetDateStringNoHourLong]: [?mod1440_h_now^i|1]")))
    gui += row("mod1440_history_column", H_COLUMN, H_CHART_H + H_AXIS, column)
    properties += block("h_bar", "frame = v\n")

    script = scripted_gui(
        "mod1440_history", "mod1440_history",
        visible="check_variable = { mod1440_nf_open = 1 }\ncheck_variable = { mod1440_nf_page = 1 }\n", dirty="mod1440_h_dirty",
        lists=block("h_grid", 'array = mod1440_h_bars\nentry_container = "mod1440_history_column"\n'),
        effects=effects, triggers=triggers, properties=properties)

    record = "".join(
        ("add_to_array = { mod1440_h_%d = %s }\n" % (n, value)) if factor == 1 else (
            "set_temp_variable = { h_v = %s }\nmultiply_temp_variable = { h_v = %d }\nadd_to_array = { mod1440_h_%d = h_v }\n" % (value, factor, n))
        for n, (caption, value, factor, unit, decimals, rise) in enumerate(SERIES))
    forget = "".join("remove_from_array = { array = mod1440_h_%d index = 0 }\n" % n for n in range(len(SERIES)))
    # A game that had the mod before the years were written down has months without one: they get a 0 in
    # front, which shows no year.
    years = (block("for_loop_effect", "start = 0\nend = %d\nvalue = h_pad\n" % H_KEEP + iff(
        "check_variable = { mod1440_h_year^num < mod1440_h_date^num }", "add_to_array = { array = mod1440_h_year value = 0 index = 0 }\n"))
        + "".join(setv("mod1440_h_yl_%d" % k, 0) for k in range(H_YEARS)) + tmp("h_before", 0) + tmp("h_slot", 0)
        + block("for_each_loop", (
            "array = mod1440_h_year\nvalue = h_y\nindex = h_yi\n"
            + iff("check_variable = { h_yi > 0 }", iff("check_variable = { h_y > 0 }", iff("NOT = { check_variable = { h_y = h_before } }", (
                tmp("h_x", "h_yi") + "multiply_temp_variable = { h_x = %d }\nadd_to_temp_variable = { h_x = %d }\n" % (H_COLUMN, first_x)
                + marks + "add_to_temp_variable = { h_slot = 1 }\n"))))
            + tmp("h_before", "h_y"))))
    scale = (tmp("h_base", 0) + iff(is_one("mod1440_h_zoom"), tmp("h_base", "h_min"))
             + tmp("h_range", "h_max") + "subtract_from_temp_variable = { h_range = h_base }\n"
             + tmp("h_quarter", "h_range") + "divide_temp_variable = { h_quarter = 4 }\n"
             + setv("mod1440_h_s0", "h_base")
             + "".join(setv("mod1440_h_s%d" % k, "mod1440_h_s%d" % (k - 1)) + "add_to_variable = { mod1440_h_s%d = h_quarter }\n" % k for k in (1, 2, 3))
             + setv("mod1440_h_s4", "h_max"))
    bars = ("clear_array = mod1440_h_bars\n" + block("for_each_loop", (
        "array = mod1440_h_now\nvalue = h_v\n" + tmp("h_bar", 0)
        + iff("check_variable = { h_range > 0 }", tmp("h_bar", "h_v") + "subtract_from_temp_variable = { h_bar = h_base }\n"
              "divide_temp_variable = { h_bar = h_range }\nmultiply_temp_variable = { h_bar = %d }\n" % H_STEPS)
        # every month the same: the columns stand at full height
        + iff("check_variable = { h_v > 0 }", tmp("h_bar", H_STEPS), "else_if")
        # zoomed in, the lowest month keeps a sliver: it was written down
        + iff(is_one("mod1440_h_zoom"), iff("check_variable = { h_bar < 4 }", tmp("h_bar", 4)))
        + "add_to_array = { mod1440_h_bars = h_bar }\n" + setv("mod1440_h_latest", "h_v"))))
    script_effects = (
        "# History: writes today's figures of the country in scope down, and forgets the oldest month past ten years.\n"
        "# Runs at the start of a game for every country and on the first of each month for a player.\n"
        + block("mod1440_h_record", (
            record + "add_to_array = { mod1440_h_date = global.date }\nadd_to_array = { mod1440_h_year = global.year }\n"
            + iff("check_variable = { mod1440_h_date^num > %d }" % H_KEEP, forget
                  + "remove_from_array = { array = mod1440_h_date index = 0 }\nremove_from_array = { array = mod1440_h_year index = 0 }\n")
            + iff(is_one("mod1440_nf_page"), "mod1440_h_draw = yes\n")))
        + "\n# History: the numbers of the table, then the chosen figure as column heights, 0 to %d, between the foot of\n" % H_STEPS
        + "# the graph (zero, or the lowest month when zoomed in) and the highest month.\n"
        + block("mod1440_h_draw", (
            tmp("h_n", "mod1440_h_date^num")
            + "".join(tmp("h_i%d" % k, "h_n") + "subtract_from_temp_variable = { h_i%d = %d }\n" % (k, k) for k in (1, 2, 13))
            + "clear_array = mod1440_h_tab_now\nclear_array = mod1440_h_tab_m\nclear_array = mod1440_h_tab_y\n"
            + iff("check_variable = { h_n > 0 }", table)
            + setv("mod1440_h_has_m", 0) + iff("check_variable = { h_n > 1 }", setv("mod1440_h_has_m", 1))
            + setv("mod1440_h_has_y", 0) + iff("check_variable = { h_n > 12 }", setv("mod1440_h_has_y", 1))
            + "clear_array = mod1440_h_now\n" + copies
            + tmp("h_max", 0)
            + block("find_highest_in_array", "array = mod1440_h_now\nvalue = h_max\nindex = h_at\n")
            # the lowest month, with a loop of the page's own: no script of the game uses find_lowest_in_array
            + tmp("h_min", "h_max") + block("for_each_loop", "array = mod1440_h_now\nvalue = h_v\n"
                                             + iff("check_variable = { h_v < h_min }", tmp("h_min", "h_v")))
            + setv("mod1440_h_max", "h_max") + setv("mod1440_h_min", "h_min")
            + scale + bars
            + years
            + iff("check_variable = { h_n > 0 }", (
                setv("mod1440_h_change", "mod1440_h_latest") + "subtract_from_variable = { mod1440_h_change = mod1440_h_now^0 }\n"
                + setv("mod1440_h_first", "mod1440_h_date^0") + setv("mod1440_h_last", "mod1440_h_date^h_i1")))
            + setv("mod1440_h_zoom_frame", 1) + iff(is_one("mod1440_h_zoom"), setv("mod1440_h_zoom_frame", 2))
            + "add_to_variable = { mod1440_h_dirty = 1 }\n")))
    monthly = "mod1440_h_record = yes\n"
    # The page is drawn when its "dirty" variable changes and not before (Engine Facts X16): while it is open
    # it is drawn again each day, so that a game loaded with the page open shows it after a day at most.
    daily = iff(is_one("mod1440_nf_open"), iff(is_one("mod1440_nf_page"), "mod1440_h_draw = yes\n"))
    return gui, script, script_effects, monthly, daily


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
             "hide": (["ar_al_none"] + ["ar_%s_z" % n for n in ("mp_training", "mp_garrison", "low_str", "low_org")]
                      + ["ar_eq_%s_%d" % (part, i) for part in ("short", "dim", "low") for i in range(len(EQUIPMENT))]),
             "_note": "Docked to Recruit & Deploy: the tab's corner at -6,78 plus the container's 1256,0. Hidden here: the twin of a value that script shows in its place (a plain 0, a red number, a grey name, an orange bar)."},
            {"name": "mod1440_army_readiness_row", "skip": True, "hide": ["ar_row_gen", "ar_row_low"]},
        ],
        "setup": [{"move": "open_recruit_deploy"}],
        "expect": ["mod1440_army_readiness/ar_fold", "mod1440_army_readiness/ar_count"],
        "crop": [1240, 70, 1000, 1230],
        "manual": ["The page after a day has passed: the counts and the bars come from a daily hook, which no check runs"],
        "checklist": [
            "Shift+M hides the page and brings it back; the handle beside the template panel does the same",
            "Train a division: In training rises, In stock falls",
            "Assign a general to an army, press Count again: the general is listed under Armies",
            "After a few days of game time the date under Count again is today's",
        ],
    },
    "states": {
        "phase": "D3", "file": "mod1440_states.gui", "screenshot": "reference/vanilla/construction.jpg",
        "windows": [
            {"name": "mod1440_states", "at": [703, 78], "sidePanel": True,
             "rows": {"st_grid": 24}, "listRows": {"st_grid": "mod1440_states_row"},
             "hide": ["st_arrow_up", "st_arrow_down"],
             "_note": "Docked to Construction: the tab's corner at -9,78 plus the container's 712,0. The vanilla window has clipping = no."},
            {"name": "mod1440_states_row", "skip": True, "hide": ["st_row_occ"]},
        ],
        "setup": [{"move": "open_construction"}, {"key": "shift+m", "wait": 1.5, "_note": "the page is hidden until asked for"}],
        "teardown": [{"key": "shift+m", "wait": 0.8, "_note": "hide it again: the page remembers per country whether it is open"}],
        "expect": ["mod1440_states/st_fold", "mod1440_states/st_refresh"],
        "crop": [690, 70, ST_W + 30, 1230],
        "manual": ["A country with occupied states: the Occupied choice, compliance and resistance, the other colour of a name"],
        "checklist": [
            "A click on a column head sorts, a second click turns the order; State gives the game's order back",
            "A click on a state moves the camera there and hides the page",
            "Free slots of a state against its state view (unlocked slots minus buildings)",
            "The totals against the sum of a column",
        ],
    },
    "national_figures": {
        "phase": "D4", "file": "mod1440_figures.gui", "screenshot": "reference/vanilla/politics.jpg",
        "windows": [{"name": "mod1440_figures", "at": [NF_X, NF_Y], "sidePanel": True,
                     "hide": ["nf_%s_dim_%d" % (name, i) for name, title, column, rows in FIGURES
                              for i, row in enumerate(rows) if row[1].startswith("modifier@")],
                     "_note": "A window of its own beside the politics panel, opened from the button in that panel's title strip. Every modifier is drawn as if it applied: script shows the grey twin of a name instead when it does not."}],
        "setup": [{"move": "open_politics"}, {"key": "shift+m", "wait": 1.5}],
        "teardown": [{"key": "shift+m", "wait": 0.8}],
        "expect": ["mod1440_figures/nf_close", "mod1440_figures/nf_history"],
        "crop": [546, 70, 1700, 1200],
        "manual": [],
        "checklist": ["A modifier against the tooltip of its source: a law, a spirit or an advisor", "Escape closes the page and leaves Politics open"],
    },
    "history": {
        "phase": "D5", "file": "mod1440_figures.gui", "screenshot": "reference/vanilla/politics.jpg",
        "windows": [
            {"name": "mod1440_history", "at": [NF_X, NF_Y], "rows": {"h_grid": 36}, "listRows": {"h_grid": "mod1440_history_column"},
             "hide": (["h_name_%d" % n for n in range(1, len(SERIES))] + ["h_pick_%d" % n for n in range(1, len(SERIES))] + ["h_none"]
                      + ["h_%s_0" % n for n in ("latest", "max", "min", "change")] + ["h_scale_%d_0" % k for k in range(5)]
                      + ["h_year_%d" % k for k in range(H_YEARS)]),
             "_note": "The first figure is the chosen one: script hides the names and the marks of the eleven others, and one of the two ways each number is written."},
            {"name": "mod1440_history_column", "skip": True},
        ],
        "setup": [{"move": "open_politics"}, {"key": "shift+m", "wait": 1.5},
                  {"clickWidget": "mod1440_figures/nf_history", "scene": "national_figures", "wait": 1.2}],
        "teardown": [{"clickWidget": "mod1440_history/h_figures", "wait": 0.8}, {"key": "shift+m", "wait": 0.8}],
        "expect": ["mod1440_history/h_close", "mod1440_history/h_figures"],
        "crop": [546, 70, 1700, 560],
        "manual": ["More than one month: the graph gets a column on the first of each month, which no check lets pass"],
        "checklist": ["After some months of game time each figure has one column per month", "The tooltip of a column gives its month and value",
                      "Zoom in: the columns start at the lowest month", "A click on a figure of the table draws it"],
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
    "mod1440_h_date^num": "120", "mod1440_st_sum_pop": "125000",
    "num_equipment@convoy": "1250", "num_equipment@train_equipment": "250",
}


def sample_for(window, text_value):
    """A text with its values written in, as wide as the game will make it."""
    def one(match):
        inside = match.group(1)
        if window.startswith(("mod1440_records", "mod1440_state_card")):
            return build_records.sample(inside)
        if "GetName" in inside:
            return "Gerd von Rundstedt" if "army_readiness" in window else "Niederschlesien"
        if "GetDateStringNoHourLong" in inside:
            return "30 September, 1944"
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
        if "_fill" in variable or variable.startswith("mod1440_nf_"):
            return "87"
        if variable.startswith("mod1440_h_yl"):
            return "1944"
        if variable.startswith("mod1440_h_"):
            return "1332.6"
        if variable.startswith(("mod1440_ar_short", "mod1440_st_sum")):
            return "1250"
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
    for name, scene in list(SCENES.items()) + list(build_records.SCENES.items()):
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
    gui, script, shares, figures_daily = national_figures()
    history_gui, history_script, recording, monthly, history_daily = history()
    B.files["interface/mod1440_figures.gui"] = HEADER_GUI + "guiTypes = {\n" + indent(gui + history_gui) + "}\n"
    B.files["common/scripted_guis/mod1440_figures.txt"] = HEADER_TXT + block("scripted_gui", script + "\n" + history_script)
    B.files["common/scripted_effects/mod1440_effects.txt"] = HEADER_TXT + count + "\n" + listing + "\n" + shares + "\n" + recording
    # The Records window of Milestone E: its pages, its recording and its hooks (tools/build_records.py)
    gui, script, records_effects, hooks, more_files = build_records.build(sys.modules[__name__])
    for rel, content in more_files.items():
        B.files[rel] = content
    B.files["interface/mod1440_records.gui"] = HEADER_GUI + "guiTypes = {\n" + indent(gui) + "}\n"
    B.files["common/scripted_guis/mod1440_records.txt"] = HEADER_TXT + block("scripted_gui", script)
    B.files["common/scripted_effects/mod1440_records.txt"] = HEADER_TXT + records_effects
    # The hooks. A new game: count and write down once for every country, so that whichever country the
    # player takes has its numbers from the first day. After that only a player's country costs time.
    B.files["common/on_actions/mod1440_on_actions.txt"] = HEADER_TXT + block("on_actions", (
        block("on_startup", block("effect", block("every_country", "mod1440_ar_count = yes\n" + monthly
                                                 + block("if", "limit = { is_ai = no }\nmod1440_ev_init = yes\n"))))
        + block("on_daily", block("effect", block("if", "limit = { is_ai = no }\nmod1440_ar_count = yes\n" + states_daily
                                                  + figures_daily + history_daily + "mod1440_rec_daily = yes\n")))
        + block("on_monthly", block("effect", block("if", "limit = { is_ai = no }\n" + monthly)))
        + "".join(block(name, block("effect", body)) for name, body in sorted(hooks.items()))))

    everything = "".join(B.files.values()) + "".join(B.loc.values())
    # A sprite the pages name and interface/1440p_ui.gfx does not declare would show as nothing in the game,
    # and a new sprite needs a restart of the game (Engine Facts X27): better to stop here.
    declared = set(re.findall(r'name = "(GFX_1440p_\w+)"', io.open(os.path.join(ROOT, "interface", "1440p_ui.gfx"), encoding="utf-8").read()))
    missing = sorted(set(re.findall(r"GFX_1440p_\w+", "".join(c for rel, c in B.files.items() if rel.endswith(".gui")))) - declared)
    if missing:
        raise ValueError("not declared in interface/1440p_ui.gfx: " + ", ".join(missing))
    B.files.update(scene_files({rel: content for rel, content in B.files.items() if rel.endswith(".gui")}))
    # every name used after "@" and every text key held as "token:<key>" (Engine Facts X24, X37); "@var:x" is a variable
    tokens = sorted(set(re.findall(r"@(?!var:)([A-Za-z_][A-Za-z0-9_]*)", everything)) | set(re.findall(r"token:([A-Za-z_][A-Za-z0-9_]*)", everything)))
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
