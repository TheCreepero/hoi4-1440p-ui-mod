"""Build larger backgrounds from vanilla textures by copying pixels only.

Every output is assembled from columns and rows of one vanilla texture: kept, repeated, or copied in
mirrored order. No pixel is drawn or blended, so the result keeps the vanilla look. Re-run after a
game update that changes a source texture.

    python tools/stretch_background.py [--game-dir DIR] [--preview DIR] [--only NAME]

Needs Pillow. Outputs go to gfx/interface/1440p_ui/ as uncompressed 32-bit DDS, the format the
vanilla files use.
"""

import argparse
import os
import re
import sys

from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(REPO_ROOT, "gfx", "interface", "1440p_ui")


def widen_periodic(frame, width, period, split, top, bottom, right_cap):
    """Widen a frame whose inner pattern repeats every `period` columns.

    Columns left of `split` are kept. From `split` on, the last full period before `split` is
    repeated, which continues the pattern without a seam. The edge rows (above `top`, from `bottom`
    down) of the vanilla right part and the last `right_cap` columns are then copied back, so the
    right edge bar, border and rivets end up where they belong.
    """
    w, h = frame.size
    out = Image.new("RGBA", (width, h))
    out.paste(frame.crop((0, 0, split, h)), (0, 0))

    tile = frame.crop((split - period, 0, split, h))
    for x in range(split, width, period):
        out.paste(tile, (x, 0))

    right_x = split + (width - w)
    out.paste(frame.crop((split, 0, w, top)), (right_x, 0))
    out.paste(frame.crop((split, bottom, w, h)), (right_x, bottom))
    out.paste(frame.crop((w - right_cap, 0, w, h)), (width - right_cap, 0))
    return out


def widen_spread(frame, width, left_cap, right_cap):
    """Widen a frame whose middle is a smooth gradient without a pattern.

    The first `left_cap` and last `right_cap` columns are kept. The columns between them are spread
    evenly over the new width, each one shown one or more times, which keeps the gradient smooth.
    """
    w, h = frame.size
    out = Image.new("RGBA", (width, h))
    out.paste(frame.crop((0, 0, left_cap, h)), (0, 0))
    out.paste(frame.crop((w - right_cap, 0, w, h)), (width - right_cap, 0))

    source_span = w - left_cap - right_cap
    target_span = width - left_cap - right_cap
    for i in range(target_span):
        x = left_cap + i * source_span // target_span
        out.paste(frame.crop((x, 0, x + 1, h)), (left_cap + i, 0))
    return out


def widen_mirror(frame, width, split):
    """Widen a frame whose middle is an irregular texture without a pattern or gradient.

    The new columns go in at `split`: the columns left of it mirrored, then the same columns again
    the right way round. Every join is between a column and its own copy, so no seam shows. The
    added width must be even, and the columns it is taken from must be plain.
    """
    w, h = frame.size
    half, odd = divmod(width - w, 2)
    if odd or half > split:
        raise ValueError("widen_mirror needs an even added width of at most twice the split column")
    out = Image.new("RGBA", (width, h))
    out.paste(frame.crop((0, 0, split, h)), (0, 0))
    section = frame.crop((split - half, 0, split, h))
    out.paste(section.transpose(Image.FLIP_LEFT_RIGHT), (split, 0))
    out.paste(section, (split + half, 0))
    out.paste(frame.crop((split, 0, w, h)), (split + 2 * half, 0))
    return out


def widen_mirror_multi(frame, inserts):
    """Apply widen_mirror at several columns, to widen each painted area of a frame by its own amount.

    `inserts` lists (split column, added width) in the columns of the vanilla frame. They are
    applied from right to left, so an insert does not move the columns of the ones still to come.
    """
    for split, added in sorted(inserts, reverse=True):
        frame = widen_mirror(frame, frame.width + added, split)
    return frame


def grow(image, axis, inserts):
    """Insert columns (axis "x") or rows (axis "y") into an image without drawing a pixel.

    `inserts` lists (split, added) or (split, added, period), in the lines of the image as passed in.
    They are applied from the far end back, so an insert does not move the lines of the ones still
    to come.

    Without a period, the added/2 lines before `split` go in mirrored and then once more the right
    way round, so every join is between a line and its own copy. This suits plain and irregular
    areas. With a period, the `added` lines before `split` go in once more as they are, which
    continues a pattern of that period without a seam; `added` must be a multiple of the period.
    """
    horizontal = axis == "x"
    for split, added, *rest in sorted(inserts, reverse=True):
        period = rest[0] if rest else None
        w, h = image.size
        if period:
            if added % period or added > split:
                raise ValueError(f"insert at {split}: {added} is not a multiple of the period {period}, or too long")
            pieces = [image.crop((split - added, 0, split, h) if horizontal else (0, split - added, w, split))]
        else:
            half, odd = divmod(added, 2)
            if odd or half > split:
                raise ValueError(f"insert at {split}: a mirrored insert needs an even length of at most twice the split")
            block = image.crop((split - half, 0, split, h) if horizontal else (0, split - half, w, split))
            pieces = [block.transpose(Image.FLIP_LEFT_RIGHT if horizontal else Image.FLIP_TOP_BOTTOM), block]
        if horizontal:
            out = Image.new("RGBA", (w + added, h))
            out.paste(image.crop((0, 0, split, h)), (0, 0))
            x = split
            for piece in pieces:
                out.paste(piece, (x, 0))
                x += piece.width
            out.paste(image.crop((split, 0, w, h)), (x, 0))
        else:
            out = Image.new("RGBA", (w, h + added))
            out.paste(image.crop((0, 0, w, split)), (0, 0))
            y = split
            for piece in pieces:
                out.paste(piece, (0, y))
                y += piece.height
            out.paste(image.crop((0, split, w, h)), (0, y))
        image = out
    return image


def grow_bands(image, axis, bands):
    """Grow each band of an image with its own inserts and put the bands back together.

    For axis "x" a band is a range of rows, (first row, end row, inserts), and its inserts add
    columns; for axis "y" it is a range of columns whose inserts add rows. The bands must cover the
    image and all grow by the same amount. This is how a bitmap with several painted areas grows
    area by area: each band gets its inserts where that band is plain.
    """
    horizontal = axis == "x"
    w, h = image.size
    parts, at = [], 0
    for start, end, inserts in bands:
        if start != at:
            raise ValueError(f"bands leave a gap or overlap at {at}")
        band = image.crop((0, start, w, end) if horizontal else (start, 0, end, h))
        parts.append(grow(band, axis, inserts))
        at = end
    if at != (h if horizontal else w):
        raise ValueError(f"bands end at {at}, the image at {h if horizontal else w}")
    sizes = {part.width if horizontal else part.height for part in parts}
    if len(sizes) != 1:
        raise ValueError(f"bands grow to different sizes: {sorted(sizes)}")
    return join(parts, "y" if horizontal else "x")


def join(parts, axis):
    """Put images side by side (axis "x") or one above the other (axis "y")."""
    horizontal = axis == "x"
    width = sum(p.width for p in parts) if horizontal else max(p.width for p in parts)
    height = max(p.height for p in parts) if horizontal else sum(p.height for p in parts)
    out = Image.new("RGBA", (width, height))
    at = 0
    for part in parts:
        out.paste(part, (at, 0) if horizontal else (0, at))
        at += part.width if horizontal else part.height
    return out


def spread(first, last, count, length, period):
    """`count` inserts of `length` lines each, evenly spaced from `first` to `last`, for grow().

    Many short inserts keep a gradient smooth where one long insert would show as a step.
    """
    step = (last - first) / max(1, count - 1)
    return [(int(round(first + i * step)), length, period) for i in range(count)]


# Army and army group badge. Both are painted alike: the name field (columns 57-229 of the top band),
# the commander box (66-219), the stats box (221-297), a plain right area (297-429) and the tray
# along the bottom (64-428). The inserts widen the name field and commander box, the stats box and
# the right area.
BADGE_INSERTS = [(200, 100), (295, 48), (425, 100)]

# ---------------------------------------------------------------------------------------------
# Unit details windows (division, ship, air wing, railway gun). All four bitmaps are painted alike:
# a main part of 553 columns (title bar, header strip, a paper with three stat columns and a
# printed line every 20 rows, a lower panel) and a side part of 303 columns (a header bar above a
# panel hatched with a pattern of 3 pixels in both directions).
#
# The numbers below are shared with the widget positions in interface/zz_1440p_unit_details.gui:
# a stat column grows by STAT_COLUMN columns and a stat row by STAT_ROW rows.

STAT_COLUMN = 78          # 155 -> 233 px for a label and its value in the 22 px typewriter font
STAT_ROW = 8              # 20 -> 28 px per row
SIDE_GROWTH = 90          # side part: 30 periods of its hatch
MAIN_GROWTH = 3 * STAT_COLUMN

# The frame line above the paper (rows 66-77) has thicker stretches; these columns are plain in it.
PAPER_FRAME_COLUMNS = [(126, STAT_COLUMN), (350, STAT_COLUMN), (496, STAT_COLUMN)]


def paper_columns():
    """Column inserts for the paper: each stat column (16-182, 186-357, 361-529) takes STAT_COLUMN / 3
    inserts of 3 columns, spread over its width.

    The printed lines are dotted with a period of about 3 columns, so a copy of 3 columns leaves
    them even, and many short copies stretch the paper grain evenly where one mirrored insert would
    show every stain twice.
    """
    count = STAT_COLUMN // 3
    return spread(24, 176, count, 3, 3) + spread(196, 352, count, 3, 3) + spread(372, 526, count, 3, 3)


def paper_rows(first, bands, last_band_rows=8, per_band=STAT_ROW):
    """Row inserts for a paper with `bands` stat rows: every band between two printed lines takes
    STAT_ROW rows, each a copy of one of its own rows.

    `first` is the first row of the first band; a band starts every 20 rows and has 16 plain rows.
    The last band ends at the bottom edge of the paper and is shorter, so its copies are taken from
    its first rows.
    """
    rows = []
    # a band has 16 plain rows: up to 8 copies go after every second one; more copies cycle through
    # rows 1 to 15, so several copies of one row follow each other (a plain row repeated is still plain)
    offset = (lambda i: 1 + 2 * i) if per_band <= 8 else (lambda i: 1 + i % 15)
    for band in range(bands - 1):
        rows += [(first + 20 * band + offset(i), 1, 1) for i in range(per_band)]
    rows += [(first + 20 * (bands - 1) + 1 + i, 1, 1) for i in range(last_band_rows)]
    return rows


def stretched(first, last, added):
    """`added` single-column (or single-row) copies spread from `first` to `last`: an even stretch
    for an irregular texture without a pattern, such as scratched metal."""
    return spread(first, last, added, 1, 1)


def side_panel(side, height_growth, header_split=75):
    """The side part of a details bitmap, SIDE_GROWTH columns wider and `height_growth` rows taller.

    The header bar and the bottom edge take one mirrored insert. The hatched panel between them
    (rows 32 to its end) takes many inserts of one period each, which keeps its hatch and its
    gradient unbroken.
    """
    h = side.height
    body_end = h - 11
    side = grow_bands(side, "x", [
        (0, 32, [(header_split, SIDE_GROWTH)]),
        (32, body_end, spread(20, 270, SIDE_GROWTH // 3, 3, 3)),
        (body_end, h, [(150, SIDE_GROWTH)]),
    ])
    if height_growth % 3:
        raise ValueError("the side panel grows in periods of 3 rows")
    return grow(side, "y", spread(60, body_end - 20, height_growth // 3, 3, 3))


def division_details(source):
    """Division details, 856x497 to 1180x587.

    Main part, by band of rows:
      0-32     title bar, plain: one mirrored insert
      33-65    header strip: the name field (columns 110-378) takes all the growth
      66-77    frame line above the paper
      78-321   paper: three stat columns, 11 stat rows
      322-487  softness strip and adjuster panel: stretched left of the notch (columns 178-197) and
               between the two icon boxes (238-279 and 489-530)
      488-496  bottom edge
    """
    h = source.height
    main = grow_bands(source.crop((0, 0, 553, h)), "x", [
        (0, 33, [(400, MAIN_GROWTH)]),
        (33, 66, [(370, MAIN_GROWTH)]),
        (66, 78, PAPER_FRAME_COLUMNS),
        (78, 322, paper_columns()),
        (322, 488, stretched(20, 170, STAT_COLUMN) + stretched(284, 484, 2 * STAT_COLUMN)),
        (488, h, [(500, MAIN_GROWTH)]),
    ])
    rows = paper_rows(105, 11) + stretched(380, 470, 2)
    main = grow(main, "y", rows)
    side = side_panel(source.crop((553, 0, 856, h)), sum(row[1] for row in rows))
    return join([main, side], "x")


# A3 redo: the paper of the ship, air wing and railway gun bitmaps is taller, so that two rows of stat
# cards (194 and 142 px) fit on it: 7 bands of 24 rows and a last band of 7, 175 rows in all (it was 64).
SMALL_PER_BAND = 24
SMALL_LAST_BAND = 7
SMALL_PAPER_GROWTH = 7 * SMALL_PER_BAND + SMALL_LAST_BAND


def small_details(frame_band, bottom_inserts):
    """A compose function for the ship and air wing details bitmaps, 856x409 to 1180x475.

    They are painted like the division bitmap, with 8 stat rows and one lower panel:
      0-32     title bar                     33-65    header strip (name field, columns 110-378)
      66-77    frame line above the paper    78-257   paper, printed lines every 20 rows from 119
      258-...  frame line below the paper (`frame_band`: its end row and its column inserts)
      ...      lower panel, plain between columns 12 and 532
      last 10  bottom edge (`bottom_inserts`)
    """
    frame_end, frame_inserts = frame_band

    def compose(source):
        h = source.height
        main = grow_bands(source.crop((0, 0, 553, h)), "x", [
            (0, 33, [(400, MAIN_GROWTH)]),
            (33, 66, [(370, MAIN_GROWTH)]),
            (66, 78, PAPER_FRAME_COLUMNS),
            (78, 258, paper_columns()),
            (258, frame_end, frame_inserts),
            (frame_end, h - 10, stretched(20, 520, MAIN_GROWTH)),
            (h - 10, h, bottom_inserts),
        ])
        rows = paper_rows(104, 8, last_band_rows=SMALL_LAST_BAND, per_band=SMALL_PER_BAND) + stretched(300, 380, 2)
        main = grow(main, "y", rows)
        side = side_panel(source.crop((553, 0, 856, h)), sum(row[1] for row in rows))
        return join([main, side], "x")

    return compose


# Template tab of the division window: a board with a tree of five regiment columns (vertical lines
# at columns 18, 103, 188, 273 and 358, hanging from a line in row 83), a support box (columns
# 447-518, rows 91-294) and a regimental support box (columns 25-437, rows 332-400).
TEMPLATE_COLUMN = 46      # 85 -> 131 px per regiment column; 5 columns and 4 px in the support box
TEMPLATE_ROW = 16         # 46 -> 62 px per regiment row


def template_board(source):
    """The template board, 548x423 to 782x513: it fills the main part of the enlarged window.

    Columns: each regiment column is stretched between its line and the next; the ornament above
    the tree (rows 28-82, columns 115-385) moves as a whole so its stem still meets the middle of
    the tree. Rows: the five regiment rows are stretched, the support box along with them.
    """
    w, h = source.size
    columns = []
    for first, last in ((30, 100), (106, 186), (191, 271), (277, 354), (362, 434)):
        columns += stretched(first, last, TEMPLATE_COLUMN)
    columns += stretched(455, 510, MAIN_GROWTH - 5 * TEMPLATE_COLUMN)
    left = 5 * TEMPLATE_COLUMN // 2 + 1          # keeps the stem above the middle of the tree line
    board = grow_bands(source, "x", [
        (0, 28, [(300, MAIN_GROWTH)]),
        (28, 83, [(105, left), (500, MAIN_GROWTH - left)]),
        (83, 402, columns),
        (402, h, [(300, MAIN_GROWTH)]),
    ])
    rows = 5 * TEMPLATE_ROW
    rest = 90 - rows
    support = 447 + 5 * TEMPLATE_COLUMN - 1      # first column of the support box after the growth
    return grow_bands(board, "y", [
        (0, support, stretched(90, 326, rows) + stretched(360, 395, rest)),
        (support, board.width, stretched(95, 290, rows) + stretched(300, 410, rest)),
    ])


def hq_board(source):
    """The picture behind an HQ template, 521x388 to 755x478. The painting (columns 0-313) keeps
    its size; the dark panel beside it grows, and the plain strip below the painting is repeated."""
    board = grow(source, "x", [(515, MAIN_GROWTH)])
    return grow(board, "y", [(386, 84)] + stretched(348, 384, 6))


def stat_tile(source, width=122, height=52, cap=6, top=16, bottom=4, plain_columns=(20, 160), plain_rows=(18, 26)):
    """A tile for one stat: the plain part of the vanilla header bar (dark metal, lighter top edge),
    with its left end copied to both ends (the right end of the bar is slanted and lighter) and its
    top and bottom rows kept. The plain middle is spread over the new width and height."""
    src_w, src_h = source.size
    out = Image.new("RGBA", (width, height))
    px, spx = out.load(), source.load()
    first, last = plain_columns
    first_row, last_row = plain_rows
    for y in range(height):
        if y < top:
            sy = y
        elif y >= height - bottom:
            sy = src_h - (height - y)
        else:
            sy = first_row + (y - top) % (last_row - first_row + 1)
        for x in range(width):
            if x < cap:
                sx = x
            elif x >= width - cap:
                sx = width - 1 - x
            else:
                sx = first + (x - cap) % (last - first + 1)
            px[x, y] = spx[sx, sy]
    return out


# ---------------------------------------------------------------------------------------------
# A4: fleet panel. Every bitmap of the panel is 493 columns wide in vanilla (the panel is 492) and
# grows by FLEET_GROWTH columns. The fleet card and the task force card are painted alike: a blue
# title bar with a black name plate (columns 44-302), boxes on scratched metal, a tray.
FLEET_GROWTH = 248        # 492 -> 740 px: one line per ship with the class name whole
FLEET_PLATE = 148         # of which the name plate takes this much
SHIP_ROW_CUT = [(14, 3), (26, 3)]   # a ship row loses 6 rows: 41 -> 35 px per row


def cut(image, axis, spans):
    """Remove columns (axis "x") or rows (axis "y"): `spans` lists (first, count) in the lines of the
    image as passed in. Short spans spread over a gradient leave no visible step."""
    horizontal = axis == "x"
    w, h = image.size
    keep, at = [], 0
    for first, count in sorted(spans):
        keep.append(image.crop((at, 0, first, h) if horizontal else (0, at, w, first)))
        at = first + count
    keep.append(image.crop((at, 0, w, h) if horizontal else (0, at, w, h)))
    return join(keep, axis)


def fleet_card(source):
    """Fleet card, 493x166 to 741x166. Bands of rows:
      0-39     title bar: the name plate grows, the count badge (columns 322-405, its rim down to
               row 37) moves with it
      40-92    commander: the name box (columns 78-224) and the stats box (224-297) grow by 60 each
      93-128   composition tray (columns 78-405)
      129-165  metal and the blue footer
    """
    rest = FLEET_GROWTH - FLEET_PLATE
    return grow_bands(source, "x", [
        (0, 40, stretched(70, 280, FLEET_PLATE) + stretched(412, 480, rest)),
        (40, 93, stretched(90, 215, 60) + stretched(232, 290, 60) + stretched(310, 460, FLEET_GROWTH - 120)),
        (93, 129, stretched(90, 395, FLEET_GROWTH)),
        (129, source.height, stretched(20, 460, FLEET_GROWTH)),
    ])


TASK_FORCE_TRAY = (79, 39)   # rows of the composition tray, which the wide card does without


def task_force_card(source):
    """Task force card, 493x125 to 741x86. Bands of rows:
      0-31     title bar, as on the fleet card
      32-78    the mission box (columns 8-380) takes the growth but 30 columns, which go to the
               box for the order buttons (387-482)
      79-117   composition tray (columns 8-482): cut, the counters sit in the mission box
      118-124  bottom edge
    """
    rest = FLEET_GROWTH - FLEET_PLATE
    wide = grow_bands(source, "x", [
        (0, 32, stretched(70, 280, FLEET_PLATE) + stretched(310, 480, rest)),
        (32, 79, stretched(20, 370, FLEET_GROWTH - 30) + stretched(395, 475, 30)),
        (79, source.height, stretched(20, 470, FLEET_GROWTH)),
    ])
    return cut(wide, "y", [TASK_FORCE_TRAY])


POPUP_GROWTH = 80         # composition editor and home base picker: 524 -> 604 and 375 -> 455
TRANSFER_GROWTH = 160     # "Select Ships to Transfer": 535 -> 695, a ship on one line


def ship_row(right_cap, growth=FLEET_GROWTH):
    """One frame of the ship row, 493x47 to 741x41 (or by another growth): a fine mesh that repeats
    every 29 columns, edge bars in rows 0-5 and 40-46, and (selected frame) a chevron in the last columns."""
    def widen(frame):
        wide = widen_periodic(frame, frame.width + growth, period=29, split=330, top=6, bottom=40, right_cap=right_cap)
        return cut(wide, "y", SHIP_ROW_CUT)
    return widen


# ---------------------------------------------------------------------------------------------
# A5, Recruit & Deploy and Division Templates. The numbers are shared with the widget positions in
# interface/zz_1440p_recruit_deploy.gui.

DEPLOY_GROWTH = 90        # left panel, 550 -> 640: the name of a division in training gets it
TEMPLATE_GROWTH = 240     # a template row, 341 -> 581: name, cap, Train, Edit and toggles on one line
TEMPLATE_PANEL_GROWTH = 243   # the template panel, 375 -> 618
TEMPLATE_SPLIT = 85       # first column right of the icon box's frame line


def conveyor_card(source):
    """Card of a template in training, 490x84 to 580x84. Bands of rows:
      0-7      the top lip: plain lines
      8-41     the name field (columns 92-312, a fine mesh without a clear period): one piece of 90
               columns goes in once more as it is; the amount pill (320-410) moves right
      42-83    scratched metal
    """
    return grow_bands(source, "x", [
        (0, 8, stretched(110, 300, DEPLOY_GROWTH)),
        (8, 42, [(300, DEPLOY_GROWTH, 30)]),
        (42, source.height, stretched(110, 470, DEPLOY_GROWTH)),
    ])


def template_row(mesh_rows, strip_rows, mesh_period):
    """Row of a template, 346x78 to 586x54 (the brown twin of a decommissioned template: 348x79 to
    588x55). The vanilla row is an icon box (columns 0-84) beside a meshed name box with a metal
    strip for the buttons under it. The one-line row does without the strip:
      icon box   loses 24 rows of its plain inside, in six spans between its corner rivets
      name box   loses 12 rows of mesh and 12 of the 13 rows of the strip, then grows by
                 TEMPLATE_GROWTH columns: plain lines above and below, two pieces of the mesh
    """
    def compose(source):
        w, h = source.size
        box = cut(source.crop((0, 0, TEMPLATE_SPLIT, h)), "y", [(18, 4), (25, 4), (32, 4), (39, 4), (46, 4), (52, 4)])
        first_mesh, strip = mesh_rows[0], strip_rows[0]
        name = cut(source.crop((TEMPLATE_SPLIT, 0, w, h)), "y", [(first_mesh + 4, 4), (first_mesh + 14, 4), (first_mesh + 24, 4), (strip, 12)])
        mesh_end = mesh_rows[1] - 12
        half = TEMPLATE_GROWTH // 2   # the mesh runs from column 7 to 251 of the name part: two pieces fit
        if TEMPLATE_GROWTH % 2 or half % mesh_period or half > 120:
            raise ValueError("the template row cannot grow by %d columns" % TEMPLATE_GROWTH)
        name = grow_bands(name, "x", [
            (0, first_mesh, stretched(20, 240, TEMPLATE_GROWTH)),
            (first_mesh, mesh_end, [(130, half, mesh_period), (244, half, mesh_period)]),
            (mesh_end, name.height, stretched(20, 240, TEMPLATE_GROWTH)),
        ])
        return join([box, name], "x")
    return compose


# ---------------------------------------------------------------------------------------------
# A6, the army overview tab (divisions, fleets, air wings). The numbers are shared with the widget
# positions in interface/zz_1440p_army_overview.gui.

OVERVIEW_GROWTH = 350     # panel 550 -> 900, rows 511 -> 861: every column on one line, names whole
OVERVIEW_BARS = 48        # the olive part beside the type icon takes the two bars lying down


def overview_army_row(source):
    """Division row, 509x35 to 861x35. The vanilla row is an olive part (columns 0-123: details
    button, type icon, bars, level), a dark name box (124-295), an olive gap (296-305), a dark box
    for theatre and army on two lines (306-447) and an olive end with the army marker (448-508).
    The wide row has the theatre and the army in a box each, on one line:
      olive 172 | name 290 | gap 10 | theatre 170 | gap 10 | army 148 | end 61"""
    left = grow(source.crop((0, 0, 124, 35)), "x", stretched(98, 120, OVERVIEW_BARS))
    name = grow(source.crop((124, 0, 296, 35)), "x", stretched(12, 160, 118))
    gap = source.crop((296, 0, 306, 35))
    box = source.crop((306, 0, 448, 35))
    theatre = grow(box, "x", stretched(12, 130, 28))
    army = grow(box, "x", stretched(12, 130, 6))
    end = source.crop((448, 0, 509, 35))
    return join([left, name, gap, theatre, gap, army, end], "x")


def overview_navy_row(source):
    """Fleet row, 509x35 to 861x35: a dark icon box (0-110), an olive part with the pride mark, the
    bars and the admiral (111-166), a dark name box (167-316), a gap (317-323), a dark region box
    (324-447) and an olive end with the mission and the ship count (448-508).
      icon 111 | olive 104 | name 370 | gap 7 | region 208 | end 61"""
    return join([
        source.crop((0, 0, 111, 35)),
        grow(source.crop((111, 0, 167, 35)), "x", stretched(4, 22, OVERVIEW_BARS)),
        grow(source.crop((167, 0, 317, 35)), "x", stretched(12, 138, 220)),
        source.crop((317, 0, 324, 35)),
        grow(source.crop((324, 0, 448, 35)), "x", stretched(12, 112, 84)),
        source.crop((448, 0, 509, 35)),
    ], "x")


def overview_air_row(source):
    """Air wing row, 509x35 to 861x35: a dark icon box with the plane count (0-96), an olive part with
    the bar and the ace (97-136), then three dark boxes: name (137-266), base (267-392) and region with
    the missions (393-508), the last one up to the row's end. The name box is the widest: a wing of
    the user's playset is "Kampfgeschwader 253 'General Wever'" (258 px in hoi_18mbs).
      icon 97 | olive 88 | name 290 | base 146 | region 240"""
    return join([
        source.crop((0, 0, 97, 35)),
        grow(source.crop((97, 0, 137, 35)), "x", stretched(6, 34, OVERVIEW_BARS)),
        grow(source.crop((137, 0, 267, 35)), "x", stretched(12, 118, 160)),
        grow(source.crop((267, 0, 393, 35)), "x", stretched(12, 114, 20)),
        grow(source.crop((393, 0, 509, 35)), "x", stretched(12, 100, 124)),
    ], "x")


# ---------------------------------------------------------------------------------------------
# A8, the theatre boxes at the top right (theatreselector.gui). Every box and row grows by THEATRE_GROWTH
# to the left; the numbers are shared with interface/zz_1440p_theatre_bar.gui.

THEATRE_GROWTH = 120      # 300 -> 420: a theatre's name and up to 13 army shields side by side


def theatre_box(frame):
    """One frame of a theatre box, 305x77 to 425x77. Rows 0-36: a black name field (columns 13-204)
    and two boxes at the right; the columns go into the name field. Rows 37-76: the tray of the army
    shields, plain apart from an emblem at 120-175 in the grey frame; half the columns go in on each side
    of it, so it stays in the middle."""
    half = THEATRE_GROWTH // 2
    return grow_bands(frame, "x", [
        (0, 37, stretched(30, 190, THEATRE_GROWTH)),
        (37, frame.height, stretched(60, 110, half) + stretched(190, 240, half)),
    ])


def theatre_strip(frame):
    """One frame of the strip along the bottom of a box (assign_group_button), 299x35 to 419x35: oak
    leaves at both ends; the grey frame has hands at 15-35 and 262-282 and an emblem at 129-168."""
    half = THEATRE_GROWTH // 2
    return grow(frame, "x", stretched(60, 115, half) + stretched(185, 240, half))


# ---------------------------------------------------------------------------------------------
# Production (phase C1). A production line is painted as a header band (rows 0-27) over a body: the
# equipment plate (columns 2-278, a clasp at 122-150 of its top and bottom edge), a dark gap
# (278-320, plain to 300), the factory slots (320-470) and the resource column (470-510). A line grows
# from 511 to 780 columns: the plate by PROD_PLATE in its plain middle (160-260), the dark gap by
# PROD_GAP. The numbers are shared with the widget positions in interface/zz_1440p_production.gui.
# (Round 1 made the lines 1000 wide and the plate 142 wider; the game draws the picture at a fixed
# place [GUL-041] and the tester found the panel too wide and empty, 2026-10-16.)

PROD_PLATE = 20           # equipment plate 278 -> 298: 20 free on each side of the picture
PROD_GAP = 249            # the gap becomes the column of manufacturer, deploy location and ready date


def production_columns(frame, gap=True):
    """A production line bitmap, or a piece of one (the equipment plate, an overlay), grown by the
    plate insert and, unless `gap` is false, the gap insert."""
    inserts = stretched(160, 260, PROD_PLATE)
    if gap:
        inserts += stretched(284, 300, PROD_GAP)
    return grow(frame, "x", inserts)


PROD_HEADER_WIDTH = 796
PROD_FILTER_CELL = 66     # a filter cell: the checkbox (45 wide, 44 columns of the cell) and the count (22)


def production_header(source):
    """The top of the production panel (production_win_top.dds, 550x253: resources, efficiency,
    factories and two rows of filters stacked) as three rows, 796x126.

    Row 1 (44 rows): the resources band (rows 8-52), then a piece of the plain efficiency band for the
    factories in use. Row 2 (48): the factories band where its add-line buttons stand (rows 114-162),
    grown by 286 columns in its plain parts, beside the plain efficiency band for the six efficiency
    figures. Row 3 (34): the twelve filter cells in one row; each cell of the source (85 columns,
    starting at column 13) keeps its checkbox part and the end of its count part.
    """
    out = Image.new("RGBA", (PROD_HEADER_WIDTH, 126), (0, 0, 0, 0))
    out.paste(source.crop((20, 8, 530, 52)), (0, 0))
    plain = grow(source.crop((20, 52, 306, 88)), "y", [(18, 8)])          # 286 x 44
    out.paste(plain, (510, 0))
    factories = grow(source.crop((20, 114, 530, 162)), "x", stretched(120, 240, 143) + stretched(300, 420, 143))
    out.paste(factories.crop((0, 0, 430, 48)), (0, 44))
    out.paste(grow(source.crop((20, 52, 386, 88)), "y", [(18, 12)]), (430, 44))
    x = 0
    for top in (176, 207):
        for k in range(6):
            c = 13 + 85 * k
            out.paste(source.crop((c, top, c + 44, top + 34)), (x, 92))
            out.paste(source.crop((c + 63, top, c + 85, top + 34)), (x + 44, 92))
            x += PROD_FILTER_CELL
    return out


# ---------------------------------------------------------------------------------------------
# General selection (phase C2). The window grows from 550x607 to 800x1180, a general's row from 510x98
# to 760x124 with a portrait box 32 wider. Shared with interface/zz_1440p_leader_selection.gui.

LEADER_ROW_WIDTH = 760
LEADER_ROW_HEIGHT = 124
LEADER_PORTRAIT_GROWTH = 32   # the white portrait box, 64 -> 96 columns


def leader_window(source):
    """The window: its header band holds a painted search field (columns 175-315), so the columns go in
    to its right (375-500, plain); the rows go in across the plain dark middle (110-520), which darkens
    towards the bottom, as many single rows so the gradient stays smooth."""
    out = grow(source, "x", [(500, 250)])
    return grow(out, "y", stretched(110, 520, 1180 - source.height))


def leader_row(source):
    """A general's row: the white portrait box (56-120) takes columns from its plain inside; the paper
    takes a mirrored insert from the plain right half (321-430); the rows go in across the stripes of
    the emblem column and the plain paper under the name (66-79)."""
    paper = LEADER_ROW_WIDTH - source.width - LEADER_PORTRAIT_GROWTH
    out = grow(source, "x", [(100, LEADER_PORTRAIT_GROWTH), (430, paper)])
    return grow(out, "y", [(79, LEADER_ROW_HEIGHT - source.height)])


# ---------------------------------------------------------------------------------------------
# Priority rows of Recruit & Deploy (A5, step 2): 493 to 575 columns, as wide as the training cards
# under them. A row is the icon box (0-95), a plain band (100-350), a lighter band behind the priority
# buttons (355-385) and the end. The columns go in from the plain band. The code puts these
# backgrounds on the rows by their vanilla names, which the mod declares again
# (interface/zz_1440p_vanilla_sprites.gfx). The label plate and the equipment meter grow with them.

PRIORITY_ROW_WIDTH = 575
PRIORITY_TITLE_GROWTH = 52    # label plate 159 -> 211
PRIORITY_METER_GROWTH = 40    # equipment meter 108 -> 148


def priority_row(source):
    return grow(source, "x", [(300, PRIORITY_ROW_WIDTH - source.width)])


# One entry per output texture. `frames` lists one widening call per frame of the source, left to right;
# `compose` is a function that builds the whole output from the source instead.
JOBS = [
    {
        # Air wing, gun emplacement and rocket rows: frame 1 striped (unselected), frame 2 red (selected).
        # Edge bars sit at columns 52-105 and 405-473, the border and bars in rows 0-5 and 41-47,
        # the corner rivets within 10 columns of each end.
        "source": "gfx/interface/airview/wing_entry_bg.dds",
        "output": "av_wing_entry_bg.dds",
        "frames": [
            lambda f: widen_periodic(f, 671, period=73, split=390, top=6, bottom=41, right_cap=10),
            lambda f: widen_periodic(f, 671, period=62, split=390, top=6, bottom=41, right_cap=10),
        ],
    },
    {
        # Division rows: frame 1 striped (unselected), frame 2 a green gradient (selected).
        # The stripes repeat every 30 columns exactly. The border is rows 0-1 and 31-32 and the
        # outer 3 columns; frame 2 has no pattern, only a 4-column border at each end.
        "source": "gfx/interface/unitcontrol/unit_entry_bg.dds",
        "output": "uv_unit_entry_bg.dds",
        "frames": [
            lambda f: widen_periodic(f, 638, period=30, split=360, top=2, bottom=31, right_cap=3),
            lambda f: widen_spread(f, 638, left_cap=4, right_cap=4),
        ],
    },
    {
        # Footer plate of the unassigned divisions list: a dark plate with an irregular texture
        # and a soft border, plain between columns 100 and 273.
        "source": "gfx/interface/unitlist_unassigned_bg.dds",
        "output": "uv_unitlist_unassigned_bg.dds",
        "frames": [
            lambda f: widen_mirror(f, 644, split=273),
        ],
    },
    {
        # Air group badge, 580 to 704 wide: a red strip with a black name field (columns 48-295)
        # above a dark tray. Plain in every row between columns 330 and 392.
        "source": "gfx/interface/airview/air_group.dds",
        "output": "av_air_group_bg.dds",
        "frames": [
            lambda f: widen_mirror(f, 704, split=392),
        ],
    },
    {
        # Army badge, 437 to 685 wide.
        "source": "gfx/interface/unitcontrol/army_group_bg.dds",
        "output": "uv_army_bg.dds",
        "frames": [
            lambda f: widen_mirror_multi(f, BADGE_INSERTS),
        ],
    },
    {
        # Army group badge, 436 to 684 wide.
        "source": "gfx/interface/unitcontrol/army_group_group_bg.dds",
        "output": "uv_army_group_bg.dds",
        "frames": [
            lambda f: widen_mirror_multi(f, BADGE_INSERTS),
        ],
    },
    {
        "source": "gfx/interface/unit_stats_bg.dds",
        "output": "ud_division_bg.dds",
        "compose": division_details,
    },
    {
        # Header bar of the officer block and of each equipment group, 268 to 358 wide: dark metal
        # up to a slanted lighter end that starts at column 175.
        "source": "gfx/interface/unit_stats_list_entry2.dds",
        "output": "ud_list_entry_bg.dds",
        "compose": lambda source: grow(source, "x", stretched(20, 160, SIDE_GROWTH)),
    },
    {
        # Tile behind one stat on the division Stats tab (A3 redo), 122x52, from the plain part of the
        # same header bar.
        "source": "gfx/interface/unit_stats_list_entry2.dds",
        "output": "ud_stat_tile.dds",
        "compose": stat_tile,
    },
    {
        # Frame of the hard and soft attack bar, 207 to 363 wide: plain lines between its ends.
        "source": "gfx/interface/softness_ratio_frame.dds",
        "output": "ud_softness_frame.dds",
        "compose": lambda source: grow(source, "x", [(100, 2 * STAT_COLUMN)]),
    },
    {
        # Line under a history entry, 520 to 754 wide: a dotted line with a red rule at column 50.
        "source": "gfx/interface/sunk_ships_entry_divider.dds",
        "output": "ud_history_divider.dds",
        "compose": lambda source: grow(source, "x", [(500, MAIN_GROWTH)]),
    },
    {
        # Strip behind the medals of the History tab, 533 to 767 wide: scratched metal with rivets
        # in the first and last 20 columns.
        "source": "gfx/interface/deployment_binding.dds",
        "output": "ud_medal_strip.dds",
        "compose": lambda source: grow(source, "x", stretched(40, 490, MAIN_GROWTH)),
    },
    {
        # Ship details (also behind the railway gun details).
        "source": "gfx/interface/naval_unit_stats_bg.dds",
        "output": "ud_ship_bg.dds",
        "compose": small_details((272, stretched(120, 400, 2 * STAT_COLUMN) + stretched(420, 530, STAT_COLUMN)),
                                 stretched(370, 540, MAIN_GROWTH)),
    },
    {
        # Air wing details.
        "source": "gfx/interface/air_unit_stats_bg.dds",
        "output": "ud_air_wing_bg.dds",
        "compose": small_details((278, stretched(20, 530, MAIN_GROWTH)), stretched(370, 530, MAIN_GROWTH)),
    },
    {
        # Row of an air wing on a carrier and of a plane type in a wing, 268 to 358 wide: a plain
        # dark box with rounded corners.
        "source": "gfx/interface/air_unit_stats_equip_entry.dds",
        "output": "ud_wing_entry_bg.dds",
        "compose": lambda source: grow(source, "x", [(134, SIDE_GROWTH)]),
    },
    {
        "source": "gfx/interface/unit_stats_template_tab_bg.dds",
        "output": "ud_template_bg.dds",
        "compose": template_board,
    },
    {
        "source": "gfx/interface/army_hq_unit_details_bg.dds",
        "output": "ud_template_hq_bg.dds",
        "compose": hq_board,
    },
    {
        # A4, fleet card.
        "source": "gfx/interface/naviesview/fleet_bg.dds",
        "output": "fl_fleet_bg.dds",
        "compose": fleet_card,
    },
    {
        # Gold outline of a selected fleet card, 497 to 745 wide: plain lines between its corners.
        "source": "gfx/interface/naviesview/fleet_bg_hl.dds",
        "output": "fl_fleet_bg_hl.dds",
        "compose": lambda source: grow(source, "x", [(250, FLEET_GROWTH)]),
    },
    {
        "source": "gfx/interface/naviesview/task_force_bg.dds",
        "output": "fl_task_force_bg.dds",
        "compose": task_force_card,
    },
    {
        "source": "gfx/interface/naviesview/task_force_bg_hl.dds",
        "output": "fl_task_force_bg_hl.dds",
        "compose": lambda source: cut(grow(source, "x", [(250, FLEET_GROWTH)]), "y", [(45, TASK_FORCE_TRAY[1])]),
    },
    {
        # Toolbar plate between the fleet card and the task forces: scratched metal with a rivet
        # in each corner.
        "source": "gfx/interface/naviesview/task_force_actions_bg.dds",
        "output": "fl_task_force_actions_bg.dds",
        "compose": lambda source: grow(source, "x", stretched(20, 470, FLEET_GROWTH)),
    },
    {
        # Ship rows: frame 1 unselected, frame 2 selected (lighter, with a chevron at the right end).
        "source": "gfx/interface/naval_unit_ship_entry.dds",
        "output": "fl_ship_entry.dds",
        "frames": [ship_row(12), ship_row(34)],
    },
    {
        # Gold outline of a selected ship row, 490x43 to 738x37: plain lines and a thick right end.
        "source": "gfx/interface/naviesview/naval_unit_ship_entry_highlight.dds",
        "output": "fl_ship_entry_highlight.dds",
        "compose": lambda source: cut(grow(source, "x", [(245, FLEET_GROWTH)]), "y", [(12, 2), (20, 2), (28, 2)]),
    },
    {
        # Home base button of the fleet card, 124 to 184 wide: an anchor badge and a name bar that
        # is plain between columns 45 and 115.
        "source": "gfx/interface/naval_deploy_button.dds",
        "output": "fl_home_base_button.dds",
        "compose": lambda source: grow(source, "x", stretched(45, 115, 60)),
    },
    {
        # A4 step 2. Row of the composition editor, 493 to 573 wide: a plate for the remove button
        # (columns 0-40), then a plain bar.
        "source": "gfx/interface/task_force_comp_unit_bg.dds",
        "output": "fl_comp_entry.dds",
        "compose": lambda source: grow(source, "x", stretched(60, 470, POPUP_GROWTH)),
    },
    {
        # The "+" row under them: a plain bar.
        "source": "gfx/interface/task_force_comp_add_bg.dds",
        "output": "fl_comp_add.dds",
        "compose": lambda source: grow(source, "x", stretched(30, 470, POPUP_GROWTH)),
    },
    {
        # Header and menu bar of the composition editor, 505 to 585 wide: scratched metal, rivets
        # in the corners.
        "source": "gfx/interface/frontend_task_force_composition_editor_upper_bar.dds",
        "output": "fl_comp_editor_bar.dds",
        "compose": lambda source: grow(source, "x", stretched(30, 475, POPUP_GROWTH)),
    },
    {
        # Row of the home base picker, 335 to 415 wide: an icon plate (columns 0-33), then a
        # meshed name bar.
        "source": "gfx/interface/deploy_port_fleet_bg.dds",
        "output": "fl_home_base_entry.dds",
        "compose": lambda source: grow(source, "x", stretched(60, 320, POPUP_GROWTH)),
    },
    {
        # Header of the transfer window, 516 to 676 wide.
        "source": "gfx/interface/tradeview/trade_header.dds",
        "output": "fl_transfer_header.dds",
        "compose": lambda source: grow(source, "x", stretched(30, 490, TRANSFER_GROWTH)),
    },
    {
        # Ship rows of the transfer window, 653x41.
        "source": "gfx/interface/naval_unit_ship_entry.dds",
        "output": "fl_transfer_ship_entry.dds",
        "frames": [ship_row(12, TRANSFER_GROWTH), ship_row(34, TRANSFER_GROWTH)],
    },
    {
        # A5. Card of a template in training.
        "source": "gfx/interface/military_deployment_conveyor_bg.dds",
        "output": "rd_conveyor_bg.dds",
        "compose": conveyor_card,
    },
    {
        # Summary row under the card, 518 to 608 wide: plain metal between the rivets at column 65
        # and the bar slot at 213.
        "source": "gfx/interface/military_deployment_add_line_bg.dds",
        "output": "rd_summary_bg.dds",
        "compose": lambda source: grow(source, "x", stretched(80, 200, DEPLOY_GROWTH)),
    },
    {
        # Row of a division in training, 514 to 604 wide: the name box (columns 5-203) is a plain
        # dark box.
        "source": "gfx/interface/military_deployment_line_bg.dds",
        "output": "rd_line_bg.dds",
        "compose": lambda source: grow(source, "x", stretched(25, 190, DEPLOY_GROWTH)),
    },
    {
        # Closing line under the rows of a card, 516 to 606 wide.
        "source": "gfx/interface/military_deployment_end_line.dds",
        "output": "rd_end_line.dds",
        "compose": lambda source: grow(source, "x", stretched(30, 480, DEPLOY_GROWTH)),
    },
    {
        # Location button of a card, 223 to 313 wide: frame 1 plain, frame 2 with chevrons every
        # 15 columns.
        "source": "gfx/interface/conveyor_location_btn.dds",
        "output": "rd_location_btn.dds",
        "frames": [
            lambda f: grow(f, "x", stretched(45, 200, DEPLOY_GROWTH)),
            lambda f: grow(f, "x", [(170, DEPLOY_GROWTH, 15)]),
        ],
    },
    {
        # Header of the Recruit & Deploy panel, 543 to 633 wide: scratched metal up to the box of
        # the close button at column 491.
        "source": "gfx/interface/header_bg.dds",
        "output": "rd_header_bg.dds",
        "compose": lambda source: grow(source, "x", stretched(120, 480, DEPLOY_GROWTH)),
    },
    {
        # Strip under that header, 533 to 623 wide.
        "source": "gfx/interface/deployment_binding.dds",
        "output": "rd_binding.dds",
        "compose": lambda source: grow(source, "x", stretched(40, 490, DEPLOY_GROWTH)),
    },
    {
        # Header of the Division Templates panel, 375 to 618 wide: plain between columns 70 and 365.
        "source": "gfx/interface/subview_header_bg_375x101.dds",
        "output": "rd_templates_header.dds",
        "compose": lambda source: grow(source, "x", stretched(75, 360, TEMPLATE_PANEL_GROWTH)),
    },
    {
        # Row of a template: the mesh of the name box is rows 12-49, the strip under it 53-65.
        "source": "gfx/interface/deployment_named_division_bg.dds",
        "output": "rd_template_entry.dds",
        "compose": template_row(mesh_rows=(12, 50), strip_rows=(53, 66), mesh_period=4),
    },
    {
        # Its brown twin for a decommissioned template: mesh rows 13-48, strip 52-64.
        "source": "gfx/interface/deployment_named_division_obsolete_bg.dds",
        "output": "rd_template_entry_obsolete.dds",
        "compose": template_row(mesh_rows=(13, 49), strip_rows=(52, 65), mesh_period=12),
    },
    {
        # A6. Rows of the army overview: a division, a fleet, an air wing.
        "source": "gfx/interface/armyoverview_entry_bg.dds",
        "output": "ao_army_entry.dds",
        "compose": overview_army_row,
    },
    {
        "source": "gfx/interface/armyoverview_naval_entry_bg.dds",
        "output": "ao_navy_entry.dds",
        "compose": overview_navy_row,
    },
    {
        "source": "gfx/interface/armyoverview_air_entry_bg.dds",
        "output": "ao_air_entry.dds",
        "compose": overview_air_row,
    },
    {
        # Title bar, 543 to 893 wide: scratched metal up to the box of the close button at column 491.
        "source": "gfx/interface/header_bg.dds",
        "output": "ao_header_bg.dds",
        "compose": lambda source: grow(source, "x", stretched(120, 480, OVERVIEW_GROWTH)),
    },
    {
        # Picture strip under the title, three frames (army, navy, air) of 522 to 872: a painting that
        # fades into a dark plate, plain from column 300 to the rim.
        "source": "gfx/interface/overview_top_strip.dds",
        "output": "ao_top_strip.dds",
        "frames": [lambda f: grow(f, "x", stretched(320, 505, OVERVIEW_GROWTH))] * 3,
    },
    {
        # Box of the filter, 190 to 320 wide: a dark field with rounded ends.
        "source": "gfx/interface/edittextbox_bg1.dds",
        "output": "ao_filter_bg.dds",
        "compose": lambda source: grow(source, "x", stretched(20, 170, 130)),
    },
    {
        # Plate under the list ("Active in 1 Theater(s)"), 516 to 866 wide.
        "source": "gfx/interface/tradeview/trade_header.dds",
        "output": "ao_bottom.dds",
        "compose": lambda source: grow(source, "x", stretched(30, 490, OVERVIEW_GROWTH)),
    },
    {
        # A8. A theatre box: five frames (army, grey, navy, reserve fleets, air).
        "source": "gfx/interface/theater/theater_group_bg.dds",
        "output": "ts_group_bg.dds",
        "frames": [theatre_box] * 5,
    },
    {
        "source": "gfx/interface/theater/assign_group_button.dds",
        "output": "ts_assign_button.dds",
        "frames": [theatre_strip] * 4,
    },
    {
        # The frame around the chosen box, 303x74 to 423x74: lines, with marks at columns 12-42 and
        # 274-302; plain between 183 and 274.
        "source": "gfx/interface/theater/selected_theatre_frame.dds",
        "output": "ts_selected_frame.dds",
        "compose": lambda source: grow(source, "x", stretched(195, 265, THEATRE_GROWTH)),
    },
    {
        # The rows under a box (an army group's armies, a fleet row), 301x33 and 301x39 to 421 wide,
        # four frames each: plain between the edges at 3 and 298.
        "source": "gfx/interface/theater/theatre_dropdown_middle.dds",
        "output": "ts_dropdown_middle.dds",
        "frames": [lambda f: grow(f, "x", stretched(60, 240, THEATRE_GROWTH))] * 4,
    },
    {
        "source": "gfx/interface/theater/theatre_dropdown_bottom.dds",
        "output": "ts_dropdown_bottom.dds",
        "frames": [lambda f: grow(f, "x", stretched(60, 240, THEATRE_GROWTH))] * 4,
    },
    {
        # The "new theatre" button under the boxes, 303x37 to 423x37: plain between its ends.
        "source": "gfx/interface/theater/theater_group_assign_btn.dds",
        "output": "ts_new_group_button.dds",
        "compose": lambda source: grow(source, "x", stretched(40, 260, THEATRE_GROWTH)),
    },
    {
        # A strategic region under a box, 198x39 to 318x39, three frames: plain between 30 and 165.
        "source": "gfx/interface/theatre_selection_background.dds",
        "output": "ts_region_bg.dds",
        "frames": [lambda f: grow(f, "x", stretched(40, 160, THEATRE_GROWTH))] * 3,
    },
    {
        # A7. A plane type in the air wing reorganisation window, 458 to 578 wide, two frames: olive
        # bands, plain from column 60 to the dark column at 365; the clasps of the top and bottom edges
        # sit at 212-245, so the columns go in after them.
        "source": "gfx/interface/equipment_item_large_02.dds",
        "output": "aw_equipment_entry.dds",
        "frames": [lambda f: grow(f, "x", stretched(260, 355, 120))] * 2,
    },
    {
        # Plate of one modifier, 74 to 120 wide: seven of them fill a row of the wider header.
        "source": "gfx/interface/modifiers/MODIFIER_bg.dds",
        "output": "ao_modifier_bg.dds",
        "compose": lambda source: grow(source, "x", stretched(14, 56, 46)),
    },
    # C1. Production: the lines 1000 wide, the equipment plates and overlays 142 wider, the panel top
    # rearranged. production_item and the naval strip keep their vanilla sprite names (the code sets
    # them), the others get GFX_1440p_ names.
    {
        "source": "gfx/interface/production_win_top.dds",
        "output": "pd_header.dds",
        "compose": production_header,
    },
    {
        "source": "gfx/interface/production_item.dds",
        "output": "pd_line.dds",
        "frames": [production_columns],
    },
    {
        # Three frames: one, two and three rows of factory slots.
        "source": "gfx/interface/naval_production_item_slots_strip.dds",
        "output": "pd_naval_line.dds",
        "frames": [production_columns] * 3,
    },
    {
        "source": "gfx/interface/production_item_collapsed.dds",
        "output": "pd_line_collapsed.dds",
        "frames": [production_columns],
    },
    {
        "source": "gfx/interface/production_line_selected.dds",
        "output": "pd_line_selected.dds",
        "frames": [production_columns],
    },
    {
        "source": "gfx/interface/naval_production_line_selected.dds",
        "output": "pd_naval_line_selected.dds",
        "frames": [production_columns],
    },
    {
        "source": "gfx/interface/production_item_selected_collapsed.dds",
        "output": "pd_line_selected_collapsed.dds",
        "frames": [production_columns],
    },
    {
        # The marker of a line that a military-industrial organisation produces: the header band only.
        "source": "gfx/interface/military_industrial_organization/production_item_has_mio.dds",
        "output": "pd_line_has_mio.dds",
        "frames": [production_columns],
    },
    {
        "source": "gfx/interface/prod_land_equipment_item_large.dds",
        "output": "pd_land_item_large.dds",
        "frames": [lambda f: production_columns(f, gap=False)],
    },
    {
        "source": "gfx/interface/prod_naval_equipment_item_large.dds",
        "output": "pd_naval_item_large.dds",
        "frames": [lambda f: production_columns(f, gap=False)],
    },
    {
        "source": "gfx/interface/equipment_item_collapsed.dds",
        "output": "pd_item_collapsed.dds",
        "frames": [lambda f: production_columns(f, gap=False)],
    },
    {
        "source": "gfx/interface/naval_item_collapsed.dds",
        "output": "pd_naval_item_collapsed.dds",
        "frames": [lambda f: production_columns(f, gap=False)],
    },
    {
        "source": "gfx/interface/outdated_equipment_overlay.dds",
        "output": "pd_outdated_overlay.dds",
        "frames": [lambda f: production_columns(f, gap=False)],
    },
    {
        "source": "gfx/interface/outdated_naval_equipment_overlay.dds",
        "output": "pd_outdated_naval_overlay.dds",
        "frames": [lambda f: production_columns(f, gap=False)],
    },
    {
        "source": "gfx/interface/outdated_equipment_overlay_collapsed.dds",
        "output": "pd_outdated_overlay_collapsed.dds",
        "frames": [lambda f: production_columns(f, gap=False)],
    },
    {
        "source": "gfx/interface/outdated_naval_overlay_collapsed.dds",
        "output": "pd_outdated_naval_overlay_collapsed.dds",
        "frames": [lambda f: production_columns(f, gap=False)],
    },
    {
        # The deploy location button of a ship line, 124 to 185 wide: a round badge (0-36), a plain bar.
        "source": "gfx/interface/naval_deploy_button.dds",
        "output": "pd_deploy_button.dds",
        "compose": lambda source: grow(source, "x", stretched(50, 110, 61)),
    },
    # C2. General selection: the window and a general's row.
    {
        "source": "gfx/interface/leader_selection_bg.dds",
        "output": "ls_window_bg.dds",
        "compose": leader_window,
    },
    {
        "source": "gfx/interface/leader_selection_entry_bg.dds",
        "output": "ls_entry_bg.dds",
        "compose": leader_row,
    },
    # A5, step 2. The priority rows of Recruit & Deploy (the lend-lease row uses the garrisons texture),
    # their label plate and their equipment meter.
    {
        "source": "gfx/interface/deploy_reinforcements_entry.dds",
        "output": "rd_reinforcements_entry.dds",
        "compose": priority_row,
    },
    {
        "source": "gfx/interface/deploy_upgrades_entry.dds",
        "output": "rd_upgrades_entry.dds",
        "compose": priority_row,
    },
    {
        "source": "gfx/interface/deploy_supply_entry.dds",
        "output": "rd_supply_entry.dds",
        "compose": priority_row,
    },
    {
        "source": "gfx/interface/deploy_operations_entry.dds",
        "output": "rd_operations_entry.dds",
        "compose": priority_row,
    },
    {
        "source": "gfx/interface/deploy_garrisons_entry.dds",
        "output": "rd_garrisons_entry.dds",
        "compose": priority_row,
    },
    {
        "source": "gfx/interface/deploy_priority_title_bg.dds",
        "output": "rd_priority_title_bg.dds",
        "compose": lambda source: grow(source, "x", [(80, PRIORITY_TITLE_GROWTH)]),
    },
    {
        "source": "gfx/interface/deploy_priority_equipment_meter_bg.dds",
        "output": "rd_priority_meter_bg.dds",
        "compose": lambda source: grow(source, "x", [(80, PRIORITY_METER_GROWTH)]),
    },
]


from guiparse import find_game_dir  # noqa: E402  (shared with render_gui.py)


def build(job, game_dir):
    source = Image.open(os.path.join(game_dir, *job["source"].split("/"))).convert("RGBA")
    if "compose" in job:
        out = job["compose"](source)
        return source, [out], out
    count = len(job["frames"])
    frame_width = source.width // count
    frames = [
        widen(source.crop((i * frame_width, 0, (i + 1) * frame_width, source.height)))
        for i, widen in enumerate(job["frames"])
    ]
    return source, frames, join(frames, "x")


def write_preview(job, source, frames, preview_dir):
    """Vanilla frames above the widened ones, on a mid-grey ground, at 2x for inspection."""
    count = 1 if "compose" in job else len(frames)
    frame_width = source.width // count
    rows = [source.crop((i * frame_width, 0, (i + 1) * frame_width, source.height)) for i in range(count)] + frames
    gap = 6
    sheet = Image.new("RGBA", (max(r.width for r in rows) + 2 * gap, sum(r.height + gap for r in rows) + gap), (90, 96, 104, 255))
    y = gap
    for row in rows:
        sheet.alpha_composite(row, (gap, y))
        y += row.height + gap
    if "compose" not in job:   # rows are small, so they are enlarged; a composed window is read at 1:1
        sheet = sheet.resize((sheet.width * 2, sheet.height * 2), Image.NEAREST)
    path = os.path.join(preview_dir, os.path.splitext(job["output"])[0] + "_preview.png")
    sheet.convert("RGB").save(path)
    return path


def main():
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--game-dir", help="Hearts of Iron IV install folder (default: HOI4_GAME_DIR, then Steam)")
    parser.add_argument("--preview", metavar="DIR", help="also write before/after PNG previews to DIR")
    parser.add_argument("--only", metavar="NAME", help="build only the outputs whose file name contains NAME")
    args = parser.parse_args()

    game_dir = find_game_dir(args.game_dir)
    if not game_dir:
        sys.exit("Hearts of Iron IV install not found. Pass --game-dir or set HOI4_GAME_DIR.")

    os.makedirs(OUT_DIR, exist_ok=True)
    for job in JOBS:
        if args.only and args.only not in job["output"]:
            continue
        source, frames, out = build(job, game_dir)
        target = os.path.join(OUT_DIR, job["output"])
        out.save(target)
        print(f"{job['source']} {source.size} -> {os.path.relpath(target, REPO_ROOT)} {out.size}")
        if args.preview:
            os.makedirs(args.preview, exist_ok=True)
            print("   preview:", write_preview(job, source, frames, args.preview))


if __name__ == "__main__":
    main()
