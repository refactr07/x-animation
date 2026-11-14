"""The motion vocabulary. One move per kind of object, used the same way every time.

Everything eases with smootherstep over one second unless a move says otherwise: that is the curve
and the default 3Blue1Brown's Manim uses, and it is what makes motion read as calm and deliberate.
Nothing here bounces, flashes, wiggles or spins.

    write(label)                 words arrive letter by letter (stroke, then fill)
    rise(label)                  a short label or number fades in while rising a little
    pop(dot)                     a dot, badge or chip grows from 60% while fading in
    draw(outline)                a line, curve or line pictogram draws on
    build(shape)                 a tinted shape: the outline draws, then the fill comes up
    grow(arrow)                  an arrow grows from its tail
    pop_list(rows)               a list lands top to bottom, fast
    morph(a, b)                  one thing becomes another
    recolor(shape, GREEN)        a change of colour role
    leave(a, b)                  things go: fade, shorter than they came in
"""

from __future__ import annotations

import numpy as np
from manim import (
    DOWN,
    RIGHT,
    UP,
    Animation,
    AnimationGroup,
    Create,
    Dot,
    FadeIn,
    FadeOut,
    GrowArrow,
    LaggedStart,
    Mobject,
    MoveAlongPath,
    ReplacementTransform,
    Restore,
    Succession,
    Transform,
    TransformFromCopy,
    Uncreate,
    UpdateFromAlphaFunc,
    VMobject,
    Wait,
    Write,
    linear,
)

from xcore.tokens import TOKENS

from .theme import FAST, LAG, MOVE, TRANSFORM, YELLOW, tint

_m = TOKENS["motion"]


# ------------------------------------------------------------------ easing
def smooth(t: float) -> float:
    """Smootherstep, 6t^5 - 15t^4 + 10t^3: zero velocity and zero acceleration at both ends.

    Clamped to 0..1, because Manim hands an animation alpha = t / run_time without clamping: in a
    play() that mixes run times, the shorter animations would otherwise run past their end.
    """
    t = min(1.0, max(0.0, t))
    return t * t * t * (10 - 15 * t + 6 * t * t)


def ease_out(t: float) -> float:
    """Arrivals that should settle quickly: fast start, soft landing (quintic)."""
    t = min(1.0, max(0.0, t))
    return 1 - (1 - t) ** 5


def ease_in(t: float) -> float:
    """Departures: slow start, fast finish (cubic)."""
    t = min(1.0, max(0.0, t))
    return t**3


def use_house_motion() -> None:
    """Make smootherstep over MOVE seconds the default for every animation (Write stays linear)."""
    Animation.set_default(rate_func=smooth, run_time=MOVE)


# ------------------------------------------------------------------ arriving
def write(mob: VMobject, run_time: float | None = None, **kw) -> Write:
    """Words arriving: each glyph's outline draws, then fills. About 0.06 s per glyph."""
    glyphs = len(mob.family_members_with_points())
    auto = min(_m["write_max"], max(_m["write_min"], _m["write_per_glyph"] * glyphs + 0.3))
    return Write(mob, run_time=run_time or auto, **kw)


def rise(mob: Mobject, distance: float = 0.25, run_time: float = 0.6, **kw) -> FadeIn:
    """A short label, number or mark fades in while rising. Use distance=0.1 when it lands just
    above another label, so it never drifts through it."""
    return FadeIn(mob, shift=UP * distance, run_time=run_time, **kw)


def pop(mob: Mobject, run_time: float = 0.5, **kw) -> FadeIn:
    """A dot, badge, chip or small icon grows from 60% while fading in. No overshoot."""
    return FadeIn(mob, scale=0.6, run_time=run_time, **kw)


def fade_in(mob: Mobject, shift=None, run_time: float = 0.8, **kw) -> FadeIn:
    """Paragraphs, panels and pictures."""
    return FadeIn(mob, shift=shift, run_time=run_time, **kw) if shift is not None else FadeIn(mob, run_time=run_time, **kw)


def draw(mob: VMobject, run_time: float = MOVE, **kw) -> Create:
    """Lines, curves, outlines and line pictograms draw on."""
    return Create(mob, run_time=run_time, **kw)


def build(mob: VMobject, run_time: float = MOVE) -> Succession:
    """A tinted shape: its outline draws, then its fill comes up. (Create alone would wipe the fill
    in at an angle while the outline is still drawing.)"""
    target = mob.copy()
    for part in mob.family_members_with_points():
        part.set_fill(opacity=0)
    return Succession(Create(mob, run_time=0.62 * run_time), Transform(mob, target, run_time=0.38 * run_time))


def grow(arrow: VMobject, run_time: float = 0.7, **kw) -> GrowArrow:
    """An arrow grows from its tail."""
    return GrowArrow(arrow, run_time=run_time, **kw)


def pop_list(items, item_time: float | None = None, shift=RIGHT * 0.15) -> LaggedStart:
    """A list landing top to bottom: each row about 0.25 s, 0.035 s apart."""
    item_time = item_time or _m["list_item"]
    lag = _m["list_lag"]
    n = max(len(items), 1)
    return LaggedStart(*[FadeIn(i, shift=shift) for i in items], lag_ratio=lag / item_time,
                       run_time=item_time + lag * (n - 1))


def stagger(anims, lag_ratio: float = LAG, run_time: float | None = None) -> LaggedStart:
    """A group of like things, each with its own entrance, one after another."""
    anims = list(anims)
    kw = {"run_time": run_time} if run_time else {}
    return LaggedStart(*anims, lag_ratio=lag_ratio, **kw)


# ------------------------------------------------------------------ changing
def morph(old: Mobject, new: Mobject, run_time: float = TRANSFORM, **kw) -> ReplacementTransform:
    """One thing becomes another (afterwards `new` is on screen and `old` is gone)."""
    return ReplacementTransform(old, new, run_time=run_time, **kw)


def from_copy(source: Mobject, new: Mobject, run_time: float = MOVE, **kw) -> TransformFromCopy:
    """`new` comes out of `source`, which stays where it is."""
    return TransformFromCopy(source, new, run_time=run_time, **kw)


def recolor(mob: VMobject, color, fill: float | None = None, run_time: float = 0.6) -> Animation:
    """A tinted shape takes a new colour role: stroke to the colour, fill to its tint."""
    return mob.animate(run_time=run_time).set_stroke(color).set_fill(tint(color, fill))


def glow(mob: VMobject, color=YELLOW, run_time: float = 0.6) -> Animation:
    """Text or a line pictogram takes the colour that says "look here"."""
    return mob.animate(run_time=run_time).set_color(color)


def dim(*mobs: Mobject, amount: float = 0.7, run_time: float = 0.6) -> AnimationGroup:
    """Push context back so the subject stands out. Undo with undim(). Use this, never set_opacity
    (which also fills outlines)."""
    for m in mobs:
        m.save_state()
    return AnimationGroup(*(m.animate(run_time=run_time).fade(amount) for m in mobs))


def undim(*mobs: Mobject, run_time: float = 0.6) -> AnimationGroup:
    return AnimationGroup(*(Restore(m, run_time=run_time) for m in mobs))


# ------------------------------------------------------------------ leaving
def leave(*mobs: Mobject, shift=None, run_time: float = FAST, **kw) -> list[FadeOut]:
    """Things go. It returns one FadeOut per object, so unpack it: self.play(*leave(a, b), rise(c)).
    Leaving is shorter than arriving."""
    if shift is None:
        return [FadeOut(m, run_time=run_time, **kw) for m in mobs]
    return [FadeOut(m, shift=shift, run_time=run_time, **kw) for m in mobs]


def sink(*mobs: Mobject, run_time: float = FAST) -> list[FadeOut]:
    """An old answer leaves: it fades while sliding down a little."""
    return leave(*mobs, shift=DOWN * 0.3, run_time=run_time)


def undraw(mob: VMobject, run_time: float = FAST, **kw) -> Uncreate:
    """Lines and arcs leave the way they came."""
    return Uncreate(mob, run_time=run_time, **kw)


# ------------------------------------------------------------------ timing inside one play
def later(delay: float, anim: Animation) -> Succession:
    """Start `anim` `delay` seconds into the play it is part of."""
    return Succession(Wait(run_time=delay), anim)


def span(anim: Animation, start: float, end: float) -> Succession:
    """Run `anim` from `start` to `end` seconds of the play it is part of (ManimGL's time_span)."""
    anim.run_time = end - start
    return later(start, anim) if start > 0 else anim


# ------------------------------------------------------------------ travelling
def glide(mob: Mobject, end, via=None, run_time: float = MOVE) -> UpdateFromAlphaFunc:
    """Move a rigid object along a curve without tilting it. Pick `via` so the path clears every
    other object: nothing may overlap, even mid-move. (Transform with path_arc would rotate it.)"""
    start = mob.get_center().copy()
    end = np.asarray(end, dtype=float)
    via = (start + end) / 2 if via is None else np.asarray(via, dtype=float)
    mob.save_state()

    def step(m: Mobject, a: float) -> None:
        m.restore()
        m.move_to((1 - a) ** 2 * start + 2 * (1 - a) * a * via + a * a * end)

    return UpdateFromAlphaFunc(mob, step, run_time=run_time)


def travel(path: VMobject, color=YELLOW, radius: float = 0.07, run_time: float = 0.9) -> Succession:
    """A signal travels along a line, arrow or curve: a small dot that appears, runs the path and is
    gone. The honest way to keep a picture alive while the voice explains it: something really is
    moving from here to there."""
    dot = Dot(path.get_start(), radius=radius, color=color).set_z_index(5)
    for part in dot.get_family():
        part.x_overlap_ok = True  # a signal is meant to cross what it travels to
    track = path.copy().set_opacity(0)
    return Succession(
        FadeIn(dot, scale=0.5, run_time=0.12 * run_time, rate_func=linear),
        MoveAlongPath(dot, track, run_time=0.76 * run_time),
        FadeOut(dot, scale=0.5, run_time=0.12 * run_time, rate_func=linear),
    )


def flip(old: Mobject, new: Mobject, run_time: float = 0.8) -> Succession:
    """A card turns over in place: `old` squeezes edge-on, `new` opens from the edge."""
    new.move_to(old)
    full = new.copy()
    new.stretch(0.02, 0)
    return Succession(
        old.animate(run_time=run_time / 2, rate_func=ease_in).stretch(0.02, 0),
        AnimationGroup(FadeOut(old, run_time=1 / 60), Transform(new, full, run_time=run_time / 2, rate_func=ease_out)),
    )


__all__ = [
    "smooth", "ease_out", "ease_in", "use_house_motion", "write", "rise", "pop", "fade_in", "draw", "build", "grow",
    "pop_list", "stagger", "morph", "from_copy", "recolor", "glow", "dim", "undim", "leave", "sink", "undraw",
    "later", "span", "glide", "travel", "flip",
]
