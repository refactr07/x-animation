"""Script text -> beats, and beats -> word times when no voiceover exists yet.

The estimate models speech as words of different lengths with pauses at punctuation, scaled so the
section runs at the chosen pace. It is good to a few tenths of a second per beat, which is enough to
build against; tools/align.py replaces every number with the measured one once the voiceover is recorded.
"""

from __future__ import annotations

import re

from .beats import norm

# Pauses, in units of one average word.
_PAUSE = {",": 0.45, ";": 0.6, ":": 0.6, "—": 0.7, "–": 0.6, ".": 1.0, "!": 1.0, "?": 1.1, "…": 1.1}
_SENTENCE_END = re.compile(r'(?<=[.!?…])["”’)\]]*\s+(?=[“"‘(\[]?[A-Z0-9])')
_CLAUSE = re.compile(r"(?<=[,;:—–])\s+")
MIN_BEAT = 1.5  # seconds: even "Five months." gets room to land
MAX_WORDS = 18  # a longer sentence is split at a clause boundary
LIST_WORDS = 3  # sentences this short that follow each other are one beat (a list of names)

_HINTS = {
    "remotion": (
        "code function terminal command api endpoint json file folder editor commit diff app website browser "
        "screen click button menu chat message prompt reply notification email dashboard table spreadsheet "
        "tweet post feed search result ui interface window tab login password form pricing plan invoice"
    ).split(),
    "manim": (
        "curve graph plot axis slope gradient vector matrix equation formula probability distribution function "
        "network neuron weight layer token embedding dimension space angle distance geometry circle triangle "
        "sum average exponential logarithm derivative integral loss error rate percent ratio scale grows shrinks"
    ).split(),
}


def split_script(text: str) -> list[str]:
    """One beat per sentence; long sentences split at a clause; runs of very short sentences merge."""
    body = "\n".join(line for line in text.splitlines() if not line.lstrip().startswith("#"))
    paragraphs = [re.sub(r"\s+", " ", p).strip() for p in re.split(r"\n\s*\n", body) if p.strip()]
    beats: list[str] = []
    for para in paragraphs:
        sentences = [s.strip() for s in _SENTENCE_END.split(para) if s.strip()]
        run: list[str] = []
        for s in sentences:
            if _count(s) <= LIST_WORDS:
                run.append(s)
                continue
            if run:
                beats.append(" ".join(run))
                run = []
            beats.extend(_split_long(s))
        if run:
            beats.append(" ".join(run))
    return beats


def _count(s: str) -> int:
    return sum(1 for w in s.split() if norm(w))


def _split_long(sentence: str) -> list[str]:
    if _count(sentence) <= MAX_WORDS:
        return [sentence]
    parts = _CLAUSE.split(sentence)
    out: list[str] = []
    cur = ""
    for part in parts:
        trial = f"{cur} {part}".strip()
        if cur and _count(cur) >= 5 and _count(trial) > MAX_WORDS:
            out.append(cur)
            cur = part
        else:
            cur = trial
    if cur:
        if out and _count(cur) < 4:
            out[-1] = f"{out[-1]} {cur}"
        else:
            out.append(cur)
    return out


def name_for(text: str, taken: set[str]) -> str:
    """A CamelCase beat name from the first telling words. Rename them when you plan the section."""
    stop = set("a an the and or but so of to in on at for with by from is are was were be been it its this that these those "
               "as if then than not no you your we our they their i my he she his her will would can could just".split())
    words = [w for w in (norm(x) for x in text.split()) if w and w not in stop and not w.isdigit()]
    base = "".join(w.capitalize() for w in words[:2]) or "Beat"
    base = re.sub(r"^[0-9]+", "", base) or "Beat"
    name, k = base, 2
    while name in taken or name == "END":
        name, k = f"{base}{k}", k + 1
    taken.add(name)
    return name


def hint(text: str) -> str:
    """A first guess at the engine from the words alone. The real choice is docs/ENGINE_ROUTING.md."""
    words = {norm(w) for w in text.split()}
    score = {eng: sorted(w for w in vocab if w in words or w + "s" in words) for eng, vocab in _HINTS.items()}
    if len(score["remotion"]) > len(score["manim"]):
        return "remotion? (" + ", ".join(score["remotion"][:3]) + ")"
    if score["manim"]:
        return "manim (" + ", ".join(score["manim"][:3]) + ")"
    return "manim"


def _weight(token: str) -> float:
    """Relative length of a spoken word: mostly its letters, with a floor for short ones."""
    core = norm(token)
    if core.isdigit():
        return 0.6 + 0.35 * len(core)  # "1,000,000" takes a while to say
    return 0.55 + 0.45 * min(len(core), 14) / 4.7


def _pause(token: str) -> float:
    tail = token.rstrip("\"'”’)]")
    return _PAUSE.get(tail[-1], 0.0) if tail else 0.0


def estimate(texts: list[str], wpm: float = 150.0, start: float = 0.0) -> list[dict]:
    """Beats with start, end and [word, start, end] for every word, at `wpm` including pauses."""
    raw: list[list[tuple[str, float, float]]] = []  # per beat: (token, speak, pause)
    for text in texts:
        row = []
        for tok in text.split():
            if norm(tok):
                row.append((tok, _weight(tok), _pause(tok)))
            elif row:  # a lone dash or ellipsis: a pause on the previous word
                t, s, p = row[-1]
                row[-1] = (t, s, p + _PAUSE.get(tok[-1], 0.4))
        raw.append(row)

    spoken = sum(s for row in raw for _, s, _ in row)
    pauses = sum(p for row in raw for _, _, p in row)
    words = sum(len(row) for row in raw)
    # `wpm` is the pace with pauses included, so one unit of weight is this many seconds:
    unit = (words * 60.0 / wpm) / max(spoken + pauses, 1e-9)

    beats, t = [], start
    for text, row in zip(texts, raw):
        b_start, out = t, []
        for tok, speak, pause in row:
            out.append([tok, round(t, 3), round(t + speak * unit, 3)])
            t += (speak + pause) * unit
        t = max(t, b_start + MIN_BEAT)
        t = round(t, 3)
        beats.append({"text": text, "start": round(b_start, 3), "end": t, "words": out})
    return beats


def retime_linear(beats: list[dict], total: float) -> list[dict]:
    """Stretch estimated beats so the last word ends at `total` seconds (a voiceover's length)."""
    if not beats:
        return beats
    t0, t1 = beats[0]["start"], beats[-1]["end"]
    k = (total - t0) / max(t1 - t0, 1e-9)

    def f(x: float) -> float:
        return round(t0 + (x - t0) * k, 3)

    return [{**b, "start": f(b["start"]), "end": f(b["end"]), "words": [[w[0], f(w[1]), f(w[2])] for w in b["words"]]} for b in beats]
