#!/usr/bin/env python3
"""Frames of a Remotion segment without rendering it: the quick way to check a layout.

    ./x still <section> <Component> 12.9 14.3 16.6        frames at these SECTION times, as one sheet
    ./x still <section> <Component>                       a frame at every cue the segment owns, and 0.4 s after

Times are section seconds, the same numbers as in the cue sheet and on the QA sheets. Frames are
rendered at 1920x1080 and tiled into renders/<video>/qa/<file>_<Component>_stills.png.
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import sys

from PIL import Image, ImageDraw

from xcore.backdrop import backdrop_png
from xcore.beats import Beats
from xcore.media import label_font, run
from xcore.paths import CACHE, RENDERS, ROOT


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("section")
    ap.add_argument("component")
    ap.add_argument("times", nargs="*", type=float)
    ap.add_argument("--cols", type=int, default=2)
    a = ap.parse_args()

    beats = Beats.load(a.section)
    seg = beats.segment(a.component)
    if seg.engine != "remotion":
        sys.exit(f"{a.component} is a Manim segment: use ./x draft {a.section} --only {a.component}")
    fps = beats.fps
    times = a.times or [t for b in beats.beats_in(seg) for t in (b.start, b.start + 0.4)]
    first = beats.frame(seg.start)
    last = beats.frame_count(seg) - 1
    frames = sorted({min(max(beats.frame(t) - first, 0), last) for t in times})

    backdrop_png(beats.backdrop, 1920, 1080)
    run([sys.executable, str(ROOT / "tools" / "registry.py")], cwd=ROOT)
    comp = re.sub(r"[^A-Za-z0-9]+", "-", f"{beats.dir.parent.name}/{beats.dir.name}") + f"-{seg.name}"
    out = CACHE / "stills" / comp
    shutil.rmtree(out, ignore_errors=True)
    out.mkdir(parents=True)
    run(["npx", "--no-install", "remotion", "render", comp, str(out), f"--frames={','.join(map(str, frames))}",
         "--image-format=png", f"--props={json.dumps({'fps': fps, 'outputWidth': 1920})}", "--log=warn", "--overwrite"], cwd=ROOT)
    files = sorted(out.glob("*.png"))
    if len(files) != len(frames):
        sys.exit(f"expected {len(frames)} frames, Remotion wrote {len(files)} (see {out})")

    w, h = 960, 540
    cols = max(1, min(a.cols, len(files)))
    rows = -(-len(files) // cols)
    sheet = Image.new("RGB", (cols * w, rows * h), (10, 10, 12))
    pen = ImageDraw.Draw(sheet)
    for k, (f, frame) in enumerate(zip(files, frames)):
        x, y = (k % cols) * w, (k // cols) * h
        sheet.paste(Image.open(f).convert("RGB").resize((w, h), Image.LANCZOS), (x, y))
        pen.rectangle([x, y, x + w - 1, y + h - 1], outline=(70, 76, 90))
        t = (frame + first) / fps
        name = next((b.name for b in reversed(beats.beats) if b.start <= t + 1e-3), "")
        stamp, f = f"{t:.2f}s  {name}", label_font(26)
        pen.rectangle([x + 4, y + 4, x + 14 + pen.textlength(stamp, font=f), y + 40], fill=(0, 0, 0))
        pen.text((x + 8, y + 7), stamp, fill=(255, 220, 90), font=f)
    dest = RENDERS / beats.dir.parent.name / "qa" / f"{beats.file}_{seg.name}_stills.png"
    dest.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(dest)
    print(f"STILLS: {dest.resolve()}  ({len(files)} frames of {comp})")


if __name__ == "__main__":
    main()
