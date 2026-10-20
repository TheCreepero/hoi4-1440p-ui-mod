"""Apply a phase's layout file to its override file: the same numbers the mock-up was drawn from
(tools/mockup.py), so the build cannot drift from the design. wiki/Workflow.md, "Handoff files", gives the shape.

    python -I tools/apply_layout.py scratch/phases/A10/layout.json
    python -I tools/apply_layout.py scratch/phases/A10/layout.json --compare interface/zz_1440p_air_region.gui

What it does, per window of the layout:
  - sets the window's position, size and background sprite;
  - removes the plates and captions it made on an earlier run (every direct child named mod1440_<prefix>_*), then
    inserts them again right after the anchor child (`after`, by default the window's background), so they draw
    under every vanilla widget and every widget the code looks up stays a direct child of its vanilla parent;
  - moves the vanilla widgets of the `move` items: position, size or maxWidth/maxHeight, font, format, fixedsize,
    sprite, and any raw key under `set`;
  - declares the plates' sprites between "# --- <id> layout ---" markers inside the "# --- <id> ---" block of
    interface/1440p_ui.gfx (made when missing);
  - writes the `sample` texts of the `move` items into tools/scenes/<scene>.json when the scene exists.

Absolute values, so a second run changes nothing. --compare reads a file instead and reports every widget whose
place differs from the layout (exit 1 when any does): the gate the builder and the orchestrator run.
What the layout cannot say (new textures, progress bars, lists, a sprite the code sets) stays the builder's work.
"""
import argparse
import io
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import guiedit  # noqa: E402
import layout as layoutmod  # noqa: E402

REPO_ROOT = layoutmod.REPO_ROOT
TEXT_KINDS = ("instanttextboxtype", "textboxtype", "editboxtype")


def repo_path(path):
    return path if os.path.isabs(path) else os.path.join(REPO_ROOT, path)


# ---------------------------------------------------------------- blocks the tool writes
def icon_block(ind, name, sprite, x, y):
    return (ind + "iconType = {\n" + ind + '\tname = "%s"\n' % name + ind + '\tspriteType = "%s"\n' % sprite
            + ind + "\tposition = { x = %d y = %d }\n" % (x, y) + ind + "\talwaystransparent = yes\n" + ind + "}")


def caption_block(ind, name, key, x, y, w, h, font, fmt):
    fmt = "center" if fmt == "centre" else fmt
    return (ind + "instantTextboxType = {\n" + ind + '\tname = "%s"\n' % name + ind + "\tposition = { x = %d y = %d }\n" % (x, y)
            + ind + '\tfont = "%s"\n' % font + ind + '\ttext = "%s"\n' % key + ind + "\tmaxWidth = %d\n" % w
            + ind + "\tmaxHeight = %d\n" % h + ind + "\tformat = %s\n" % fmt + ind + "\talwaystransparent = yes\n" + ind + "}")


def sprite_block(name, texture, border, size):
    lines = ["\tcorneredTileSpriteType = {", '\t\tname = "%s"' % name, "\t\tsize = { x = %d y = %d }" % size,
             '\t\ttextureFile = "%s"' % texture, "\t\tborderSize = { x = %d y = %d }" % tuple(border), "\t\ttilingCenter = yes"]
    if border != (0, 0):
        lines.append('\t\teffectFile = "gfx/FX/buttonstate_nodowneffect.lua"')
    lines.append("\t}")
    return "\n".join(lines)


def tool_blocks(lay, item, ind):
    """The .gui blocks of one plate or caption item (a bands item gives one per band)."""
    kind = item["kind"]
    name = layoutmod.widget_name(lay, item)
    if kind == "bands":
        sprite = layoutmod.sprite_name(lay, item)
        return [(name + "_%d" % n, icon_block(ind, name + "_%d" % n, sprite, item["x"], y)) for n, y in layoutmod.band_rows(item)]
    if kind in layoutmod.PLATE_KINDS:
        return [(name, icon_block(ind, name, layoutmod.sprite_name(lay, item), item["x"], item["y"]))]
    if kind == "caption":
        return [(name, caption_block(ind, name, item["key"], item["x"], item["y"], item["w"], item.get("h", 24),
                                     item.get("font", "hoi_18mbs"), item.get("format", "left")))]
    return []


# ---------------------------------------------------------------- the file
class Applier:
    def __init__(self, lay, gui_path):
        self.lay = lay
        self.gui = guiedit.GuiFile(gui_path)
        self.notes = []
        self.prefix = "mod1440_%s_" % lay["prefix"]

    def note(self, text):
        self.notes.append(text)

    def widget(self, path):
        steps = [s for s in path.split("/") if s]
        return self.gui.window(steps[0]).at("/".join(steps[1:]))

    def container_span(self, path):
        steps = [s for s in path.split("/") if s]
        return self.gui._span(steps[0], steps[1:])

    def children(self, path):
        start, end = self.container_span(path)
        return self.gui._children(start, end)

    def apply(self):
        for window in self.lay["windows"]:
            self.apply_window(window)
        return self

    def apply_window(self, window):
        path = window["path"]
        w = self.widget(path)
        if "position" in window:
            self.set_position(w, window["position"][0], window["position"][1])
        if "size" in window:
            self.set_size(w, window["size"][0], window["size"][1])
        if window.get("background"):
            self.set_background(path, window["background"])
        self.remove_tool_children(path)
        groups = {}
        for item in layoutmod.items(window):
            if item["kind"] in layoutmod.PLATE_KINDS or item["kind"] == "caption":
                groups.setdefault(item.get("after", window.get("after")), []).append(item)
        for anchor, group in groups.items():
            self.insert_after(path, anchor, group)
        for item in layoutmod.items(window):
            if item["kind"] == "move":
                self.apply_move(w, item)

    # ---- the window itself
    def set_position(self, w, x, y):
        if w.has("position"):
            w.set("position", x=x, y=y)
        else:
            w.add("position = { x = %d y = %d }" % (x, y))

    def set_size(self, w, width, height):
        if w.get("size", "width") is not None:
            w.set("size", width=width, height=height)
        elif w.get("size", "x") is not None:
            w.set("size", x=width, y=height)
        elif w.has("size"):
            raise guiedit.GuiEditError("%s: size has neither width nor x" % w._label())
        else:
            w.add("size = { width = %d height = %d }" % (width, height))

    def background_child(self, path):
        for name, key, a, b in self.children(path):
            if key.lower() == "background":
                return name, a, b
        return None

    def set_background(self, path, sprite):
        found = self.background_child(path)
        if not found:
            self.note("%s: no background block; the sprite %s was not set" % (path, sprite))
            return
        name, a, b = found
        text = self.gui.text
        body = text[a:b]
        # a plain background (spriteType with a position) becomes a tiled one that fills the window
        body = re.sub(r"(?im)^[ \t]*position\s*=\s*\{[^}]*\}[ \t]*\r?\n", "", body)
        if re.search(r"(?i)quadTextureSprite\s*=", body):
            body = re.sub(r'(?i)(quadTextureSprite\s*=\s*)"[^"]*"', lambda m: m.group(1) + '"%s"' % sprite, body, count=1)
        elif re.search(r"(?i)spriteType\s*=", body):
            body = re.sub(r'(?i)spriteType\s*=\s*"[^"]*"[ \t]*', 'quadTextureSprite = "%s"' % sprite, body, count=1)
        else:
            body = body.replace("{", '{\n\t\t\tquadTextureSprite = "%s"' % sprite, 1)
        self.gui.text = text[:a] + body + text[b:]

    # ---- the tool's own blocks
    def remove_tool_children(self, path):
        for name, _key, a, b in reversed(self.children(path)):
            if not (name or "").startswith(self.prefix):
                continue
            text = self.gui.text
            key_at = text.rfind("\n", 0, a)
            # the key line may be the line of the "{" or the one before it
            line_start = key_at + 1
            if not re.search(r"[A-Za-z_]\w*\s*=", text[line_start:a]):
                line_start = text.rfind("\n", 0, key_at) + 1
            line_end = text.find("\n", b)
            line_end = len(text) if line_end < 0 else line_end + 1
            self.gui.text = text[:line_start] + text[line_end:]

    def insert_after(self, path, anchor, items):
        kids = self.children(path)
        if anchor is None:
            hit = [k for k in kids if k[1].lower() == "background"]
        else:
            hit = [k for k in kids if k[0] == anchor]
        if not hit:
            raise guiedit.GuiEditError("%s: no child %r to insert the plates after" % (path, anchor or "background"))
        _name, _key, a, b = hit[0]
        text = self.gui.text
        line_start = text.rfind("\n", 0, a) + 1
        key_line = text[line_start:a]
        if not re.search(r"[A-Za-z_]\w*\s*=", key_line):
            line_start = text.rfind("\n", 0, line_start - 1) + 1
            key_line = text[line_start:]
        ind = re.match(r"[ \t]*", key_line).group(0)
        blocks = []
        for item in items:
            blocks += [block for _n, block in tool_blocks(self.lay, item, ind)]
        self.gui.text = text[:b] + "".join("\n" + block for block in blocks) + text[b:]

    # ---- the vanilla widgets
    def apply_move(self, w, item):
        target = w.at(item["path"])
        kind = target.kind().lower()
        if "x" in item or "y" in item:
            x = item.get("x", target.get("position", "x"))
            y = item.get("y", target.get("position", "y"))
            if x is None or y is None:
                raise guiedit.GuiEditError("%s: give both x and y, it has no position yet" % target._label())
            self.set_position(target, int(float(x)), int(float(y)))
        if "w" in item or "h" in item:
            self.set_extent(target, kind, item)
        if "font" in item:
            target.put("buttonFont" if "button" in kind else "font", '"%s"' % item["font"])
        if "format" in item:
            target.put("format", "center" if item["format"] == "centre" else item["format"])
        if item.get("fixed"):
            target.put("fixedsize", "yes")
        if "sprite" in item:
            self.set_sprite(target, kind, item["path"], item["sprite"])
        for key, value in item.get("set", {}).items():
            target.put(key, value)

    def set_extent(self, target, kind, item):
        if kind in TEXT_KINDS:
            if "w" in item:
                target.put("maxWidth", int(item["w"]))
            if "h" in item:
                target.put("maxHeight", int(item["h"]))
            return
        width = item.get("w", target.get("size", "width") or target.get("size", "x"))
        height = item.get("h", target.get("size", "height") or target.get("size", "y"))
        if width is None or height is None:
            self.note("%s: a %s has no size to change; give both w and h" % (target._label(), kind))
            return
        if target.has("size"):
            self.set_size(target, int(float(width)), int(float(height)))
        elif kind == "containerwindowtype":
            target.add("size = { width = %d height = %d }" % (int(float(width)), int(float(height))))
        else:
            target.add("size = { x = %d y = %d }" % (int(float(width)), int(float(height))))

    def set_sprite(self, target, kind, path, sprite):
        if kind == "containerwindowtype":
            steps = [s for s in path.split("/") if s]
            self.set_background("/".join([target.window] + target.steps), sprite)
            return
        key = "quadTextureSprite" if target.has("quadTextureSprite") else "spriteType"
        target.put(key, '"%s"' % sprite)

    def save(self):
        self.gui.save()


# ---------------------------------------------------------------- the sprites
def gfx_block_text(lay):
    decls = layoutmod.plate_declarations(lay)
    label = lay.get("gfxBlock", lay["id"])
    lines = ["\t# --- %s layout ---" % label,
             "\t# Written by tools/apply_layout.py from the layout file; the plates of the card style. Edit the layout, not this."]
    for name, texture, border, size in decls:
        lines.append("")
        lines.append(sprite_block(name, texture, border, size))
    lines.append("\t# --- end %s layout ---" % label)
    return "\n".join(lines)


def write_gfx(lay, gfx_path):
    text = io.open(gfx_path, encoding="utf-8", newline="").read()
    newline = "\r\n" if "\r\n" in text else "\n"
    text = text.replace("\r\n", "\n")
    label = lay.get("gfxBlock", lay["id"])
    block = gfx_block_text(lay)
    inner = re.compile(r"[ \t]*# --- %s layout ---.*?# --- end %s layout ---" % (re.escape(label), re.escape(label)), re.S)
    if inner.search(text):
        text = inner.sub(lambda m: block, text, count=1)
    else:
        end = re.search(r"(?m)^[ \t]*# --- end %s ---[ \t]*$" % re.escape(label), text)
        if end:
            text = text[:end.start()] + block + "\n\n" + text[end.start():]
        else:
            close = text.rstrip().rfind("}")
            text = (text[:close].rstrip("\n") + "\n\n\t# --- %s ---\n" % label + block + "\n\t# --- end %s ---\n" % label + text[close:])
    io.open(gfx_path, "w", encoding="utf-8", newline="").write(text.replace("\n", newline))


# ---------------------------------------------------------------- the scene
def write_scene_samples(lay, scene_path):
    samples = {}
    for window in lay["windows"]:
        for item in layoutmod.items(window):
            if item["kind"] == "move" and item.get("sample"):
                samples[item["path"].split("/")[-1]] = item["sample"]
    if not samples or not os.path.isfile(scene_path):
        return 0
    with open(scene_path, encoding="utf-8") as handle:
        scene = json.load(handle)
    star = scene.setdefault("samples", {}).setdefault("*", {})
    changed = 0
    for name, value in samples.items():
        if star.get(name) != value:
            star[name] = value
            changed += 1
    if changed:
        with open(scene_path, "w", encoding="utf-8", newline="\n") as handle:
            json.dump(scene, handle, indent=2)
            handle.write("\n")
    return changed


# ---------------------------------------------------------------- compare
def compare(lay, gui_path):
    """Every widget of the layout whose place in the file differs: [(widget, what, layout value, file value)]."""
    gui = guiedit.GuiFile(gui_path)
    diffs = []

    def widget(path):
        steps = [s for s in path.split("/") if s]
        return gui.window(steps[0]).at("/".join(steps[1:]))

    def check(target, what, key, component, wanted):
        try:
            got = target.get(key, component)
        except guiedit.GuiEditError as error:
            diffs.append((target._label(), what, wanted, "missing: %s" % error))
            return
        if got is None or str(got).strip('"') != str(wanted):
            diffs.append((target._label(), what, wanted, got))

    for window in lay["windows"]:
        w = widget(window["path"])
        if "position" in window:
            check(w, "position", "position", "x", window["position"][0])
            check(w, "position", "position", "y", window["position"][1])
        if "size" in window:
            check(w, "size", "size", "width", window["size"][0])
            check(w, "size", "size", "height", window["size"][1])
        for item in layoutmod.items(window):
            kind = item["kind"]
            if kind in layoutmod.PLATE_KINDS or kind == "caption":
                for name, _block in tool_blocks(lay, item, ""):
                    try:
                        t = w.at(name)
                        t.kind()
                    except guiedit.GuiEditError:
                        diffs.append((window["path"] + "/" + name, "exists", "yes", "no"))
                        continue
                    y = item["y"] if kind != "bands" else int(name.rsplit("_", 1)[1])
                    if kind == "bands":
                        y = dict(layoutmod.band_rows(item))[y]
                    check(t, "position", "position", "x", item["x"])
                    check(t, "position", "position", "y", y)
            elif kind == "move":
                try:
                    t = w.at(item["path"])
                    tk = t.kind().lower()
                except guiedit.GuiEditError:
                    diffs.append((window["path"] + "/" + item["path"], "exists", "yes", "no"))
                    continue
                if "x" in item:
                    check(t, "position", "position", "x", item["x"])
                if "y" in item:
                    check(t, "position", "position", "y", item["y"])
                if "w" in item:
                    if tk in TEXT_KINDS:
                        check(t, "maxWidth", "maxWidth", None, item["w"])
                    elif t.get("size", "width") is not None:
                        check(t, "size", "size", "width", item["w"])
                    elif t.get("size", "x") is not None:
                        check(t, "size", "size", "x", item["w"])
                if "font" in item:
                    check(t, "font", "buttonFont" if "button" in tk else "font", None, item["font"])
    return diffs


def main(argv=None):
    parser = argparse.ArgumentParser(description="Apply a layout file to an override file, or compare one with it.")
    parser.add_argument("layout")
    parser.add_argument("--gui", help="the override file (default: the layout's `file`)")
    parser.add_argument("--gfx", default="interface/1440p_ui.gfx")
    parser.add_argument("--scene", help="the scene file (default: tools/scenes/<scene>.json of the layout)")
    parser.add_argument("--no-gfx", action="store_true")
    parser.add_argument("--no-scene", action="store_true")
    parser.add_argument("--compare", metavar="GUI", help="report where this file differs from the layout; write nothing")
    args = parser.parse_args(argv)

    lay = layoutmod.load(repo_path(args.layout))
    if args.compare:
        diffs = compare(lay, repo_path(args.compare))
        for widget, what, wanted, got in diffs:
            print("%s: %s is %s, the layout says %s" % (widget, what, got, wanted))
        print("%d difference(s) between %s and %s" % (len(diffs), args.compare, args.layout))
        return 1 if diffs else 0

    gui_path = repo_path(args.gui or lay["file"])
    applier = Applier(lay, gui_path).apply()
    applier.save()
    print("wrote %s" % os.path.relpath(gui_path, REPO_ROOT))
    if not args.no_gfx and layoutmod.plate_declarations(lay):
        write_gfx(lay, repo_path(args.gfx))
        print("declared %d sprite(s) in %s" % (len(layoutmod.plate_declarations(lay)), args.gfx))
    if not args.no_scene:
        scene_path = repo_path(args.scene or os.path.join("tools", "scenes", lay.get("scene", "") + ".json"))
        if lay.get("scene") or args.scene:
            changed = write_scene_samples(lay, scene_path)
            if changed:
                print("%d sample(s) written to %s" % (changed, os.path.relpath(scene_path, REPO_ROOT)))
            elif not os.path.isfile(scene_path):
                print("no scene file %s yet: the samples wait for it" % os.path.relpath(scene_path, REPO_ROOT))
    for note in applier.notes:
        print("note: " + note)
    diffs = compare(lay, gui_path)
    if diffs:
        for widget, what, wanted, got in diffs:
            print("not applied: %s: %s is %s, the layout says %s" % (widget, what, got, wanted))
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
