"""Line pictograms, drawn from Manim primitives only: no SVG files, emoji or icon fonts.

Each is two to eight strokes at one weight, about one unit tall, light grey unless it carries a
colour role. They are deliberately plain: a pictogram says what a thing is, the animation says
what it does. Build new ones the same way, in the scene file first; move one here when a second
section needs it.
"""

from __future__ import annotations

import numpy as np
from manim import (
    DOWN,
    LEFT,
    ORIGIN,
    PI,
    RIGHT,
    TAU,
    UP,
    Arc,
    CapStyleType,
    Circle,
    Dot,
    Ellipse,
    Line,
    Polygon,
    RoundedRectangle,
    Star,
    VGroup,
    VMobject,
)

from .layout import named, parts_of
from .theme import GREEN, GREY_A, GREY_B, GREY_C, GREY_D, RED, TEAL, W_HAIR, W_SHAPE, W_THIN, YELLOW, stage, tint


def _done(group: VGroup, name: str) -> VGroup:
    for part in group.family_members_with_points():
        if part.get_stroke_width() > 0:
            part.set_cap_style(CapStyleType.ROUND)
    return named(parts_of(group), name)


def _poly(points, color, width=W_SHAPE, close=False) -> VMobject:
    m = VMobject(color=color, stroke_width=width)
    pts = [np.array([p[0], p[1], 0.0]) for p in points]
    if close:
        pts.append(pts[0])
    m.set_points_as_corners(pts)
    return m


# ------------------------------------------------------------------ people
def person(color=GREY_A, fill=None) -> VGroup:
    """A bust: round head over rounded shoulders."""
    head = Circle(radius=0.24, color=color, stroke_width=W_SHAPE)
    body = Arc(radius=0.46, start_angle=0, angle=PI, color=color, stroke_width=W_SHAPE)
    body.add_line_to(body.get_start())
    body.next_to(head, DOWN, buff=0.1)
    if fill is not None:
        head.set_fill(tint(fill), opacity=1)
        body.set_fill(tint(fill), opacity=1)
    return _done(VGroup(head, body), "person")


def team(n: int = 3, color=GREY_A, scale: float = 0.8, buff: float = 0.22) -> VGroup:
    """A few people side by side. Each is its own object, so one can become another thing."""
    return VGroup(*[person(color) for _ in range(n)]).scale(scale).arrange(RIGHT, buff=buff)


def crowd(center=ORIGIN, radius: float = 2.0, n: int = 14, color=GREEN, dot_radius: float = 0.08) -> VGroup:
    """Many around one: users, clients, requests. Small dots evenly spaced on a circle."""
    center = np.asarray(center, dtype=float)
    dots = VGroup(*[
        Dot(center + radius * np.array([np.cos(a), np.sin(a), 0]), radius=dot_radius, color=color)
        for a in (np.arange(n) + 0.5) * TAU / n
    ])
    return named(parts_of(dots), "crowd")


def robot(color=GREY_A) -> VGroup:
    """A friendly machine head: an assistant, a bot, an agent."""
    head = RoundedRectangle(width=0.9, height=0.72, corner_radius=0.16, color=color, stroke_width=W_SHAPE)
    eyes = VGroup(Dot([-0.2, 0.06, 0], radius=0.07, color=color), Dot([0.2, 0.06, 0], radius=0.07, color=color))
    mouth = Line([-0.16, -0.18, 0], [0.16, -0.18, 0], color=color, stroke_width=W_THIN)
    stem = Line([0, 0.36, 0], [0, 0.54, 0], color=color, stroke_width=W_THIN)
    tip = Dot([0, 0.6, 0], radius=0.06, color=color)
    ears = VGroup(Line([-0.45, -0.08, 0], [-0.56, -0.08, 0]), Line([0.45, -0.08, 0], [0.56, -0.08, 0]))
    ears.set_stroke(color, W_SHAPE)
    return _done(VGroup(head, eyes, mouth, stem, tip, ears), "robot")


# ------------------------------------------------------------------ documents and code
def page(width: float = 0.72, height: float = 0.94, color=GREY_B, rows: int = 4) -> VGroup:
    """A sheet with a few rows of text: a document, a file, a script."""
    sheet = RoundedRectangle(width=width, height=height, corner_radius=0.06, color=color, stroke_width=W_THIN,
                             fill_color=stage(), fill_opacity=1)
    lines = VGroup()
    for k in range(rows):
        y = height * (0.3 - 0.6 * k / max(rows - 1, 1))
        short = 0.22 if k == rows - 1 else 0.0
        lines.add(Line([-width * 0.3, y, 0], [width * (0.3 - short), y, 0], color=color, stroke_width=W_HAIR * 1.4))
    return _done(VGroup(sheet, lines), "page")


def pages(n: int = 3, color=GREY_B, offset: float = 0.09) -> VGroup:
    """A small stack of sheets: a library, a dataset, a pile of files."""
    stack = VGroup(*[page(color=color).shift((RIGHT + UP) * offset * (n - 1 - k)) for k in range(n)])
    return named(parts_of(stack.move_to(ORIGIN)), "pages")


def code_bars(color=GREY_A, colors: list | None = None, width: float = W_SHAPE * 1.3, scale: float = 1.0) -> VGroup:
    """Code without the text: seven rounded bars with indents. Pass `colors` for syntax tints."""
    widths = [1.3, 0.9, 1.1, 0.7, 1.2, 0.8, 1.0]
    indents = [0, 0.3, 0.3, 0.6, 0.3, 0, 0]
    bars = VGroup()
    for i, (w, ind) in enumerate(zip(widths, indents)):
        c = colors[i % len(colors)] if colors else color
        bars.add(Line(RIGHT * ind + DOWN * 0.24 * i, RIGHT * (ind + w) + DOWN * 0.24 * i, color=c, stroke_width=width))
    bars.scale(scale).move_to(ORIGIN)
    return _done(bars, "code")


def folder(color=GREY_B) -> VGroup:
    body = _poly([[-0.5, 0.26], [-0.5, -0.34], [0.5, -0.34], [0.5, 0.2], [0.02, 0.2], [-0.08, 0.34], [-0.42, 0.34]],
                 color, close=True)
    body.set_fill(stage(), opacity=1)
    return _done(VGroup(body), "folder")


def clipboard(color=GREY_B, rows: int = 3, done: int = 0, tick=GREEN) -> VGroup:
    """A checklist. The first `done` boxes are ticked."""
    board = RoundedRectangle(width=0.86, height=1.1, corner_radius=0.08, color=color, stroke_width=W_SHAPE,
                             fill_color=stage(), fill_opacity=1)
    clip = RoundedRectangle(width=0.36, height=0.14, corner_radius=0.05, color=color, stroke_width=W_THIN,
                            fill_color=tint(color, 0.35), fill_opacity=1).move_to(board.get_top())
    items = VGroup()
    for k in range(rows):
        y = 0.24 - 0.28 * k
        square = RoundedRectangle(width=0.14, height=0.14, corner_radius=0.03, color=color, stroke_width=W_HAIR * 1.4)
        square.move_to([-0.24, y, 0])
        line = Line([-0.08, y, 0], [0.28, y, 0], color=color, stroke_width=W_THIN)
        items.add(square, line)
        if k < done:
            items.add(_poly([[-0.29, y], [-0.25, y - 0.05], [-0.17, y + 0.07]], tick, W_THIN))
    return _done(VGroup(board, clip, items), "clipboard")


# ------------------------------------------------------------------ screens
def app_window(width: float = 2.6, height: float = 1.8, color=GREY_B, fill=None) -> VGroup:
    """A product: a rounded window with a top bar and three dots. window.body is the content area."""
    frame = RoundedRectangle(width=width, height=height, corner_radius=0.12, color=color, stroke_width=W_SHAPE,
                             fill_color=tint(fill or color, 0.1 if fill is None else 0.18), fill_opacity=1)
    bar_y = height / 2 - 0.3
    bar = Line([-width / 2, bar_y, 0], [width / 2, bar_y, 0], color=color, stroke_width=W_THIN)
    dots = VGroup(*[Dot([-width / 2 + 0.2 + 0.16 * k, height / 2 - 0.15, 0], radius=0.04, color=color) for k in range(3)])
    group = VGroup(frame, bar, dots)
    group.frame = frame
    group.body = np.array([0.0, -0.15, 0.0])  # centre of the content area, relative to the window's centre
    return _done(group, "window")


def browser(width: float = 3.0, height: float = 2.0, color=GREY_B) -> VGroup:
    """A website: a window with an address field."""
    win = app_window(width, height, color)
    field = RoundedRectangle(width=width * 0.5, height=0.13, corner_radius=0.06, color=color, stroke_width=W_HAIR * 1.4)
    field.move_to([0.12, height / 2 - 0.15, 0])
    group = VGroup(*win, field)
    group.frame = win.frame
    return _done(group, "browser")


def terminal(width: float = 2.4, height: float = 1.5, color=GREY_B, prompt=GREEN) -> VGroup:
    """A command line: a dark window with a prompt."""
    frame = RoundedRectangle(width=width, height=height, corner_radius=0.12, color=color, stroke_width=W_SHAPE,
                             fill_color=stage(), fill_opacity=1)
    x, y = -width / 2 + 0.28, height / 2 - 0.36
    chevron = _poly([[x, y + 0.1], [x + 0.12, y], [x, y - 0.1]], prompt, W_SHAPE)
    cursor = Line([x + 0.24, y - 0.1, 0], [x + 0.46, y - 0.1, 0], color=prompt, stroke_width=W_SHAPE)
    group = VGroup(frame, chevron, cursor)
    group.frame = frame
    return _done(group, "terminal")


def phone(color=GREY_B) -> VGroup:
    body = RoundedRectangle(width=0.62, height=1.14, corner_radius=0.1, color=color, stroke_width=W_SHAPE,
                            fill_color=stage(), fill_opacity=1)
    notch = Line([-0.1, 0.45, 0], [0.1, 0.45, 0], color=color, stroke_width=W_THIN)
    return _done(VGroup(body, notch), "phone")


def laptop(color=GREY_B) -> VGroup:
    screen = RoundedRectangle(width=1.24, height=0.8, corner_radius=0.07, color=color, stroke_width=W_SHAPE,
                              fill_color=stage(), fill_opacity=1).shift(UP * 0.12)
    base = Line([-0.82, -0.36, 0], [0.82, -0.36, 0], color=color, stroke_width=W_SHAPE)
    return _done(VGroup(screen, base), "laptop")


def chat_bubble(width: float = 2.2, height: float = 0.9, color=GREY_B, side: str = "left", fill=None) -> VGroup:
    """A message. The tail sits at the speaker's bottom corner: side="left" for the other party,
    "right" for the person asking."""
    body = RoundedRectangle(width=width, height=height, corner_radius=min(0.22, height / 2 - 1e-3), color=color,
                            stroke_width=W_SHAPE, fill_color=tint(fill or color, 0.12 if fill is None else 0.2),
                            fill_opacity=1)
    s = -1 if side == "left" else 1
    x, y = s * (width / 2 - 0.34), -height / 2
    tail = _poly([[x, y + 0.02], [x + s * 0.2, y - 0.2], [x + s * 0.22, y + 0.02]], color, W_SHAPE)
    cover = Line([x + s * 0.02, y, 0], [x + s * 0.2, y, 0], stroke_width=W_SHAPE * 1.5, color=body.get_fill_color())
    group = VGroup(body, cover, tail)
    group.body = body
    return _done(group, "bubble")


# ------------------------------------------------------------------ machines and infrastructure
def server(color=GREY_B, units: int = 3, light=GREEN) -> VGroup:
    """A rack of machines: a server, a backend, compute."""
    rows = VGroup()
    for k in range(units):
        slot = RoundedRectangle(width=1.0, height=0.3, corner_radius=0.06, color=color, stroke_width=W_SHAPE,
                                fill_color=stage(), fill_opacity=1).shift(DOWN * 0.36 * k)
        led = Dot(slot.get_left() + RIGHT * 0.16, radius=0.045, color=light)
        vent = Line(slot.get_right() + LEFT * 0.42, slot.get_right() + LEFT * 0.14, color=color, stroke_width=W_THIN)
        rows.add(slot, led, vent)
    return _done(rows.move_to(ORIGIN), "server")


def database(color=GREY_B, width: float = 0.96, height: float = 1.0) -> VGroup:
    """A cylinder of stacked discs: stored data."""
    ry = 0.16
    top = Ellipse(width=width, height=2 * ry, color=color, stroke_width=W_SHAPE).shift(UP * (height / 2 - ry))
    left = Line([-width / 2, height / 2 - ry, 0], [-width / 2, -height / 2 + ry, 0], color=color, stroke_width=W_SHAPE)
    right = left.copy().shift(RIGHT * width)
    arcs = VGroup()
    for y in (-height / 2 + ry, -height / 2 + ry + (height - 2 * ry) / 2):
        arc = Arc(radius=1, start_angle=PI, angle=PI, color=color, stroke_width=W_SHAPE if y < -0.2 else W_THIN)
        arc.stretch_to_fit_width(width).stretch_to_fit_height(ry).move_to([0, y - ry / 2, 0])
        arcs.add(arc)
    return _done(VGroup(top, left, right, arcs), "database")


def cloud(color=GREY_B, width: float = 1.5) -> VGroup:
    """The cloud, an outside service, the internet at large."""
    from manim import Union

    k = width / 1.5
    lobes = [
        Circle(radius=0.26 * k).move_to([-0.46 * k, -0.08 * k, 0]),
        Circle(radius=0.36 * k).move_to([-0.12 * k, 0.12 * k, 0]),
        Circle(radius=0.28 * k).move_to([0.3 * k, 0.04 * k, 0]),
        Circle(radius=0.2 * k).move_to([0.54 * k, -0.14 * k, 0]),
        RoundedRectangle(width=1.0 * k, height=0.3 * k, corner_radius=0.14 * k).move_to([0.04 * k, -0.19 * k, 0]),
    ]
    outline = Union(*lobes, color=color, stroke_width=W_SHAPE, fill_color=stage(), fill_opacity=1)
    return _done(VGroup(outline).move_to(ORIGIN), "cloud")


def chip_cpu(color=GREY_B, core=None) -> VGroup:
    """A processor: compute, a GPU, hardware."""
    body = RoundedRectangle(width=0.8, height=0.8, corner_radius=0.08, color=color, stroke_width=W_SHAPE,
                            fill_color=stage(), fill_opacity=1)
    inner = RoundedRectangle(width=0.36, height=0.36, corner_radius=0.04, color=core or color, stroke_width=W_THIN)
    if core is not None:
        inner.set_fill(tint(core, 0.3), opacity=1)
    pins = VGroup()
    for k in (-0.22, 0.0, 0.22):
        pins.add(Line([k, 0.4, 0], [k, 0.54, 0]), Line([k, -0.4, 0], [k, -0.54, 0]),
                 Line([0.4, k, 0], [0.54, k, 0]), Line([-0.4, k, 0], [-0.54, k, 0]))
    pins.set_stroke(color, W_THIN)
    return _done(VGroup(body, inner, pins), "cpu")


def gear(color=GREY_B, teeth: int = 8, radius: float = 0.46) -> VGroup:
    """A setting, a mechanism, "how it works"."""
    pts = []
    for k in range(teeth):
        a = k * TAU / teeth
        w = TAU / teeth
        for da, r in ((-0.3, radius * 0.78), (-0.16, radius), (0.16, radius), (0.3, radius * 0.78)):
            pts.append([r * np.cos(a + da * w), r * np.sin(a + da * w)])
    rim = _poly(pts, color, W_SHAPE, close=True)
    rim.set_fill(stage(), opacity=1)
    hub = Circle(radius=radius * 0.3, color=color, stroke_width=W_THIN)
    return _done(VGroup(rim, hub), "gear")


def dial(value: float = 0.5, color=GREY_B, needle=TEAL, radius: float = 0.3) -> VGroup:
    """One tunable number: a gauge open at the bottom, its needle set by `value` in 0..1.

    dial.needle is the needle; turn it with turn_dial(dial, value).
    """
    arc = Arc(radius=radius, start_angle=-PI / 4, angle=1.5 * PI, color=color, stroke_width=W_THIN)
    needle_line = Line(ORIGIN, UP * radius * 0.8, color=needle, stroke_width=W_SHAPE)
    hub = Dot(ORIGIN, radius=0.04, color=needle)
    group = VGroup(arc, needle_line, hub)
    group.needle, group.value = needle_line, 0.5
    _done(group, "dial")
    return turn_dial(group, value)


def turn_dial(d: VGroup, value: float) -> VGroup:
    """Point a dial's needle at `value` (0 = far left, 1 = far right)."""
    value = min(max(value, 0.0), 1.0)
    d.needle.rotate(-(value - d.value) * 1.5 * PI, about_point=d[2].get_center())
    d.value = value
    return d


def turn_dials(dials, values, run_time: float = 1.0, lag_ratio: float = 0.0):
    """Animate needles to new values: self.play(turn_dials(model.dials, values)).

    Never in the same play() as moving or scaling the panel: the two changes would fight over
    the needles. Move first, then turn.
    """
    from manim import AnimationGroup, UpdateFromAlphaFunc

    anims = []
    for d, v in zip(dials, values):
        start = d.value

        def step(m, a, d=d, start=start, v=v):
            turn_dial(d, start + (v - start) * a)

        anims.append(UpdateFromAlphaFunc(d, step, run_time=run_time))
    return AnimationGroup(*anims, lag_ratio=lag_ratio)


def dial_panel(rows: int = 2, cols: int = 3, color=GREY_B, needle=TEAL, values=None, seed: int = 7) -> VGroup:
    """A model as a box of tunable dials: its parameters. panel.dials is the list of dials."""
    rng = np.random.default_rng(seed)
    vals = list(values) if values is not None else list(rng.uniform(0.08, 0.92, rows * cols))
    dials = VGroup(*[dial(vals[i], color, needle, radius=0.2) for i in range(rows * cols)])
    dials.arrange_in_grid(rows=rows, cols=cols, buff=0.2)
    frame = RoundedRectangle(width=dials.width + 0.5, height=dials.height + 0.5, corner_radius=0.14, color=color,
                             stroke_width=W_SHAPE, fill_color=tint(color, 0.12), fill_opacity=1)
    group = VGroup(frame, dials)
    group.frame, group.dials = frame, list(dials)
    return named(parts_of(group), "model")


def neural_net(layers=(3, 4, 4, 2), color=GREY_A, edge=GREY_D, width: float = 3.6, height: float = 2.2,
               node_radius: float = 0.11) -> VGroup:
    """A small feed-forward network. net.layers[i] is a VGroup of nodes; net.edges[i] the lines
    from layer i to layer i + 1 (in row-major order)."""
    xs = np.linspace(-width / 2, width / 2, len(layers))
    nodes, edges = [], []
    for x, n in zip(xs, layers):
        ys = np.linspace(height / 2, -height / 2, n) if n > 1 else [0.0]
        ys = [y * (n - 1) / max(max(layers) - 1, 1) for y in ys]
        nodes.append(VGroup(*[
            Circle(radius=node_radius, color=color, stroke_width=W_THIN, fill_color=stage(), fill_opacity=1).move_to([x, y, 0])
            for y in ys
        ]))
    for a, b in zip(nodes[:-1], nodes[1:]):
        group = VGroup()
        for p in a:
            for q in b:
                d = q.get_center() - p.get_center()
                u = d / np.linalg.norm(d)
                group.add(Line(p.get_center() + u * node_radius, q.get_center() - u * node_radius, color=edge,
                               stroke_width=W_HAIR))
        edges.append(group)
    net = VGroup(*edges, *nodes)
    net.layers, net.edges = nodes, edges
    return named(parts_of(net), "network")


# ------------------------------------------------------------------ small things
def clock(color=GREY_B, radius: float = 0.44, hour: float = 10, minute: float = 10) -> VGroup:
    """Time passing, a deadline, latency."""
    face = Circle(radius=radius, color=color, stroke_width=W_SHAPE, fill_color=stage(), fill_opacity=1)
    ha = PI / 2 - TAU * ((hour % 12) + minute / 60) / 12
    ma = PI / 2 - TAU * minute / 60
    hands = VGroup(
        Line(ORIGIN, radius * 0.5 * np.array([np.cos(ha), np.sin(ha), 0])),
        Line(ORIGIN, radius * 0.74 * np.array([np.cos(ma), np.sin(ma), 0])),
    ).set_stroke(color, W_THIN)
    group = VGroup(face, hands)
    group.hands = hands
    return _done(group, "clock")


def magnifier(color=GREY_B) -> VGroup:
    """Search, inspection, "look closer"."""
    lens = Circle(radius=0.3, color=color, stroke_width=W_SHAPE).shift(UP * 0.1 + LEFT * 0.1)
    handle = Line(lens.get_center() + 0.3 * np.array([0.707, -0.707, 0]),
                  lens.get_center() + 0.62 * np.array([0.707, -0.707, 0]), color=color, stroke_width=W_SHAPE * 1.5)
    return _done(VGroup(lens, handle), "search")


def padlock(color=GREY_B, locked: bool = True) -> VGroup:
    """A secret, security, access."""
    body = RoundedRectangle(width=0.62, height=0.48, corner_radius=0.08, color=color, stroke_width=W_SHAPE,
                            fill_color=stage(), fill_opacity=1)
    shackle = Arc(radius=0.19, start_angle=0, angle=PI, color=color, stroke_width=W_SHAPE)
    shackle.add_line_to(shackle.get_end() + DOWN * 0.1)
    shackle.next_to(body, UP, buff=0)
    if not locked:
        shackle.shift(RIGHT * 0.38 + UP * 0.06)
    hole = Dot(body.get_center() + UP * 0.02, radius=0.05, color=color)
    return _done(VGroup(shackle, body, hole), "lock")


def key(color=GREY_B) -> VGroup:
    """A credential, an API key, the thing that unlocks."""
    bow = Circle(radius=0.2, color=color, stroke_width=W_SHAPE).shift(LEFT * 0.36)
    shaft = Line([-0.16, 0, 0], [0.52, 0, 0], color=color, stroke_width=W_SHAPE)
    teeth = VGroup(Line([0.3, 0, 0], [0.3, -0.16, 0]), Line([0.46, 0, 0], [0.46, -0.12, 0])).set_stroke(color, W_SHAPE)
    return _done(VGroup(bow, shaft, teeth), "key")


def bolt(color=YELLOW, fill: bool = True) -> VGroup:
    """Speed, energy, power."""
    shape = Polygon([0.12, 0.44, 0], [-0.26, -0.06, 0], [-0.02, -0.06, 0], [-0.12, -0.44, 0], [0.26, 0.08, 0],
                    [0.02, 0.08, 0], color=color, stroke_width=W_THIN)
    if fill:
        shape.set_fill(tint(color, 0.3), opacity=1)
    return _done(VGroup(shape), "bolt")


def star(color=YELLOW, outer: float = 0.5, fill: bool = True) -> VGroup:
    """Quality, a favourite, the standout. Centred on the origin: place it with shift()."""
    shape = Star(n=5, outer_radius=outer, inner_radius=outer * 0.42, color=color, stroke_width=W_SHAPE)
    if fill:
        shape.set_fill(tint(color, 0.3), opacity=1)
    return _done(VGroup(shape), "star")


def lightbulb(color=YELLOW) -> VGroup:
    """An idea."""
    glass = Arc(radius=0.3, start_angle=-PI / 3, angle=PI * 5 / 3, color=color, stroke_width=W_SHAPE).shift(UP * 0.12)
    a, b = glass.get_start(), glass.get_end()
    neck = VGroup(Line(a, [0.13, -0.3, 0]), Line(b, [-0.13, -0.3, 0])).set_stroke(color, W_SHAPE)
    base = VGroup(Line([-0.13, -0.38, 0], [0.13, -0.38, 0]), Line([-0.08, -0.47, 0], [0.08, -0.47, 0]))
    base.set_stroke(color, W_THIN)
    return _done(VGroup(glass, neck, base), "idea")


def envelope(color=GREY_B) -> VGroup:
    """A message, an email, a notification."""
    body = RoundedRectangle(width=1.0, height=0.68, corner_radius=0.06, color=color, stroke_width=W_SHAPE,
                            fill_color=stage(), fill_opacity=1)
    flap = _poly([[-0.48, 0.3], [0, -0.06], [0.48, 0.3]], color, W_THIN)
    return _done(VGroup(body, flap), "mail")


def globe(color=GREY_B, radius: float = 0.46) -> VGroup:
    """The web, the world, everywhere."""
    rim = Circle(radius=radius, color=color, stroke_width=W_SHAPE, fill_color=stage(), fill_opacity=1)
    meridian = Ellipse(width=radius * 0.9, height=radius * 2, color=color, stroke_width=W_THIN)
    equator = Line(LEFT * radius, RIGHT * radius, color=color, stroke_width=W_THIN)
    lat = VGroup(*[
        Line(LEFT * radius * 0.87 + UP * s * radius * 0.5, RIGHT * radius * 0.87 + UP * s * radius * 0.5)
        for s in (-1, 1)
    ]).set_stroke(color, W_HAIR * 1.4)
    return _done(VGroup(rim, meridian, equator, lat), "globe")


def warning(color=RED) -> VGroup:
    """Risk, a failure, "careful"."""
    tri = Polygon([0, 0.46, 0], [-0.5, -0.38, 0], [0.5, -0.38, 0], color=color, stroke_width=W_SHAPE)
    tri.round_corners(0.06)
    tri.set_fill(tint(color, 0.18), opacity=1)
    stem = Line([0, 0.16, 0], [0, -0.1, 0], color=color, stroke_width=W_SHAPE)
    point = Dot([0, -0.24, 0], radius=0.045, color=color)
    return _done(VGroup(tri, stem, point), "warning")


def coin(color=None, radius: float = 0.4) -> VGroup:
    """Money, cost, price."""
    from .text import T
    from .theme import GOLD, SMALL

    c = color or GOLD
    rim = Circle(radius=radius, color=c, stroke_width=W_SHAPE, fill_color=tint(c, 0.22), fill_opacity=1)
    sign = T("$", SMALL, c, weight="bold").move_to(rim)
    return named(parts_of(VGroup(rim, sign)), "coin")


def eye(color=GREY_B) -> VGroup:
    """Attention, observation, "it sees"."""
    upper = Arc(radius=0.62, start_angle=PI / 2 - 0.86, angle=1.72, color=color, stroke_width=W_SHAPE).shift(DOWN * 0.4)
    lower = upper.copy().rotate(PI, about_point=ORIGIN)
    iris = Circle(radius=0.16, color=color, stroke_width=W_SHAPE)
    pupil = Dot(ORIGIN, radius=0.06, color=color)
    return _done(VGroup(upper, lower, iris, pupil), "eye")


def line_chart(color=None, width: float = 1.2, height: float = 0.8, rising: bool = True) -> VGroup:
    """Growth or decline at a glance: two axes and a trend."""
    c = color or (GREEN if rising else RED)
    ax = _poly([[-width / 2, height / 2], [-width / 2, -height / 2], [width / 2, -height / 2]], GREY_C, W_THIN)
    ys = [-0.3, -0.12, -0.2, 0.08, 0.02, 0.36] if rising else [0.36, 0.1, 0.18, -0.08, -0.02, -0.3]
    xs = np.linspace(-width / 2 + 0.12, width / 2 - 0.08, len(ys))
    trend = _poly([[x, y * height] for x, y in zip(xs, ys)], c, W_SHAPE)
    return _done(VGroup(ax, trend), "chart")


__all__ = [
    "person", "team", "crowd", "robot", "page", "pages", "code_bars", "folder", "clipboard", "app_window", "browser",
    "terminal", "phone", "laptop", "chat_bubble", "server", "database", "cloud", "chip_cpu", "gear", "dial",
    "turn_dial", "turn_dials", "dial_panel", "neural_net", "clock", "magnifier", "padlock", "key", "bolt", "star", "lightbulb",
    "envelope", "globe", "warning", "coin", "eye", "line_chart",
]
