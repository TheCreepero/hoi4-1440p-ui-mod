"""Build wider row backgrounds from vanilla textures by copying pixels only.

Every output is assembled from columns of one vanilla texture: kept, repeated, or copied in
mirrored order. No pixel is drawn or blended, so the result keeps the vanilla look. Re-run after a
game update that changes a source texture.

    python tools/stretch_background.py [--game-dir DIR] [--preview DIR]

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


# Army and army group badge. Both are painted alike: the name field (columns 57-229 of the top band),
# the commander box (66-219), the stats box (221-297), a plain right area (297-429) and the tray
# along the bottom (64-428). The inserts widen the name field and commander box, the stats box and
# the right area.
BADGE_INSERTS = [(200, 100), (295, 48), (425, 100)]

# One entry per output texture. `frames` lists one widening call per frame of the source, left to right.
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
]


from guiparse import find_game_dir  # noqa: E402  (shared with render_gui.py)


def build(job, game_dir):
    source = Image.open(os.path.join(game_dir, *job["source"].split("/"))).convert("RGBA")
    count = len(job["frames"])
    frame_width = source.width // count
    frames = [
        widen(source.crop((i * frame_width, 0, (i + 1) * frame_width, source.height)))
        for i, widen in enumerate(job["frames"])
    ]
    out = Image.new("RGBA", (sum(f.width for f in frames), source.height))
    x = 0
    for frame in frames:
        out.paste(frame, (x, 0))
        x += frame.width
    return source, frames, out


def write_preview(job, source, frames, preview_dir):
    """Vanilla frames above the widened ones, on a mid-grey ground, at 2x for inspection."""
    count = len(frames)
    frame_width = source.width // count
    rows = [source.crop((i * frame_width, 0, (i + 1) * frame_width, source.height)) for i in range(count)] + frames
    gap = 6
    sheet = Image.new("RGBA", (max(r.width for r in rows) + 2 * gap, sum(r.height + gap for r in rows) + gap), (90, 96, 104, 255))
    y = gap
    for row in rows:
        sheet.alpha_composite(row, (gap, y))
        y += row.height + gap
    sheet = sheet.resize((sheet.width * 2, sheet.height * 2), Image.NEAREST)
    path = os.path.join(preview_dir, os.path.splitext(job["output"])[0] + "_preview.png")
    sheet.convert("RGB").save(path)
    return path


def main():
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--game-dir", help="Hearts of Iron IV install folder (default: HOI4_GAME_DIR, then Steam)")
    parser.add_argument("--preview", metavar="DIR", help="also write before/after PNG previews to DIR")
    args = parser.parse_args()

    game_dir = find_game_dir(args.game_dir)
    if not game_dir:
        sys.exit("Hearts of Iron IV install not found. Pass --game-dir or set HOI4_GAME_DIR.")

    os.makedirs(OUT_DIR, exist_ok=True)
    for job in JOBS:
        source, frames, out = build(job, game_dir)
        target = os.path.join(OUT_DIR, job["output"])
        out.save(target)
        print(f"{job['source']} {source.size} -> {os.path.relpath(target, REPO_ROOT)} {out.size}")
        if args.preview:
            os.makedirs(args.preview, exist_ok=True)
            print("   preview:", write_preview(job, source, frames, args.preview))


if __name__ == "__main__":
    main()
