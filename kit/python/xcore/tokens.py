"""theme/tokens.json and theme/backdrops.json, plus the small colour maths both engines agree on."""

from __future__ import annotations

import json

from .paths import THEME

TOKENS: dict = json.loads((THEME / "tokens.json").read_text())
BACKDROPS: dict = json.loads((THEME / "backdrops.json").read_text())


def color(name: str) -> str:
    """Hex for a token path such as "blue", "grey.b" or a role such as "focus"."""
    role = TOKENS["role"].get(name)
    if isinstance(role, str) and name != "notes":
        name = role
    node = TOKENS["color"]
    for part in name.split("."):
        node = node[part]
    if not isinstance(node, str):
        raise KeyError(f"{name!r} is a group of colours, not one colour")
    return node


def rgb(hex_color: str) -> tuple[int, int, int]:
    h = hex_color.lstrip("#")
    return int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)


def to_hex(r: float, g: float, b: float) -> str:
    return "#{:02X}{:02X}{:02X}".format(*(max(0, min(255, round(v))) for v in (r, g, b)))


def mix(base: str, top: str, amount: float) -> str:
    """`top` laid over `base` at `amount` (0..1), in sRGB: the solid tint used for fills.

    Both engines mix the same way (kit/remotion/theme.ts `mix`), so a tinted fill is the same
    colour on either side of an engine switch.
    """
    a, b = rgb(base), rgb(top)
    return to_hex(*(a[i] + (b[i] - a[i]) * amount for i in range(3)))


def luminance(hex_color: str) -> float:
    def lin(v: int) -> float:
        c = v / 255
        return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4

    r, g, b = (lin(v) for v in rgb(hex_color))
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast(a: str, b: str) -> float:
    """WCAG contrast ratio between two colours (1..21)."""
    la, lb = luminance(a), luminance(b)
    hi, lo = max(la, lb), min(la, lb)
    return (hi + 0.05) / (lo + 0.05)


def type_px(name: str) -> float:
    return float(TOKENS["type"][name])


def typst_size(px: float) -> float:
    """Typst / Manim font_size that gives an em of `px` pixels at 1080p."""
    return px / TOKENS["font"]["typst_px_per_font_size"]


def stroke_width(px: float) -> float:
    """Manim stroke_width that draws `px` pixels wide at 1080p."""
    return px / TOKENS["stroke"]["manim_px_per_stroke_width"]


def units(px: float) -> float:
    """1080p pixels to Manim units (135 px per unit)."""
    return px / TOKENS["layout"]["unit_px"]


def px(units_: float) -> float:
    return units_ * TOKENS["layout"]["unit_px"]
