"""The timing model. One beats.json per section is the single source of time for both engines.

A section is a list of beats (one idea each, narration verbatim), each with a start, an end and the
time of every word. Segments say which engine draws which run of beats. Scene code never contains a
number of seconds: it names beats and words, so retiming to a voiceover changes this file only.

    b = Beats.load("videos/demo/01-training")
    b.cue("Downhill")                 # seconds from the start of the section
    b.word_time("Downhill", "nudge")  # when that word is spoken
    b.segment("Descent").start        # where a Manim scene or Remotion component begins
"""

from __future__ import annotations

import json
import math
import re
from dataclasses import dataclass, field
from pathlib import Path

from .paths import section_dir, video_config
from .tokens import BACKDROPS, TOKENS

END = "END"
ENGINES = ("manim", "remotion")
_NAME = re.compile(r"^[A-Z][A-Za-z0-9]*$")


def frame_of(seconds: float, fps: float) -> int:
    """The frame a time falls on. Half frames round up, in Python and in TypeScript alike
    (Python's round() goes to the even neighbour, JavaScript's Math.round() goes up)."""
    return math.floor(seconds * fps + 0.5 + 1e-9)


def norm(word: str) -> str:
    """How words are compared: lower case, letters and digits only ("Don't," -> "dont")."""
    return re.sub(r"[^a-z0-9]", "", word.lower().replace("’", "'"))


@dataclass
class Word:
    text: str
    start: float
    end: float


@dataclass
class Beat:
    name: str
    text: str
    start: float
    end: float
    words: list[Word] = field(default_factory=list)
    picture: str = ""

    @property
    def duration(self) -> float:
        return self.end - self.start

    def find(self, phrase: str, nth: int = 1) -> Word:
        """The nth place `phrase` (one word or several) is spoken in this beat. Returns its first word."""
        want = [norm(w) for w in phrase.split() if norm(w)]
        if not want:
            raise ValueError("empty word")
        have = [norm(w.text) for w in self.words]
        hits = [i for i in range(len(have) - len(want) + 1) if have[i : i + len(want)] == want]
        if len(hits) < nth:
            said = " ".join(w.text for w in self.words)
            raise KeyError(f'beat {self.name}: "{phrase}" (occurrence {nth}) is not in its narration: "{said}"')
        return self.words[hits[nth - 1]]


@dataclass
class Segment:
    index: int
    engine: str
    name: str  # Manim scene class or Remotion component
    first: str  # beat it starts on
    until: str  # beat the next segment starts on, or END
    start: float
    end: float

    @property
    def duration(self) -> float:
        return self.end - self.start


class Beats:
    def __init__(self, data: dict, path: Path | None = None):
        self.data = data
        self.path = path
        self.dir = path.parent if path else None
        video = video_config(self.dir) if self.dir else {}
        self.video = video
        self.fps: int = int(data.get("fps") or video.get("fps") or TOKENS["render"]["fps"])
        self.tail: float = float(data.get("tail", 0.8))
        self.backdrop: str = data.get("backdrop", "dots")
        self.beats: list[Beat] = [
            Beat(
                name=b["name"],
                text=b["text"],
                start=float(b["start"]),
                end=float(b["end"]),
                words=[Word(w[0], float(w[1]), float(w[2])) for w in b.get("words", [])],
                picture=b.get("picture", ""),
            )
            for b in data.get("beats", [])
        ]
        self.duration: float = round((self.beats[-1].end if self.beats else 0.0) + self.tail, 4)
        self.segments: list[Segment] = []
        for i, s in enumerate(data.get("segments", [])):
            name = s.get("scene") or s.get("component") or f"segment{i}"
            try:
                start, end = self.cue(s["from"]), self.cue(s["to"])
            except KeyError:
                start, end = 0.0, 0.0  # reported by check()
            self.segments.append(Segment(i, s.get("engine", ""), name, s.get("from", ""), s.get("to", ""), start, end))

    # ------------------------------------------------------------------ loading
    @classmethod
    def load(cls, ref: str | Path) -> "Beats":
        p = Path(ref)
        path = p if p.name == "beats.json" and p.exists() else section_dir(ref) / "beats.json"
        return cls(json.loads(path.read_text(encoding="utf-8")), path.resolve())

    # ------------------------------------------------------------------ lookups
    def beat(self, name: str) -> Beat:
        for b in self.beats:
            if b.name == name:
                return b
        raise KeyError(f"no beat named {name!r}; beats are: {', '.join(b.name for b in self.beats)}")

    def cue(self, name: str | float) -> float:
        """Start of a beat in section seconds. END is the end of the section (last word + tail)."""
        if isinstance(name, (int, float)):
            return float(name)
        if name == END:
            return self.duration
        return self.beat(name).start

    def next_cue(self, name: str) -> float:
        """Where the beat after `name` starts (END after the last one)."""
        names = [b.name for b in self.beats]
        i = names.index(name)
        return self.beats[i + 1].start if i + 1 < len(names) else self.duration

    def word_time(self, beat: str, phrase: str, nth: int = 1) -> float:
        return self.beat(beat).find(phrase, nth).start

    def segment(self, name: str) -> Segment:
        for s in self.segments:
            if s.name == name:
                return s
        raise KeyError(f"no segment named {name!r}; segments are: {', '.join(s.name for s in self.segments)}")

    def beats_in(self, seg: Segment) -> list[Beat]:
        return [b for b in self.beats if seg.start - 1e-6 <= b.start < seg.end - 1e-6]

    def frame(self, seconds: float, fps: float | None = None) -> int:
        return frame_of(seconds, fps or self.fps)

    @property
    def frames(self) -> int:
        return self.frame(self.duration)

    def frame_count(self, seg: Segment, fps: float | None = None) -> int:
        """Frames a segment owns at a frame rate. Computed from frame indices on the section's grid,
        so the segments always add up to the section, with no frame gained or lost at a switch."""
        return self.frame(seg.end, fps) - self.frame(seg.start, fps)

    @property
    def file(self) -> str:
        if self.data.get("file"):
            return self.data["file"]
        number = self.dir.name.split("-", 1)[0] if self.dir else "00"
        prefix = self.video.get("file_prefix") or (self.dir.parent.name if self.dir else "section")
        return f"{prefix}_{number}"

    def cue_sheet(self) -> str:
        rows = [f"{int(b.start // 60):02d}:{b.start % 60:05.2f}  {b.name}" for b in self.beats]
        rows.append(f"{int(self.duration // 60):02d}:{self.duration % 60:05.2f}  {END}")
        return "\n".join(rows)

    # ------------------------------------------------------------------ rules
    def check(self) -> list[str]:
        """Everything that must hold before a render starts. Returns a list of problems."""
        errs: list[str] = []
        if not self.beats:
            return ["no beats: split the script into beats first (./x beats)"]

        seen: set[str] = set()
        t = 0.0
        for i, b in enumerate(self.beats):
            if not _NAME.match(b.name) or b.name == END:
                errs.append(f"beat {i + 1}: name {b.name!r} must be CamelCase letters and digits (END is reserved)")
            if b.name in seen:
                errs.append(f"beat name {b.name!r} is used twice")
            seen.add(b.name)
            if abs(b.start - t) > 1e-3:
                errs.append(f"beat {b.name} starts at {b.start:.3f}s but the previous beat ended at {t:.3f}s")
            if b.end <= b.start:
                errs.append(f"beat {b.name} ends before it starts")
            t = b.end
            spoken = [w for w in b.text.split() if norm(w)]
            if [norm(w.text) for w in b.words] != [norm(w) for w in spoken]:
                errs.append(f"beat {b.name}: its word times do not match its narration (rerun ./x beats time)")
            last = b.start
            for w in b.words:
                if w.start < last - 1e-3 or w.end > b.end + 1e-3 or w.end < w.start:
                    errs.append(f'beat {b.name}: word "{w.text}" ({w.start:.2f}-{w.end:.2f}s) is out of order or outside the beat')
                    break
                last = w.start

        segs = self.data.get("segments", [])
        if not segs:
            errs.append("no segments: say which engine draws each run of beats (docs/ENGINE_ROUTING.md)")
        expect = self.beats[0].name
        names: set[str] = set()
        for i, s in enumerate(segs):
            who = s.get("scene") or s.get("component") or f"#{i + 1}"
            if s.get("engine") not in ENGINES:
                errs.append(f"segment {who}: engine must be one of {ENGINES}")
            if s.get("engine") == "manim" and not s.get("scene"):
                errs.append(f"segment #{i + 1}: a manim segment names its scene class in 'scene'")
            if s.get("engine") == "remotion" and not s.get("component"):
                errs.append(f"segment #{i + 1}: a remotion segment names its component in 'component'")
            if who in names:
                errs.append(f"segment name {who!r} is used twice")
            names.add(who)
            for key in ("from", "to"):
                if s.get(key) != END and s.get(key) not in seen:
                    errs.append(f"segment {who}: '{key}' is {s.get(key)!r}, which is not a beat")
            if s.get("from") != expect:
                errs.append(f"segment {who} starts on {s.get('from')!r} but should start on {expect!r} (segments must be contiguous)")
            expect = s.get("to")
        if segs and expect != END:
            errs.append(f"the last segment must run to {END!r}, not {expect!r}")
        for s in self.segments:
            if s.end - s.start < 1.0 - 1e-6 and not any(e.startswith(f"segment {s.name}") for e in errs):
                errs.append(f"segment {s.name} lasts {s.end - s.start:.2f}s: an engine switch needs at least 1s on screen")

        if self.backdrop not in BACKDROPS["styles"]:
            errs.append(f"backdrop {self.backdrop!r} is not one of {sorted(BACKDROPS['styles'])}")
        elif self.dir is not None:
            policy = self.video.get("backdrop_policy", BACKDROPS["policy"]["default"])
            prev = previous_section(self.dir)
            if policy == "rotate" and prev is not None:
                before = json.loads((prev / "beats.json").read_text()).get("backdrop")
                if before == self.backdrop:
                    errs.append(
                        f"backdrop {self.backdrop!r} repeats the previous section ({prev.name}): "
                        "pick a different one, or set backdrop_policy to 'fixed' in video.json"
                    )
        return errs


def previous_section(section: Path) -> Path | None:
    """The section numbered just below this one in the same video."""
    try:
        n = int(section.name.split("-", 1)[0])
    except ValueError:
        return None
    best: tuple[int, Path] | None = None
    for d in section.parent.iterdir():
        try:
            m = int(d.name.split("-", 1)[0])
        except ValueError:
            continue
        if m < n and (d / "beats.json").exists() and (best is None or m > best[0]):
            best = (m, d)
    return best[1] if best else None


def dump(data: dict) -> str:
    """beats.json text: one beat per block, word times on one line, so diffs stay readable."""
    head = {k: v for k, v in data.items() if k not in ("beats", "segments")}
    lines = json.dumps(head, indent=2, ensure_ascii=False).rstrip("}\n").rstrip() + ",\n"
    lines += '  "beats": [\n'
    blocks = []
    for b in data.get("beats", []):
        rows = [
            f'      "name": {json.dumps(b["name"])}',
            f'      "text": {json.dumps(b["text"], ensure_ascii=False)}',
            f'      "start": {b["start"]:.3f}',
            f'      "end": {b["end"]:.3f}',
        ]
        if b.get("picture"):
            rows.append(f'      "picture": {json.dumps(b["picture"], ensure_ascii=False)}')
        words = ", ".join(f"[{json.dumps(w[0], ensure_ascii=False)}, {w[1]:.3f}, {w[2]:.3f}]" for w in b.get("words", []))
        rows.append(f'      "words": [{words}]')
        blocks.append("    {\n" + ",\n".join(rows) + "\n    }")
    lines += ",\n".join(blocks) + "\n  ],\n"
    lines += '  "segments": [\n'
    lines += ",\n".join("    " + json.dumps(s, ensure_ascii=False) for s in data.get("segments", []))
    lines += "\n  ]\n}\n"
    return lines
