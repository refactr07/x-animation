"""Where things live. Every path in the kit and the tools is derived from ROOT."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]

THEME = ROOT / "theme"
PUBLIC = ROOT / "public"
FONTS = PUBLIC / "fonts"
VIDEOS = ROOT / "videos"
RENDERS = ROOT / "renders"
CACHE = ROOT / ".cache"
STUDIO = ROOT / "studio.json"


def studio() -> dict:
    """studio.json: which video is being worked on right now."""
    return json.loads(STUDIO.read_text()) if STUDIO.exists() else {}


def section_dir(ref: str | Path) -> Path:
    """Resolve a section from any of: a folder, a file inside it, `video/section`, or a bare
    section name (looked up in the active video, then in every video)."""
    p = Path(ref)
    if p.is_file():
        p = p.parent
    if (p / "beats.json").exists():
        return p.resolve()
    if (ROOT / p / "beats.json").exists():
        return (ROOT / p).resolve()
    if (VIDEOS / p / "beats.json").exists():
        return (VIDEOS / p).resolve()
    name = p.name
    active = studio().get("active_video")
    pools = ([VIDEOS / active] if active else []) + sorted(d for d in VIDEOS.glob("*") if d.is_dir())
    for video in pools:
        for cand in sorted(video.glob("*")):
            if (cand / "beats.json").exists() and (cand.name == name or cand.name.split("-", 1)[-1] == name):
                return cand.resolve()
    raise FileNotFoundError(f"no section found for {ref!r} (expected a folder holding beats.json)")


def video_of(section: Path) -> Path:
    return section.parent


def video_config(section: Path) -> dict:
    f = video_of(section) / "video.json"
    return json.loads(f.read_text()) if f.exists() else {}
