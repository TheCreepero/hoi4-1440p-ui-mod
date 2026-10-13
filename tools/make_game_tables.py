"""Reads the installed game and writes the tables of game content the Records window needs.

    python -I tools/make_game_tables.py            write tools/portraits_table.py and tools/victory_points_table.py
    python -I tools/make_game_tables.py --check    exit 1 when a table on disk differs from the game
    python -I tools/make_game_tables.py --mods     write tools/portraits_mods_table.py from the mods of the
                                                   launcher's playset (the officers those mods add)

To be run again after a game update: tools/build_managers.py reads the tables, not the game.

    portraits_table.py        every character of common/characters with a portrait sprite: who can be a general,
                              an admiral or a head of government, and which sprite the game shows for each
    victory_points_table.py   every victory point of history/states: its province, state and value
    portraits_mods_table.py   the same as portraits_table.py for characters that mods add. Optional: the build
                              tool uses it when it is there. A name the loaded game does not know is not found
                              and logs nothing, so the lookup is harmless without those mods.

Script cannot ask the game for a character's portrait or for the name of a province. It can ask whether a
character is a certain one (is_character) and who controls a province (province_controllers), so the mod
carries these two lists (wiki/Engine-Facts.md, X58 to X60).
"""
import glob
import io
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import guiparse  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UNIT_ROLES = ("corps_commander", "field_marshal", "navy_leader")


def blocks(text):
    """The 'name = { ... }' blocks at the top level of a text."""
    out, i = [], 0
    for m in re.finditer(r"([A-Za-z_0-9.\-']+)\s*=\s*\{", text):
        if m.start() < i:
            continue
        depth, j = 1, m.end()
        while depth and j < len(text):
            depth += {"{": 1, "}": -1}.get(text[j], 0)
            j += 1
        out.append((m.group(1), text[m.end():j - 1]))
        i = j
    return out


def without_comments(text):
    return re.sub(r"#[^\n]*", "", text)


def portraits(game, by_effect=False):
    """(character, file tag, army sprite, navy sprite, civilian sprite, roles) for every character with a sprite.
    by_effect: a character whose file gives him no role at all is taken as an officer too. That is how mods add
    generals: the character is defined bare, and an event gives him his command (add_corps_commander_role)."""
    rows = []
    for path in sorted(glob.glob(os.path.join(game, "common", "characters", "*.txt"))):
        tag = os.path.splitext(os.path.basename(path))[0]
        text = without_comments(io.open(path, encoding="utf-8-sig", errors="replace").read())
        for top, body in blocks(text):
            if top != "characters":
                continue
            for name, character in blocks(body):
                found = {}
                for kind in ("army", "navy", "civilian"):
                    m = re.search(r"\b%s\s*=\s*\{[^{}]*?\blarge\s*=\s*\"?(GFX_[A-Za-z0-9_\-]+)\"?" % kind, character)
                    if m:
                        found[kind] = m.group(1)
                roles = [role for role in UNIT_ROLES + ("country_leader",) if re.search(r"\b%s\s*=\s*\{" % role, character)]
                if by_effect and not roles and not re.search(r"\b(advisor|scientist)\s*=\s*\{", character):
                    roles = ["navy_leader"] if ("navy" in found and "army" not in found) else ["corps_commander"]
                if found and roles:
                    rows.append((name, tag, found.get("army", ""), found.get("navy", ""), found.get("civilian", ""), " ".join(roles)))
    return rows


def playset(user):
    """(name, folder) of the mods of the launcher's playset, this mod left out. While a game check runs the
    harness has its own playset in place and keeps the user's in scratch/dlc_load.backup.json."""
    path = os.path.join(ROOT, "scratch", "dlc_load.backup.json")
    if not os.path.isfile(path):
        path = os.path.join(user, "dlc_load.json")
    mods = []
    for rel in json.load(io.open(path, encoding="utf-8-sig")).get("enabled_mods", []):
        file = os.path.join(user, rel)
        if not os.path.isfile(file):
            continue
        text = io.open(file, encoding="utf-8-sig", errors="replace").read()
        name = re.search(r'^\s*name\s*=\s*"([^"]*)"', text, re.M)
        folder = re.search(r'^\s*path\s*=\s*"([^"]*)"', text, re.M)
        if not folder or not os.path.isdir(folder.group(1)):
            continue
        if os.path.isfile(os.path.join(folder.group(1), "tools", "make_game_tables.py")) or "hoi4-1440p-ui-mod" in rel:
            continue
        mods.append((name.group(1) if name else rel, folder.group(1)))
    return mods


def mod_portraits(game, user):
    """The characters the mods of the playset add to the game's own, and the names of the mods that add any."""
    from portraits_table import PORTRAITS
    known = set(row[0] for row in PORTRAITS)
    tags = country_tags(game)
    rows, used = [], []
    for name, folder in playset(user):
        added = 0
        for row in portraits(folder, by_effect=True):
            if row[0] in known:
                continue        # the game's own character: its sprite name is the game's, whatever picture a mod puts there
            known.add(row[0])
            # the file of a country: named after its tag (USA), or with the tag as a part of its name (AUGA_USA)
            source = row[1]
            if source not in tags:
                parts = [part for part in re.split(r"[^A-Za-z0-9]+", source) if part in tags]
                source = parts[0] if parts else "mod_" + re.sub(r"[^A-Za-z0-9]+", "_", source)
            rows.append((row[0], source) + row[2:])
            added += 1
        if added:
            used.append("%s: %d" % (name, added))
    return rows, used


def country_tags(game):
    """The tags of common/country_tags: a file of characters named after one holds that country's people."""
    tags = set()
    for path in glob.glob(os.path.join(game, "common", "country_tags", "*.txt")):
        text = without_comments(io.open(path, encoding="utf-8-sig", errors="replace").read())
        tags.update(re.findall(r"^\s*([A-Z][A-Z0-9]{2})\s*=", text, re.M))
    return tags


def victory_points(game):
    """(province, state, value) for every victory point, and which provinces have a name."""
    rows = []
    for path in sorted(glob.glob(os.path.join(game, "history", "states", "*.txt"))):
        text = without_comments(io.open(path, encoding="utf-8-sig", errors="replace").read())
        state = re.search(r"\bid\s*=\s*(\d+)", text)
        for m in re.finditer(r"victory_points\s*=\s*\{\s*(\d+)\s+([\d.]+)\s*\}", text):
            rows.append((int(m.group(1)), int(state.group(1)), int(float(m.group(2)))))
    names = set()
    for path in glob.glob(os.path.join(game, "localisation", "english", "*.yml")):
        text = io.open(path, encoding="utf-8-sig", errors="replace").read()
        names.update(int(k) for k in re.findall(r"^\s*VICTORY_POINTS_(\d+):", text, re.M))
    seen, out = set(), []
    for province, state, value in sorted(rows):
        if province in names and province not in seen:     # a point without a name could not be written down
            seen.add(province)
            out.append((province, state, value))
    return out


def version(game):
    for line in io.open(os.path.join(game, "launcher-settings.json"), encoding="utf-8", errors="replace"):
        m = re.search(r'"rawVersion"\s*:\s*"([^"]+)"', line)
        if m:
            return m.group(1)
    return "unknown"


def main(argv):
    game = guiparse.find_game_dir()
    if not game or not os.path.isdir(game):
        print("game folder not found: the tables on disk stay as they are")
        return 2
    if "--mods" in argv:
        user = os.path.join(os.path.expanduser("~"), "Documents", "Paradox Interactive", "Hearts of Iron IV")
        rows, used = mod_portraits(game, user)
        content = (
            '"""Made by tools/make_game_tables.py --mods from the mods of the launcher\'s playset: run it again when the\n'
            "playset changes. Delete this file for a build that knows the game's own characters only.\n\n"
            "A row is as in portraits_table.py. A character whose file gives him no role is taken as an officer whose\n"
            "command comes by an effect. The game's own characters are left out, also where a mod changes them.\n"
            '%d characters."""\n\nMODS = [\n%s]\n\nPORTRAITS = [\n%s]\n'
            % (len(rows), "".join("    %r,\n" % line for line in used), "".join("    %r,\n" % (row,) for row in rows)))
        io.open(os.path.join(ROOT, "tools", "portraits_mods_table.py"), "w", encoding="utf-8", newline="\n").write(content)
        print("wrote tools/portraits_mods_table.py: %d characters of %d mods" % (len(rows), len(used)))
        return 0
    made = version(game)
    people = portraits(game)
    tags = sorted(country_tags(game) & set(row[1] for row in people))
    points = victory_points(game)
    files = {
        "tools/portraits_table.py": (
            '"""Made by tools/make_game_tables.py from the game %s: change the game, not this file.\n\n'
            "A row is (character, file of common/characters, army sprite, navy sprite, civilian sprite, roles).\n"
            "TAGS are the files that carry the name of a country: script asks a country for its tag before it goes\n"
            "through the people of that file.\n"
            '%d characters."""\n\nTAGS = %r\n\nPORTRAITS = [\n%s]\n'
            % (made, len(people), tags, "".join("    %r,\n" % (row,) for row in people))),
        "tools/victory_points_table.py": (
            '"""Made by tools/make_game_tables.py from the game %s: change the game, not this file.\n\n'
            "A row is (province, state, value). The name of a point is the game's text VICTORY_POINTS_<province>.\n"
            '%d victory points."""\n\nVICTORY_POINTS = [\n%s]\n'
            % (made, len(points), "".join("    %r,\n" % (row,) for row in points))),
    }
    stale = []
    for rel, content in files.items():
        path = os.path.join(ROOT, rel)
        current = io.open(path, encoding="utf-8", newline="").read() if os.path.isfile(path) else None
        if current != content:
            stale.append(rel)
            if "--check" not in argv:
                io.open(path, "w", encoding="utf-8", newline="\n").write(content)
                print("wrote", rel)
    print("%d characters with a portrait, %d victory points" % (len(people), len(points)))
    return 1 if ("--check" in argv and stale) else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
