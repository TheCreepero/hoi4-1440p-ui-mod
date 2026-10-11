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
