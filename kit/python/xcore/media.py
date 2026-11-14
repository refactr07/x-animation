"""ffprobe / ffmpeg helpers shared by the tools: probing, verification, the stillness check."""

from __future__ import annotations

import json
import shutil
import subprocess
from dataclasses import dataclass
from fractions import Fraction
from pathlib import Path


def need(tool: str) -> str:
    path = shutil.which(tool)
    if not path:
        raise SystemExit(f"{tool} is not installed (macOS: brew install ffmpeg)")
    return path


def run(cmd: list[str], log: Path | None = None, cwd: Path | None = None, env: dict | None = None) -> str:
    """Run a command, returning its combined output. On failure, raise with the end of the output."""
    proc = subprocess.run([str(c) for c in cmd], cwd=cwd, env=env, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    if log is not None:
        log.parent.mkdir(parents=True, exist_ok=True)
        log.write_text(proc.stdout)
    if proc.returncode != 0:
        tail = "\n".join(proc.stdout.strip().splitlines()[-30:])
        where = f" (full log: {log})" if log else ""
        raise RuntimeError(f"command failed: {' '.join(str(c) for c in cmd[:6])} ...{where}\n{tail}")
    return proc.stdout


@dataclass
class Info:
    width: int
    height: int
    fps: Fraction
    frames: int
    duration: float
    codec: str
    pix_fmt: str
    color_space: str
    color_range: str
    size_mb: float
    has_audio: bool

    @property
    def spec(self) -> str:
        return (f"{self.width}x{self.height} at {float(self.fps):g} fps, {self.duration:.2f} s, {self.frames} frames, "
                f"{self.codec} {self.pix_fmt}, {self.size_mb:.1f} MB")


def probe(path: Path) -> Info:
    need("ffprobe")
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-count_packets", "-show_entries",
         "stream=codec_type,codec_name,width,height,r_frame_rate,nb_read_packets,pix_fmt,color_space,color_range",
         "-show_entries", "format=duration,size", "-of", "json", str(path)],
        check=True, capture_output=True, text=True,
    ).stdout
    data = json.loads(out)
    video = next(s for s in data["streams"] if s.get("codec_type") == "video")
    frames = int(video.get("nb_read_packets") or 0)
    fps = Fraction(video["r_frame_rate"])
    return Info(
        width=int(video["width"]), height=int(video["height"]), fps=fps, frames=frames,
        duration=float(data["format"].get("duration") or (frames / fps if fps else 0)),
        codec=video.get("codec_name", "?"), pix_fmt=video.get("pix_fmt", "?"),
        color_space=video.get("color_space", "unknown"), color_range=video.get("color_range", "unknown"),
        size_mb=int(data["format"].get("size", 0)) / 1e6,
        has_audio=any(s.get("codec_type") == "audio" for s in data["streams"]),
    )


def still_stretches(video: Path, longest: float = 2.5, delta: int = 6, pixels: int = 12, tail: float = 1.0):
    """Stretches of the video in which nothing visibly changes for more than `longest` seconds.

    The video is decoded small (192x108, grey). A frame "moves" when at least `pixels` pixels change
    by more than `delta` levels from the frame before: 12 pixels at that size is about a 35 px
    square at 1080p, so compression shimmer or a blinking cursor does not count as motion. The last
    `tail` seconds (the closing still) are ignored. Returns ([(start, end), ...], share of frames
    that move).
    """
    import numpy as np

    need("ffmpeg")
    w, h = 192, 108
    info = probe(video)
    fps = float(info.fps)
    proc = subprocess.Popen(
        ["ffmpeg", "-v", "error", "-i", str(video), "-vf", f"scale={w}:{h}:flags=area,format=gray", "-f", "rawvideo", "-"],
        stdout=subprocess.PIPE,
    )
    moving, prev = [], None
    while True:
        buf = proc.stdout.read(w * h)
        if len(buf) < w * h:
            break
        frame = np.frombuffer(buf, np.uint8).astype(np.int16)
        moving.append(prev is not None and int((np.abs(frame - prev) > delta).sum()) >= pixels)
        prev = frame
    proc.wait()
    end = len(moving) - int(tail * fps)
    found, i = [], 0
    while i < end:
        if moving[i]:
            i += 1
            continue
        j = i
        while j < end and not moving[j]:
            j += 1
        if (j - i) / fps > longest:
            found.append((i / fps, j / fps))
        i = j
    share = (sum(moving[:end]) / end) if end > 0 else 0.0
    return found, share


def label_font(size: int):
    """A monospace font for the stamps on QA sheets."""
    from PIL import ImageFont

    for name in ("/System/Library/Fonts/Menlo.ttc", "/System/Library/Fonts/Supplemental/Courier New.ttf",
                 "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"):
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            continue
    return ImageFont.load_default()
