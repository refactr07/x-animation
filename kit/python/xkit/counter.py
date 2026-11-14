"""Numbers that run: a counter bound to a ValueTracker.

    steps = ValueTracker(0)
    readout = counter(self, steps, "{:,.0f}", size=HEADING, anchor=RIGHT, at=[4, 1, 0])
    self.add(readout)
    self.play(steps.animate(rate_func=linear).set_value(5000), run_time=3)
    readout.clear_updaters()        # freeze it once the count stops

The digits of Computer Modern are all one width, the number is anchored on one edge and it sits on
a fixed baseline, so it never jitters while it runs (not even when a comma appears).
"""

from __future__ import annotations

import numpy as np
from manim import ORIGIN, RIGHT, UP, ValueTracker, VGroup

from .text import T, baseline, minus
from .theme import BODY, WHITE

_cache: dict[tuple, VGroup] = {}


def _typeset(text: str, size: float, color, weight: str):
    key = (text, round(size, 3), str(color), weight)
    if key not in _cache:
        _cache[key] = T(text, size, color, weight=weight, smart=False)
    return _cache[key].copy()


def _place(mob, at: np.ndarray, anchor, digit_height: float):
    """Anchor one edge at `at`, with the digits (not the bounding box) centred on its height."""
    mob.move_to(at, aligned_edge=anchor)
    mob.shift(UP * ((at[1] - digit_height / 2) - baseline(mob)))
    return mob


def counter(scene, tracker: ValueTracker, fmt: str = "{:,.0f}", size: float = BODY, color=WHITE,
            anchor=RIGHT, at=ORIGIN, weight: str = "regular", place=None) -> VGroup:
    """A live number showing fmt.format(tracker value).

    `anchor` is the edge that stays put (RIGHT keeps the last digit still while digits are added on
    the left; LEFT and ORIGIN also work) and `at` is where that edge sits. Pass `place(mob)` instead
    to position it yourself on every frame, e.g. place=lambda m: m.next_to(bar, UP).
    """
    at = np.asarray(at, dtype=float)
    digit_height = float(T("0", size).height)

    def update(holder: VGroup, dt: float = 0) -> None:
        mob = _typeset(minus(fmt.format(tracker.get_value())), size, color, weight)
        if place is not None:
            place(mob)
        else:
            _place(mob, at, anchor, digit_height)
        holder.submobjects = [mob]

    holder = scene.live(update)
    update(holder)
    return holder


def still_number(value: float, fmt: str = "{:,.0f}", size: float = BODY, color=WHITE, anchor=RIGHT, at=ORIGIN,
                 weight: str = "regular"):
    """The same number as a plain object, in the same place: bring this in with rise(), then swap it
    for the live counter (a live number cannot fade in, its shape changes every frame)."""
    mob = T(minus(fmt.format(value)), size, color, weight=weight, smart=False)
    return _place(mob, np.asarray(at, dtype=float), anchor, float(T("0", size).height))


__all__ = ["counter", "still_number"]
