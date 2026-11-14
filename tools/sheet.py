#!/usr/bin/env python3
"""QA sheets: look at a render the way a viewer would, without scrubbing it.

    ./x sheet  <video.mp4> [--count 30] [--beats <section>]     storyboard: evenly spaced frames
    ./x frames <video.mp4> 3.2 5.58 7.9 ... [--width 960]       detail: the frames at chosen times
    ./x frames <video.mp4> --cues <section>                     detail: every cue, and 0.4 s after it

Read the storyboard first (does each beat have one clear picture?), then a detail sheet at the
moments evenly spaced frames miss: the middle of every transform, every engine switch, and the
frame each label lands on. Tiles are stamped with their time and, with --beats, their beat.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import av
from PIL import Image, ImageDraw

from xcore.media import label_font

INK = (10, 10, 12)
EDGE = (70, 76, 90)
STAMP = (255, 220, 90)


def duration_of(path: Path) -> float:
    with av.open(str(path)) as box:
        s = box.streams.video[0]
        if box.duration:
            return box.duration / 1_000_000
        return float(s.frames / s.average_rate) if s.frames else 0.0


def grab(path: Path, times: list[float]) -> list[tuple[float, Image.Image]]:
    """The first frame at or after each time (times ascending)."""
    shots = []
    with av.open(str(path)) as box:
        stream = box.streams.video[0]
        for t in sorted(times):
            box.seek(int(max(t - 1.0, 0) / stream.time_base), stream=stream, backward=True)
            last = None
            for frame in box.decode(stream):
                if frame.time is None:
                    continue
                last = frame
                if frame.time + 1e-4 >= t:
                    break
            if last is None:
                sys.exit(f"no frame found at {t} s in {path}")
            shots.append((float(last.time), last.to_image()))
    return shots


def compose(shots, labels, cols: int, width: int, out: Path) -> Path:
    w = min(width, shots[0][1].width)
    h = round(w * shots[0][1].height / shots[0][1].width)
    cols = max(1, min(cols, len(shots)))
    rows = -(-len(shots) // cols)
    sheet = Image.new("RGB", (cols * w, rows * h), INK)
    pen = ImageDraw.Draw(sheet)
    f = label_font(max(12, w // 26))
    for k, ((t, img), label) in enumerate(zip(shots, labels)):
        x, y = (k % cols) * w, (k // cols) * h
        sheet.paste(img.convert("RGB").resize((w, h), Image.LANCZOS), (x, y))
        pen.rectangle([x, y, x + w - 1, y + h - 1], outline=EDGE)
        text = f"{t:.2f}s" + (f"  {label}" if label else "")
        tw = pen.textlength(text, font=f)
        pen.rectangle([x + 4, y + 4, x + 12 + tw, y + 10 + f.size], fill=(0, 0, 0))
        pen.text((x + 8, y + 6), text, fill=STAMP, font=f)
    out.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(out)
    return out


def beat_namer(section: str | None):
    if not section:
        return lambda t: ""
    from xcore.beats import Beats

    b = Beats.load(section)

    def name(t: float) -> str:
        current = ""
        for beat in b.beats:
            if beat.start <= t + 1e-3:
                current = beat.name
        return current

    return name


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("mode", choices=["sheet", "frames"])
    ap.add_argument("video", type=Path)
    ap.add_argument("times", nargs="*", type=float)
    ap.add_argument("--count", type=int, default=30, help="storyboard: about this many frames")
    ap.add_argument("--beats", help="a section: stamp each tile with its beat")
    ap.add_argument("--cues", help="a section: take a frame at every cue and 0.4 s after it")
    ap.add_argument("--offset", type=float, default=0.0, help="section time of the video's first frame (a segment clip)")
    ap.add_argument("--cols", type=int)
    ap.add_argument("--width", type=int)
    ap.add_argument("--out", type=Path)
    a = ap.parse_args()

    total = duration_of(a.video)
    namer = beat_namer(a.beats or a.cues)
    if a.mode == "sheet":
        n = max(2, a.count)
        times = [min(total - 0.02, i * total / (n - 1)) for i in range(n)]
        cols, width, suffix = a.cols or 6, a.width or 384, "sheet"
    else:
        times = list(a.times)
        if a.cues:
            from xcore.beats import Beats

            b = Beats.load(a.cues)
            for beat in b.beats:
                for t in (beat.start, beat.start + 0.4):
                    if 0 <= t - a.offset < total:
                        times.append(t - a.offset)
        if not times:
            sys.exit("frames needs times, or --cues <section>")
        times = [min(max(t, 0.0), max(total - 0.02, 0.0)) for t in times]
        cols, width, suffix = a.cols or 3, a.width or 640, "frames"
    shots = grab(a.video, times)
    labels = [namer(t + a.offset) for t, _ in shots]
    out = a.out or a.video.with_name(f"{a.video.stem}_{suffix}.png")
    print(f"{'STORYBOARD' if a.mode == 'sheet' else 'DETAIL'} SHEET: {compose(shots, labels, cols, width, out).resolve()}")


if __name__ == "__main__":
    main()
