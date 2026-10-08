"""Build wider row backgrounds from vanilla textures by copying pixels only.

Every output is assembled from columns of one vanilla texture. No pixel is drawn, blended or
resampled, so the result keeps the vanilla look exactly. Re-run after a game update that changes
a source texture.

    python tools/stretch_background.py [--game-dir DIR] [--preview DIR]

Needs Pillow. Outputs go to gfx/interface/1440p_ui/ as uncompressed 32-bit DDS, the format the
vanilla files use.
"""

import argparse
import os
import re
import sys

from PIL import Image

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


# One entry per output texture. `frames` lists one widening call per frame of the source, left to right.
JOBS = [
    {
        # Air wing, gun emplacement and rocket rows: frame 1 striped (unselected), frame 2 red (selected).
        # Edge bars sit at columns 52-105 and 405-473, the border and bars in rows 0-5 and 41-47,
        # the corner rivets within 10 columns of each end.
        "source": "gfx/interface/airview/wing_entry_bg.dds",
        "output": "av_wing_entry_bg.dds",
        "frames": [
            lambda f: widen_periodic(f, 734, period=73, split=390, top=6, bottom=41, right_cap=10),
            lambda f: widen_periodic(f, 734, period=62, split=390, top=6, bottom=41, right_cap=10),
        ],
    },
]


def find_game_dir(explicit):
    candidates = [explicit, os.environ.get("HOI4_GAME_DIR")]
    steam_roots = [r"C:\Program Files (x86)\Steam"]
    try:
        import winreg

        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Valve\Steam") as key:
            steam_roots.insert(0, winreg.QueryValueEx(key, "SteamPath")[0].replace("/", "\\"))
    except OSError:
        pass
    for root in list(steam_roots):
        vdf = os.path.join(root, "steamapps", "libraryfolders.vdf")
        if os.path.isfile(vdf):
            with open(vdf, encoding="utf-8", errors="replace") as handle:
                steam_roots += [m.replace("\\\\", "\\") for m in re.findall(r'"path"\s+"([^"]+)"', handle.read())]
    candidates += [os.path.join(root, "steamapps", "common", "Hearts of Iron IV") for root in steam_roots]
    for candidate in candidates:
        if candidate and os.path.isdir(os.path.join(candidate, "gfx", "interface")):
            return candidate
    return None


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
