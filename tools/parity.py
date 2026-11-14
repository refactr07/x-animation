#!/usr/bin/env python3
"""Do the two engines agree? Render one test card in Manim and in Remotion and measure the difference.

    ./x parity            render videos/kit/00-parity through the normal pipeline, then measure
    ./x parity --keep     measure the last render again without rendering

Both halves of the card come from videos/kit/00-parity/card.json and pass through the same assembly
and encode as a real section, so this tests what a viewer would see at an engine switch:

  colour    every palette colour and its tint, as flat patches        within 3 levels per channel
  type      a line at every size in every family: ink width, height   within 2 px
            and the baseline it sits on                               within 2 px
  strokes   a line at every stroke width                              within 1 px
  backdrop  an empty strip of the stage                               within 3 levels

Run it after changing theme/tokens.json, the fonts, either kit, or upgrading Manim or Remotion.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import av
import numpy as np

from xcore.paths import RENDERS, ROOT
from xcore.tokens import TOKENS

SECTION = ROOT / "videos" / "kit" / "00-parity"
VIDEO = RENDERS / "kit" / "kit_parity_preview.mp4"
TOL = {"colour": 3, "type": 2.0, "stroke": 1.0, "backdrop": 3}


def frame_at(path: Path, t: float) -> np.ndarray:
    with av.open(str(path)) as box:
        stream = box.streams.video[0]
        box.seek(int(max(t - 0.5, 0) / stream.time_base), stream=stream, backward=True)
        for frame in box.decode(stream):
            if frame.time is not None and frame.time + 1e-4 >= t:
                return np.asarray(frame.to_image().convert("RGB")).astype(np.int16)
    sys.exit(f"no frame at {t} s in {path}")


def ink_box(img: np.ndarray, x0: int, y0: int, x1: int, y1: int, level: int = 110):
    """Bounding box (left, top, right, bottom) of bright ink in a region, or None."""
    region = img[y0:y1, x0:x1].max(axis=2) > level
    ys, xs = np.where(region)
    if not len(xs):
        return None
    return x0 + xs.min(), y0 + ys.min(), x0 + xs.max() + 1, y0 + ys.max() + 1


def main() -> None:
    if "--keep" not in sys.argv:
        r = subprocess.run([sys.executable, "-W", "ignore", str(ROOT / "tools" / "render.py"), "preview", str(SECTION)],
                           cwd=ROOT, capture_output=True, text=True)
        if r.returncode not in (0, 2):
            sys.exit(r.stdout[-3000:] + r.stderr[-2000:])
    if not VIDEO.exists():
        sys.exit(f"{VIDEO} is missing: run ./x parity without --keep")
    card = json.loads((SECTION / "card.json").read_text())
    manim, remotion = frame_at(VIDEO, 0.75), frame_at(VIDEO, 2.25)
    fails: list[str] = []

    print("COLOUR (mean RGB of each patch: Manim | Remotion | largest channel difference)")
    for row in ("patch", "tint"):
        spec = card[row]
        for k, name in enumerate(card["colors"]):
            x, y = spec["x0"] + k * spec["dx"], spec["y"]
            box = (slice(y + 16, y + spec["h"] - 16), slice(x + 20, x + spec["w"] - 20))
            a, b = manim[box].reshape(-1, 3).mean(0), remotion[box].reshape(-1, 3).mean(0)
            d = float(np.abs(a - b).max())
            ok = d <= TOL["colour"]
            print(f"  {row:<5} {name:<8} {tuple(int(round(v)) for v in a)!s:<16} {tuple(int(round(v)) for v in b)!s:<16} {d:4.1f} {'' if ok else '  <-- FAIL'}")
            if not ok:
                fails.append(f"colour {row} {name}: {d:.1f} levels apart")

    print("TYPE (ink box of each line: width x height, left edge, baseline; Manim | Remotion)")
    for item in card["text"]:
        size = TOKENS["type"][item["size"]]
        region = (item["x"] - 30, int(item["y"] - size * 1.1), 1150, int(item["y"] + size * 0.45))
        a, b = ink_box(manim, *region), ink_box(remotion, *region)
        label = f"{item['family']} {item['size']}"
        if a is None or b is None:
            fails.append(f"type {label}: no ink found")
            print(f"  {label:<12} no ink found  <-- FAIL")
            continue
        dw, dh = abs((a[2] - a[0]) - (b[2] - b[0])), abs((a[3] - a[1]) - (b[3] - b[1]))
        dbase, dleft = abs(a[3] - b[3]), abs(a[0] - b[0])
        ok = max(dw, dh, dbase) <= TOL["type"] and dleft <= 4
        print(f"  {label:<12} {a[2] - a[0]:4d} x {a[3] - a[1]:<3d} left {a[0]:4d} base {a[3]:4d} | "
              f"{b[2] - b[0]:4d} x {b[3] - b[1]:<3d} left {b[0]:4d} base {b[3]:4d} | "
              f"dw {dw} dh {dh} dbase {dbase} dleft {dleft}{'' if ok else '  <-- FAIL'}")
        if not ok:
            fails.append(f"type {label}: width {dw} px, height {dh} px, baseline {dbase} px, left {dleft} px apart")

    print("STROKES (thickness in px at 1080p: token | Manim | Remotion)")
    for item in card["strokes"]:
        x = (item["x1"] + item["x2"]) // 2
        col = slice(item["y"] - 20, item["y"] + 20)

        def thick(img: np.ndarray) -> float:
            # sum of coverage across the line: anti-aliased edges count for their share
            return float(img[col, x - 40:x + 40].max(axis=2).mean(axis=1).sum() / 255.0)

        want = TOKENS["stroke"][item["name"]]
        a, b = thick(manim), thick(remotion)
        ok = abs(a - b) <= TOL["stroke"] and abs(a - want) <= TOL["stroke"]
        print(f"  {item['name']:<6} {want:5.2f} | {a:5.2f} | {b:5.2f}{'' if ok else '  <-- FAIL'}")
        if not ok:
            fails.append(f"stroke {item['name']}: token {want}, Manim {a:.2f}, Remotion {b:.2f}")

    probe = card["backdrop_probe"]
    box = (slice(probe["y"], probe["y"] + probe["h"]), slice(probe["x"], probe["x"] + probe["w"]))
    diff = np.abs(manim[box] - remotion[box])
    ok = diff.max() <= TOL["backdrop"] * 4 and diff.mean() <= 0.5
    print(f"BACKDROP empty strip: mean difference {diff.mean():.3f} levels, largest {int(diff.max())}{'' if ok else '  <-- FAIL'}")
    if not ok:
        fails.append(f"backdrop: mean {diff.mean():.2f}, max {int(diff.max())} levels apart")

    if fails:
        print(f"\nPARITY FAIL: {len(fails)} difference(s)\n" + "\n".join("  - " + f for f in fails))
        sys.exit(1)
    print("\nPARITY OK: both engines draw the same colours, type, strokes and backdrop")


if __name__ == "__main__":
    main()
