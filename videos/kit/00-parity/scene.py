import json
from pathlib import Path

from xkit import *
from xcore import tokens as tk

# The Manim half of the engine parity card (see README.md in videos/kit). CardR.tsx draws the same
# card from the same card.json; `./x parity` measures the two against each other.

CARD = json.loads((Path(__file__).parent / "card.json").read_text())
SIZES = {"title": TITLE, "label": LABEL, "body": BODY, "small": SMALL, "tiny": TINY}
WIDTHS = {"hair": W_HAIR, "thin": W_THIN, "shape": W_SHAPE, "hero": W_HERO, "arrow": W_ARROW}
MAKE = {"serif": T, "mono": mono, "sans": sans}


def at(x, y):
    """Canvas pixels (origin top left, y down) to Manim units."""
    return np.array([(x - 960) / UNIT_PX, (540 - y) / UNIT_PX, 0.0])


class CardM(Segment):
    audit = False  # a test card packs things closer than a picture ever would

    def construct(self):
        self.beat("Manim")
        for row, fill in (("patch", lambda c: ManimColor(tk.color(c))), ("tint", lambda c: tint(tk.color(c), CARD["tint"]["amount"]))):
            spec = CARD[row]
            for k, name in enumerate(CARD["colors"]):
                rect = Rectangle(width=spec["w"] / UNIT_PX, height=spec["h"] / UNIT_PX, stroke_width=0,
                                 fill_color=fill(name), fill_opacity=1)
                self.add(rect.move_to(at(spec["x0"] + k * spec["dx"] + spec["w"] / 2, spec["y"] + spec["h"] / 2)))
        for item in CARD["text"]:
            text = MAKE[item["family"]](item["text"], SIZES[item["size"]])
            origin = at(item["x"], item["y"])
            text.shift(RIGHT * (origin[0] - text.get_left()[0]) + UP * (origin[1] - baseline(text)))
            self.add(text)
        for item in CARD["strokes"]:
            self.add(Line(at(item["x1"], item["y"]), at(item["x2"], item["y"]), color=WHITE, stroke_width=WIDTHS[item["name"]]))
        self.finish()
