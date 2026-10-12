"""The role-play pages of Milestone E (wiki/Roleplay-Pages.md): the Records window and what it keeps.

Not run by itself: tools/build_managers.py imports it and writes its output with everything else.

    interface/mod1440_records.gui                the window's four pages, their rows, the top bar button, the state card
    common/scripted_guis/mod1440_records.txt     what shows when, and what the buttons do
    common/scripted_effects/mod1440_records.txt  the recording, the daily comparison, the lists of the pages
    hooks                                        handed back to build_managers.py, which writes the one on_actions file

What a record is (wiki/Engine-Facts.md): a line of the log holds a date, a text key and up to two scopes (a
state, a country, a character); the name is looked up when the row is drawn (X33, X34, X37). An officer's
record is variables of the mod on the officer himself (X32). Nothing here writes to the game but one command,
add_history_entry, for the unit honours of phase E6.

How the pages look (wiki/Scripted-GUIs.md, "The Records"): dark cards as on the manager pages; figures as
tiles, a small label over a large value; every list striped, with a bar of column heads; names in the game's
highlight yellow; the game's own text icons, flags, medal strips and progress bars. The sprites are declared in
interface/1440p_ui.gfx (GFX_1440p_SG_*), all of them tiles of vanilla textures.
"""
import re

M = None        # tools/build_managers.py, set by build(): its helpers write the .gui and script pieces
B = None

REC_X, REC_Y, REC_W, REC_H = 440, 100, 1680, 1220
PAGES = [("wd", "War Diary"), ("of", "Officers"), ("gv", "Government"), ("wr", "Wars")]
LOG_KEEP = 500          # lines of each log
VIEW_ROWS = 200         # lines of the diary on one page of the list
BLANK = "token:mod1440_blank"
TILE_W, TILE_H = 156, 64
TILE = "GFX_1440p_SG_tile"                  # the plate of a figure
STRIPE = "GFX_1440p_SG_stripe_%dx%d"        # the darker band of every second row of a list
PICK = "GFX_1440p_SG_pick_%dx%d"            # the lighter band of the chosen row
ODD_ROWS = 512                              # rows a list can stripe
LONG = "GetDateStringNoHourLong"            # "1 January, 1936"


# ---------------------------------------------------------------- small pieces

def block(name, body):
    return M.block(name, body)


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


def token(name, words):
    """A text the script holds as a text key (X37). The key is lower case, as the probe's were."""
    key = "mod1440_" + name
    if B.loc.get(key, words) != words:
        raise ValueError("two texts for " + key)
    B.loc[key] = words
    return "token:" + key


def plain(name, x, y, width, key, font=None, fmt="left", height=24):
    """A text that lets a click through to the button under it."""
    return ('instantTextboxType = { name = "%s" position = { x = %d y = %d } font = "%s" text = "%s" '
            'maxWidth = %d maxHeight = %d format = %s alwaystransparent = yes }\n'
            % (name, x, y, font or M.FONT_LABEL, key, width, height, fmt))


def scaled(name, x, y, sprite, scale, tooltip=None):
    tip = ' pdx_tooltip = "%s"' % tooltip if tooltip else ""
    return 'iconType = { name = "%s" position = { x = %d y = %d } spriteType = "%s" scale = %s%s }\n' % (name, x, y, sprite, scale, tip)


def listing(name, grid, x, y, width, height, row_height):
    inner = ('gridboxtype = {\n\tname = "%s"\n\tposition = { x = 0 y = 0 }\n\tsize = { width = %d height = 100%%%% }\n'
             '\tslotsize = { width = 1 height = 1 }\n\tadd_horizontal = no\n\tformat = "UPPER_LEFT"\n}\n' % (grid, width - 30))
    return ('containerWindowType = {\n\tname = "%s"\n\tposition = { x = %d y = %d }\n\tsize = { width = %d height = %d }\n'
            '\tverticalScrollbar = "right_vertical_slider"\n\tscroll_wheel_factor = %d\n\tsmooth_scrolling = yes\n'
            '\tbackground = { name = "Background" quadTextureSprite = "%s" }\n%s}\n'
            % (name, x, y, width, height, row_height * 3, M.CARD_BG, M.indent(inner)))


def row(name, width, height, body):
    return 'containerWindowType = {\n\tname = "%s"\n\tsize = { width = %d height = %d }\n%s}\n' % (name, width, height, M.indent(body))


def heads(name, x, y, width, labels):
    """A bar of column heads over a list: (x, width, text, format, tooltip or None) each."""
    inner = ""
    for n, (lx, lw, label, fmt, tip) in enumerate(labels):
        inner += M.text("%s_%d" % (name, n), lx, 5, lw, B.key("%s_%d" % (name, n), label), M.FONT_SMALL, fmt, 20,
                        tooltip=B.key("%s_%d_tt" % (name, n), tip) if tip else None)
    return M.box(name, x, y, width, 30, inner, M.HEAD_SPRITES[240])


def tile(name, x, y, label, value, tip=None, when=None):
    """A figure: a plate with a small label over a large value. Returns the widgets and their triggers."""
    tooltip = B.key(name + "_tt", tip) if tip else None
    out = M.icon(name + "_bg", x, y, TILE)
    out += M.text(name + "_l", x + 6, y + 7, TILE_W - 12, B.key(name + "_l", label), M.FONT_SMALL, "centre", 20, tooltip=tooltip)
    out += M.text(name, x + 6, y + 30, TILE_W - 12, B.key(name, value), M.FONT_VALUE, "centre", 26, tooltip=tooltip)
    triggers = "".join(block(part + "_visible", when) for part in (name + "_bg", name + "_l", name)) if when else ""
    return out, triggers


def card(name, x, y, width, height, title, inner):
    return M.box(name, x, y, width, height,
                 M.text(name + "_title", 14, 8, width - 28, B.key(name + "_title", title), M.FONT_CARD, height=30) + inner, M.CARD_BG)


def head(prefix, page, hint):
    """The title strip every page of the window has: its name, the four page buttons, Close."""
    body = M.box(prefix + "_head", 3, 3, REC_W - 6, 50, "", "GFX_tiled_header")
    body += M.text(prefix + "_title", 22, 8, 310, B.key("rec_title_%d" % page, PAGES[page][1]), M.FONT_TITLE, height=40)
    effects = ""
    properties = ""
    for n, (short, label) in enumerate(PAGES):
        body += M.button("%s_tab_%d" % (prefix, n), 340 + n * 146, 12, "GFX_sort_button_140x29", B.key("rec_tab_%d" % n, label))
        effects += block("%s_tab_%d_click" % (prefix, n), setv("mod1440_rec_page", n) + "mod1440_rec_show = yes\n")
        properties += block("%s_tab_%d" % (prefix, n), "frame = mod1440_rec_tab_%d\n" % n)
    body += M.text(prefix + "_hint", REC_W - 770, 18, 690, B.key(prefix + "_hint", hint), M.FONT_SMALL, "right")
    body += M.button(prefix + "_close", REC_W - 66, 10, "GFX_closebutton", shortcut="ESCAPE", tooltip=B.key("rec_close_tt", "Close"))
    effects += block(prefix + "_close_click", setv("mod1440_rec_open", 0))
    return body, effects, properties


def page_gui(prefix, page, body, **parts):
    visible = "check_variable = { mod1440_rec_open = 1 }\ncheck_variable = { mod1440_rec_page = %d }\n" % page
    gui = M.box("mod1440_records_" + prefix, REC_X, REC_Y, REC_W, REC_H, body, M.PAGE_BG)
    return gui, M.scripted_gui("mod1440_records_" + prefix, "mod1440_records_" + prefix, visible=visible, **parts)


def pad(arrays, count):
    """Script that fills the arrays up to <count> elements, so that a text of a hidden row reads no missing element."""
    first = arrays[0][0]
    return block("for_loop_effect", "start = 0\nend = %d\nvalue = pad_n\n" % count + iff(
        "check_variable = { %s^num < %d }" % (first, count), "".join("add_to_array = { %s = %s }\n" % a for a in arrays)))


# ---------------------------------------------------------------- the recording

# A kind of line is (name, family, words). The family is the filter of the diary it belongs to:
# 1 war and peace, 2 territory, 3 government, 4 officers, 5 air and sea. A kind's place in this list is its
# number in the counters (mod1440_ct), which a save keeps: add new kinds at the end.
KINDS = [
    ("begins", 1, "The record begins"),
    ("war_on", 1, "War declared on"), ("war_by", 1, "War declared by"), ("war_with", 1, "At war with"),
    ("peace", 1, "Peace with"), ("capitulated", 1, "Capitulated:"), ("we_capitulated", 1, "We capitulated"),
    ("annexed", 1, "Annexed"), ("subject_new", 1, "Made a subject:"), ("subject_gone", 1, "No longer a subject:"),
    ("faction_in", 1, "Joined the faction led by"), ("faction_out", 1, "Left the faction"),
    ("member_in", 1, "Joined our faction:"), ("member_out", 1, "Left our faction:"),
    ("state_taken", 2, "State taken"), ("state_lost", 2, "State lost"),
    ("capital_taken", 2, "Capital taken"), ("capital_lost", 2, "Capital lost"),
    ("landing", 2, "Landing in"), ("airborne", 2, "Airborne landing in"), ("cited", 2, "Divisions cited in"),
    ("party", 3, "The ruling party changed"), ("government", 3, "The government changed"), ("election", 3, "An election was held"),
    ("leader", 3, "New head of government"), ("appointed", 3, "Appointed"), ("dismissed", 3, "Left office"),
    ("commissioned", 4, "Commissioned"), ("promoted", 4, "Promoted to field marshal"), ("level", 4, "Gained a skill level"),
    ("decorated", 4, "Decorated"),
    ("ace_new", 5, "An ace was promoted"), ("ace_lost", 5, "An ace was lost"), ("ace_down", 5, "An enemy ace was shot down"),
    ("pride_lost", 5, "Our pride of the fleet was sunk by"), ("pride_sunk", 5, "Sank the pride of the fleet of"),
]
FAMILY = dict((name, family) for name, family, words in KINDS)
NUMBER = dict((name, n) for n, (name, family, words) in enumerate(KINDS))
LOG_ARRAYS = ["date", "day", "kind", "fam", "a", "b", "sa", "sb"]
# the game's own text icon for each family
FAMILY_ICON = {1: "army_experience", 2: "victory_points", 3: "pol_power", 4: "command_power", 5: "air_experience"}


def fill(name, a=None, b=None, state=False):
    """Script that sets what the next line says: its kind, and whom or what it is about. a is a state
    (state=True) or a character, b a country."""
    out = tmp("ev_kind", "token:mod1440_ev_" + name) + tmp("ev_fam", FAMILY[name]) + tmp("ev_kid", NUMBER[name])
    out += tmp("ev_sa", (2 if state else 1) if a else 0) + tmp("ev_a", a or 0)
    return out + tmp("ev_sb", 1 if b else 0) + tmp("ev_b", b or 0)


def line(name, a=None, b=None, state=False, log="ev"):
    """Script that writes one line for the country in scope."""
    return fill(name, a, b, state) + "mod1440_%s_add = yes\n" % log


def count(*names):
    """Script that sums the counters of some kinds into the temporary variable ct_sum."""
    return tmp("ct_sum", 0) + "".join("add_to_temp_variable = { ct_sum = mod1440_ct^%d }\n" % NUMBER[name] for name in names)


def recording():
    for name, family, words in KINDS:
        token("ev_" + name, words)
    token("blank", "")
    out = "# The Records: one line of a log, for the country in scope. The caller has set the temporary variables\n"
    out += "# ev_kind, ev_fam, ev_kid, ev_a, ev_b, ev_sa and ev_sb (tools/build_records.py, line()). The oldest line goes past %d.\n" % LOG_KEEP
    out += "# Each kind of line is counted (mod1440_ct), a line of the territory log in that log only.\n"
    values = {"date": "global.date", "day": "global.num_days", "kind": "ev_kind", "fam": "ev_fam", "a": "ev_a", "b": "ev_b",
              "sa": "ev_sa", "sb": "ev_sb"}
    counted = pad([("mod1440_ct", 0)], len(KINDS) + 8) + "add_to_variable = { mod1440_ct^ev_kid = 1 }\n"
    for log in ("ev", "tr"):
        body = "".join("add_to_array = { mod1440_%s_%s = %s }\n" % (log, part, values[part]) for part in LOG_ARRAYS)
        body += iff("check_variable = { mod1440_%s_date^num > %d }" % (log, LOG_KEEP),
                    "".join("remove_from_array = { array = mod1440_%s_%s index = 0 }\n" % (log, part) for part in LOG_ARRAYS))
        body += counted if log == "tr" else iff("NOT = { check_variable = { ev_fam = 2 } }", counted)
        out += block("mod1440_%s_add" % log, body) + "\n"
    out += "# The Records: which rows of a list are striped: 0, 1, 0, 1 ... for %d rows.\n" % ODD_ROWS
    out += block("mod1440_rec_odd", iff("check_variable = { mod1440_odd^num < %d }" % ODD_ROWS, tmp("odd_v", 0) + block(
        "for_loop_effect", "start = 0\nend = %d\nvalue = odd_n\n" % ODD_ROWS
        + iff("check_variable = { mod1440_odd^num < %d }" % ODD_ROWS, "add_to_array = { mod1440_odd = odd_v }\n")
        + iff("check_variable = { odd_v = 0 }", tmp("odd_v", 1)) + els(tmp("odd_v", 0)))))
    return out


def compare(game, copy, value, new_body, gone_body):
    """Script for the daily comparison of an array of the game with the mod's copy of yesterday: new_body
    runs for each element that is new, gone_body for each that is gone, with the element in the temporary
    variable <value>. The copy is made again afterwards."""
    out = ""
    if new_body:
        out += block("for_each_loop", "array = %s\nvalue = %s\n" % (game, value)
                     + iff("NOT = { is_in_array = { array = %s value = %s } }" % (copy, value), new_body))
    if gone_body:
        out += block("for_each_loop", "array = %s\nvalue = %s\n" % (copy, value)
                     + iff("NOT = { is_in_array = { array = %s value = %s } }" % (game, value), gone_body))
    out += "clear_array = %s\n" % copy
    out += block("for_each_loop", "array = %s\nvalue = %s\nadd_to_array = { %s = %s }\n" % (game, value, copy, value))
    return out


# ---------------------------------------------------------------- War Diary (E1)

WD_LIST_W = 1190
WD_ROW_W = WD_LIST_W - 30
WD_ROW = 30
WD_ICON_X, WD_EVENT_X, WD_A_X, WD_B_X = 196, 232, 540, 840
WD_PANE_X = 14 + WD_LIST_W + 12
WD_PANE_W = REC_W - WD_PANE_X - 14
WD_FILTERS = [
    (0, "all", "All", "Everything but the single states: wars, capitals, government, officers, air and sea."),
    (1, "war", "War and peace", "Wars declared and ended, capitulations, annexations, subjects, factions."),
    (2, "land", "Territory", "Every state taken or lost, landings, and the divisions you cited."),
    (3, "gov", "Government", "Parties, elections, heads of government, advisors."),
    (4, "off", "Officers", "Commissions, promotions, skill levels, decorations."),
    (5, "air", "Air and sea", "Aces and the pride of a fleet."),
]
# the figures of the record: (name, label, kinds counted or a variable, tooltip)
WD_FIGURES = [
    ("wars", "Wars begun", ("war_on", "war_by", "war_with"), "Countries you went to war with since the record began."),
    ("peace", "Wars ended", ("peace",), "Enemies you are no longer at war with."),
    ("cap", "Capitulations", ("capitulated",), "Enemies that capitulated."),
    ("annex", "Annexations", ("annexed",), "Countries you annexed."),
    ("taken", "States taken", ("state_taken", "capital_taken"), "States you took control of."),
    ("lost", "States lost", ("state_lost", "capital_lost"), "States you lost control of."),
    ("capitals", "Capitals taken", ("capital_taken",), "Capitals among the states you took."),
    ("govs", "Governments", ("party", "government", "leader"), "Changes of ruling party, of government and of its head."),
    ("comm", "Commissioned", ("commissioned",), "Generals and admirals who joined your officers."),
    ("prom", "Promotions", ("promoted",), "Generals promoted to field marshal."),
    ("dec", "Decorations", ("decorated",), "Decorations you awarded to officers."),
    ("hon", "Divisions cited", "mod1440_hn_count", "Lines written into the history of your divisions: for a capital taken, or on your word."),
]


def war_diary():
    body, effects, properties = head("wd", 0, "Written by the mod as the game goes, from the day it is active. Shift+J or Escape closes.")
    triggers = ""
    for n, (value, name, label, tip) in enumerate(WD_FILTERS):
        text_icon = "£%s  " % FAMILY_ICON[value] if value else ""
        body += M.button("wd_show_%s" % name, 16 + n * 146, 62, "GFX_sort_button_140x29", B.key("wd_show_%s" % name, text_icon + label),
                         tooltip=B.key("wd_show_%s_tt" % name, tip))
        effects += block("wd_show_%s_click" % name, setv("mod1440_wd_filter", value) + setv("mod1440_wd_from", 0) + "mod1440_wd_list = yes\n")
        properties += block("wd_show_%s" % name, "frame = mod1440_wd_frame_%d\n" % value)
    body += M.button("wd_newer", 906, 62, "GFX_sort_button_100x29", B.key("wd_newer", "Newer"),
                     tooltip=B.key("wd_newer_tt", "The %d lines after these." % VIEW_ROWS))
    effects += block("wd_newer_click", "subtract_from_variable = { mod1440_wd_from = %d }\n" % VIEW_ROWS
                     + "clamp_variable = { var = mod1440_wd_from min = 0 }\nmod1440_wd_list = yes\n")
    body += M.button("wd_older", 1010, 62, "GFX_sort_button_100x29", B.key("wd_older", "Older"),
                     tooltip=B.key("wd_older_tt", "The %d lines before these." % VIEW_ROWS))
    effects += block("wd_older_click", tmp("wd_next", "mod1440_wd_from") + "add_to_temp_variable = { wd_next = %d }\n" % VIEW_ROWS
                     + iff("check_variable = { wd_next < mod1440_wd_total }", setv("mod1440_wd_from", "wd_next") + "mod1440_wd_list = yes\n"))
    body += M.text("wd_count", 1116, 66, 86, B.key("wd_count", "[?mod1440_wd_fam^num|0] of [?mod1440_wd_total|0]"), M.FONT_SMALL, "right",
                   tooltip=B.key("wd_count_tt", "Lines shown, of the lines this filter has."))

    body += heads("wd_heads", 14, 98, WD_LIST_W, [
        (12, 170, "Date", "left", None), (WD_EVENT_X, 290, "Event", "left", None),
        (WD_A_X + 6, 280, "State, person or country", "left", "A state's name is a button: it shows the state on the map."),
        (WD_B_X, 290, "Country", "left", "For a state: whom it was taken from or lost to.")])
    body += listing("wd_list", "wd_grid", 14, 130, WD_LIST_W, REC_H - 130 - 14, WD_ROW)
    body += M.text("wd_none", 40, 150, 900, B.key("wd_none", "Nothing of this kind is written down yet."), M.FONT_LABEL)
    triggers += block("wd_none_visible", "check_variable = { mod1440_wd_fam^num < 1 }\n")

    # ---- a line: date, the family's icon, the words, then whom or what it is about
    country = B.key("wd_row_b", "§Y[?mod1440_wd_b^i.GetNameWithFlag]§!")
    entry = M.icon("wd_row_stripe", 0, 0, STRIPE % (WD_ROW_W, WD_ROW))
    entry += M.button("wd_row_go", WD_A_X, 0, M.HEAD_SPRITES[240], tooltip=B.key("wd_row_go_tt", "Show this state on the map"))
    entry += M.text("wd_row_date", 12, 5, 178, B.key("wd_row_date", "[?mod1440_wd_date^i.%s]" % LONG), M.FONT_SMALL, height=22)
    for family, text_icon in sorted(FAMILY_ICON.items()):
        entry += M.text("wd_row_icon_%d" % family, WD_ICON_X, 3, 30, B.key("wd_icon_%d" % family, "£" + text_icon), M.FONT_LABEL, height=24)
        triggers += block("wd_row_icon_%d_visible" % family, "check_variable = { v = %d }\n" % family)
    entry += M.text("wd_row_event", WD_EVENT_X, 4, WD_A_X - WD_EVENT_X - 8, B.key("wd_row_event", "[?mod1440_wd_kind^i.GetTokenLocalizedKey]"),
                    M.FONT_LABEL, height=22)
    entry += plain("wd_row_a", WD_A_X + 8, 4, WD_B_X - WD_A_X - 16, B.key("wd_row_a", "§Y[?mod1440_wd_a^i.GetName]§!"), height=22)
    entry += M.text("wd_row_b", WD_B_X, 4, WD_ROW_W - WD_B_X - 8, country, M.FONT_LABEL, height=22)
    entry += M.text("wd_row_b_near", WD_A_X + 8, 4, 440, country, M.FONT_LABEL, height=22)
    triggers += block("wd_row_stripe_visible", "check_variable = { mod1440_odd^i = 1 }\n")
    triggers += block("wd_row_go_visible", "check_variable = { mod1440_wd_sa^i = 2 }\n")
    triggers += block("wd_row_a_visible", "check_variable = { mod1440_wd_sa^i > 0 }\n")
    # a line about a country alone has its country where the eye looks next, not two columns away
    triggers += block("wd_row_b_visible", "check_variable = { mod1440_wd_sb^i > 0 }\ncheck_variable = { mod1440_wd_sa^i > 0 }\n")
    triggers += block("wd_row_b_near_visible", "check_variable = { mod1440_wd_sb^i > 0 }\ncheck_variable = { mod1440_wd_sa^i = 0 }\n")
    effects += block("wd_row_go_click", tmp("wd_state", "mod1440_wd_a^i")
                     + block("var:wd_state", block("ROOT", "goto_state = PREV\n" + setv("mod1440_rec_open", 0))))

    # ---- the record so far: since when, twelve figures, the switch of the battle honours
    pane = M.text("wd_since_l", 16, 46, 150, B.key("wd_since_l", "Kept since"), M.FONT_SMALL, height=22)
    pane += M.text("wd_since", 170, 44, WD_PANE_W - 186, B.key("wd_since", "[?mod1440_ev_since.%s]" % LONG), M.FONT_LABEL, height=22)
    pane += M.text("wd_days_l", 16, 72, 150, B.key("wd_days_l", "Days on record"), M.FONT_SMALL, height=22)
    pane += M.text("wd_days", 170, 70, WD_PANE_W - 186, B.key("wd_days", "[?mod1440_wd_days|0]"), M.FONT_LABEL, height=22)
    sums = ""
    left = (WD_PANE_W - 2 * TILE_W - 12) // 2
    for n, (name, label, source, tip) in enumerate(WD_FIGURES):
        variable = source if isinstance(source, str) else "mod1440_wd_n_" + name
        piece, extra = tile("wd_f_" + name, left + (n % 2) * (TILE_W + 12), 110 + (n // 2) * (TILE_H + 10), label, "[?%s|0]" % variable, tip)
        pane += piece
        if not isinstance(source, str):
            sums += count(*source) + setv(variable, "ct_sum")
    y = 110 + 6 * (TILE_H + 10) + 10
    pane += M.text("wd_hon_title", 14, y, WD_PANE_W - 28, B.key("wd_hon_title", "Battle honours"), M.FONT_CARD, height=30)
    pane += M.button("wd_honours", 16, y + 38, "GFX_sort_button_202x29", B.key("wd_honours", "Written by themselves"), tooltip=B.key(
        "wd_honours_tt", "While this is chosen, your divisions that stand in an enemy capital when it falls get a line in their own history (By Blood Alone). A division takes one line a day."))
    pane += M.text("wd_hon_1", 16, y + 76, WD_PANE_W - 32, B.key("wd_hon_1", "A division that stands in an enemy capital when it falls"), M.FONT_SMALL, height=20)
    pane += M.text("wd_hon_2", 16, y + 96, WD_PANE_W - 32, B.key("wd_hon_2", "gets a line in its own history. Select a state you hold"), M.FONT_SMALL, height=20)
    pane += M.text("wd_hon_3", 16, y + 116, WD_PANE_W - 32, B.key("wd_hon_3", "to cite the divisions there yourself."), M.FONT_SMALL, height=20)
    pane += M.text("wd_kept", 16, REC_H - 62 - 14 - 34, WD_PANE_W - 32,
                   B.key("wd_kept", "The newest %d lines are kept, and %d of single states." % (LOG_KEEP, LOG_KEEP)), M.FONT_SMALL, height=20)
    effects += block("wd_honours_click", flip("mod1440_hn_auto") + "mod1440_rec_show = yes\n")
    properties += block("wd_honours", "frame = mod1440_hn_frame\n")
    body += card("wd_pane", WD_PANE_X, 62, WD_PANE_W, REC_H - 62 - 14, "The record", pane)

    gui, script = page_gui("wd", 0, body, dirty="mod1440_rec_dirty",
                           lists=block("wd_grid", 'array = mod1440_wd_fam\nentry_container = "mod1440_records_diary_row"\n'),
                           effects=effects, triggers=triggers, properties=properties)
    gui += row("mod1440_records_diary_row", WD_ROW_W, WD_ROW, entry)

    view = ["date", "kind", "fam", "a", "b", "sa", "sb"]

    def copy(log, wanted):
        keep = tmp("wd_ok", 1)
        if wanted:
            keep += iff("check_variable = { mod1440_wd_filter > 0 } NOT = { check_variable = { mod1440_%s_fam^wd_m = mod1440_wd_filter } }" % log,
                        tmp("wd_ok", 0))
        return block("for_loop_effect", (
            "start = 0\nend = mod1440_%s_date^num\nvalue = wd_n\n" % log
            + tmp("wd_m", "mod1440_%s_date^num" % log) + "subtract_from_temp_variable = { wd_m = 1 }\nsubtract_from_temp_variable = { wd_m = wd_n }\n"
            + keep
            + iff("check_variable = { wd_ok = 1 }", (
                "add_to_temp_variable = { wd_seen = 1 }\n"
                + iff("check_variable = { wd_seen > mod1440_wd_from } check_variable = { mod1440_wd_fam^num < %d }" % VIEW_ROWS,
                      "".join("add_to_array = { mod1440_wd_%s = mod1440_%s_%s^wd_m }\n" % (part, log, part) for part in view))))))

    frames = "".join(setv("mod1440_wd_frame_%d" % v, 1) for v, _, _, _ in WD_FILTERS)
    frames += "".join(iff("check_variable = { mod1440_wd_filter = %d }" % v, setv("mod1440_wd_frame_%d" % v, 2)) for v, _, _, _ in WD_FILTERS)
    script_effects = (
        "# War Diary: copies the lines the chosen filter wants, newest first, %d from the chosen place, into the arrays\n"
        "# the page draws. Territory has a log of its own; every other filter reads the main log. Then the figures\n"
        "# of the record: sums of the counters, and the days since it began.\n" % VIEW_ROWS
        + block("mod1440_wd_list", (
            "".join("clear_array = mod1440_wd_%s\n" % part for part in view)
            + tmp("wd_seen", 0)
            + iff("check_variable = { mod1440_wd_filter = 2 }", copy("tr", False)) + els(copy("ev", True))
            + setv("mod1440_wd_total", "wd_seen") + frames
            + pad([("mod1440_ct", 0)], len(KINDS) + 8) + sums
            + setv("mod1440_wd_days", "global.num_days") + "subtract_from_variable = { mod1440_wd_days = mod1440_ev_since_day }\n"
            + "add_to_variable = { mod1440_rec_dirty = 1 }\n")))
    return gui, script, script_effects


# ---------------------------------------------------------------- Officers (E2)

# A column is (name, value of the officer, width, head, what the tooltip says). An admiral has no planning and
# logistics: his third and fourth levels are manoeuvring and coordination, and his command is ships.
OF_COLUMNS = [
    ("skill", "skill_level", 56, "Skill", "Skill level."),
    ("atk", "attack_level", 52, "Atk", "Attack."),
    ("def", "defense_level", 52, "Def", "Defence."),
    ("c3", "planning_level", 52, "Pln", "Planning; for an admiral manoeuvring."),
    ("c4", "logistics_level", 52, "Log", "Logistics; for an admiral coordination."),
    ("traits", "num_traits", 56, "Traits", "How many traits the officer has."),
    ("cmd", "num_units", 60, "Cmd", "Divisions under his command today; for an admiral ships."),
    ("won", "mod1440_of_won", 56, "Won", "Battles won since the record began."),
    ("lost", "mod1440_of_lost", 56, "Lost", "Battles lost since the record began."),
    ("dec", "mod1440_of_dec^num", 84, "Medals", "Decorations you have awarded."),
]
OF_NAVY = {"c3": "maneuvering_level", "c4": "coordination_level", "cmd": "num_ships"}
OF_NAME, OF_RANK = 240, 84
OF_ROW_W = OF_NAME + OF_RANK + sum(c[2] for c in OF_COLUMNS)
OF_ROW = 30
OF_FILTERS = [
    (0, "all", "All", "Every officer serving today."),
    (1, "army", "Army", "Generals and field marshals."),
    (2, "navy", "Navy", "Admirals."),
    (3, "cmd", "With a command", "Officers who lead troops or ships today."),
    (4, "dec", "Decorated", "Officers you have decorated."),
    (5, "former", "Former", "Officers the record knows who serve no longer."),
]
OF_CARD_X = 14 + OF_ROW_W + 30 + 12
OF_CARD_W = REC_W - OF_CARD_X - 14
MEDAL_SLOTS = 12        # decorations a country can award at most (Chile has twelve medals)
CARD_LINES = 7          # decorations and diary lines the card shows
DEC_ARRAYS = ["dec", "dec_key", "dec_date", "dec_set", "dec_frame"]     # an officer's decorations, on the officer


def officers():
    from unit_medals_table import MEDALS
    sets = sorted(set(m[1] for m in MEDALS))
    body, effects, properties = head("of", 1, "Every general and admiral, with what the mod has written down about him. Click one for his record.")
    triggers = ""
    row_triggers = ""
    for n, (value, name, label, tip) in enumerate(OF_FILTERS):
        body += M.button("of_show_%s" % name, 16 + n * 146, 62, "GFX_sort_button_140x29", B.key("of_show_%s" % name, label),
                         tooltip=B.key("of_show_%s_tt" % name, tip))
        effects += block("of_show_%s_click" % name, setv("mod1440_of_show", value) + "mod1440_of_list = yes\n")
        properties += block("of_show_%s" % name, "frame = mod1440_of_frame_%d\n" % value)
    body += M.text("of_count", 16 + 6 * 146 + 8, 66, 200, B.key("of_count", "[?mod1440_of_rows^num|0] listed"), M.FONT_SMALL)

    # ---- column heads: a click sorts, a second click turns the order
    x = 14
    body += M.button("of_sort_name", x, 100, M.HEAD_SPRITES[OF_NAME], B.key("of_sort_name", "Officer"),
                     tooltip=B.key("of_sort_name_tt", "Back to the order of the game."))
    effects += block("of_sort_name_click", setv("mod1440_of_sort_by", 0) + "mod1440_of_list = yes\n")
    x += OF_NAME
    body += M.icon("of_h_rank_bg", x, 100, M.HEAD_SPRITES[OF_RANK])
    body += M.text("of_h_rank", x + 4, 105, OF_RANK - 8, B.key("of_h_rank", "Rank"), M.FONT_SMALL, "centre", 20)
    x += OF_RANK
    entry = M.icon("of_row_stripe", 0, 0, STRIPE % (OF_ROW_W, OF_ROW))
    entry += M.icon("of_row_pick", 0, 0, PICK % (OF_ROW_W, OF_ROW))
    entry += M.button("of_row", 0, 0, M.HEAD_SPRITES[OF_NAME], tooltip=B.key("of_row_tt", "Show this officer's record"))
    entry += plain("of_row_name", 10, 4, OF_NAME - 16, B.key("of_row_name", "[THIS.GetName]"), height=22)
    row_triggers += block("of_row_stripe_visible", is_one("mod1440_of_odd") + "\n") + block("of_row_pick_visible", is_one("mod1440_of_picked") + "\n")
    for rank, label, trigger in (("fm", "Marshal", "is_field_marshal = yes"), ("gen", "General", "is_corps_commander = yes"),
                                 ("adm", "Admiral", "is_navy_leader = yes")):
        entry += M.text("of_row_%s" % rank, OF_NAME + 4, 5, OF_RANK - 8, B.key("of_rank_%s" % rank, label), M.FONT_SMALL, "centre", 22)
        row_triggers += block("of_row_%s_visible" % rank, trigger + "\n")
    keys = ""
    rx = OF_NAME + OF_RANK
    for number, (name, value, width, label, tip) in enumerate(OF_COLUMNS, start=1):
        body += M.button("of_sort_%s" % name, x, 100, M.HEAD_SPRITES[width], B.key("of_sort_%s" % name, label),
                         tooltip=B.key("of_sort_%s_tt" % name, tip + "\\nClick to sort, click again to turn the order."))
        effects += block("of_sort_%s_click" % name, (
            iff("check_variable = { mod1440_of_sort_by = %d }" % number, flip("mod1440_of_up"))
            + els(setv("mod1440_of_sort_by", number) + setv("mod1440_of_up", 0))
            + setv("mod1440_of_arrow_x", x + width - 21) + "mod1440_of_list = yes\n"))
        key = tmp("of_key", value)
        if name in OF_NAVY:
            key += iff("is_navy_leader = yes", tmp("of_key", OF_NAVY[name]))
        keys += iff("check_variable = { ROOT.mod1440_of_sort_by = %d }" % number, key, "if" if number == 1 else "else_if")
        # a number stands under the middle of its head
        entry += M.text("of_cell_%s" % name, rx + 4, 4, width - 8, B.key("of_cell_%s" % name, "[?%s|0]" % value), M.FONT_LABEL, "centre", 22)
        if name in OF_NAVY:
            entry += M.text("of_cell_%s_navy" % name, rx + 4, 4, width - 8, B.key("of_cell_%s_navy" % name, "[?%s|0]" % OF_NAVY[name]),
                            M.FONT_LABEL, "centre", 22)
            row_triggers += block("of_cell_%s_visible" % name, "NOT = { is_navy_leader = yes }\n")
            row_triggers += block("of_cell_%s_navy_visible" % name, "is_navy_leader = yes\n")
        elif name in ("won", "lost", "dec"):
            row_triggers += block("of_cell_%s_visible" % name, M.more_than_zero(value))
        x += width
        rx += width
    body += M.icon("of_arrow_down", 0, 111, "GFX_arrow_down_small")
    body += M.icon("of_arrow_up", 0, 111, "GFX_arrow_up_small")
    properties += block("of_arrow_down", "x = mod1440_of_arrow_x\n") + block("of_arrow_up", "x = mod1440_of_arrow_x\n")
    triggers += block("of_arrow_down_visible", M.more_than_zero("mod1440_of_sort_by") + "NOT = { %s }\n" % is_one("mod1440_of_up"))
    triggers += block("of_arrow_up_visible", M.more_than_zero("mod1440_of_sort_by") + is_one("mod1440_of_up") + "\n")
    body += listing("of_list", "of_grid", 14, 132, OF_ROW_W + 30, REC_H - 132 - 14, OF_ROW)
    # the row's scope is the officer: the mark of the one chosen before is taken off, his put on
    effects += block("of_row_click", (
        block("ROOT", iff(is_one("mod1440_of_has_sel"), block("var:mod1440_of_sel", setv("mod1440_of_picked", 0)))
              + setv("mod1440_of_sel", "PREV") + setv("mod1440_of_has_sel", 1))
        + setv("mod1440_of_picked", 1) + block("ROOT", "mod1440_of_card = yes\n")))

    # ---- the file of the chosen officer
    has = is_one("mod1440_of_has_sel") + "\n"
    inner = M.text("of_c_name", 16, 10, OF_CARD_W - 32, B.key("of_c_name", "[?mod1440_of_sel.GetName]"), M.FONT_TITLE, height=40)
    inner += M.text("of_c_none", 16, 18, OF_CARD_W - 32, B.key("of_c_none", "Click an officer in the table to open his file."), M.FONT_LABEL)
    triggers += block("of_c_name_visible", has) + block("of_c_none_visible", "NOT = { %s }\n" % has.strip())

    def variants(name, x, y, width, font, fmt, options):
        """One of several texts on the same spot, each shown when its condition holds."""
        out, extra = "", ""
        for suffix, value, condition in options:
            widget = "of_c_%s%s" % (name, suffix)
            out += M.text(widget, x, y, width, B.key(widget, value), font, fmt, 22)
            extra += block(widget + "_visible", has + condition)
        return out, extra

    rank3 = "check_variable = { mod1440_of_c_rank = 3 }\n"
    for name, x, y, width, font, fmt, options in (
            ("rank", 18, 56, 170, M.FONT_LABEL, "left", [("_1", "§YField Marshal§!", "check_variable = { mod1440_of_c_rank = 1 }\n"),
                                                         ("_2", "§YGeneral§!", "check_variable = { mod1440_of_c_rank = 2 }\n"),
                                                         ("_3", "§YAdmiral§!", rank3)]),
            ("service", 196, 58, 180, M.FONT_SMALL, "left", [("_on", "serving", "NOT = { %s }\n" % is_one("mod1440_of_c_former")),
                                                             ("_off", "§Rno longer serving§!", is_one("mod1440_of_c_former") + "\n")]),
            ("cmd", OF_CARD_W - 316, 58, 300, M.FONT_SMALL, "right", [("_army", "commands [?mod1440_of_c_cmd|0] divisions", "NOT = { %s }\n" % rank3.strip()),
                                                                      ("_navy", "commands [?mod1440_of_c_cmd|0] ships", rank3)])):
        piece, extra = variants(name, x, y, width, font, fmt, options)
        inner += piece
        triggers += extra
    step = (OF_CARD_W - 32 - 4 * TILE_W) // 3 + TILE_W
    for n, (name, label, value, tip) in enumerate((
            ("skill", "Skill", "[?mod1440_of_c_skill|0]", None),
            ("won", "Battles won", "[?mod1440_of_c_won|0]", "Counted since the record began."),
            ("lost", "Battles lost", "[?mod1440_of_c_lost|0]", "Counted since the record began."),
            ("states", "States taken", "[?mod1440_of_c_states|0]", "States you took while he had the most divisions in them."))):
        piece, extra = tile("of_c_" + name, 16 + n * step, 88, label, value, tip, has)
        inner += piece
        triggers += extra
    for n, (name, label) in enumerate((("since", "Commissioned"), ("prom", "Promoted to field marshal"), ("lvl", "Last skill level"))):
        y = 164 + n * 24
        inner += M.text("of_c_%s_l" % name, 18, y, 300, B.key("of_c_%s_l" % name, label), M.FONT_SMALL, height=22)
        options = [("", "[?mod1440_of_c_%s.%s]" % (name, LONG), is_one("mod1440_of_c_has_%s" % name) + "\n")]
        options.append(("_old", "before the record began" if name == "since" else "-", "NOT = { %s }\n" % is_one("mod1440_of_c_has_%s" % name)))
        piece, extra = variants(name, 320, y - 2, OF_CARD_W - 336, M.FONT_LABEL, "left", options)
        inner += piece
        triggers += extra + block("of_c_%s_l_visible" % name, has)

    # ---- his decorations: the medals side by side, then their names
    y = 244
    inner += M.text("of_c_dec_title", 16, y, 300, B.key("of_c_dec_title", "Decorations"), M.FONT_CARD, height=30)
    inner += M.button("of_takeback", OF_CARD_W - 160, y + 2, "GFX_sort_button_140x29", B.key("of_takeback", "Take back last"),
                      tooltip=B.key("of_takeback_tt", "Takes the decoration awarded last from this officer."))
    inner += M.text("of_c_dec_none", 18, y + 40, 500, B.key("of_c_dec_none", "None yet. Award one below."), M.FONT_SMALL, height=22)
    triggers += block("of_c_dec_title_visible", has)
    triggers += block("of_takeback_visible", has + M.more_than_zero("mod1440_of_c_dec_n"))
    triggers += block("of_c_dec_none_visible", has + "check_variable = { mod1440_of_c_dec_n < 1 }\n")
    effects += block("of_takeback_click", "mod1440_md_takeback = yes\n")
    for k in range(CARD_LINES):
        more = has + "check_variable = { mod1440_of_c_dec_n > %d }\n" % k
        tip = B.key("of_c_rack_%d_tt" % k, "[?mod1440_of_c_dec_key^%d.GetTokenLocalizedKey]\\n[?mod1440_of_c_dec_date^%d.%s]" % (k, k, LONG))
        for s, name in enumerate(sets):
            widget = "of_c_rack_%d_%s" % (k, name)
            inner += scaled(widget, 14 + k * 60, y + 34, "GFX_medal_icon_%s_large" % name, 1.0, tip)
            properties += block(widget, "frame = mod1440_of_c_dec_frame^%d\n" % k)
            triggers += block(widget + "_visible", more + "check_variable = { mod1440_of_c_dec_set^%d = %d }\n" % (k, s))
        ly = y + 122 + k * 22
        inner += M.text("of_c_dec_%d" % k, 18, ly, 430, B.key("of_c_dec_%d" % k, "[?mod1440_of_c_dec_key^%d.GetTokenLocalizedKey]" % k),
                        M.FONT_SMALL, height=22)
        inner += M.text("of_c_dec_%d_d" % k, 460, ly, OF_CARD_W - 476,
                        B.key("of_c_dec_%d_d" % k, "[?mod1440_of_c_dec_date^%d.%s]" % (k, LONG)), M.FONT_SMALL, height=22)
        triggers += block("of_c_dec_%d_visible" % k, more) + block("of_c_dec_%d_d_visible" % k, more)

    # ---- the medals his country can award
    y += 122 + CARD_LINES * 22 + 6
    inner += M.text("of_md_title", 16, y, 400, B.key("of_md_title", "Award a decoration"), M.FONT_CARD, height=30)
    inner += M.text("of_md_hint", 18, y + 32, OF_CARD_W - 36, B.key(
        "of_md_hint", "Your country's medals as the game has them. For an officer they are a record only: no bonus, no cost."), M.FONT_SMALL, height=22)
    triggers += block("of_md_title_visible", has) + block("of_md_hint_visible", has)
    y += 58
    half = OF_CARD_W // 2 - 8
    for k in range(MEDAL_SLOTS):
        sx = 18 + (k % 2) * half
        sy = y + (k // 2) * 50
        more = has + "check_variable = { mod1440_md_count > %d }\n" % k
        for s, name in enumerate(sets):
            widget = "of_md_%d_%s" % (k, name)
            inner += scaled(widget, sx - 2, sy - 4, "GFX_medal_icon_%s_large" % name, 0.65)
            properties += block(widget, "frame = mod1440_md_frame^%d\n" % k)
            triggers += block(widget + "_visible", has + "check_variable = { mod1440_md_set^%d = %d }\n" % (k, s))
        inner += M.text("of_md_%d_name" % k, sx + 40, sy, half - 46,
                        B.key("of_md_%d_name" % k, "[?mod1440_md_key^%d.GetTokenLocalizedKey]" % k), M.FONT_SMALL, height=22)
        inner += M.button("of_award_%d" % k, sx + 40, sy + 20, "GFX_sort_button_100x29", B.key("of_award", "Award"))
        inner += M.text("of_md_%d_held" % k, sx + 148, sy + 25, 150, B.key("of_md_held", "§Gawarded§!"), M.FONT_SMALL, height=22)
        held = "check_variable = { mod1440_md_has^%d = 1 }\n" % k
        triggers += block("of_md_%d_name_visible" % k, more) + block("of_award_%d_visible" % k, more)
        triggers += block("of_award_%d_click_enabled" % k, "NOT = { %s }\n" % held.strip()) + block("of_md_%d_held_visible" % k, more + held)
        effects += block("of_award_%d_click" % k, tmp("md_k", k) + "mod1440_md_award = yes\n")

    y += (MEDAL_SLOTS // 2) * 50 + 2
    inner += M.text("of_ln_title", 16, y, 400, B.key("of_ln_title", "In the War Diary"), M.FONT_CARD, height=30)
    inner += M.text("of_ln_none", 18, y + 36, 500, B.key("of_ln_none", "Nothing yet."), M.FONT_SMALL, height=22)
    triggers += block("of_ln_title_visible", has) + block("of_ln_none_visible", has + "check_variable = { mod1440_of_ln_n < 1 }\n")
    for k in range(CARD_LINES):
        more = has + "check_variable = { mod1440_of_ln_n > %d }\n" % k
        inner += M.text("of_ln_%d_d" % k, 18, y + 36 + k * 22, 170, B.key("of_ln_%d_d" % k, "[?mod1440_of_ln_date^%d.%s]" % (k, LONG)),
                        M.FONT_SMALL, height=22)
        inner += M.text("of_ln_%d" % k, 196, y + 36 + k * 22, OF_CARD_W - 212,
                        B.key("of_ln_%d" % k, "[?mod1440_of_ln_kind^%d.GetTokenLocalizedKey]" % k), M.FONT_SMALL, height=22)
        triggers += block("of_ln_%d_d_visible" % k, more) + block("of_ln_%d_visible" % k, more)
    body += M.box("of_card", OF_CARD_X, 96, OF_CARD_W, REC_H - 96 - 14, inner, M.CARD_BG)

    gui, script = page_gui("of", 1, body, dirty="mod1440_rec_dirty",
                           lists=block("of_grid", 'array = mod1440_of_rows\nchange_scope = yes\nentry_container = "mod1440_records_officer_row"\n'),
                           effects=effects, triggers=triggers + row_triggers, properties=properties)
    gui += row("mod1440_records_officer_row", OF_ROW_W, OF_ROW, entry)

    # ---- script
    mark = setv("mod1440_of_seen_day", "global.num_days") + iff(
        "NOT = { %s }" % is_one("mod1440_of_known"), setv("mod1440_of_known", 1) + "add_to_array = { PREV.mod1440_of_known = THIS }\n")
    keep = tmp("of_keep", 1)
    former = "check_variable = { mod1440_of_seen_day < global.num_days }"
    keep += iff("check_variable = { ROOT.mod1440_of_show = 5 } NOT = { %s }" % former, tmp("of_keep", 0))
    keep += iff("NOT = { check_variable = { ROOT.mod1440_of_show = 5 } } " + former, tmp("of_keep", 0))
    keep += iff("check_variable = { ROOT.mod1440_of_show = 1 } is_navy_leader = yes", tmp("of_keep", 0))
    keep += iff("check_variable = { ROOT.mod1440_of_show = 2 } NOT = { is_navy_leader = yes }", tmp("of_keep", 0))
    keep += iff("check_variable = { ROOT.mod1440_of_show = 3 } check_variable = { num_units < 1 } check_variable = { num_ships < 1 }", tmp("of_keep", 0))
    keep += iff("check_variable = { ROOT.mod1440_of_show = 4 } check_variable = { mod1440_of_dec^num < 1 }", tmp("of_keep", 0))
    frames = "".join(setv("mod1440_of_frame_%d" % v, 1) for v, _, _, _ in OF_FILTERS)
    frames += "".join(iff("check_variable = { mod1440_of_show = %d }" % v, setv("mod1440_of_frame_%d" % v, 2)) for v, _, _, _ in OF_FILTERS)

    def date_copy(name):
        return (setv("PREV.mod1440_of_c_%s" % name, "mod1440_of_%s" % name) + setv("PREV.mod1440_of_c_has_%s" % name, 0)
                + iff("check_variable = { mod1440_of_%s_day > 0 }" % name, setv("PREV.mod1440_of_c_has_%s" % name, 1)))

    medals = "".join(iff("check_variable = { mod1440_md_id^num < %d } %s" % (MEDAL_SLOTS, available), (
        "add_to_array = { mod1440_md_id = %d }\nadd_to_array = { mod1440_md_key = token:%s }\n"
        "add_to_array = { mod1440_md_set = %d }\nadd_to_array = { mod1440_md_frame = %d }\n" % (n, name, sets.index(strip), frame)))
        for n, (name, strip, frame, available) in enumerate(MEDALS, start=1))
    script_effects = (
        "# Officers: marks every officer who serves today with the day, and adds an officer the record does not know\n"
        "# yet to its list. A retired officer keeps his place in that list (X34).\n"
        + block("mod1440_of_seen", block("for_each_scope_loop", "array = army_leaders\n" + mark)
                + block("for_each_scope_loop", "array = navy_leaders\n" + mark))
        + "\n# Officers: makes the list of the page again: who the filter wants, in the order of the chosen column,\n"
        "# every second row marked for its stripe.\n"
        + block("mod1440_of_list", (
            "mod1440_of_seen = yes\nclear_array = mod1440_of_rows\n"
            + block("for_each_scope_loop", "array = mod1440_of_known\n" + keep
                    + iff("check_variable = { of_keep = 1 }", "add_to_array = { ROOT.mod1440_of_rows = THIS }\n"))
            + iff("check_variable = { mod1440_of_sort_by > 0 }", (
                "clear_array = mod1440_of_keys\n"
                + block("for_each_scope_loop", "array = mod1440_of_rows\n" + tmp("of_key", 0) + keys
                        + iff(is_one("ROOT.mod1440_of_up"), "multiply_temp_variable = { of_key = -1 }\n")
                        + "add_to_array = { ROOT.mod1440_of_keys = of_key }\n")
                + "clear_array = mod1440_of_sorted\n"
                + block("for_loop_effect", "start = 0\nend = mod1440_of_rows^num\nvalue = of_step\n"
                        + block("find_highest_in_array", "array = mod1440_of_keys\nvalue = of_high\nindex = of_at\n")
                        + "add_to_array = { mod1440_of_sorted = mod1440_of_rows^of_at }\n" + setv("mod1440_of_keys^of_at", -2000000))
                + "clear_array = mod1440_of_rows\n"
                + block("for_each_loop", "array = mod1440_of_sorted\nvalue = of_copy\nadd_to_array = { mod1440_of_rows = of_copy }\n")))
            + tmp("of_par", 0) + block("for_each_scope_loop", "array = mod1440_of_rows\n" + setv("mod1440_of_odd", "of_par")
                                       + iff("check_variable = { of_par = 0 }", tmp("of_par", 1)) + els(tmp("of_par", 0)))
            + frames + "mod1440_md_list = yes\nmod1440_of_card = yes\n"))
        + "\n# Officers: copies the chosen officer's values, record, decorations and diary lines to the country, where\n"
        "# his file reads them. His own values are read in his scope (X33).\n"
        + block("mod1440_of_card", iff(is_one("mod1440_of_has_sel"), (
            "".join("clear_array = mod1440_of_c_%s\n" % part for part in DEC_ARRAYS[1:])
            + block("var:mod1440_of_sel", (
                setv("PREV.mod1440_of_c_skill", "skill_level") + setv("PREV.mod1440_of_c_rank", 2) + setv("PREV.mod1440_of_c_cmd", "num_units")
                + iff("is_field_marshal = yes", setv("PREV.mod1440_of_c_rank", 1))
                + iff("is_navy_leader = yes", setv("PREV.mod1440_of_c_rank", 3) + setv("PREV.mod1440_of_c_cmd", "num_ships"))
                + setv("PREV.mod1440_of_c_won", "mod1440_of_won") + setv("PREV.mod1440_of_c_lost", "mod1440_of_lost")
                + setv("PREV.mod1440_of_c_states", "mod1440_of_states")
                + date_copy("since") + date_copy("prom") + date_copy("lvl")
                + setv("PREV.mod1440_of_c_former", 0) + iff(former, setv("PREV.mod1440_of_c_former", 1))
                + "".join(block("for_each_loop", "array = mod1440_of_%s\nvalue = of_v\nadd_to_array = { PREV.mod1440_of_c_%s = of_v }\n" % (part, part))
                          for part in DEC_ARRAYS[1:])))
            + setv("mod1440_of_c_dec_n", "mod1440_of_c_dec_key^num")
            + pad([("mod1440_of_c_dec_key", BLANK), ("mod1440_of_c_dec_date", 0), ("mod1440_of_c_dec_set", -1), ("mod1440_of_c_dec_frame", 1)], CARD_LINES)
            # which of the medals on offer he holds already
            + block("for_each_loop", "array = mod1440_md_id\nvalue = md_v\nindex = md_i\n" + tmp("md_h", 0)
                    + block("var:mod1440_of_sel", iff("is_in_array = { array = mod1440_of_dec value = md_v }", tmp("md_h", 1)))
                    + setv("mod1440_md_has^md_i", "md_h"))
            + "clear_array = mod1440_of_ln_date\nclear_array = mod1440_of_ln_kind\n"
            + block("for_loop_effect", (
                "start = 0\nend = mod1440_ev_date^num\nvalue = of_n\n"
                + tmp("of_m", "mod1440_ev_date^num") + "subtract_from_temp_variable = { of_m = 1 }\nsubtract_from_temp_variable = { of_m = of_n }\n"
                + iff("check_variable = { mod1440_ev_sa^of_m = 1 } check_variable = { mod1440_ev_a^of_m = mod1440_of_sel } "
                      "check_variable = { mod1440_of_ln_date^num < %d }" % CARD_LINES,
                      "add_to_array = { mod1440_of_ln_date = mod1440_ev_date^of_m }\nadd_to_array = { mod1440_of_ln_kind = mod1440_ev_kind^of_m }\n")))
            + setv("mod1440_of_ln_n", "mod1440_of_ln_date^num")
            + pad([("mod1440_of_ln_date", 0), ("mod1440_of_ln_kind", BLANK)], CARD_LINES)))
            + "add_to_variable = { mod1440_rec_dirty = 1 }\n")
        + "\n# Officers: the medals the country in scope has, by the game's own conditions (tools/unit_medals_table.py),\n"
        "# %d at most. They fill the Award buttons of the file.\n" % MEDAL_SLOTS
        + block("mod1440_md_list", (
            "".join("clear_array = mod1440_md_%s\n" % part for part in ("id", "key", "set", "frame", "has")) + medals
            + setv("mod1440_md_count", "mod1440_md_id^num")
            + pad([("mod1440_md_id", 0), ("mod1440_md_key", BLANK), ("mod1440_md_set", -1), ("mod1440_md_frame", 1), ("mod1440_md_has", 0)], MEDAL_SLOTS)))
        + "\n# Officers: gives the chosen officer the medal of slot md_k, once. A record of the mod: arrays on the\n"
        "# officer. The War Diary gets a line.\n"
        + block("mod1440_md_award", iff(is_one("mod1440_of_has_sel") + " check_variable = { md_k < mod1440_md_count }", (
            tmp("md_id", "mod1440_md_id^md_k") + tmp("md_key", "mod1440_md_key^md_k") + tmp("md_set", "mod1440_md_set^md_k")
            + tmp("md_frame", "mod1440_md_frame^md_k") + tmp("md_done", 0)
            + block("var:mod1440_of_sel", iff("NOT = { is_in_array = { array = mod1440_of_dec value = md_id } }", (
                "add_to_array = { mod1440_of_dec = md_id }\nadd_to_array = { mod1440_of_dec_key = md_key }\n"
                "add_to_array = { mod1440_of_dec_date = global.date }\nadd_to_array = { mod1440_of_dec_set = md_set }\n"
                "add_to_array = { mod1440_of_dec_frame = md_frame }\n" + tmp("md_done", 1))))
            + iff("check_variable = { md_done = 1 }", line("decorated", a="mod1440_of_sel"))
            + "mod1440_of_card = yes\n")))
        + block("mod1440_md_takeback", iff(is_one("mod1440_of_has_sel"), (
            block("var:mod1440_of_sel", iff("check_variable = { mod1440_of_dec^num > 0 }", (
                tmp("md_n", "mod1440_of_dec^num") + "subtract_from_temp_variable = { md_n = 1 }\n"
                + "".join("remove_from_array = { array = mod1440_of_%s index = md_n }\n" % part for part in DEC_ARRAYS))))
            + "mod1440_of_card = yes\n"))))

    # ---- hooks: the officer is the scope, FROM his country (X43)
    human = "FROM = { is_ai = no }"

    def dated(name, kind):
        return iff(human, setv("mod1440_of_%s" % name, "global.date") + setv("mod1440_of_%s_day" % name, "global.num_days")
                   + fill(kind, a="THIS") + block("FROM", "mod1440_ev_add = yes\n"))

    hooks = {
        "on_unit_leader_created": dated("since", "commissioned"),
        "on_army_leader_promoted": dated("prom", "promoted"),
        "on_unit_leader_level_up": dated("lvl", "level"),
        "on_army_leader_won_combat": iff(human, "add_to_variable = { mod1440_of_won = 1 }\n"),
        "on_army_leader_lost_combat": iff(human, "add_to_variable = { mod1440_of_lost = 1 }\n"),
        "on_navy_leader_won_combat": iff(human, "add_to_variable = { mod1440_of_won = 1 }\n"),
        "on_navy_leader_lost_combat": iff(human, "add_to_variable = { mod1440_of_lost = 1 }\n"),
    }
    return gui, script, script_effects, hooks


# ---------------------------------------------------------------- Government (E3)

GV_COL = (REC_W - 28 - 24) // 3
GV_ROW = 26
GV_H = REC_H - 62 - 14          # what a column has from the title strip to the bottom
GV_LIST_ROW_W = GV_COL - 16 - 30
OFFICES = [("army_chief", "is_army_chief", "Chief of the army"), ("navy_chief", "is_navy_chief", "Chief of the navy"),
           ("air_chief", "is_air_chief", "Chief of the air force"), ("theorist", "is_theorist", "Theorist")]
IDEOLOGIES = [("Fascist", "fascism"), ("Democratic", "democratic"), ("Communist", "communism"), ("Neutral", "neutrality")]
# The laws of the vanilla game, by the idea that holds each. Another mod's law reads "another law".
LAWS = [
    ("Economy", ["undisturbed_isolation", "isolation", "civilian_economy", "low_economic_mobilisation", "partial_economic_mobilisation",
                 "war_economy", "tot_economic_mobilisation", "totaler_krieg_economy", "national_defense_state", "new_economic_policy",
                 "new_economic_policy_2", "capital_investment_model", "JAP_war_communism_idea", "SPR_collectivized_society"]),
    ("Trade", ["uncontrolled_exports", "free_trade", "export_focus", "limited_exports", "autarkic_economy", "autarkic_economy_improved",
               "closed_economy", "special_economic_zones"]),
    ("Conscription", ["disarmed_nation", "volunteer_only", "limited_conscription", "extensive_conscription", "service_by_requirement",
                      "all_adults_serve", "scraping_the_barrel", "ETH_chitet_law", "ETH_chitet_law_peace_time", "SWI_citizen_militia_1",
                      "SWI_citizen_militia_2"]),
]
BEGAN = "before the record"
GV_FIGURES = [("elections", "Elections", ("election",), "Elections held since the record began."),
              ("changes", "Changes of rule", ("party", "government"), "Changes of the ruling party or of the government."),
              ("heads", "New heads", ("leader",), "Heads of government who took office."),
              ("appointed", "Appointments", ("appointed",), "Advisors, chiefs and members of the high command who took office.")]


def government():
    body, effects, properties = head("gv", 2, "Who rules and who serves. A date is the day the mod first saw the name in office.")
    triggers = ""
    lists = ""
    extra_gui = ""
    bottoms = [62, 62, 62]

    def place(column, name, title, inner, height):
        nonlocal body
        body += card("gv_" + name, 14 + column * (GV_COL + 12), bottoms[column], GV_COL, height, title, inner)
        bottoms[column] += height + 12

    def pair(name, n, label, value):
        return (M.text("gv_%s_l" % name, 16, 46 + n * GV_ROW, 200, B.key("gv_%s_l" % name, label), M.FONT_SMALL, height=22)
                + M.text("gv_%s" % name, 220, 44 + n * GV_ROW, GV_COL - 236, B.key("gv_%s" % name, value), M.FONT_LABEL, height=22))

    def since(name, x, y, date, old, width, fmt="left", word=""):
        """A date, or the words for an office held when the record began: the widgets and their triggers."""
        out = M.text(name, x, y, width, B.key(name, "%s[?%s.%s]" % (word, date, LONG)), M.FONT_SMALL, fmt, 22)
        out += M.text(name + "_old", x, y, width, B.key("gv_began", BEGAN), M.FONT_SMALL, fmt, 22)
        return out, block(name + "_visible", "check_variable = { %s = 0 }\n" % old) + block(name + "_old_visible", "check_variable = { %s = 1 }\n" % old)

    # ---- column 1: who rules
    inner = M.text("gv_leader", 16, 44, GV_COL - 32, B.key("gv_leader", "[ROOT.GetLeader]"), M.FONT_TITLE, height=40)
    inner += M.text("gv_party", 18, 88, GV_COL - 36, B.key("gv_party", "§Y[ROOT.GetRulingParty]§!, [ROOT.GetRulingIdeology]"), M.FONT_LABEL, height=22)
    inner += M.text("gv_party_long", 18, 112, GV_COL - 36, B.key("gv_party_long", "[ROOT.GetRulingPartyLong]"), M.FONT_SMALL, height=22)
    inner += M.text("gv_office_l", 18, 144, 200, B.key("gv_office_l", "In office"), M.FONT_SMALL, height=22)
    piece, extra = since("gv_leader_since", 220, 144, "mod1440_gv_leader_since", "mod1440_gv_leader_old", GV_COL - 236, word="since ")
    inner += piece
    triggers += extra
    inner += M.text("gv_election_l", 18, 144 + GV_ROW, 200, B.key("gv_election_l", "Last election"), M.FONT_SMALL, height=22)
    inner += M.text("gv_election", 220, 144 + GV_ROW, GV_COL - 236, B.key("gv_election", "[ROOT.GetLastElection]"), M.FONT_SMALL, height=22)
    inner += M.text("gv_next_l", 18, 144 + 2 * GV_ROW, 200, B.key("gv_next_l", "Next election"), M.FONT_SMALL, height=22)
    inner += M.text("gv_next", 220, 144 + 2 * GV_ROW, GV_COL - 236, B.key("gv_next", "in [?days_until_next_election|0] days"), M.FONT_SMALL, height=22)
    inner += M.text("gv_next_none", 220, 144 + 2 * GV_ROW, GV_COL - 236, B.key("gv_next_none", "none"), M.FONT_SMALL, height=22)
    triggers += block("gv_next_visible", "check_variable = { days_until_next_election > -1 }\n")
    triggers += block("gv_next_none_visible", "check_variable = { days_until_next_election < 0 }\n")
    place(0, "chief", "Head of government", inner, 144 + 3 * GV_ROW + 12)

    # parties: the name and its share, the leader, and a bar as long as the party's support
    inner = ""
    for n, (ideology, token_name) in enumerate(IDEOLOGIES):
        y = 44 + n * 62
        inner += M.text("gv_p_%d" % n, 18, y, GV_COL - 110, B.key("gv_p_%d" % n, "[ROOT.Get%sParty]" % ideology), M.FONT_SMALL, height=22)
        inner += M.text("gv_p_%d_pop" % n, GV_COL - 96, y - 2, 80, B.key("gv_p_%d_pop" % n, "[?party_popularity@%s|%%0]" % token_name), M.FONT_VALUE, "right", 24)
        inner += M.text("gv_p_%d_who" % n, 18, y + 20, GV_COL - 36, B.key("gv_p_%d_who" % n, "§Y[ROOT.Get%sLeader]§!" % ideology), M.FONT_SMALL, height=22)
        inner += M.icon("gv_p_%d_bar" % n, 18, y + 44, "GFX_1440p_SG_bar_wide")
        properties += block("gv_p_%d_bar" % n, "frame = mod1440_gv_pop_%d\n" % n)
    place(0, "parties", "Parties", inner, 44 + 4 * 62 + 6)

    inner = "".join(pair("law_%d" % n, n, label, "[?mod1440_gv_law_%d.GetTokenLocalizedKey]" % n) for n, (label, ideas) in enumerate(LAWS))
    place(0, "laws", "Laws", inner, 46 + len(LAWS) * GV_ROW + 12)

    inner = pair("capital", 0, "Capital", "[ROOT.Capital.GetName]") + pair("agency", 1, "Intelligence", "[ROOT.GetAgency]")
    inner += pair("operatives", 2, "Operatives", "[?num_of_operatives|0]")
    place(0, "state", "State", inner, 46 + 3 * GV_ROW + 12)

    sums = ""
    inner = ""
    for n, (name, label, kinds, tip) in enumerate(GV_FIGURES):
        piece, extra = tile("gv_f_" + name, (GV_COL - 2 * TILE_W - 12) // 2 + (n % 2) * (TILE_W + 12), 48 + (n // 2) * (TILE_H + 10), label, "[?mod1440_gv_n_%s|0]" % name, tip)
        inner += piece
        sums += count(*kinds) + setv("mod1440_gv_n_" + name, "ct_sum")
    place(0, "record", "Since the record began", inner, GV_H - (bottoms[0] - 62))

    # ---- column 2: who serves. A list is read by row index: an advisor has no scope in a row (X42)
    def people(name, array, top, height):
        nonlocal triggers, lists, extra_gui
        out = listing("gv_%s_list" % name, "gv_%s_grid" % name, 8, top, GV_COL - 16, height, GV_ROW)
        out += M.text("gv_%s_none" % name, 22, top + 8, 400, B.key("gv_%s_none" % name, "Nobody is appointed."), M.FONT_SMALL, height=22)
        triggers += block("gv_%s_none_visible" % name, "check_variable = { %s^num < 1 }\n" % array)
        entry = M.icon("gv_%s_row_stripe" % name, 0, 0, STRIPE % (GV_LIST_ROW_W, GV_ROW))
        entry += M.text("gv_%s_row_name" % name, 10, 2, GV_LIST_ROW_W - 200, B.key("gv_%s_row_name" % name, "§Y[?%s^i.GetName]§!" % array), M.FONT_LABEL, height=22)
        piece, extra = since("gv_%s_row_since" % name, GV_LIST_ROW_W - 184, 4, "%s_since^i" % array, "v", 176, "right")
        entry += piece
        triggers += extra + block("gv_%s_row_stripe_visible" % name, "check_variable = { mod1440_odd^i = 1 }\n")
        lists += block("gv_%s_grid" % name, 'array = %s_old\nentry_container = "mod1440_records_%s_row"\n' % (array, name))
        extra_gui += row("mod1440_records_%s_row" % name, GV_LIST_ROW_W, GV_ROW, entry)
        return out

    cabinet_h = 44 + 10 * GV_ROW + 4 + 12
    place(1, "adv", "Cabinet", people("adv", "mod1440_gv_adv", 44, 10 * GV_ROW + 4), cabinet_h)
    inner = ""
    for k, (variable, trigger, label) in enumerate(OFFICES):
        y = 46 + k * GV_ROW
        inner += M.text("gv_of_%d_l" % k, 18, y, 170, B.key("gv_of_%d_l" % k, label), M.FONT_SMALL, height=22)
        inner += M.text("gv_of_%d" % k, 190, y - 2, 190, B.key("gv_of_%d" % k, "§Y[?mod1440_gv_of_%d.GetName]§!" % k), M.FONT_LABEL, height=22)
        inner += M.text("gv_of_%d_none" % k, 190, y, 190, B.key("gv_vacant", "vacant"), M.FONT_SMALL, height=22)
        piece, extra = since("gv_of_%d_since" % k, GV_COL - 196, y, "mod1440_gv_of_%d_since" % k, "mod1440_gv_of_%d_old" % k, 178, "right")
        inner += piece
        has = is_one("mod1440_gv_of_%d_has" % k)
        triggers += block("gv_of_%d_visible" % k, has + "\n") + block("gv_of_%d_none_visible" % k, "NOT = { %s }\n" % has)
        triggers += extra.replace("check_variable = { mod1440_gv_of_%d_old" % k, has + "\ncheck_variable = { mod1440_gv_of_%d_old" % k)
    top = 46 + len(OFFICES) * GV_ROW + 10
    hc_h = GV_H - cabinet_h - 12
    place(1, "hc", "High command", inner + people("hc", "mod1440_gv_hc", top, hc_h - top - 12), hc_h)

    # ---- column 3: the faction and the subjects
    def countries(name, array, top, height):
        nonlocal lists, extra_gui, triggers
        lists += block("gv_%s_grid" % name, 'array = %s\nchange_scope = yes\nentry_container = "mod1440_records_%s_row"\n' % (array, name))
        extra_gui += row("mod1440_records_%s_row" % name, GV_LIST_ROW_W, GV_ROW,
                         M.text("gv_%s_row_name" % name, 10, 2, GV_LIST_ROW_W - 18, B.key("gv_country_row", "[THIS.GetNameWithFlag]"), M.FONT_LABEL, height=22))
        return listing("gv_%s_list" % name, "gv_%s_grid" % name, 8, top, GV_COL - 16, height, GV_ROW)

    faction_h = 600
    inner = M.text("gv_faction", 16, 44, GV_COL - 32, B.key("gv_faction", "[ROOT.GetFactionName]"), M.FONT_TITLE, height=40)
    inner += M.text("gv_faction_none", 18, 52, GV_COL - 36, B.key("gv_faction_none", "In no faction."), M.FONT_LABEL, height=22)
    triggers += block("gv_faction_visible", "is_in_faction = yes\n") + block("gv_faction_none_visible", "is_in_faction = no\n")
    inner += M.text("gv_members_l", 18, 90, 300, B.key("gv_members_l", "Members"), M.FONT_SMALL, height=22)
    inner += M.text("gv_members_n", GV_COL - 120, 90, 100, B.key("gv_members_n", "[?mod1440_gv_fac^num|0]"), M.FONT_SMALL, "right", 22)
    inner += countries("fac", "mod1440_gv_fac", 114, faction_h - 114 - 12)
    place(2, "faction", "Faction", inner, faction_h)
    inner = M.text("gv_subjects_n", GV_COL - 120, 14, 100, B.key("gv_subjects_n", "[?mod1440_ev_subjects^num|0]"), M.FONT_SMALL, "right", 22)
    inner += M.text("gv_sub_none", 22, 52, 400, B.key("gv_sub_none", "No subjects."), M.FONT_SMALL, height=22)
    triggers += block("gv_sub_none_visible", "check_variable = { mod1440_ev_subjects^num < 1 }\n")
    subjects_h = GV_H - faction_h - 12
    inner += countries("sub", "mod1440_ev_subjects", 44, subjects_h - 44 - 12)
    place(2, "subjects", "Subjects", inner, subjects_h)

    gui, script = page_gui("gv", 2, body, lists=lists, effects=effects, triggers=triggers, properties=properties)
    gui += extra_gui

    # ---- script: the daily comparison of offices
    begun = is_one("mod1440_gv_begun")

    def office_array(game, copy):
        return (
            "clear_array = mod1440_gv_new\nclear_array = mod1440_gv_new_since\nclear_array = mod1440_gv_new_old\n"
            + block("for_each_loop", (
                "array = %s\nvalue = gv_c\n" % game + tmp("gv_since", "global.date") + tmp("gv_old", 1) + iff(begun, tmp("gv_old", 0)) + tmp("gv_found", 0)
                + block("for_each_loop", "array = %s\nvalue = gv_o\nindex = gv_j\n" % copy + iff(
                    "check_variable = { gv_o = gv_c }", tmp("gv_found", 1) + tmp("gv_since", "%s_since^gv_j" % copy) + tmp("gv_old", "%s_old^gv_j" % copy)))
                + iff("check_variable = { gv_found = 0 } " + begun, line("appointed", a="gv_c"))
                + "add_to_array = { mod1440_gv_new = gv_c }\nadd_to_array = { mod1440_gv_new_since = gv_since }\nadd_to_array = { mod1440_gv_new_old = gv_old }\n"))
            + block("for_each_loop", "array = %s\nvalue = gv_o\n" % copy + iff(
                "NOT = { is_in_array = { array = %s value = gv_o } } %s" % (game, begun), line("dismissed", a="gv_o")))
            + "".join("clear_array = %s%s\n" % (copy, part) + block(
                "for_each_loop", "array = mod1440_gv_new%s\nvalue = gv_o\nadd_to_array = { %s%s = gv_o }\n" % (part, copy, part))
                for part in ("", "_since", "_old")))

    offices = ""
    for k, (variable, trigger, label) in enumerate(OFFICES):
        holder = "mod1440_gv_of_%d" % k
        offices += iff("any_character = { %s = yes }" % trigger, iff(
            "NOT = { %s check_variable = { %s = %s } }" % (is_one(holder + "_has"), holder, variable), (
                setv(holder, variable) + setv(holder + "_has", 1) + setv(holder + "_since", "global.date") + setv(holder + "_old", 1)
                + iff(begun, setv(holder + "_old", 0) + line("appointed", a=variable)))))
        offices += els(iff(is_one(holder + "_has"), setv(holder + "_has", 0) + iff(begun, line("dismissed", a=holder))))
    laws = ""
    for n, (label, ideas) in enumerate(LAWS):
        laws += setv("mod1440_gv_law_%d" % n, token("gv_law_other", "another law"))
        laws += "".join(iff("has_idea = %s" % idea, setv("mod1440_gv_law_%d" % n, "token:" + idea)) for idea in ideas)
    support = "".join(setv("mod1440_gv_pop_%d" % n, "party_popularity_100@" + token_name) for n, (ideology, token_name) in enumerate(IDEOLOGIES))
    script_effects = (
        "# Government: compares who holds each office with yesterday's copy. A new name gets today's date and a line\n"
        "# in the War Diary, a name that is gone a line. The first run only takes the copy. Then the laws in force,\n"
        "# the length of the parties' bars and the figures of the record.\n"
        + block("mod1440_gv_daily", (
            iff("NOT = { check_variable = { mod1440_gv_leader = country_leader } }", (
                setv("mod1440_gv_leader", "country_leader") + setv("mod1440_gv_leader_since", "global.date") + setv("mod1440_gv_leader_old", 1)
                + iff(begun, setv("mod1440_gv_leader_old", 0) + line("leader", a="country_leader"))))
            + offices + office_array("political_advisor", "mod1440_gv_adv") + office_array("high_command", "mod1440_gv_hc")
            + laws + support + pad([("mod1440_ct", 0)], len(KINDS) + 8) + sums + setv("mod1440_gv_begun", 1))))
    return gui, script, script_effects


# ---------------------------------------------------------------- Wars (E4), with the counters of the air war (E5)

WR_ROW_W = REC_W - 28 - 30
WR_ROW = 30
WR_PARTS = ["enemy", "since", "day0", "cas0", "taken", "lost", "days", "cas", "capd", "old", "surr"]
WO_PARTS = ["enemy", "since", "until", "days", "cas", "taken", "lost", "outcome", "old"]
WO_KEEP = 200
# a column of the two tables: (name, x, width, format, head, tooltip)
WR_COLUMNS = [("since", 390, 180, "left", "Since", None), ("until", 580, 180, "left", "Until", None),
              ("days", 770, 70, "right", "Days", None),
              ("cas", 850, 150, "right", "Our casualties", "Your country's whole loss in that time, whoever caused it."),
              ("taken", 1010, 80, "right", "Taken", "States you took from this enemy."), ("lost", 1100, 80, "right", "Lost", "States you lost to this enemy."),
              ("surrender", 1200, 180, "left", "Surrender", "How close the enemy is to capitulating."),
              ("outcome", 1390, 220, "left", "Outcome", None)]
WR_FIGURES = [
    ("cas", "Casualties", "[?casualties|0]", "Your dead of all wars."),
    ("convoys", "Convoys sunk", "[?convoys_destroyed|0]", "Enemy convoys your country has sunk."),
    ("longest", "Longest war", "[?longest_war_length|0] mo.", "Months of your longest war."),
    ("surrender", "Our surrender", "[?surrender_progress|%0]", "How close your country is to capitulating."),
    ("ws_cas", "Lost to casualties", "[?has_casualties_war_support|%1]", "War support lost to casualties."),
    ("ws_con", "Lost to convoys", "[?has_convoys_war_support|%1]", "War support lost to sunk convoys."),
    ("ws_bomb", "Lost to bombing", "[?has_bombing_war_support|%1]", "War support lost to enemy bombing."),
    ("ace_new", "Aces promoted", "[?mod1440_ac_new|0]", "Pilots of yours who became aces."),
    ("ace_lost", "Aces lost", "[?mod1440_ac_lost|0]", "Aces of yours who were killed."),
    ("ace_down", "Enemy aces downed", "[?mod1440_ac_down|0]", "Enemy aces your air force shot down."),
]


def wars():
    body, effects, properties = head("wr", 3, "One row per enemy. Casualties are your country's whole loss in that time, whoever caused it.")
    triggers = ""
    step = (REC_W - 28 - len(WR_FIGURES) * TILE_W) // (len(WR_FIGURES) - 1) + TILE_W
    for n, (name, label, value, tip) in enumerate(WR_FIGURES):
        piece, extra = tile("wr_f_" + name, 14 + n * step, 62, label, value, tip)
        body += piece

    def columns(name, y, skip):
        return heads(name, 14, y, REC_W - 28, [(10, 360, "Country", "left", None)] + [
            (x, width, label, fmt, tip) for column, x, width, fmt, label, tip in WR_COLUMNS if column not in skip])

    now_h = 9 * WR_ROW + 4
    body += M.text("wr_now_title", 20, 136, 400, B.key("wr_now_title", "At war with"), M.FONT_CARD, height=30)
    body += columns("wr_now_heads", 170, ("until",))
    body += listing("wr_now_list", "wr_now_grid", 14, 202, REC_W - 28, now_h, WR_ROW)
    body += M.text("wr_now_none", 40, 214, 600, B.key("wr_now_none", "At peace."), M.FONT_LABEL)
    triggers += block("wr_now_none_visible", "check_variable = { mod1440_wr_enemy^num < 1 }\n")
    y = 202 + now_h + 12
    body += M.text("wr_old_title", 20, y, 400, B.key("wr_old_title", "Finished wars"), M.FONT_CARD, height=30)
    body += columns("wr_old_heads", y + 34, ("surrender",))
    body += listing("wr_old_list", "wr_old_grid", 14, y + 66, REC_W - 28, REC_H - (y + 66) - 14, WR_ROW)
    body += M.text("wr_old_none", 40, y + 78, 600, B.key("wr_old_none", "None since the record began."), M.FONT_LABEL)
    triggers += block("wr_old_none_visible", "check_variable = { mod1440_wo_enemy^num < 1 }\n")

    def cells(prefix, texts, old_test):
        nonlocal triggers
        out = M.icon(prefix + "_stripe", 0, 0, STRIPE % (WR_ROW_W, WR_ROW))
        triggers += block(prefix + "_stripe_visible", "check_variable = { mod1440_odd^i = 1 }\n")
        for name, x, width, fmt, label, tip in WR_COLUMNS:
            if name in texts:
                out += M.text("%s_%s" % (prefix, name), x, 4, width, B.key("%s_%s" % (prefix, name), texts[name]), M.FONT_LABEL, fmt, 22)
        out += M.text(prefix + "_since_old", 390, 5, 180, B.key("gv_began", BEGAN), M.FONT_SMALL, height=22)
        triggers += block(prefix + "_since_visible", "NOT = { %s }\n" % old_test) + block(prefix + "_since_old_visible", old_test + "\n")
        return out

    # today's enemies, read by row index; the list runs over the surrender progress, which fills the bar
    entry = cells("wr_row", {
        "since": "[?mod1440_wr_since^i.%s]" % LONG, "days": "[?mod1440_wr_days^i|0]", "cas": "[?mod1440_wr_cas^i|0]",
        "taken": "[?mod1440_wr_taken^i|0]", "lost": "[?mod1440_wr_lost^i|0]", "outcome": "§Gcapitulated§!"},
        "check_variable = { mod1440_wr_old^i = 1 }")
    entry += M.text("wr_row_enemy", 10, 4, 370, B.key("wr_row_enemy", "§Y[?mod1440_wr_enemy^i.GetNameWithFlag]§!"), M.FONT_LABEL, height=22)
    entry += M.icon("wr_row_bar", 1200, 9, "GFX_1440p_SG_bar")
    entry += M.text("wr_row_pct", 1312, 4, 60, B.key("wr_row_pct", "[?v|0]%"), M.FONT_LABEL, "right", 22)
    properties += block("wr_row_bar", "frame = v\n")
    triggers += block("wr_row_outcome_visible", "check_variable = { mod1440_wr_capd^i > 0 }\n")
    gui_rows = row("mod1440_records_war_row", WR_ROW_W, WR_ROW, entry)
    # finished wars: the list runs over the days, so v is the length of the war
    entry = cells("wo_row", {
        "since": "[?mod1440_wo_since^i.%s]" % LONG, "until": "[?mod1440_wo_until^i.%s]" % LONG, "days": "[?v|0]",
        "cas": "[?mod1440_wo_cas^i|0]", "taken": "[?mod1440_wo_taken^i|0]", "lost": "[?mod1440_wo_lost^i|0]",
        "outcome": "[?mod1440_wo_outcome^i.GetTokenLocalizedKey]"}, "check_variable = { mod1440_wo_old^i = 1 }")
    entry += M.text("wo_row_enemy", 10, 4, 370, B.key("wo_row_enemy", "§Y[?mod1440_wo_enemy^i.GetNameWithFlag]§!"), M.FONT_LABEL, height=22)
    gui_rows += row("mod1440_records_past_war_row", WR_ROW_W, WR_ROW, entry)

    lists = block("wr_now_grid", 'array = mod1440_wr_surr\nentry_container = "mod1440_records_war_row"\n')
    lists += block("wr_old_grid", 'array = mod1440_wo_days\nentry_container = "mod1440_records_past_war_row"\n')
    gui, script = page_gui("wr", 3, body, lists=lists, effects=effects, triggers=triggers, properties=properties)
    gui += gui_rows

    # ---- script
    outcomes = dict((name, token("wr_out_" + name, words)) for name, words in (
        ("peace", "Peace"), ("capitulated", "Capitulated"), ("subject", "Made a subject"), ("annexed", "Annexed"), ("gone", "No longer exists")))
    find = tmp("wr_j", -1) + block("for_each_loop", "array = mod1440_wr_enemy\nvalue = wr_v\nindex = wr_i\n"
                                   + iff("check_variable = { wr_v = wr_c }", tmp("wr_j", "wr_i")))
    start = {"enemy": "wr_c", "since": "global.date", "day0": "global.num_days", "cas0": "casualties", "taken": 0, "lost": 0, "days": 0,
             "cas": 0, "capd": 0, "old": "wr_old", "surr": 0}
    end = {"enemy": "wr_c", "since": "mod1440_wr_since^wr_j", "until": "global.date", "days": "wr_d", "cas": "wr_k",
           "taken": "mod1440_wr_taken^wr_j", "lost": "mod1440_wr_lost^wr_j", "outcome": "wr_out", "old": "mod1440_wr_old^wr_j"}
    script_effects = (
        "# Wars: a row for the enemy in wr_c, from today (wr_old = 1: the war ran when the record began).\n"
        + block("mod1440_wr_open", iff("NOT = { is_in_array = { array = mod1440_wr_enemy value = wr_c } }",
                                       "".join("add_to_array = { mod1440_wr_%s = %s }\n" % (part, start[part]) for part in WR_PARTS)))
        + "\n# Wars: the war with wr_c is over: its row moves to the finished wars with the end date, its length, what it\n"
        "# cost and how it ended.\n"
        + block("mod1440_wr_close", find + iff("check_variable = { wr_j > -1 }", (
            tmp("wr_out", outcomes["peace"])
            + iff("check_variable = { mod1440_wr_capd^wr_j = 1 }", tmp("wr_out", outcomes["capitulated"]))
            + iff("is_in_array = { array = subjects value = wr_c }", tmp("wr_out", outcomes["subject"]))
            + iff("var:wr_c = { exists = no }", tmp("wr_out", outcomes["gone"]))
            + iff("check_variable = { mod1440_wr_capd^wr_j = 2 }", tmp("wr_out", outcomes["annexed"]))
            + tmp("wr_d", "global.num_days") + "subtract_from_temp_variable = { wr_d = mod1440_wr_day0^wr_j }\n"
            + tmp("wr_k", "casualties") + "subtract_from_temp_variable = { wr_k = mod1440_wr_cas0^wr_j }\n"
            + "".join("add_to_array = { array = mod1440_wo_%s value = %s index = 0 }\n" % (part, end[part]) for part in WO_PARTS)
            + "".join("remove_from_array = { array = mod1440_wr_%s index = wr_j }\n" % part for part in WR_PARTS)
            + iff("check_variable = { mod1440_wo_enemy^num > %d }" % WO_KEEP, (
                tmp("wr_last", "mod1440_wo_enemy^num") + "subtract_from_temp_variable = { wr_last = 1 }\n"
                + "".join("remove_from_array = { array = mod1440_wo_%s index = wr_last }\n" % part for part in WO_PARTS))))))
        + "\n# Wars: one more state taken from (wr_f = 1) or lost to (wr_f = 2) the enemy in wr_c.\n"
        + block("mod1440_wr_count", find + iff("check_variable = { wr_j > -1 }", (
            iff("check_variable = { wr_f = 1 }", "add_to_variable = { mod1440_wr_taken^wr_j = 1 }\n")
            + iff("check_variable = { wr_f = 2 }", "add_to_variable = { mod1440_wr_lost^wr_j = 1 }\n"))))
        + block("mod1440_wr_annexed", find + iff("check_variable = { wr_j > -1 }", setv("mod1440_wr_capd^wr_j", 2)))
        + "\n# Wars: the numbers of today's rows, each enemy's surrender progress for its bar, and a line in the War\n"
        "# Diary when an enemy or the country itself has capitulated.\n"
        + block("mod1440_wr_daily", (
            block("for_each_loop", (
                "array = mod1440_wr_enemy\nvalue = wr_v\nindex = wr_i\n"
                + tmp("wr_d", "global.num_days") + "subtract_from_temp_variable = { wr_d = mod1440_wr_day0^wr_i }\n" + setv("mod1440_wr_days^wr_i", "wr_d")
                + tmp("wr_k", "casualties") + "subtract_from_temp_variable = { wr_k = mod1440_wr_cas0^wr_i }\n" + setv("mod1440_wr_cas^wr_i", "wr_k")
                + tmp("wr_s", 0) + block("var:wr_v", tmp("wr_s", "surrender_progress")) + "multiply_temp_variable = { wr_s = 100 }\n"
                + setv("mod1440_wr_surr^wr_i", "wr_s")
                + iff("check_variable = { mod1440_wr_capd^wr_i = 0 } var:wr_v = { has_capitulated = yes }",
                      setv("mod1440_wr_capd^wr_i", 1) + line("capitulated", b="wr_v"))))
            + iff("has_capitulated = yes NOT = { %s }" % is_one("mod1440_ev_capd"), setv("mod1440_ev_capd", 1) + line("we_capitulated"))
            + iff("has_capitulated = no", setv("mod1440_ev_capd", 0)))))
    return gui, script, script_effects


# ---------------------------------------------------------------- the frame: button, state card, hooks, daily run

HONOUR_DLC = 'has_dlc = "By Blood Alone"'


def open_war(country, old=0):
    return tmp("wr_c", country) + tmp("wr_old", old) + "mod1440_wr_open = yes\n"


def frame():
    """The top bar button, the card in the state view, and the script that ties the pages together."""
    handle = M.button("rec_toggle", 0, 0, "GFX_button_148x34", B.key("rec_toggle", "Records"), shortcut="shift+j",
                      tooltip=B.key("rec_toggle_tt", "The War Diary, your officers, your government and your wars"))
    gui = M.box("mod1440_records_handle", 1300, 4, 148, 34, handle)
    script = M.scripted_gui("mod1440_records_handle", "mod1440_records_handle", "top_bar", effects=block(
        "rec_toggle_click", "mod1440_ev_init = yes\n" + flip("mod1440_rec_open") + iff(is_one("mod1440_rec_open"), "mod1440_rec_show = yes\n")))

    # ---- the state card (E1 part C, E6): what the record knows of the selected state, and the citation
    inner = M.text("sc_title", 12, 6, 200, B.key("sc_title", "The record"), M.FONT_SMALL, height=22)
    inner += M.text("sc_taken", 12, 28, 476, B.key("sc_taken", "Taken from §Y[?mod1440_sr_from.GetNameWithFlag]§! on [?mod1440_sr_date.%s]" % LONG),
                    M.FONT_LABEL, height=22)
    inner += M.text("sc_untaken", 12, 28, 476, B.key("sc_untaken", "Yours since before the record began."), M.FONT_LABEL, height=22)
    inner += M.button("sc_cite", 12, 56, "GFX_sort_button_202x29", B.key("sc_cite", "Cite the divisions here"), tooltip=B.key(
        "sc_cite_tt", "Every division of yours that stands in this state gets a line in its own history: Cited by the high command. "
                      "You can then award a medal for it in the division's history, at the game's price. A division takes one line a day."))
    inner += M.text("sc_cited", 224, 60, 260, B.key("sc_cited", "§G[?mod1440_sr_cited|0] divisions cited today§!"), M.FONT_SMALL, height=22)
    gui += M.box("mod1440_state_card", 470, 0, 500, 94, inner, M.CARD_BG)
    cite = (tmp("hn_n", 0)
            + block("every_state_division", "limit = { OWNER = { tag = ROOT } }\n" + block(
                "add_history_entry", 'key = mod1440_hn_cited\nsubject = "Citation"\nallow = yes\n') + "add_to_temp_variable = { hn_n = 1 }\n")
            + setv("mod1440_sr_cited", "hn_n") + setv("mod1440_sr_cited_day", "global.num_days")
            + iff("check_variable = { hn_n > 0 }", fill("cited", a="THIS", state=True)
                  + block("ROOT", "mod1440_tr_add = yes\nadd_to_variable = { mod1440_hn_count = hn_n }\n")))
    mine = "is_controlled_by = ROOT\n"
    state_script = block("mod1440_state_card", (
        'context_type = selected_state_context\nwindow_name = "mod1440_state_card"\nparent_window_token = selected_state_view\n\n'
        + block("visible", mine) + "\n" + block("effects", block("sc_cite_click", cite)) + "\n"
        + block("triggers", (
            block("sc_taken_visible", "check_variable = { mod1440_sr_day > 0 }\n")
            + block("sc_untaken_visible", "check_variable = { mod1440_sr_day < 1 }\n")
            + block("sc_cite_visible", HONOUR_DLC + "\n")
            + block("sc_cited_visible", "check_variable = { mod1440_sr_cited_day = global.num_days }\ncheck_variable = { mod1440_sr_cited > 0 }\n")))
        + "\n" + block("ai_enabled", "always = no\n")))
    token("hn_capture", "Took part in the capture of $PROVINCE$")
    token("hn_cited", "Cited by the high command at $PROVINCE$")

    # ---- script
    tabs = "".join(setv("mod1440_rec_tab_%d" % n, 1) for n in range(len(PAGES)))
    tabs += "".join(iff("check_variable = { mod1440_rec_page = %d }" % n, setv("mod1440_rec_tab_%d" % n, 2)) for n in range(len(PAGES)))
    lists = ["mod1440_wd_list = yes\n", "mod1440_of_list = yes\n", "mod1440_gv_daily = yes\n", "mod1440_wr_daily = yes\n"]
    show = "mod1440_rec_odd = yes\n" + tabs + setv("mod1440_hn_frame", 1) + iff(is_one("mod1440_hn_auto"), setv("mod1440_hn_frame", 2))
    show += "".join(iff("check_variable = { mod1440_rec_page = %d }" % n, lists[n]) for n in range(len(PAGES)))

    copy_members = "clear_array = mod1440_gv_fac\n" + block(
        "for_each_loop", "array = faction_members\nvalue = ev_c\nadd_to_array = { mod1440_gv_fac = ev_c }\n")
    in_faction = tmp("ev_in", 0) + iff("is_in_faction = yes", tmp("ev_in", 1))
    credit = (tmp("of_best", 0) + block("for_each_loop", (
        "array = army_leaders\nvalue = of_l\n" + block("var:of_l", tmp("of_n", "num_units_in_state@var:tr_s"))
        + iff("check_variable = { of_n > of_best }", tmp("of_best", "of_n") + tmp("of_who", "of_l"))))
        + iff("check_variable = { of_best > 0 }", block("var:of_who", "add_to_variable = { mod1440_of_states = 1 }\n")))
    honour = iff("check_variable = { tr_cap = 1 } %s %s" % (is_one("mod1440_hn_auto"), HONOUR_DLC), (
        tmp("hn_n", 0)
        + block("var:tr_s", block("every_state_division", "limit = { OWNER = { tag = ROOT } }\n" + block(
            "add_history_entry", 'key = mod1440_hn_capture\nsubject = "Capital"\nallow = no\n') + "add_to_temp_variable = { hn_n = 1 }\n"))
        + "add_to_variable = { mod1440_hn_count = hn_n }\n"))
    script_effects = (
        "# The Records: what the window shows. Sets the buttons' frames and makes the list of the open page.\n"
        + block("mod1440_rec_show", show + "add_to_variable = { mod1440_rec_dirty = 1 }\n")
        + "\n# The Records: the first run for the country in scope. Takes the copies the daily comparison needs, opens a\n"
        "# row for each war that already runs and writes the first line.\n"
        + block("mod1440_ev_init", iff("NOT = { %s }" % is_one("mod1440_ev_begun"), (
            setv("mod1440_ev_begun", 1) + setv("mod1440_hn_auto", 1)
            + setv("mod1440_ev_since", "global.date") + setv("mod1440_ev_since_day", "global.num_days") + "mod1440_rec_odd = yes\n"
            + line("begins")
            + block("for_each_loop", "array = enemies\nvalue = ev_c\nadd_to_array = { mod1440_ev_enemies = ev_c }\n" + open_war("ev_c", 1))
            + block("for_each_loop", "array = subjects\nvalue = ev_c\nadd_to_array = { mod1440_ev_subjects = ev_c }\n")
            + in_faction + setv("mod1440_ev_fac", "ev_in") + copy_members
            + "mod1440_gv_daily = yes\nmod1440_of_seen = yes\n")))
        + "\n# The Records: once a day for a player's country. What no hook tells is found by comparing with yesterday:\n"
        "# the end of a war, a new or lost subject, the faction, the offices. Then the numbers of the wars.\n"
        + block("mod1440_rec_daily", (
            "mod1440_ev_init = yes\n"
            + compare("enemies", "mod1440_ev_enemies", "ev_c",
                      line("war_with", b="ev_c") + open_war("ev_c"),
                      line("peace", b="ev_c") + tmp("wr_c", "ev_c") + "mod1440_wr_close = yes\n")
            + compare("subjects", "mod1440_ev_subjects", "ev_c", line("subject_new", b="ev_c"), line("subject_gone", b="ev_c"))
            + in_faction
            + iff("NOT = { check_variable = { mod1440_ev_fac = ev_in } }", (
                iff("check_variable = { ev_in = 1 }", line("faction_in", b="faction_leader")) + els(line("faction_out"))
                + setv("mod1440_ev_fac", "ev_in") + copy_members))
            + els(compare("faction_members", "mod1440_gv_fac", "ev_c", line("member_in", b="ev_c"), line("member_out", b="ev_c")))
            + "mod1440_wr_daily = yes\nmod1440_gv_daily = yes\nmod1440_of_seen = yes\n"
            + iff(is_one("mod1440_rec_open"), "mod1440_rec_show = yes\n")))
        + "\n# The Records: a war has begun between the country in scope and wr_c (a hook says who attacked).\n"
        + block("mod1440_ev_war_on", line("war_on", b="wr_c") + tmp("wr_old", 0) + "mod1440_wr_open = yes\n"
                + iff("NOT = { is_in_array = { array = mod1440_ev_enemies value = wr_c } }", "add_to_array = { mod1440_ev_enemies = wr_c }\n"))
        + block("mod1440_ev_war_by", line("war_by", b="wr_c") + tmp("wr_old", 0) + "mod1440_wr_open = yes\n"
                + iff("NOT = { is_in_array = { array = mod1440_ev_enemies value = wr_c } }", "add_to_array = { mod1440_ev_enemies = wr_c }\n"))
        + "\n# The Records: the country in scope has taken the state tr_s from tr_c (tr_cap = 1: a capital). A line, the\n"
        "# count of the war, the general with the most divisions there, what the state card shows, and the honour.\n"
        + block("mod1440_tr_taken", (
            iff("check_variable = { tr_cap = 1 }", line("capital_taken", a="tr_s", b="tr_c", state=True)
                + line("capital_taken", a="tr_s", b="tr_c", state=True, log="tr"))
            + els(line("state_taken", a="tr_s", b="tr_c", state=True, log="tr"))
            + tmp("wr_c", "tr_c") + tmp("wr_f", 1) + "mod1440_wr_count = yes\n" + credit
            + block("var:tr_s", setv("mod1440_sr_date", "global.date") + setv("mod1440_sr_day", "global.num_days")
                    + setv("mod1440_sr_from", "tr_c"))
            + honour))
        + block("mod1440_tr_lost", (
            iff("check_variable = { tr_cap = 1 }", line("capital_lost", a="tr_s", b="tr_c", state=True)
                + line("capital_lost", a="tr_s", b="tr_c", state=True, log="tr"))
            + els(line("state_lost", a="tr_s", b="tr_c", state=True, log="tr"))
            + tmp("wr_c", "tr_c") + tmp("wr_f", 2) + "mod1440_wr_count = yes\n")))

    # ---- hooks (X43 for those seen firing; the others after the comments of the vanilla files)
    human = "is_ai = no"
    state = block("FROM.FROM", tmp("tr_s", "THIS") + tmp("tr_cap", 0) + iff("is_capital = yes", tmp("tr_cap", 1)))

    def simple(kind):
        return iff(human, line(kind))

    def ace(counter, kind, word):
        return iff(human, "add_to_variable = { mod1440_ac_%s = 1 }\n" % counter + line(kind)
                   + 'log = "MOD1440 listening: %s, ace [FROM.GetFullName] ([FROM.GetCallsign])"\n' % word)

    hooks = {
        # ROOT the attacker, FROM the defender
        "on_war_relation_added": (iff(human, tmp("wr_c", "FROM") + "mod1440_ev_war_on = yes\n")
                                  + iff("FROM = { is_ai = no }", block("FROM", tmp("wr_c", "PREV") + "mod1440_ev_war_by = yes\n"))),
        # ROOT the annexer, FROM the annexed
        "on_annex": iff(human, line("annexed", b="FROM") + tmp("wr_c", "FROM") + "mod1440_wr_annexed = yes\n"),
        # ROOT the new controller, FROM the old one, FROM.FROM the state
        "on_state_control_changed": (iff(human, state + tmp("tr_c", "FROM") + "mod1440_tr_taken = yes\n")
                                     + iff("FROM = { is_ai = no }", state + block("FROM", tmp("tr_c", "PREV") + "mod1440_tr_lost = yes\n"))),
        # the scope is the state invaded, ROOT the country that lands: one line per state and day
        "on_naval_invasion": iff("ROOT = { is_ai = no } NOT = { check_variable = { mod1440_sr_landing = global.num_days } }", (
            setv("mod1440_sr_landing", "global.num_days") + fill("landing", a="THIS", state=True) + block("ROOT", "mod1440_ev_add = yes\n")
            + 'log = "MOD1440 listening: on_naval_invasion, state [THIS.GetName], by [ROOT.GetName]"\n')),
        # ROOT the state dropped into, FROM the country
        "on_units_paradropped_in_state": iff("FROM = { is_ai = no }", (
            fill("airborne", a="THIS", state=True) + block("FROM", "mod1440_ev_add = yes\n")
            + 'log = "MOD1440 listening: on_units_paradropped_in_state, state [THIS.GetName], by [FROM.GetName]"\n')),
        "on_ruling_party_change": simple("party"),
        "on_government_change": simple("government"),
        "on_new_term_election": simple("election"),
        # the country is the scope, FROM the ace. Whether an ace can be kept is not known (wiki/phases/E5-aces-roll.md):
        # the first hook tries and writes what it reads back to game.log.
        "on_ace_promoted": ace("new", "ace_new", "on_ace_promoted") + iff(human, (
            "add_to_array = { mod1440_ac_try = FROM }\n"
            'log = "MOD1440 listening: kept [?mod1440_ac_try^num] aces, the first reads [?mod1440_ac_try^0.GetFullName]"\n')),
        "on_ace_killed": ace("lost", "ace_lost", "on_ace_killed"),
        "on_ace_killed_on_accident": ace("lost", "ace_lost", "on_ace_killed_on_accident"),
        "on_ace_killed_by_ace": ace("lost", "ace_lost", "on_ace_killed_by_ace"),
        "on_ace_killed_other_ace": ace("down", "ace_down", "on_ace_killed_other_ace"),
        "on_non_ace_killed_other_ace": ace("down", "ace_down", "on_non_ace_killed_other_ace"),
        # ROOT the owner of the ship, FROM the country that sank it
        "on_pride_of_the_fleet_sunk": (iff(human, line("pride_lost", b="FROM"))
                                       + iff("FROM = { is_ai = no }", block("FROM", line("pride_sunk", b="PREV")))),
    }
    return gui, script + "\n" + state_script, script_effects, hooks


# ---------------------------------------------------------------- samples and scenes, for the renderer and the tests

# What a text of these pages shows at its widest, by what stands between its brackets.
SAMPLES = [
    (LONG, "30 September, 1944"), (r"GetDateStringNoHour", "1944.12.31"), (r"GetLastElection", " 1:00, 5 March, 1933"),
    (r"GetNameWithFlag", "The Czechoslovak Republic"),
    (r"mod1440_wd_kind|mod1440_of_ln_kind", "Our pride of the fleet was sunk by"), (r"mod1440_wo_outcome", "No longer exists"),
    (r"mod1440_gv_law", "Partial Mobilization"), (r"dec_key|md_key", "Knight's Cross (Swords & Diamonds)"),
    (r"GetRulingParty$", "NSDAP"), (r"Get\w+Party(Long)?$", "Nationalsozialistische Deutsche Arbeiterpartei"),
    (r"GetRulingIdeology", "fascist"), (r"GetFactionName", "Co-Prosperity Sphere"), (r"GetAgency", "Intelligence Agency"),
    (r"Capital\.GetName|mod1440_wd_a", "Niederschlesien"), (r"GetLeader$", "Konstantin von Neurath"), (r"Leader$|GetName", "Konstantin von Neurath"),
    (r"^\?casualties|mod1440_wr_cas|mod1440_wo_cas", "1250000"), (r"party_popularity", "100%"), (r"_war_support", "12.5%"),
    (r"surrender_progress", "100%"), (r"days_until_next_election|mod1440_wr_days|mod1440_wd_days", "1460"), (r"\?v\b", "100"),
    (r"\^num|mod1440_wd_total", "500"), (r"_level|skill|num_traits|mod1440_of_c_skill", "9"), (r"num_units|num_ships|mod1440_of_c_cmd", "240"),
    (r"mod1440_", "128"), (r"", "128"),
]


def sample(inside):
    for pattern, value in SAMPLES:
        if re.search(pattern, inside):
            return value
    return ""


def scenes():
    from unit_medals_table import MEDALS
    others = sorted(set(m[1] for m in MEDALS) - {"ger"})
    place = {"at": [REC_X, REC_Y], "freeWindow": True}
    crop = [REC_X - 10, REC_Y - 10, REC_W + 20, REC_H + 20]
    shot = "reference/vanilla/theatre_bar.jpg"
    back = [{"key": "shift+j", "wait": 0.8}]

    def tab(n):
        return [{"key": "shift+j", "wait": 1.5}, {"clickWidget": "mod1440_records_wd/wd_tab_%d" % n, "scene": "war_diary", "wait": 1.2}]

    officer_hide = (["of_arrow_up", "of_arrow_down", "of_c_none", "of_c_rank_2", "of_c_rank_3", "of_c_service_off", "of_c_cmd_navy",
                     "of_c_since_old", "of_c_prom_old", "of_c_lvl_old", "of_c_dec_none", "of_ln_none"]
                    + ["of_c_rack_%d_%s" % (k, s) for k in range(CARD_LINES) for s in others]
                    + ["of_md_%d_%s" % (k, s) for k in range(MEDAL_SLOTS) for s in others]
                    + ["of_md_%d_held" % k for k in range(1, MEDAL_SLOTS)])
    office_hide = ["gv_of_%d_none" % k for k in range(len(OFFICES))] + ["gv_of_%d_since_old" % k for k in range(len(OFFICES))]
    return {
        "war_diary": {
            "phase": "E1", "file": "mod1440_records.gui", "screenshot": shot,
            "windows": [dict(place, name="mod1440_records_wd", rows={"wd_grid": 24}, listRows={"wd_grid": "mod1440_records_diary_row"},
                             hide=["wd_none"], _note="A window of its own over the map, opened from the Records button of the top bar."),
                        {"name": "mod1440_records_diary_row", "skip": True,
                         "hide": ["wd_row_icon_%d" % f for f in (2, 3, 4, 5)] + ["wd_row_b_near"]}],
            "setup": [{"key": "shift+j", "wait": 1.5}, {"clickWidget": "mod1440_records_wd/wd_tab_0", "wait": 1.0}],
            "teardown": back,
            "expect": ["mod1440_records_wd/wd_close", "mod1440_records_wd/wd_older"],
            "crop": crop,
            "manual": ["Lines that need a war: capitulation, landings, aces"],
            "checklist": ["A line about a state: its button moves the camera there", "The filters; Older and Newer past 200 lines"],
        },
        "officers": {
            "phase": "E2", "file": "mod1440_records.gui", "screenshot": shot,
            "windows": [dict(place, name="mod1440_records_of", rows={"of_grid": 26}, listRows={"of_grid": "mod1440_records_officer_row"},
                             hide=officer_hide, _note="The file shows a German field marshal; script hides the twins of his rank, command and service and the medal strips of other countries."),
                        {"name": "mod1440_records_officer_row", "skip": True,
                         "hide": ["of_row_pick", "of_row_gen", "of_row_adm", "of_cell_c3_navy", "of_cell_c4_navy", "of_cell_cmd_navy"]}],
            "setup": tab(1),
            "teardown": [{"clickWidget": "mod1440_records_of/of_tab_0", "wait": 0.8}] + back,
            "expect": ["mod1440_records_of/of_close", "mod1440_records_of/of_sort_skill"],
            "crop": crop,
            "manual": ["Battles won and lost, states taken: they need fighting"],
            "checklist": ["A click on an officer opens his file and marks his row", "Award and Take back last", "Sorting by each column"],
        },
        "government": {
            "phase": "E3", "file": "mod1440_records.gui", "screenshot": shot,
            "windows": [dict(place, name="mod1440_records_gv",
                             rows={"gv_adv_grid": 3, "gv_hc_grid": 3, "gv_fac_grid": 4, "gv_sub_grid": 2},
                             listRows={"gv_adv_grid": "mod1440_records_adv_row", "gv_hc_grid": "mod1440_records_hc_row",
                                       "gv_fac_grid": "mod1440_records_fac_row", "gv_sub_grid": "mod1440_records_sub_row"},
                             hide=["gv_leader_since_old", "gv_next_none", "gv_faction_none", "gv_adv_none", "gv_hc_none", "gv_sub_none"] + office_hide,
                             _note="Every office filled since the record began; script hides the twins.")]
                       + [{"name": "mod1440_records_%s_row" % n, "skip": True, "hide": ["gv_%s_row_since_old" % n]} for n in ("adv", "hc")]
                       + [{"name": "mod1440_records_%s_row" % n, "skip": True} for n in ("fac", "sub")],
            "setup": tab(2),
            "teardown": [{"clickWidget": "mod1440_records_gv/gv_tab_0", "wait": 0.8}] + back,
            "expect": ["mod1440_records_gv/gv_close"],
            "crop": crop,
            "manual": ["Operatives; an election"],
            "checklist": ["Hire an advisor: the next day the Cabinet lists the name with the date"],
        },
        "wars": {
            "phase": "E4", "file": "mod1440_records.gui", "screenshot": shot,
            "windows": [dict(place, name="mod1440_records_wr", rows={"wr_now_grid": 3, "wr_old_grid": 6},
                             listRows={"wr_now_grid": "mod1440_records_war_row", "wr_old_grid": "mod1440_records_past_war_row"},
                             hide=["wr_now_none", "wr_old_none"]),
                        {"name": "mod1440_records_war_row", "skip": True, "hide": ["wr_row_since_old", "wr_row_outcome"]},
                        {"name": "mod1440_records_past_war_row", "skip": True, "hide": ["wo_row_since_old"]}],
            "setup": tab(3),
            "teardown": [{"clickWidget": "mod1440_records_wr/wr_tab_0", "wait": 0.8}] + back,
            "expect": ["mod1440_records_wr/wr_close"],
            "crop": crop,
            "manual": ["A war that ends; casualties above zero"],
            "checklist": ["Declare a war: a row appears with today's date", "After a peace the row moves to the finished wars"],
        },
    }


SCENES = {}


def build(managers):
    """Returns the files' pieces: (gui, scripted GUIs, scripted effects, hooks by name)."""
    global M, B
    M, B = managers, managers.B
    out_gui, out_script, out_effects = "", "", recording()
    hooks = {}
    for part in (war_diary(), officers(), government(), wars(), frame()):
        out_gui += part[0]
        out_script += ("\n" if out_script else "") + part[1]
        out_effects += "\n" + part[2]
        if len(part) > 3:
            for name, body in part[3].items():
                hooks[name] = hooks.get(name, "") + body
    SCENES.clear()
    SCENES.update(scenes())
    return out_gui, out_script, out_effects, hooks
