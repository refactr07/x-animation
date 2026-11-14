# Research: what this system is built on

Three things were studied before any of this was written: how 3Blue1Brown's videos are made, what
Manim Community Edition can and cannot do today, and what Remotion is good at. This file records what
was found, where, and which design decision each finding led to. Version facts are as of
**13 November 2026**.

## 1. 3Blue1Brown

### Where the facts come from

| Source | What it holds |
|---|---|
| [3b1b/videos](https://github.com/3b1b/videos) | The scene code behind the videos, his `custom_config.yml`, his workflow notes |
| [3b1b/manim](https://github.com/3b1b/manim) (ManimGL) | The library he uses: `default_config.yml`, `rate_functions.py`, animation defaults |
| Two of his videos, measured frame by frame for an earlier project | An overview of large language models and the first transformer chapter of his deep learning series: cuts, holds, easing, type sizes |

His scene code is licensed CC BY-NC-SA, so it was read and measured, never copied. Everything here
is drawn from primitives of our own; the colour values and the easing curve come from the Manim
library itself, which is MIT licensed.

### His settings (`custom_config.yml`)

| Setting | Value |
|---|---|
| Resolution, frame rate | 3840 x 2160, 30 fps |
| Background | `#000000`, pure black (ManimGL's own default is `#333333`) |
| Text font | CMU Serif, centred; math through LaTeX in Computer Modern |
| Encoder | `saturation: 1.5` is applied when a file is written |

### ManimGL's defaults, which are the look

| Default | Value |
|---|---|
| Easing of every animation | `smooth(t) = t^3 (10 s^2 + 5 s t + t^2)` with `s = 1 - t`, which is smootherstep `6t^5 - 15t^4 + 10t^3` |
| Run time of an animation | 1 second |
| `self.wait()` | 1 second |
| Stroke | width 4, colour `GREY_A #DDDDDD` |
| Palette | `BLUE_C #58C4DD`, `TEAL_C #5CD0B3`, `GREEN_C #83C167`, `YELLOW_C #FFFF00`, `GOLD_C #F0AC5F`, `RED_C #FC6255`, greys `#DDDDDD #BBBBBB #888888 #444444 #222222` |
| Frame | 8 units tall; buffers 0.1 / 0.25 / 0.5 / 1.0 |

### What his code actually does

Counted over the 38 files (56,643 lines) of his 2024 transformer series and his 2025 videos:

| | |
|---|---|
| Most used moves | `.animate` 1,784 · `FadeIn` 1,213 · `FadeOut` 1,019 · `Write` 552 · `ShowCreation` 480 · `TransformFromCopy` 461 · `LaggedStart` and `LaggedStartMap` 804 · `FadeTransform` 201 · `GrowArrow` 157 · `ReplacementTransform` 139 |
| Almost never used | `Flash` 4 · `Wiggle` 1 · `Uncreate` 5 · `DrawBorderThenFill` 9 |
| Easing | The default (smootherstep) nearly always. Stated otherwise 170 times: `linear` 71, `there_and_back` 34, `there_and_back_with_pause` 15 |
| Run times written out (1,368) | 2 s: 417 · 3 s: 243 · 1 s: 155 · 5 s: 122 · 4 s: 117. Everything not written out runs 1 s |
| `lag_ratio` (1,054) | median 0.1; then 0.25, 0.5, 0.01, 0.05 |
| Waits (2,340) | 1 s: 1,869 · 2 s: 123 · 3 s: 98 |
| Colours named | `YELLOW` 504 · `WHITE` 365 · `BLUE` 333 · `RED` 250 · `TEAL` 210 · `GREEN` 98 · `GREY_B` 94 · `PINK` 64 |
| Devices | `SurroundingRectangle` 360 · colour-coded math terms (`t2c`) 579 · `time_span=` (staggering inside one play) 325 · `set_backstroke` 109 · `fix_in_frame` 146 · `Brace` 110 |
| Camera | `frame.reorient` 392 (3D), `frame.set_height` 57 |
| Type sizes (ManimGL units) | 72, 36, 60, 24, 90, 48 |

### What the two measured videos show

| | |
|---|---|
| Cuts | 1.9 to 2.4 per minute; median shot 17 to 18 s; only at a change of topic. Inside a shot everything morphs |
| Stillness | 46% and 61% of the time nothing moves: a change lands on each new idea, then a hold while it is explained |
| Background | pure black on 71 to 74% of all pixels; no grain, glow, vignette or gradient |
| Easing | a row of tokens moving fits smootherstep over exactly 1.00 s (rms error 0.002) |
| Text | a six-letter word writes on in about 0.67 s; an eleven-row list lands within about 0.4 s |
| Type | Computer Modern everywhere; a title is about 82 px at 1080p, body text about 46 px, list words about 37 px |
| Colour | on strokes and words, not on big fills: blue for the input, yellow for "look here", teal to yellow for value, red for attention, grey for the machine |

### What this repo takes from it, and what it leaves

**Takes:** the black stage; Computer Modern for everything; colour as meaning with one role per
colour; thin strokes; smootherstep over one second as the default for every move; a small fixed set
of moves; fast staggered lists; highlight boxes and colour-coded math; one picture that keeps
transforming; hard cuts only where the topic changes.

**Leaves:** his characters, logo and shots (build original pictures in the same language); 30 fps
(this repo's default is 60, set per video); the encoder saturation boost (a token colour here is
the colour in the file); and the long holds. The house rule is that the picture keeps making small
meaningful changes while the voice explains, with no still stretch over 2.5 s (see `FEEDBACK.md`).

## 2. Manim Community Edition

Version used: **0.22.1** (27 October 2026), pinned in `pyproject.toml`.

### What changed recently and matters here

| Version | Change | Used for |
|---|---|---|
| 0.21 (Aug 2026) | `Typst` and `MathTypst`: text and math without a TeX install, with named parts (`{{ ... : name }}`) | All type in `xkit/text.py` |
| 0.21 | Cairo renderer 2.2x faster on animation-heavy scenes; parallel encoding of partial movie files | 4K60 renders in about 3x real time |
| 0.22 (Oct 2026) | One `--format` option; `--video-codec`, `--pixel-format`, `--encoder-option` | Lossless RGB segment clips (`libx264rgb`, `crf=0`) |
| 0.22 | A `Manager` coordinates the render; `Scene.play`, `wait`, `next_section` delegate to it | Nothing to change; the kit only uses public `Scene` methods |
| 0.22 | ManimPango 0.7 fixes kerning of small text | Not relied on: all text goes through Typst |

Sources: the [0.21.0](https://docs.manim.community/en/stable/changelog/0.21.0-changelog.html),
[0.22.0](https://docs.manim.community/en/stable/changelog/0.22.0-changelog.html) and
[0.22.1](https://docs.manim.community/en/stable/changelog/0.22.1-changelog.html) changelogs, and the
installed source.

### Things found in the source that the kit is built around

| Finding | Consequence |
|---|---|
| Manim CE's `smooth` is a sigmoid, not ManimGL's curve; `smootherstep` exists under its own name | The kit installs a clamped smootherstep as the default easing (`xkit/motion.py`) |
| Manim CE's `YELLOW` is `#F7D96F`, not `#FFFF00` | `from xkit import *` replaces Manim's colour names with the palette |
| The clock advances by whole frames: an animated play renders `len(arange(0, run_time, 1/fps))` frames, a frozen wait writes `int(duration * fps)` copies of one frame | `Segment` counts time in frames and pads every hold to an exact frame count, so a cue lands on the same frame in both engines |
| `Camera.background_image` is cropped to the pixel size, never scaled, and stays put when the camera frame moves | The backdrop is one PNG per output size, painted by both engines |
| `alpha = t / run_time` is passed to an animation unclamped; `play(run_time=...)` overrides every animation's own run time | The easing clamps to 0..1; `later()` and `span()` time moves inside one play |
| The SVG cache hands out copies of earlier text objects that have lost their recorded baselines (the same word in another colour is a cache hit) | Kit text is parsed fresh (`use_svg_cache=False`); 40 text objects take 0.12 s |
| A Typst glyph's recorded frame starts at the top of its line box, not on the baseline | `T()` fixes the top edge at 0.8 em, so `baseline()` is exact for every font, after any move or scale |
| Typst sets `raw` text at 0.8 em | `mono()` sets it at an absolute 10 pt, the size Manim compiles at, so code is the same em as text |
| Typst font size 48 gives an em of 0.5 units: 1.40625 px at 1080p per font-size unit. Stroke width 1 draws 1.35 px | The token file holds px at 1080p; each kit converts |

## 3. Remotion

Version used: **4.0.543**, every `@remotion/*` package pinned to it in `package.json`.

| Finding | Source | Consequence |
|---|---|---|
| Every frame must be a function of `useCurrentFrame()`. CSS transitions and animations do not render | [remotion-dev/skills](https://github.com/remotion-dev/skills) | Components take time from `useTimeline()`; nothing animates by itself |
| Drive motion with `interpolate()` or your own easing over an explicit range, always clamped | same | `kit/remotion/time.ts`: `ramp`, `track`, `smooth` |
| Keep `useCurrentFrame()` in the smallest component that needs it | same | `Enter`, `Write` and `Code` read the clock themselves |
| Local fonts load through `@remotion/fonts`, which holds the render until they are ready | same | `kit/remotion/fonts.ts` loads the same OTF files Manim gives to Typst |
| `calculateMetadata` can set a composition's length and frame rate from its props | same | One composition per segment; drafts render at 30 fps through `--props` |
| `remotion render --frames=0,30,90` writes chosen frames as images in one call | same | `./x still`: layout checks without a render |
| Remotion is free for individuals and for companies of up to three people; larger companies need a licence | [remotion.dev/docs/license](https://www.remotion.dev/docs/license) | Check this applies to you before publishing work made with it |

## 4. What each engine is for

| | Manim | Remotion |
|---|---|---|
| Is, at heart | A geometry engine: every object is a set of curves that can be interpolated into any other | A browser: a layout engine with type, flexbox, SVG, canvas and images |
| Best at | One shape becoming another; math with selectable parts; axes and plots; cameras, also in 3D; anything defined by coordinates | Text that flows; interfaces and products; code with syntax colour; tables; counters and readouts; images, footage, 3D with materials |
| Weak at | Layout (nothing flows or wraps on its own), interfaces, pictures and video | Morphing arbitrary shapes, typeset math, geometric construction |

That split is the routing rule in `docs/ENGINE_ROUTING.md`.

## 5. Decisions that follow from all this

1. **One token file** (`theme/tokens.json`), read by both kits, with sizes in px at 1080p.
2. **One clock**: `beats.json` per section, with a start for every beat and a time for every word.
   Scene code names beats and words and never states a second, so retiming to a voiceover changes
   that file only.
3. **Segments, not layers.** Each run of beats is rendered natively by its engine into a clip of
   exactly the frames it owns, and the clips are joined and encoded once. No engine composites
   the other's frames, which is why a 23 s section renders at 4K60 in about a minute.
4. **One backdrop file** for both engines, and **lossless RGB** out of Manim, so the only colour
   conversion happens once, at assembly.
5. **Measured, not assumed**: `./x parity` renders the same card in both engines through the real
   pipeline. Current result: colours within 1 level, type within 1 px with identical baselines,
   strokes within 0.07 px.
6. **Rules as code**: the overlap audit, the stillness check, the layout check, the contrast check
   and render verification run on every render rather than living in a checklist.
