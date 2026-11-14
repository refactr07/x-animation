#!/usr/bin/env python3
"""Draw the backdrop PNGs both engines paint: one per style and output size.

    ./x backdrops          every style at 960x540, 1920x1080 and 3840x2160 into public/backdrops/

They are rebuilt on demand by the render pipeline, so this is only needed before opening Remotion
Studio on a fresh clone, or after editing theme/backdrops.json (bump VERSION in
kit/python/xcore/backdrop.py and BACKDROP_VERSION in kit/remotion/theme.ts together).
"""

from xcore.backdrop import ensure_all
from xcore.paths import ROOT

if __name__ == "__main__":
    files = ensure_all([(960, 540), (1920, 1080), (3840, 2160)])
    print(f"BACKDROPS: {len(files)} files in {files[0].parent.relative_to(ROOT)}")
