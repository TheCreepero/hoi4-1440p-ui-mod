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


def text(name, x, y, width, key, font=FONT_LABEL, fmt="left", height=24, tooltip=None, fixed=False):
    """fixed: the box keeps its height, and a text that needs more lines is cut there instead of running into
    what stands below it (a name another mod makes longer)."""
    tip = ' pdx_tooltip = "%s"' % tooltip if tooltip else ""
    tip += " fixedsize = yes" if fixed else ""
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

# The kinds of land equipment: every archetype a land sub-unit asks for, with the sprite of its picture and that
# picture's size (tools/equipment_kinds_table.py, made from the game by tools/make_game_tables.py). A playset with
# a map of its own has a table of its own (tools/equipment_kinds_mods_table.py, made with --mods), and script counts
# the kinds of the table whose number of states the loaded game has (Engine Facts X72), the game's otherwise. The
# name of a kind is the game's own text for the archetype, so it follows the player's language.
from equipment_kinds_table import KINDS as AR_KINDS  # noqa: E402
try:
    from equipment_kinds_mods_table import MAPS as AR_MAPS  # noqa: E402
except ImportError:
    AR_MAPS = []
AR_TABLES = [(0, AR_KINDS)] + [(states, rows) for _mods, states, rows in AR_MAPS]
EQUIPMENT = [row[0] for row in AR_KINDS]        # the game's kinds (tools/check_playset.py compares the playset with them)

# The page: from the corner of the Recruit & Deploy panel (screen -6,78), beside the template panel, which ends at
# 1246. 975 wide: it stops short of the theatre box under the clock (screen x 2234). Two scripted GUIs one under the
# other: the head (title strip and figures), which is the whole page in its short form, and the body (equipment and
# armies); a group of widgets is hidden only as a scripted GUI of its own (Engine Facts X15).
AR_X, AR_Y, AR_W = 1256, 0, 975
AR_H = 1210                     # ends where the template panel ends, above the army portraits of the bottom bar
AR_HEAD = 60                    # height of the title strip
AR_SUM_H = 244                  # the head: title strip and the two cards of figures
AR_IN = AR_W - 28               # what a card has between the margins of the page
AR_CARD_W = (AR_IN - 12) // 2   # a card of figures: 467
AR_TILE, AR_STEP = 145, 151     # three tiles in a row of a card
AR_TABLE = AR_IN - 28           # a table inside a card: 919
AR_ROW_W = AR_TABLE - 30        # a row beside the scrollbar: 889
AR_EQ_ROW, AR_EQ_ROWS = 32, 9   # the equipment list: nine rows on the screen
AR_AL_ROW, AR_AL_ROWS = 50, 10  # the armies list: ten rows on the screen
AR_HQ = "GFX_1440p_SG_head_136"
ROW = 30                        # a row of a list
LOW = 75                        # a bar is orange below this many percent
# A picture of a kind stands in a box; the game's pictures are of many sizes, and an icon has one scale. So a row
# has one icon per scale, and script shows the one its kind needs: the largest scale at which the picture fits.
AR_SCALES = [1.0, 0.9, 0.8, 0.7, 0.6, 0.5, 0.4]
AR_PIC_BOX = (84, 30)           # in an equipment row
AR_WORST_BOX = (56, 24)         # the worst equipped kind in an army row

# The figures: manpower in one card, the army in the other. (name, label, value, tooltip, variable that
# decides between the value and a plain 0, or None)
AR_FIGURES = [
    ("Manpower", [
        ("mp_free", "Free manpower", "[?manpower_k|0]K", "Men you can still call up: the manpower of the top bar.", None),
        ("mp_training", "In training", "[?amount_manpower_in_deployment_queue|*1]",
         "Men of the divisions in training. Queue a division and this rises.", "amount_manpower_in_deployment_queue"),
        ("mp_garrison", "Garrisons need", "[?garrison_manpower_need|*1]", "Men the garrisons of your occupied states ask for.", "garrison_manpower_need"),
        ("mp_army", "In the army", "[?deployed_army_manpower_k|0]K", "Men of the divisions in the field.", None),
        ("mp_navy", "In the navy", "[?deployed_navy_manpower_k|0]K", "Men serving on your ships.", None),
        ("mp_air", "In the air force", "[?deployed_airforce_manpower_k|0]K", "Men serving in your air wings.", None),
    ]),
    ("Army", [
        ("divisions", "Divisions", "[?num_divisions|0]", "Divisions in the field.", None),
        ("battalions", "Battalions", "[?num_battalions|0]", "Battalions of the divisions in the field.", None),
        ("xp", "Army experience", "[?army_experience|0]", "Army experience to spend on templates and equipment.", None),
        ("low_str", "Under strength", "[?mod1440_ar_low_str|Y0]", "Divisions below 75% strength, as of the last count.", "mod1440_ar_low_str"),
        ("low_org", "Low organisation", "[?mod1440_ar_low_org|Y0]", "Divisions below 50% organisation, as of the last count.", "mod1440_ar_low_org"),
        ("fuel", "Fuel", None, None, None),     # a tile of its own: value and bar
    ]),
]


def ar_scale(width, height, box):
    """The index in AR_SCALES of the largest scale at which a picture fits its box."""
    fit = min(box[0] / float(width), box[1] / float(height), 1.0)
    for n, scale in enumerate(AR_SCALES):
        if scale <= fit + 0.001:
            return n
    return len(AR_SCALES) - 1


def ar_pictures(prefix, x, y, box, image):
    """One icon per scale in a box of a row, each shown by script for the kinds of its scale; the sprite is named
    by script (image). Each stands in the middle of the box's height for the pictures of its scale."""
    heights = {}
    for _states, rows in AR_TABLES:
        for _kind, _sprite, width, height in rows:
            heights.setdefault(ar_scale(width, height, box), []).append(height * AR_SCALES[ar_scale(width, height, box)])
    out, props = "", ""
    for n, scale in enumerate(AR_SCALES):
        seen = sorted(heights.get(n, [box[1]]))
        middle = seen[len(seen) // 2]
        out += scaled("%s_%d" % (prefix, n), x, y + int((box[1] - middle) // 2), "GFX_archetype_infantry_equipment_medium", scale)
        props += block("%s_%d" % (prefix, n), 'image = "%s"\n' % image)
    return out, props


def army_readiness():
    effects = ""
    triggers = ""
    properties = ""
    counted = more_than_zero("mod1440_ar_counted")
    folded = "check_variable = { mod1440_ar_folded = 1 }"
    small = "check_variable = { mod1440_ar_small = 1 }"

    # ---- the head: title strip, the date of the count and its button, the size, the fold
    head = box("ar_head", 3, 3, AR_W - 6, 50, "", "GFX_tiled_header")
    head += text("ar_title", 22, 8, 350, B.key("ar_title", "Army Readiness"), FONT_TITLE, height=40)
    head += text("ar_counted", 380, 20, 270, B.key("ar_counted", "Counted [?mod1440_ar_counted.GetDateStringNoHourLong]"), FONT_SMALL, "right", 20)
    triggers += block("ar_counted_visible", counted)
    head += button("ar_count", 662, 10, "GFX_button_123x34", B.key("ar_count", "Count again"), tooltip=B.key(
        "ar_count_tt", "Goes through every division and every kind of equipment once. The two counts of divisions, the fuel bar, the equipment and the armies are from the last time this ran: at the start of each day, and on this button."))
    effects += block("ar_count_click", "mod1440_ar_count = yes\n")
    head += button("ar_small", 795, 13, "GFX_sort_button_100x29", B.key("ar_small", "Summary"), tooltip=B.key(
        "ar_small_tt", "Fold the page to its figures: the map below them is free for picking a deploy location."))
    head += button("ar_full", 795, 13, "GFX_sort_button_100x29", B.key("ar_full", "Full"), tooltip=B.key(
        "ar_full_tt", "Show the equipment and the armies again."))
    effects += block("ar_small_click", setv("mod1440_ar_small", 1))
    effects += block("ar_full_click", setv("mod1440_ar_small", 0) + "mod1440_ar_count = yes\n")
    triggers += block("ar_small_visible", "NOT = { %s }\n" % small) + block("ar_full_visible", small + "\n")
    # the game writes the shortcut into the tooltip by itself (Engine Facts X8)
    head += button("ar_fold", AR_W - 66, 10, "GFX_closebutton", shortcut="shift+m",
                   tooltip=B.key("ar_fold_tt", "Hide this page and give the map back"))
    effects += block("ar_fold_click", setv("mod1440_ar_folded", 1))

    # ---- the figures: two cards of six tiles
    band_y = AR_HEAD + 6
    band_h = AR_SUM_H - band_y - 4
    for c, (title, figures) in enumerate(AR_FIGURES):
        inner = text("ar_card_%d_title" % c, 14, 7, AR_CARD_W - 28, B.key("ar_card_%d_title" % c, title), FONT_LABEL, height=24)
        for n, (name, label, value, tip, zero) in enumerate(figures):
            x, y = 11 + (n % 3) * AR_STEP, 34 + (n // 3) * (TILE_H + 6)
            if name == "fuel":
                tip = B.key("ar_fuel_tt", "Fuel in store, of the most you can store: the numbers of the top bar. The bar is their share as of the last count, orange below %d%%." % LOW)
                inner += icon("ar_fuel_bg", x, y, tile_sprite(AR_TILE))
                inner += text("ar_fuel_l", x + 6, y + 7, AR_TILE - 12, B.key("ar_fuel_l", label), FONT_SMALL, "centre", 20, tooltip=tip)
                inner += text("ar_fuel", x + 6, y + 26, AR_TILE - 12, B.key("ar_fuel", "[?fuel_k|0]K of [?max_fuel_k|0]K"), FONT_VALUE, "centre", 24, tooltip=tip)
                inner += icon("ar_fuel_bar", x + 14, y + 50, bar_sprite(AR_TILE - 28))
                inner += icon("ar_fuel_low", x + 14, y + 50, bar_sprite(AR_TILE - 28, low=True))
                low = "check_variable = { mod1440_ar_fuel < %d }\n" % LOW
                properties += block("ar_fuel_bar", "frame = mod1440_ar_fuel\n") + block("ar_fuel_low", "frame = mod1440_ar_fuel\n")
                triggers += block("ar_fuel_bar_visible", counted + "NOT = { %s }\n" % low.strip()) + block("ar_fuel_low_visible", counted + low)
                continue
            part, more = tile("ar_" + name, x, y, label, value, tip, width=AR_TILE, zero=zero)
            inner += part
            triggers += more
        head += box("ar_card_%d" % c, 14 + c * (AR_CARD_W + 12), band_y, AR_CARD_W, band_h, inner, CARD_BG)

    # ---- equipment: the kinds in use, worst equipped first, from the arrays of the last count
    body = ""
    c_stock, c_field, c_need, c_short, c_bar, c_pct = 400, 500, 600, 700, 722, 884      # right edges; the bar's left edge
    eq_h = 68 + AR_EQ_ROWS * AR_EQ_ROW + 8
    inner = text("ar_eq_caption", 300, 12, AR_IN - 300 - 14, B.key("ar_eq_caption", "§g[?mod1440_ar_fill^num|0] of [?mod1440_ar_kinds|0] kinds in use, the worst equipped first§!"),
                 FONT_SMALL, "right", 20, tooltip=B.key("ar_eq_caption_tt", "A kind is listed while you have some in stock or your divisions in the field need some. The numbers are from the last count."))
    inner += heads("ar_eq_heads", 14, 36, AR_TABLE, [
        (100, 200, "Kind", "left", None),
        (c_stock - 90, 90, "In stock", "right", "Equipment in the stockpile that no division and no training has taken: the number of the logistics tab, as of the last count."),
        (c_field - 90, 90, "In the field", "right", "Equipment in the hands of the divisions in the field. Red when it is less than they need."),
        (c_need - 90, 90, "Needed", "right", "What the templates of the divisions in the field ask for. Divisions in training are not counted."),
        (c_short - 86, 86, "Short", "right", "What the divisions in the field lack: needed less in the field. Red when the stock cannot fill it, orange when it can."),
        (c_bar, 150, "Equipped", "left", "In the field as a share of needed. Orange below %d%%." % LOW),
    ])
    inner += listing("ar_eq_list", "ar_eq_grid", 14, 68, AR_TABLE, AR_EQ_ROWS * AR_EQ_ROW, AR_EQ_ROW)
    inner += text("ar_eq_none", 28, 80, 700, B.key("ar_eq_none", "No kind of land equipment in stock or needed."), FONT_SMALL)
    triggers += block("ar_eq_none_visible", "check_variable = { mod1440_ar_fill^num < 1 }\n")
    body += card("ar_equipment", 14, 6, AR_IN, eq_h, "Equipment", inner)

    # A row of the list: the list's array holds the share of each kind (the bar's fill, "v"); the other values are
    # elements of the arrays beside it at the row's index ("i", Engine Facts X50).
    def at(array):
        return "mod1440_ar_%s^i" % array

    eq = icon("ar_er_stripe", 0, 0, STRIPE % (AR_ROW_W, AR_EQ_ROW))
    eq_triggers = block("ar_er_stripe_visible", "check_variable = { %s = 1 }\n" % at("odd"))
    pictures, more = ar_pictures("ar_er_pic", 8, 1, AR_PIC_BOX, "[?%s.GetTokenKey]" % at("pic"))
    eq += pictures
    properties += more
    eq_triggers += "".join(block("ar_er_pic_%d_visible" % n, "check_variable = { %s = %d }\n" % (at("cls"), n)) for n in range(len(AR_SCALES)))
    eq += text("ar_er_name", 100, 6, 200, B.key("ar_er_name", "[?%s.GetTokenLocalizedKey]" % at("kind")), FONT_LABEL, height=22, fixed=True)

    def cell(name, edge, width, value, font=FONT_VALUE, y=4):
        return text("ar_er_" + name, edge - width, y, width, B.key("ar_er_" + name, value), font, "right", 24)

    short = "check_variable = { %s > 0 }\n" % at("short")
    eq += cell("stock", c_stock, 90, "[?%s|0]" % at("stock"))
    eq += cell("field", c_field, 90, "[?%s|0]" % at("field")) + cell("field_short", c_field, 90, "[?%s|R0]" % at("field"))
    eq += cell("need", c_need, 90, "[?%s|0]" % at("need"))
    eq += cell("short", c_short, 86, "[?%s|R0]" % at("short")) + cell("short_covered", c_short, 86, "§O[?%s|0]§!" % at("short"))
    eq_triggers += block("ar_er_field_visible", "NOT = { %s }\n" % short.strip()) + block("ar_er_field_short_visible", short)
    eq_triggers += block("ar_er_short_visible", short + "check_variable = { %s = 1 }\n" % at("red"))
    eq_triggers += block("ar_er_short_covered_visible", short + "check_variable = { %s = 0 }\n" % at("red"))
    eq += icon("ar_er_bar", c_bar, 10, bar_sprite(110)) + icon("ar_er_low", c_bar, 10, bar_sprite(110, low=True))
    eq += cell("pct", c_pct, 50, "[?%s|0]%%" % at("fill"), FONT_LABEL, 6)
    needed = "check_variable = { %s > 0 }\n" % at("need")
    eq_triggers += block("ar_er_bar_visible", needed + "check_variable = { v > %d }\n" % (LOW - 1))
    eq_triggers += block("ar_er_low_visible", needed + "check_variable = { v < %d }\n" % LOW)
    eq_triggers += block("ar_er_pct_visible", needed)
    properties += block("ar_er_bar", "frame = v\n") + block("ar_er_low", "frame = v\n")
    triggers += eq_triggers

    # ---- armies: one row per general who has troops
    armies_y = 6 + eq_h + 10
    armies_h = AR_H - AR_SUM_H - armies_y - 14
    inner = text("ar_al_caption", 300, 12, AR_IN - 300 - 14, B.key("ar_al_caption", "§g[?mod1440_ar_leaders^num|0] commanders with troops; a click on HQ moves the camera there§!"),
                 FONT_SMALL, "right", 20)
    columns = [
        (10, 200, "Commander", "left", "A general or field marshal who commands troops, with his rank and skill. An army without a commander cannot be listed."),
        (250, 140, "HQ", "centre", "The state where the commander's headquarters is deployed, as of the last count. A click moves the camera there."),
        (394, 50, "Div", "centre", "Divisions under this commander."),
        (446, 40, "Inf", "centre", "Divisions that are mostly infantry."),
        (486, 40, "Arm", "centre", "Divisions that are mostly armour."),
        (526, 40, "Mot", "centre", "Divisions that are mostly motorised."),
        (566, 40, "Mech", "centre", "Divisions that are mostly mechanised."),
        (610, 80, "Fighting", "centre", "Divisions of this commander in combat now, and how many of them attack and defend."),
        (694, 84, "Planning", "centre", "The planning bonus the divisions have built up, as a share of the most they can have, as of the last count."),
        (782, 104, "Worst kind", "centre", "The worst equipped kind of equipment of this army, with what it has as a share of what its templates ask for, as of the last count. Orange below %d%%." % LOW),
    ]
    inner += heads("ar_al_heads", 14, 36, AR_TABLE, [(x, w, caption, fmt, tip) for x, w, caption, fmt, tip in columns])
    inner += listing("ar_al_list", "ar_al_grid", 14, 68, AR_TABLE, AR_AL_ROWS * AR_AL_ROW, AR_AL_ROW)
    inner += text("ar_al_none", 28, 84, 700, B.key("ar_al_none", "No army has a commander yet. An army is listed here once it has one."), FONT_SMALL)
    triggers += block("ar_al_none_visible", "check_variable = { mod1440_ar_leaders^num < 1 }\n")
    body += card("ar_armies", 14, armies_y, AR_IN, armies_h, "Armies", inner)

    # A row: the row's scope is the commander, and his variables are the values of the last count
    entry = icon("ar_row_stripe", 0, 0, STRIPE % (AR_ROW_W, AR_AL_ROW))
    row_triggers = block("ar_row_stripe_visible", is_one("mod1440_al_odd") + "\n")
    entry += scaled("ar_row_face", 6, 2, "GFX_portrait_unknown", 0.22) + scaled("ar_row_unknown", 6, 2, "GFX_portrait_unknown", 0.22)
    properties += block("ar_row_face", 'image = "[?mod1440_p.GetTokenKey]"\n')
    row_triggers += block("ar_row_face_visible", more_than_zero("mod1440_p_ver")) + block("ar_row_unknown_visible", "NOT = { %s }\n" % more_than_zero("mod1440_p_ver").strip())
    entry += text("ar_row_name", 48, 5, 200, B.key("ar_row_name", "§Y[THIS.GetName]§!"), FONT_LABEL, height=22, fixed=True)
    entry += text("ar_row_fm", 48, 27, 110, B.key("ar_rank_fm", "§gField Marshal§!"), FONT_SMALL, height=20)
    entry += text("ar_row_gen", 48, 27, 110, B.key("ar_rank_gen", "§gGeneral§!"), FONT_SMALL, height=20)
    row_triggers += block("ar_row_fm_visible", "is_field_marshal = yes\n") + block("ar_row_gen_visible", "NOT = { is_field_marshal = yes }\n")
    entry += text("ar_row_skill", 160, 27, 80, B.key("ar_row_skill", "§gSkill§! [?skill_level|0]"), FONT_SMALL, height=20)
    # HQ: the state of his deployed headquarters, a button that moves the camera there
    hq = more_than_zero("mod1440_al_hq")
    entry += button("ar_row_hq", 252, 10, AR_HQ, tooltip=B.key("ar_row_hq_tt", "Show the headquarters on the map"))
    entry += scaled("ar_row_hq_icon", 256, 13, "GFX_countryaction_gotolocation_big", 0.75)
    entry += plain("ar_row_hq_name", 282, 16, 104, B.key("ar_row_hq_name", "[?mod1440_al_hq.GetName]"), FONT_SMALL, "centre", 20)
    entry += text("ar_row_hq_none", 250, 16, 140, B.key("ar_row_hq_none", "§gnot deployed§!"), FONT_SMALL, "centre", 20)
    row_triggers += "".join(block("%s_visible" % name, hq) for name in ("ar_row_hq", "ar_row_hq_icon", "ar_row_hq_name"))
    row_triggers += block("ar_row_hq_none_visible", "NOT = { %s }\n" % hq.strip())
    effects += block("ar_row_hq_click", tmp("ar_hq", "mod1440_al_hq") + block("var:ar_hq", block("ROOT", "goto_state = PREV\n")))
    entry += text("ar_row_div", 394, 13, 50, B.key("ar_row_div", "[?num_units|0]"), FONT_VALUE, "centre", 24)
    for k, (name, variable) in enumerate((("inf", "num_infantry"), ("arm", "num_armored"), ("mot", "num_motorized"), ("mech", "num_mechanized"))):
        entry += text("ar_row_%s" % name, 446 + k * 40, 15, 40, B.key("ar_row_%s" % name, "[?%s|0]" % variable), FONT_LABEL, "centre", 22)
        entry += text("ar_row_%s_none" % name, 446 + k * 40, 15, 40, B.key("ar_row_dash", "§g-§!"), FONT_LABEL, "centre", 22)
        row_triggers += block("ar_row_%s_visible" % name, more_than_zero(variable))
        row_triggers += block("ar_row_%s_none_visible" % name, "NOT = { %s }\n" % more_than_zero(variable).strip())
    fighting = more_than_zero("num_units_in_combat")
    entry += text("ar_row_fight", 610, 4, 80, B.key("ar_row_fight", "§Y[?num_units_in_combat|0]§!"), FONT_VALUE, "centre", 24)
    entry += text("ar_row_split", 610, 27, 80, B.key("ar_row_split", "§g[?num_units_offensive_combats|0] att, [?num_units_defensive_combats|0] def§!"), FONT_SMALL, "centre", 20)
    entry += text("ar_row_fight_none", 610, 15, 80, B.key("ar_row_dash", "§g-§!"), FONT_LABEL, "centre", 22)
    row_triggers += block("ar_row_fight_visible", fighting) + block("ar_row_split_visible", fighting)
    row_triggers += block("ar_row_fight_none_visible", "NOT = { %s }\n" % fighting.strip())
    entry += text("ar_row_plan", 694, 6, 84, B.key("ar_row_plan", "[?mod1440_al_plan|0]%"), FONT_LABEL, "centre", 22)
    entry += icon("ar_row_plan_bar", 702, 30, bar_sprite(68))
    properties += block("ar_row_plan_bar", "frame = mod1440_al_plan\n")
    # the worst equipped kind: its picture, its share and a bar
    worst = "check_variable = { mod1440_al_wk = 1 }\n"
    pictures, more = ar_pictures("ar_row_worst", 782, 3, AR_WORST_BOX, "[?mod1440_al_wpic.GetTokenKey]")
    entry += pictures
    properties += more
    row_triggers += "".join(block("ar_row_worst_%d_visible" % n, worst + "check_variable = { mod1440_al_wcls = %d }\n" % n) for n in range(len(AR_SCALES)))
    low = "check_variable = { mod1440_al_fill < %d }\n" % LOW
    entry += text("ar_row_pct", 838, 6, 46, B.key("ar_row_pct", "[?mod1440_al_fill|0]%"), FONT_LABEL, "right", 22)
    entry += icon("ar_row_bar", 786, 30, bar_sprite(98)) + icon("ar_row_low", 786, 30, bar_sprite(98, low=True))
    properties += block("ar_row_bar", "frame = mod1440_al_fill\n") + block("ar_row_low", "frame = mod1440_al_fill\n")
    row_triggers += block("ar_row_pct_visible", worst) + block("ar_row_bar_visible", worst + "NOT = { %s }\n" % low.strip())
    row_triggers += block("ar_row_low_visible", worst + low)
    triggers += row_triggers

    gui = box("mod1440_army_readiness", AR_X, AR_Y, AR_W, AR_SUM_H, head, PAGE_BG)
    gui += box("mod1440_army_readiness_body", AR_X, AR_Y + AR_SUM_H, AR_W, AR_H - AR_SUM_H, body, PAGE_BG)
    gui += row("mod1440_army_readiness_eqrow", AR_ROW_W, AR_EQ_ROW, eq)
    gui += row("mod1440_army_readiness_row", AR_ROW_W, AR_AL_ROW, entry)

    # ---- the handle that brings a hidden page back, in the form it was left in
    handle = button("ar_unfold", 0, 0, "GFX_button_148x34", B.key("ar_unfold", "Army Readiness"), shortcut="shift+m",
                    tooltip=B.key("ar_unfold_tt", "Show the Army Readiness page"))
    gui += box("mod1440_army_readiness_handle", AR_X, 8, 148, 34, handle)

    # Each scripted GUI takes the effects, triggers and properties of the widgets in its own window and rows.
    def mine(part, names):
        out = ""
        for m in re.finditer(r"^(\w+) = \{\n(?:\t[^\n]*\n)*?\}\n", part, re.M):
            widget = re.sub(r"_(click|visible)$", "", m.group(1))
            if widget in names:
                out += m.group(0)
        return out

    head_names = set(re.findall(r'name = "(\w+)"', head))
    body_names = set(re.findall(r'name = "(\w+)"', body + eq + entry))
    script = scripted_gui(
        "mod1440_army_readiness", "mod1440_army_readiness", "deployment_tab",
        visible="NOT = { %s }\n" % folded,
        effects=mine(effects, head_names), triggers=mine(triggers, head_names), properties=mine(properties, head_names))
    script += "\n" + scripted_gui(
        "mod1440_army_readiness_body", "mod1440_army_readiness_body", "deployment_tab",
        visible="NOT = { %s }\nNOT = { %s }\n" % (folded, small),
        lists=(block("ar_eq_grid", 'array = mod1440_ar_fill\nentry_container = "mod1440_army_readiness_eqrow"\n')
               + block("ar_al_grid", 'array = mod1440_ar_leaders\nchange_scope = yes\nentry_container = "mod1440_army_readiness_row"\n')),
        effects=mine(effects, body_names), triggers=mine(triggers, body_names), properties=mine(properties, body_names))
    script += "\n" + scripted_gui(
        "mod1440_army_readiness_handle", "mod1440_army_readiness_handle", "deployment_tab",
        visible=folded + "\n",
        effects=block("ar_unfold_click", setv("mod1440_ar_folded", 0) + "mod1440_ar_count = yes\n"))
    return gui, script, ar_count()


# The arrays of the equipment list, one element per kind in use, in the order of the list: the text key of the
# kind, the sprite of its picture as a text key, the scale of the picture, stock, in the field, needed, short, the
# share, whether the stock falls short of the gap (red) and the band of every second row.
AR_ARRAYS = ["kind", "pic", "cls", "stock", "field", "need", "short", "fill", "red", "odd"]


def ar_count():
    """The scripted effects of the counting: mod1440_ar_count and the effects of each table of kinds."""
    from_portraits = portrait_version()
    tables = ""
    for m, (states, rows) in enumerate(AR_TABLES):
        kinds = ""
        for kind, sprite, width, height in rows:
            kinds += (tmp("ar_s", "num_equipment@" + kind) + tmp("ar_d", "num_target_equipment_in_armies@" + kind)
                      + iff("OR = { check_variable = { ar_s > 0 } check_variable = { ar_d > 0 } }", (
                          tmp("ar_f", "num_equipment_in_armies@" + kind) + tmp("ar_tok", "token:" + kind)
                          + tmp("ar_pic", "token:" + sprite) + tmp("ar_cls", ar_scale(width, height, AR_PIC_BOX))
                          + "mod1440_ar_add = yes\n")))
        worst = ""
        for kind, sprite, width, height in rows:
            worst += iff("check_variable = { num_target_equipment@%s > 0 }" % kind, (
                tmp("al_share", "num_equipment@" + kind) + "divide_temp_variable = { al_share = num_target_equipment@%s }\n" % kind
                + "multiply_temp_variable = { al_share = 100 }\n"
                + iff("check_variable = { al_share < mod1440_al_fill }", (
                    setv("mod1440_al_fill", "al_share") + setv("mod1440_al_wk", 1)
                    + setv("mod1440_al_wpic", "token:" + sprite) + setv("mod1440_al_wcls", ar_scale(width, height, AR_WORST_BOX))))))
        source = "the game's own kinds" if not states else "the kinds of a playset with %d states" % states
        tables += ("\n# Army Readiness: %s (%d), for the country in scope.\n" % (source, len(rows))
                   + block("mod1440_ar_kinds_%d" % m, setv("mod1440_ar_kinds", len(rows)) + kinds)
                   + "\n# Army Readiness: the worst equipped kind of %s, in the scope of a general.\n" % source
                   + block("mod1440_ar_worst_%d" % m, worst))

    def pick(effect):
        """The effect of the table of the loaded map (the temporary ar_map); the game's own otherwise."""
        if len(AR_TABLES) == 1:
            return "%s_0 = yes\n" % effect
        out = ""
        for m in range(1, len(AR_TABLES)):
            out += iff("check_variable = { ar_map = %d }" % m, "%s_%d = yes\n" % (effect, m), "if" if m == 1 else "else_if")
        return out + els("%s_0 = yes\n" % effect)

    states = tmp("ar_map", 0)
    if len(AR_TABLES) > 1:
        # the map does not change in a game: its states are counted once per country
        states += iff("check_variable = { mod1440_ar_states = 0 }", tmp("ar_n", 0) + block("every_state", "add_to_temp_variable = { ar_n = 1 }\n")
                      + setv("mod1440_ar_states", "ar_n"))
        states += "".join(iff("check_variable = { mod1440_ar_states = %d }" % n, tmp("ar_map", m)) for m, (n, _rows) in enumerate(AR_TABLES) if m)

    # A kind in use: its values into the arrays the list is sorted from. A share is worked out as have / need * 100,
    # dividing first: the product of a large stock and 100 is more than a script number is sure to hold.
    add = (tmp("ar_fill", 0) + tmp("ar_short", 0) + tmp("ar_red", 0) + tmp("ar_key", 0)
           + iff("check_variable = { ar_d > 0 }", (
                        tmp("ar_fill", "ar_f") + "divide_temp_variable = { ar_fill = ar_d }\nmultiply_temp_variable = { ar_fill = 100 }\n"
                        + iff("check_variable = { ar_fill > 100 }", tmp("ar_fill", 100))
                        + tmp("ar_short", "ar_d") + "subtract_from_temp_variable = { ar_short = ar_f }\n"
                        + iff("check_variable = { ar_short < 0 }", tmp("ar_short", 0))
                        # A text cuts the fraction of a number off, and equipment in the field has one: the gap is
                        # rounded up, so that it is what "Needed" less "In the field" gives on the page (X65).
                        + tmp("ar_whole", "ar_short") + "round_temp_variable = ar_whole\n"
                        + iff("check_variable = { var = ar_whole value = ar_short compare = less_than }", "add_to_temp_variable = { ar_whole = 1 }\n")
                        + tmp("ar_short", "ar_whole")
                        + iff("check_variable = { ar_short > 0 } check_variable = { var = ar_s value = ar_short compare = less_than }", tmp("ar_red", 1))
                        # the sort key: the worse equipped, the higher; a kind only in stock comes after them all
                        + tmp("ar_key", 200) + "subtract_from_temp_variable = { ar_key = ar_fill }\n"))
           + "".join("add_to_array = { mod1440_ar_u_%s = ar_%s }\n" % (a, v) for a, v in (
               ("kind", "tok"), ("pic", "pic"), ("cls", "cls"), ("stock", "s"), ("field", "f"), ("need", "d"),
               ("short", "short"), ("fill", "fill"), ("red", "red"), ("key", "key"))))
    sort = ("".join("clear_array = mod1440_ar_%s\n" % a for a in AR_ARRAYS) + tmp("ar_par", 0)
            + block("for_loop_effect", "start = 0\nend = mod1440_ar_u_key^num\nvalue = ar_step\n"
                    + block("find_highest_in_array", "array = mod1440_ar_u_key\nvalue = ar_high\nindex = ar_at\n")
                    + "".join("add_to_array = { mod1440_ar_%s = mod1440_ar_u_%s^ar_at }\n" % (a, a) for a in AR_ARRAYS if a != "odd")
                    + "add_to_array = { mod1440_ar_odd = ar_par }\n" + iff("check_variable = { ar_par = 0 }", tmp("ar_par", 1)) + els(tmp("ar_par", 0))
                    + setv("mod1440_ar_u_key^ar_at", -1)))
    unsorted = "".join("clear_array = mod1440_ar_u_%s\n" % a for a in AR_ARRAYS if a != "odd") + "clear_array = mod1440_ar_u_key\n"

    # The fuel bar, the share of what can be stored
    fuel = setv("mod1440_ar_fuel", 0) + iff("check_variable = { max_fuel_k > 0 }", (
        setv("mod1440_ar_fuel", "fuel_k") + "divide_variable = { mod1440_ar_fuel = max_fuel_k }\nmultiply_variable = { mod1440_ar_fuel = 100 }\n"
        + "clamp_variable = { var = mod1440_ar_fuel min = 0 max = 100 }\n"))

    # The game's own loop over the leaders: its array army_leaders holds nothing in the place of a general whose
    # command came by an effect, and neither does THIS. mod1440_of_me gives what a variable can hold of him
    # (tools/build_records.py, places()). Every second commander of the list gets the darker band.
    general = (setv("mod1440_al_fill", 101) + setv("mod1440_al_wk", 0) + pick("mod1440_ar_worst")
               + iff("check_variable = { mod1440_al_fill > 100 }", setv("mod1440_al_fill", 100))
               + setv("mod1440_al_hq", "state_deployed")
               + setv("mod1440_al_plan", "avg_unit_planning_ratio") + "multiply_variable = { mod1440_al_plan = 100 }\n"
               + "clamp_variable = { var = mod1440_al_plan min = 0 max = 100 }\n"
               # the portrait, once per table of portraits and again when the numbers of text keys have moved
               # (build_records.kept_tokens()), for a player's country only: the lookup is long
               + iff("check_variable = { ar_player = 1 } " + build_records.portrait_stale(from_portraits), "mod1440_p_officer = yes\n")
               + setv("mod1440_al_odd", "al_odd") + iff("check_variable = { al_odd = 0 }", tmp("al_odd", 1)) + els(tmp("al_odd", 0))
               + "add_to_array = { PREV.mod1440_ar_leaders = of_me }\n")
    # a player's record first learns whether the numbers of text keys have moved since the save was made: the
    # portraits looked up before are stale then (fix round 1; this runs before the Records' daily round)
    leaders = (iff("check_variable = { ar_player = 1 } check_variable = { mod1440_ev_begun = 1 }", "mod1440_tk_check = yes\n")
               + "mod1440_of_refs = yes\nclear_array = mod1440_ar_leaders\n" + tmp("al_odd", 0) + block("every_army_leader", (
        "limit = { check_variable = { num_units > 0 } }\nmod1440_of_me = yes\n"
        + iff("NOT = { check_variable = { of_me = 0 } }", general))))
    count = (
        "# Army Readiness: the two division counts, the fuel bar, the kinds of equipment in use worst equipped first\n"
        "# and the list of generals with troops, for the country in scope. Runs at the start of a game for every\n"
        "# country, each day for a player, and on a click.\n"
        + block("mod1440_ar_count",
                tmp("ar_player", 0) + iff("is_ai = no", tmp("ar_player", 1))
                + "set_variable = { mod1440_ar_low_str = 0 }\nset_variable = { mod1440_ar_low_org = 0 }\n"
                + block("every_country_division", "limit = { unit_strength < 0.75 }\nadd_to_variable = { PREV.mod1440_ar_low_str = 1 }\n")
                + block("every_country_division", "limit = { unit_organization < 0.5 }\nadd_to_variable = { PREV.mod1440_ar_low_org = 1 }\n")
                + fuel + states + unsorted + pick("mod1440_ar_kinds") + sort + leaders
                + "set_variable = { mod1440_ar_counted = global.date }\n")
        + "\n# Army Readiness: a kind in use, from ar_s (stock), ar_f (in the field), ar_d (needed), ar_tok, ar_pic, ar_cls.\n"
        + block("mod1440_ar_add", add)
        + tables)
    return count


def portrait_version():
    """The version of the table of portraits, which the Officers page uses too (tools/build_records.py): an
    officer whose portrait was looked up in another table is looked up again."""
    build_records.M, build_records.B = sys.modules[__name__], B
    return build_records.portraits()[1]


# ---------------------------------------------------------------- States (D3), docked to Construction

# One row per state the player controls, in a table card, and under it a band of four cards for the chosen
# state (redesign of 2026-10-16, scratch/redesign/d3-states). A column is (name, value of the state, width,
# head, tip, group): the head is ("text", caption), ("building", frame of GFX_buildings_strip) or ("resource",
# frame of GFX_resources_strip); the tip is a text of the game ("$key$") or of the mod; columns of one group
# stand together, with a gap to the next group. A resource is shown as the list effect's rounded copy of the
# state's number: "|0" cuts a fraction off and the state view rounds (Engine Facts X65).
STATE_COLUMNS = [
    ("free", "mod1440_st_free", 100, ("text", "Free"), "Free building slots for factories and the other buildings that share slots, counted when the list was made. The bar is the share of the slots that shared buildings already take; it counts the game's own shared buildings only, so a building another mod adds is not in it (the free number is the game's own).", "free"),
    ("infra", "infrastructure_level", 52, ("building", 3), "Infrastructure.", "build"),
    ("civ", "industrial_complex_level", 52, ("building", 1), "Civilian factories.", "build"),
    ("mil", "arms_factory_level", 52, ("building", 2), "Military factories.", "build"),
    ("dock", "building_level@dockyard", 52, ("building", 4), "Naval dockyards.", "build"),
    ("refinery", "building_level@synthetic_refinery", 52, ("building", 10), "Synthetic refineries.", "build"),
    ("silo", "building_level@fuel_silo", 52, ("building", 14), "Fuel silos.", "build"),
    ("air", "building_level@air_base", 52, ("building", 5), "Air base.", "build"),
    ("aa", "building_level@anti_air_building", 52, ("building", 9), "Anti-air.", "build"),
    ("radar", "building_level@radar_station", 52, ("building", 11), "Radar station.", "build"),
    ("oil", "mod1440_st_r_oil", 56, ("resource", 1), "Oil.", "res"),
    ("aluminium", "mod1440_st_r_aluminium", 56, ("resource", 2), "Aluminium.", "res"),
    ("rubber", "mod1440_st_r_rubber", 56, ("resource", 3), "Rubber.", "res"),
    ("tungsten", "mod1440_st_r_tungsten", 56, ("resource", 4), "Tungsten.", "res"),
    ("steel", "mod1440_st_r_steel", 56, ("resource", 5), "Steel.", "res"),
    ("chromium", "mod1440_st_r_chromium", 56, ("resource", 6), "Chromium.", "res"),
    ("coal", "mod1440_st_r_coal", 56, ("resource", 7), "Coal.", "res"),
    ("pop", "state_population_k", 84, ("text", "People"), "Population of the state, in thousands.", "people"),
    ("compliance", "compliance", 60, ("text", "Compl."), "Compliance, for a state that is not a core of yours.", "occ"),
    ("resistance", "resistance", 60, ("text", "Resist."), "Resistance, for a state that is not a core of yours.", "occ"),
]
STATE_GROUPS = [("free", "Slots"), ("build", "Buildings"), ("res", "Resources"), ("occ", "Occupation")]
HEAD_SPRITES = {52: "GFX_1440p_SG_head_52", 56: "GFX_1440p_SG_head_56", 60: "GFX_1440p_SG_head_60",
                84: "GFX_1440p_SG_head_84", 100: "GFX_1440p_SG_head_100", 200: "GFX_1440p_SG_head_200",
                240: "GFX_1440p_SG_head_240", 300: "GFX_1440p_SG_head_300"}
# The game's name of each building column, for damaged_building_level@ (the three with a variable of their own)
ST_BUILDING = {"infra": "infrastructure", "civ": "industrial_complex", "mil": "arms_factory", "dock": "dockyard",
               "refinery": "synthetic_refinery", "silo": "fuel_silo", "air": "air_base", "aa": "anti_air_building",
               "radar": "radar_station"}
# The game's buildings that take a shared slot (shares_slots = yes in common/buildings): the five the slots card
# names with their icon, and the others, counted together. A building another mod adds is not counted (rule 6).
ST_SHARED = [("civ", "industrial_complex", 1), ("mil", "arms_factory", 2), ("dock", "dockyard", 4),
             ("refinery", "synthetic_refinery", 10), ("silo", "fuel_silo", 14)]
ST_SHARED_OTHER = ["rocket_site", "nuclear_reactor", "nuclear_reactor_heavy_water", "commercial_nuclear_reactor",
                   "energy_infrastructure", "industrial_infrastructure", "mega_gun_emplacement", "stronghold_network"]
# The game's state categories (common/state_category); their names are text keys of the game
ST_CATEGORIES = ["megalopolis", "metropolis", "large_city", "city", "large_town", "town", "rural", "pastoral",
                 "wasteland", "enclave", "large_island", "small_island", "tiny_island"]
ST_RESOURCES = ["oil", "aluminium", "rubber", "tungsten", "steel", "chromium", "coal"]

# From the corner of the construction panel (screen -9,78), whose building column ends at x 700.
ST_X, ST_Y = 712, 0
ST_NAME = 200
ST_GAP = 10                     # between the groups of columns
ST_FREE_BAR = 62                # the slot bar takes the first 62 px of the free column (6 margin, 56 bar)


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
ST_ROW = 30
ST_ROWS = 26                                                # rows on the screen: Germany's 24 fit
# The cards stand 7 px inside the page: the rows and their scrollbar take the page's width less 14 a side,
# which is where the rows stood before the cards (the page keeps its place and width).
ST_CARD_X = 7
ST_CARD_W = ST_W - 2 * ST_CARD_X
ST_TABLE_Y = 62
# The captions stand 27 px above the heads, clear of the arrow of the sorted column, which reaches 9 px above
# its head: in the game a caption 22 px above ran into it (check of 2026-10-13).
ST_CAPTION_Y, ST_HEAD_Y = ST_TABLE_Y + 4, ST_TABLE_Y + 31
ST_LIST_Y = ST_HEAD_Y + 34
ST_LIST_H = ST_ROWS * ST_ROW
ST_TOTAL_Y = ST_LIST_Y + ST_LIST_H + 6
ST_TABLE_H = ST_TOTAL_Y + ST_ROW + 9 - ST_TABLE_Y
ST_BAND_Y = ST_TABLE_Y + ST_TABLE_H + 12
ST_BAND_H = ST_H - 14 - ST_BAND_Y
# the four cards of the band: the state, its building slots, its buildings, occupation
ST_CARDS = [("state", None, 430), ("slots", "Building Slots", 300), ("build", "Buildings", 404)]
ST_CARDS.append(("occ", "Occupation", ST_CARD_W - sum(w for n, t, w in ST_CARDS) - 3 * 12))
ST_CARD_AT = {}
_x = 0
for _name, _title, _w in ST_CARDS:
    ST_CARD_AT[_name] = (_x, _w)
    _x += _w + 12
ST_CHIP_W = 96                  # four chips side by side in the card of the state
ST_SAMPLES = {                  # what the renderer writes for the values of the band (tools/scenes/states.json)
    "THIS.GetName": "Hessen", "THIS.GetCapitalVictoryPointName": "Frankfurt", "?mod1440_st_cat.GetTokenLocalizedKey": "Dense Urban Region",
    "THIS.Owner.GetNameDef": "the German Reich", "?mod1440_sr_from.GetNameWithFlag": "Poland", "?mod1440_sr_date.GetDateStringNoHourLong": "27 September, 1939",
    "?mod1440_st_free|G0": "§G6§!", "?mod1440_st_slots|0": "9", "?mod1440_st_used_n|0": "3", "?mod1440_st_used_other|0": "1",
    "?mod1440_st_dmg|0": "3", "?days_since_last_strategic_bombing|0": "4", "?state_population_k|0": "3802",
    "?compliance|1": "8.4", "?compliance_speed|+=2": "+0.12", "?resistance|1": "31.6", "?resistance_speed|-=2": "-0.05",
    "?resistance_target|1": "40.0", "?mod1440_st_r_coal|0": "16",
}


def st_sample(window, inside):
    """A sample for a value of the States page, or None for the shared rules of sample_for."""
    if window == "mod1440_states_row" and inside.startswith("?mod1440_st_r_"):
        return "250"
    if window == "mod1440_states_card" or window == "mod1440_states" and inside.startswith("?modifier@"):
        if inside in ST_SAMPLES:
            return ST_SAMPLES[inside]
        if inside.startswith("?damaged_building_level"):
            return "2"
        if inside.startswith("?modifier@"):
            return {"compliance_growth": "-2.0%", "resistance_target": "+5.0%"}.get(inside.split("@")[1].split("|")[0], "+5.0%")
        if inside.startswith("?mod1440_st_r_"):
            return "0"
        if inside.startswith(("?infrastructure", "?industrial", "?arms_factory", "?building_level")):
            return {"?infrastructure_level|0": "4", "?industrial_complex_level|0": "2", "?arms_factory_level|0": "1"}.get(inside, "0")
    return None


def free_slot_tree(low, high):
    """Script that finds how many shared building slots are free in the state in scope, between low and high.
    The trigger takes a written number only (Engine Facts X20), so the search is written out: five questions."""
    if low == high:
        return "set_variable = { mod1440_st_free = %d }\n" % low
    middle = (low + high) // 2
    question = block("free_building_slots", "building = industrial_complex\nsize > %d\ninclude_locked = no\n" % middle)
    return block("if", block("limit", question) + free_slot_tree(middle + 1, high)) + block("else", free_slot_tree(low, middle))


def strip(name, x, y, sprite, frame, scale):
    """A frame of a strip of icons (buildings, resources), which lets a click through."""
    return ('iconType = { name = "%s" position = { x = %d y = %d } spriteType = "%s" frame = %d scale = %s '
            'alwaystransparent = yes }\n' % (name, x, y, sprite, frame, scale))


def states_band():
    """The band under the table: four cards for the chosen state. The cards and what belongs to the country
    stand in the page; what belongs to the state is a list of one row (the array mod1440_st_card holds the
    chosen state), so that its texts and triggers run in the state's scope (Engine Facts X10, X36, X39).
    Returns the page's widgets, the row, the triggers of each and the effects."""
    page, entry, triggers, row_triggers, effects, properties = "", "", "", "", "", ""
    for name, title, width in ST_CARDS:
        x, w = ST_CARD_AT[name]
        inner = text("st_band_%s_title" % name, 14, 8, w - 28, B.key("st_band_%s_title" % name, title), FONT_CARD, height=30) if title else ""
        page += box("st_band_%s" % name, ST_CARD_X + x, ST_BAND_Y, w, ST_BAND_H, inner, CARD_BG)
    page += text("st_c_none", ST_CARD_X + 14, ST_BAND_Y + 14, 400, B.key("st_c_none", "No state is listed. Choose All in the title strip."), FONT_LABEL)
    triggers += block("st_c_none_visible", "check_variable = { mod1440_st_rows^num < 1 }\n")

    owned, core = "is_owned_by = ROOT\n", "is_core_of = ROOT\n"
    noncore = "NOT = { is_core_of = ROOT }\n"

    # ---- the state: flag, name, capital and category, owner, the War Diary's record, chips, resources, people
    x0 = ST_CARD_AT["state"][0]
    entry += icon("st_c_flag", x0 + 14, 12, "GFX_flag_small2")
    properties += block("st_c_flag", 'image = "[THIS.Owner.GetFlag]"\n')
    entry += text("st_c_name", x0 + 66, 10, 350, B.key("st_c_name", "[THIS.GetName]"), FONT_CARD, height=30, fixed=True)
    entry += text("st_c_where", x0 + 66, 42, 350, B.key("st_c_where", "Capital [THIS.GetCapitalVictoryPointName]  ·  [?mod1440_st_cat.GetTokenLocalizedKey]"), FONT_SMALL, height=20, fixed=True)
    entry += text("st_c_where_cap", x0 + 66, 42, 350, B.key("st_c_where_cap", "Capital [THIS.GetCapitalVictoryPointName]"), FONT_SMALL, height=20, fixed=True)
    row_triggers += block("st_c_where_visible", "NOT = { check_variable = { mod1440_st_cat = 0 } }\n")
    row_triggers += block("st_c_where_cap_visible", "check_variable = { mod1440_st_cat = 0 }\n")
    for name, value, condition in (
            ("core", "Core of §Y[THIS.Owner.GetNameDef]§!", owned + core),
            ("owned", "Owned by §Y[THIS.Owner.GetNameDef]§!, not a core", owned + noncore),
            ("held", "Owned by §Y[THIS.Owner.GetNameDef]§!, held by you", "NOT = { is_owned_by = ROOT }\n")):
        entry += text("st_c_owner_%s" % name, x0 + 14, 70, 402, B.key("st_c_owner_%s" % name, value), FONT_SMALL, height=20, fixed=True)
        row_triggers += block("st_c_owner_%s_visible" % name, condition)
    # the record E1 keeps on a state (tools/build_records.py): every state carries a country once the Records
    # have begun, so the text never names a variable that is not there (Engine Facts X73)
    entry += text("st_c_taken", x0 + 14, 94, 402, B.key("st_c_taken", "Taken from §Y[?mod1440_sr_from.GetNameWithFlag]§! on [?mod1440_sr_date.GetDateStringNoHourLong]"), FONT_SMALL, height=20, fixed=True)
    entry += text("st_c_untaken", x0 + 14, 94, 402, B.key("st_c_untaken", "§gIn your hands since before the record began.§!"), FONT_SMALL, height=20)
    row_triggers += block("st_c_taken_visible", "check_variable = { mod1440_sr_day > 0 }\n")
    row_triggers += block("st_c_untaken_visible", "NOT = { check_variable = { mod1440_sr_day > 0 } }\n")
    # chips: four places, each with the first of its labels that applies
    chips = [
        [("core", "§GCore§!", owned + core), ("noncore", "Not a core", owned + noncore), ("occupied", "§YOccupied§!", "NOT = { is_owned_by = ROOT }\n")],
        [("coastal", "Coastal", "is_coastal = yes\n"), ("inland", "§gInland§!", "is_coastal = no\n")],
        [("capital", "§YCapital§!", "is_capital = yes\n")],
        [("island", "Island", "is_island_state = yes\n"), ("dmz", "§RDemilitarised§!", "is_island_state = no\nis_demilitarized_zone = yes\n"),
         ("border", "§RBorder war§!", "is_island_state = no\nis_demilitarized_zone = no\nhas_border_war = yes\n")],
    ]
    for place, options in enumerate(chips):
        for name, label, condition in options:
            entry += box("st_c_chip_%s" % name, x0 + 14 + place * (ST_CHIP_W + 6), 120, ST_CHIP_W, 26,
                         text("st_c_chip_%s_t" % name, 0, 4, ST_CHIP_W, B.key("st_c_chip_%s" % name, label), FONT_SMALL, "centre", 20),
                         HEAD_SPRITES[240])
            row_triggers += block("st_c_chip_%s_visible" % name, condition)
    for n, resource in enumerate(ST_RESOURCES):
        rx = x0 + 14 + n * 57
        entry += strip("st_c_res_icon_%d" % n, rx, 156, "GFX_resources_strip", n + 1, 0.9)
        variable = "mod1440_st_r_" + resource
        entry += text("st_c_res_%d" % n, rx + 26, 157, 30, B.key("st_c_res_%d" % n, "[?%s|0]" % variable), FONT_LABEL, height=22)
        entry += text("st_c_res_%d_z" % n, rx + 26, 157, 30, B.key("st_c_res_z", "§g-§!"), FONT_LABEL, height=22)
        row_triggers += block("st_c_res_%d_visible" % n, more_than_zero(variable))
        row_triggers += block("st_c_res_%d_z_visible" % n, "NOT = { %s }\n" % more_than_zero(variable).strip())
    entry += text("st_c_people_l", x0 + 14, 194, 80, B.key("st_c_people_l", "People"), FONT_SMALL, height=20)
    entry += text("st_c_people", x0 + 80, 192, 160, B.key("st_c_people", "[?state_population_k|0]K"), FONT_LABEL, height=22)
    entry += button("st_c_goto", x0 + ST_CARD_AT["state"][1] - 162, ST_BAND_H - 46, "GFX_button_148x34", B.key("st_c_goto", "Show on map"),
                    tooltip=B.key("st_c_goto_tt", "Moves the camera to this state and hides the page"))
    effects += block("st_c_goto_click", block("ROOT", "goto_state = PREV\nset_variable = { mod1440_st_open = 0 }\nadd_to_variable = { mod1440_st_dirty = 1 }\n"))

    # ---- building slots: the free count, a bar of the used share, the shared buildings by icon
    x0, w = ST_CARD_AT["slots"]
    entry += text("st_c_free", x0 + 14, 44, 60, B.key("st_c_free", "[?mod1440_st_free|G0]"), FONT_TITLE, height=40)
    entry += text("st_c_of", x0 + 74, 58, w - 88, B.key("st_c_of", "free of [?mod1440_st_slots|0]"), FONT_LABEL, height=22)
    tip = B.key("st_c_bar_tt", "Shared slots in use: the shared buildings over the free slots and the shared buildings. Only the game's own shared buildings are counted; a building another mod adds is not, so with such a mod the bar is short. The free number is the game's own.")
    entry += scaled("st_c_bar", x0 + 14, 98, bar_sprite(w - 28), 1, tooltip=tip)
    properties += block("st_c_bar", "frame = mod1440_st_used\n")
    entry += text("st_c_used", x0 + 14, 120, w - 28, B.key("st_c_used", "[?mod1440_st_used_n|0] used by shared buildings:"), FONT_SMALL, height=20)
    for n, (name, building, frame) in enumerate(ST_SHARED):
        sx = x0 + 14 + n * 54
        entry += strip("st_c_sh_icon_%s" % name, sx, 144, "GFX_buildings_strip", frame, 0.6)
        value = dict((c[0], c[1]) for c in STATE_COLUMNS)[name]
        entry += text("st_c_sh_%s" % name, sx + 28, 146, 24, B.key("st_c_sh_%s" % name, "[?%s|0]" % value), FONT_LABEL, height=22)
        entry += text("st_c_sh_%s_z" % name, sx + 28, 146, 24, B.key("st_c_sh_z", "§g-§!"), FONT_LABEL, height=22)
        row_triggers += block("st_c_sh_%s_visible" % name, more_than_zero(value))
        row_triggers += block("st_c_sh_%s_z_visible" % name, "NOT = { %s }\n" % more_than_zero(value).strip())
    entry += text("st_c_sh_other", x0 + 14, 176, w - 28, B.key("st_c_sh_other", "and [?mod1440_st_used_other|0] in other shared buildings"), FONT_SMALL, height=20)
    row_triggers += block("st_c_sh_other_visible", more_than_zero("mod1440_st_used_other"))
    entry += text("st_c_note", x0 + 14, 200, w - 28, B.key("st_c_note", "§gThe game's own shared buildings only§!"), FONT_SMALL, height=20)

    # ---- buildings: the nine icons, the level under each, a damaged level in red, damage and bombing
    x0, w = ST_CARD_AT["build"]
    for n, (name, value, width, head, tip_text, group) in enumerate(c for c in STATE_COLUMNS if c[5] == "build"):
        bx = x0 + 12 + n * 42
        damaged = "damaged_building_level@" + ST_BUILDING[name]
        entry += strip("st_c_b_icon_%s" % name, bx, 44, "GFX_buildings_strip", head[1], 0.9)
        entry += text("st_c_b_%s" % name, bx - 2, 90, 46, B.key("st_c_b_%s" % name, "[?%s|0]" % value), FONT_VALUE, "centre", 26)
        entry += text("st_c_b_%s_z" % name, bx - 2, 90, 46, B.key("st_c_b_z", "§g-§!"), FONT_VALUE, "centre", 26)
        entry += text("st_c_b_%s_dmg" % name, bx - 2, 118, 46, B.key("st_c_b_%s_dmg" % name, "§R-[?%s|0]§!" % damaged), FONT_SMALL, "centre", 20)
        row_triggers += block("st_c_b_%s_visible" % name, more_than_zero(value))
        row_triggers += block("st_c_b_%s_z_visible" % name, "NOT = { %s }\n" % more_than_zero(value).strip())
        row_triggers += block("st_c_b_%s_dmg_visible" % name, more_than_zero(damaged))
    entry += text("st_c_dmg", x0 + 14, 150, w - 28, B.key("st_c_dmg", "§R[?mod1440_st_dmg|0] levels damaged§!, in red above"), FONT_SMALL, height=20)
    entry += text("st_c_nodmg", x0 + 14, 150, w - 28, B.key("st_c_nodmg", "§gNo building is damaged.§!"), FONT_SMALL, height=20)
    row_triggers += block("st_c_dmg_visible", more_than_zero("mod1440_st_dmg"))
    row_triggers += block("st_c_nodmg_visible", "NOT = { %s }\n" % more_than_zero("mod1440_st_dmg").strip())
    # What the game gives for a state never bombed is not known yet (a 1936 start has none): a day count
    # from 1 to ten years is taken as a bombing, anything else as none.
    bombed = "check_variable = { days_since_last_strategic_bombing > 0 }\ncheck_variable = { days_since_last_strategic_bombing < 3650 }\n"
    entry += text("st_c_bombed", x0 + 14, 172, w - 28, B.key("st_c_bombed", "Last bombed [?days_since_last_strategic_bombing|0] days ago"), FONT_SMALL, height=20)
    entry += text("st_c_unbombed", x0 + 14, 172, w - 28, B.key("st_c_unbombed", "§gNot bombed.§!"), FONT_SMALL, height=20)
    row_triggers += block("st_c_bombed_visible", bombed)
    row_triggers += block("st_c_unbombed_visible", "NOT = { AND = { %s } }\n" % bombed.replace("\n", " ").strip())

    # ---- occupation: the state's figures for a state that is not a core, then the country's modifiers
    x0, w = ST_CARD_AT["occ"]
    for n, (name, label, value) in enumerate((
            ("compliance", "$COMPLIANCE$", "[?compliance|1]%  [?compliance_speed|+=2]"),
            ("resistance", "$RESISTANCE$", "[?resistance|1]%  [?resistance_speed|-=2]"),
            ("target", "Resistance target", "[?resistance_target|1]%"))):
        y = 44 + n * 21
        entry += text("st_c_occ_%s_l" % name, x0 + 14, y, 130, B.key("st_c_occ_%s_l" % name, label), FONT_SMALL, height=20)
        entry += text("st_c_occ_%s" % name, x0 + 140, y, w - 154, B.key("st_c_occ_%s" % name, value), FONT_SMALL, "right", 20)
        row_triggers += block("st_c_occ_%s_l_visible" % name, noncore) + block("st_c_occ_%s_visible" % name, noncore)
    entry += text("st_c_occ_core", x0 + 14, 44, w - 28, B.key("st_c_occ_core", "§gA core of yours: no occupation.§!"), FONT_SMALL, height=20)
    row_triggers += block("st_c_occ_core_visible", core)
    page += text("st_c_mod_caption", ST_CARD_X + x0 + 14, ST_BAND_Y + 112, w - 28, B.key("st_c_mod_caption", "§gYour country's modifiers§!"), FONT_SMALL, height=20)
    for n, (key, token, fmt) in enumerate((("MODIFIER_COMPLIANCE_GROWTH", "compliance_growth", "+=%1"),
                                           ("MODIFIER_RESISTANCE_TARGET", "resistance_target", "-=%1"),
                                           ("MODIFIER_REQUIRED_GARRISON_FACTOR", "required_garrison_factor", "-=%1"))):
        y = ST_BAND_Y + 134 + n * 21
        variable = "modifier@" + token
        page += text("st_c_mod_%d_l" % n, ST_CARD_X + x0 + 14, y, 190, key, FONT_SMALL, height=20)
        page += text("st_c_mod_%d" % n, ST_CARD_X + x0 + 200, y, w - 214, B.key("st_c_mod_%d" % n, "[?%s|%s]" % (variable, fmt)), FONT_SMALL, "right", 20)
        page += text("st_c_mod_%d_z" % n, ST_CARD_X + x0 + 200, y, w - 214, B.key("st_c_mod_z", "§g-§!"), FONT_SMALL, "right", 20)
        changed = "NOT = { check_variable = { %s = 0 } }\n" % variable
        triggers += block("st_c_mod_%d_visible" % n, changed) + block("st_c_mod_%d_z_visible" % n, "check_variable = { %s = 0 }\n" % variable)

    # the list of one row, between the cards and the country's modifiers: drawn over the one, under the other
    grid = ('gridboxtype = {\n\tname = "st_card_grid"\n\tposition = { x = %d y = %d }\n\tsize = { width = %d height = %d }\n'
            '\tslotsize = { width = 1 height = 1 }\n\tadd_horizontal = no\n\tformat = "UPPER_LEFT"\n}\n' % (ST_CARD_X, ST_BAND_Y, ST_CARD_W, ST_BAND_H))
    cards_end = page.index('instantTextboxType = { name = "st_c_mod_caption"')
    page = page[:cards_end] + grid + page[cards_end:]
    return page, row("mod1440_states_card", ST_CARD_W, ST_BAND_H, entry), triggers, row_triggers, effects, properties


def states_table():
    effects = ""
    triggers = ""
    properties = ""

    # ---- title strip, with the choices of which states to list: each a button with a second frame for "chosen"
    body = box("st_head", 3, 3, ST_W - 6, 50, "", "GFX_tiled_header")
    body += text("st_title", 22, 8, 170, B.key("st_title", "States"), FONT_TITLE, height=40)
    body += text("st_hint", ST_W - 86 - 590, 18, 590, B.key("st_hint", "Click a state for its card, right-click to see it on the map. Shift+M hides the page."), FONT_SMALL, "right")
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
                   tooltip=B.key("st_refresh_tt", "Makes the list again. It is made when the page opens, when you sort or choose, and at the start of each day while the page is open. The numbers of a row, the totals and the cards are from that moment."))
    effects += block("st_refresh_click", "mod1440_st_list = yes\n")

    # ---- the table card: a caption over each group of columns
    body += box("st_table", ST_CARD_X, ST_TABLE_Y, ST_CARD_W, ST_TABLE_H, "", CARD_BG)
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
    picked = is_one("mod1440_st_picked") + "\n"
    unpicked = "NOT = { %s }\n" % picked.strip()
    owned, held = "is_owned_by = ROOT\n", "NOT = { is_owned_by = ROOT }\n"
    entry = icon("st_row_stripe", 0, 0, STRIPE % (ST_ROWS_W, ST_ROW))
    entry += icon("st_row_pick", 0, 0, PICK % (ST_ROWS_W, ST_ROW))
    entry += button("st_row", 0, 0, HEAD_SPRITES[ST_NAME], tooltip=B.key("st_row_tt", "Click: this state's cards under the table. Right-click: show it on the map and hide the page."))
    # the owner's flag beside the name of a state that is held but not owned
    entry += 'iconType = { name = "st_row_flag" position = { x = 8 y = 7 } spriteType = "GFX_flag_smallest" alwaystransparent = yes }\n'
    properties += block("st_row_flag", 'image = "[THIS.Owner.GetFlag]"\n')
    # the name: yellow on the chosen row, another colour for a state that is not a core of yours
    names = [("name", 10, "[THIS.GetName]", owned + "is_core_of = ROOT\n" + unpicked),
             ("occ", 10, "§L[THIS.GetName]§!", owned + "NOT = { is_core_of = ROOT }\n" + unpicked),
             ("chosen", 10, "§Y[THIS.GetName]§!", owned + picked),
             ("held", 36, "§L[THIS.GetName]§!", held + unpicked),
             ("held_chosen", 36, "§Y[THIS.GetName]§!", held + picked)]
    row_triggers = block("st_row_stripe_visible", is_one("mod1440_st_odd") + "\n") + block("st_row_pick_visible", picked)
    row_triggers += block("st_row_flag_visible", held)
    for name, nx, value, condition in names:
        entry += plain("st_row_%s" % name, nx, 4, ST_NAME - nx - 6, B.key("st_row_%s" % name, value), height=22)
        row_triggers += block("st_row_%s_visible" % name, condition)
    # the used share of the shared slots, left of the free count
    entry += scaled("st_row_bar", ST_EDGE["free"] + 6, 11, bar_sprite(ST_FREE_BAR - 6), 1, tooltip=B.key("st_row_bar_tt", "Shared slots in use. Only the game's own shared buildings are counted: with a mod that adds some, the bar is short. The free number is the game's own."))
    properties += block("st_row_bar", "frame = mod1440_st_used\n")
    row_triggers += block("st_row_bar_visible", more_than_zero("mod1440_st_slots"))
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
        # a value stands in the middle of its column, under the middle of its head; the free count in the
        # middle of what the bar leaves of its column
        cell_x, cell_w = (ST_EDGE[name] + ST_FREE_BAR, width - ST_FREE_BAR) if name == "free" else (ST_EDGE[name], width)
        entry += text("st_cell_%s" % name, cell_x, 4, cell_w, B.key("st_cell_%s" % name, "[?%s%s" % (value, fmt)), FONT_LABEL, "centre", 22)
        if group == "occ":
            row_triggers += block("st_cell_%s_visible" % name, "NOT = { is_core_of = ROOT }\n")
            continue
        if group == "build":
            # a damaged building: its level in red, in place of the plain one
            damaged = more_than_zero("damaged_building_level@" + ST_BUILDING[name])
            entry += text("st_cell_%s_dmg" % name, cell_x, 4, cell_w, B.key("st_cell_%s_dmg" % name, "[?%s|R0]" % value), FONT_LABEL, "centre", 22)
            row_triggers += block("st_cell_%s_visible" % name, more_than_zero(value) + "NOT = { %s }\n" % damaged.strip())
            row_triggers += block("st_cell_%s_dmg_visible" % name, damaged)
        elif name != "pop":
            row_triggers += block("st_cell_%s_visible" % name, more_than_zero(value))
        # the total of the column, over the states that are listed
        total += text("st_total_%s" % name, cell_x, 4, cell_w,
                      B.key("st_total_%s" % name, "[?mod1440_st_sum_%s%s" % (name, "|0]K" if name == "pop" else "|0]")), FONT_LABEL, "centre", 22)
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
    body += box("st_totals", 14, ST_TOTAL_Y, ST_ROWS_W, ST_ROW, total, HEAD_SPRITES[240])
    # A click chooses the state for the band; a right-click moves the camera there and hides the page (the
    # left click of the first build). The row's scope is the state.
    effects += block("st_row_click", block("ROOT", "set_variable = { mod1440_st_sel = PREV }\nmod1440_st_pick = yes\n"))
    effects += block("st_row_right_click", block("ROOT", "goto_state = PREV\nset_variable = { mod1440_st_open = 0 }\nadd_to_variable = { mod1440_st_dirty = 1 }\n"))

    # ---- the band of the chosen state
    band, card_row, band_triggers, card_triggers, band_effects, band_properties = states_band()
    body += band
    triggers += band_triggers
    effects += band_effects
    properties += band_properties

    gui = box("mod1440_states", ST_X, ST_Y, ST_W, ST_H, body, PAGE_BG)
    gui += row("mod1440_states_row", ST_ROWS_W, ST_ROW, entry)
    gui += card_row
    handle = button("st_unfold", 0, 0, "GFX_button_148x34", B.key("st_unfold", "States"), shortcut="shift+m",
                    tooltip=B.key("st_unfold_tt", "Show every state you control as a table"))
    gui += box("mod1440_states_handle", ST_X, 8, 148, 34, handle)

    script = scripted_gui(
        "mod1440_states", "mod1440_states", "construction_tab",
        visible="check_variable = { mod1440_st_open = 1 }\n", dirty="mod1440_st_dirty",
        lists=(block("st_grid", 'array = mod1440_st_rows\nchange_scope = yes\nentry_container = "mod1440_states_row"\n')
               + block("st_card_grid", 'array = mod1440_st_card\nchange_scope = yes\nentry_container = "mod1440_states_card"\n')),
        effects=effects, triggers=triggers + row_triggers + card_triggers, properties=properties)
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
    # what the cards and the slot bar need of each state, kept on the state when the list is made
    shared = "".join("add_to_variable = { mod1440_st_used_n = building_level@%s }\n" % b for n, b, f in ST_SHARED[1:])
    other = "".join("add_to_variable = { mod1440_st_used_other = building_level@%s }\n" % b for b in ST_SHARED_OTHER)
    figures = (
        setv("mod1440_st_used_n", "building_level@" + ST_SHARED[0][1]) + shared
        + setv("mod1440_st_used_other", 0) + other
        + "add_to_variable = { mod1440_st_used_n = mod1440_st_used_other }\n"
        + setv("mod1440_st_slots", "mod1440_st_free") + "add_to_variable = { mod1440_st_slots = mod1440_st_used_n }\n"
        + setv("mod1440_st_used", 0)
        + iff("check_variable = { mod1440_st_slots > 0 }", setv("mod1440_st_used", "mod1440_st_used_n")
              + "multiply_variable = { mod1440_st_used = 100 }\ndivide_variable = { mod1440_st_used = mod1440_st_slots }\n")
        + "".join(setv("mod1440_st_r_" + r, "resource@" + r) + "round_variable = mod1440_st_r_%s\n" % r for r in ST_RESOURCES)
        + setv("mod1440_st_dmg", 0)
        + "".join("add_to_variable = { mod1440_st_dmg = damaged_building_level@%s }\n" % b for b in ST_BUILDING.values())
        + "".join(iff("has_state_category = %s" % c, setv("mod1440_st_cat", "token:" + c), "if" if n == 0 else "else_if")
                  for n, c in enumerate(ST_CATEGORIES))
        + els(setv("mod1440_st_cat", 0))
        + setv("mod1440_st_picked", 0))
    listing_script = (
        "# States: makes the list of the page again, for the country in scope. For each state it controls: count the\n"
        "# free shared slots and what the cards need, keep the state if the choices of the page want it and add it\n"
        "# to the totals; then sort, and choose the state of the cards.\n"
        + block("mod1440_st_list", (
            "clear_array = mod1440_st_rows\n" + clear
            + block("for_each_scope_loop", (
                "array = controlled_states\n"
                + free_slot_tree(0, 31) + figures
                + "set_temp_variable = { st_keep = 1 }\n"
                + block("if", block("limit", "check_variable = { ROOT.mod1440_st_show = 1 }\nNOT = { is_core_of = ROOT }\n") + "set_temp_variable = { st_keep = 0 }\n")
                + block("if", block("limit", "check_variable = { ROOT.mod1440_st_show = 2 }\nis_core_of = ROOT\n") + "set_temp_variable = { st_keep = 0 }\n")
                + block("if", block("limit", "check_variable = { ROOT.mod1440_st_only_free = 1 }\ncheck_variable = { mod1440_st_free < 1 }\n") + "set_temp_variable = { st_keep = 0 }\n")
                + iff("check_variable = { st_keep = 1 }", "add_to_array = { ROOT.mod1440_st_rows = THIS }\n" + sums)))
            + "mod1440_st_sort = yes\n" + bands + arrows + frames
            + "mod1440_st_pick = yes\n"))
        + "\n# States: the state of the cards, for the country in scope. The one in mod1440_st_sel if it is listed, else\n"
        "# the first of the list. Its row gets the mark of the chosen row, the others lose theirs (as on the Officers page).\n"
        + block("mod1440_st_pick", (
            block("for_each_scope_loop", "array = mod1440_st_rows\n" + setv("mod1440_st_picked", 0))
            + "clear_array = mod1440_st_card\n"
            + iff("check_variable = { mod1440_st_rows^num > 0 }", (
                iff("NOT = { is_in_array = { array = mod1440_st_rows value = mod1440_st_sel } }", setv("mod1440_st_sel", "mod1440_st_rows^0"))
                + block("var:mod1440_st_sel", setv("mod1440_st_picked", 1))
                + "add_to_array = { mod1440_st_card = mod1440_st_sel }\n"))
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


# ---------------------------------------------------------------- National Figures and History (D4, D5), docked to Politics

# One page beside the politics panel (redesign of 2026-10-16, wiki/phases/D4-national-figures.md): twenty figures
# as tiles that also choose the graph, the chosen figure month by month across the page, and the summed modifiers
# in four lists that show what applies, or all of them.
#
# A row is (label, value, format): the label is a text key of the game (it then follows the player's language)
# or a text of the mod; the value is a variable of the country; the format is what follows the bar in
# "[?value|format]". "+" colours a gain green, "-" colours a gain red (for costs and penalties), "=" adds
# the sign. A value from "modifier@" is the country's summed modifier, the number the game works with.
def modifier_row(key, token, fmt="+=%1"):
    return (key, "modifier@" + token, fmt)


# The groups of summed modifiers: (name, title, column, rows).
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
    ("manpower", "Manpower", 2, [
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
    ("research", "Research and Intelligence", 3, [
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
# The four lists, left to right: (title, the groups they hold in this order, rows on the screen)
NF_COLUMNS = [("Politics and Diplomacy", ["politics", "occupation"], 20), ("Industry", ["industry"], 11),
              ("Army and Manpower", ["manpower", "army"], 20), ("Navy, Air and Research", ["research", "navy", "air"], 20)]
# How a value of a list row is written: the kind a row carries in its list (0 is the head of a group)
NF_FORMATS = ["+=%1", "-=%1", "+=%2", "+=2", "+=0", "%1", "%2"]
RESOURCES = ["oil", "aluminium", "rubber", "tungsten", "steel", "chromium", "coal"]

# A figure is (caption, value of the country, factor, unit, decimals, rise): the value is written down on the
# first of each month, times the factor (100 turns a 0 to 1 share into a percentage). decimals is how the
# number is written, rise the colour of a change: "+" a rise is green, "-" a rise is red. The first twelve are
# the series of the build before 2026-10-16, in their order: a save keeps their arrays mod1440_h_0 to _11. The
# eight after them start later in such a save and get -1 in front, for the months they were not written down.
SERIES = [
    ("Free manpower", "manpower_k", 1, "in thousands", 1, "+"),
    ("Manpower in the field", "deployed_total_manpower_k", 1, "in thousands", 1, "+"),
    ("Divisions", "num_divisions", 1, "", 0, "+"),
    ("Civilian factories", "num_of_civilian_factories", 1, "", 0, "+"),
    ("Military factories", "num_of_military_factories", 1, "", 0, "+"),
    ("Dockyards", "num_of_naval_factories", 1, "", 0, "+"),
    ("Stability", "stability", 100, "in percent", 1, "+"),
    ("War support", "has_war_support", 100, "in percent", 1, "+"),
    ("Fuel", "fuel_k", 1, "in thousands", 1, "+"),
    ("Infantry equipment", "num_equipment@infantry_equipment", 1, "in stock", 0, "+"),
    ("Casualties", "casualties_k", 1, "in thousands", 1, "-"),
    ("Political power", "political_power", 1, "", 0, "+"),
    ("Research slots", "amount_research_slots", 1, "", 0, "+"),
    ("Technologies", "num_researched_technologies", 1, "researched so far", 0, "+"),
    ("Command power", "command_power", 1, "", 1, "+"),
    ("States controlled", "num_controlled_states", 1, "", 0, "+"),
    ("Convoys in stock", "num_equipment@convoy", 1, "", 0, "+"),
    ("Trains in stock", "num_equipment@train_equipment", 1, "", 0, "+"),
    ("Ships", "num_ships", 1, "", 0, "+"),
    ("Planes on airfields", "num_deployed_planes", 1, "", 0, "+"),
]
H_OLD = 12              # series a save of the build before 2026-10-16 has

# The tiles, in two rows of two groups of five: (series, value of today, tooltip, bar variable or None). The
# tile's label is its series' caption; under the value stands its change in a month, or a bar.
NF_TILES = [
    [(3, "£civ_factory [?num_of_civilian_factories|0]  §g[?num_of_civilian_factories_available_for_projects|0] free§!",
      "Your civilian factories, and how many of them are free for construction once consumer goods and trade have taken theirs.", None),
     (4, "£mil_factory [?num_of_military_factories|0]  §g[?num_of_available_military_factories|0] idle§!",
      "Your military factories, and how many of them have no production line.", None),
     (5, "£nav_dockyard_texticon [?num_of_naval_factories|0]  §g[?num_of_available_naval_factories|0] idle§!",
      "Your dockyards, and how many of them have no production line.", None),
     (12, "[?amount_research_slots|0]", "Your research slots.", None),
     (13, "[?num_researched_technologies|0]", "Technologies you have researched.", None),
     (11, "[?political_power|0]  [?political_power_daily|+=2]", "Political power, and what you gain each day.", None),
     (14, "[?command_power|0]  [?command_power_daily|+=2]", "Command power, and what you gain each day.", None),
     (6, "[?stability|%1]", "Stability.", "mod1440_nf_stab"),
     (7, "[?has_war_support|%1]", "War support.", "mod1440_nf_ws"),
     (15, "[?num_controlled_states|0]", "States you control.", None)],
    [(0, "[?manpower_k|1]K", "Men you can still call up: the manpower of the top bar.", None),
     (1, "[?deployed_total_manpower_k|1]K", "Men in your divisions, ships and air wings.", None),
     (2, "[?num_divisions|0]", "Divisions in the field.", None),
     (9, "[?num_equipment@infantry_equipment|0]", "Infantry equipment in the stockpile.", None),
     (10, "[?casualties_k|1]K", "Men lost in all your wars.", None),
     (8, "[?fuel_k|0]K of [?max_fuel_k|0]K", "Fuel in your stockpile, and what the stockpile can hold.", "mod1440_nf_fuel"),
     (16, "[?num_equipment@convoy|0]", "Convoys that no trade, supply route or naval invasion uses.", None),
     (17, "[?num_equipment@train_equipment|0]", "Trains in the stockpile.", None),
     (18, "[?num_ships|0]", "Your ships.", None),
     (19, "[?num_deployed_planes|0]", "Planes in your air wings.", None)],
]

# From the corner of the politics panel (screen -6,78): beside the panel, which is 550 wide, and short of the
# theatre box under the clock (screen x 2234); from under the top bar to above the army portraits.
NF_X, NF_Y, NF_W, NF_H = 556, 0, 1680, 1210
NF_IN = NF_W - 28                       # a card, between the margins of the page
NF_TW, NF_TH, NF_TGAP, NF_TSPLIT = 155, 62, 6, 18   # a tile, the gap between tiles and between the two groups
NF_TILE_SPRITE = "GFX_1440p_SG_tile_%dx%d" % (NF_TW, NF_TH)
NF_PICK_SPRITE = PICK % (NF_TW - 6, NF_TH - 6)
NF_FIG_Y, NF_FIG_H = 56, 188            # the card of the tiles
NF_GRAPH_Y, NF_GRAPH_H = 256, 352       # the card of the graph
NF_COL_Y, NF_COL_W, NF_COL_H = 620, 404, 576    # the four cards of modifiers
NF_ROW = 26                             # a row of a list of modifiers
NF_LIST_W = NF_COL_W - 16               # a list in its card, with its scrollbar
NF_ROW_W = NF_LIST_W - 30               # a row of it
NF_PLATE_W, NF_PLATE_H = 150, 48        # the six numbers of the chosen figure

H_KEEP = 120            # months on the graph: ten years
H_COLUMN = 12           # px from one column to the next
H_CHART_W, H_CHART_H = H_KEEP * H_COLUMN, 240
H_STEPS = H_CHART_H     # heights a column can have (the "steps" of the column sprite): one per pixel
H_AXIS = 20             # under the columns: the years
H_YEARS = 10            # year marks under the graph: ten years have at most ten first months
H_INSET = 4             # the columns stand this far inside the frame of the graph
H_CHART_X, H_CHART_Y = 80, 64           # the frame of the graph in its card
H_COLUMN_SPRITE = "GFX_1440p_SG_column_%dx%d" % (H_COLUMN - 2, H_CHART_H)


# A share on a plate, as the Records' pages use it (tools/build_records.py): the National Figures page had it first.
NF_GAP = 5                      # between the tiles of a band of ten
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


def through(name, x, y, sprite):
    """An icon that lets a click through to the button under it."""
    return 'iconType = { name = "%s" position = { x = %d y = %d } spriteType = "%s" alwaystransparent = yes }\n' % (name, x, y, sprite)


def nf_token(name, words):
    """A text of the mod that script holds as a text key (X37). The key is lower case, as the probe's were and as
    the Records' are (tools/build_records.py, token)."""
    key = "mod1440_" + name
    if B.loc.get(key, words) != words:
        raise ValueError("two texts for " + key)
    B.loc[key] = words
    return "token:" + key


def label_token(name, i, label):
    """A modifier's label as a text key that script holds: a label in capitals is a key of the game; a text of the
    mod gets a key in lower case."""
    if re.match(r"^[A-Z][A-Z0-9_]*$", label):
        return "token:" + label
    return nf_token("nf_%s_%d" % (name, i), label.strip())


def figure_tiles():
    """The card of twenty tiles. Returns its inside, triggers, properties and effects."""
    inner = text("nf_fig_hint", NF_IN - 14 - 700, 14, 700, B.key(
        "nf_fig_hint", "§gThe change in a month under each; written down on the first of each month§!"), FONT_SMALL, "right", 20)
    triggers, properties, effects = "", "", ""
    for r, tiles in enumerate(NF_TILES):
        for c, (n, value, tip, bar) in enumerate(tiles):
            x = 14 + c * (NF_TW + NF_TGAP) + (NF_TSPLIT if c >= 5 else 0)
            y = 44 + r * (NF_TH + 6)
            caption, variable, factor, unit, decimals, rise = SERIES[n]
            name = "nf_t%d" % n
            inner += button(name, x, y, NF_TILE_SPRITE, tooltip=B.key(name + "_tt", tip + "\\nClick to see its months on the graph."))
            inner += through(name + "_pick", x + 3, y + 3, NF_PICK_SPRITE)
            triggers += block(name + "_pick_visible", "check_variable = { mod1440_h_series = %d }\n" % n)
            effects += block(name + "_click", "set_variable = { mod1440_h_series = %d }\nmod1440_h_draw = yes\n" % n)
            inner += plain(name + "_l", x + 6, y + 4, NF_TW - 12, B.key("h_series_%d" % n, caption), FONT_SMALL, "centre", 20)
            inner += plain(name + "_v", x + 6, y + 21, NF_TW - 12, B.key(name + "_v", value), FONT_VALUE, "centre", 24)
            if bar:
                inner += through(name + "_bar", x + 8, y + 46, bar_sprite(140))
                properties += block(name + "_bar", "frame = %s\n" % bar)
                continue
            # the change since the month before, written down by mod1440_h_draw
            month = "check_variable = { mod1440_h_tab_hm^%d = 1 }\n" % n
            same = "check_variable = { mod1440_h_tab_m^%d = 0 }\n" % n
            inner += plain(name + "_dm", x + 6, y + 42, NF_TW - 12, B.key(name + "_dm", "[?mod1440_h_tab_m^%d|%s=%d] §gin a month§!" % (n, rise, decimals)),
                           FONT_SMALL, "centre", 20)
            inner += plain(name + "_same", x + 6, y + 42, NF_TW - 12, B.key("nf_t_same", "§gno change§!"), FONT_SMALL, "centre", 20)
            triggers += block(name + "_dm_visible", month + "NOT = { %s }\n" % same.strip()) + block(name + "_same_visible", month + same)
    return inner, triggers, properties, effects


def figure_graph():
    """The card of the chosen figure: its name, six numbers, and its months as columns. Returns its inside, the
    year marks (which belong to the page: script moves them), the column entry, triggers, properties, effects
    and the script that places the year marks."""
    triggers, properties, effects = "", "", ""
    some = more_than_zero("mod1440_h_valid")
    inner = ""
    for n, (caption, variable, factor, unit, decimals, rise) in enumerate(SERIES):
        # the name, and under it in grey the unit of its numbers
        chosen = "check_variable = { mod1440_h_series = %d }\n" % n
        inner += text("h_name_%d" % n, 14, 10, 312, B.key("h_name_%d" % n, caption), FONT_CARD, height=30)
        triggers += block("h_name_%d_visible" % n, chosen)
        if unit:
            inner += text("h_unit_%d" % n, 14, 36, 312, B.key("h_unit_%d" % n, "§g%s§!" % unit), FONT_SMALL, height=20)
            triggers += block("h_unit_%d_visible" % n, chosen)

    def number(name, x, y, width, variable, font, fmt, signed=False, when=""):
        """A number of the chosen figure with its own decimals, and a change in the colours of its figure: one text
        for each way of writing, of which a trigger shows one."""
        out, extra = "", ""
        for decimals in (0, 1):
            for rise in (("+", "-") if signed else ("",)):
                widget = "%s_%d%s" % (name, decimals, {"+": "", "-": "r", "": ""}[rise])
                out += text(widget, x, y, width, B.key(widget, "[?%s|%s%s%d]" % (variable, rise, "=" if signed else "", decimals)), font, fmt, 24)
                shown = some + when + "check_variable = { mod1440_h_dec = %d }\n" % decimals
                if signed:
                    shown += "check_variable = { mod1440_h_rise = %d }\n" % (1 if rise == "+" else 0)
                extra += block(widget + "_visible", shown)
        return out, extra

    plates = [("latest", "Latest", "mod1440_h_latest", False, "", "The newest month written down."),
              ("dm", "In a month", "mod1440_h_dm", True, is_one("mod1440_h_has_m") + "\n", "The change since the month before."),
              ("dy", "In a year", "mod1440_h_dy", True, is_one("mod1440_h_has_y") + "\n", "The change since twelve months before."),
              ("max", "Highest", "mod1440_h_max", False, "", "The highest month on the graph."),
              ("min", "Lowest", "mod1440_h_min", False, "", "The lowest month on the graph."),
              ("change", "Since the first month", "mod1440_h_change", True, "", "The newest month less the oldest month on the graph.")]
    for k, (name, label, variable, signed, when, tip) in enumerate(plates):
        x = 330 + k * (NF_PLATE_W + 6)
        inner += icon("h_%s_bg" % name, x, 6, tile_sprite(NF_PLATE_W, NF_PLATE_H))
        inner += text("h_%s_l" % name, x + 4, 9, NF_PLATE_W - 8, B.key("h_%s_l" % name, "§g%s§!" % label), FONT_SMALL, "centre", 18,
                      tooltip=B.key("h_%s_tt" % name, tip))
        part, more = number("h_" + name, x + 4, 26, NF_PLATE_W - 8, variable, FONT_VALUE, "centre", signed, when)
        inner += part
        triggers += more
    inner += text("h_months", NF_IN - 14 - 150 - 10 - 200, 20, 200, B.key("h_months", "§g[?mod1440_h_valid|0] months§!"), FONT_SMALL, "right", 20,
                  tooltip=B.key("h_months_tt", "Months written down for this figure, 120 at most."))
    inner += button("h_zoom", NF_IN - 14 - 140, 14, "GFX_sort_button_140x29", B.key("h_zoom", "Zoom in"), tooltip=B.key(
        "h_zoom_tt", "The columns start at the lowest month instead of at zero, so that small changes show."))
    effects += block("h_zoom_click", flip("mod1440_h_zoom") + "mod1440_h_draw = yes\n")
    properties += block("h_zoom", "frame = mod1440_h_zoom_frame\n")
    # the scale on the left: five heights, from the foot of the columns to the highest month
    for k in range(5):
        part, more = number("h_scale_%d" % k, 14, H_CHART_Y + H_CHART_H - k * (H_CHART_H // 4) - 10, H_CHART_X - 20,
                            "mod1440_h_s%d" % k, FONT_SMALL, "right")
        inner += part
        triggers += more
    # the columns stand on bands a quarter of the height each, and have the years under them
    bands = "".join(icon("h_band_%d" % k, H_INSET, k * (H_CHART_H // 4), STRIPE % (H_CHART_W, H_CHART_H // 4)) for k in (1, 3))
    grid = ('gridboxtype = {\n\tname = "h_grid"\n\tposition = { x = %d y = 0 }\n\tsize = { width = %d height = %d }\n'
            '\tslotsize = { width = %d height = %d }\n\tadd_horizontal = yes\n\tmax_slots_horizontal = %d\n\tformat = "UPPER_LEFT"\n}\n'
            % (H_INSET, H_CHART_W, H_CHART_H + H_AXIS, H_COLUMN, H_CHART_H + H_AXIS, H_KEEP))
    inner += box("h_chart", H_CHART_X, H_CHART_Y, H_CHART_W + 2 * H_INSET, H_CHART_H + H_AXIS, bands + grid, CARD_BG)
    below = H_CHART_Y + H_CHART_H + H_AXIS + 4
    inner += text("h_from", H_CHART_X + H_INSET, below, 300, B.key("h_from", "[?mod1440_h_first.GetDateStringNoHourLong]"), FONT_SMALL, height=20)
    inner += text("h_to", H_CHART_X + H_INSET + H_CHART_W - 300, below, 300, B.key("h_to", "[?mod1440_h_last.GetDateStringNoHourLong]"), FONT_SMALL, "right", 20)
    # a game that got the mod after its start, and a figure the build before this one did not write down, have
    # nothing until the first of the next month
    inner += text("h_none", H_CHART_X + 20, H_CHART_Y + 100, 1000, B.key(
        "h_none", "Nothing is written down for this figure yet. The first column comes on the first of next month."), FONT_LABEL)
    triggers += block("h_none_visible", "NOT = { %s }\n" % some.strip())
    for name in ("h_from", "h_to", "h_months"):
        triggers += block(name + "_visible", some)

    # Under the columns, the year at each first month written down in a new year. The texts belong to the
    # page and script moves them (the x property, as the arrow of a sorted column: Engine Facts X4).
    marks = ""          # script: the k-th year mark gets its year and its place
    years = ""
    first_x = 14 + H_CHART_X + H_INSET + H_COLUMN // 2 - 20
    for k in range(H_YEARS):
        years += text("h_year_%d" % k, first_x, NF_GRAPH_Y + H_CHART_Y + H_CHART_H + 1, 40,
                      B.key("h_year_%d" % k, "[?mod1440_h_yl_%d|0]" % k), FONT_SMALL, "centre", 18)
        properties += block("h_year_%d" % k, "x = mod1440_h_yx_%d\n" % k)
        triggers += block("h_year_%d_visible" % k, more_than_zero("mod1440_h_yl_%d" % k))
        marks += iff("check_variable = { h_slot = %d }" % k, setv("mod1440_h_yl_%d" % k, "h_y") + setv("mod1440_h_yx_%d" % k, "h_x"),
                     "if" if k == 0 else "else_if")
    # a column: a month that was not written down for this figure (-1) is left out
    column = ('iconType = { name = "h_bar" position = { x = 1 y = 0 } spriteType = "%s" pdx_tooltip = "%s" }\n'
              % (H_COLUMN_SPRITE, B.key("h_bar_tt", "[?mod1440_h_date^i.GetDateStringNoHourLong]: [?mod1440_h_now^i|1]")))
    properties += block("h_bar", "frame = v\n")
    triggers += block("h_bar_visible", "check_variable = { v > -1 }\n")
    place = (block("for_loop_effect", "start = 0\nend = %d\nvalue = h_pad\n" % H_KEEP + iff(
        "check_variable = { mod1440_h_year^num < mod1440_h_date^num }", "add_to_array = { array = mod1440_h_year value = 0 index = 0 }\n"))
        + "".join(setv("mod1440_h_yl_%d" % k, 0) for k in range(H_YEARS)) + tmp("h_before", 0) + tmp("h_slot", 0)
        + block("for_each_loop", (
            "array = mod1440_h_year\nvalue = h_y\nindex = h_yi\n"
            + iff("check_variable = { h_yi > 0 }", iff("check_variable = { h_y > 0 }", iff("NOT = { check_variable = { h_y = h_before } }", (
                tmp("h_x", "h_yi") + "multiply_temp_variable = { h_x = %d }\nadd_to_temp_variable = { h_x = %d }\n" % (H_COLUMN, first_x)
                + marks + "add_to_temp_variable = { h_slot = 1 }\n"))))
            + tmp("h_before", "h_y"))))
    return inner, years, column, triggers, properties, effects, place


def modifier_lists():
    """The four cards of summed modifiers, each one list of the groups it holds, and the resource table under
    Industry. Returns the cards, the four row containers, the dynamic lists, triggers and the fill effect."""
    cards, rows, lists, triggers, fill = "", "", "", "", ""
    groups = {name: (title, column, entries) for name, title, column, entries in FIGURES}
    for c, (title, names, shown) in enumerate(NF_COLUMNS):
        x = 14 + c * (NF_COL_W + 12)
        total = sum(len(groups[g][2]) for g in names)
        inner = text("nf_c%d_count" % c, NF_COL_W - 14 - 200, 16, 200, B.key("nf_c%d_count" % c, "§g[?mod1440_nf_a%d|0] of %d apply§!" % (c, total)),
                     FONT_SMALL, "right", 20)
        inner += listing("nf_l%d" % c, "nf_l%d_grid" % c, 8, 44, NF_LIST_W, shown * NF_ROW + 8, NF_ROW)
        lists += block("nf_l%d_grid" % c, 'array = mod1440_nf_c%d_k\nentry_container = "mod1440_figures_row_%d"\n' % (c, c))
        if "industry" in names:
            inner += resource_table(14 + 2, 44 + shown * NF_ROW + 8 + 16)
        cards += card("nf_col%d" % c, x, NF_COL_Y, NF_COL_W, NF_COL_H, title, inner)

        # A row of the list: the head of a group (kind 0), or a modifier with the kind of its format. The label is
        # a text key held in an array; the value a copy of the modifier when the list was made.
        arr = "mod1440_nf_c%d_" % c
        p = "nf_r%d_" % c
        head = "check_variable = { v = 0 }\n"
        line = "check_variable = { v > 0 }\n"
        zero = "check_variable = { %sv^i = 0 }\n" % arr
        some = "NOT = { %s }\n" % zero.strip()
        entry = icon(p + "stripe", 0, 0, STRIPE % (NF_ROW_W, NF_ROW))
        entry += icon(p + "head", 0, 0, "GFX_1440p_SG_head_%dx%d" % (NF_ROW_W, NF_ROW))
        entry += text(p + "hname", 8, 4, 240, B.key(p + "hname", "§Y[?%st^i.GetTokenLocalizedKey]§!" % arr), FONT_SMALL, height=20)
        entry += text(p + "hcount", NF_ROW_W - 8 - 100, 4, 100, B.key(p + "hcount", "§g[?%sv^i|0] of [?%sn^i|0]§!" % (arr, arr)), FONT_SMALL, "right", 20)
        entry += text(p + "label", 8, 4, 250, B.key(p + "label", "[?%st^i.GetTokenLocalizedKey]" % arr), FONT_SMALL, height=20, fixed=True)
        entry += text(p + "dim", 8, 4, 250, B.key(p + "dim", "§g[?%st^i.GetTokenLocalizedKey]§!" % arr), FONT_SMALL, height=20, fixed=True)
        row_triggers = block(p + "stripe_visible", line + "check_variable = { mod1440_odd^i = 1 }\n")
        for part in ("head", "hname", "hcount"):
            row_triggers += block(p + part + "_visible", head)
        row_triggers += block(p + "label_visible", line + some) + block(p + "dim_visible", line + zero)
        for k, fmt in enumerate(NF_FORMATS, start=1):
            entry += text(p + "v%d" % k, NF_ROW_W - 8 - 86, 2, 86, B.key(p + "v%d" % k, "[?%sv^i|%s]" % (arr, fmt)), FONT_LABEL, "right", 22)
            row_triggers += block(p + "v%d_visible" % k, "check_variable = { v = %d }\n" % k + some)
        rows += row("mod1440_figures_row_%d" % c, NF_ROW_W, NF_ROW, entry)
        triggers += row_triggers

        # the script that makes the list: a head per group, then each modifier that applies, or every one
        fill += "".join("clear_array = %s%s\n" % (arr, part) for part in "ktvn") + setv("mod1440_nf_a%d" % c, 0)
        for g in names:
            title_g, column, entries = groups[g]
            fill += (tmp("nf_h", arr + "k^num") + "add_to_array = { %sk = 0 }\n" % arr
                     + "add_to_array = { %st = %s }\n" % (arr, nf_token("nf_grp_%s" % g, title_g))
                     + "add_to_array = { %sv = 0 }\nadd_to_array = { %sn = %d }\n" % (arr, arr, len(entries)) + tmp("nf_g", 0))
            for i, (label, value, fmt) in enumerate(entries):
                fill += tmp("nf_x", value) + iff("NOT = { check_variable = { nf_x = 0 } }", "add_to_temp_variable = { nf_g = 1 }\n")
                fill += iff("OR = { %s NOT = { check_variable = { nf_x = 0 } } }" % is_one("mod1440_nf_all"), (
                    "add_to_array = { %sk = %d }\n" % (arr, NF_FORMATS.index(fmt) + 1)
                    + "add_to_array = { %st = %s }\n" % (arr, label_token(g, i, label))
                    + "add_to_array = { %sv = nf_x }\nadd_to_array = { %sn = 0 }\n" % (arr, arr)))
            fill += "set_variable = { %sv^nf_h = nf_g }\nadd_to_variable = { mod1440_nf_a%d = nf_g }\n" % (arr, c)
    return cards, rows, lists, triggers, fill


def resource_table(x, y):
    """Resources: a small table, live, under the list of Industry."""
    width = NF_COL_W - 32
    cols = [("balance", "Balance", "resource", "+=0", "What is left after your own use and your exports."),
            ("made", "Made", "resource_produced", "0", "Produced in your states."),
            ("used", "Used", "resource_consumed", "0", "Used by your production lines."),
            ("in", "Import", "resource_imported", "0", "Bought from other countries."),
            ("out", "Export", "resource_exported", "0", "Sold to other countries.")]
    name_w, col_w = 112, 52
    out = heads("nf_res_heads", x, y, width, [(8, 100, "Resource", "left", None)] + [
        (name_w + c * col_w, col_w - 4, caption, "right", tip) for c, (cname, caption, variable, fmt, tip) in enumerate(cols)])
    out += stripes("nf_res_stripe", x, y + 30, width, NF_ROW, len(RESOURCES))
    for r, resource in enumerate(RESOURCES):
        ry = y + 30 + r * NF_ROW
        out += text("nf_res_name_%d" % r, x + 8, ry + 2, name_w - 10, B.key(
            "nf_res_name_%d" % r, "£resources_strip|%d  $PRODUCTION_MATERIALS_%s$" % (r + 1, resource.upper())), FONT_SMALL, height=22)
        for c, (cname, caption, variable, fmt, tip) in enumerate(cols):
            out += text("nf_res_%s_%d" % (cname, r), x + name_w + c * col_w, ry, col_w - 4,
                        B.key("nf_res_%s_%d" % (cname, r), "[?%s@%s|%s]" % (variable, resource, fmt)), FONT_LABEL, "right", 22)
    return out


def resource_triggers():
    return "".join(block("nf_res_%s_%d_visible" % (cname, r), more_than_zero("%s@%s" % (variable, resource)))
                   for r, resource in enumerate(RESOURCES)
                   for cname, variable in (("made", "resource_produced"), ("used", "resource_consumed"),
                                           ("in", "resource_imported"), ("out", "resource_exported")))


def national_figures():
    triggers = resource_triggers()
    properties = ""
    effects = ""

    # ---- title strip: the title, the two views of the modifiers, a hint and the button that folds the page
    body = box("nf_head", 3, 3, NF_W - 6, 50, "", "GFX_tiled_header")
    body += text("nf_title", 22, 8, 300, B.key("nf_title", "National Figures"), FONT_TITLE, height=40)
    views = [("applies", "What applies", 0, "Only the modifiers that are not 0."),
             ("all", "All modifiers", 1, "Every modifier the page knows, those that are 0 in grey.")]
    for k, (name, caption, value, tip) in enumerate(views):
        x = 330 + k * 150
        body += button("nf_view_%s" % name, x, 13, "GFX_sort_button_140x29", tooltip=B.key("nf_view_%s_tt" % name, tip))
        body += plain("nf_view_%s_off" % name, x, 18, 140, B.key("nf_view_%s" % name, caption), FONT_SMALL, "centre", 20)
        body += plain("nf_view_%s_on" % name, x, 18, 140, B.key("nf_view_%s_on" % name, "§Y%s§!" % caption), FONT_SMALL, "centre", 20)
        chosen = "check_variable = { mod1440_nf_all = %d }\n" % value
        triggers += block("nf_view_%s_on_visible" % name, chosen) + block("nf_view_%s_off_visible" % name, "NOT = { %s }\n" % chosen.strip())
        effects += block("nf_view_%s_click" % name, setv("mod1440_nf_all", value) + "mod1440_nf_fill = yes\n")
        properties += block("nf_view_%s" % name, "frame = mod1440_nf_frame_%s\n" % name)
    body += text("nf_hint", NF_W - 84 - 980, 18, 980, B.key(
        "nf_hint", "§gSums over every law, spirit, advisor, technology and focus. Click a figure for its months.§!"), FONT_SMALL, "right")
    body += button("nf_fold", NF_W - 66, 10, "GFX_closebutton",
                   tooltip=B.key("nf_fold_tt", "Hide this page and give the map back. Shift+M or the Figures button brings it back."))
    effects += block("nf_fold_click", "set_variable = { mod1440_nf_open = 0 }\n")

    # ---- twenty figures, the graph of the chosen one, the modifiers
    inner, more, props, clicks = figure_tiles()
    triggers += more
    properties += props
    effects += clicks
    body += card("nf_figures", 14, NF_FIG_Y, NF_IN, NF_FIG_H, "Figures", inner)
    inner, years, column, more, props, clicks, place = figure_graph()
    triggers += more
    properties += props
    effects += clicks
    body += box("nf_graph", 14, NF_GRAPH_Y, NF_IN, NF_GRAPH_H, inner, CARD_BG)
    body += years
    cards, rows, lists, more, fill = modifier_lists()
    body += cards
    triggers += more

    gui = box("mod1440_figures", NF_X, NF_Y, NF_W, NF_H, body, PAGE_BG)
    gui += row("mod1440_figures_column", H_COLUMN, H_CHART_H + H_AXIS, column)
    gui += rows
    # The button that opens it sits in the title strip of Politics. Between x 230 and 356 another mod has its own
    # button there (Better Mechanics: Production, "Economy Status"), and the game's own stands from 454 on: the
    # button takes the 92 px between them, with the short caption.
    handle = button("nf_toggle", 0, 0, "GFX_1440p_SG_button_92", B.key("nf_toggle", "Figures"), shortcut="shift+m",
                    tooltip=B.key("nf_toggle_tt", "National Figures: show or hide the figures, their months and the summed modifiers of your country"))
    gui += box("mod1440_figures_handle", 359, 12, 92, 34, handle)

    # Docked to the tab, as Army Readiness and States: it opens and closes with Politics, whose window lets it
    # out (interface/zz_1440p_politics.gui, clipping = no). No dirty: the tiles and the resource table are live.
    script = scripted_gui("mod1440_figures", "mod1440_figures", "politics_tab",
                          visible="check_variable = { mod1440_nf_open = 1 }\n",
                          lists=block("h_grid", 'array = mod1440_h_bars\nentry_container = "mod1440_figures_column"\n') + lists,
                          effects=effects, triggers=triggers, properties=properties)
    opened = "mod1440_nf_bars = yes\nmod1440_nf_fill = yes\nmod1440_h_draw = yes\n"
    script += "\n" + scripted_gui("mod1440_figures_handle", "mod1440_figures_handle", "politics_tab",
                                  effects=block("nf_toggle_click", flip("mod1440_nf_open") + iff(is_one("mod1440_nf_open"), opened)))

    # A bar is filled by a variable and by nothing else (Engine Facts X26), so the shares are worked out here.
    bars = (setv("mod1440_nf_stab", "stability") + "multiply_variable = { mod1440_nf_stab = 100 }\n"
            + setv("mod1440_nf_ws", "has_war_support") + "multiply_variable = { mod1440_nf_ws = 100 }\n"
            + setv("mod1440_nf_fuel", 0) + iff("check_variable = { max_fuel_k > 0 }", (
                setv("mod1440_nf_fuel", "fuel_k") + "divide_variable = { mod1440_nf_fuel = max_fuel_k }\n"
                "multiply_variable = { mod1440_nf_fuel = 100 }\nclamp_variable = { var = mod1440_nf_fuel min = 0 max = 100 }\n")))
    frames = setv("mod1440_nf_frame_applies", 2) + setv("mod1440_nf_frame_all", 1) + iff(
        is_one("mod1440_nf_all"), setv("mod1440_nf_frame_applies", 1) + setv("mod1440_nf_frame_all", 2))
    script_effects = (
        "# National Figures: how far the bars of the page are filled, 0 to 100, for the country in scope. Runs when\n"
        "# the page opens and each day for a player; the numbers beside the bars follow the game by themselves.\n"
        + block("mod1440_nf_bars", bars)
        + "\n# National Figures: the four lists of summed modifiers, for the country in scope: per group a head and each\n"
        "# modifier that is not 0, or every one in the All view, with a copy of its value. Runs when the page opens,\n"
        "# when the view changes and each day while it is open.\n"
        + block("mod1440_nf_fill", "mod1440_rec_odd = yes\n" + fill + frames))
    # Each day: the bars, open or not (a few lines of script); the lists and the graph while the page is open, so
    # that a page left open in a saved game is right again after a day at most.
    daily = "mod1440_nf_bars = yes\n" + iff(is_one("mod1440_nf_open"), "mod1440_nf_fill = yes\nmod1440_h_draw = yes\n")
    return gui, script, script_effects, daily, place


def history_script(place):
    """The monthly record of the twenty figures and the drawing of the chosen one. Returns the effects and the
    monthly hook."""
    pad = ""            # script: a figure of the newer build gets -1 for the months it was not written down
    for n in range(H_OLD, len(SERIES)):
        pad += (tmp("h_p", "mod1440_h_date^num") + "subtract_from_temp_variable = { h_p = mod1440_h_%d^num }\n" % n
                + iff("check_variable = { h_p > 0 }", block("for_loop_effect", (
                    "start = 0\nend = h_p\nvalue = h_q\nadd_to_array = { array = mod1440_h_%d value = -1 index = 0 }\n" % n))))
    record = "".join(
        ("add_to_array = { mod1440_h_%d = %s }\n" % (n, value)) if factor == 1 else (
            "set_temp_variable = { h_v = %s }\nmultiply_temp_variable = { h_v = %d }\nadd_to_array = { mod1440_h_%d = h_v }\n" % (value, factor, n))
        for n, (caption, value, factor, unit, decimals, rise) in enumerate(SERIES))
    forget = "".join("remove_from_array = { array = mod1440_h_%d index = 0 }\n" % n for n in range(len(SERIES)))

    def known(n, index):
        """A month of a figure that was written down: for the newer eight, not the -1 of the months before."""
        return "check_variable = { mod1440_h_%d^%s > -1 }" % (n, index) if n >= H_OLD else "always = yes"

    table = ""          # script: today's value of each figure, its change in a month and in a year
    copies = ""         # script: the chosen figure's months and how it is written
    for n, (caption, value, factor, unit, decimals, rise) in enumerate(SERIES):
        s = "mod1440_h_%d" % n
        table += (tmp("h_now", 0) + tmp("h_dm", 0) + tmp("h_hm", 0) + tmp("h_dy", 0) + tmp("h_hy", 0)
                  + iff("check_variable = { h_n > 0 }", tmp("h_now", "%s^h_i1" % s))
                  + iff("check_variable = { h_n > 1 } %s %s" % (known(n, "h_i1"), known(n, "h_i2")),
                        tmp("h_dm", "%s^h_i1" % s) + "subtract_from_temp_variable = { h_dm = %s^h_i2 }\n" % s + tmp("h_hm", 1))
                  + iff("check_variable = { h_n > 12 } %s %s" % (known(n, "h_i1"), known(n, "h_i13")),
                        tmp("h_dy", "%s^h_i1" % s) + "subtract_from_temp_variable = { h_dy = %s^h_i13 }\n" % s + tmp("h_hy", 1))
                  + "".join("add_to_array = { mod1440_h_tab_%s = h_%s }\n" % (part, part) for part in ("now", "dm", "hm", "dy", "hy")))
        copies += iff("check_variable = { mod1440_h_series = %d }" % n, (
            block("for_each_loop", "array = %s\nvalue = h_v\nadd_to_array = { mod1440_h_now = h_v }\n" % s)
            + setv("mod1440_h_dec", decimals) + setv("mod1440_h_rise", 1 if rise == "+" else 0) + tmp("h_skip", 1 if n >= H_OLD else 0)
            + "".join(setv("mod1440_h_%s" % part, "mod1440_h_tab_%s^%d" % (part, n)) for part in ("dm", "dy"))
            + setv("mod1440_h_has_m", "mod1440_h_tab_hm^%d" % n) + setv("mod1440_h_has_y", "mod1440_h_tab_hy^%d" % n)), "if" if n == 0 else "else_if")
    # a month that counts: every month of the first twelve figures, a month written down of the newer eight
    counts = "OR = { check_variable = { h_skip = 0 } check_variable = { h_v > -1 } }"
    scale = (tmp("h_base", 0) + iff(is_one("mod1440_h_zoom"), tmp("h_base", "h_min"))
             + tmp("h_range", "h_max") + "subtract_from_temp_variable = { h_range = h_base }\n"
             + tmp("h_quarter", "h_range") + "divide_temp_variable = { h_quarter = 4 }\n"
             + setv("mod1440_h_s0", "h_base")
             + "".join(setv("mod1440_h_s%d" % k, "mod1440_h_s%d" % (k - 1)) + "add_to_variable = { mod1440_h_s%d = h_quarter }\n" % k for k in (1, 2, 3))
             + setv("mod1440_h_s4", "h_max"))
    bars = ("clear_array = mod1440_h_bars\n" + block("for_each_loop", (
        "array = mod1440_h_now\nvalue = h_v\n" + tmp("h_bar", -1) + iff(counts, (
            tmp("h_bar", 0)
            + iff("check_variable = { h_range > 0 }", tmp("h_bar", "h_v") + "subtract_from_temp_variable = { h_bar = h_base }\n"
                  "divide_temp_variable = { h_bar = h_range }\nmultiply_temp_variable = { h_bar = %d }\n" % H_STEPS)
            # every month the same: the columns stand at full height
            + iff("check_variable = { h_v > 0 }", tmp("h_bar", H_STEPS), "else_if")
            # zoomed in, the lowest month keeps a sliver: it was written down
            + iff(is_one("mod1440_h_zoom"), iff("check_variable = { h_bar < 4 }", tmp("h_bar", 4)))
            + iff("check_variable = { h_bar < 0 }", tmp("h_bar", 0)) + iff("check_variable = { h_bar > %d }" % H_STEPS, tmp("h_bar", H_STEPS))))
        + "add_to_array = { mod1440_h_bars = h_bar }\n")))
    effects = (
        "# History: writes today's twenty figures of the country in scope down, and forgets the oldest month past ten\n"
        "# years. Runs at the start of a game for every country and on the first of each month for a player.\n"
        + block("mod1440_h_record", (
            record + "add_to_array = { mod1440_h_date = global.date }\nadd_to_array = { mod1440_h_year = global.year }\n" + pad
            + iff("check_variable = { mod1440_h_date^num > %d }" % H_KEEP, forget
                  + "remove_from_array = { array = mod1440_h_date index = 0 }\nremove_from_array = { array = mod1440_h_year index = 0 }\n")
            + iff(is_one("mod1440_nf_open"), "mod1440_h_draw = yes\n")))
        + "\n# History: today's value and the changes of each figure for the tiles, then the chosen figure as column\n"
        + "# heights, 0 to %d, between the foot of the graph (zero, or the lowest month when zoomed in) and the highest\n" % H_STEPS
        + "# month. A month of a newer figure that was not written down (-1) is drawn as no column and counts for nothing.\n"
        + block("mod1440_h_draw", (
            pad + tmp("h_n", "mod1440_h_date^num")
            + "".join(tmp("h_i%d" % k, "h_n") + "subtract_from_temp_variable = { h_i%d = %d }\n" % (k, k) for k in (1, 2, 13))
            + "".join("clear_array = mod1440_h_tab_%s\n" % part for part in ("now", "dm", "hm", "dy", "hy"))
            + table
            + "clear_array = mod1440_h_now\n" + copies
            + tmp("h_max", 0)
            + block("find_highest_in_array", "array = mod1440_h_now\nvalue = h_max\nindex = h_at\n")
            # the lowest month, the first month and how many count, with a loop of the page's own: no script of the
            # game uses find_lowest_in_array
            + tmp("h_min", "h_max") + tmp("h_valid", 0) + tmp("h_first", 0)
            + block("for_each_loop", "array = mod1440_h_now\nvalue = h_v\n" + iff(counts, (
                iff("check_variable = { h_valid = 0 }", tmp("h_first", "h_v"))
                + "add_to_temp_variable = { h_valid = 1 }\n" + iff("check_variable = { h_v < h_min }", tmp("h_min", "h_v")))))
            + iff("check_variable = { h_valid = 0 }", tmp("h_max", 0) + tmp("h_min", 0))
            + setv("mod1440_h_max", "h_max") + setv("mod1440_h_min", "h_min") + setv("mod1440_h_valid", "h_valid")
            + scale + bars
            + place
            + setv("mod1440_h_latest", 0) + setv("mod1440_h_change", 0)
            + iff("check_variable = { h_n > 0 }", (
                setv("mod1440_h_latest", "mod1440_h_now^h_i1")
                + setv("mod1440_h_change", "mod1440_h_latest") + "subtract_from_variable = { mod1440_h_change = h_first }\n"
                + setv("mod1440_h_first", "mod1440_h_date^0") + setv("mod1440_h_last", "mod1440_h_date^h_i1")))
            + setv("mod1440_h_zoom_frame", 1) + iff(is_one("mod1440_h_zoom"), setv("mod1440_h_zoom_frame", 2)))))
    monthly = "mod1440_h_record = yes\n"
    return effects, monthly


NF_SCENE_CHOSEN = 4         # the scenes draw the page with Military factories chosen, as the design did


def nf_scene_windows():
    """The windows of the National Figures page for its two scenes: what script hides with Military factories
    chosen, a 0-decimal figure and a rise, and where it moves the year marks; one kind of list row."""
    n = NF_SCENE_CHOSEN
    hide = ["nf_t%d_pick" % k for k in range(len(SERIES)) if k != n] + ["h_name_%d" % k for k in range(len(SERIES)) if k != n]
    hide += ["h_unit_%d" % k for k in range(len(SERIES)) if k != n and SERIES[k][3]]
    hide += ["nf_t%d_same" % k for k in range(len(SERIES))] + ["h_none"]
    hide += ["nf_view_applies_off", "nf_view_all_on"]
    for name in ("latest", "max", "min"):
        hide.append("h_%s_1" % name)
    for name in ("dm", "dy", "change"):
        hide += ["h_%s_0r" % name, "h_%s_1" % name, "h_%s_1r" % name]
    hide += ["h_scale_%d_1" % k for k in range(5)]
    first_x = 14 + H_CHART_X + H_INSET + H_COLUMN // 2 - 20
    place = {"h_year_%d" % k: [first_x + 12 * k * H_COLUMN, NF_GRAPH_Y + H_CHART_Y + H_CHART_H + 1] for k in range(H_YEARS)}
    rows = {"h_grid": H_KEEP}
    list_rows = {"h_grid": "mod1440_figures_column"}
    windows = [{"name": "mod1440_figures", "at": [NF_X - 6, NF_Y + 78], "sidePanel": True, "rows": rows, "listRows": list_rows,
                "hide": hide, "place": place,
                "_note": "Docked to Politics: the tab's corner at -6,78 plus the container's 556,0. Military factories is the chosen figure; script hides the pick plates and names of the other nineteen, the 'no change' twins and the ways of writing a number it does not use. The list rows are drawn alike: a modifier with a value."},
               {"name": "mod1440_figures_column", "skip": True},
               {"name": "mod1440_figures_handle", "at": [359 - 6, 12 + 78]}]
    for c, (title, names, shown) in enumerate(NF_COLUMNS):
        rows["nf_l%d_grid" % c] = (11, 8, 10, 7)[c]
        list_rows["nf_l%d_grid" % c] = "mod1440_figures_row_%d" % c
        windows.append({"name": "mod1440_figures_row_%d" % c, "skip": True,
                        "hide": ["nf_r%d_%s" % (c, part) for part in ("head", "hname", "hcount", "dim", "stripe")]
                        + ["nf_r%d_v%d" % (c, k) for k in range(2, len(NF_FORMATS) + 1)]})
    return windows


# ---------------------------------------------------------------- Top bar strip (D7), on the top bar of every screen

# Values the vanilla top bar keeps in its tooltips, in the empty middle of the bar (x 1042 to 2152, the band's
# flat interior y 3 to 31; scratch/phases/D7/design.json, round 2). The user chose on 2026-10-17 that the values
# are chosen in the game: an edit button opens a panel of eighteen, each with its width and a switch; the chips
# stand in the order of the catalogue and close up from the left. A chip is the game's value box at its own width,
# the game's icon and the value in the top bar's font; its label is in the tooltip.
#
# A chip is three widgets side by side in the strip's container (a nested container follows no x and no _visible,
# Engine Facts X15). Each has an x from a country variable and shows while its switch is on (X4). The effect
# mod1440_tb_place sets those variables on a click only, never on a tick (rule 5); the texts read game values
# directly and follow them without a dirty variable (X2). A save of an earlier build has none of the variables:
# the fixed twin, the eight defaults at fixed places, shows until the first click on the edit button or the next
# day sets them (on_startup does not run when a save is loaded).
TB_X, TB_Y = 1042, 3            # the strip's container, 912x28: y 3 to 31 is the band's flat interior
TB_ROOM = 912                   # px for chips, 1042 to 1954: 16 before the edit button
TB_BOX_Y, TB_H = 1, 26          # a chip's box: 26 high at screen y 4 (the vanilla boxes: 26 at y 5)
TB_TEXT_Y = TB_BOX_Y + 4        # the value at box y + 4, as on the vanilla bar (box y 5, text y 8)
TB_PAD_L, TB_ICON_GAP = 3, 4    # the icon 3 px into the box, the value 4 px after it
TB_GAP, TB_GROUP_GAP = 4, 16    # between chips of a group, and where the group changes
TB_EDIT = (1970, 4, 28, 26)     # the edit button, 4 px left of the Records handle (2002)
TB_VER = 1                      # mod1440_tb_ver: the strip of this build is set up for the country
TB_PANEL_X, TB_PANEL_Y, TB_PANEL_W = 2152 - 842, 40, 842    # under the band, its right edge on the handle's
TB_GROUPS = ["Gains", "Factories", "Fuel", "Manpower", "Resources"]
TB_COLUMNS = [["Gains", "Factories", "Fuel"], ["Manpower", "Resources"]]
TB_RES_NAMES = ["Oil", "Aluminium", "Rubber", "Tungsten", "Steel", "Chromium", "Coal"]
TB_RES_TIP = "%s balance: produced and bought, less what your lines use and what you sell. Red, with the game's crossed icon, below 0."


def tb_chip(name, group, label, width, sprite, frame, scale, icon_w, icon_h, text_x, value, tip, default, twin=None, below=None):
    """One value of the catalogue. Sizes measured by the design (scratch/phases/D7/custom-layout.json): 3 px,
    the icon, 4 px, the value at its widest, 5 px. twin: the value in another colour, shown while `below`
    (a trigger) holds; for a resource also the game's crossed icon."""
    return {"name": name, "group": group, "label": label, "width": width, "sprite": sprite, "frame": frame, "scale": scale,
            "icon": (icon_w, icon_h), "text_x": text_x, "text_w": width - text_x - 5, "value": value, "tip": tip,
            "default": default, "twin": twin, "below": below}


def tb_idle(variable):
    return "check_variable = { %s > 0 }" % variable


# The catalogue, in the order the chips stand. Every value is in the game's documentation folder: the dynamic
# variables political_power_daily, command_power_daily, num_of_*_factories, num_of_available_*_factories,
# num_of_civilian_factories_available_for_projects, fuel_k, max_fuel_k, deployed_total_manpower_k,
# amount_manpower_in_deployment_queue, resource@<r> and modifier@<m>; stability_weekly, war_support_weekly and
# consumer_goods_factor are modifiers.
TB_CHIPS = [
    tb_chip("pp", "Gains", "Political power per day", 90, "GFX_pol_power_icon", 1, 1.0, 27, 27, 34,
            "[?political_power_daily|+=2]§g/d§!", "Political power you gain each day. The top bar shows the stock.", True),
    tb_chip("cp", "Gains", "Command power per day", 87, "GFX_command_power", 1, 1.0, 24, 22, 31,
            "[?command_power_daily|+=2]§g/d§!", "Command power you gain each day, up to the most you can hold.", True),
    tb_chip("stab", "Gains", "Stability per week", 106, "GFX_stability_icon", 1, 1.0, 27, 24, 34,
            "[?modifier@stability_weekly|+=%1]§g/wk§!",
            "Stability changes by this much each week (the weekly modifiers). The top bar shows where it stands.", True),
    tb_chip("ws", "Gains", "War support per week", 105, "GFX_war_support_icon", 1, 1.0, 26, 24, 33,
            "[?modifier@war_support_weekly|+=%1]§g/wk§!",
            "War support changes by this much each week (the weekly modifiers). The top bar shows where it stands.", True),
    tb_chip("civ", "Factories", "Civilian factories, free", 119, "GFX_civ_factory", 1, 1.2, 22, 22, 29,
            "[?num_of_civilian_factories|0]  §g[?num_of_civilian_factories_available_for_projects|0] free§!",
            "Civilian factories, and how many are free for construction once consumer goods and trade have taken theirs.", True),
    tb_chip("mil", "Factories", "Military factories, idle", 115, "GFX_mil_factory", 1, 1.2, 22, 22, 29,
            "[?num_of_military_factories|0]  §g[?num_of_available_military_factories|0] idle§!",
            "Military factories, and how many have no production line. Yellow while any stands idle.", True,
            twin="[?num_of_military_factories|0]  §Y[?num_of_available_military_factories|0] idle§!",
            below=tb_idle("num_of_available_military_factories")),
    tb_chip("dock", "Factories", "Dockyards, idle", 107, "GFX_nav_dockyard_texticon", 1, 1.1, 22, 22, 29,
            "[?num_of_naval_factories|0]  §g[?num_of_available_naval_factories|0] idle§!",
            "Dockyards, and how many have no production line. Yellow while any stands idle.", True,
            twin="[?num_of_naval_factories|0]  §Y[?num_of_available_naval_factories|0] idle§!",
            below=tb_idle("num_of_available_naval_factories")),
    tb_chip("cg", "Factories", "Consumer goods", 74, "GFX_consumer_goods_texticon", 1, 1.0, 20, 20, 27,
            "[?modifier@consumer_goods_factor|%1]", "Consumer goods: the share of your civilian factories that the people's needs take.", False),
    tb_chip("fuel", "Fuel", "Fuel in store", 128, "GFX_fuel_state", 1, 1.0, 26, 24, 33,
            "[?fuel_k|0]K§g/[?max_fuel_k|0]K§!",
            "Fuel in store, of what your silos and refineries can hold. The top bar shows how long it lasts.", True),
    tb_chip("mp_field", "Manpower", "Manpower in the field", 119, "GFX_manpower_icon", 1, 0.9, 24, 24, 31,
            "[?deployed_total_manpower_k|0]K§g field§!", "Men in your divisions, ships and air wings.", False),
    tb_chip("mp_train", "Manpower", "Manpower in training", 139, "GFX_manpower_icon", 1, 0.9, 24, 24, 31,
            "[?amount_manpower_in_deployment_queue|*1]§g training§!", "Men of the divisions in training.", False),
] + [tb_chip("res_" + res, "Resources", TB_RES_NAMES[r], 61, "GFX_resources_strip", r + 1, 0.7, 19, 19, 26,
             "[?resource@%s|0]" % res, TB_RES_TIP % TB_RES_NAMES[r], False,
             twin="§R[?resource@%s|0]§!" % res, below="check_variable = { resource@%s < 0 }" % res)
     for r, res in enumerate(RESOURCES)]
TB_DEFAULT = [c["name"] for c in TB_CHIPS if c["default"]]


def tb_place(on):
    """What mod1440_tb_place does, for the .gui positions and the scenes: in catalogue order each chip that is on
    stands at the cursor, which then moves by the chip's width and 4, or 16 where the group changes. Returns the
    right end (px used) and the x of each chip in the strip's container."""
    x, last, out = 0, None, {}
    for c in TB_CHIPS:
        if c["name"] not in on:
            continue
        if last is not None:
            x += TB_GAP if c["group"] == last else TB_GROUP_GAP
        out[c["name"]] = x
        x += c["width"]
        last = c["group"]
    return x, out


def tb_icon(name, x, y, sprite, frame=None, scale=None, tooltip=None, transparent=False):
    extra = (" frame = %d" % frame if frame else "") + (" scale = %s" % scale if scale and scale != 1.0 else "")
    extra += ' pdx_tooltip = "%s"' % tooltip if tooltip else ""
    extra += " alwaystransparent = yes" if transparent else ""
    return 'iconType = { name = "%s" position = { x = %d y = %d } spriteType = "%s"%s }\n' % (name, x, y, sprite, extra)


def tb_icon_dy(c):
    """The icon in the middle of the box's height, never above the band's interior (screen y 3)."""
    return max((TB_H - c["icon"][1]) // 2, -1)


def tb_parts(c, x):
    """Where each widget of a chip stands with its box at x: {widget suffix: (x, y)}."""
    n = c["name"]
    icon = (x + TB_PAD_L, TB_BOX_Y + tb_icon_dy(c))
    value = (x + c["text_x"], TB_TEXT_Y)
    parts = {n + "_bg": (x, TB_BOX_Y), n + "_icon": icon, n: value}
    if c["twin"]:
        parts[n + ("_neg" if n.startswith("res_") else "_idle")] = value
    if n.startswith("res_"):
        parts[n + "_miss"] = icon
    return parts


def tb_widgets(prefix, c, x):
    """The widgets of one chip, named <prefix>_<chip>..., with the box at x."""
    n = c["name"]
    tip = B.key("tb_%s_tt" % n, c["tip"])
    pos = tb_parts(c, x)
    out = tb_icon("%s_%s_bg" % (prefix, n), pos[n + "_bg"][0], pos[n + "_bg"][1], "GFX_1440p_SG_topbox_%dx%d" % (c["width"], TB_H), tooltip=tip)
    out += tb_icon("%s_%s_icon" % (prefix, n), pos[n + "_icon"][0], pos[n + "_icon"][1], c["sprite"], c["frame"], c["scale"], tooltip=tip)
    if n.startswith("res_"):
        out += tb_icon("%s_%s_miss" % (prefix, n), pos[n + "_miss"][0], pos[n + "_miss"][1], "GFX_missing_resources_strip", c["frame"], c["scale"], tooltip=tip)
    out += text("%s_%s" % (prefix, n), pos[n][0], pos[n][1], c["text_w"], B.key("tb_%s" % n, c["value"]), FONT_LABEL, height=22, tooltip=tip, fixed=True)
    if c["twin"]:
        twin = n + ("_neg" if n.startswith("res_") else "_idle")
        out += text("%s_%s" % (prefix, twin), pos[twin][0], pos[twin][1], c["text_w"], B.key("tb_%s" % twin, c["twin"]), FONT_LABEL, height=22, tooltip=tip, fixed=True)
    return out


def tb_triggers(prefix, c, on):
    """What shows of a chip: everything while its switch is on (on: a trigger, or "" for the fixed twin); a value
    with a twin shows the one its trigger asks for."""
    n = c["name"]
    shown = on + "\n" if on else ""
    out = block("%s_%s_bg_visible" % (prefix, n), shown) if on else ""
    if c["twin"]:
        twin = n + ("_neg" if n.startswith("res_") else "_idle")
        out += block("%s_%s_visible" % (prefix, n), shown + "NOT = { %s }\n" % c["below"])
        out += block("%s_%s_visible" % (prefix, twin), shown + c["below"] + "\n")
    elif on:
        out += block("%s_%s_visible" % (prefix, n), shown)
    if n.startswith("res_"):
        out += block("%s_%s_icon_visible" % (prefix, n), shown + "NOT = { %s }\n" % c["below"])
        out += block("%s_%s_miss_visible" % (prefix, n), shown + c["below"] + "\n")
    elif on:
        out += block("%s_%s_icon_visible" % (prefix, n), shown)
    return out


def tb_switch(n):
    return "check_variable = { mod1440_tb_on_%s = 1 }" % n


def tb_refused(c):
    """Off, and less room left than the chip and a group gap need: the most a chip can add to the strip."""
    return "NOT = { %s } check_variable = { mod1440_tb_room < %d }" % (tb_switch(c["name"]), c["width"] + TB_GROUP_GAP)


def tb_strip():
    """The moving strip, its fixed twin and the edit button: three scripted GUIs on the top bar."""
    _right, at = tb_place(TB_DEFAULT)
    body, triggers, properties = "", "", ""
    fixed, fixed_triggers = "", ""
    for c in TB_CHIPS:
        n = c["name"]
        # the .gui places a chip where the defaults put it; script moves it (a chip that is off stands at 0, hidden)
        body += tb_widgets("tb", c, at.get(n, 0))
        triggers += tb_triggers("tb", c, tb_switch(n))
        for suffix, variable in ((("_bg", "x"), ("_icon", "xi"), ("_miss", "xi"), ("", "xt"), ("_idle", "xt"), ("_neg", "xt"))):
            if n + suffix in tb_parts(c, 0):
                properties += block("tb_%s%s" % (n, suffix), "x = mod1440_tb_%s_%s\n" % (variable, n))
        if c["default"]:
            fixed += tb_widgets("tbf", c, at[n])
            fixed_triggers += tb_triggers("tbf", c, "")
    gui = box("mod1440_top_bar_strip", TB_X, TB_Y, TB_ROOM, 28, body)
    gui += box("mod1440_top_bar_fixed", TB_X, TB_Y, TB_ROOM, 28, fixed)
    current = "check_variable = { mod1440_tb_ver = %d }\n" % TB_VER
    script = scripted_gui("mod1440_top_bar_strip", "mod1440_top_bar_strip", "top_bar", visible=current,
                          triggers=triggers, properties=properties)
    script += scripted_gui("mod1440_top_bar_fixed", "mod1440_top_bar_fixed", "top_bar", visible="NOT = { %s }\n" % current.strip(),
                           triggers=fixed_triggers)
    # the edit button: the chip's box as a button with the game's edit-list picture, in a container of its own so
    # that it stays when every chip is off
    ex, ey, ew, eh = TB_EDIT
    edit = button("tb_edit", 0, 0, "GFX_1440p_SG_topbtn_%dx%d" % (ew, eh),
                  tooltip=B.key("tb_edit_tt", "Choose the values of this strip."))
    edit += tb_icon("tb_edit_icon", (ew - 22) // 2, (eh - 22) // 2, "GFX_edit_list_icon", transparent=True)
    gui += box("mod1440_top_bar_edit", ex, ey, ew, eh, edit)
    script += scripted_gui("mod1440_top_bar_edit", "mod1440_top_bar_edit", "top_bar", effects=block(
        "tb_edit_click", iff("NOT = { %s }" % current.strip(), "mod1440_tb_default = yes\n") + flip("mod1440_tb_setup")))
    return gui, script


TB_CARD_Y, TB_CARD_W, TB_CARD_GAP, TB_MARGIN = 84, 400, 14, 14
TB_HEAD_H, TB_ROW = 30, 32


def tb_rows():
    """Each value's row in the panel: (chip, card x, row y), relative to the panel; and the cards' height."""
    rows, heights = [], []
    for col, groups in enumerate(TB_COLUMNS):
        cx = TB_MARGIN + col * (TB_CARD_W + TB_CARD_GAP)
        y = TB_CARD_Y + 8
        for group in groups:
            rows.append((None, cx, y, group))
            y += TB_HEAD_H + 2
            for c in TB_CHIPS:
                if c["group"] == group:
                    rows.append((c, cx, y, group))
                    y += TB_ROW
        heights.append(y - TB_CARD_Y)
    return rows, max(heights) + 8


def tb_panel():
    """The panel of the edit button: the width used, the eighteen values in five groups with their width and a
    switch, Default and close."""
    rows, card_h = tb_rows()
    foot_y = TB_CARD_Y + card_h + 12
    height = foot_y + 34 + 14
    body = box("tb_head", 3, 3, TB_PANEL_W - 6, 44, "", "GFX_tiled_header")
    body += text("tb_title", 16, 11, 500, B.key("tb_title", "Top bar values"), FONT_CARD, height=30)
    body += button("tb_close", TB_PANEL_W - 50, 8, "GFX_closebutton", shortcut="ESCAPE", tooltip=B.key("tb_close_tt", "Close"))
    body += icon("tb_used_bar", 16, 60, bar_sprite(300))
    body += text("tb_used", 330, 56, TB_PANEL_W - 330 - 16, B.key(
        "tb_used", "[?mod1440_tb_used|0] of %d px used, [?mod1440_tb_room|0] left. A value that needs more stays off." % TB_ROOM), FONT_SMALL, height=20)
    properties = block("tb_used_bar", "frame = mod1440_tb_used_pct\n")
    triggers, effects = "", ""
    for col in range(len(TB_COLUMNS)):
        body += box("tb_card_%d" % col, TB_MARGIN + col * (TB_CARD_W + TB_CARD_GAP), TB_CARD_Y, TB_CARD_W, card_h, "", CARD_BG)
    n_in_group = 0
    for c, cx, y, group in rows:
        if c is None:
            body += heads("tb_head_%d" % TB_GROUPS.index(group), cx + 8, y, TB_CARD_W - 16, [
                (8, 200, group, "left", None), (242, 60, "Width", "left", None), (322, 60, "Shown", "left", None)])
            n_in_group = 0
            continue
        n = c["name"]
        if n_in_group % 2:
            body += icon("tb_s_%s_stripe" % n, cx + 8, y, STRIPE % (TB_CARD_W - 16, TB_ROW))
        n_in_group += 1
        tip = B.key("tb_%s_tt" % n, c["tip"])
        # the chip's icon at most 24 px high, in the middle of a 26 px column
        k = min(1.0, 24.0 / c["icon"][1])
        w, h = int(round(c["icon"][0] * k)), int(round(c["icon"][1] * k))
        body += tb_icon("tb_s_%s_icon" % n, cx + 16 + (26 - w) // 2, y + (TB_ROW - h) // 2, c["sprite"], c["frame"], round(c["scale"] * k, 3), tooltip=tip)
        label = B.key("tb_s_%s" % n, c["label"])
        body += text("tb_s_%s_name" % n, cx + 50, y + 5, 220, label, FONT_LABEL, height=22, tooltip=tip, fixed=True)
        body += text("tb_s_%s_name_off" % n, cx + 50, y + 5, 220, B.key("tb_s_%s_grey" % n, "§g%s§!" % c["label"]), FONT_LABEL, height=22, tooltip=tip, fixed=True)
        need = c["width"] + TB_GROUP_GAP
        need_tip = B.key("tb_s_%s_need_tt" % n, "Needs %d px of the strip: %d for the value and up to %d between groups. "
                         "[?mod1440_tb_room|0] px are left; turn another value off first." % (need, c["width"], TB_GROUP_GAP))
        body += text("tb_s_%s_w" % n, cx + 230, y + 7, 70, B.key("tb_s_w_%d" % c["width"], "§g%d px§!" % c["width"]), FONT_SMALL, "right", 20)
        body += text("tb_s_%s_w_off" % n, cx + 230, y + 7, 70, B.key("tb_s_w_%d_off" % c["width"], "§R%d px§!" % c["width"]), FONT_SMALL, "right", 20, tooltip=need_tip)
        # the switch: the game's gold box, empty while the value is off, ticked while it is on (two buttons, X4)
        body += ('buttonType = { name = "tb_s_%s_off" position = { x = %d y = %d } quadTextureSprite = "GFX_checkbox_gold_32" frame = 1 '
                 'clicksound = click_default pdx_tooltip = "%s" }\n' % (n, cx + 338, y, B.key("tb_s_%s_on_tt" % n, "Show %s on the top bar. It needs %d px of the strip; a value that does not fit stays off." % (c["label"].lower() if not n.startswith("res_") else c["label"], need))))
        body += ('buttonType = { name = "tb_s_%s_on" position = { x = %d y = %d } quadTextureSprite = "GFX_checkbox_gold_32" frame = 2 '
                 'clicksound = click_default pdx_tooltip = "%s" }\n' % (n, cx + 338, y, B.key("tb_s_off_tt", "Take this value off the top bar.")))
        refused = tb_refused(c)
        triggers += block("tb_s_%s_name_visible" % n, "NOT = { AND = { %s } }\n" % refused)
        triggers += block("tb_s_%s_name_off_visible" % n, refused + "\n")
        triggers += block("tb_s_%s_w_visible" % n, "NOT = { AND = { %s } }\n" % refused)
        triggers += block("tb_s_%s_w_off_visible" % n, refused + "\n")
        triggers += block("tb_s_%s_off_visible" % n, "NOT = { %s }\n" % tb_switch(n))
        triggers += block("tb_s_%s_off_click_enabled" % n, "NOT = { check_variable = { mod1440_tb_room < %d } }\n" % need)
        triggers += block("tb_s_%s_on_visible" % n, tb_switch(n) + "\n")
        effects += block("tb_s_%s_off_click" % n, setv("mod1440_tb_on_%s" % n, 1) + "mod1440_tb_place = yes\n")
        effects += block("tb_s_%s_on_click" % n, setv("mod1440_tb_on_%s" % n, 0) + "mod1440_tb_place = yes\n")
    body += button("tb_default", 16, foot_y, "GFX_button_123x34", B.key("tb_default", "Default"), tooltip=B.key(
        "tb_default_tt", "The eight values the strip starts with: political power and command power per day, stability and "
                         "war support per week, the three kinds of factories, and fuel."))
    body += text("tb_foot", 156, foot_y + 8, TB_PANEL_W - 156 - 16, B.key(
        "tb_foot", "§gThe values stand in the order of this list. Your choice is kept with your country.§!"), FONT_SMALL, height=20)
    effects += block("tb_close_click", setv("mod1440_tb_setup", 0))
    effects += block("tb_default_click", "mod1440_tb_default = yes\n")
    gui = box("mod1440_top_bar_setup", TB_PANEL_X, TB_PANEL_Y, TB_PANEL_W, height, body, PAGE_BG)
    script = scripted_gui("mod1440_top_bar_setup", "mod1440_top_bar_setup", "top_bar", visible=is_one("mod1440_tb_setup") + "\n",
                          effects=effects, triggers=triggers, properties=properties)
    return gui, script, height


def tb_effects():
    """mod1440_tb_place: the x of every chip that is on, the width used and the room left; mod1440_tb_default:
    the eight defaults on, the rest off. Both run on a click, on the first day of a save without them, and once
    at the start of a game."""
    place = tmp("tb_c", 0) + tmp("tb_g", 0)
    for c in TB_CHIPS:
        n, g = c["name"], TB_GROUPS.index(c["group"]) + 1
        place += iff(tb_switch(n), (
            iff("check_variable = { tb_g = %d }" % g, "add_to_temp_variable = { tb_c = %d }\n" % TB_GAP)
            + iff("check_variable = { tb_g > 0 }", "add_to_temp_variable = { tb_c = %d }\n" % TB_GROUP_GAP, "else_if")
            + setv("mod1440_tb_x_%s" % n, "tb_c")
            + setv("mod1440_tb_xi_%s" % n, "tb_c") + "add_to_variable = { mod1440_tb_xi_%s = %d }\n" % (n, TB_PAD_L)
            + setv("mod1440_tb_xt_%s" % n, "tb_c") + "add_to_variable = { mod1440_tb_xt_%s = %d }\n" % (n, c["text_x"])
            + "add_to_temp_variable = { tb_c = %d }\n" % c["width"] + tmp("tb_g", g)))
    place += setv("mod1440_tb_used", "tb_c") + setv("mod1440_tb_room", TB_ROOM) + "subtract_from_variable = { mod1440_tb_room = tb_c }\n"
    place += (setv("mod1440_tb_used_pct", "tb_c") + "multiply_variable = { mod1440_tb_used_pct = 100 }\n"
              + "divide_variable = { mod1440_tb_used_pct = %d }\n" % TB_ROOM)
    default = "".join(setv("mod1440_tb_on_%s" % c["name"], 1 if c["default"] else 0) for c in TB_CHIPS)
    default += setv("mod1440_tb_ver", TB_VER) + "mod1440_tb_place = yes\n"
    # the effect that another one calls stands first in the file (Engine Facts X70)
    return block("mod1440_tb_place", place) + "\n" + block("mod1440_tb_default", default)


def tb_daily():
    """A save of an earlier build, or a country the player takes over later: the defaults on the next day."""
    return iff("NOT = { check_variable = { mod1440_tb_ver = %d } }" % TB_VER, "mod1440_tb_default = yes\n")


def top_bar():
    gui, script = tb_strip()
    panel_gui, panel_script, _height = tb_panel()
    return gui + panel_gui, script + panel_script, tb_effects()


# The scene: samples of Germany on 1 January 1936 where they are known (35, 28 and 10 factories, 8 military
# factories idle, fuel 297K of 371K, the resource balance D4 checked), the others as the design drew them.
TB_SAMPLES = {
    "pp": "§G+2.00§!§g/d§!", "cp": "§G+0.85§!§g/d§!", "stab": "§G+0.2%§!§g/wk§!", "ws": "§G+0.3%§!§g/wk§!",
    "civ": "35  §g3 free§!", "mil": "28  §g8 idle§!", "mil_idle": "28  §Y8 idle§!", "dock": "10  §g0 idle§!", "dock_idle": "10  §Y0 idle§!",
    "cg": "25.0%", "fuel": "297K§g/371K§!", "mp_field": "1310K§g field§!", "mp_train": "38.4K§g training§!",
}
for _r, (_res, _value) in enumerate(zip(RESOURCES, ["3", "104", "-5", "3", "177", "1", "195"])):
    TB_SAMPLES["res_" + _res] = _value
    TB_SAMPLES["res_%s_neg" % _res] = "§R%s§!" % _value
TB_CHOSEN = ["pp", "stab", "ws", "civ", "mil", "dock", "res_oil", "res_rubber", "res_steel"]   # figure custom-chosen-detail


def tb_strip_hide(on, below=()):
    """What script hides of the moving strip with these values on; below: the chips whose twin shows (8 military
    factories idle; rubber below 0)."""
    hide = []
    for c in TB_CHIPS:
        n = c["name"]
        parts = list(tb_parts(c, 0))
        if n not in on:
            hide += ["tb_" + p for p in parts]
        elif c["twin"]:
            twin = n + ("_neg" if n.startswith("res_") else "_idle")
            hide += ["tb_" + (n if n in below else twin)]
            if n.startswith("res_"):
                hide += ["tb_" + n + ("_icon" if n in below else "_miss")]
    return hide


def tb_panel_hide(on):
    used, _at = tb_place(on)
    hide = []
    for c in TB_CHIPS:
        n = c["name"]
        refused = n not in on and TB_ROOM - used < c["width"] + TB_GROUP_GAP
        hide.append("tb_s_%s_%s" % (n, "off" if n in on else "on"))
        hide += ["tb_s_%s_name" % n, "tb_s_%s_w" % n] if refused else ["tb_s_%s_name_off" % n, "tb_s_%s_w_off" % n]
    return hide


def tb_used_sample(on):
    used, _at = tb_place(on)
    return "%d of %d px used, %d left. A value that needs more stays off." % (used, TB_ROOM, TB_ROOM - used)


def tb_scene():
    right, at = tb_place(TB_DEFAULT)
    chosen_right, chosen_at = tb_place(TB_CHOSEN)
    # the design measured these (scratch/phases/D7/custom-layout.json): the build must stand where it drew them
    assert (right, [TB_X + at[n] for n in TB_DEFAULT]) == (909, [1042, 1136, 1227, 1337, 1458, 1581, 1700, 1823]), at
    assert chosen_right == 881, chosen_right
    assert right <= TB_ROOM
    samples = {"tb_" + k: v for k, v in TB_SAMPLES.items()}
    place = {}
    for n, x in chosen_at.items():
        c = next(c for c in TB_CHIPS if c["name"] == n)
        for part, (px, py) in tb_parts(c, x).items():
            place["tb_" + part] = [px, py]
    strip_states = ["", "panel", "escape", "chosen"]
    windows = [
        {"name": "mod1440_top_bar_strip", "at": [TB_X, TB_Y], "drawIn": strip_states,
         "hide": tb_strip_hide(TB_DEFAULT, below=("mil",)),
         "_note": "The moving strip with its eight defaults. Script shows the yellow twin of military factories (8 idle) and the grey dockyards (0 idle), and hides the ten values that are off."},
        {"name": "mod1440_top_bar_fixed", "at": [TB_X, TB_Y], "drawIn": ["old_save"], "hide": ["tbf_mil", "tbf_dock_idle"],
         "_note": "The fixed twin: the eight defaults at fixed places, shown instead of the moving strip in a save of an earlier build until the first click on the edit button or the next day."},
        {"name": "mod1440_top_bar_edit", "at": [TB_EDIT[0], TB_EDIT[1]]},
        {"name": "mod1440_records_handle", "at": [2002, 3], "_note": "From mod1440_records.gui (tools/build_records.py): moved to the right end and lowered to 28 px in D7."},
        {"name": "mod1440_top_bar_setup", "at": [TB_PANEL_X, TB_PANEL_Y], "drawIn": ["panel", "chosen"], "hide": tb_panel_hide(TB_DEFAULT),
         "_note": "The panel of the edit button, shown while mod1440_tb_setup is 1. With the defaults 3 px are left, so every value that is off is refused."},
    ]
    return {
        "phase": "D7", "file": "mod1440_top_bar.gui", "screenshot": "reference/vanilla/politics.jpg",
        "windows": windows,
        "samples": {"mod1440_top_bar_strip": samples, "mod1440_top_bar_fixed": {"tbf_" + k: v for k, v in TB_SAMPLES.items()},
                    "mod1440_top_bar_setup": {"tb_used": tb_used_sample(TB_DEFAULT)}},
        "setup": [{"wait": 1.0, "_note": "the clean state: the strip is on the top bar of every screen"}],
        "captures": [
            {"name": "panel", "steps": [{"clickWidget": "mod1440_top_bar_edit/tb_edit", "wait": 1.2}]},
            {"name": "escape", "steps": [{"key": "escape", "wait": 1.0, "_note": "the panel's close button takes Escape (SGUI-008); the game menu must not open"}]},
        ],
        "states": [
            {"name": "chosen", "_note": "Another choice, drawn by the renderer only (figure custom-chosen-detail of the design): command power and fuel off, oil, rubber (below 0, red with the crossed icon) and steel on; the panel open over it, 31 px left, so every value that is off is refused.",
             "hide": {"mod1440_top_bar_strip": tb_strip_hide(TB_CHOSEN, below=("mil", "res_rubber")),
                      "mod1440_top_bar_setup": tb_panel_hide(TB_CHOSEN)},
             "place": {"mod1440_top_bar_strip": place},
             "samples": {"mod1440_top_bar_setup": {"tb_used": tb_used_sample(TB_CHOSEN)}}},
            {"name": "old_save", "_note": "A save of a build before D7, until the first click on the edit button or the next day: the fixed twin of the eight defaults."},
        ],
        "expect": ["mod1440_top_bar_strip/tb_mil_bg", "mod1440_top_bar_strip/tb_fuel_bg", "mod1440_top_bar_edit/tb_edit", "mod1440_records_handle/rec_toggle"],
        "crop": [1030, 0, 1130, 600],
        "manual": [
            "Every value against the game's own number (Scripted GUIs rule 3); hover the tooltips",
            "A save of a build before D7: the fixed twin until the first click on the edit button or the next day",
            "A switch and the chips moving (a capture shows one state; the checker clicks a switch by hand in an open game, or the user does)",
            "A country with nuclear bombs: the nukes counter (x 970 to 1026) stays clear of the strip",
        ],
        "checklist": TB_CHECKLIST,
    }


TB_CHECKLIST = [
    "The strip stands inside the top bar's dark band: the chips' boxes at y 4 to 29 (or 6 to 31 if the 2 px of SGUI-007 apply), never on the band's lower edge (y 32 to 35) or the alerts row (y 40); measure in the 1:1 capture",
    "Eight chips from x 1042 to 1951 in this order: political power per day, command power per day, stability per week, war support per week, civilian factories (free), military factories (idle), dockyards (idle), fuel; then the edit button at 1970 and the Records handle at 2002 to 2152, 28 px high, clear of the clock plate (2168)",
    "Political power per day against the political power tooltip of the top bar",
    "Command power per day against the command power tooltip",
    "Stability and war support per week against the weekly change in their tooltips (the chip reads the modifiers stability_weekly and war_support_weekly; the tooltip may also apply a weekly factor)",
    "Civilian factories and free against the factory tooltip of the top bar (35, and the free ones once consumer goods and trade have taken theirs)",
    "Military factories and idle against the factory tooltip and the production screen (28 and 8 idle for Germany 1936): the idle count yellow while above 0; dockyards 10 and 0 idle, grey",
    "Fuel against the fuel tooltip of the top bar (297K of 371K for Germany 1936)",
    "Hover every chip: its tooltip names the value and says what the number means",
    "The edit button opens the panel at 1310,40 (842x544) under the band, clear of the alerts row; Escape and the close button close it, and Escape does not open the game menu",
    "With the defaults the panel says 909 of 912 px used, 3 left: every value that is off is refused (dimmed box, grey name, red width; its tooltip names the room it needs)",
    "Untick command power: the six chips after it move 91 px left at once, 94 px are left, and consumer goods and the seven resources become free to tick; tick oil: it stands after fuel with its own icon",
    "Consumer goods, manpower in the field and in training, and each resource against the game's numbers (production tab, Recruit & Deploy, trade tab) once ticked",
    "Default brings the eight back, in their places; the choice survives a save and a load",
    "error.log names no mod1440 file and has no Could not find sprite type line for a GFX_1440p_SG_topbox, topbtn or button_150x28 sprite",
]

# ---------------------------------------------------------------- scenes: what the renderer and the harness need

# One scene per page (tools/scenes/<name>.json, see wiki/Game-Recipes.md): where the page stands on the screen,
# the recipe that brings it up, the widgets that prove it is up, and a sample for every text that holds a
# value, so that the renderer draws numbers and the tests measure them against their boxes.
SCENES = {
    "army_readiness": {
        "phase": "D2", "file": "mod1440_army_readiness.gui", "screenshot": "reference/vanilla/recruit_deploy.jpg",
        "windows": [
            {"name": "mod1440_army_readiness", "at": [1250, 78], "sidePanel": True,
             "hide": ["ar_full"] + ["ar_%s_z" % n for n in ("mp_training", "mp_garrison", "low_str", "low_org")] + ["ar_fuel_low"],
             "_note": "The head: title strip and figures, the whole page in its short form. Docked to Recruit & Deploy: the tab's corner at -6,78 plus the container's 1256,0. Hidden here: the twin of a value that script shows in its place (a plain 0, an orange bar, the Full button of the short form)."},
            {"name": "mod1440_army_readiness_body", "at": [1250, 78 + AR_SUM_H], "sidePanel": True,
             "rows": {"ar_eq_grid": AR_EQ_ROWS, "ar_al_grid": AR_AL_ROWS},
             "listRows": {"ar_eq_grid": "mod1440_army_readiness_eqrow", "ar_al_grid": "mod1440_army_readiness_row"},
             "hide": ["ar_eq_none", "ar_al_none"],
             "_note": "The body, under the head while the page is in its full form: the equipment and the armies."},
            {"name": "mod1440_army_readiness_eqrow", "skip": True,
             "hide": ["ar_er_field", "ar_er_short_covered", "ar_er_low"] + ["ar_er_pic_%d" % n for n in range(len(AR_SCALES)) if n != ar_scale(81, 23, AR_PIC_BOX)],
             "_note": "A row per kind in use. The renderer draws one sprite and one fill for every row: in the game each row has the picture of its kind at its scale, and a bar of its share."},
            {"name": "mod1440_army_readiness_row", "skip": True,
             "hide": (["ar_row_gen", "ar_row_unknown", "ar_row_hq_none", "ar_row_fight_none", "ar_row_low"]
                      + ["ar_row_%s_none" % n for n in ("inf", "arm", "mot", "mech")]
                      + ["ar_row_worst_%d" % n for n in range(len(AR_SCALES)) if n != ar_scale(81, 23, AR_WORST_BOX)])},
        ],
        # sample rows of a mobilising Germany, as on the design page (one text per row, in drawing order)
        "samples": {
            "mod1440_army_readiness": {"ar_fuel": "297K of 371K", "ar_mp_free": "1332K", "ar_mp_training": "38.4K", "ar_low_str": "§Y6§!", "ar_low_org": "§Y2§!", "ar_xp": "37", "ar_mp_army": "1310K", "ar_divisions": "172", "ar_battalions": "1650"},
            "mod1440_army_readiness_body": {
                "ar_eq_caption": "§g9 of %d kinds in use, the worst equipped first§!" % len(AR_KINDS),
                "ar_al_caption": "§g12 commanders with troops; a click on HQ moves the camera there§!"},
            "mod1440_army_readiness_eqrow": {
                "ar_er_name": ["$%s$" % k for k in ("light_tank_chassis", "support_equipment", "artillery_equipment", "infantry_equipment",
                                                     "motorized_equipment", "anti_tank_equipment", "armored_car_equipment",
                                                     "anti_air_equipment", "medium_tank_chassis")],
                "ar_er_stock": ["0", "40", "120", "21400", "1200", "310", "0", "140", "12"],
                "ar_er_field_short": ["\u00a7R1450\u00a7!", "\u00a7R2280\u00a7!", "\u00a7R3790\u00a7!", "\u00a7R79100\u00a7!", "\u00a7R2900\u00a7!", "1080", "288", "0", "0"],
                "ar_er_need": ["2160", "3150", "4420", "86400", "3100", "1080", "288", "0", "0"],
                "ar_er_short": ["\u00a7R710\u00a7!", "\u00a7R870\u00a7!", "\u00a7R630\u00a7!", "\u00a7O7300\u00a7!", "\u00a7O200\u00a7!", "", "", "", ""],
                "ar_er_pct": ["67%", "72%", "85%", "91%", "93%", "100%", "100%", "", ""],
            },
            "mod1440_army_readiness_row": {
                "ar_row_name": ["\u00a7Y%s\u00a7!" % n for n in ("Gerd von Rundstedt", "Fedor von Bock", "Heinz Guderian", "Erich von Manstein",
                                                       "Wilhelm Ritter von Leeb", "G\u00fcnther von Kluge", "Johannes Blaskowitz",
                                                       "Erwin von Witzleben", "Wilhelm List", "Kurt von Hammerstein")],
                "ar_row_fm": ["\u00a7gField Marshal\u00a7!"] * 2 + ["\u00a7gGeneral\u00a7!"] * 8,
                "ar_row_skill": ["\u00a7gSkill\u00a7! %d" % n for n in (4, 4, 4, 4, 3, 3, 3, 3, 3, 2)],
                "ar_row_hq_name": ["Schlesien", "Pommern", "Ostpreussen", "Schlesien", "Westfalen", "Brandenburg", "Sachsen", "Rheinland", "Bayern", "Hessen"],
                "ar_row_div": ["36", "30", "8", "12", "14", "12", "10", "8", "6", "4"],
                "ar_row_inf": ["30", "24", "2", "11", "14", "11", "10", "8", "6", "4"],
                "ar_row_arm": ["2", "3", "4"] + ["\u00a7g-\u00a7!"] * 7,
                "ar_row_mot": ["4", "3", "2", "1", "\u00a7g-\u00a7!", "1"] + ["\u00a7g-\u00a7!"] * 4,
                "ar_row_mech": ["\u00a7g-\u00a7!"] * 10,
                "ar_row_fight": ["\u00a7g-\u00a7!", "\u00a7g-\u00a7!", "\u00a7Y3\u00a7!"] + ["\u00a7g-\u00a7!"] * 7,
                "ar_row_split": ["", "", "\u00a7g2 att, 1 def\u00a7!"] + [""] * 7,
                "ar_row_plan": ["100%", "85%", "42%", "100%", "64%", "100%", "90%", "30%", "100%", "0%"],
                "ar_row_pct": ["72%", "67%", "61%", "86%", "84%", "91%", "93%", "95%", "97%", "100%"],
            },
        },
        "setup": [{"move": "open_recruit_deploy"}],
        "expect": ["mod1440_army_readiness/ar_fold", "mod1440_army_readiness/ar_count", "mod1440_army_readiness/ar_small"],
        "crop": [1240, 70, 1000, 1230],
        "manual": ["The page after a day has passed: the counts and the bars come from a daily hook, which no check runs",
                   "A commander with a deployed headquarters, and one fighting: a 1936 start has none"],
        "checklist": [
            "Shift+M hides the page and brings it back in the form it was left in; the handle beside the template panel does the same",
            "Summary folds the page to its title strip and figures, with no seam left where the body was; Full brings the body back under them",
            "The equipment card lists only the kinds you have or need, the worst equipped first, each with the game's picture of the kind at a size that fits its row",
            "Short is red where the stock cannot fill the gap and orange where it can; In the field is red where it is short",
            "Fuel reads the top bar's fuel (297K of 371K for Germany in 1936) and its bar is that share",
            "Assign a general to an army, press Count again: the general is listed under Armies with his portrait, rank and skill",
            "Deploy his HQ: the HQ button names its state and a click moves the camera there; without one it reads not deployed",
            "Inf, Arm, Mot and Mech against the army badge; Worst kind shows a picture and its share",
            "Train a division: In training rises at once; In stock falls at the next count",
            "error.log names no mod1440 file and has no Could not find sprite type line for an archetype picture",
        ],
    },
    "states": {
        "phase": "D3", "file": "mod1440_states.gui", "screenshot": "reference/vanilla/construction.jpg",
        "windows": [
            {"name": "mod1440_states", "at": [703, 78], "sidePanel": True,
             "rows": {"st_grid": 24, "st_card_grid": 1},
             "listRows": {"st_grid": "mod1440_states_row", "st_card_grid": "mod1440_states_card"},
             "hide": ["st_arrow_up", "st_arrow_down", "st_c_none"] + ["st_c_mod_%d_z" % n for n in (0, 1)] + ["st_c_mod_2"],
             "_note": "Docked to Construction: the tab's corner at -9,78 plus the container's 712,0. The vanilla window has clipping = no. The band under the table is a list of one row, the chosen state; the third modifier is 0 for Germany in 1936 and shows its grey dash."},
            {"name": "mod1440_states_row", "skip": True,
             "hide": ["st_row_occ", "st_row_chosen", "st_row_held", "st_row_held_chosen", "st_row_flag", "st_row_pick"]
                     + ["st_cell_%s_dmg" % c[0] for c in STATE_COLUMNS if c[5] == "build"] + ["st_cell_compliance", "st_cell_resistance"],
             "_note": "Every row is drawn as a core of yours that is not the chosen one: script shows the other names, the flag, the mark of the chosen row and the red levels instead where they apply."},
            {"name": "mod1440_states_card", "skip": True,
             "hide": (["st_c_where_cap", "st_c_owner_owned", "st_c_owner_held", "st_c_taken", "st_c_chip_noncore", "st_c_chip_occupied",
                       "st_c_chip_coastal", "st_c_chip_capital", "st_c_chip_island", "st_c_chip_dmz", "st_c_chip_border",
                       "st_c_sh_other", "st_c_dmg", "st_c_bombed", "st_c_sh_civ_z", "st_c_sh_mil_z"]
                      + ["st_c_sh_%s" % n for n in ("dock", "refinery", "silo")]
                      + ["st_c_res_%d" % n for n in range(6)] + ["st_c_res_6_z"]
                      + ["st_c_b_%s_z" % n for n in ("infra", "civ", "mil")]
                      + ["st_c_b_%s" % n for n in ("dock", "refinery", "silo", "air", "aa", "radar")]
                      + ["st_c_b_%s_dmg" % n for n in ST_BUILDING]
                      + ["st_c_occ_%s%s" % (n, part) for n in ("compliance", "resistance", "target") for part in ("", "_l")]),
             "_note": "The band as Hessen shows it on 1 January 1936: a core, inland, six of nine slots free, coal its only resource, nothing damaged."},
        ],
        "setup": [{"move": "open_construction"}, {"key": "shift+m", "wait": 1.5, "_note": "the page is hidden until asked for"}],
        # A left click on the fourth row chooses it; a right-click on the third moves the camera and hides the page;
        # Shift+M brings the page back with the fourth still chosen. The teardown then hides it as before.
        "captures": [
            {"name": "pick", "steps": [{"clickWidget": "mod1440_states_row/st_row#3", "wait": 1.2}]},
            {"name": "goto", "steps": [{"clickWidget": "mod1440_states_row/st_row#2", "button": "right", "wait": 1.5}]},
            {"name": "back", "steps": [{"key": "shift+m", "wait": 1.5}]},
        ],
        "teardown": [{"key": "shift+m", "wait": 0.8, "_note": "hide it again: the page remembers per country whether it is open"}],
        "expect": ["mod1440_states/st_fold", "mod1440_states/st_refresh", "mod1440_states/st_band_slots"],
        "crop": [690, 70, ST_W + 30, 1230],
        "manual": ["A country with occupied states: the Occupied choice, compliance and resistance, the other colour of a name, the owner's flag in the row and the card, the occupation card",
                   "A bombed state: the red levels in its row and card, the line of damage and the day of the last bombing",
                   "Tooltips: the slot bar of a row and of the slots card say that only the game's own shared buildings are counted"],
        "checklist": [
            "The page opens with the first state of the list chosen: its row on the light band, its name yellow, its cards under the table",
            "A left click on another state chooses it: the band and the mark follow, the page stays open",
            "A right-click on a state, and Show on map in the band, move the camera there and hide the page",
            "Sort by a column, choose Cores, press Refresh: the chosen state keeps its mark while it is listed",
            "Hessen against its state view: 6 free of 9 slots, the slot bar a third full, coal 17 (the state view's number), buildings 4, 2, 1",
            "The state card: Capital Frankfurt and Dense Urban Region, Core of the German Reich, the Core and Inland chips",
            "The occupation card: compliance growth -2.0% and resistance target +5.0% as on National Figures, required garrisons a grey dash",
            "A click on a column head sorts, a second click turns the order; State gives the game's order back",
            "The totals against the sum of a column",
        ],
    },
    "national_figures": {
        "phase": "D4", "file": "mod1440_figures.gui", "screenshot": "reference/vanilla/politics.jpg",
        "windows": nf_scene_windows(),
        "setup": [{"move": "open_politics"}, {"key": "shift+m", "wait": 1.5, "_note": "the page is hidden until asked for"}],
        "captures": [{"name": "all", "steps": [{"clickWidget": "mod1440_figures/nf_view_all", "wait": 1.0}]}],
        "teardown": [{"clickWidget": "mod1440_figures/nf_view_applies", "wait": 0.8},
                     {"key": "shift+m", "wait": 0.8, "_note": "hide it again: the page remembers per country whether it is open"}],
        "expect": ["mod1440_figures/nf_fold", "mod1440_figures/nf_view_all", "mod1440_figures/h_zoom"],
        "crop": [540, 64, 1700, 1234],
        "manual": ["The advisor and law picker opened from the panel: it stands above the page",
                   "More than one month: the changes under the tiles and the graph, which no check lets pass"],
        "checklist": [
            "The page stands beside the politics panel and takes clicks; Escape closes Politics and the page with it",
            "Shift+M, the Figures button and the page's close button fold the page; it opens again folded or open as left",
            "What applies lists only modifiers that are not 0; All modifiers lists every one, those that are 0 in grey, and scrolls",
            "A modifier against the tooltip of its source: a law, a spirit or an advisor; the counts '6 of 12' against the rows",
            "Command power and its daily gain against the top bar; the twenty tiles against the top bar and the panels",
            "The two Industry rows whose game text starts with a text icon (production efficiency growth and cap): is the icon drawn?",
        ],
    },
    "history": {
        "phase": "D5", "file": "mod1440_figures.gui", "screenshot": "reference/vanilla/politics.jpg",
        "windows": nf_scene_windows(),
        "setup": [{"move": "open_politics"}, {"key": "shift+m", "wait": 1.5},
                  {"clickWidget": "mod1440_figures/nf_t4", "scene": "national_figures", "wait": 1.0}],
        "teardown": [{"clickWidget": "mod1440_figures/nf_t0", "scene": "national_figures", "wait": 0.8}, {"key": "shift+m", "wait": 0.8}],
        "expect": ["mod1440_figures/h_zoom", "mod1440_figures/nf_t4"],
        "crop": [540, 64, 1700, 636],
        "manual": ["More than one month: the graph gets a column on the first of each month, which no check lets pass"],
        "checklist": ["A click on a tile draws its figure; the chosen tile has the lighter plate",
                      "After some months of game time each figure has one column per month; a save of the build before has the eight new figures from the month of the update on",
                      "The tooltip of a column gives its month and value",
                      "Zoom in: the columns start at the lowest month", "The six numbers against the columns"],
    },
    "top_bar": tb_scene(),      # d7-top-bar
}

SAMPLE_VALUES = {
    "manpower_k": "12500", "deployed_army_manpower_k": "4300", "deployed_navy_manpower_k": "310", "deployed_airforce_manpower_k": "275",
    "num_divisions": "350", "num_battalions": "3400", "army_experience": "500", "mod1440_ar_low_str": "24", "mod1440_ar_low_org": "17",
    "skill_level": "4", "num_units": "24", "num_units_in_combat": "12", "num_infantry": "20", "num_armored": "3", "num_motorized": "1",
    "mod1440_al_fill": "87", "mod1440_st_free": "12", "state_population_k": "12500", "compliance": "45", "resistance": "20",
    "mod1440_st_rows^num": "152", "mod1440_h_max": "1332.6", "mod1440_h_half": "666.3", "mod1440_h_latest": "1250.4",
    "fuel_k": "297.2", "max_fuel_k": "371.5", "num_ships": "38", "num_deployed_planes": "992", "num_controlled_states": "24",
    "amount_research_slots": "4", "num_researched_technologies": "55",
    "mod1440_h_date^num": "120", "mod1440_h_valid": "120", "mod1440_st_sum_pop": "125000",
    "num_equipment@convoy": "1250", "num_equipment@train_equipment": "250",
}


def sample_for(window, text_value):
    """A text with its values written in, as wide as the game will make it."""
    def one(match):
        inside = match.group(1)
        if window.startswith(("mod1440_records", "mod1440_state_card")):
            return build_records.sample(inside)
        if window.startswith("mod1440_states") and st_sample(window, inside) is not None:      # d3-states
            return st_sample(window, inside)
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
        if "GetTokenLocalizedKey" in variable and window.startswith("mod1440_figures"):
            return "Share of factories on consumer goods"
        if variable in SAMPLE_VALUES:
            return SAMPLE_VALUES[variable]
        if "_fill" in variable or variable.startswith("mod1440_nf_"):
            return "87"
        if variable.startswith("mod1440_h_yl_"):
            return str(1936 + int(variable[len("mod1440_h_yl_"):]))
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
            "setup": scene["setup"], "captures": scene.get("captures", []), "expect": scene["expect"], "crop": scene["crop"],
            "manual": scene["manual"], "checklist": scene["checklist"],
        }
        for window, extra in scene.get("samples", {}).items():     # d2-readiness: samples of the scene's own
            document["samples"].setdefault(window, {}).update(extra)
        if "teardown" in scene:
            document["teardown"] = scene["teardown"]
        if "captures" in scene:
            document["captures"] = scene["captures"]
        # --- e-diary-wars: states the renderer can draw and the harness cannot bring up (render_gui.py --state)
        if "states" in scene:
            document["states"] = scene["states"]
        out["tools/scenes/%s.json" % name] = json.dumps(document, indent=2, ensure_ascii=True) + "\n"
    return out


# ---------------------------------------------------------------- texts of the reworked vanilla screens

def screen_texts():
    """Fixed captions that the override files (interface/zz_1440p_*.gui) show where no vanilla key
    has the word (W9). They share the localisation files of the pages."""
    # --- a6-overview: the caption of the Modifiers card in the army overview's rail
    B.key("ao_modifiers", "Modifiers")


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
    gui, script, shares, figures_daily, place = national_figures()
    recording, monthly = history_script(place)
    history_daily = ""      # since D4 and D5 are one page, its daily drawing is part of figures_daily
    B.files["interface/mod1440_figures.gui"] = HEADER_GUI + "guiTypes = {\n" + indent(gui) + "}\n"
    B.files["common/scripted_guis/mod1440_figures.txt"] = HEADER_TXT + block("scripted_gui", script)
    B.files["common/scripted_effects/mod1440_effects.txt"] = HEADER_TXT + count + "\n" + listing + "\n" + shares + "\n" + recording
    # The top bar strip (D7): the strip, its fixed twin, the edit button and the panel
    gui, script, tb_script = top_bar()
    B.files["interface/mod1440_top_bar.gui"] = HEADER_GUI + "guiTypes = {\n" + indent(gui) + "}\n"
    B.files["common/scripted_guis/mod1440_top_bar.txt"] = HEADER_TXT + block("scripted_gui", script)
    B.files["common/scripted_effects/mod1440_top_bar.txt"] = HEADER_TXT + tb_script
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
                                                 + block("if", "limit = { is_ai = no }\nmod1440_ev_init = yes\nmod1440_tb_default = yes\n"))))
        + block("on_daily", block("effect", block("if", "limit = { is_ai = no }\nmod1440_ar_count = yes\n" + states_daily
                                                  + figures_daily + history_daily + "mod1440_rec_daily = yes\n" + tb_daily())))
        + block("on_monthly", block("effect", block("if", "limit = { is_ai = no }\n" + monthly)))
        + "".join(block(name, block("effect", body)) for name, body in sorted(hooks.items()))))

    screen_texts()
    everything = "".join(B.files.values()) + "".join(B.loc.values())
    # A sprite the pages name and interface/1440p_ui.gfx does not declare would show as nothing in the game,
    # and a new sprite needs a restart of the game (Engine Facts X27): better to stop here.
    declared = set(re.findall(r'name = "(GFX_1440p_\w+)"', io.open(os.path.join(ROOT, "interface", "1440p_ui.gfx"), encoding="utf-8").read()))
    missing = sorted(set(re.findall(r"GFX_1440p_\w+", "".join(c for rel, c in B.files.items() if rel.endswith(".gui")))) - declared)
    if missing:
        raise ValueError("not declared in interface/1440p_ui.gfx: " + ", ".join(missing))
    # A tooltip shows a "$key$" of its text as written: the game's name is put in a text box only (the sort
    # tooltips of the States page, fix round of 2026-10-16).
    tips = set(re.findall(r'pdx_tooltip = "(\w+)"', "".join(c for rel, c in B.files.items() if rel.endswith(".gui"))))
    nested = sorted(t for t in tips if re.search(r"\$\w+\$", B.loc.get(t, "")))
    if nested:
        raise ValueError("a $key$ in a tooltip is not resolved: " + ", ".join(nested))
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
        if current is not None and current.replace("\r\n", "\n") == content:   # a checkout may carry CRLF
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
