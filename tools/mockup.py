"""Helpers for design mock-ups: draw the game's sprites and fonts, and paste pieces of a reference capture,
onto a canvas. A mock-up script imports this module and composes a proposal before any .gui file exists
(wiki/Design-Rules.md, "Recipe for a screen phase", step 2).

    import sys; sys.path.insert(0, "tools")
    from mockup import Mockup
    m = Mockup("reference/vanilla/production.jpg", panel="reference/vanilla/production-panel.png")
    m.sprite("GFX_tiled_plain_bg", 0, 80, 1044, 1360)        # any sprite, at its size or a given one
    m.text("hoi_36header", 45, 86, "Production")              # a game font; colour codes and text icons work
    m.paste(m.cut((16, 76, 512, 112)), 12, 140)               # a piece of the panel capture, at 1:1
    m.save("scratch/mockups/production.png", crop=(0, 60, 1100, 1440))

Pieces cut from a capture keep what the code draws there (pictures, portraits, values); sprites and
fonts come from the game files through the renderer, so a mock-up looks like the game at 1:1.
"""
import os
import sys

from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import guiparse  # noqa: E402
from render_gui import Rect, Renderer  # noqa: E402

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class Mockup:
    def __init__(self, frame, panel=None, game_dir=None):
        """`frame`: the image to draw on, usually a reference capture of the whole screen. `panel`: an
        optional second image to cut pieces from (a lossless panel capture)."""
        self.renderer = Renderer(guiparse.find_game_dir(game_dir), options={"vanilla": False})
        self.canvas = Image.open(os.path.join(REPO_ROOT, frame)).convert("RGBA")
        self.source = Image.open(os.path.join(REPO_ROOT, panel)).convert("RGBA") if panel else self.canvas.copy()

    def sprite(self, name, x, y, width=None, height=None, frame=1):
        """Draw a sprite at (x, y); a tiled sprite takes the given size."""
        return self.renderer.draw_sprite(self.canvas, self.renderer.sprite(name), Rect(x, y, width, height), frame=frame)

    def texture(self, name):
        """The sprite's texture as an image (a portrait, a hull picture), to resize or paste."""
        return self.renderer.texture(self.renderer.sprite(name))

    def text(self, font, x, y, text):
        self.renderer.draw_text_line(self.canvas, self.renderer.font(font), x, y, text, None)

    def text_width(self, font, text):
        return self.renderer.text_width(self.renderer.font(font), text)

    def cut(self, box):
        """A piece (left, top, right, bottom) of the source capture."""
        return self.source.crop(box)

    def paste(self, image, x, y):
        self.canvas.alpha_composite(image.convert("RGBA"), (int(x), int(y)))

    def save(self, path, crop=None):
        path = os.path.join(REPO_ROOT, path)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        image = self.canvas.crop(crop) if crop else self.canvas
        image.convert("RGB").save(path)
        return path
