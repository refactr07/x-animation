#!/usr/bin/env python3
"""Render the kit's specimen sheets (tools/specimens.py) to docs/assets/kit_*.png.

    ./x specimens
"""

from __future__ import annotations

import shutil
import sys

from xcore.media import run
from xcore.paths import CACHE, ROOT

SCENES = {"Palette": "kit_palette.png", "Shapes": "kit_shapes.png", "Pictograms": "kit_pictograms.png"}

if __name__ == "__main__":
    media = CACHE / "specimens"
    for scene, name in SCENES.items():
        run([sys.executable, "-W", "ignore", "-m", "manim", "render", str(ROOT / "tools" / "specimens.py"), scene, "-s",
             "--format", "png", "--resolution", "1920,1080", "--media_dir", str(media), "--progress_bar", "none",
             "--verbosity", "WARNING", "-o", scene], cwd=ROOT)
        src = next(media.rglob(f"{scene}.png"))
        dest = ROOT / "docs" / "assets" / name
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(src, dest)
        print(f"SPECIMEN: {dest.relative_to(ROOT)}")
