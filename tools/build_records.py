"""The role-play pages of Milestone E (wiki/Roleplay-Pages.md): the Records window and what it keeps.

Not run by itself: tools/build_managers.py imports it and writes its output with everything else.

    interface/mod1440_records.gui                        the window's four pages, their rows, the top bar button, the state card
    common/scripted_guis/mod1440_records.txt             what shows when, and what the buttons do
    common/scripted_effects/mod1440_records.txt          the recording, the daily comparison, the lists of the pages
    common/scripted_effects/mod1440_portraits.txt        which sprite the game shows for each general, admiral and head of government
    common/scripted_effects/mod1440_victory_points.txt   the daily look at who holds each victory point
    hooks                                                handed back to build_managers.py, which writes the one on_actions file

What a record is (wiki/Engine-Facts.md): a line of the log holds a date, a text key and up to three scopes (a
state, a country, a character); the name is looked up when the row is drawn (X33, X34, X37). An officer's
record is variables of the mod on the officer himself (X32). Nothing here writes to the game but one command,
add_history_entry, for the unit honours of phase E6.

How the pages look (wiki/Scripted-GUIs.md, "The Records"): dark cards as on the manager pages; figures as
tiles, a small label over a large value; every list striped, with a bar of column heads; names in the game's
highlight yellow; the game's own text icons, flags, portraits, medal strips and progress bars. The sprites are
declared in interface/1440p_ui.gfx (GFX_1440p_SG_*), all of them tiles of vanilla textures.

Two tables of game content stand beside this file, made by tools/make_game_tables.py: the portrait sprite of
every named character (portraits_table.py) and every victory point (victory_points_table.py).
"""
import re
import zlib

M = None        # tools/build_managers.py, set by build(): its helpers write the .gui and script pieces
B = None

REC_X, REC_Y, REC_W, REC_H = 440, 100, 1680, 1220
PAGES = [("wd", "War Diary"), ("of", "Officers"), ("gv", "Government"), ("wr", "Wars")]
LOG_KEEP = 500          # lines of each log
VIEW_ROWS = 200         # lines of the diary on one page of the list
BLANK = "token:mod1440_blank"
TILE_W, TILE_H = 156, 64                    # the plate of a figure (build_managers.tile)
SMALL_TILE = 148                            # a narrower plate, where three stand beside a portrait
STRIPE = "GFX_1440p_SG_stripe_%dx%d"        # the darker band of every second row of a list
PICK = "GFX_1440p_SG_pick_%dx%d"            # the lighter band of the chosen row
ODD_ROWS = 512                              # rows a list can stripe
LONG = "GetDateStringNoHourLong"            # "1 January, 1936"
UNKNOWN = "GFX_portrait_unknown"            # the game's picture of a leader it has no portrait of (156x210)
FLAG = "GFX_shield_medium"                  # the game's flag in its frame (82x52)
VP_MAJOR = 15                               # a victory point worth this much is written into the main log too


# ---------------------------------------------------------------- small pieces

# The pieces every page shares are in tools/build_managers.py: script (block, iff, els, setv, tmp, is_one,
# flip) and the look (plain, scaled, listing, row, heads, tile, card, gauge). Here they are reached by their
# bare names, which reads better in the long page functions below.

def _shared(name):
    def call(*args, **kwargs):
        return getattr(M, name)(*args, **kwargs)
    call.__name__ = name
    return call


block, iff, els, setv, tmp, is_one, flip = (_shared(n) for n in ("block", "iff", "els", "setv", "tmp", "is_one", "flip"))
plain, scaled, listing, row, heads, tile, card, gauge = (
    _shared(n) for n in ("plain", "scaled", "listing", "row", "heads", "tile", "card", "gauge"))


def token(name, words):
    """A text the script holds as a text key (X37). The key is lower case, as the probe's were."""
    key = "mod1440_" + name
    if B.loc.get(key, words) != words:
        raise ValueError("two texts for " + key)
    B.loc[key] = words
    return "token:" + key


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


def shown_if(names, trigger):
    """The same <widget>_visible trigger for several widgets."""
    return "".join(block(name + "_visible", trigger) for name in names)


# ---------------------------------------------------------------- portraits and flags

# An icon shows another sprite when script names one: the "image" property takes a text, and the text can hold
# a variable (the game's _documentation.md of scripted GUIs; The New Order writes "GFX_[?v.GetTokenKey]").
# A person's portrait: the game declares a sprite for each named character (GFX_portrait_...), and script can
# ask whether a character is a certain one (is_character). So the mod carries the list of who has which sprite
# (portraits_table.py) and puts the sprite's name on the officer as a text key, once. A general the game made
# up has a portrait script cannot learn: he shows the game's picture of an unknown leader.

# The strips of medal pictures are sprites of this mod on the game's own pictures (interface/1440p_ui.gfx, made
# with tools/list_medals.py --sprites). The game's sprites GFX_medal_icon_<set>_large are in interface/medals.gfx,
# and a mod that brings a file of that name drops the sets its copy lacks: Road to 56 has none for Ethiopia, and
# the game then logs "Could not find sprite type" for every icon that names it.
MEDAL_STRIP = "GFX_1440p_medal_%s"


def table_version(table):
    """A number that changes when a table of game content changes: what script kept from the old one is then
    worked out again."""
    return zlib.crc32(repr(table).encode("utf-8")) % 1000000 + 1


def portrait(name, x, y, scale=1.0):
    """The icon of a portrait: an unknown leader until script names a sprite (see shown())."""
    return scaled(name, x, y, UNKNOWN, scale)


def shown(name, variable):
    """The property that gives a portrait icon the sprite whose name the variable holds as a text key."""
    return block(name, 'image = "[?%s.GetTokenKey]"\n' % variable)


def flag(name, x, y):
    """The icon of a flag; flown(name, country) says whose."""
    return M.icon(name, x, y, FLAG)


def flown(name, country):
    return block(name, 'image = "[%s.GetFlag]"\n' % country)


def portraits():
    """The script that finds a person's portrait. Returns the text of common/scripted_effects/mod1440_portraits.txt
    and the version of the table it was made from.

    mod1440_p_officer   in the scope of a general or an admiral, PREV his country: leaves the sprite's name on him
    mod1440_p_leader    in the scope of a head of government, PREV his country: leaves it in the temporary p_tok
    """
    from portraits_table import PORTRAITS, TAGS
    # the officers other mods add, when their table has been made (tools/make_game_tables.py --mods): a name the
    # loaded game does not know is not found and logs nothing (Engine Facts X68)
    try:
        from portraits_mods_table import PORTRAITS as others
    except ImportError:
        others = []
    game_own = set(row[0] for row in PORTRAITS)
    PORTRAITS = PORTRAITS + [row for row in others if row[0] not in game_own]
    version = table_version(PORTRAITS)
    unknown = "token:" + UNKNOWN

    def chains(prefix, people):
        """One effect per file of characters, and the script that calls the country's own file first."""
        by_file = {}
        for name, source, sprite in people:
            by_file.setdefault(source, []).append((name, sprite))
        effects, own, others = "", "", ""
        for source in sorted(by_file):
            # is_character writes an error for a character no country has recruited yet (seen in game: "not a
            # valid character"), so the country is asked first whether it has him, which the game's own script
            # does for the same reason
            body = "".join(iff("PREV = { has_character = %s } is_character = %s" % (name, name),
                               tmp("p_tok", "token:" + sprite) + tmp("p_found", 1), "if" if n == 0 else "else_if")
                           for n, (name, sprite) in enumerate(by_file[source]))
            effects += block("mod1440_p_%s_%s" % (prefix, source), body)
            call = "mod1440_p_%s_%s = yes\n" % (prefix, source)
            if source in TAGS:
                own += iff("PREV = { original_tag = %s }" % source, call, "else_if" if own else "if")
            others += iff("check_variable = { p_found = 0 }", call)
        # a person who serves another country than the one whose file names him is found by going through all
        return effects, tmp("p_tok", unknown) + tmp("p_found", 0) + own + iff("check_variable = { p_found = 0 }", others)

    officers, leaders = [], []
    plain_name = re.compile(r"^[A-Za-z0-9_]+$")     # eight names of the game hold a hyphen: left out, a text key may not take it
    for name, source, army, navy, civilian, roles in PORTRAITS:
        if not plain_name.match(name):
            continue
        if "country_leader" in roles and plain_name.match(civilian or army or navy or "-"):
            leaders.append((name, source, civilian or army or navy))
        if any(role in roles for role in ("corps_commander", "field_marshal", "navy_leader")):
            # an admiral shows his navy portrait, a general his army portrait; whichever the game has otherwise
            first = (navy or army) if roles.strip() == "navy_leader" else (army or navy)
            if plain_name.match(first or civilian or "-"):
                officers.append((name, source, first or civilian))
    officer_effects, find_officer = chains("of", officers)
    leader_effects, find_leader = chains("ld", leaders)
    out = ("# Generated by tools/build_managers.py from tools/portraits_table.py (the game's characters).\n"
           "# The sprite the game shows for a person, as a text key: an icon of the Records window takes it as its image.\n\n"
           "# In the scope of a general or an admiral, PREV his country. %d officers.\n" % len(officers)
           + block("mod1440_p_officer", find_officer + setv("mod1440_p", "p_tok") + setv("mod1440_p_ver", version))
           + "\n# In the scope of a head of government, PREV his country: the sprite is left in p_tok. %d leaders.\n" % len(leaders)
           + block("mod1440_p_leader", find_leader)
           + "\n" + officer_effects + "\n" + leader_effects)
    return out, version


def leader_portrait(country, variable, version):
    """Script that puts the portrait of a country's head of government into a variable of the country in
    scope. <country> is a variable that holds the country, or THIS. The portrait is looked up when another
    leader rules or the table has changed, and kept on the leader's own country (mod1440_ld_p)."""
    find = (iff("OR = { NOT = { check_variable = { mod1440_ld_p_ver = %d } } NOT = { check_variable = { mod1440_ld_p_of = country_leader } } }" % version, (
        tmp("p_ld", "country_leader") + block("var:p_ld", "mod1440_p_leader = yes\n")
        + setv("mod1440_ld_p", "p_tok") + setv("mod1440_ld_p_ver", version) + setv("mod1440_ld_p_of", "country_leader")))
        + tmp("p_face", "mod1440_ld_p"))
    return (tmp("p_face", "token:" + UNKNOWN) + (find if country == "THIS" else block("var:" + country, iff("exists = yes", find)))
            + setv(variable, "p_face"))


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
    ("vp_taken", 2, "Victory point taken"), ("vp_lost", 2, "Victory point lost"),
    ("commissioned_more", 4, "More officers commissioned"),
]
FAMILY = dict((name, family) for name, family, words in KINDS)
NUMBER = dict((name, n) for n, (name, family, words) in enumerate(KINDS))
# What a line holds. a: whom or what it is about (sa says which: 1 a person, 2 a state, 3 the name of a victory
# point), b: a country (sb 1), c: the officer on the spot (sc 1), p: for a victory point its state, x: 1 when
# the line stands in the other log too.
LOG_ARRAYS = ["date", "day", "kind", "fam", "a", "b", "sa", "sb", "c", "sc", "p", "x"]
NEW_ARRAYS = ["c", "sc", "p", "x"]          # a game saved before 2026-10-13 has logs without these
# the game's own text icon for each family
FAMILY_ICON = {1: "army_experience", 2: "victory_points", 3: "pol_power", 4: "command_power", 5: "air_experience"}


def fill(name, a=None, b=None, state=False, point=False, c=None, sc=None, p=None):
    """Script that sets what the next line says: its kind, and whom or what it is about. a is a character, a
    state (state=True) or the text key of a victory point's name (point=True); b a country; c an officer,
    written when the temporary variable sc is above zero (or always, without sc); p the state of a point."""
    out = tmp("ev_kind", "token:mod1440_ev_" + name) + tmp("ev_fam", FAMILY[name]) + tmp("ev_kid", NUMBER[name])
    out += tmp("ev_sa", (3 if point else 2 if state else 1) if a else 0) + tmp("ev_a", a or 0)
    # the officer has temporary variables of his own: ev_c is the country in the loops of the daily comparison
    out += tmp("ev_sb", 1 if b else 0) + tmp("ev_b", b or 0) + tmp("ev_so", 0) + tmp("ev_o", 0)
    if c:
        officer = tmp("ev_so", 1) + tmp("ev_o", c)
        out += iff("check_variable = { %s > 0 }" % sc, officer) if sc else officer
    return out + tmp("ev_p", p or 0) + tmp("ev_x", 0)


def line(name, a=None, b=None, state=False, log="ev", both=False, **more):
    """Script that writes one line for the country in scope: into one log, or into both."""
    out = fill(name, a, b, state, **more)
    if both:
        return out + tmp("ev_x", 1) + "mod1440_ev_add = yes\nmod1440_tr_add = yes\n"
    return out + "mod1440_%s_add = yes\n" % log


def count(*names):
    """Script that sums the counters of some kinds into the temporary variable ct_sum."""
    return tmp("ct_sum", 0) + "".join("add_to_temp_variable = { ct_sum = mod1440_ct^%d }\n" % NUMBER[name] for name in names)


def recording():
    for name, family, words in KINDS:
        token("ev_" + name, words)
    token("blank", "")
    out = "# The Records: one line of a log, for the country in scope. The caller has set the temporary variables\n"
    out += "# ev_kind, ev_fam, ev_kid and one for each part of a line (tools/build_records.py, fill()). The oldest line goes past %d.\n" % LOG_KEEP
    out += "# Each kind of line is counted (mod1440_ct), a line of the territory log in that log only.\n"
    values = {"date": "global.date", "day": "global.num_days", "kind": "ev_kind", "fam": "ev_fam", "a": "ev_a", "b": "ev_b",
              "sa": "ev_sa", "sb": "ev_sb", "c": "ev_o", "sc": "ev_so", "p": "ev_p", "x": "ev_x"}
    counted = pad([("mod1440_ct", 0)], len(KINDS) + 8) + "add_to_variable = { mod1440_ct^ev_kid = 1 }\n"
    for log in ("ev", "tr"):
        body = "mod1440_ev_grow = yes\n"
        body += "".join("add_to_array = { mod1440_%s_%s = %s }\n" % (log, part, values[part]) for part in LOG_ARRAYS)
        body += iff("check_variable = { mod1440_%s_date^num > %d }" % (log, LOG_KEEP),
                    "".join("remove_from_array = { array = mod1440_%s_%s index = 0 }\n" % (log, part) for part in LOG_ARRAYS))
        body += counted if log == "tr" else iff("NOT = { check_variable = { ev_fam = 2 } }", counted)
        # a person the line names by his place says so himself from now on (places())
        body += iff("check_variable = { ev_sa = 1 }", tmp("ch_v", "ev_a") + "mod1440_ch_mark = yes\n")
        body += iff("check_variable = { ev_so = 1 }", tmp("ch_v", "ev_o") + "mod1440_ch_mark = yes\n")
        out += block("mod1440_%s_add" % log, body) + "\n"
    out += "# The Records: a game saved before a line had an officer has logs without the newer parts. They get a 0 for\n"
    out += "# each line that is there, and a capital in the territory log the mark that it stands in the main log too.\n"
    grow = ""
    for log in ("ev", "tr"):
        longer = "check_variable = { mod1440_%s_x^num < mod1440_%s_date^num }" % (log, log)
        fix = block("for_loop_effect", "start = 0\nend = %d\nvalue = gr_n\n" % LOG_KEEP + "".join(
            iff("check_variable = { mod1440_%s_%s^num < mod1440_%s_date^num }" % (log, part, log),
                "add_to_array = { array = mod1440_%s_%s value = 0 index = 0 }\n" % (log, part)) for part in NEW_ARRAYS))
        if log == "tr":
            fix += (tmp("gr_taken", "token:mod1440_ev_capital_taken") + tmp("gr_lost", "token:mod1440_ev_capital_lost")
                    + block("for_each_loop", "array = mod1440_tr_kind\nvalue = gr_k\nindex = gr_i\n" + iff(
                        "OR = { check_variable = { gr_k = gr_taken } check_variable = { gr_k = gr_lost } }", setv("mod1440_tr_x^gr_i", 1))))
        grow += iff(longer, fix)
    out += block("mod1440_ev_grow", grow) + "\n"
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


def merged(match, take):
    """Script that goes through the lines of both logs together, newest first, and runs take(log) for each
    line that match(log) holds for (None: every line). Both are functions of the log's name ("ev", "tr") that
    return script; the line's index is in the temporary variable mg_m. A line that stands in both logs is
    taken from the main log."""
    def one(log, pointer):
        test = match(log) if match else None
        inner = iff(test, take(log)) if test else take(log)
        if log == "tr":
            inner = iff("NOT = { check_variable = { mod1440_tr_x^mg_m = 1 } }", inner)
        return tmp("mg_m", pointer) + "subtract_from_temp_variable = { %s = 1 }\n" % pointer + inner

    return (tmp("mg_e", "mod1440_ev_date^num") + "subtract_from_temp_variable = { mg_e = 1 }\n"
            + tmp("mg_t", "mod1440_tr_date^num") + "subtract_from_temp_variable = { mg_t = 1 }\n"
            + tmp("mg_all", "mod1440_ev_date^num") + "add_to_temp_variable = { mg_all = mod1440_tr_date^num }\n"
            + block("for_loop_effect", (
                "start = 0\nend = mg_all\nvalue = mg_i\n" + tmp("mg_log", 0)
                # the newer of the two lines the pointers stand on; on the same day the main log's first
                + iff("check_variable = { mg_e > -1 }", tmp("mg_log", 1) + iff("check_variable = { mg_t > -1 }", (
                    tmp("mg_ed", "mod1440_ev_day^mg_e") + tmp("mg_td", "mod1440_tr_day^mg_t")
                    + iff("check_variable = { mg_td > mg_ed }", tmp("mg_log", 2)))))
                + iff("check_variable = { mg_t > -1 }", tmp("mg_log", 2), "else_if")
                + iff("check_variable = { mg_log = 1 }", one("ev", "mg_e"))
                + iff("check_variable = { mg_log = 2 }", one("tr", "mg_t"), "else_if"))))


# ---------------------------------------------------------------- War Diary (E1)

WD_LIST_W = 1270
WD_ROW_W = WD_LIST_W - 30
WD_ROW = 30
WD_ICON_X, WD_EVENT_X, WD_A_X, WD_B_X, WD_C_X = 196, 232, 540, 788, 1018
WD_PANE_X = 14 + WD_LIST_W + 12
WD_PANE_W = REC_W - WD_PANE_X - 14
WD_FILTERS = [
    (0, "all", "All", "Everything, newest first."),
    (1, "war", "War and peace", "Wars declared and ended, capitulations, annexations, subjects, factions."),
    (2, "land", "Territory", "Every state and every victory point taken or lost, landings, and the divisions you cited."),
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
    ("vpt", "Points taken", ("vp_taken",), "Victory points you took from an enemy."),
    ("vpl", "Points lost", ("vp_lost",), "Victory points an enemy took from you."),
    ("capitals", "Capitals taken", ("capital_taken",), "Capitals among the states you took."),
    ("govs", "Governments", ("party", "government", "leader"), "Changes of ruling party, of government and of its head."),
    ("comm", "Commissioned", ("commissioned",), "Generals and admirals who joined your officers."),
    ("prom", "Promotions", ("promoted",), "Generals promoted to field marshal."),
    ("dec", "Decorations", ("decorated",), "Decorations you awarded to officers."),
    ("hon", "Divisions cited", "mod1440_hn_count", "Lines written into the history of your divisions: for a capital taken, or on your word."),
]
WD_VIEW = ["date", "kind", "fam", "a", "b", "sa", "sb", "c", "sc", "p"]     # what a row of the page needs of a line


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
    body += M.text("wd_count", 14 + WD_LIST_W - 130, 66, 120, B.key("wd_count", "[?mod1440_wd_fam^num|0] of [?mod1440_wd_total|0]"), M.FONT_SMALL, "right",
                   tooltip=B.key("wd_count_tt", "Lines shown, of the lines this filter has."))

    body += heads("wd_heads", 14, 98, WD_LIST_W, [
        (12, 170, "Date", "left", None), (WD_EVENT_X, 290, "Event", "left", None),
        (WD_A_X + 6, 236, "State, place or person", "left", "The name of a state or of a victory point is a button: it shows the place on the map."),
        (WD_B_X, 220, "Country", "left", "For a state or a victory point: whom it was taken from or lost to."),
        (WD_C_X, 200, "Officer", "left", "The general who had the most divisions in the state when it changed hands.")])
    body += listing("wd_list", "wd_grid", 14, 130, WD_LIST_W, REC_H - 130 - 14, WD_ROW)
    body += M.text("wd_none", 40, 150, 900, B.key("wd_none", "Nothing of this kind is written down yet."), M.FONT_LABEL)
    triggers += block("wd_none_visible", "check_variable = { mod1440_wd_fam^num < 1 }\n")

    # ---- a line: date, the family's icon, the words, then whom or what it is about, the country, the officer
    country = B.key("wd_row_b", "§Y[?mod1440_wd_b^i.GetNameWithFlag]§!")
    entry = M.icon("wd_row_stripe", 0, 0, STRIPE % (WD_ROW_W, WD_ROW))
    entry += M.button("wd_row_go", WD_A_X, 0, M.HEAD_SPRITES[240], tooltip=B.key("wd_row_go_tt", "Show this place on the map"))
    entry += M.text("wd_row_date", 12, 5, 178, B.key("wd_row_date", "[?mod1440_wd_date^i.%s]" % LONG), M.FONT_SMALL, height=22)
    for family, text_icon in sorted(FAMILY_ICON.items()):
        entry += M.text("wd_row_icon_%d" % family, WD_ICON_X, 3, 30, B.key("wd_icon_%d" % family, "£" + text_icon), M.FONT_LABEL, height=24)
        triggers += block("wd_row_icon_%d_visible" % family, "check_variable = { v = %d }\n" % family)
    entry += M.text("wd_row_event", WD_EVENT_X, 4, WD_A_X - WD_EVENT_X - 8, B.key("wd_row_event", "[?mod1440_wd_kind^i.GetTokenLocalizedKey]"),
                    M.FONT_LABEL, height=22)
    entry += plain("wd_row_a", WD_A_X + 8, 4, 226, B.key("wd_row_a", "§Y[?mod1440_wd_a^i.GetName]§!"), height=22)
    entry += plain("wd_row_point", WD_A_X + 8, 4, 226, B.key("wd_row_point", "§Y[?mod1440_wd_a^i.GetTokenLocalizedKey]§!"), height=22)
    entry += M.text("wd_row_b", WD_B_X, 4, WD_C_X - WD_B_X - 8, country, M.FONT_LABEL, height=22)
    entry += M.text("wd_row_b_near", WD_A_X + 8, 4, 440, country, M.FONT_LABEL, height=22)
    entry += M.text("wd_row_c", WD_C_X, 4, WD_ROW_W - WD_C_X - 8, B.key("wd_row_c", "§Y[?mod1440_wd_c^i.GetName]§!"), M.FONT_LABEL, height=22)
    triggers += block("wd_row_stripe_visible", "check_variable = { mod1440_odd^i = 1 }\n")
    triggers += block("wd_row_go_visible", "check_variable = { mod1440_wd_sa^i > 1 }\n")
    triggers += block("wd_row_a_visible", "check_variable = { mod1440_wd_sa^i > 0 }\ncheck_variable = { mod1440_wd_sa^i < 3 }\n")
    triggers += block("wd_row_point_visible", "check_variable = { mod1440_wd_sa^i = 3 }\n")
    # a line about a country alone has its country where the eye looks next, not two columns away
    triggers += block("wd_row_b_visible", "check_variable = { mod1440_wd_sb^i > 0 }\ncheck_variable = { mod1440_wd_sa^i > 0 }\n")
    triggers += block("wd_row_b_near_visible", "check_variable = { mod1440_wd_sb^i > 0 }\ncheck_variable = { mod1440_wd_sa^i = 0 }\n")
    triggers += block("wd_row_c_visible", "check_variable = { mod1440_wd_sc^i = 1 }\n")
    # the camera goes to the state, or to the state of the victory point
    effects += block("wd_row_go_click", tmp("wd_state", "mod1440_wd_a^i") + iff("check_variable = { mod1440_wd_sa^i = 3 }", tmp("wd_state", "mod1440_wd_p^i"))
                     + block("var:wd_state", block("ROOT", "goto_state = PREV\n" + setv("mod1440_rec_open", 0))))

    # ---- the record so far: since when, fourteen figures, the switch of the battle honours
    pane = M.text("wd_since_l", 16, 46, 130, B.key("wd_since_l", "Kept since"), M.FONT_SMALL, height=22)
    pane += M.text("wd_since", 150, 44, WD_PANE_W - 166, B.key("wd_since", "[?mod1440_ev_since.%s]" % LONG), M.FONT_LABEL, height=22)
    pane += M.text("wd_days_l", 16, 72, 130, B.key("wd_days_l", "Days on record"), M.FONT_SMALL, height=22)
    pane += M.text("wd_days", 150, 70, WD_PANE_W - 166, B.key("wd_days", "[?mod1440_wd_days|0]"), M.FONT_LABEL, height=22)
    sums = ""
    left = (WD_PANE_W - 2 * TILE_W - 12) // 2
    for n, (name, label, source, tip) in enumerate(WD_FIGURES):
        variable = source if isinstance(source, str) else "mod1440_wd_n_" + name
        piece, extra = tile("wd_f_" + name, left + (n % 2) * (TILE_W + 12), 110 + (n // 2) * (TILE_H + 10), label, "[?%s|0]" % variable, tip)
        pane += piece
        if not isinstance(source, str):
            sums += count(*source) + setv(variable, "ct_sum")
    y = 110 + ((len(WD_FIGURES) + 1) // 2) * (TILE_H + 10) + 10
    pane += M.text("wd_hon_title", 14, y, WD_PANE_W - 28, B.key("wd_hon_title", "Battle honours"), M.FONT_CARD, height=30)
    pane += M.button("wd_honours", 16, y + 38, "GFX_sort_button_202x29", B.key("wd_honours", "Written by themselves"), tooltip=B.key(
        "wd_honours_tt", "While this is chosen, your divisions that stand in an enemy capital when it falls get a line in their own history (By Blood Alone). A division takes one line a day."))
    for k, words in enumerate(("A division that stands in an enemy capital", "when it falls gets a line in its own history.",
                               "Select a state you hold to cite the", "divisions there yourself.")):
        pane += M.text("wd_hon_%d" % (k + 1), 16, y + 76 + k * 20, WD_PANE_W - 32, B.key("wd_hon_%d" % (k + 1), words), M.FONT_SMALL, height=20)
    pane += M.text("wd_kept_1", 16, REC_H - 62 - 14 - 54, WD_PANE_W - 32, B.key("wd_kept_1", "The newest %d lines are kept, and %d" % (LOG_KEEP, LOG_KEEP)), M.FONT_SMALL, height=20)
    pane += M.text("wd_kept_2", 16, REC_H - 62 - 14 - 34, WD_PANE_W - 32, B.key("wd_kept_2", "of states and victory points."), M.FONT_SMALL, height=20)
    effects += block("wd_honours_click", flip("mod1440_hn_auto") + "mod1440_rec_show = yes\n")
    properties += block("wd_honours", "frame = mod1440_hn_frame\n")
    body += card("wd_pane", WD_PANE_X, 62, WD_PANE_W, REC_H - 62 - 14, "The record", pane)

    gui, script = page_gui("wd", 0, body, dirty="mod1440_rec_dirty",
                           lists=block("wd_grid", 'array = mod1440_wd_fam\nentry_container = "mod1440_records_diary_row"\n'),
                           effects=effects, triggers=triggers, properties=properties)
    gui += row("mod1440_records_diary_row", WD_ROW_W, WD_ROW, entry)

    def take(log, index):
        """A line the filter wants: counted, and copied to the page when it is one of those on show."""
        return ("add_to_temp_variable = { wd_seen = 1 }\n"
                + iff("check_variable = { wd_seen > mod1440_wd_from } check_variable = { mod1440_wd_fam^num < %d }" % VIEW_ROWS,
                      "".join("add_to_array = { mod1440_wd_%s = mod1440_%s_%s^%s }\n" % (part, log, part, index) for part in WD_VIEW)))

    def one_log(log, by_family):
        keep = take(log, "wd_m")
        if by_family:
            keep = iff("check_variable = { mod1440_%s_fam^wd_m = mod1440_wd_filter }" % log, keep)
        return block("for_loop_effect", (
            "start = 0\nend = mod1440_%s_date^num\nvalue = wd_n\n" % log
            + tmp("wd_m", "mod1440_%s_date^num" % log) + "subtract_from_temp_variable = { wd_m = 1 }\nsubtract_from_temp_variable = { wd_m = wd_n }\n"
            + keep))

    frames = "".join(setv("mod1440_wd_frame_%d" % v, 1) for v, _, _, _ in WD_FILTERS)
    frames += "".join(iff("check_variable = { mod1440_wd_filter = %d }" % v, setv("mod1440_wd_frame_%d" % v, 2)) for v, _, _, _ in WD_FILTERS)
    script_effects = (
        "# War Diary: copies the lines the chosen filter wants, newest first, %d from the chosen place, into the arrays\n"
        "# the page draws. All goes through both logs together; Territory has a log of its own; every other filter\n"
        "# reads the main log. Then the figures of the record: sums of the counters, and the days since it began.\n" % VIEW_ROWS
        + block("mod1440_wd_list", (
            "mod1440_ev_grow = yes\n" + "".join("clear_array = mod1440_wd_%s\n" % part for part in WD_VIEW)
            + tmp("wd_seen", 0)
            + iff("check_variable = { mod1440_wd_filter = 0 }", merged(None, lambda log: take(log, "mg_m")))
            + iff("check_variable = { mod1440_wd_filter = 2 }", one_log("tr", False), "else_if") + els(one_log("ev", True))
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
OF_FACE_W, OF_FACE = 40, 0.22               # the column of the portrait in a row, and how small it is drawn (34x46)
OF_NAME, OF_RANK = 240, 84
OF_ROW_W = OF_FACE_W + OF_NAME + OF_RANK + sum(c[2] for c in OF_COLUMNS)
OF_ROW = 48
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
OF_SIDE = 16 + 156 + 16                     # where the text beside the portrait of a file begins
MEDAL_SLOTS = 12        # decorations a country can award at most (Chile has twelve medals)
CARD_LINES = 7          # medals on the rack, and diary lines the file shows
DEC_LINES = 5           # decorations the file lists by name
DEC_ARRAYS = ["dec", "dec_key", "dec_date", "dec_set", "dec_frame"]     # an officer's decorations, on the officer
OF_FIGURES = [
    ("skill", "Skill", "[?mod1440_of_c_skill|0]", None),
    ("won", "Battles won", "[?mod1440_of_c_won|0]", "Counted since the record began."),
    ("lost", "Battles lost", "[?mod1440_of_c_lost|0]", "Counted since the record began."),
    ("states", "States taken", "[?mod1440_of_c_states|0]", "States you took while he had the most divisions in them."),
    ("vps", "Points taken", "[?mod1440_of_c_vps|0]", "Victory points you took from an enemy while he had the most divisions in their state."),
    ("vpl", "Points lost", "[?mod1440_of_c_vpl|0]", "Victory points an enemy took while he had the most divisions in their state."),
]


def subject(prefix, k, x, y, width, has):
    """The state or the victory point a line of a file is about: one text for each, script shows which.
    Returns the widgets and their triggers."""
    out = M.text("%s_%d_s" % (prefix, k), x, y, width, B.key("%s_%d_s" % (prefix, k), "§Y[?mod1440_%s_a^%d.GetName]§!" % (prefix, k)), M.FONT_SMALL, height=22)
    out += M.text("%s_%d_p" % (prefix, k), x, y, width, B.key("%s_%d_p" % (prefix, k), "§Y[?mod1440_%s_a^%d.GetTokenLocalizedKey]§!" % (prefix, k)),
                  M.FONT_SMALL, height=22)
    more = has + "check_variable = { mod1440_%s_date^num > %d }\n" % (prefix, k)
    return out, (block("%s_%d_s_visible" % (prefix, k), more + "check_variable = { mod1440_%s_sa^%d = 2 }\n" % (prefix, k))
                 + block("%s_%d_p_visible" % (prefix, k), more + "check_variable = { mod1440_%s_sa^%d = 3 }\n" % (prefix, k)))


def officers(portrait_version):
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
    body += M.text("of_count", 16 + 6 * 146 + 8, 66, 100, B.key("of_count", "[?mod1440_of_rows^num|0] listed"), M.FONT_SMALL)

    # ---- column heads: a click sorts, a second click turns the order
    x = 14 + OF_FACE_W
    middle = (OF_ROW - 30) // 2             # a row is higher than its plate and its line of text: both stand in the middle
    body += M.button("of_sort_name", x, 100, M.HEAD_SPRITES[OF_NAME], B.key("of_sort_name", "Officer"),
                     tooltip=B.key("of_sort_name_tt", "Back to the order of the game."))
    effects += block("of_sort_name_click", setv("mod1440_of_sort_by", 0) + "mod1440_of_list = yes\n")
    x += OF_NAME
    body += M.icon("of_h_rank_bg", x, 100, M.HEAD_SPRITES[OF_RANK])
    body += M.text("of_h_rank", x + 4, 105, OF_RANK - 8, B.key("of_h_rank", "Rank"), M.FONT_SMALL, "centre", 20)
    x += OF_RANK
    entry = M.icon("of_row_stripe", 0, 0, STRIPE % (OF_ROW_W, OF_ROW))
    entry += M.icon("of_row_pick", 0, 0, PICK % (OF_ROW_W, OF_ROW))
    entry += portrait("of_row_face", 3, 1, OF_FACE)
    properties += shown("of_row_face", "mod1440_p")
    entry += M.button("of_row", OF_FACE_W, middle, M.HEAD_SPRITES[OF_NAME], tooltip=B.key("of_row_tt", "Show this officer's record"))
    entry += plain("of_row_name", OF_FACE_W + 10, middle + 4, OF_NAME - 16, B.key("of_row_name", "[THIS.GetName]"), height=22)
    row_triggers += block("of_row_stripe_visible", is_one("mod1440_of_odd") + "\n") + block("of_row_pick_visible", is_one("mod1440_of_picked") + "\n")
    for rank, label, trigger in (("fm", "Marshal", "is_field_marshal = yes"), ("gen", "General", "is_corps_commander = yes"),
                                 ("adm", "Admiral", "is_navy_leader = yes")):
        entry += M.text("of_row_%s" % rank, OF_FACE_W + OF_NAME + 4, middle + 5, OF_RANK - 8, B.key("of_rank_%s" % rank, label), M.FONT_SMALL, "centre", 22)
        row_triggers += block("of_row_%s_visible" % rank, trigger + "\n")
    keys = ""
    rx = OF_FACE_W + OF_NAME + OF_RANK
    for number, (name, value, width, label, tip) in enumerate(OF_COLUMNS, start=1):
        body += M.button("of_sort_%s" % name, x, 100, M.HEAD_SPRITES[width], B.key("of_sort_%s" % name, label),
                         tooltip=B.key("of_sort_%s_tt" % name, tip + "\\nClick to sort, click again to turn the order."))
        effects += block("of_sort_%s_click" % name, (
            iff("check_variable = { mod1440_of_sort_by = %d }" % number, flip("mod1440_of_up"))
            + els(setv("mod1440_of_sort_by", number) + setv("mod1440_of_up", 0))
            + setv("mod1440_of_arrow_x", x + width - M.ARROW_DX) + "mod1440_of_list = yes\n"))
        key = tmp("of_key", value)
        if name in OF_NAVY:
            key += iff("is_navy_leader = yes", tmp("of_key", OF_NAVY[name]))
        keys += iff("check_variable = { ROOT.mod1440_of_sort_by = %d }" % number, key, "if" if number == 1 else "else_if")
        # a number stands under the middle of its head
        entry += M.text("of_cell_%s" % name, rx + 4, middle + 4, width - 8, B.key("of_cell_%s" % name, "[?%s|0]" % value), M.FONT_LABEL, "centre", 22)
        if name in OF_NAVY:
            entry += M.text("of_cell_%s_navy" % name, rx + 4, middle + 4, width - 8, B.key("of_cell_%s_navy" % name, "[?%s|0]" % OF_NAVY[name]),
                            M.FONT_LABEL, "centre", 22)
            row_triggers += block("of_cell_%s_visible" % name, "NOT = { is_navy_leader = yes }\n")
            row_triggers += block("of_cell_%s_navy_visible" % name, "is_navy_leader = yes\n")
        elif name in ("won", "lost", "dec"):
            row_triggers += block("of_cell_%s_visible" % name, M.more_than_zero(value))
        x += width
        rx += width
    first = x - sum(column[2] for column in OF_COLUMNS) + OF_COLUMNS[0][2] - M.ARROW_DX
    body += scaled("of_arrow_down", first, 100 + M.ARROW_DY, "GFX_arrow_down_small", M.ARROW)
    body += scaled("of_arrow_up", first, 100 + M.ARROW_DY, "GFX_arrow_up_small", M.ARROW)
    properties += block("of_arrow_down", "x = mod1440_of_arrow_x\n") + block("of_arrow_up", "x = mod1440_of_arrow_x\n")
    triggers += block("of_arrow_down_visible", M.more_than_zero("mod1440_of_sort_by") + "NOT = { %s }\n" % is_one("mod1440_of_up"))
    triggers += block("of_arrow_up_visible", M.more_than_zero("mod1440_of_sort_by") + is_one("mod1440_of_up") + "\n")
    body += listing("of_list", "of_grid", 14, 132, OF_ROW_W + 30, REC_H - 132 - 14, OF_ROW)
    # the row's scope is the officer: the mark of the one chosen before is taken off, his put on
    effects += block("of_row_click", (
        "mod1440_of_me = yes\n"
        + block("ROOT", iff(is_one("mod1440_of_has_sel"), block("var:mod1440_of_sel", setv("mod1440_of_picked", 0)))
                + setv("mod1440_of_sel", "of_me") + setv("mod1440_of_has_sel", 1))
        + setv("mod1440_of_picked", 1) + block("ROOT", "mod1440_of_card = yes\n")))

    # ---- the file of the chosen officer: his portrait, and beside it who he is and what he has done
    has = is_one("mod1440_of_has_sel") + "\n"
    side = OF_CARD_W - OF_SIDE - 16
    inner = portrait("of_c_face", 16, 14)
    properties += shown("of_c_face", "mod1440_of_c_p")
    inner += M.text("of_c_name", OF_SIDE, 10, side, B.key("of_c_name", "[?mod1440_of_sel.GetName]"), M.FONT_TITLE, height=40)
    inner += M.text("of_c_none", 16, 18, OF_CARD_W - 32, B.key("of_c_none", "Click an officer in the table to open his file."), M.FONT_LABEL)
    triggers += shown_if(["of_c_face", "of_c_name"], has) + block("of_c_none_visible", "NOT = { %s }\n" % has.strip())

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
            ("rank", OF_SIDE + 2, 56, 150, M.FONT_LABEL, "left", [("_1", "§YField Marshal§!", "check_variable = { mod1440_of_c_rank = 1 }\n"),
                                                                  ("_2", "§YGeneral§!", "check_variable = { mod1440_of_c_rank = 2 }\n"),
                                                                  ("_3", "§YAdmiral§!", rank3)]),
            ("service", OF_SIDE + 160, 58, 180, M.FONT_SMALL, "left", [("_on", "serving", "NOT = { %s }\n" % is_one("mod1440_of_c_former")),
                                                                       ("_off", "§Rno longer serving§!", is_one("mod1440_of_c_former") + "\n")]),
            ("cmd", OF_SIDE + 2, 80, 300, M.FONT_SMALL, "left", [("_army", "commands [?mod1440_of_c_cmd|0] divisions", "NOT = { %s }\n" % rank3.strip()),
                                                                 ("_navy", "commands [?mod1440_of_c_cmd|0] ships", rank3)])):
        piece, extra = variants(name, x, y, width, font, fmt, options)
        inner += piece
        triggers += extra
    for n, (name, label, value, tip) in enumerate(OF_FIGURES):
        piece, extra = tile("of_c_" + name, OF_SIDE + (n % 3) * (SMALL_TILE + 8), 108 + (n // 3) * (TILE_H + 6), label, value, tip, has, width=SMALL_TILE)
        inner += piece
        triggers += extra
    for n, (name, label) in enumerate((("since", "Commissioned"), ("prom", "Promoted to field marshal"), ("lvl", "Last skill level"))):
        y = 254 + n * 24
        inner += M.text("of_c_%s_l" % name, 18, y, 300, B.key("of_c_%s_l" % name, label), M.FONT_SMALL, height=22)
        options = [("", "[?mod1440_of_c_%s.%s]" % (name, LONG), is_one("mod1440_of_c_has_%s" % name) + "\n")]
        options.append(("_old", "before the record began" if name == "since" else "-", "NOT = { %s }\n" % is_one("mod1440_of_c_has_%s" % name)))
        piece, extra = variants(name, 320, y - 2, OF_CARD_W - 336, M.FONT_LABEL, "left", options)
        inner += piece
        triggers += extra + block("of_c_%s_l_visible" % name, has)

    # ---- his decorations: the medals side by side, then their names
    y = 332
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
            inner += scaled(widget, 14 + k * 60, y + 34, MEDAL_STRIP % name, 1.0, tip)
            properties += block(widget, "frame = mod1440_of_c_dec_frame^%d\n" % k)
            triggers += block(widget + "_visible", more + "check_variable = { mod1440_of_c_dec_set^%d = %d }\n" % (k, s))
    for k in range(DEC_LINES):
        more = has + "check_variable = { mod1440_of_c_dec_n > %d }\n" % k
        ly = y + 122 + k * 22
        inner += M.text("of_c_dec_%d" % k, 18, ly, 430, B.key("of_c_dec_%d" % k, "[?mod1440_of_c_dec_key^%d.GetTokenLocalizedKey]" % k),
                        M.FONT_SMALL, height=22)
        inner += M.text("of_c_dec_%d_d" % k, 460, ly, OF_CARD_W - 476,
                        B.key("of_c_dec_%d_d" % k, "[?mod1440_of_c_dec_date^%d.%s]" % (k, LONG)), M.FONT_SMALL, height=22)
        triggers += block("of_c_dec_%d_visible" % k, more) + block("of_c_dec_%d_d_visible" % k, more)

    # ---- the medals his country can award
    y += 122 + DEC_LINES * 22 + 6
    inner += M.text("of_md_title", 16, y, 400, B.key("of_md_title", "Award a decoration"), M.FONT_CARD, height=30)
    inner += M.text("of_md_hint", 18, y + 32, OF_CARD_W - 36, B.key(
        "of_md_hint", "Your country's medals as the game has them. For an officer they are a record only: no bonus, no cost."), M.FONT_SMALL, height=22)
    triggers += block("of_md_title_visible", has) + block("of_md_hint_visible", has)
    y += 58
    half = OF_CARD_W // 2 - 8
    for k in range(MEDAL_SLOTS):
        sx = 18 + (k % 2) * half
        sy = y + (k // 2) * 46
        more = has + "check_variable = { mod1440_md_count > %d }\n" % k
        for s, name in enumerate(sets):
            widget = "of_md_%d_%s" % (k, name)
            inner += scaled(widget, sx - 2, sy - 4, MEDAL_STRIP % name, 0.6)
            properties += block(widget, "frame = mod1440_md_frame^%d\n" % k)
            triggers += block(widget + "_visible", has + "check_variable = { mod1440_md_set^%d = %d }\n" % (k, s))
        inner += M.text("of_md_%d_name" % k, sx + 40, sy - 2, half - 46,
                        B.key("of_md_%d_name" % k, "[?mod1440_md_key^%d.GetTokenLocalizedKey]" % k), M.FONT_SMALL, height=22)
        inner += M.button("of_award_%d" % k, sx + 40, sy + 17, "GFX_sort_button_100x29", B.key("of_award", "Award"))
        inner += M.text("of_md_%d_held" % k, sx + 148, sy + 22, 150, B.key("of_md_held", "§Gawarded§!"), M.FONT_SMALL, height=22)
        held = "check_variable = { mod1440_md_has^%d = 1 }\n" % k
        triggers += block("of_md_%d_name_visible" % k, more) + block("of_award_%d_visible" % k, more)
        triggers += block("of_award_%d_click_enabled" % k, "NOT = { %s }\n" % held.strip()) + block("of_md_%d_held_visible" % k, more + held)
        effects += block("of_award_%d_click" % k, tmp("md_k", k) + "mod1440_md_award = yes\n")

    # ---- what the War Diary has about him: his own lines, and the states and victory points he was at
    y += (MEDAL_SLOTS // 2) * 46 + 2
    inner += M.text("of_ln_title", 16, y, 400, B.key("of_ln_title", "In the War Diary"), M.FONT_CARD, height=30)
    inner += M.text("of_ln_none", 18, y + 36, 500, B.key("of_ln_none", "Nothing yet."), M.FONT_SMALL, height=22)
    triggers += block("of_ln_title_visible", has) + block("of_ln_none_visible", has + "check_variable = { mod1440_of_ln_n < 1 }\n")
    for k in range(CARD_LINES):
        more = has + "check_variable = { mod1440_of_ln_n > %d }\n" % k
        inner += M.text("of_ln_%d_d" % k, 18, y + 36 + k * 22, 170, B.key("of_ln_%d_d" % k, "[?mod1440_of_ln_date^%d.%s]" % (k, LONG)),
                        M.FONT_SMALL, height=22)
        inner += M.text("of_ln_%d" % k, 196, y + 36 + k * 22, 200,
                        B.key("of_ln_%d" % k, "[?mod1440_of_ln_kind^%d.GetTokenLocalizedKey]" % k), M.FONT_SMALL, height=22)
        piece, extra = subject("of_ln", k, 400, y + 36 + k * 22, OF_CARD_W - 416, has)
        inner += piece
        triggers += block("of_ln_%d_d_visible" % k, more) + block("of_ln_%d_visible" % k, more) + extra
    body += M.box("of_card", OF_CARD_X, 96, OF_CARD_W, REC_H - 96 - 14, inner, M.CARD_BG)

    gui, script = page_gui("of", 1, body, dirty="mod1440_rec_dirty",
                           lists=block("of_grid", 'array = mod1440_of_rows\nchange_scope = yes\nentry_container = "mod1440_records_officer_row"\n'),
                           effects=effects, triggers=triggers + row_triggers, properties=properties)
    gui += row("mod1440_records_officer_row", OF_ROW_W, OF_ROW, entry)

    # ---- script
    # THIS is nothing a variable can hold for an officer whose command came by an effect: of_me is (places())
    has_me = "NOT = { check_variable = { of_me = 0 } }"
    mark = setv("mod1440_of_seen_day", "global.num_days") + "mod1440_of_me = yes\n" + iff(
        "NOT = { %s } %s" % (is_one("mod1440_of_known"), has_me), (
            setv("mod1440_of_known", 1) + "add_to_array = { PREV.mod1440_of_known = of_me }\n"
            # No hook tells of a command given by an effect. An officer first met after the country's list was made
            # is taken as commissioned on that day; the first few of a day get a line, the others share one.
            + iff("check_variable = { of_had = 1 } NOT = { has_variable = mod1440_of_since_day }", (
                setv("mod1440_of_since", "global.date") + setv("mod1440_of_since_day", "global.num_days")
                + "add_to_temp_variable = { of_new = 1 }\n"
                + iff("check_variable = { of_new < %d }" % (COMM_LINES + 1),
                      fill("commissioned", a="of_me") + block("PREV", "mod1440_ev_add = yes\n"))))))
    # his portrait is looked up once, and again when the game's list of characters has changed
    mark += iff("NOT = { check_variable = { mod1440_p_ver = %d } }" % portrait_version, "mod1440_p_officer = yes\n")
    # an officer who serves no longer is not seen by the daily run: his portrait is looked up when the list is made
    keep = iff("NOT = { check_variable = { mod1440_p_ver = %d } }" % portrait_version, "mod1440_p_officer = yes\n") + tmp("of_keep", 1)
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

    def his(log):
        """A line of a log that is about the chosen officer: he is its person, or the officer on the spot."""
        return ("check_variable = { mod1440_of_ln_date^num < %d } OR = { "
                "AND = { check_variable = { mod1440_%s_sa^mg_m = 1 } check_variable = { mod1440_%s_a^mg_m = mod1440_of_sel } } "
                "AND = { check_variable = { mod1440_%s_sc^mg_m = 1 } check_variable = { mod1440_%s_c^mg_m = mod1440_of_sel } } }"
                % (CARD_LINES, log, log, log, log))

    def his_line(log):
        """The date and the words of the line; and what it is about, unless that is the officer himself."""
        return ("add_to_array = { mod1440_of_ln_date = mod1440_%s_date^mg_m }\nadd_to_array = { mod1440_of_ln_kind = mod1440_%s_kind^mg_m }\n" % (log, log)
                + iff("check_variable = { mod1440_%s_sa^mg_m > 1 }" % log,
                      "add_to_array = { mod1440_of_ln_a = mod1440_%s_a^mg_m }\nadd_to_array = { mod1440_of_ln_sa = mod1440_%s_sa^mg_m }\n" % (log, log))
                + els("add_to_array = { mod1440_of_ln_a = 0 }\nadd_to_array = { mod1440_of_ln_sa = 0 }\n"))

    medals = "".join(iff("check_variable = { mod1440_md_id^num < %d } %s" % (MEDAL_SLOTS, available), (
        "add_to_array = { mod1440_md_id = %d }\nadd_to_array = { mod1440_md_key = token:%s }\n"
        "add_to_array = { mod1440_md_set = %d }\nadd_to_array = { mod1440_md_frame = %d }\n" % (n, name, sets.index(strip), frame)))
        for n, (name, strip, frame, available) in enumerate(MEDALS, start=1))
    script_effects = (
        places()
        + "# Officers: marks every officer who serves today with the day, and adds an officer the record does not know\n"
        "# yet to its list. A retired officer keeps his place in that list (X34).\n"
        + block("mod1440_of_seen", (
            "mod1440_of_refs = yes\n" + tmp("of_had", 0) + iff(is_one("mod1440_of_listed"), tmp("of_had", 1)) + tmp("of_new", 0)
            # the game's own loops reach every leader; its arrays army_leaders and navy_leaders hold nothing in the
            # place of one without a number
            + block("every_army_leader", mark) + block("every_navy_leader", mark)
            + setv("mod1440_of_listed", 1)
            + iff("check_variable = { of_new > %d }" % COMM_LINES, (
                tmp("of_more", "of_new") + "subtract_from_temp_variable = { of_more = %d }\n" % COMM_LINES
                + line("commissioned_more") + "add_to_variable = { mod1440_ct^%d = of_more }\n" % NUMBER["commissioned"]))))
        + "\n# Officers: makes the list of the page again: who the filter wants, in the order of the chosen column,\n"
        "# every second row marked for its stripe.\n"
        + block("mod1440_of_list", (
            "mod1440_of_seen = yes\nclear_array = mod1440_of_rows\n"
            + block("for_each_scope_loop", "array = mod1440_of_known\n" + keep
                    + iff("check_variable = { of_keep = 1 }", "mod1440_of_me = yes\n" + iff(
                        has_me, "add_to_array = { ROOT.mod1440_of_rows = of_me }\n")))
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
            "mod1440_ev_grow = yes\n" + "".join("clear_array = mod1440_of_c_%s\n" % part for part in DEC_ARRAYS[1:])
            + block("var:mod1440_of_sel", (
                setv("PREV.mod1440_of_c_skill", "skill_level") + setv("PREV.mod1440_of_c_rank", 2) + setv("PREV.mod1440_of_c_cmd", "num_units")
                + iff("is_field_marshal = yes", setv("PREV.mod1440_of_c_rank", 1))
                + iff("is_navy_leader = yes", setv("PREV.mod1440_of_c_rank", 3) + setv("PREV.mod1440_of_c_cmd", "num_ships"))
                + setv("PREV.mod1440_of_c_won", "mod1440_of_won") + setv("PREV.mod1440_of_c_lost", "mod1440_of_lost")
                + setv("PREV.mod1440_of_c_states", "mod1440_of_states")
                + setv("PREV.mod1440_of_c_vps", "mod1440_of_vps") + setv("PREV.mod1440_of_c_vpl", "mod1440_of_vpl")
                + iff("NOT = { check_variable = { mod1440_p_ver = %d } }" % portrait_version, "mod1440_p_officer = yes\n")
                + setv("PREV.mod1440_of_c_p", "mod1440_p")
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
            + "".join("clear_array = mod1440_of_ln_%s\n" % part for part in ("date", "kind", "a", "sa"))
            + merged(his, his_line)
            + setv("mod1440_of_ln_n", "mod1440_of_ln_date^num")
            + pad([("mod1440_of_ln_date", 0), ("mod1440_of_ln_kind", BLANK), ("mod1440_of_ln_a", 0), ("mod1440_of_ln_sa", 0)], CARD_LINES)))
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
        # an officer without a number whose place is not known yet: it is looked for before the line is written
        return iff(human, setv("mod1440_of_%s" % name, "global.date") + setv("mod1440_of_%s_day" % name, "global.num_days")
                   + "mod1440_of_me = yes\n"
                   + iff("check_variable = { of_me = 0 }", block("FROM", "mod1440_of_refs = yes\n") + "mod1440_of_me = yes\n")
                   + iff("NOT = { check_variable = { of_me = 0 } }", fill(kind, a="of_me") + block("FROM", "mod1440_ev_add = yes\n")))

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


# ---------------------------------------------------------------- characters a variable cannot hold as they are

# A variable holds a unit leader as a number the game gave him, and a character who is no unit leader as his
# place in the game's list of characters (Engine Facts X66, X67). A leader whose command came by an effect
# (add_corps_commander_role and its siblings: 125 uses in the game's own files, and how most mods add generals)
# has no number: THIS is REF_NONE for every one of them. He is a character all the same, and his place leads to
# him. So his place is looked for once (he gets a mark, every place is entered until the mark is met) and kept
# on him as mod1440_ch_at. A place lasts as long as the game loads the same characters: after a game update or
# another set of mods the same number is somebody else. That is noticed (the character at the highest place the
# mod keeps no longer says so himself), everybody is found again and every list that holds a place is put right.
REF_NONE = "-21474.83648"       # what a variable holds of a leader without a number
REF_FIRST = "5368.70912"        # the first place: 2^29 hundred-thousandths
REF_STEP = "0.00001"            # from one place to the next
REF_BLOCKS = 120                # how far the list is searched, in thousands of places (a loop ends after 1000 rounds)
COMM_LINES = 8                  # officers first met on one day who get a line of their own in the War Diary


def places():
    here = "check_variable = { mod1440_ch_at = %s }"
    is_place = "check_variable = { %s > 5368 }"
    # a leader without a number: does his place still lead to him, or has he none yet?
    need = tmp("rf_me", "THIS") + iff("check_variable = { rf_me = %s }" % REF_NONE, (
        iff("check_variable = { mod1440_ch_at > 0 }", (
            tmp("rf_r", "mod1440_ch_at") + tmp("rf_ok", 0)
            + block("PREV", block("var:rf_r", iff(here % "rf_r", tmp("rf_ok", 1))))
            + iff("check_variable = { rf_ok = 0 }", tmp("rf_stale", 1))))
        + els(iff("NOT = { has_variable = mod1440_ch_at }", setv("mod1440_ch_probe", 1) + "add_to_temp_variable = { rf_need = 1 }\n"))))
    lost = iff("has_variable = mod1440_ch_probe", "clear_variable = mod1440_ch_probe\n" + setv("mod1440_ch_at", -1))
    step = (
        block("var:rf_c", (
            iff("has_variable = mod1440_ch_probe", (
                "clear_variable = mod1440_ch_probe\n" + setv("mod1440_ch_at", "rf_c")
                + "add_to_temp_variable = { rf_found = 1 }\n" + tmp("rf_top", "rf_c")))
            + iff("check_variable = { mod1440_ch_at > 0 }", (
                iff("NOT = { %s }" % (here % "rf_c"), (
                    "add_to_temp_array = { rf_old = mod1440_ch_at }\nadd_to_temp_array = { rf_new = rf_c }\n" + setv("mod1440_ch_at", "rf_c")))
                + tmp("rf_top", "rf_c")), "else_if")))
        + "add_to_temp_variable = { rf_c = %s }\n" % REF_STEP)
    going = "OR = { check_variable = { rf_stale = 1 } check_variable = { rf_found < rf_need } }"
    out = (
        "# Characters: what a variable can hold of the officer in scope, in of_me. His number, or for a leader without\n"
        "# one his place; 0 while that is not known.\n"
        + block("mod1440_of_me", tmp("of_me", "THIS") + iff("check_variable = { of_me = %s }" % REF_NONE, (
            tmp("of_me", 0) + iff("check_variable = { mod1440_ch_at > 0 }", tmp("of_me", "mod1440_ch_at")))))
        + "\n# Characters: writes on the character at the place ch_v that he stands there, so that a later day can tell\n"
        "# whether the place is still his. For the scope of a country: a place nobody stands on leaves the scope\n"
        "# where it is, and what THIS is there tells that apart.\n"
        + block("mod1440_ch_mark", iff(is_place % "ch_v", block("var:ch_v", (
            tmp("ch_t", "THIS") + iff("OR = { check_variable = { ch_t = ch_v } check_variable = { ch_t < 0 } }", (
                setv("mod1440_ch_at", "ch_v")
                + iff("check_variable = { ch_v > global.mod1440_ch_top }", setv("global.mod1440_ch_top", "ch_v"))))))))
        + "\n# Characters: for the country in scope, gives every general and admiral without a number his place, and\n"
        "# looks whether the places kept so far still lead to their characters. If not, everybody is found again\n"
        "# (rf_old, rf_new: where each one was and is) and the lists of every country with a record are put right.\n"
        + block("mod1440_of_refs", (
            "mod1440_ch_adopt = yes\n"
            + tmp("rf_stale", 0) + tmp("rf_need", 0) + tmp("rf_found", 0) + "clear_temp_array = rf_old\nclear_temp_array = rf_new\n"
            + iff("check_variable = { global.mod1440_ch_top > 0 }", (
                tmp("rf_r", "global.mod1440_ch_top") + tmp("rf_ok", 0) + block("var:rf_r", iff(here % "rf_r", tmp("rf_ok", 1)))
                + iff("check_variable = { rf_ok = 0 }", tmp("rf_stale", 1))))
            + block("every_army_leader", need) + block("every_navy_leader", need)
            + iff(going, (
                tmp("rf_c", REF_FIRST) + tmp("rf_top", 0)
                + block("for_loop_effect", "start = 0\nend = %d\nvalue = rf_block\n" % REF_BLOCKS + iff(
                    going, block("for_loop_effect", "start = 0\nend = 1000\nvalue = rf_i\n" + step)))
                # one who was not found is not looked for again
                + block("every_army_leader", lost) + block("every_navy_leader", lost)
                + iff("check_variable = { rf_stale = 1 }", (
                    setv("global.mod1440_ch_top", "rf_top")
                    + block("every_country", "limit = { %s }\nmod1440_ch_remap = yes\n" % is_one("mod1440_ev_begun"))))
                + els(iff("check_variable = { rf_top > global.mod1440_ch_top }", setv("global.mod1440_ch_top", "rf_top")))))))
        + "\n# Characters: where the character of the place rm_v stands now, in rm_to: looked up in rf_old and rf_new, and 0\n"
        "# when nobody at that place says it is his (the character is gone, or was never marked).\n"
        + block("mod1440_ch_place", tmp("rm_to", "rm_v") + iff(is_place % "rm_v", (
            tmp("rm_brk", 0)
            + block("for_each_loop", "array = rf_old\nindex = rm_k\nvalue = rm_o\nbreak = rm_brk\n" + iff(
                "check_variable = { rm_o = rm_v }", tmp("rm_to", "rf_new^rm_k") + tmp("rm_brk", 1)))
            + tmp("rm_ok", 0) + block("var:rm_to", iff(here % "rm_to", tmp("rm_ok", 1)))
            + iff("check_variable = { rm_ok = 0 }", tmp("rm_to", 0) + "add_to_temp_variable = { rm_lost = 1 }\n"))))
    )

    def in_array(name, test=None, also=""):
        body = tmp("rm_v", "%s^rm_i" % name) + "mod1440_ch_place = yes\n" + setv("%s^rm_i" % name, "rm_to") + also
        return block("for_loop_effect", "start = 0\nend = %s^num\nvalue = rm_i\n" % name + (iff(test, body) if test else body))

    def in_variable(name):
        return tmp("rm_v", name) + "mod1440_ch_place = yes\n" + setv(name, "rm_to")

    logs = ""
    for log in ("ev", "tr"):
        for part, kind in (("a", "sa"), ("c", "sc")):
            logs += in_array("mod1440_%s_%s" % (log, part), "check_variable = { mod1440_%s_%s^rm_i = 1 }" % (log, kind),
                             iff("check_variable = { rm_to = 0 }", setv("mod1440_%s_%s^rm_i" % (log, kind), 0)))
    offices = "".join(iff(is_one("mod1440_gv_of_%d_has" % k), in_variable("mod1440_gv_of_%d" % k)) for k in range(len(OFFICES)))
    out += (
        "\n# Characters: puts right every place the country in scope keeps, after the game's list of characters has\n"
        "# changed: the people on the lines of both logs, the list of officers, the chosen officer, the offices.\n"
        + block("mod1440_ch_remap", (
            tmp("rm_lost", 0) + logs + in_array("mod1440_of_known")
            # an officer who is gone leaves the list
            + "clear_temp_array = rm_keep\n"
            + block("for_each_loop", "array = mod1440_of_known\nvalue = rm_v\n" + iff(
                "NOT = { check_variable = { rm_v = 0 } }", "add_to_temp_array = { rm_keep = rm_v }\n"))
            + "clear_array = mod1440_of_known\n"
            + block("for_each_loop", "array = rm_keep\nvalue = rm_v\nadd_to_array = { mod1440_of_known = rm_v }\n")
            + iff(is_one("mod1440_of_has_sel"), in_variable("mod1440_of_sel")
                  + iff("check_variable = { mod1440_of_sel = 0 }", setv("mod1440_of_has_sel", 0)))
            # the offices: one holder who cannot be found, and the copies are taken again without a line
            + tmp("rm_lost", 0) + in_variable("mod1440_gv_leader") + offices
            + in_array("mod1440_gv_adv") + in_array("mod1440_gv_hc")
            + iff("check_variable = { rm_lost > 0 }", setv("mod1440_gv_begun", 0))))
    )

    def adopt_array(name, test=None):
        body = tmp("ch_v", "%s^rm_i" % name) + "mod1440_ch_mark = yes\n"
        return block("for_loop_effect", "start = 0\nend = %s^num\nvalue = rm_i\n" % name + (iff(test, body) if test else body))

    adopt = "".join(adopt_array("mod1440_%s_%s" % (log, part), "check_variable = { mod1440_%s_%s^rm_i = 1 }" % (log, kind))
                    for log in ("ev", "tr") for part, kind in (("a", "sa"), ("c", "sc")))
    out += (
        "\n# Characters: once for a country, marks everybody whose place its lists hold already (a game saved by an\n"
        "# earlier build of the mod).\n"
        + block("mod1440_ch_adopt", iff("NOT = { %s }" % is_one("mod1440_ch_adopted"), (
            setv("mod1440_ch_adopted", 1) + adopt + adopt_array("mod1440_of_known") + "mod1440_gv_marks = yes\n")))
        + "\n# Characters: marks the holders of the offices the Government page keeps.\n"
        + block("mod1440_gv_marks", (
            tmp("ch_v", "mod1440_gv_leader") + "mod1440_ch_mark = yes\n"
            + "".join(iff(is_one("mod1440_gv_of_%d_has" % k), tmp("ch_v", "mod1440_gv_of_%d" % k) + "mod1440_ch_mark = yes\n")
                      for k in range(len(OFFICES)))
            + block("for_each_loop", "array = mod1440_gv_adv\nvalue = ch_v\nmod1440_ch_mark = yes\n")
            + block("for_each_loop", "array = mod1440_gv_hc\nvalue = ch_v\nmod1440_ch_mark = yes\n")))
        + "\n"
    )
    return out


# ---------------------------------------------------------------- Government (E3)

GV_COL = (REC_W - 28 - 24) // 3
GV_ROW = 26
GV_H = REC_H - 62 - 14          # what a column has from the title strip to the bottom
GV_LIST_ROW_W = GV_COL - 16 - 30
GV_FACE = 0.8                   # the portrait of the head of government: 125x168 of 156x210
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


def government(portrait_version):
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

    # ---- column 1: who rules. The country's flag beside the name, the portrait beside the party and the dates
    face_w = int(156 * GV_FACE)
    beside = GV_COL - 16 - face_w - 12              # where the texts beside the portrait end
    inner = M.text("gv_leader", 16, 44, GV_COL - 32 - 94, B.key("gv_leader", "[ROOT.GetLeader]"), M.FONT_TITLE, height=40)
    inner += flag("gv_flag", GV_COL - 16 - 82, 40)
    properties += flown("gv_flag", "ROOT")
    inner += portrait("gv_face", GV_COL - 16 - face_w, 100, GV_FACE)
    properties += shown("gv_face", "mod1440_gv_p")
    inner += M.text("gv_party", 18, 100, beside - 18, B.key("gv_party", "§Y[ROOT.GetRulingParty]§!, [ROOT.GetRulingIdeology]"), M.FONT_LABEL, height=22)
    inner += M.text("gv_party_long", 18, 124, beside - 18, B.key("gv_party_long", "[ROOT.GetRulingPartyLong]"), M.FONT_SMALL, height=22)
    top = 166
    inner += M.text("gv_office_l", 18, top, 130, B.key("gv_office_l", "In office"), M.FONT_SMALL, height=22)
    piece, extra = since("gv_leader_since", 150, top, "mod1440_gv_leader_since", "mod1440_gv_leader_old", beside - 150, word="since ")
    inner += piece
    triggers += extra
    inner += M.text("gv_election_l", 18, top + GV_ROW, 130, B.key("gv_election_l", "Last election"), M.FONT_SMALL, height=22)
    inner += M.text("gv_election", 150, top + GV_ROW, beside - 150, B.key("gv_election", "[ROOT.GetLastElection]"), M.FONT_SMALL, height=22)
    inner += M.text("gv_next_l", 18, top + 2 * GV_ROW, 130, B.key("gv_next_l", "Next election"), M.FONT_SMALL, height=22)
    inner += M.text("gv_next", 150, top + 2 * GV_ROW, beside - 150, B.key("gv_next", "in [?days_until_next_election|0] days"), M.FONT_SMALL, height=22)
    inner += M.text("gv_next_none", 150, top + 2 * GV_ROW, beside - 150, B.key("gv_next_none", "none"), M.FONT_SMALL, height=22)
    triggers += block("gv_next_visible", "check_variable = { days_until_next_election > -1 }\n")
    triggers += block("gv_next_none_visible", "check_variable = { days_until_next_election < 0 }\n")
    place(0, "chief", "Head of government", inner, 100 + int(210 * GV_FACE) + 12)

    # parties: the name and its share, the leader, and a bar as long as the party's support
    inner = ""
    for n, (ideology, token_name) in enumerate(IDEOLOGIES):
        y = 44 + n * 62
        inner += M.text("gv_p_%d" % n, 18, y, GV_COL - 110, B.key("gv_p_%d" % n, "[ROOT.Get%sParty]" % ideology), M.FONT_SMALL, height=22, fixed=True)
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
        piece, extra = tile("gv_f_" + name, (GV_COL - 2 * TILE_W - 12) // 2 + (n % 2) * (TILE_W + 12), 44 + (n // 2) * (TILE_H + 8), label, "[?mod1440_gv_n_%s|0]" % name, tip)
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
        # NOT with two conditions inside means "neither": the test "not this holder already" is written as an OR
        offices += iff("any_character = { %s = yes }" % trigger, iff(
            "OR = { NOT = { %s } NOT = { check_variable = { %s = %s } } }" % (is_one(holder + "_has"), holder, variable), (
                setv(holder, variable) + setv(holder + "_has", 1) + setv(holder + "_since", "global.date") + setv(holder + "_old", 1)
                + iff(begun, setv(holder + "_old", 0) + line("appointed", a=variable)))))
        offices += els(iff(is_one(holder + "_has"), setv(holder + "_has", 0) + iff(begun, line("dismissed", a=holder))))
    laws = ""
    for n, (label, ideas) in enumerate(LAWS):
        laws += setv("mod1440_gv_law_%d" % n, token("gv_law_other", "another law"))
        laws += "".join(iff("has_idea = %s" % idea, setv("mod1440_gv_law_%d" % n, "token:" + idea)) for idea in ideas)
    support = "".join(setv("mod1440_gv_pop_%d" % n, "party_popularity_100@" + token_name) for n, (ideology, token_name) in enumerate(IDEOLOGIES))
    # the leader's portrait: looked up when another leader rules, and when the game's list of characters has changed
    face = leader_portrait("THIS", "mod1440_gv_p", portrait_version)
    script_effects = (
        "# Government: compares who holds each office with yesterday's copy. A new name gets today's date and a line\n"
        "# in the War Diary, a name that is gone a line. The first run only takes the copy. Then the laws in force,\n"
        "# the length of the parties' bars, the leader's portrait and the figures of the record.\n"
        + block("mod1440_gv_daily", (
            iff("NOT = { check_variable = { mod1440_gv_leader = country_leader } }", (
                setv("mod1440_gv_leader", "country_leader") + setv("mod1440_gv_leader_since", "global.date") + setv("mod1440_gv_leader_old", 1)
                + iff(begun, setv("mod1440_gv_leader_old", 0) + line("leader", a="country_leader"))))
            + face
            + offices + office_array("political_advisor", "mod1440_gv_adv") + office_array("high_command", "mod1440_gv_hc")
            + laws + support + pad([("mod1440_ct", 0)], len(KINDS) + 8) + sums + setv("mod1440_gv_begun", 1)
            + "mod1440_gv_marks = yes\n")))
    return gui, script, script_effects


# ---------------------------------------------------------------- Wars (E4), with the counters of the air war (E5)

WR_LIST_W = 940                 # the two tables on the left
WR_ROW_W = WR_LIST_W - 30
WR_ROW = 30
WR_NAME = 300                   # the plate with the enemy's name, which is the row's button
WR_CARD_X = 14 + WR_LIST_W + 12
WR_CARD_W = REC_W - WR_CARD_X - 14
WR_FACE = 0.8                   # the portraits of the two heads of government: 125x168
WR_LINES = 20                   # lines of the War Diary a war's file shows
# What a row of a war holds. The newer parts stand last: a game saved before them has rows without (see wr_grow).
WR_PARTS = ["enemy", "since", "day0", "cas0", "taken", "lost", "days", "cas", "capd", "old", "surr", "vpt", "vpl"]
WO_PARTS = ["enemy", "since", "until", "days", "cas", "taken", "lost", "outcome", "old", "vpt", "vpl"]
WR_NEW = ["vpt", "vpl"]
WO_KEEP = 200
# the columns of a row after the name: (name, x, width, format, head, tooltip)
WR_NOW = [("since", 308, 150, "left", "Since", None), ("days", 462, 50, "right", "Days", None),
          ("cas", 516, 100, "right", "Casualties", "Your country's whole loss in that time, whoever caused it."),
          ("taken", 620, 50, "right", "Taken", "States you took from this enemy."), ("lost", 674, 50, "right", "Lost", "States you lost to this enemy."),
          ("surrender", 736, 170, "left", "Surrender", "How close the enemy is to capitulating.")]
WR_OLD = [("since", 308, 150, "left", "Since", None), ("until", 462, 150, "left", "Until", None), ("days", 616, 50, "right", "Days", None),
          ("outcome", 680, 226, "left", "Outcome", None)]
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
# the figures of one war, on its file: (name, label, value, tooltip)
WR_CARD_FIGURES = [
    ("days", "Days", "[?mod1440_wr_c_days|0]", "How long the war has lasted, or lasted."),
    ("cas", "Our casualties", "[?mod1440_wr_c_cas|0]", "Your country's whole loss in that time, whoever caused it."),
    ("taken", "States taken", "[?mod1440_wr_c_taken|0]", "States you took from this enemy."),
    ("lost", "States lost", "[?mod1440_wr_c_lost|0]", "States you lost to this enemy."),
    ("vpt", "Points taken", "[?mod1440_wr_c_vpt|0]", "Victory points you took from this enemy."),
    ("vpl", "Points lost", "[?mod1440_wr_c_vpl|0]", "Victory points this enemy took from you."),
]


def wars(portrait_version):
    body, effects, properties = head("wr", 3, "One row per enemy. Click a war for its file. Casualties are your country's whole loss in that time.")
    triggers = ""
    step = (WR_LIST_W - TILE_W) // 4
    for n, (name, label, value, tip) in enumerate(WR_FIGURES):
        piece, extra = tile("wr_f_" + name, 14 + (n % 5) * step, 62 + (n // 5) * (TILE_H + 6), label, value, tip)
        body += piece

    def columns(name, y, table):
        return heads(name, 14, y, WR_LIST_W, [(10, WR_NAME - 20, "Country", "left", "Click a war for its file.")] + [
            (x, width, label, fmt, tip) for column, x, width, fmt, label, tip in table])

    top = 62 + 2 * (TILE_H + 6) + 6
    now_h = 7 * WR_ROW + 4
    body += M.text("wr_now_title", 20, top, 400, B.key("wr_now_title", "At war with"), M.FONT_CARD, height=30)
    body += columns("wr_now_heads", top + 34, WR_NOW)
    body += listing("wr_now_list", "wr_now_grid", 14, top + 66, WR_LIST_W, now_h, WR_ROW)
    body += M.text("wr_now_none", 40, top + 78, 600, B.key("wr_now_none", "At peace."), M.FONT_LABEL)
    triggers += block("wr_now_none_visible", "check_variable = { mod1440_wr_enemy^num < 1 }\n")
    y = top + 66 + now_h + 12
    body += M.text("wr_old_title", 20, y, 400, B.key("wr_old_title", "Finished wars"), M.FONT_CARD, height=30)
    body += columns("wr_old_heads", y + 34, WR_OLD)
    body += listing("wr_old_list", "wr_old_grid", 14, y + 66, WR_LIST_W, REC_H - (y + 66) - 14, WR_ROW)
    body += M.text("wr_old_none", 40, y + 78, 600, B.key("wr_old_none", "None since the record began."), M.FONT_LABEL)
    triggers += block("wr_old_none_visible", "check_variable = { mod1440_wo_enemy^num < 1 }\n")

    def cells(prefix, kind, table, texts, name, old_test):
        """A row of one of the two tables: band, mark of the chosen war, the plate that is its button, the cells."""
        nonlocal triggers, effects
        out = M.icon(prefix + "_stripe", 0, 0, STRIPE % (WR_ROW_W, WR_ROW)) + M.icon(prefix + "_pick", 0, 0, PICK % (WR_ROW_W, WR_ROW))
        out += M.button(prefix, 0, 0, M.HEAD_SPRITES[WR_NAME], tooltip=B.key("wr_row_tt", "Open the file of this war"))
        out += plain(prefix + "_enemy", 10, 4, WR_NAME - 16, B.key(prefix + "_enemy", name), height=22)
        triggers += block(prefix + "_stripe_visible", "check_variable = { mod1440_odd^i = 1 }\n")
        triggers += block(prefix + "_pick_visible", "check_variable = { mod1440_wr_sel_kind = %d }\ncheck_variable = { mod1440_wr_sel_i = i }\n" % kind)
        effects += block(prefix + "_click", setv("mod1440_wr_sel_kind", kind) + setv("mod1440_wr_sel_i", "i") + "mod1440_wr_card = yes\n")
        for column, x, width, fmt, label, tip in table:
            if column in texts:
                out += M.text("%s_%s" % (prefix, column), x, 4, width, B.key("%s_%s" % (prefix, column), texts[column]), M.FONT_LABEL, fmt, 22)
        out += M.text(prefix + "_since_old", 308, 5, 150, B.key("gv_began", BEGAN), M.FONT_SMALL, height=22)
        triggers += block(prefix + "_since_visible", "NOT = { %s }\n" % old_test) + block(prefix + "_since_old_visible", old_test + "\n")
        return out

    # today's enemies, read by row index; the list runs over the surrender progress, which fills the bar
    entry = cells("wr_row", 1, WR_NOW, {
        "since": "[?mod1440_wr_since^i.%s]" % LONG, "days": "[?mod1440_wr_days^i|0]", "cas": "[?mod1440_wr_cas^i|0]",
        "taken": "[?mod1440_wr_taken^i|0]", "lost": "[?mod1440_wr_lost^i|0]"},
        "§Y[?mod1440_wr_enemy^i.GetNameWithFlag]§!", "check_variable = { mod1440_wr_old^i = 1 }")
    entry += M.icon("wr_row_bar", 736, 9, "GFX_1440p_SG_bar")
    entry += M.text("wr_row_pct", 845, 4, 60, B.key("wr_row_pct", "[?v|0]%"), M.FONT_LABEL, "right", 22)
    properties += block("wr_row_bar", "frame = v\n")
    gui_rows = row("mod1440_records_war_row", WR_ROW_W, WR_ROW, entry)
    # finished wars: the list runs over the days, so v is the length of the war
    entry = cells("wo_row", 2, WR_OLD, {
        "since": "[?mod1440_wo_since^i.%s]" % LONG, "until": "[?mod1440_wo_until^i.%s]" % LONG, "days": "[?v|0]",
        "outcome": "[?mod1440_wo_outcome^i.GetTokenLocalizedKey]"},
        "§Y[?mod1440_wo_enemy^i.GetNameWithFlag]§!", "check_variable = { mod1440_wo_old^i = 1 }")
    gui_rows += row("mod1440_records_past_war_row", WR_ROW_W, WR_ROW, entry)

    # ---- the file of the chosen war: the two flags, the two heads of government, the figures, the lines
    has = is_one("mod1440_wr_c_has") + "\n"
    past = has + "check_variable = { mod1440_wr_sel_kind = 2 }\n"
    lives = has + is_one("mod1440_wr_c_exists") + "\n"       # the enemy is still a country: it has a leader to show
    known = has + "check_variable = { mod1440_wr_c_old = 0 }\n"
    face_w, face_h = int(156 * WR_FACE), int(210 * WR_FACE)
    right = WR_CARD_W - 16
    them = "mod1440_wr_c_enemy"
    inner = M.text("wr_c_none", 16, 48, WR_CARD_W - 32, B.key("wr_c_none", "Click a war in a table to open its file."), M.FONT_LABEL)
    triggers += block("wr_c_none_visible", "NOT = { %s }\n" % has.strip())
    shows = []                                              # what shows for any chosen war
    inner += flag("wr_c_flag_us", 16, 44) + flag("wr_c_flag_them", right - 82, 44)
    properties += flown("wr_c_flag_us", "ROOT") + flown("wr_c_flag_them", "?" + them)
    half = (WR_CARD_W - 2 * (16 + 82 + 12)) // 2 - 6
    inner += M.text("wr_c_us", 16 + 82 + 12, 58, half, B.key("wr_c_us", "[ROOT.GetName]"), M.FONT_VALUE, height=26)
    inner += M.text("wr_c_them", right - 82 - 12 - half, 58, half, B.key("wr_c_them", "[?%s.GetName]" % them), M.FONT_VALUE, "right", 26)
    inner += portrait("wr_c_face_us", 16, 112, WR_FACE) + portrait("wr_c_face_them", right - face_w, 112, WR_FACE)
    properties += shown("wr_c_face_us", "mod1440_gv_p") + shown("wr_c_face_them", "mod1440_wr_c_p")
    block_w = (WR_CARD_W - 2 * (16 + face_w + 12)) // 2 - 6
    left_x, right_x = 16 + face_w + 12, right - face_w - 12 - block_w
    for n, (us, theirs, font) in enumerate((
            ("§Y[ROOT.GetLeader]§!", "§Y[?%s.GetLeader]§!" % them, M.FONT_LABEL),
            ("[ROOT.GetRulingParty]", "[?%s.GetRulingParty]" % them, M.FONT_SMALL),
            ("[ROOT.GetRulingIdeology]", "[?%s.GetRulingIdeology]" % them, M.FONT_SMALL))):
        inner += M.text("wr_c_us_%d" % n, left_x, 118 + n * 26, block_w, B.key("wr_c_us_%d" % n, us), font, height=22)
        inner += M.text("wr_c_them_%d" % n, right_x, 118 + n * 26, block_w, B.key("wr_c_them_%d" % n, theirs), font, "right", 22)
        shows.append("wr_c_us_%d" % n)
        triggers += block("wr_c_them_%d_visible" % n, lives)
    inner += M.text("wr_c_gone", right_x, 118, block_w, B.key("wr_c_gone", "This country is no more."), M.FONT_SMALL, "right", 22)
    triggers += block("wr_c_gone_visible", has + "NOT = { %s }\n" % is_one("mod1440_wr_c_exists")) + block("wr_c_face_them_visible", lives)
    shows += ["wr_c_flag_us", "wr_c_flag_them", "wr_c_us", "wr_c_them", "wr_c_face_us"]

    # when it began and ended, in the middle between the two portraits' feet
    y = 112 + face_h - 52
    inner += M.text("wr_c_since_l", left_x, y, 60, B.key("wr_c_since_l", "Since"), M.FONT_SMALL, height=22)
    inner += M.text("wr_c_since", left_x + 62, y - 2, 200, B.key("wr_c_since", "[?mod1440_wr_c_since.%s]" % LONG), M.FONT_LABEL, height=22)
    inner += M.text("wr_c_since_old", left_x + 62, y, 200, B.key("gv_began", BEGAN), M.FONT_SMALL, height=22)
    inner += M.text("wr_c_until_l", left_x, y + 26, 60, B.key("wr_c_until_l", "Until"), M.FONT_SMALL, height=22)
    inner += M.text("wr_c_until", left_x + 62, y + 24, 200, B.key("wr_c_until", "[?mod1440_wr_c_until.%s]" % LONG), M.FONT_LABEL, height=22)
    inner += M.text("wr_c_outcome", right_x, y + 24, block_w, B.key("wr_c_outcome", "§Y[?mod1440_wr_c_outcome.GetTokenLocalizedKey]§!"), M.FONT_LABEL, "right", 22)
    inner += M.text("wr_c_capd", right_x, y + 24, block_w, B.key("wr_c_capd", "§Ghas capitulated§!"), M.FONT_LABEL, "right", 22)
    shows.append("wr_c_since_l")
    triggers += block("wr_c_since_visible", known) + block("wr_c_since_old_visible", has + is_one("mod1440_wr_c_old") + "\n")
    triggers += shown_if(["wr_c_until_l", "wr_c_until", "wr_c_outcome"], past)
    triggers += block("wr_c_capd_visible", has + "check_variable = { mod1440_wr_sel_kind = 1 }\ncheck_variable = { mod1440_wr_c_capd > 0 }\n")

    # the figures: six tiles, then how close each side is to giving up
    y = 112 + face_h + 14
    gap = (WR_CARD_W - 32 - 4 * TILE_W) // 3
    for n, (name, label, value, tip) in enumerate(WR_CARD_FIGURES):
        piece, extra = tile("wr_c_" + name, 16 + (n % 4) * (TILE_W + gap), y + (n // 4) * (TILE_H + 8), label, value, tip, has)
        inner += piece
        triggers += extra
    for n, (name, label, value, variable, tip) in enumerate((
            ("their", "Their surrender", "[?mod1440_wr_c_surr|0]%", "mod1440_wr_c_surr", "How close this enemy is to capitulating."),
            ("our", "Our surrender", "[?surrender_progress|%0]", "mod1440_wr_c_ours", "How close your country is to capitulating."))):
        piece, extra = gauge("wr_c_" + name, 16 + (2 + n) * (TILE_W + gap), y + TILE_H + 8, B.key("wr_c_%s_l" % name, label), value, variable, tip, wide=False)
        inner += piece
        properties += extra
        when = has if name == "our" else has + "check_variable = { mod1440_wr_sel_kind = 1 }\n"
        triggers += shown_if(["wr_c_%s_bg" % name, "wr_c_%s_l" % name, "wr_c_" + name, "wr_c_%s_bar" % name], when)

    # what the War Diary has about this war
    y += 2 * (TILE_H + 8) + 8
    inner += M.text("wr_ln_title", 16, y, 400, B.key("wr_ln_title", "In the War Diary"), M.FONT_CARD, height=30)
    inner += M.text("wr_ln_none", 18, y + 36, 500, B.key("wr_ln_none", "Nothing yet."), M.FONT_SMALL, height=22)
    shows.append("wr_ln_title")
    triggers += block("wr_ln_none_visible", has + "check_variable = { mod1440_wr_ln_n < 1 }\n")
    for k in range(WR_LINES):
        more = has + "check_variable = { mod1440_wr_ln_n > %d }\n" % k
        ly = y + 36 + k * 22
        inner += M.text("wr_ln_%d_d" % k, 18, ly, 170, B.key("wr_ln_%d_d" % k, "[?mod1440_wr_ln_date^%d.%s]" % (k, LONG)), M.FONT_SMALL, height=22)
        inner += M.text("wr_ln_%d" % k, 196, ly, 200, B.key("wr_ln_%d" % k, "[?mod1440_wr_ln_kind^%d.GetTokenLocalizedKey]" % k), M.FONT_SMALL, height=22)
        piece, extra = subject("wr_ln", k, 400, ly, WR_CARD_W - 416, has)
        inner += piece
        triggers += block("wr_ln_%d_d_visible" % k, more) + block("wr_ln_%d_visible" % k, more) + extra
    triggers += shown_if(shows, has)
    body += card("wr_card", WR_CARD_X, 62, WR_CARD_W, REC_H - 62 - 14, "The war", inner)

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
             "cas": 0, "capd": 0, "old": "wr_old", "surr": 0, "vpt": 0, "vpl": 0}
    end = {"enemy": "wr_c", "since": "mod1440_wr_since^wr_j", "until": "global.date", "days": "wr_d", "cas": "wr_k",
           "taken": "mod1440_wr_taken^wr_j", "lost": "mod1440_wr_lost^wr_j", "outcome": "wr_out", "old": "mod1440_wr_old^wr_j",
           "vpt": "mod1440_wr_vpt^wr_j", "vpl": "mod1440_wr_vpl^wr_j"}
    # a game saved before a row counted victory points: the rows that are there get a 0 each
    grow = "".join(iff("check_variable = { mod1440_%s_%s^num < mod1440_%s_enemy^num }" % (table, WR_NEW[0], table), block(
        "for_loop_effect", "start = 0\nend = %d\nvalue = gr_n\n" % WO_KEEP + "".join(
            iff("check_variable = { mod1440_%s_%s^num < mod1440_%s_enemy^num }" % (table, part, table), "add_to_array = { mod1440_%s_%s = 0 }\n" % (table, part))
            for part in WR_NEW))) for table in ("wr", "wo"))

    def copy(table, parts):
        return "".join(setv("mod1440_wr_c_" + part, "mod1440_%s_%s^mod1440_wr_sel_i" % (table, part)) for part in parts)

    def of_this_war(log):
        return ("check_variable = { mod1440_wr_ln_date^num < %d } check_variable = { mod1440_%s_sb^mg_m = 1 } "
                "check_variable = { mod1440_%s_b^mg_m = mod1440_wr_c_enemy }" % (WR_LINES, log, log))

    def war_line(log):
        return ("add_to_array = { mod1440_wr_ln_date = mod1440_%s_date^mg_m }\nadd_to_array = { mod1440_wr_ln_kind = mod1440_%s_kind^mg_m }\n" % (log, log)
                + iff("check_variable = { mod1440_%s_sa^mg_m > 1 }" % log,
                      "add_to_array = { mod1440_wr_ln_a = mod1440_%s_a^mg_m }\nadd_to_array = { mod1440_wr_ln_sa = mod1440_%s_sa^mg_m }\n" % (log, log))
                + els("add_to_array = { mod1440_wr_ln_a = 0 }\nadd_to_array = { mod1440_wr_ln_sa = 0 }\n"))

    script_effects = (
        "# Wars: a row for the enemy in wr_c, from today (wr_old = 1: the war ran when the record began).\n"
        + block("mod1440_wr_open", "mod1440_wr_grow = yes\n" + iff(
            "NOT = { is_in_array = { array = mod1440_wr_enemy value = wr_c } }",
            "".join("add_to_array = { mod1440_wr_%s = %s }\n" % (part, start[part]) for part in WR_PARTS)))
        + block("mod1440_wr_grow", grow)
        + "\n# Wars: the war with wr_c is over: its row moves to the finished wars with the end date, its length, what it\n"
        "# cost and how it ended. The file that was open stays on the same war.\n"
        + block("mod1440_wr_close", "mod1440_wr_grow = yes\n" + find + iff("check_variable = { wr_j > -1 }", (
            tmp("wr_out", outcomes["peace"])
            + iff("check_variable = { mod1440_wr_capd^wr_j = 1 }", tmp("wr_out", outcomes["capitulated"]))
            + iff("is_in_array = { array = subjects value = wr_c }", tmp("wr_out", outcomes["subject"]))
            + iff("var:wr_c = { exists = no }", tmp("wr_out", outcomes["gone"]))
            + iff("check_variable = { mod1440_wr_capd^wr_j = 2 }", tmp("wr_out", outcomes["annexed"]))
            + tmp("wr_d", "global.num_days") + "subtract_from_temp_variable = { wr_d = mod1440_wr_day0^wr_j }\n"
            + tmp("wr_k", "casualties") + "subtract_from_temp_variable = { wr_k = mod1440_wr_cas0^wr_j }\n"
            + "".join("add_to_array = { array = mod1440_wo_%s value = %s index = 0 }\n" % (part, end[part]) for part in WO_PARTS)
            + "".join("remove_from_array = { array = mod1440_wr_%s index = wr_j }\n" % part for part in WR_PARTS)
            # the chosen row: a finished war moved down by one; this war is now the first of the finished; a war below it moved up
            + iff("check_variable = { mod1440_wr_sel_kind = 2 }", "add_to_variable = { mod1440_wr_sel_i = 1 }\n")
            + iff("check_variable = { mod1440_wr_sel_kind = 1 }", (
                iff("check_variable = { mod1440_wr_sel_i = wr_j }", setv("mod1440_wr_sel_kind", 2) + setv("mod1440_wr_sel_i", 0))
                + iff("check_variable = { mod1440_wr_sel_i > wr_j }", "subtract_from_variable = { mod1440_wr_sel_i = 1 }\n", "else_if")), "else_if")
            + iff("check_variable = { mod1440_wo_enemy^num > %d }" % WO_KEEP, (
                tmp("wr_last", "mod1440_wo_enemy^num") + "subtract_from_temp_variable = { wr_last = 1 }\n"
                + "".join("remove_from_array = { array = mod1440_wo_%s index = wr_last }\n" % part for part in WO_PARTS))))))
        + "\n# Wars: one more state taken from (wr_f = 1) or lost to (wr_f = 2) the enemy in wr_c, or one more victory\n"
        "# point taken (3) or lost (4).\n"
        + block("mod1440_wr_count", "mod1440_wr_grow = yes\n" + find + iff("check_variable = { wr_j > -1 }", "".join(
            iff("check_variable = { wr_f = %d }" % n, "add_to_variable = { mod1440_wr_%s^wr_j = 1 }\n" % part)
            for n, part in enumerate(("taken", "lost", "vpt", "vpl"), start=1))))
        + block("mod1440_wr_annexed", find + iff("check_variable = { wr_j > -1 }", setv("mod1440_wr_capd^wr_j", 2)))
        + "\n# Wars: the numbers of today's rows, each enemy's surrender progress for its bar, and a line in the War\n"
        "# Diary when an enemy or the country itself has capitulated. Then the file of the chosen war.\n"
        + block("mod1440_wr_daily", (
            "mod1440_wr_grow = yes\n"
            + block("for_each_loop", (
                "array = mod1440_wr_enemy\nvalue = wr_v\nindex = wr_i\n"
                + tmp("wr_d", "global.num_days") + "subtract_from_temp_variable = { wr_d = mod1440_wr_day0^wr_i }\n" + setv("mod1440_wr_days^wr_i", "wr_d")
                + tmp("wr_k", "casualties") + "subtract_from_temp_variable = { wr_k = mod1440_wr_cas0^wr_i }\n" + setv("mod1440_wr_cas^wr_i", "wr_k")
                + tmp("wr_s", 0) + block("var:wr_v", tmp("wr_s", "surrender_progress")) + "multiply_temp_variable = { wr_s = 100 }\n"
                + setv("mod1440_wr_surr^wr_i", "wr_s")
                + iff("check_variable = { mod1440_wr_capd^wr_i = 0 } var:wr_v = { has_capitulated = yes }",
                      setv("mod1440_wr_capd^wr_i", 1) + line("capitulated", b="wr_v"))))
            + iff("has_capitulated = yes NOT = { %s }" % is_one("mod1440_ev_capd"), setv("mod1440_ev_capd", 1) + line("we_capitulated"))
            + iff("has_capitulated = no", setv("mod1440_ev_capd", 0))))
        + "\n# Wars: what the page needs when it is on show. With nothing chosen yet, the file opens on the first war\n"
        "# there is.\n"
        + block("mod1440_wr_show", (
            iff("check_variable = { mod1440_wr_sel_kind < 1 }", (
                iff("check_variable = { mod1440_wr_enemy^num > 0 }", setv("mod1440_wr_sel_kind", 1) + setv("mod1440_wr_sel_i", 0))
                + iff("check_variable = { mod1440_wo_enemy^num > 0 }", setv("mod1440_wr_sel_kind", 2) + setv("mod1440_wr_sel_i", 0), "else_if")))
            + "mod1440_wr_card = yes\n"))
        + "\n# Wars: copies the chosen war to the variables its file reads, looks up the two portraits and gathers the\n"
        "# lines the War Diary has about this enemy, newest first.\n"
        + block("mod1440_wr_card", (
            "mod1440_wr_grow = yes\nmod1440_ev_grow = yes\n" + setv("mod1440_wr_c_has", 0)
            # with no war chosen the hidden flag and names still ask for a country: the own one
            + iff("check_variable = { mod1440_wr_c_enemy = 0 }", setv("mod1440_wr_c_enemy", "THIS"))
            + iff("check_variable = { mod1440_wr_sel_kind = 1 } check_variable = { mod1440_wr_sel_i < mod1440_wr_enemy^num }", (
                setv("mod1440_wr_c_has", 1) + copy("wr", ("enemy", "since", "old", "days", "cas", "taken", "lost", "vpt", "vpl", "surr", "capd"))))
            + iff("check_variable = { mod1440_wr_sel_kind = 2 } check_variable = { mod1440_wr_sel_i < mod1440_wo_enemy^num }", (
                setv("mod1440_wr_c_has", 1) + copy("wo", ("enemy", "since", "old", "days", "cas", "taken", "lost", "vpt", "vpl", "until", "outcome"))
                + setv("mod1440_wr_c_surr", 0) + setv("mod1440_wr_c_capd", 0)), "else_if")
            + iff(is_one("mod1440_wr_c_has"), (
                setv("mod1440_wr_c_ours", "surrender_progress") + "multiply_variable = { mod1440_wr_c_ours = 100 }\n"
                + setv("mod1440_wr_c_exists", 0) + iff("var:mod1440_wr_c_enemy = { exists = yes }", setv("mod1440_wr_c_exists", 1))
                + leader_portrait("mod1440_wr_c_enemy", "mod1440_wr_c_p", portrait_version)
                + "".join("clear_array = mod1440_wr_ln_%s\n" % part for part in ("date", "kind", "a", "sa"))
                + merged(of_this_war, war_line)
                + setv("mod1440_wr_ln_n", "mod1440_wr_ln_date^num")
                + pad([("mod1440_wr_ln_date", 0), ("mod1440_wr_ln_kind", BLANK), ("mod1440_wr_ln_a", 0), ("mod1440_wr_ln_sa", 0)], WR_LINES))))))
    return gui, script, script_effects


# ---------------------------------------------------------------- victory points

# Script learns of a state that changes hands from a hook, of a single province from nothing: so the mod looks,
# once a day while the country is at war, at who holds each victory point (the global array
# province_controllers) and compares with its copy of the day before. A point that passed between the country
# and an enemy becomes a line of the territory log, with the general who had the most divisions in its state.

def victory_points():
    """Returns the text of common/scripted_effects/mod1440_victory_points.txt and the version of the game's table.

    A mod can bring states of its own: Road to 56 has 1143 for the game's 1081 and other numbers for many, so a
    point of the game's table is in another state there, or no point at all. tools/victory_points_mods_table.py
    holds the points of such a map, and script picks the table by the number of states the loaded game has."""
    from victory_points_table import VICTORY_POINTS
    try:
        from victory_points_mods_table import MAPS
    except ImportError:
        MAPS = []
    tables = [("the game's history/states", 0, VICTORY_POINTS)] + [("the states of " + name, states, rows) for name, states, rows in MAPS]
    versions = [table_version(rows) for _name, _states, rows in tables]
    assert len(set(versions)) == len(versions), "two tables of victory points with the same version"
    version = versions[0]
    parts = ""
    for m, (source, states, rows) in enumerate(tables):
        scan, sync = "", ""
        for n, (province, state, value) in enumerate(rows):
            name = token("vp_%d" % province, "$VICTORY_POINTS_%d$" % province)
            now = "global.province_controllers^%d" % province
            scan += tmp("vp_now", now) + iff("NOT = { check_variable = { mod1440_vp_ctl^%d = vp_now } }" % n, (
                tmp("vp_old", "mod1440_vp_ctl^%d" % n) + setv("mod1440_vp_ctl^%d" % n, "vp_now") + tmp("vp_k", name) + tmp("vp_v", value)
                + block(str(state), tmp("vp_s", "THIS")) + "mod1440_vp_changed = yes\n"))
            sync += "add_to_array = { mod1440_vp_ctl = %s }\n" % now
        parts += ("\n# The %d points of %s: the copy, and the daily comparison.\n" % (len(rows), source)
                  + block("mod1440_vp_sync_%d" % m, "clear_array = mod1440_vp_ctl\n" + sync + setv("mod1440_vp_ver", versions[m]))
                  + block("mod1440_vp_scan_%d" % m, iff("NOT = { check_variable = { mod1440_vp_ver = %d } }" % versions[m],
                                                        "mod1440_vp_sync_%d = yes\n" % m) + els(scan)))

    def pick(effect):
        """The effect of the map that is loaded: of the game's own unless the number of states is another map's."""
        out = "mod1440_vp_map = yes\n"
        for m in range(1, len(tables)):
            out += iff("check_variable = { vp_map = %d }" % m, "%s_%d = yes\n" % (effect, m), "if" if m == 1 else "else_if")
        return out + (els("%s_0 = yes\n" % effect) if len(tables) > 1 else "%s_0 = yes\n" % effect)

    which = tmp("vp_map", 0)
    if len(tables) > 1:
        which += tmp("vp_states", 0) + block("every_state", "add_to_temp_variable = { vp_states = 1 }\n")
        which += "".join(iff("check_variable = { vp_states = %d }" % states, tmp("vp_map", m))
                         for m, (_source, states, _rows) in enumerate(tables) if m)
    enemy = "OR = { is_in_array = { array = enemies value = %s } is_in_array = { array = mod1440_ev_enemies value = %s } }"
    # a point that changes hands because its country gave up or is gone was not fought for: no line
    fought = "var:%s = { exists = yes has_capitulated = no }"

    def changed(kind, other, flag_value, counter):
        return (tmp("tr_s", "vp_s") + "mod1440_of_best = yes\n"
                + iff("check_variable = { vp_v > %d }" % (VP_MAJOR - 1), line(kind, a="vp_k", b=other, point=True, c="of_who", sc="of_best", p="vp_s", both=True))
                + els(line(kind, a="vp_k", b=other, point=True, c="of_who", sc="of_best", p="vp_s", log="tr"))
                + tmp("wr_c", other) + tmp("wr_f", flag_value) + "mod1440_wr_count = yes\n"
                + iff("check_variable = { of_best > 0 }", block("var:of_who", "add_to_variable = { %s = 1 }\n" % counter)))

    out = ("# Generated by tools/build_managers.py from tools/victory_points_table.py (the game's history/states)\n"
           "# and tools/victory_points_mods_table.py (the states of a mod).\n\n"
           "# Victory points: which table is the loaded game's. vp_map: 0 the game's own, and the map of a mod when the\n"
           "# game has as many states as that map.\n"
           + block("mod1440_vp_map", which)
           + "\n# Victory points: the copy of who holds each point today, without a line: the first run, the first day of a\n"
           "# war, and after the list of points has changed (another build of the mod, another map).\n"
           + block("mod1440_vp_sync", pick("mod1440_vp_sync"))
           + "\n# Victory points: once a day for a player's country at war. Each point whose holder is another than\n"
           "# yesterday goes to mod1440_vp_changed with vp_old and vp_now (the holders), vp_k (its name), vp_v (its\n"
           "# value) and vp_s (its state).\n"
           + block("mod1440_vp_scan", pick("mod1440_vp_scan"))
           + parts
           + "\n# Victory points: one has changed hands. A line when the country in scope took it from an enemy or lost it to\n"
           "# one, the count of that war, and the count of the general on the spot.\n"
           + block("mod1440_vp_changed", (
               tmp("vp_me", "THIS")
               + iff("check_variable = { vp_now = vp_me } %s %s" % (enemy % ("vp_old", "vp_old"), fought % "vp_old"),
                     changed("vp_taken", "vp_old", 3, "mod1440_of_vps"))
               + iff("check_variable = { vp_old = vp_me } %s" % (enemy % ("vp_now", "vp_now")),
                     changed("vp_lost", "vp_now", 4, "mod1440_of_vpl"), "else_if"))))
    return out, version


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
    # the file of a war shows the portrait of the country's own head of government, which the Government page looks up
    lists = ["mod1440_wd_list = yes\n", "mod1440_of_list = yes\n", "mod1440_gv_daily = yes\n",
             "mod1440_gv_daily = yes\nmod1440_wr_daily = yes\nmod1440_wr_show = yes\n"]
    show = "mod1440_rec_odd = yes\n" + tabs + setv("mod1440_hn_frame", 1) + iff(is_one("mod1440_hn_auto"), setv("mod1440_hn_frame", 2))
    show += "".join(iff("check_variable = { mod1440_rec_page = %d }" % n, lists[n]) for n in range(len(PAGES)))

    # an icon asks for its sprite also before anybody is chosen: until then it is told the unknown leader
    faces = "".join(iff("check_variable = { %s = 0 }" % v, setv(v, "token:" + UNKNOWN)) for v in ("mod1440_of_c_p", "mod1440_wr_c_p", "mod1440_gv_p"))
    copy_members = "clear_array = mod1440_gv_fac\n" + block(
        "for_each_loop", "array = faction_members\nvalue = ev_c\nadd_to_array = { mod1440_gv_fac = ev_c }\n")
    in_faction = tmp("ev_in", 0) + iff("is_in_faction = yes", tmp("ev_in", 1))

    def credit(counter):
        return iff("check_variable = { of_best > 0 }", block("var:of_who", "add_to_variable = { %s = 1 }\n" % counter))

    honour = iff("check_variable = { tr_cap = 1 } %s %s" % (is_one("mod1440_hn_auto"), HONOUR_DLC), (
        tmp("hn_n", 0)
        + block("var:tr_s", block("every_state_division", "limit = { OWNER = { tag = ROOT } }\n" + block(
            "add_history_entry", 'key = mod1440_hn_capture\nsubject = "Capital"\nallow = no\n') + "add_to_temp_variable = { hn_n = 1 }\n"))
        + "add_to_variable = { mod1440_hn_count = hn_n }\n"))

    def changed(kind, capital):
        """The line for a state that changed hands: a capital into both logs, any other into the territory log."""
        return (iff("check_variable = { tr_cap = 1 }", line(capital, a="tr_s", b="tr_c", state=True, c="of_who", sc="of_best", both=True))
                + els(line(kind, a="tr_s", b="tr_c", state=True, c="of_who", sc="of_best", log="tr")))

    script_effects = (
        "# The Records: what the window shows. Sets the buttons' frames and makes the list of the open page.\n"
        + block("mod1440_rec_show", "mod1440_ev_grow = yes\n" + faces + show + "add_to_variable = { mod1440_rec_dirty = 1 }\n")
        + "\n# The Records: the first run for the country in scope. Takes the copies the daily comparison needs, opens a\n"
        "# row for each war that already runs and writes the first line.\n"
        # The card of a state names the country it was taken from. A state nobody took holds none, and the game
        # logs "invalid scope for var" each time such a state is selected, also while the line is hidden (Engine
        # Facts X73). So every state gets a country once, for all players: the line shows only where
        # mod1440_sr_day says the state was taken.
        + block("mod1440_ev_init", iff("NOT = { check_variable = { global.mod1440_sr_named = 1 } }", (
            block("every_state", iff("NOT = { has_variable = mod1440_sr_from }", setv("mod1440_sr_from", "PREV")))
            + setv("global.mod1440_sr_named", 1))) + iff("NOT = { %s }" % is_one("mod1440_ev_begun"), (
            setv("mod1440_ev_begun", 1) + setv("mod1440_hn_auto", 1)
            + setv("mod1440_ev_since", "global.date") + setv("mod1440_ev_since_day", "global.num_days") + "mod1440_rec_odd = yes\n"
            + line("begins")
            + block("for_each_loop", "array = enemies\nvalue = ev_c\nadd_to_array = { mod1440_ev_enemies = ev_c }\n" + open_war("ev_c", 1))
            + block("for_each_loop", "array = subjects\nvalue = ev_c\nadd_to_array = { mod1440_ev_subjects = ev_c }\n")
            + in_faction + setv("mod1440_ev_fac", "ev_in") + copy_members
            + "mod1440_gv_daily = yes\nmod1440_of_seen = yes\n")))
        + "\n# The Records: once a day for a player's country. The victory points first, while yesterday's enemies are\n"
        "# still known. Then what no hook tells, found by comparing with yesterday: the end of a war, a new or lost\n"
        "# subject, the faction, the offices. Then the numbers of the wars.\n"
        + block("mod1440_rec_daily", (
            "mod1440_ev_init = yes\nmod1440_ev_grow = yes\n"
            # at peace nothing is looked at; the copy is taken again on the first day of the next war
            + iff("has_war = yes", "mod1440_vp_scan = yes\n") + els(setv("mod1440_vp_ver", 0))
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
        + "\n# The Records: the general of the country in scope with the most divisions in the state tr_s: of_who, and\n"
        "# of_best how many divisions that is (0: nobody stands there).\n"
        + block("mod1440_of_best", tmp("of_best", 0) + tmp("of_who", 0) + block("every_army_leader", (
            tmp("of_n", "num_units_in_state@var:tr_s")
            + iff("check_variable = { of_n > of_best }", "mod1440_of_me = yes\n" + iff(
                "NOT = { check_variable = { of_me = 0 } }", tmp("of_best", "of_n") + tmp("of_who", "of_me"))))))
        + "\n# The Records: the country in scope has taken the state tr_s from tr_c (tr_cap = 1: a capital). A line with\n"
        "# the general on the spot, the count of the war and his own, what the state card shows, and the honour.\n"
        + block("mod1440_tr_taken", (
            "mod1440_of_best = yes\n" + changed("state_taken", "capital_taken")
            + tmp("wr_c", "tr_c") + tmp("wr_f", 1) + "mod1440_wr_count = yes\n" + credit("mod1440_of_states")
            + block("var:tr_s", setv("mod1440_sr_date", "global.date") + setv("mod1440_sr_day", "global.num_days")
                    + setv("mod1440_sr_from", "tr_c"))
            + honour))
        + block("mod1440_tr_lost", (
            "mod1440_of_best = yes\n" + changed("state_lost", "capital_lost")
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
    (r"mod1440_wd_kind|mod1440_of_ln_kind|mod1440_wr_ln_kind", "Our pride of the fleet was sunk by"), (r"outcome", "No longer exists"),
    (r"mod1440_gv_law", "Partial Mobilization"), (r"dec_key|md_key", "Knight's Cross (Swords & Diamonds)"),
    (r"GetRulingParty$", "NSDAP"), (r"Get\w+Party(Long)?$", "Nationalsozialistische Deutsche Arbeiterpartei"),
    (r"GetRulingIdeology", "fascist"), (r"GetFactionName", "Co-Prosperity Sphere"), (r"GetAgency", "Intelligence Agency"),
    (r"Capital\.GetName|mod1440_wd_a|mod1440_of_ln_a|mod1440_wr_ln_a", "Niederschlesien"), (r"^ROOT\.GetName$|mod1440_wr_c_enemy\.GetName", "Czechoslovakia"),
    (r"GetLeader$", "Konstantin von Neurath"), (r"Leader$|GetName", "Konstantin von Neurath"),
    (r"^\?casualties|mod1440_wr_cas|mod1440_wo_cas|mod1440_wr_c_cas", "1250000"), (r"party_popularity", "100%"), (r"_war_support", "12.5%"),
    (r"surrender_progress", "100%"), (r"days_until_next_election|mod1440_wr_days|mod1440_wd_days|mod1440_wr_c_days", "1460"), (r"\?v\b", "100"),
    (r"\^num|mod1440_wd_total", "500"), (r"_level|skill|num_traits|mod1440_of_c_skill", "9"), (r"num_units|num_ships|mod1440_of_c_cmd", "240"),
    (r"mod1440_wr_c_surr", "100"), (r"mod1440_", "128"), (r"", "128"),
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

    def subjects(prefix, count):
        return ["%s_%d_p" % (prefix, k) for k in range(count)]

    officer_hide = (["of_arrow_up", "of_arrow_down", "of_c_none", "of_c_rank_2", "of_c_rank_3", "of_c_service_off", "of_c_cmd_navy",
                     "of_c_since_old", "of_c_prom_old", "of_c_lvl_old", "of_c_dec_none", "of_ln_none"]
                    + ["of_c_rack_%d_%s" % (k, s) for k in range(CARD_LINES) for s in others]
                    + ["of_md_%d_%s" % (k, s) for k in range(MEDAL_SLOTS) for s in others]
                    + ["of_md_%d_held" % k for k in range(1, MEDAL_SLOTS)] + subjects("of_ln", CARD_LINES))
    office_hide = ["gv_of_%d_none" % k for k in range(len(OFFICES))] + ["gv_of_%d_since_old" % k for k in range(len(OFFICES))]
    return {
        "war_diary": {
            "phase": "E1", "file": "mod1440_records.gui", "screenshot": shot,
            "windows": [dict(place, name="mod1440_records_wd", rows={"wd_grid": 24}, listRows={"wd_grid": "mod1440_records_diary_row"},
                             hide=["wd_none"], _note="A window of its own over the map, opened from the Records button of the top bar."),
                        {"name": "mod1440_records_diary_row", "skip": True,
                         "hide": ["wd_row_icon_%d" % f for f in (1, 3, 4, 5)] + ["wd_row_b_near", "wd_row_point"],
                         "_note": "Drawn as a line of the territory log: a state, the country it was taken from, the officer."}],
            "setup": [{"key": "shift+j", "wait": 1.5}, {"clickWidget": "mod1440_records_wd/wd_tab_0", "wait": 1.0}],
            "teardown": back,
            "expect": ["mod1440_records_wd/wd_close", "mod1440_records_wd/wd_older"],
            "crop": crop,
            "manual": ["Lines that need a war: a state and a victory point taken with the general on the spot, capitulation, landings, aces"],
            "checklist": ["A line about a state or a victory point: its button moves the camera there", "The filters; Older and Newer past 200 lines",
                          "All shows the lines of both logs by date, a capital once"],
        },
        "officers": {
            "phase": "E2", "file": "mod1440_records.gui", "screenshot": shot,
            "windows": [dict(place, name="mod1440_records_of", rows={"of_grid": 18}, listRows={"of_grid": "mod1440_records_officer_row"},
                             hide=officer_hide, _note="The file shows a German field marshal; script hides the twins of his rank, command and service and the medal strips of other countries. A portrait is the game's unknown leader until script names the officer's sprite."),
                        {"name": "mod1440_records_officer_row", "skip": True,
                         "hide": ["of_row_pick", "of_row_gen", "of_row_adm", "of_cell_c3_navy", "of_cell_c4_navy", "of_cell_cmd_navy"]}],
            "setup": tab(1),
            "teardown": [{"clickWidget": "mod1440_records_of/of_tab_0", "wait": 0.8}] + back,
            "expect": ["mod1440_records_of/of_close", "mod1440_records_of/of_sort_skill"],
            "crop": crop,
            "manual": ["Battles won and lost, states and victory points taken: they need fighting", "A general the game made up: he shows the unknown leader"],
            "checklist": ["Each row shows its officer's portrait", "A click on an officer opens his file with his portrait and marks his row",
                          "Award and Take back last", "Sorting by each column"],
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
            "checklist": ["The flag and the portrait of the head of government", "Hire an advisor: the next day the Cabinet lists the name with the date"],
        },
        "wars": {
            "phase": "E4", "file": "mod1440_records.gui", "screenshot": shot,
            "windows": [dict(place, name="mod1440_records_wr", rows={"wr_now_grid": 3, "wr_old_grid": 6},
                             listRows={"wr_now_grid": "mod1440_records_war_row", "wr_old_grid": "mod1440_records_past_war_row"},
                             hide=["wr_now_none", "wr_old_none", "wr_c_none", "wr_c_gone", "wr_c_since_old", "wr_c_capd", "wr_ln_none"] + subjects("wr_ln", WR_LINES),
                             _note="The file shows a finished war: script hides what only a war of today has."),
                        {"name": "mod1440_records_war_row", "skip": True, "hide": ["wr_row_since_old", "wr_row_pick"]},
                        {"name": "mod1440_records_past_war_row", "skip": True, "hide": ["wo_row_since_old", "wo_row_pick"]}],
            "setup": tab(3),
            "teardown": [{"clickWidget": "mod1440_records_wr/wr_tab_0", "wait": 0.8}] + back,
            "expect": ["mod1440_records_wr/wr_close"],
            "crop": crop,
            "manual": ["A war that ends; casualties above zero; an enemy that is annexed (the file says the country is no more)"],
            "checklist": ["Declare a war: a row appears with today's date, and its file opens by itself",
                          "A click on a war opens its file: the two flags, the two heads of government, the figures, the lines",
                          "After a peace the row moves to the finished wars and the file stays on that war"],
        },
    }


SCENES = {}


def build(managers):
    """Returns the files' pieces: (gui, scripted GUIs, scripted effects, hooks by name, further files by path)."""
    global M, B
    M, B = managers, managers.B
    portrait_script, portrait_version = portraits()
    point_script, point_version = victory_points()
    out_gui, out_script, out_effects = "", "", recording()
    hooks = {}
    for part in (war_diary(), officers(portrait_version), government(portrait_version), wars(portrait_version), frame()):
        out_gui += part[0]
        out_script += ("\n" if out_script else "") + part[1]
        out_effects += "\n" + part[2]
        if len(part) > 3:
            for name, body in part[3].items():
                hooks[name] = hooks.get(name, "") + body
    SCENES.clear()
    SCENES.update(scenes())
    return out_gui, out_script, out_effects, hooks, {
        "common/scripted_effects/mod1440_portraits.txt": portrait_script,
        "common/scripted_effects/mod1440_victory_points.txt": point_script,
    }
