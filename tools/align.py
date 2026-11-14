#!/usr/bin/env python3
"""Retime a section to its recorded voiceover: every beat and every word gets its measured time.

    ./x align <section> <voiceover.wav>                    the file is this section's narration
    ./x align <section> <full-video.wav> --start 83.2 --end 121.0     this section's part of a longer file
    ./x align <section> <voiceover.wav> --dry              report only, change nothing

It listens to the audio (faster-whisper, word timestamps), matches what it hears to the narration in
beats.json word by word, and writes the measured times back. Scene code names beats and words, never
seconds, so nothing else changes: render again and every move lands on the recorded voice.

Needs the voice extra once:  uv sync --extra voice
The section's part of the audio is copied to <section>/voiceover.wav, so drafts and previews play
with sound. (Audio is never committed: .gitignore covers it.)
"""

from __future__ import annotations

import argparse
import difflib
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from xcore.beats import Beats, dump, norm
from xcore.media import need, probe
from xcore.timing import _weight

PREROLL = 0.1  # a beat starts this long before its first word, so the first move lands on it
TAIL_PAD = 0.3  # the last beat ends this long after its last word


def transcribe(audio: Path, model: str, language: str) -> list[tuple[str, float, float]]:
    try:
        from faster_whisper import WhisperModel
    except ImportError:
        sys.exit("faster-whisper is not installed in this project. Run once:  uv sync --extra voice")
    whisper = WhisperModel(model, device="cpu", compute_type="int8")
    # Hand it samples, not a path: faster-whisper's own decoder and the PyAV that Manim pins disagree.
    segments, _ = whisper.transcribe(samples_16k(audio), language=language, word_timestamps=True, vad_filter=True,
                                     condition_on_previous_text=False)
    words = []
    for seg in segments:
        for w in seg.words or []:
            if norm(w.word):
                words.append((w.word.strip(), float(w.start), float(w.end)))
    return words


def samples_16k(audio: Path):
    """The audio as mono 16 kHz float samples, which is what the recogniser listens to."""
    import numpy as np

    need("ffmpeg")
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", str(audio), "-f", "f32le", "-ac", "1", "-ar", "16000", "-"],
                         check=True, capture_output=True).stdout
    return np.frombuffer(raw, np.float32)


def cut(audio: Path, start: float, end: float | None, dest: Path) -> Path:
    need("ffmpeg")
    cmd = ["ffmpeg", "-v", "error", "-y", "-ss", f"{start:.3f}"]
    if end is not None:
        cmd += ["-t", f"{end - start:.3f}"]
    cmd += ["-i", str(audio), "-ac", "1", "-ar", "48000", "-c:a", "pcm_s16le", str(dest)]
    subprocess.run(cmd, check=True)
    return dest


def match(script: list[str], heard: list[tuple[str, float, float]]) -> list[tuple[float, float] | None]:
    """For each script word, the (start, end) it was heard at, or None when it could not be matched.

    Numbers and names are often transcribed differently ("5000" / "five thousand"); those gaps are
    filled in afterwards from their neighbours.
    """
    a = [norm(w) for w in script]
    b = [norm(w[0]) for w in heard]
    times: list[tuple[float, float] | None] = [None] * len(a)
    for tag, i1, i2, j1, j2 in difflib.SequenceMatcher(a=a, b=b, autojunk=False).get_opcodes():
        if tag == "equal":
            for k in range(i2 - i1):
                times[i1 + k] = (heard[j1 + k][1], heard[j1 + k][2])
        elif tag == "replace" and (i2 - i1) == (j2 - j1):
            # same number of words, spelled differently ("colour" / "color"): trust the positions
            for k in range(i2 - i1):
                times[i1 + k] = (heard[j1 + k][1], heard[j1 + k][2])
    return times


def fill(script: list[str], times: list[tuple[float, float] | None], total: float) -> list[tuple[float, float]]:
    """Give unmatched words a time between their matched neighbours, in proportion to their length."""
    out: list[tuple[float, float]] = [(0.0, 0.0)] * len(script)
    i = 0
    while i < len(script):
        if times[i] is not None:
            out[i] = times[i]  # type: ignore[assignment]
            i += 1
            continue
        j = i
        while j < len(script) and times[j] is None:
            j += 1
        left = out[i - 1][1] if i > 0 else 0.0
        right = times[j][0] if j < len(script) else total  # type: ignore[index]
        weights = [_weight(w) for w in script[i:j]]
        span, acc = max(right - left, 0.0), 0.0
        for k, w in enumerate(weights):
            a = left + span * acc / sum(weights)
            acc += w
            out[i + k] = (a, left + span * acc / sum(weights))
        i = j
    return out


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("section")
    ap.add_argument("audio", type=Path)
    ap.add_argument("--start", type=float, default=0.0, help="where this section begins in the audio file, seconds")
    ap.add_argument("--end", type=float, help="where it ends (default: the end of the file)")
    ap.add_argument("--model", default="small.en", help="faster-whisper model (small.en is plenty for clean narration)")
    ap.add_argument("--language", default="en")
    ap.add_argument("--dry", action="store_true", help="report the new times without writing anything")
    a = ap.parse_args()

    if not a.audio.exists():
        sys.exit(f"{a.audio} does not exist")
    beats = Beats.load(a.section)
    section = beats.dir
    with tempfile.TemporaryDirectory() as tmp:
        piece = cut(a.audio, a.start, a.end, Path(tmp) / "voiceover.wav")
        total = probe_audio(piece)
        heard = transcribe(piece, a.model, a.language)
        if not heard:
            sys.exit("no speech was recognised in that audio")

        script, owner = [], []
        for bi, b in enumerate(beats.beats):
            for tok in b.text.split():
                if norm(tok):
                    script.append(tok)
                    owner.append(bi)
        matched = match(script, heard)
        hit = sum(t is not None for t in matched) / len(script)
        times = fill(script, matched, total)

        data = json.loads((section / "beats.json").read_text(encoding="utf-8"))
        starts = []
        for bi in range(len(beats.beats)):
            first = next(k for k, o in enumerate(owner) if o == bi)
            before = times[first - 1][1] if first > 0 else 0.0
            starts.append(0.0 if bi == 0 else max(times[first][0] - PREROLL, before))
        last_end = min(total, times[-1][1] + TAIL_PAD)
        ends = starts[1:] + [last_end]

        print(f"ALIGN {section.parent.name}/{section.name}: {len(heard)} words heard, {hit:.0%} of the {len(script)} "
              f"script words matched, audio {total:.2f} s")
        print(f"  {'beat':<16} {'was':>8} {'now':>8} {'moved':>8}")
        new_beats = []
        for bi, b in enumerate(data["beats"]):
            words = [[script[k], round(times[k][0], 3), round(times[k][1], 3)] for k, o in enumerate(owner) if o == bi]
            # keep each word inside its beat even when the recogniser's edges disagree by a few ms
            words = [[w, min(max(s, starts[bi]), ends[bi]), min(max(e, starts[bi]), ends[bi])] for w, s, e in words]
            print(f"  {b['name']:<16} {b['start']:8.2f} {starts[bi]:8.2f} {starts[bi] - b['start']:+8.2f}")
            new_beats.append({**b, "start": round(starts[bi], 3), "end": round(ends[bi], 3), "words": words})
        unmatched = [script[k] for k, t in enumerate(matched) if t is None]
        if unmatched:
            print(f"  not heard as written (timed from their neighbours): {' '.join(unmatched[:24])}{' ...' if len(unmatched) > 24 else ''}")
        if hit < 0.85:
            print("  WARNING: under 85% matched. Is this the right audio, the right --start/--end, the final script?")
        tail = max(0.0, round(total - last_end, 3))
        print(f"  section length {last_end + max(tail, 0.4):.2f} s (was {beats.duration:.2f} s)")
        if a.dry:
            print("DRY RUN: nothing written")
            return
        data["beats"] = new_beats
        data["tail"] = round(max(tail, 0.4), 3)
        data["timing"] = {"source": "voiceover", "file": a.audio.name, "model": a.model, "matched": round(hit, 3),
                          **({"start": a.start} if a.start else {}), **({"end": a.end} if a.end else {})}
        (section / "beats.json").write_text(dump(data), encoding="utf-8")
        shutil.copyfile(piece, section / "voiceover.wav")
    errs = Beats.load(section).check()
    if errs:
        sys.exit("BEATS FAIL after alignment\n" + "\n".join("  - " + e for e in errs))
    print(f"WROTE {section / 'beats.json'} and voiceover.wav. Now: ./x draft {section.parent.name}/{section.name}")


def probe_audio(path: Path) -> float:
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(path)],
                         check=True, capture_output=True, text=True).stdout.strip()
    return float(out)


if __name__ == "__main__":
    main()

_ = probe  # the video probe is kept importable for tools that extend this one
