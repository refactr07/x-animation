#!/usr/bin/env python3
"""Find still stretches in a render: nothing on screen should sit unchanged for long.

    ./x stillness <video.mp4> [--max 2.5] [--beats <section>]

A picture that holds for more than a couple of seconds loses the viewer. This reports every stretch
longer than --max seconds in which nothing visibly changes (compression shimmer and a blinking
cursor do not count: a change has to be about a 35 px square at 1080p). The closing second is
ignored. Exit code 1 when a stretch is found. The render pipeline runs this on every render.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from xcore.media import still_stretches
from xcore.tokens import TOKENS


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("video", type=Path)
    ap.add_argument("--max", type=float, default=TOKENS["motion"]["max_still"])
    ap.add_argument("--beats", help="a section, to name the beat each stretch falls in")
    a = ap.parse_args()
    beats = None
    if a.beats:
        from xcore.beats import Beats

        beats = Beats.load(a.beats)
    found, share = still_stretches(a.video, longest=a.max)
    for start, end in found:
        where = ""
        if beats:
            where = " (beat " + next((b.name for b in reversed(beats.beats) if b.start <= start + 1e-3), "?") + ")"
        print(f"STILL {start:6.2f}-{end:6.2f} s: {end - start:.1f} s with no visible change{where}")
    print(f"STILLNESS {'FAIL' if found else 'ok'}: {len(found)} stretch(es) over {a.max:g} s; {share:.0%} of frames move")
    sys.exit(1 if found else 0)


if __name__ == "__main__":
    main()
