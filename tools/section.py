#!/usr/bin/env python3
"""Sections: create one from a pasted script, time its beats, check its rules.

    ./x new "Hook" --video my-video --script script.txt  the first section of a new video (it becomes the active one)
    ./x new "The problem" --script script.txt            the next section of the active video
    ./x time  <section> [--wpm 150] [--total 41.2]       recompute every beat and word time from the text
    ./x check <section>                                  the rules a render needs (exit 1 on a problem)
    ./x cues  <section>                                  the cue sheet
    ./x show  <section>                                  beats with times, engine and picture

<section> is a folder, `video/section`, or just the section's name or number in the active video.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

from xcore.beats import END, Beats, dump, norm, previous_section
from xcore.paths import ROOT, STUDIO, VIDEOS, section_dir, studio
from xcore.timing import estimate, hint, name_for, retime_linear, split_script
from xcore.tokens import BACKDROPS, TOKENS

RESERVED = ("demo", "kit")  # the reference section and the self-tests: never a home for new sections

CONTINUITY = """# Continuity: {title}

Read this before planning a section and add a block after delivering one. It keeps every section of
the video in one visual language: the same colour for the same idea, the same shape for the same
thing, and each section opening where the last one left off.

## Video

- Topic:
- Colour roles (fixed for the whole video): blue = , teal = , yellow = the thing to look at, red = wrong, green = right
- Central picture:
- Recurring shapes (kit call, size, where it sits):
- Promises made to the viewer (a callback is owed later):

## Sections

<!-- One block per delivered section:
### NN · slug · file · duration
- Engines: which beats Manim drew, which Remotion drew, and why
- Backdrop:
- Introduced: new shapes and what they stand for
- Ends on: the final composed frame, with positions
- Next opens on: what the next section should bring back first
-->
"""


def slugify(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")[:48] or "section"


def camel(text: str) -> str:
    words = re.findall(r"[A-Za-z0-9]+", text)
    name = "".join(w[:1].upper() + w[1:] for w in words) or "Scene"
    return name if name[0].isalpha() else "S" + name


def narration_words(script: str) -> list[str]:
    body = "\n".join(line for line in script.splitlines() if not line.lstrip().startswith("#"))
    return [norm(w) for w in body.split() if norm(w)]


def ensure_video(slug: str, title: str | None = None) -> Path:
    video = VIDEOS / slug
    video.mkdir(parents=True, exist_ok=True)
    cfg = video / "video.json"
    if not cfg.exists():
        cfg.write_text(json.dumps({
            "title": title or slug.replace("-", " ").title(),
            "fps": TOKENS["render"]["fps"],
            "wpm": 150,
            "file_prefix": slug,
            "backdrop_policy": BACKDROPS["policy"]["default"],
            "roles": {},
        }, indent=2) + "\n")
        print(f"created {cfg.relative_to(ROOT)}")
    cont = video / "CONTINUITY.md"
    if not cont.exists():
        cont.write_text(CONTINUITY.format(title=title or slug))
    return video


def next_backdrop(video: Path, number: int) -> str:
    rotation = BACKDROPS["policy"]["rotation"]
    prev = previous_section(video / f"{number:02d}-x")
    if prev is None:
        return rotation[0]
    before = json.loads((prev / "beats.json").read_text()).get("backdrop")
    return rotation[(rotation.index(before) + 1) % len(rotation)] if before in rotation else rotation[0]


def build_beats(texts: list[str], wpm: float, names: list[str] | None = None) -> list[dict]:
    taken: set[str] = set(names or [])
    out = []
    for i, b in enumerate(estimate(texts, wpm)):
        name = names[i] if names and i < len(names) else name_for(b["text"], taken)
        out.append({"name": name, **b})
    return out


def cmd_new(a) -> None:
    script = Path(a.script).read_text(encoding="utf-8") if a.script and a.script != "-" else sys.stdin.read()
    if not script.strip():
        sys.exit("the script is empty: pass --script FILE or pipe the text in")
    slug = a.video or studio().get("active_video")
    if slug and not (VIDEOS / slug).exists() and not a.video:
        slug = None  # studio.json names a video that is gone
    if slug in RESERVED and not a.video:
        sys.exit(f"The active video is {slug!r}, which belongs to the repo itself. Start your own video:\n"
                 f'  ./x new "{a.title}" --video <video-slug> --script <file>\n'
                 "Later sections of that video need no --video: it becomes the active one.")
    if not slug:
        sys.exit('There is no active video. Start one:  ./x new "Title" --video <video-slug> --script <file>')
    video = ensure_video(slug)
    STUDIO.write_text(json.dumps({**studio(), "active_video": slug}, indent=2) + "\n")
    cfg = json.loads((video / "video.json").read_text())

    numbers = [int(d.name.split("-", 1)[0]) for d in video.iterdir() if d.is_dir() and d.name[:2].isdigit()]
    number = max(numbers, default=0) + 1
    folder = video / f"{number:02d}-{slugify(a.title)}"
    folder.mkdir()
    (folder / "script.md").write_text(script.rstrip() + "\n", encoding="utf-8")

    texts = split_script(script)
    beats = build_beats(texts, float(a.wpm or cfg.get("wpm", 150)))
    data = {
        "section": folder.name,
        "title": a.title,
        "file": f"{cfg.get('file_prefix', slug)}_{number:02d}",
        "backdrop": a.backdrop or next_backdrop(video, number),
        "timing": {"source": "estimate", "wpm": float(a.wpm or cfg.get("wpm", 150))},
        "tail": 0.8,
        "beats": beats,
        "segments": [{"engine": "manim", "scene": camel(a.title), "from": beats[0]["name"], "to": END}],
    }
    (folder / "beats.json").write_text(dump(data), encoding="utf-8")
    print(f"created {folder.relative_to(ROOT)}  ({len(beats)} beats, {beats[-1]['end'] + 0.8:.1f} s, backdrop {data['backdrop']})\n")
    for b in beats:
        print(f"  {b['start']:6.2f}  {b['name']:<18} {hint(b['text']):<26} {b['text']}")
    print("\nNext: rename the beats, give each a picture, choose the engine per run of beats "
          "(docs/ENGINE_ROUTING.md) in beats.json,\nthen ./x time, ./x scaffold and build.")


def cmd_time(a) -> None:
    folder = section_dir(a.section)
    path = folder / "beats.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    texts = [b["text"] for b in data["beats"]]
    names = [b["name"] for b in data["beats"]]
    script = (folder / "script.md").read_text(encoding="utf-8") if (folder / "script.md").exists() else ""
    if script:
        want, have = narration_words(script), [norm(w) for t in texts for w in t.split() if norm(w)]
        if want != have:
            k = next((i for i, (x, y) in enumerate(zip(want, have)) if x != y), min(len(want), len(have)))
            sys.exit(f"the beats no longer say what script.md says (first difference at word {k + 1}: "
                     f"script {want[k:k + 4]} vs beats {have[k:k + 4]}). Narration is verbatim: fix the beat texts.")
    wpm = float(a.wpm or data.get("timing", {}).get("wpm") or 150)
    timed = estimate(texts, wpm)
    if a.total:
        timed = retime_linear(timed, float(a.total))
    old = {b["name"]: b for b in data["beats"]}
    data["beats"] = [
        {"name": n, **({"picture": old[n]["picture"]} if old[n].get("picture") else {}), **t}
        for n, t in zip(names, timed)
    ]
    data["timing"] = {"source": "estimate", "wpm": wpm, **({"fitted_to": float(a.total)} if a.total else {})}
    path.write_text(dump(data), encoding="utf-8")
    b = Beats.load(folder)
    print(f"timed {len(b.beats)} beats at {wpm:g} wpm" + (f", fitted to {a.total} s" if a.total else "") + f": {b.duration:.2f} s")
    print(b.cue_sheet())


def cmd_check(a) -> None:
    b = Beats.load(a.section)
    errs = b.check()
    if errs:
        print("BEATS FAIL\n" + "\n".join("  - " + e for e in errs))
        sys.exit(1)
    engines = ", ".join(f"{s.name} ({s.engine}, {s.duration:.1f}s)" for s in b.segments)
    print(f"BEATS OK: {len(b.beats)} beats, {b.duration:.2f} s at {b.fps} fps, backdrop {b.backdrop}, file {b.file}\n  {engines}")


def cmd_cues(a) -> None:
    print(Beats.load(a.section).cue_sheet())


def cmd_show(a) -> None:
    b = Beats.load(a.section)
    owner = {}
    for s in b.segments:
        for beat in b.beats_in(s):
            owner[beat.name] = f"{s.engine}:{s.name}"
    for beat in b.beats:
        print(f"{beat.start:6.2f}-{beat.end:6.2f}  {beat.name:<16} {owner.get(beat.name, '?'):<26} {beat.text}")
        if beat.picture:
            print(f"{'':15}{'':16} {'':26} -> {beat.picture}")
    print(f"{b.duration:6.2f}         {END}")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    n = sub.add_parser("new")
    n.add_argument("title")
    n.add_argument("--video")
    n.add_argument("--script")
    n.add_argument("--wpm", type=float)
    n.add_argument("--backdrop", choices=sorted(BACKDROPS["styles"]))
    n.set_defaults(fn=cmd_new)
    t = sub.add_parser("time")
    t.add_argument("section")
    t.add_argument("--wpm", type=float)
    t.add_argument("--total", type=float, help="voiceover length in seconds up to the last word")
    t.set_defaults(fn=cmd_time)
    for name, fn in (("check", cmd_check), ("cues", cmd_cues), ("show", cmd_show)):
        p = sub.add_parser(name)
        p.add_argument("section")
        p.set_defaults(fn=fn)
    a = ap.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
