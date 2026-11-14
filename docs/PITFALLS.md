# Pitfalls

Engine quirks that cost time once and must not cost it again. Each was met while building this
repo; most are now handled by the kit, and the note says how. Add to this list when a new one
bites.

## Manim

| # | What happens | What to do |
|---|---|---|
| M1 | **Manim CE's `smooth` is not ManimGL's.** It is a sigmoid; 3Blue1Brown's motion is smootherstep. | The kit installs a clamped smootherstep as every animation's default. Use `smooth` from `xkit`, not `rate_functions.smooth`. |
| M2 | **Manim CE's `YELLOW` is `#F7D96F`**, and its other names are not the palette either. | `from xkit import *` replaces the colour names. Never `from manim import YELLOW` in a scene. |
| M3 | **A play's run time overrides every animation in it**, and an animation is handed `t / run_time` unclamped: in a play that mixes run times, the short ones run past their end. | Give each animation its own `run_time` and leave the play's unset. The house easing clamps. To start something later inside a play use `later(delay, anim)`. |
| M4 | **A wait is not always the frames you asked for.** A frozen wait writes `int(duration * fps)` copies of one frame, an animated one renders `len(arange(0, duration, 1/fps))`: float error drops or adds a frame. | `Segment.wait`, `beat`, `on` and `finish` hold for an exact number of frames and raise if Manim wrote a different number. Do not call `Scene.wait` through `super()`. |
| M5 | **An object rebuilt every frame leaves a frozen copy behind**: a play remembers each object's parts when it starts. | Build it with `self.live(update)`, which empties the holder before every play. |
| M6 | **A live number cannot fade in**: its shape changes every frame. | `rise(still_number(...))`, then swap it for the `counter(...)` in the same place. |
| M7 | **Turning a dial's needle while its panel moves**: the rotation and the move fight over the same points and leave pieces behind. | Move first, then `turn_dials`. Never both in one play. |
| M8 | **`Transform(..., path_arc=...)` tilts a rigid object** as it travels. | `glide(mob, end, via)` moves its centre along a curve without rotating it. |
| M9 | **`set_opacity` on an outline also fills it.** | Push things back with `dim()` (built on `fade`) and bring them back with `undim()`. |
| M10 | **`next_to(arc)` uses the arc's bounding box**, which is far from its stroke. | Anchor to `arc.point_from_proportion(0.5)`. |
| M11 | **`move_to` centres the bounding box**, so words with and without descenders land on different lines, and a star's box is off its own centre. | `baseline_row`, `align_baseline`; `star()` is centred on the origin, place it with `shift`. |
| M12 | **The SVG cache loses text baselines.** A second `Typst` object with the same source (the same word in another colour) is a copy without its baseline record. | Kit text sets `use_svg_cache=False`. Create text with `T`, `sans`, `mono`, not `Typst(...)` directly. |
| M13 | **Typst sets `raw` text at 0.8 em**, and a relative size inside the show rule is relative to that. | `mono()` uses an absolute size. Code is the same em as the text beside it. |
| M14 | **Typst forms ligatures** (fi, fl), so a word can have fewer glyphs than letters. | Never slice text by character index. Name parts instead (`eq` with `{{ ... : name }}`). |
| M15 | **A camera background image is cropped, not scaled.** | Backdrops are drawn per output size (`xcore/backdrop.py`); `Segment` picks the right one. |
| M16 | **Caching makes the clock inexact**: a cached play advances time by its nominal length. | The kit sets `config.disable_caching = True`. Leave it. |
| M17 | **The overlap audit skips lines and arrows** (they are meant to touch things) and anything under 60% opacity. A line drawn across an object, or a card fading out while another slides through its place, passes the audit and still looks wrong. | Route connectors round objects; let a leaving object finish before another crosses its place. Check transitions on a detail sheet. |
| M18 | **Things that move into a filled shape get covered** by a fill drawn later. | Give them `set_z_index(1)` when they are created. |
| M19 | **Thousands of submobjects or heavy `always_redraw` make 4K crawl.** | Precompute geometry; keep live objects small. |

## Remotion

| # | What happens | What to do |
|---|---|---|
| R1 | **CSS transitions, CSS animations and Tailwind animation classes do not render.** Frames are captured one at a time. | Every value is a function of `t` from `useTimeline()`. |
| R2 | **`Math.random()`, `Date.now()`, timers and component state** make frames differ between renders. | None of them. Use `random(seed)` from `remotion` if noise is needed. |
| R3 | **A component that reads the clock re-renders every frame**, and so does everything under it. | Read `useTimeline()` in the smallest component that animates (`Enter`, `Write`, `Code` do). |
| R4 | **A digit count that changes resizes its box** and shifts what is beside it. | `<Num>` uses tabular figures; give a readout a fixed place, do not flow things after it. |
| R5 | **The wrong backdrop size is resampled**, and then it no longer matches Manim's. | Renders pass `outputWidth`; do not draw a backdrop yourself. |
| R6 | **`@remotion/*` packages of different versions break the bundle.** | All are pinned to one version. Upgrade them together: `npm run upgrade`. |
| R7 | **The TypeScript check is not part of a render.** A type error only shows when you ask. | `./x typecheck` before a final. |
| R8 | **npm 12 blocks install scripts** and warns about esbuild's. | Nothing to do: the platform binary arrives as an optional dependency and bundling works. |

## The pipeline

| # | What happens | What to do |
|---|---|---|
| P1 | **Python's `round()` and JavaScript's `Math.round()` disagree on half frames** (to even, and up). One frame of drift at an engine switch. | Both kits use one rule, `frame_of` / `frameOf`: half frames round up. |
| P2 | **RGB to YUV conversion defaults to BT.601 in swscale**, while players assume BT.709 for HD and 4K: colours shift slightly, and differently per engine. | Manim writes lossless RGB; the one conversion happens at assembly with BT.709 stated; the file is tagged. `./x parity` proves it. |
| P3 | **A draft can pass the stillness check on compression shimmer.** | The check ignores changes smaller than about a 35 px square at 1080p. A three-dot "typing" indicator does not count as motion, and should not. |
| P4 | **faster-whisper's own audio decoder and the PyAV that Manim pins disagree.** | `tools/align.py` decodes with ffmpeg and hands the recogniser samples. |
| P5 | **zsh stops on an unmatched glob** (`rm -rf *.egg-info`). | Quote globs or use `find` in shell snippets. |
| P6 | **A 4K render watched in the foreground** makes everyone wait. | Run `./x final` in the background; send the preview or the draft meanwhile. |
