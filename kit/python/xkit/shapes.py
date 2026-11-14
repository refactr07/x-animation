"""Themed building blocks: boxes, tokens, chips, arrows, highlights, axes, lists of numbers.

Shapes that carry a colour role are a full-strength stroke plus a solid tint of the same hue.
Neutral structure is grey. Colour lives on strokes, words and small fills; big areas stay dark.
"""

from __future__ import annotations

import numpy as np
from manim import (
    DOWN,
    LEFT,
    ORIGIN,
    PI,
    RIGHT,
    UP,
    Arrow,
    Axes,
    Brace,
    CapStyleType,
    Circle,
    CurvedArrow,
    Dot,
    Line,
    Mobject,
    Rectangle,
    RoundedRectangle,
    SurroundingRectangle,
    VGroup,
    VMobject,
)

from .layout import frames, named, parts_of
from .text import T, baseline, num
from .theme import (
    BLACK,
    BLUE,
    BODY,
    GAP,
    GREEN,
    GREY_A,
    GREY_B,
    GREY_C,
    GREY_D,
    PANEL_RADIUS,
    RADIUS,
    RED,
    SMALL,
    TINY,
    W_ARROW,
    W_HAIR,
    W_HERO,
    W_SHAPE,
    W_THIN,
    WHITE,
    YELLOW,
    ramp_color,
    stage,
    tint,
)


# ------------------------------------------------------------------ boxes and discs
def box(width: float = 2.0, height: float = 1.2, color=GREY_B, fill: float | None = None,
        radius: float = RADIUS, stroke: float = W_SHAPE) -> RoundedRectangle:
    """A rounded rectangle: stroke in `color`, solid tint of it inside (fill=0 for the bare stage)."""
    r = min(radius, width / 2 - 1e-3, height / 2 - 1e-3)
    return RoundedRectangle(width=width, height=height, corner_radius=r, color=color, stroke_width=stroke,
                            fill_color=tint(color, fill), fill_opacity=1)


def disc(radius: float = 0.5, color=BLUE, fill: float | None = None, stroke: float = W_SHAPE) -> Circle:
    """The subject of a picture as one solid-tint circle."""
    return Circle(radius=radius, color=color, stroke_width=stroke, fill_color=tint(color, fill), fill_opacity=1)


def ring(radius: float = 1.0, color=GREY_B, stroke: float = W_SHAPE) -> Circle:
    return Circle(radius=radius, color=color, stroke_width=stroke)


def dot(point=ORIGIN, color=WHITE, radius: float = 0.08) -> Dot:
    return Dot(point, radius=radius, color=color)


def panel(width: float = 5.0, height: float = 3.0, color=GREY_B) -> RoundedRectangle:
    """A framed screen for a picture inside the picture: stage-coloured, thin light outline."""
    return RoundedRectangle(width=width, height=height, corner_radius=PANEL_RADIUS, color=color,
                            stroke_width=W_THIN, fill_color=stage(), fill_opacity=1)


def rule(start, end, color=GREY_D) -> Line:
    """A thin divider between columns or halves of a split frame."""
    return Line(start, end, color=color, stroke_width=W_HAIR)


# ------------------------------------------------------------------ words in boxes
def token(text: str, color=BLUE, size: float = SMALL, pad_x: float = 0.16, pad_y: float = 0.12,
          text_color=WHITE, family: str = "serif") -> VGroup:
    """A word in a thin coloured box with a tint of the same hue: a token, a tag, an option.

    token.box and token.label are its parts. Rows of tokens share a height, so they line up.
    """
    label = T(text, size, text_color, family=family)
    line_box = T("Hg", size)  # every token is as tall as a full line, whatever letters it holds
    frame = RoundedRectangle(width=label.width + 2 * pad_x, height=line_box.height + 2 * pad_y,
                             corner_radius=0.06, color=color, stroke_width=W_THIN,
                             fill_color=tint(color, 0.22), fill_opacity=1)
    label.move_to(frame)
    label.shift(UP * (_baseline_fix(label, line_box)))
    group = parts_of(VGroup(frame, label))
    group.box, group.label = frame, label
    return named(group, f"token:{text}")


def _baseline_fix(label, line_box) -> float:
    """Shift that puts `label` where it would sit inside a centred full-height line of text."""
    return float((baseline(line_box) - line_box.get_center()[1]) - (baseline(label) - label.get_center()[1]))


def chip(text: str, color=YELLOW, size: float = SMALL, pad_x: float = 0.22, pad_y: float = 0.1,
         weight: str = "regular") -> VGroup:
    """A solid pill with dark text: a name tag for the thing it sits beside. Title Case, 1-3 words."""
    label = T(text, size, BLACK, weight=weight)
    line_box = T("Hg", size)
    h = line_box.height + 2 * pad_y
    pill = RoundedRectangle(width=label.width + 2 * pad_x + 0.1, height=h, corner_radius=h / 2 - 1e-3,
                            color=color, stroke_width=0, fill_color=color, fill_opacity=1)
    label.move_to(pill)
    label.shift(UP * _baseline_fix(label, line_box))
    group = parts_of(VGroup(pill, label))
    group.box, group.label = pill, label
    return named(group, f"chip:{text}")


def badge(text: str, color=WHITE, radius: float = 0.26, size: float = TINY) -> VGroup:
    """A small numbered circle: step 1, option A."""
    circle = Circle(radius=radius, color=color, stroke_width=W_THIN, fill_color=stage(), fill_opacity=1)
    label = T(text, size, color).move_to(circle)
    group = parts_of(VGroup(circle, label))
    return named(group, f"badge:{text}")


# ------------------------------------------------------------------ arrows and connectors
def arrow(start, end, color=GREY_A, width: float = W_ARROW, buff: float = 0.2, tip: float = 0.3) -> Arrow:
    """The house arrow: a thick light-grey shaft with a big head. `start` and `end` are points or
    mobjects (then it runs between their edges)."""
    return Arrow(start, end, buff=buff, color=color, stroke_width=width, tip_length=tip,
                 max_tip_length_to_length_ratio=0.5, max_stroke_width_to_length_ratio=20)


def thin_arrow(start, end, color=GREY_B, buff: float = 0.15) -> Arrow:
    """A size smaller, for dense rows and for arrows inside a diagram."""
    return arrow(start, end, color=color, width=W_SHAPE, buff=buff, tip=0.2)


def arc_arrow(start, end, angle: float = -PI / 3, color=WHITE, width: float = W_THIN, tip: float = 0.18) -> CurvedArrow:
    """A curved arrow: "this looks at that", "this feeds back into that"."""
    return CurvedArrow(np.asarray(start, dtype=float), np.asarray(end, dtype=float), angle=angle, color=color,
                       stroke_width=width, tip_length=tip)


def link(a: Mobject, b: Mobject, color=GREY_C, width: float = W_THIN, buff: float = 0.12) -> Line:
    """A plain line between the facing edges of two objects."""
    direction = b.get_center() - a.get_center()
    unit = direction / max(np.linalg.norm(direction), 1e-9)
    line = Line(a.get_boundary_point(unit) + unit * buff, b.get_boundary_point(-unit) - unit * buff,
                color=color, stroke_width=width)
    line.x_connector = True
    return line


# ------------------------------------------------------------------ pointing at things
def highlight_box(mob: Mobject, color=YELLOW, buff: float = 0.12, fill: float = 0.0) -> SurroundingRectangle:
    """The rectangle that says "look here"."""
    rect = SurroundingRectangle(mob, buff=buff, color=color, stroke_width=W_THIN, corner_radius=0.06)
    if fill:
        rect.set_fill(tint(color, fill), opacity=1)
    return frames(rect, mob)


def underline(mob: Mobject, color=YELLOW, buff: float = 0.1, width: float = W_SHAPE) -> Line:
    line = Line(mob.get_corner(DOWN + LEFT) + DOWN * buff, mob.get_corner(DOWN + RIGHT) + DOWN * buff,
                color=color, stroke_width=width)
    line.set_cap_style(CapStyleType.ROUND)
    return frames(line, mob)


def strike(mob: Mobject, color=RED, inset: float = 0.0, width: float = W_HERO) -> VGroup:
    """An X across a box or a picture: "it was not this". Play it as stagger([draw(x[0]), draw(x[1])], 0.3).
    For a word or a line of text use cross_out(), which leaves it readable."""
    ul, dr = mob.get_corner(UP + LEFT), mob.get_corner(DOWN + RIGHT)
    ur, dl = mob.get_corner(UP + RIGHT), mob.get_corner(DOWN + LEFT)
    k = (RIGHT + DOWN) * inset
    j = (LEFT + DOWN) * inset
    x = VGroup(Line(ul + k, dr - k), Line(ur + j, dl - j)).set_stroke(color, width)
    for part in x:
        part.set_cap_style(CapStyleType.ROUND)
    return frames(x, mob)


def cross_out(mob: Mobject, color=RED, width: float = W_SHAPE, overhang: float = 0.08) -> Line:
    """One line through a word: struck from the list, no longer true."""
    y = mob.get_center()[1]
    line = Line([mob.get_left()[0] - overhang, y, 0], [mob.get_right()[0] + overhang, y, 0], color=color, stroke_width=width)
    line.set_cap_style(CapStyleType.ROUND)
    return frames(line, mob)


def check(color=GREEN, size: float = 0.5, width: float = W_HERO) -> VMobject:
    """A tick: correct, done, working."""
    mark = VMobject(color=color, stroke_width=width)
    mark.set_points_as_corners([np.array(p) * size for p in ([-0.5, 0.0, 0], [-0.15, -0.35, 0], [0.5, 0.4, 0])])
    mark.set_cap_style(CapStyleType.ROUND)
    return named(mark, "check")


def cross(color=RED, size: float = 0.5, width: float = W_HERO) -> VGroup:
    """A small x: wrong, failed, removed."""
    h = size * 0.4
    x = VGroup(Line([-h, h, 0], [h, -h, 0]), Line([h, h, 0], [-h, -h, 0])).set_stroke(color, width)
    for part in x:
        part.set_cap_style(CapStyleType.ROUND)
    return named(parts_of(x), "cross")


def brace_label(mob: Mobject, text: str, direction=DOWN, color=GREY_B, size: float = SMALL, buff: float = 0.12) -> VGroup:
    """A brace along one side of something, with a short label."""
    brace = Brace(mob, direction=direction, buff=buff, color=color)
    label = T(text, size, color).next_to(brace, direction, buff=GAP * 0.6)
    group = VGroup(brace, label)
    group.brace, group.label = brace, label
    return group


# ------------------------------------------------------------------ plots
def axes(x_range=(0, 6, 1), y_range=(0, 4, 1), width: float = 7.0, height: float = 4.0, ticks: bool = True,
         color=GREY_C) -> Axes:
    """Clean axes: thin grey lines, small ticks, no numbers (add the few that matter with T())."""
    return Axes(
        x_range=list(x_range), y_range=list(y_range), x_length=width, y_length=height, tips=False,
        axis_config={"color": color, "stroke_width": W_THIN, "include_ticks": ticks, "tick_size": 0.06},
    )


def axis_label(ax: Axes, text: str, axis: str = "x", size: float = SMALL, color=GREY_C):
    """A name for an axis: at the right end of x, or above the top of y."""
    label = T(text, size, color)
    if axis == "x":
        return label.next_to(ax.x_axis.get_right(), DOWN, buff=GAP * 0.7).shift(LEFT * label.width / 2)
    return label.next_to(ax.y_axis.get_top(), UP, buff=GAP * 0.5)


# ------------------------------------------------------------------ numbers
def bar_list(rows: list[tuple[str, float]], scale: float = 2.2, size: float = SMALL, row_gap: float | None = None,
             bar_height: float | None = None, percent: bool = True, more: bool = False, relative: bool = True,
             number_size: float | None = None) -> VGroup:
    """Words with value bars: probabilities, scores, shares.

    `rows` is [(word, value 0..1), ...]. Words are right-aligned to one edge, bars grow right from
    it with length value x `scale` and a colour that follows the value, percentages sit at the
    bar ends. With relative=True the top row is always the strongest colour; with relative=False
    the colour shows the value itself, so a list of equally unsure guesses stays pale. The result's .rows holds VGroup(word, bar, number) per row; .words, .bars and
    .numbers hold the columns, so a scene can restack or rescale them.
    """
    top = max((v for _, v in rows), default=1.0) or 1.0
    line_h = T("Hg", size).height
    row_gap = 0.45 * line_h if row_gap is None else row_gap
    bar_height = 0.72 * line_h if bar_height is None else bar_height
    number_size = 0.78 * size if number_size is None else number_size
    out, words, bars, numbers = VGroup(), VGroup(), VGroup(), VGroup()
    for i, (word, value) in enumerate(rows):
        y = -i * (line_h + row_gap)
        label = T(word, size)
        label.move_to([-(label.width / 2) - 0.2, y, 0])
        bar = Rectangle(width=max(value * scale, 0.02), height=bar_height, stroke_width=0,
                        fill_color=ramp_color(value / top if relative else value), fill_opacity=1)
        bar.move_to([bar.width / 2, y, 0])
        row = VGroup(label, bar)
        if percent:
            pct = num(value * 100, "{:.0f}%", number_size, GREY_B)
            pct.next_to(bar, RIGHT, buff=0.16)
            row.add(pct)
            numbers.add(pct)
        words.add(label)
        bars.add(bar)
        out.add(parts_of(row))
    if more:
        dots = T("⋮", size, GREY_C).move_to([-0.45, -len(rows) * (line_h + row_gap), 0])
        out.add(dots)
    out.rows, out.words, out.bars, out.numbers = list(out)[: len(rows)], words, bars, numbers
    return named(parts_of(out.move_to(ORIGIN)), "bar_list")


def bracket_vector(values, fmt: str = "{:+.1f}", size: float = TINY, color=WHITE, row_gap: float = 0.14,
                   more: bool = False) -> VGroup:
    """A column of numbers in square brackets: a vector, an embedding.

    Entries dim with their magnitude (never below 58% white, so they always stay readable).
    """
    entries = VGroup()
    peak = max((abs(v) for v in values), default=1.0) or 1.0
    line_h = T("+8.8", size).height
    for i, v in enumerate(values):
        strength = 0.58 + 0.42 * abs(v) / peak
        entry = num(v, fmt, size, color).set_opacity(strength)
        entry.move_to([0, -i * (line_h + row_gap), 0])
        entries.add(entry)
    if more:
        entries.add(T("⋮", size, GREY_C).move_to([0, -len(values) * (line_h + row_gap), 0]))
    w, h = entries.width + 0.36, entries.height + 0.3
    c = entries.get_center()
    lip = 0.12

    def side(sign: int) -> VMobject:
        x = c[0] + sign * w / 2
        pts = [[x - sign * lip, c[1] + h / 2, 0], [x, c[1] + h / 2, 0], [x, c[1] - h / 2, 0], [x - sign * lip, c[1] - h / 2, 0]]
        m = VMobject(color=color, stroke_width=W_THIN)
        m.set_points_as_corners([np.array(p) for p in pts])
        return m

    group = VGroup(side(-1), entries, side(1))
    group.entries = entries
    return named(parts_of(group.move_to(ORIGIN)), "vector")


def progress_bar(width: float = 4.0, value: float = 0.0, color=BLUE, height: float = 0.16) -> VGroup:
    """A track with a fill. Set it with set_progress(bar, value) inside an updater or a live()."""
    track = RoundedRectangle(width=width, height=height, corner_radius=height / 2 - 1e-3, stroke_width=0,
                             fill_color=GREY_D, fill_opacity=1)
    fill = track.copy().set_fill(color)
    group = VGroup(track, fill)
    group.track, group.fill, group.full_width = track, fill, width
    set_progress(group, value)
    return named(parts_of(group), "progress")


def set_progress(bar: VGroup, value: float) -> VGroup:
    v = min(max(value, 0.0), 1.0)
    h = bar.track.height
    w = max(bar.full_width * v, h)
    new = RoundedRectangle(width=w, height=h, corner_radius=h / 2 - 1e-3, stroke_width=0,
                           fill_color=bar.fill.get_fill_color(), fill_opacity=1 if v > 0 else 0)
    new.move_to(bar.track.get_left() + RIGHT * w / 2)
    bar.fill.become(new)
    return bar


__all__ = [
    "box", "disc", "ring", "dot", "panel", "rule", "token", "chip", "badge", "arrow", "thin_arrow", "arc_arrow",
    "link", "highlight_box", "underline", "strike", "cross_out", "check", "cross", "brace_label", "axes", "axis_label",
    "bar_list", "bracket_vector", "progress_bar", "set_progress",
]
