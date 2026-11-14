# CLAUDE.md: x-animation

A two-engine motion studio for narrated explainer videos in the 3Blue1Brown tradition. A pasted
portion of a script goes in; a verified 3840 x 2160 video whose pictures land on the spoken words
comes out. **Manim Community** draws what transforms, **Remotion** draws what is laid out, and both
read one style (`theme/tokens.json`) and one clock per section (`beats.json`).

## Always

1. **Before planning or changing any animation, read [`FEEDBACK.md`](FEEDBACK.md)** (standing rules
   and the review log) and the active video's `CONTINUITY.md`. `FEEDBACK.md` wins any conflict.
2. **When feedback is given, log it in `FEEDBACK.md` in the same turn**: the words as given, what
   was wrong, the fix, the rule. Never repeat a logged mistake.
3. **In this repository a pasted script is built with this repository's workflow** (the
   `x-animation` skill in `.claude/skills/`), not with any other animation skill installed on the
   machine, unless one is asked for by name.
4. **Never type a colour, a font, a size or a duration into a scene or a component.** Import the
   name (`BLUE`, `BODY`, `P.blue`, `TYPE.body`). Values live in `theme/tokens.json`.
5. **Never put a number of seconds that places a beat into scene code.** `beat()`, `on()`,
   `cue()` and `word()` read `beats.json`.
6. **Verify before delivering.** A draft that says `QA: clean`, sheets that pass your own eye, one
   full-size frame, a final that passed `VERIFY`. An unverified file is not delivered.
7. **Never block a turn on a 4K render.** Run `./x final` in the background; send the draft or the
   preview meanwhile.

## When a script portion is pasted

Work end to end in one turn: plan, build, check, render, deliver. Ask only when the script depends
on data or assets that are not available. The full procedure is
[`docs/WORKFLOW.md`](docs/WORKFLOW.md); in short:

1. **Create:** save the text to a scratch file, then `./x new "Title" --script <file>`. The first
   section of a new video also takes `--video <slug>`, which makes it the active video; `demo` and
   `kit` belong to the repo and never take new sections. The script is kept verbatim in `script.md`.
2. **Plan in `beats.json`:** name the beats, split or merge them (one idea each), give each a
   `"picture"`, choose the engine for each run of beats (`"segments"`), choose the backdrop, fix
   the colour roles. Then `./x time <section>` and `./x check <section>`.
3. **Build:** `./x scaffold <section>`, then write the Manim scenes in `scene.py`
   (`class X(Segment)`, `self.beat()`, `self.on("word")`, `self.finish()`) and the Remotion
   components in `<Component>.tsx` (`useTimeline()`, `cue()`, `word()`).
4. **Draft and look:** `./x draft <section>`. Fix every `TIMING`, `OVERLAP`, `LAYOUT` and `STILL`
   line. Read the storyboard and cue sheets in `renders/<video>/qa/`, and a detail sheet
   (`./x frames`) at every transform and engine switch. Repeat until clean.
5. **Final:** `./x typecheck`, then `./x final <section>` in the background.
6. **Record:** append the section to the video's `CONTINUITY.md`; write the section's `README.md`.
7. **Deliver:** the absolute path and specs, how it plays, engines, colours, the cue sheet
   (format in `docs/WORKFLOW.md`). Plain words about the video, not the code.

Read `videos/demo/01-training` once per session before building: it is the bar.

## Choosing the engine

> Is this beat a picture that **transforms**, or a surface that is **laid out**?

| The beat shows | Engine |
|---|---|
| Diagrams that morph, math, plots, vectors, models and networks, tokens flowing, pictogram metaphors, architecture with signals, 3D space | **Manim** (the default) |
| Code in an editor, a terminal, a product or chat window, tables, counters and readouts in a panel, paragraphs, data-heavy charts, screenshots and footage | **Remotion** |

Switch only at beat boundaries, where the narration changes subject; never for a single short
beat; keep one beat's picture in one engine. Full guide with tie-breakers:
[`docs/ENGINE_ROUTING.md`](docs/ENGINE_ROUTING.md).

## The rules that matter most

From [`FEEDBACK.md`](FEEDBACK.md) and [`STYLE.md`](STYLE.md):

- **Nothing overlaps, ever**, mid-move included. Make room first, then enter.
- **Clean and minimal.** One picture per beat, one focal point, a third of the frame empty, at most
  three accent colours.
- **Dynamic.** Something meaningful changes every couple of seconds; nothing sits still for more
  than 2.5 s; no idle wiggles, pulses, bounces or drifting.
- **On the word.** A change lands on the word that causes it.
- **Minimal text.** Labels of 1 to 3 words, shown after the thing they name, never under 24 px.
  No captions of the narration, bullet lists or titles.
- **Colour is meaning.** One role per colour for the whole video.
- **Continuity.** The central picture transforms; the stage is not cleared. Frame 0 is moving, the
  last frame is a clean still. An engine switch lands on a composed frame.
- **One backdrop per section**; the next section uses a different one.
- **Never looks AI-generated**: see the list at the end of `STYLE.md`.
- **Original pictures only.** No 3Blue1Brown characters, logo or shots; no real brand logos or
  likenesses of real people.

## Commands

```bash
./x help                                  # everything, with one line each
./x new "Title" --script file.txt         # the next section of the active video (--video <slug> starts one)
./x time|check|show|cues <section>        # the beat sheet
./x scaffold <section>                    # starting code for every segment
./x draft <section> [--only Name]         # 960x540 check render + QA sheets
./x still <section> <Component> t1 t2     # Remotion frames without a render
./x frames <video.mp4> t1 t2 ...          # chosen frames of any render
./x preview <section>                     # 1920x1080
./x final <section>                       # 3840x2160 master, verified
./x align <section> voiceover.wav         # retime to a recorded voiceover
./x parity | contrast | specimens | doctor | typecheck | studio
```

`<section>` is a folder, `video/section`, or a section's name or number in the active video.
Python runs through `uv run` (the `./x` wrapper does this).

## Layout

```
theme/tokens.json, backdrops.json   the single source of every colour, size, stroke and duration
kit/python/xcore/                   engine-agnostic: tokens, the beat and cue model, backdrops, media checks
kit/python/xkit/                    the Manim kit: theme, text, motion, shapes, pictograms, Segment
kit/remotion/                       the Remotion kit: theme, time, cues, components, the segment host
videos/<video>/                     video.json (frame rate, pace, colour roles), CONTINUITY.md
videos/<video>/<NN-slug>/           one section: script.md, beats.json, scene.py, <Component>.tsx, README.md
videos/demo/01-training/            the reference section, built in both engines
videos/kit/00-parity/               the engine parity test card
src/                                Remotion entry; sections.generated.tsx is written by ./x sync
tools/                              everything ./x runs
public/fonts/                       Latin Modern (Computer Modern), shared by both engines
renders/, .cache/, public/backdrops/   generated, not committed
docs/                               WORKFLOW, ENGINE_ROUTING, KIT, PITFALLS, RESEARCH
```

## Conventions

- **`beats.json` is the single source of time**: a start for every beat, a time for every word,
  and which engine draws which run of beats. `./x time` writes estimates; `./x align` replaces
  them with measured times. Scene code does not change when it is retimed.
- **Time is counted in frames.** A segment owns exactly the frames between its cues; `Segment`
  pads holds to the frame, and the same rounding rule is used in Python and TypeScript.
- **Both engines paint the same backdrop PNG and load the same font files.** `./x parity` measures
  that they still agree; run it after touching tokens, fonts, either kit, or upgrading an engine.
- **New shapes are built from primitives in the section first**, the kit's way (thin strokes, one
  weight, grey unless they carry a role). A shape a second section needs moves into the kit, gets a
  specimen (`tools/specimens.py`) and is looked at.
- **Engine quirks** that have already cost time are in [`docs/PITFALLS.md`](docs/PITFALLS.md).
  Read it before debugging; add to it after.
- **Media is never committed**: renders, voiceovers and footage are ignored by git.
- **This repository is public.** Keep names, addresses, private paths and unreleased scripts out
  of anything committed; a video's script belongs in the repo only if it may be published.

## Environment

- Python 3.13 through uv (`.venv`), Manim Community 0.22.1 with Typst. Node 24 (`.nvmrc`),
  Remotion 4.0.543 with every `@remotion/*` package on the same version (`npm run upgrade` moves
  them together). ffmpeg for assembly and checks.
- `./x setup` prepares a fresh clone; `./x doctor` says what is missing.
- Remotion is free for individuals and for companies of up to three people; larger companies need
  a company licence (<https://www.remotion.dev/docs/license>).
