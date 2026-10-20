"""The layout file of a phase: one JSON file that both the mock-up (tools/mockup.py) and the override file
(tools/apply_layout.py) are made from, so the design is written once and the build cannot drift from it.
The shape is given in wiki/Workflow.md, "Handoff files"; the design language it draws is in wiki/Design-Language.md.

    import layout
    lay = layout.load("scratch/phases/A10/layout.json")
    for window in lay["windows"]:
        for item in layout.items(window):      # repeats expanded, names and keys filled in
            ...

A layout names a phase (`id`), a prefix for the widgets and sprites it adds (`prefix`: widgets `mod1440_<prefix>_*`,
sprites `GFX_1440p_<PREFIX>_*`), the override file, the scene, the capture the mock-up is drawn on, and the windows.
A window is a guiedit path ("strategicairview", "strategicairview/details_wnd"), where it stands on the screen
(`at`, for the mock-up), its own position, size and background (for the file), the child after which the plates
are inserted (`after`), and its items, in drawing order, with x and y relative to the window:

  kind      what it is                                      file                        mock-up
  title     the title strip (header_bg.dds)                 iconType + tile sprite      the tile
  card      a card plate (tiled_plain_bg_small.dds)         iconType + tile sprite      the tile
  head      a head bar (tiled_header_1.dds)                 iconType + tile sprite      the tile
  bands     the bands of a table: one plate per even row    iconType per band + sprite  the tiles
            (x, y, w, row, rows; `every` = 2)
  plate     a plate on a texture (texture, border) or on    iconType (+ tile sprite)    the tile or the sprite
            an existing sprite (sprite)
  caption   a text of the mod (key, text, font, w, h,       instantTextboxType          the text
            format)
  move      a vanilla widget at its new place (path, x, y,  position, size or maxWidth, the sample text or the
            w, h, font, format, fixed, sprite, sample, set) font, sprite, fixedsize     sprite, when given
  text      a sample text (font, text, w, align)            -                           the text
  sprite    a sprite (name, frame, w, h)                    -                           the sprite
  paste     a piece of the panel capture (box, x, y)        -                           the piece

Any item may carry `repeat`: {"var": "n", "range": [1, 12]} or {"var": "n", "values": [...]}, with `dx` and `dy`
per step; "{n}" and "{i}" (0-based) in `path`, `name`, `key`, `text`, `sample` are filled in, and a list under
`texts`, `samples` or `keys` gives one value per step. An item may carry its own `after` (the plates of a chart go after the
chart's background, not after the window's).
"""
import json
import os
import re

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# The tiles of the card style (wiki/Design-Language.md): texture and border of each plate kind.
PLATES = {
    "title": ("gfx/interface/header_bg.dds", (61, 21)),
    "card": ("gfx/interface/tiles/tiled_plain_bg_small.dds", (16, 16)),
    "head": ("gfx/interface/tiles/tiled_header_1.dds", (8, 8)),
    "bands": ("gfx/interface/tiles/black_bg_tile.dds", (3, 3)),
}
PLATE_KINDS = ("title", "card", "head", "bands", "plate")
TEXT_KINDS = ("caption", "text")
KINDS = PLATE_KINDS + TEXT_KINDS + ("move", "sprite", "paste")
FORMATS = ("left", "center", "centre", "right")


class LayoutError(Exception):
    pass


def load(path):
    """The layout, checked: every item has a known kind and the fields its kind needs."""
    with open(path, encoding="utf-8") as handle:
        lay = json.load(handle)
    for key in ("id", "prefix", "windows"):
        if key not in lay:
            raise LayoutError("%s: no %r" % (path, key))
    if not re.match(r"^[a-z][a-z0-9]*$", lay["prefix"]):
        raise LayoutError("%s: the prefix is lower-case letters and digits (%r)" % (path, lay["prefix"]))
    for window in lay["windows"]:
        if "path" not in window:
            raise LayoutError("%s: a window has no path" % path)
        for item in window.get("items", []):
            _check(item, window["path"], path)
    return lay


def _check(item, window, path):
    kind = item.get("kind")
    where = "%s: %s" % (path, window)
    if kind not in KINDS:
        raise LayoutError("%s: unknown kind %r (one of %s)" % (where, kind, ", ".join(KINDS)))
    need = {
        "title": ("name", "x", "y", "w", "h"), "card": ("name", "x", "y", "w", "h"), "head": ("name", "x", "y", "w", "h"),
        "bands": ("name", "x", "y", "w", "row", "rows"), "plate": ("name", "x", "y"),
        "caption": ("name", "x", "y", "w", "key"), "move": ("path",), "text": ("font", "x", "y"),
        "sprite": ("name", "x", "y"), "paste": ("box", "x", "y"),
    }[kind]
    lists = {"key": "keys", "text": "texts", "sample": "samples"}
    for key in need:
        if key not in item and not (item.get("repeat") and lists.get(key) in item):
            raise LayoutError("%s: a %s item needs %r (%s)" % (where, kind, key, json.dumps(item)[:80]))
    if kind == "plate" and "sprite" not in item and not ("texture" in item and "w" in item and "h" in item):
        raise LayoutError("%s: a plate names a sprite, or a texture with w and h (%s)" % (where, item["name"]))
    if item.get("format", "left") not in FORMATS:
        raise LayoutError("%s: format %r" % (where, item.get("format")))


def items(window):
    """The window's items with every `repeat` expanded, in drawing order."""
    out = []
    for item in window.get("items", []):
        rep = item.get("repeat")
        if not rep:
            out.append(dict(item))
            continue
        var = rep.get("var", "n")
        values = rep["values"] if "values" in rep else list(range(rep["range"][0], rep["range"][1] + 1))
        for i, value in enumerate(values):
            step = dict(item)
            del step["repeat"]
            fill = {var: value, "i": i}
            for key in ("path", "name", "key", "text", "sample"):
                if isinstance(step.get(key), str):
                    step[key] = _fill(step[key], fill)
            if "texts" in step:
                step["text"] = step["texts"][i] if i < len(step["texts"]) else ""
            if "samples" in step:
                step["sample"] = step["samples"][i] if i < len(step["samples"]) else ""
            if "keys" in step:
                step["key"] = step["keys"][i] if i < len(step["keys"]) else ""
            step["x"] = step.get("x", 0) + rep.get("dx", 0) * i
            step["y"] = step.get("y", 0) + rep.get("dy", 0) * i
            out.append(step)
    return out


def _fill(text, values):
    for key, value in values.items():
        text = text.replace("{%s}" % key, str(value))
    return text


def widget_name(lay, item):
    """mod1440_<prefix>_<name>"""
    return "mod1440_%s_%s" % (lay["prefix"], item["name"])


def sprite_name(lay, item):
    """GFX_1440p_<PREFIX>_<name>, or the existing sprite the item names."""
    if item["kind"] == "plate" and "sprite" in item:
        return item["sprite"]
    return "GFX_1440p_%s_%s" % (lay["prefix"].upper(), item["name"])


def plate_texture(item):
    """(texture path, (border x, border y)) of a plate kind, or None for a plate on an existing sprite."""
    if item["kind"] == "plate":
        if "sprite" in item:
            return None
        return item["texture"], tuple(item.get("border", (0, 0)))
    return PLATES[item["kind"]]


def plate_size(item):
    if item["kind"] == "bands":
        return item["w"], item["row"]
    return item["w"], item["h"]


def band_rows(item):
    """(row number from 1, y) of every band of a `bands` item: the even rows unless `every` says otherwise."""
    every = item.get("every", 2)
    first = item.get("first", every)      # the first banded row, counted from 1
    return [(n, item["y"] + item["row"] * (n - 1)) for n in range(first, item["rows"] + 1, every)]


def plate_declarations(lay):
    """One (sprite name, texture, border, (w, h)) per sprite the layout declares, in the order they first appear."""
    seen = {}
    for window in lay["windows"]:
        for item in items(window):
            if item["kind"] not in PLATE_KINDS:
                continue
            tex = plate_texture(item)
            if tex is None:
                continue
            name = sprite_name(lay, item)
            size = plate_size(item)
            if name in seen and seen[name][2] != size:
                raise LayoutError("%s is declared at two sizes: %s and %s" % (name, seen[name][2], size))
            seen.setdefault(name, (tex[0], tex[1], size))
    return [(name, tex, border, size) for name, (tex, border, size) in seen.items()]


def window_screen_origin(window):
    at = window.get("at", (0, 0))
    return int(at[0]), int(at[1])
