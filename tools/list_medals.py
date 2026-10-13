"""Dev only: reads the game's unit medals and prints the rows of tools/unit_medals_table.py. To be run again
after a game update that changes the medals, and the rows pasted into that file.

    python -I tools/list_medals.py > scratch/medals_table.txt
"""
import io
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import guiparse  # noqa: E402

GAME = guiparse.find_game_dir()


def blocks(text):
    """Top-level 'name = { ... }' blocks of a text, comments removed."""
    text = re.sub(r"#[^\n]*", "", text)
    out, i = [], 0
    for m in re.finditer(r"([A-Za-z_0-9]+)\s*=\s*\{", text):
        if m.start() < i:
            continue
        depth, j = 1, m.end()
        while depth:
            depth += {"{": 1, "}": -1}.get(text[j], 0)
            j += 1
        out.append((m.group(1), text[m.end():j - 1]))
        i = j
    return out


source = io.open(os.path.join(GAME, "common", "unit_medals", "00_default.txt"), encoding="utf-8").read()
loc = io.open(os.path.join(GAME, "localisation", "english", "unit_medals_l_english.yml"), encoding="utf-8-sig").read()
names = dict(re.findall(r'^\s*([A-Za-z_0-9]+):\d*\s*"([^"]*)"', loc, re.M))
medals = blocks(dict(blocks(source))["unit_medals"])
print("# (id, icon set, frame, available) : %d medals" % len(medals))
for name, body in medals:
    parts = dict(blocks(body))
    available = " ".join(parts.get("available", "always = yes").split())
    frame = re.search(r"\bframe\s*=\s*(\d+)", body)
    icon = re.search(r'icon\s*=\s*"GFX_medal_icon_(\w+)"', body)
    ship = "ship" if "ship_modifiers" in parts else ""
    unit = "unit" if "unit_modifiers" in parts else ""
    sys.stdout.write('    ("%s", "%s", %s, "%s"),  # %s %s%s\n' % (
        name, icon.group(1), frame.group(1) if frame else "1", available, names.get(name, "?"), unit, ship))
