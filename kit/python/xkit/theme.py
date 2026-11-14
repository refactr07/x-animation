"""The Blackboard style for Manim, read from theme/tokens.json.

`from xkit import *` replaces Manim's colour names with these, so `BLUE` or `YELLOW` in a scene is
always the house colour (Manim CE's own YELLOW is #F7D96F; ours is the pure #FFFF00 of the reference
look). Sizes are Typst font sizes, strokes are Manim stroke widths, lengths are Manim units.
"""

from __future__ import annotations

from manim import ManimColor, config, interpolate_color

from xcore import tokens as _t
from xcore.tokens import TOKENS

_c = TOKENS["color"]

# ------------------------------------------------------------------ palette
BG = ManimColor(_c["bg"])
BLACK = ManimColor("#000000")
WHITE = ManimColor(_c["text"])
GREY_A = ManimColor(_c["grey"]["a"])  # arrows, light strokes
GREY_B = ManimColor(_c["grey"]["b"])  # outlines of neutral things
GREY_C = ManimColor(_c["grey"]["c"])  # secondary labels, inactive words, axes
GREY_D = ManimColor(_c["grey"]["d"])  # guides, empty slots
GREY_E = ManimColor(_c["grey"]["e"])  # faint fills
GREY = GREY_C
BLUE = ManimColor(_c["blue"])
BLUE_LIGHT = ManimColor(_c["blue_light"])  # blue words: lighter, easier to read as text
BLUE_DEEP = ManimColor(_c["blue_deep"])
TEAL = ManimColor(_c["teal"])
TEAL_DEEP = ManimColor(_c["teal_deep"])  # fill of function boxes
GREEN = ManimColor(_c["green"])
YELLOW = ManimColor(_c["yellow"])
GOLD = ManimColor(_c["gold"])
ORANGE = ManimColor(_c["orange"])
RED = ManimColor(_c["red"])
PINK = ManimColor(_c["pink"])
PURPLE = ManimColor(_c["purple"])
RAMP = [ManimColor(h) for h in _c["ramp"]]  # low -> high value


def role(name: str) -> ManimColor:
    """Colour of a role from tokens.json ("subject", "focus", "wrong", ...)."""
    return ManimColor(_t.color(name))


# ------------------------------------------------------------------ type (Typst font sizes)
HERO, TITLE, HEADING, LABEL, BODY, SMALL, TINY = (
    _t.typst_size(TOKENS["type"][k]) for k in ("hero", "title", "heading", "label", "body", "small", "tiny")
)
MIN_TEXT_PX = TOKENS["type"]["min"]

# ------------------------------------------------------------------ strokes (Manim stroke widths)
W_ARROW, W_HERO, W_SHAPE, W_THIN, W_HAIR, W_BACK = (
    _t.stroke_width(TOKENS["stroke"][k]) for k in ("arrow", "hero", "shape", "thin", "hair", "backstroke")
)

# ------------------------------------------------------------------ layout (Manim units)
UNIT_PX = TOKENS["layout"]["unit_px"]
MARGIN_X = _t.units(TOKENS["layout"]["margin_x"])
MARGIN_Y = _t.units(TOKENS["layout"]["margin_y"])
GAP = _t.units(TOKENS["layout"]["gap"])  # an object to its label
SPACE = _t.units(TOKENS["layout"]["space"])  # between sibling objects
CLEARANCE = _t.units(TOKENS["layout"]["clearance"])  # the least gap between two objects
RADIUS = _t.units(TOKENS["radius"]["shape"])
PANEL_RADIUS = _t.units(TOKENS["radius"]["panel"])
FRAME_W = TOKENS["layout"]["frame_width_units"]
FRAME_H = TOKENS["layout"]["frame_height_units"]

# ------------------------------------------------------------------ motion (seconds)
_m = TOKENS["motion"]
MOVE, FAST, TRANSFORM, CAMERA, LAG, LEAD = (_m[k] for k in ("move", "fast", "transform", "camera", "lag", "lead"))


def px(pixels: float) -> float:
    """1080p pixels as Manim units."""
    return _t.units(pixels)


# ------------------------------------------------------------------ the stage
_stage = [ManimColor(_c["bg"])]


def set_stage(hex_color: str) -> None:
    """Called by Segment with the section's backdrop colour. Tints mix over it."""
    _stage[0] = ManimColor(hex_color)
    config.background_color = _stage[0]


def stage() -> ManimColor:
    return _stage[0]


def tint(color, amount: float | None = None) -> ManimColor:
    """A solid tint of `color` over the stage: the fill of every shape that carries a colour role.

    Solid, never translucent: a solid fill hides whatever line passes behind the shape.
    """
    return interpolate_color(_stage[0], ManimColor(color), TOKENS["tint"]["fill"] if amount is None else amount)


def ramp_color(p: float) -> ManimColor:
    """Colour for a value in 0..1: pale yellow (low) through green to teal (high)."""
    p = min(max(p, 0.0), 1.0) * (len(RAMP) - 1)
    i = min(int(p), len(RAMP) - 2)
    return interpolate_color(RAMP[i], RAMP[i + 1], p - i)


config.background_color = BG

__all__ = [
    "BG", "BLACK", "WHITE", "GREY_A", "GREY_B", "GREY_C", "GREY_D", "GREY_E", "GREY",
    "BLUE", "BLUE_LIGHT", "BLUE_DEEP", "TEAL", "TEAL_DEEP", "GREEN", "YELLOW", "GOLD", "ORANGE", "RED", "PINK", "PURPLE",
    "RAMP", "role", "HERO", "TITLE", "HEADING", "LABEL", "BODY", "SMALL", "TINY", "MIN_TEXT_PX",
    "W_ARROW", "W_HERO", "W_SHAPE", "W_THIN", "W_HAIR", "W_BACK",
    "UNIT_PX", "MARGIN_X", "MARGIN_Y", "GAP", "SPACE", "CLEARANCE", "RADIUS", "PANEL_RADIUS", "FRAME_W", "FRAME_H",
    "MOVE", "FAST", "TRANSFORM", "CAMERA", "LAG", "LEAD", "px", "set_stage", "stage", "tint", "ramp_color",
]
