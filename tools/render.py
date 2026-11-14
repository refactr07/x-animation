#!/usr/bin/env python3
"""Render a section: every segment in its own engine, joined into one verified file.

    ./x draft   <section>             960x540, 30 fps: for checking. Run it after every change.
    ./x preview <section>             1920x1080 at the video's frame rate: a quick look to send.
    ./x final   <section>             3840x2160 master. Start it in the background; it takes minutes.
    ./x draft   <section> --only Learn    just one segment (a Manim scene or a Remotion component)

What happens:
  1. beats.json is checked (./x check) and Remotion's registry is brought up to date (./x sync).
  2. Each segment is rendered by its engine to a clip of exactly the frames it owns. Manim scenes
     render in parallel as lossless RGB; Remotion compositions render through its CLI. A clip is
     reused when nothing it depends on has changed (--force renders everything again).
  3. The clips are joined and encoded once: H.264, yuv420p, BT.709. With a voiceover file in the
     section folder (voiceover.wav / .mp3 / .m4a), drafts and previews carry it.
  4. The file is verified (size, frame rate, exact frame count, codec, colour tags), checked for
     still stretches, and two QA sheets are written beside it.

Output: renders/<video>/<file>_draft.mp4, <file>_preview.mp4 or <file>.mp4 (the master).
Exit code 1: the render failed. Exit code 2: it rendered, but a QA check needs attention.
"""

from __future__ import annotations

import argparse
import concurrent.futures as futures
import hashlib
import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path

from xcore.backdrop import backdrop_png
from xcore.beats import Beats, Segment
from xcore.media import need, probe, run, still_stretches
from xcore.paths import CACHE, RENDERS, ROOT
from xcore.tokens import TOKENS

AUDIO = ("voiceover.wav", "voiceover.mp3", "voiceover.m4a", "voiceover.aiff", "voiceover.flac")


def quality(mode: str, beats: Beats) -> dict:
    q = dict(TOKENS["render"][mode])
    q["fps"] = int(q.get("fps") or beats.fps)
    q["mode"] = mode
    return q


def stamp(paths: list[Path], extra: str) -> str:
    """A fingerprint of everything a clip depends on."""
    h = hashlib.sha1(extra.encode())
    for p in sorted(paths):
        if p.is_file():
            h.update(str(p.relative_to(ROOT)).encode())
            h.update(p.read_bytes())
    return h.hexdigest()


def sources(section: Path, engine: str) -> list[Path]:
    shared = [ROOT / "theme" / "tokens.json", ROOT / "theme" / "backdrops.json", section / "beats.json",
              section.parent / "video.json", ROOT / "tools" / "render.py"]
    if engine == "manim":
        return shared + list((ROOT / "kit" / "python").rglob("*.py")) + list(section.glob("*.py"))
    return (shared + list((ROOT / "kit" / "remotion").rglob("*.ts*")) + list((ROOT / "src").glob("*.ts*"))
            + list(section.glob("*.ts*")) + [ROOT / "remotion.config.ts", ROOT / "package.json"])


# ------------------------------------------------------------------ engines
def render_manim(section: Path, seg: Segment, q: dict, clip: Path, log: Path) -> list[str]:
    media = CACHE / "manim" / section.parent.name / section.name / seg.name / q["mode"]
    cmd = [
        sys.executable, "-W", "ignore", "-m", "manim", "render", str(section / "scene.py"), seg.name,
        "--format", "mp4", "--resolution", f"{q['width']},{q['height']}", "--frame_rate", str(q["fps"]),
        "--media_dir", str(media), "--disable_caching", "--progress_bar", "none", "--verbosity", "WARNING",
        # lossless RGB: the one colour conversion happens when the section is assembled
        "--video-codec", "libx264rgb", "--pixel-format", "rgb24",
        "--encoder-option", "crf=0", "--encoder-option", "preset=ultrafast",
    ]
    out = run(cmd, log=log, cwd=ROOT, env={**os.environ, "PYTHONWARNINGS": "ignore"})
    hits = sorted(media.rglob(f"{seg.name}.mp4"), key=lambda p: p.stat().st_mtime)
    hits = [h for h in hits if "partial_movie_files" not in h.parts]
    if not hits:
        raise RuntimeError(f"Manim finished but wrote no {seg.name}.mp4 (log: {log})")
    clip.parent.mkdir(parents=True, exist_ok=True)
    hits[-1].replace(clip)
    return [line for line in out.splitlines() if re.match(r"(CUE|TIMING|OVERLAP|SEGMENT|LAYOUT) ", line)]


def render_remotion(section: Path, seg: Segment, q: dict, clip: Path, log: Path) -> list[str]:
    comp = re.sub(r"[^A-Za-z0-9]+", "-", f"{section.parent.name}/{section.name}") + f"-{seg.name}"
    props = json.dumps({"fps": q["fps"], "outputWidth": q["width"]})
    final = q["mode"] == "final"
    cmd = [
        "npx", "--no-install", "remotion", "render", comp, str(clip),
        f"--props={props}", f"--scale={q['width'] / TOKENS['layout']['width']:g}",
        "--codec=h264", "--pixel-format=yuv420p", "--color-space=bt709",
        f"--crf={6 if final else 12}", f"--x264-preset={'medium' if final else 'veryfast'}",
        f"--image-format={'png' if final else 'jpeg'}", *([] if final else ["--jpeg-quality=95"]),
        f"--concurrency={4 if final else 6}", "--log=warn", "--overwrite",
    ]
    clip.parent.mkdir(parents=True, exist_ok=True)
    run(cmd, log=log, cwd=ROOT)
    return []


def render_segment(beats: Beats, seg: Segment, q: dict, force: bool) -> tuple[Path, list[str], bool]:
    section = beats.dir
    base = CACHE / "clips" / section.parent.name / section.name / q["mode"]
    clip = base / f"{seg.index:02d}_{seg.name}.mp4"
    mark = clip.with_suffix(".stamp")
    notes_file = clip.with_suffix(".notes")
    want = stamp(sources(section, seg.engine), json.dumps([q, seg.name, seg.start, seg.end]))
    if not force and clip.exists() and mark.exists() and mark.read_text() == want:
        return clip, (notes_file.read_text().splitlines() if notes_file.exists() else []), True
    log = CACHE / "logs" / section.parent.name / section.name / f"{q['mode']}_{seg.name}.log"
    engine = render_manim if seg.engine == "manim" else render_remotion
    notes = engine(section, seg, q, clip, log)
    mark.write_text(want)
    notes_file.write_text("\n".join(notes))
    return clip, notes, False


# ------------------------------------------------------------------ assembly
def assemble(beats: Beats, clips: list[tuple[Segment, Path]], q: dict, out: Path, audio: Path | None) -> None:
    need("ffmpeg")
    inputs, chains, labels = [], [], []
    for k, (seg, clip) in enumerate(clips):
        frames = beats.frame_count(seg, q["fps"])
        info = probe(clip)
        if (info.width, info.height) != (q["width"], q["height"]):
            raise RuntimeError(f"{clip.name} is {info.width}x{info.height}, expected {q['width']}x{q['height']}")
        if abs(info.frames - frames) > 2:
            raise RuntimeError(f"segment {seg.name} has {info.frames} frames but owns {frames}: "
                               "its timing is off (does the scene end with self.finish()?)")
        inputs += ["-i", str(clip)]
        steps = []
        if info.pix_fmt.startswith(("gbr", "rgb", "bgr")):
            # Manim's lossless RGB: convert to BT.709 video range here, once, with accurate rounding
            steps.append("scale=out_color_matrix=bt709:out_range=tv:flags=lanczos+accurate_rnd+full_chroma_int")
        steps += ["format=yuv420p", "setsar=1", f"fps={q['fps']}"]
        if info.frames < frames:
            steps.append(f"tpad=stop_mode=clone:stop={frames - info.frames}")
        steps.append(f"trim=end_frame={frames}")
        steps.append("setpts=PTS-STARTPTS")
        chains.append(f"[{k}:v]{','.join(steps)}[v{k}]")
        labels.append(f"[v{k}]")
    graph = ";".join(chains) + f";{''.join(labels)}concat=n={len(clips)}:v=1:a=0[v]"
    cmd = ["ffmpeg", "-v", "error", "-y", *inputs]
    if audio:
        cmd += ["-i", str(audio)]
    cmd += ["-filter_complex", graph, "-map", "[v]"]
    if audio:
        cmd += ["-map", f"{len(clips)}:a:0", "-af", "apad", "-c:a", "aac", "-b:a", "192k", "-t", f"{beats.duration:.4f}"]
    cmd += [
        "-c:v", "libx264", "-preset", q["preset"], "-crf", str(q["crf"]), "-pix_fmt", "yuv420p",
        "-color_primaries", "bt709", "-color_trc", "bt709", "-colorspace", "bt709", "-color_range", "tv",
        "-r", str(q["fps"]), "-movflags", "+faststart", str(out),
    ]
    out.parent.mkdir(parents=True, exist_ok=True)
    run(cmd)


def verify(beats: Beats, q: dict, out: Path) -> list[str]:
    info = probe(out)
    want_frames = beats.frame(beats.duration, q["fps"])
    checks = [
        ("resolution", (info.width, info.height) == (q["width"], q["height"]), f"{info.width}x{info.height}"),
        ("frame rate", info.fps == q["fps"], f"{float(info.fps):g} fps"),
        ("frame count", info.frames == want_frames, f"{info.frames} (want {want_frames})"),
        ("codec", info.codec == "h264", info.codec),
        ("pixel format", info.pix_fmt == "yuv420p", info.pix_fmt),
        ("colour", info.color_space == "bt709" and info.color_range == "tv", f"{info.color_space} / {info.color_range}"),
    ]
    bad = []
    for name, ok, detail in checks:
        print(f"VERIFY {'ok  ' if ok else 'FAIL'} {name:<13}{detail}")
        if not ok:
            bad.append(name)
    return bad


def sheets(beats: Beats, out: Path) -> None:
    qa = out.parent / "qa"
    qa.mkdir(parents=True, exist_ok=True)
    section = str(beats.dir)
    tool = [sys.executable, "-W", "ignore", str(ROOT / "tools" / "sheet.py")]
    for args in (
        ["sheet", str(out), "--beats", section, "--count", "30", "--out", str(qa / f"{out.stem}_sheet.png")],
        ["frames", str(out), "--cues", section, "--out", str(qa / f"{out.stem}_cues.png")],
    ):
        print(subprocess.run(tool + args, capture_output=True, text=True, cwd=ROOT).stdout.strip())


# ------------------------------------------------------------------ main
def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("mode", choices=["draft", "preview", "final"])
    ap.add_argument("section")
    ap.add_argument("--only", help="render just this segment (scene class or component name)")
    ap.add_argument("--force", action="store_true", help="render every segment again, even unchanged ones")
    ap.add_argument("--jobs", type=int, default=3, help="Manim scenes rendered at the same time")
    ap.add_argument("--no-audio", action="store_true", help="leave the voiceover out of a draft or preview")
    a = ap.parse_args()

    started = time.time()
    beats = Beats.load(a.section)
    errs = beats.check()
    if errs:
        sys.exit("BEATS FAIL\n" + "\n".join("  - " + e for e in errs))
    q = quality(a.mode, beats)
    section = beats.dir
    backdrop_png(beats.backdrop, q["width"], q["height"])

    segs = [s for s in beats.segments if not a.only or s.name == a.only]
    if not segs:
        sys.exit(f"no segment named {a.only!r}; segments are: {', '.join(s.name for s in beats.segments)}")
    if any(s.engine == "remotion" for s in segs):
        run([sys.executable, str(ROOT / "tools" / "registry.py")], cwd=ROOT)

    print(f"RENDER {section.parent.name}/{section.name} {a.mode}: {q['width']}x{q['height']} at {q['fps']} fps, "
          f"{beats.duration:.2f} s, backdrop {beats.backdrop}")
    results: dict[int, tuple[Path, list[str], bool]] = {}
    manim = [s for s in segs if s.engine == "manim"]
    with futures.ThreadPoolExecutor(max_workers=max(1, a.jobs)) as pool:
        jobs = {pool.submit(render_segment, beats, s, q, a.force): s for s in manim}
        # Remotion drives several browser tabs per render, so its segments go one at a time
        for s in (x for x in segs if x.engine == "remotion"):
            results[s.index] = render_segment(beats, s, q, a.force)
        for job in futures.as_completed(jobs):
            results[jobs[job].index] = job.result()

    issues: list[str] = []
    for s in segs:
        clip, notes, reused = results[s.index]
        print(f"  {s.engine:<8} {s.name:<18} {s.start:6.2f}-{s.end:6.2f} s  {'reused' if reused else 'rendered'}")
        for line in notes:
            if line.startswith(("TIMING", "OVERLAP", "LAYOUT")):
                print("    " + line)
                issues.append(line)

    name = beats.file + {"draft": "_draft", "preview": "_preview", "final": ""}[a.mode]
    out_dir = RENDERS / section.parent.name
    if a.only:
        out = out_dir / f"{name}_{a.only}.mp4"
        one = [(segs[0], results[segs[0].index][0])]

        class Part:  # a one-segment "section", so the assembler can be reused
            fps, duration, dir = beats.fps, segs[0].duration, beats.dir
            frame_count = staticmethod(beats.frame_count)

        assemble(Part, one, q, out, None)
        print(f"SEGMENT CLIP: {out.resolve()}  ({probe(out).spec})")
        subprocess.run([sys.executable, "-W", "ignore", str(ROOT / "tools" / "sheet.py"), "sheet", str(out), "--count", "18",
                        "--out", str(out_dir / "qa" / f"{out.stem}_sheet.png")], cwd=ROOT)
        sys.exit(2 if issues else 0)

    audio = None if (a.no_audio or a.mode == "final") else next((section / n for n in AUDIO if (section / n).exists()), None)
    out = out_dir / f"{name}.mp4"
    assemble(beats, [(s, results[s.index][0]) for s in segs], q, out, audio)

    bad = verify(beats, q, out)
    if bad:
        sys.exit(f"VERIFY FAILED ({', '.join(bad)}): {out} is not to be delivered")
    limit = TOKENS["motion"]["max_still"]
    stills, share = still_stretches(out, longest=limit)
    for start, end in stills:
        where = next((b.name for b in reversed(beats.beats) if b.start <= start + 1e-3), "?")
        line = f"STILL {start:6.2f}-{end:6.2f} s: {end - start:.1f} s with no visible change (beat {where})"
        print(line)
        issues.append(line)
    print(f"STILLNESS {'FAIL' if stills else 'ok'}: {len(stills)} stretch(es) over {limit:g} s; {share:.0%} of frames move")
    sheets(beats, out)

    print("\nCUE SHEET")
    print(beats.cue_sheet())
    took = time.time() - started
    label = {"draft": "DRAFT", "preview": "PREVIEW", "final": "FINAL"}[a.mode]
    print(f"\n{label}: {out.resolve()}  ({probe(out).spec}{', with voiceover' if audio else ''}; rendered in {took:.0f} s)")
    if issues:
        print(f"QA: {len(issues)} thing(s) to fix before delivering (TIMING, OVERLAP and STILL lines above)")
        sys.exit(2)
    print("QA: clean")


if __name__ == "__main__":
    main()
