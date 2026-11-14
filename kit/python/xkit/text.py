"""Type. Everything is set by Typst in Latin Modern (the OpenType Computer Modern), from the same
font files Remotion loads, so a word looks identical on either side of an engine switch.

    T("Language model")                      one line: labels, titles, numbers
    T("wrong", color=RED, weight="bold")
    mono("loss.backward()")                  Computer Modern Typewriter
    paragraph("A long example ...", width=6) wrapped text that is content, not narration
    eq("{{ w : w }} arrow.l w - eta nabla L", colors={"w": BLUE})   math, parts coloured by name
"""

from __future__ import annotations

import json
import re

from manim import DOWN, LEFT, RIGHT, UP, MathTypst, Typst, VGroup, VMobject

from xcore.paths import FONTS
from xcore.tokens import TOKENS

from .theme import BODY, UNIT_PX, W_BACK, WHITE, stage

_FONT = TOKENS["font"]
_PATHS = [str(FONTS)]
_PX_PER_SIZE = _FONT["typst_px_per_font_size"]


def _lit(text: str) -> str:
    """A Typst string literal."""
    return json.dumps(text, ensure_ascii=False)


def curly(text: str) -> str:
    """Typewriter quotes to typographic ones: "it's" -> “it’s”."""
    text = re.sub(r"(?<=\w)'(?=\w)", "’", text)  # apostrophes inside words
    text = re.sub(r'(^|[\s(\[{—–-])"', r"\1“", text).replace('"', "”")
    text = re.sub(r"(^|[\s(\[{—–-])'", r"\1‘", text).replace("'", "’")
    return text


# Every single line of text is given the same line box: its top edge sits _TOP em above the baseline,
# whatever the font. Manim reports where that top edge is, which is how baseline() finds the baseline.
_TOP = 0.8
_EDGES = f"top-edge: {_TOP}em, bottom-edge: -0.2em"
_TYPST_PT = 10  # Manim compiles Typst at 10 pt, so one em is 10 units of the frame it reports


def _tracked(kwargs: dict) -> None:
    """Ask Manim to record baselines, and to parse this text afresh: its SVG cache hands out copies
    of earlier objects that have lost that record (the same word in another colour is a cache hit)."""
    kwargs.setdefault("track_baselines", True)
    kwargs.setdefault("use_svg_cache", False)


def _preamble(family: str, weight: str, italic: bool, line: bool = True) -> str:
    style = ', style: "italic"' if italic else ""
    edges = f", {_EDGES}" if line else ""
    return f'#set text(font: "{_FONT[family]}", weight: "{weight}"{style}{edges})'


def T(text: str, size: float = BODY, color=WHITE, weight: str = "regular", italic: bool = False,
      family: str = "serif", smart: bool = True, **kwargs) -> Typst:
    """One line of text. `size` is one of HERO, TITLE, HEADING, LABEL, BODY, SMALL, TINY."""
    body = curly(text) if smart else text
    _tracked(kwargs)
    return Typst("#" + _lit(body), typst_preamble=_preamble(family, weight, italic), font_paths=_PATHS,
                 font_size=size, color=color, **kwargs)


def sans(text: str, size: float = BODY, color=WHITE, weight: str = "regular", **kwargs) -> Typst:
    """Computer Modern Sans: interface text (buttons, tabs) when a picture shows a product."""
    return T(text, size, color, weight, family="sans", **kwargs)


def mono(text: str, size: float = BODY, color=WHITE, weight: str = "regular", **kwargs) -> Typst:
    """Code and anything typed: Computer Modern Typewriter. Leading spaces are kept."""
    # raw text is set at 0.8 em by default; an absolute size puts it on the same em as the serif
    pre = f'#show raw: set text(font: "{_FONT["mono"]}", size: {_TYPST_PT}pt, weight: "{weight}", {_EDGES})'
    _tracked(kwargs)
    block = ", block: true" if "\n" in text else ""
    return Typst(f"#raw({_lit(text)}{block})", typst_preamble=pre, font_paths=_PATHS, font_size=size, color=color, **kwargs)


def paragraph(text: str, width: float, size: float = BODY, color=WHITE, align: str = "left",
              leading: float = 0.6, italic: bool = False, **kwargs) -> Typst:
    """Wrapped text `width` Manim units wide. For example text that is the subject (a prompt, a
    sentence being analysed). Narration is never put on screen."""
    width_em = width * UNIT_PX / (size * _PX_PER_SIZE)
    src = (f"#set par(leading: {leading}em)\n#set align({align})\n"
           f"#block(width: {width_em:.3f}em)[#{_lit(curly(text))}]")
    return Typst(src, typst_preamble=_preamble("serif", "regular", italic, line=False), font_paths=_PATHS,
                 font_size=size, color=color, **kwargs)


def eq(expr: str, size: float = BODY, color=WHITE, colors: dict | None = None, **kwargs) -> MathTypst:
    """Typst math. Name parts with {{ ... : name }} to colour them or move them between equations:

        eq("{{ w : w }} arrow.l {{ w : w0 }} - {{ eta : lr }} nabla L", colors={"w": BLUE, "lr": YELLOW})
        new.select("w")      # the part named w, e.g. for ReplacementTransform(old.select("w"), new.select("w"))

    Typst reminders: a^2, x_1, sqrt(x), a/b, sum_(k=1)^n, integral_a^b f(x) dif x, lim_(x -> 0),
    pi, infinity, times, dot, arrow.r, nabla, partial, RR, bold(v), "words in quotes".
    """
    mob = MathTypst(expr, font_size=size, color=color, font_paths=_PATHS, **kwargs)
    for key, col in (colors or {}).items():
        mob.select(key).set_color(col)
    return mob


def num(value: float, fmt: str = "{:,.0f}", size: float = BODY, color=WHITE, **kwargs) -> Typst:
    """A formatted number. Computer Modern digits are all one width, so columns line up."""
    return T(minus(fmt.format(value)), size, color, smart=False, **kwargs)


def minus(text: str) -> str:
    """A hyphen in front of a digit becomes a true minus sign, which is as wide as a plus."""
    return re.sub(r"-(?=[\d.])", "−", text)


def backstroke(mob: VMobject, width: float = W_BACK, color=None) -> VMobject:
    """An outline in the stage colour behind text, so it stays readable over lines and fills."""
    mob.set_stroke(stage() if color is None else color, width=width, background=True)
    return mob


def baseline(mob: VMobject) -> float:
    """The y of the line a piece of text sits on (its bottom edge, for anything that is not text).

    Manim reports, for each glyph of Typst output, a frame (origin, right, up) whose origin is the
    top of the glyph's line box and whose axes are one Typst point long, with "up" pointing down the
    page. T(), sans() and mono() fix that top edge at _TOP em above the baseline, so the baseline is
    _TOP em = _TOP * 10 points along the "up" axis from the origin. This holds after any move or scale.
    """
    if getattr(mob, "track_baselines", False):
        frames = mob.baseline_frames
        if not frames:
            raise RuntimeError("this text has lost its baseline record: create it with T(), sans() or mono()")
        origin, _, down = frames[0]
        return float(origin[1] + _TOP * _TYPST_PT * (down[1] - origin[1]))
    return float(mob.get_bottom()[1])


def align_baseline(mob: VMobject, to: VMobject) -> VMobject:
    """Move `mob` up or down so it sits on the same line as `to`."""
    return mob.shift(UP * (baseline(to) - baseline(mob)))


def baseline_row(*mobs: VMobject, buff: float = 0.25) -> VGroup:
    """Lay words out left to right on one shared baseline, centred on the origin.

    arrange() centres bounding boxes, which drops a word without descenders below its neighbours
    ("map" beside "ant"). Use this for token rows, lists of names and anything read as one line.
    """
    x = 0.0
    for m in mobs:
        m.shift(DOWN * baseline(m))
        m.shift(RIGHT * (x - m.get_left()[0]))
        x = m.get_right()[0] + buff
    row = VGroup(*mobs)
    row.shift(LEFT * row.get_center()[0])
    return row


__all__ = ["T", "sans", "mono", "paragraph", "eq", "num", "minus", "backstroke", "baseline", "align_baseline", "baseline_row", "curly"]
