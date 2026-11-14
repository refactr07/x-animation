"""Backdrops as PNG files, one per (style, resolution).

Both engines paint the same file: Manim as its camera background, Remotion as a full-frame image.
That is what keeps a cut between engines from shifting the stage by even a pixel.
"""

from __future__ import annotations

from pathlib import Path

from .paths import PUBLIC
from .tokens import BACKDROPS, TOKENS, rgb

OUT = PUBLIC / "backdrops"
VERSION = 1  # bump when the drawing below changes, so stale files are rebuilt


def backdrop_file(style: str, width: int, height: int) -> Path:
    return OUT / f"{style}_{width}x{height}_v{VERSION}.png"


def backdrop_png(style: str, width: int, height: int) -> Path:
    """Path of the backdrop PNG for this resolution, drawing it first if it is missing."""
    if style not in BACKDROPS["styles"]:
        raise KeyError(f"backdrop {style!r} is not one of {sorted(BACKDROPS['styles'])}")
    path = backdrop_file(style, width, height)
    if not path.exists():
        OUT.mkdir(parents=True, exist_ok=True)
        _draw(style, width, height).save(path, optimize=True)
    return path


def _draw(style: str, width: int, height: int):
    from PIL import Image, ImageDraw

    spec = BACKDROPS["styles"][style]
    pattern = spec.get("pattern")
    if not pattern:
        return Image.new("RGB", (width, height), rgb(spec["bg"]))

    # Draw at 4x and scale down: Pillow has no anti-aliased primitives, and a dot 2 px wide needs them.
    ss = 4
    w, h = width * ss, height * ss
    k = ss * width / TOKENS["layout"]["width"]  # 1080p px -> supersampled px
    img = Image.new("RGB", (w, h), rgb(spec["bg"]))
    pen = ImageDraw.Draw(img)
    step = pattern["spacing_px"] * k
    cx, cy = w / 2, h / 2
    nx, ny = int(cx // step) + 1, int(cy // step) + 1
    ink = rgb(pattern["color"])
    if pattern["kind"] == "dots":
        r = pattern["radius_px"] * k
        for i in range(-nx, nx + 1):
            for j in range(-ny, ny + 1):
                x, y = cx + i * step, cy + j * step
                pen.ellipse([x - r, y - r, x + r, y + r], fill=ink)
    elif pattern["kind"] == "grid":
        half = pattern["width_px"] * k / 2
        for i in range(-nx, nx + 1):
            x = cx + i * step
            pen.rectangle([x - half, 0, x + half, h], fill=ink)
        for j in range(-ny, ny + 1):
            y = cy + j * step
            pen.rectangle([0, y - half, w, y + half], fill=ink)
    else:
        raise ValueError(f"unknown backdrop pattern {pattern['kind']!r}")
    return img.resize((width, height), Image.LANCZOS)


def ensure_all(sizes: list[tuple[int, int]]) -> list[Path]:
    return [backdrop_png(style, w, h) for style in BACKDROPS["styles"] for w, h in sizes]
