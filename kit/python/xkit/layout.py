"""Layout rules as code: the safe area, and the rule that no two objects ever overlap.

check_layout() tests one composed frame before it is played. The overlap audit is run by Segment on
every tenth of a second of every animation, so a collision in the middle of a move is caught too.
"""

from __future__ import annotations

import numpy as np
from manim import Arc, Line, Mobject, TracedPath, ValueTracker, config

from .theme import CLEARANCE, MARGIN_X, MARGIN_Y


def safe_box() -> tuple[float, float, float, float]:
    """(left, bottom, right, top) of the safe area in Manim units."""
    hw, hh = config.frame_width / 2 - MARGIN_X, config.frame_height / 2 - MARGIN_Y
    return -hw, -hh, hw, hh


def _box(m: Mobject) -> tuple[float, float, float, float]:
    (x0, y0, _), (x1, y1, _) = m.get_corner([-1, -1, 0]), m.get_corner([1, 1, 0])
    return float(x0), float(y0), float(x1), float(y1)


def describe(m: Mobject) -> str:
    x0, y0, x1, y1 = _box(m)
    name = getattr(m, "x_name", "") or type(m).__name__
    return f"{name} [x {x0:.2f}..{x1:.2f}, y {y0:.2f}..{y1:.2f}]"


def named(mob: Mobject, name: str) -> Mobject:
    """Give a mobject a name for layout and overlap messages."""
    mob.x_name = name
    return mob


def check_layout(*mobs: Mobject, gap: float = CLEARANCE) -> None:
    """Raise if anything leaves the safe area or two things overlap (by bounding box).

    Call it on the labels and key shapes of a composed frame before playing it. For a layout that
    only exists after a move, check transformed copies. Do not pass a ring together with what it
    surrounds (its box always contains it); the QA sheet covers those.
    """
    left, bottom, right, top = safe_box()
    boxes = []
    for i, m in enumerate(mobs):
        x0, y0, x1, y1 = _box(m)
        if x0 < left - 1e-6 or x1 > right + 1e-6 or y0 < bottom - 1e-6 or y1 > top + 1e-6:
            raise ValueError(f"LAYOUT: item {i} leaves the safe area: {describe(m)}")
        boxes.append((x0, y0, x1, y1))
    for i in range(len(boxes)):
        for j in range(i + 1, len(boxes)):
            a, b = boxes[i], boxes[j]
            if a[0] < b[2] + gap and b[0] < a[2] + gap and a[1] < b[3] + gap and b[1] < a[3] + gap:
                raise ValueError(f"LAYOUT: items {i} and {j} overlap: {describe(mobs[i])} / {describe(mobs[j])}")


# ------------------------------------------------------------------ the overlap audit
def allow_overlap(*mobs: Mobject) -> Mobject | None:
    """Mark objects the audit should ignore: a deliberate crossing (a signal travelling into a box,
    pages pouring into a model). Undo with watch_again() once it has landed."""
    for m in mobs:
        for sm in m.get_family():
            sm.x_overlap_ok = True
    return mobs[0] if mobs else None


def watch_again(*mobs: Mobject) -> None:
    for m in mobs:
        for sm in m.get_family():
            sm.x_overlap_ok = False


_part_counter = [0]


def parts_of(group: Mobject) -> Mobject:
    """Declare that the pieces of `group` are one object (the faces of a box, the cells of a grid,
    the bars of a chart). The audit never compares two pieces of one object, even while they are
    animated in one by one. Copies keep the mark."""
    _part_counter[0] += 1
    token = _part_counter[0]
    for sm in group.get_family():
        sm.x_part_of = token
    return group


def frames(box: Mobject, target: Mobject) -> Mobject:
    """Declare that `box` is a frame around `target` (a highlight box, an underline, a brace)."""
    box.x_frames = target
    return box


def _token(m: Mobject):
    tok = getattr(m, "x_part_of", None)
    if tok is not None:
        return tok
    toks = {getattr(sm, "x_part_of", None) for sm in m.family_members_with_points()}
    return toks.pop() if len(toks) == 1 else None


def _is_frame_of(box: Mobject, other: Mobject) -> bool:
    target = getattr(box, "x_frames", None)
    if target is None:
        return False
    fam = other.get_family()
    return target in fam or any(t in fam for t in target.get_family())


def _connector(m: Mobject) -> bool:
    """Lines and arrows, or a plain group made only of them. Connectors are meant to touch things."""
    if type(m).__name__ in ("Arrow", "DoubleArrow", "CurvedArrow", "CurvedDoubleArrow", "DashedLine", "Brace"):
        return True
    if isinstance(m, (Line, Arc, TracedPath)) and not m.submobjects:
        return True
    if getattr(m, "x_connector", False):
        return True
    return type(m).__name__ in ("VGroup", "Group") and bool(m.submobjects) and all(_connector(sm) for sm in m.submobjects)


def _allowed(m: Mobject) -> bool:
    if getattr(m, "x_overlap_ok", False):
        return True
    fam = m.family_members_with_points()
    return bool(fam) and all(getattr(sm, "x_overlap_ok", False) for sm in fam)


def _visible(m: Mobject, threshold: float) -> bool:
    fam = m.family_members_with_points()
    if not fam:
        return False
    best = 0.0
    for sm in fam:
        try:
            stroke = float(sm.get_stroke_opacity()) if sm.get_stroke_width() > 0 else 0.0
            best = max(best, float(sm.get_fill_opacity()), stroke)
        except (AttributeError, TypeError):
            return True  # images and other non-vector objects: treat as visible
        if best >= threshold:
            return True
    return False


def _outline(m: Mobject, per_curve: int = 8, cap: int = 2500) -> np.ndarray:
    """Points sampled along every drawn curve (control points alone are too sparse)."""
    pts = []
    for sm in m.family_members_with_points():
        p = sm.points
        if len(p) >= 4 and len(p) % 4 == 0:
            c = p.reshape(-1, 4, 3)
            t = np.linspace(0, 1, per_curve)[:, None, None]
            u = 1 - t
            pts.append((u**3 * c[:, 0] + 3 * u * u * t * c[:, 1] + 3 * u * t * t * c[:, 2] + t**3 * c[:, 3]).reshape(-1, 3))
        elif len(p):
            pts.append(p)
    if not pts:
        return np.zeros((0, 2))
    a = np.concatenate(pts)[:, :2]
    if len(a) > cap:
        a = a[np.linspace(0, len(a) - 1, cap).astype(int)]
    return a


def find_overlaps(mobs, clearance: float = CLEARANCE, visible: float = 0.6) -> list[tuple[Mobject, Mobject]]:
    """Pairs of visible top-level objects whose drawn outlines come within `clearance` of each other:
    crossing, touching, or sitting on each other's lines.

    Something wholly inside another (text on a card, a region inside a region, a highlight frame
    round a row) is fine as long as it keeps clear of the container's outline. Skipped: connectors
    (lines, arrows, braces), objects still fading (opacity below `visible`), anything marked with
    allow_overlap(), pieces of one parts_of() object, and trackers.
    """
    from scipy.spatial import cKDTree

    items = [
        (m, _box(m))
        for m in mobs
        if not isinstance(m, ValueTracker) and not _allowed(m) and not _connector(m) and _visible(m, visible)
    ]
    cache: dict[int, np.ndarray] = {}
    bad = []
    for i in range(len(items)):
        for j in range(i + 1, len(items)):
            (a, A), (b, B) = items[i], items[j]
            ta, tb = _token(a), _token(b)
            if ta is not None and ta == tb:
                continue
            if _is_frame_of(a, b) or _is_frame_of(b, a):
                continue
            if min(A[2], B[2]) - max(A[0], B[0]) <= -clearance or min(A[3], B[3]) - max(A[1], B[1]) <= -clearance:
                continue  # bounding boxes are apart
            pa = cache.setdefault(id(a), _outline(a))
            pb = cache.setdefault(id(b), _outline(b))
            if not len(pa) or not len(pb):
                continue
            d, _ = cKDTree(pb).query(pa, k=1, distance_upper_bound=clearance)
            if (d < clearance).any():
                bad.append((a, b))
    return bad


__all__ = ["safe_box", "check_layout", "allow_overlap", "watch_again", "parts_of", "frames", "named",
           "find_overlaps", "describe"]
