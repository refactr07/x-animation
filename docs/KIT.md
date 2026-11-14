# The kits

Two kits, one style. `xkit` is the Manim half, `@kit` the Remotion half; both read
`theme/tokens.json`, and `./x parity` measures that they draw the same thing. Specimens:
`./x specimens` (`docs/assets/kit_*.png`).

## Timing, in both

| | Manim (`Segment` methods) | Remotion (`useTimeline()`) |
|---|---|---|
| Start a beat on its cue | `self.beat("Name")` | `cue("Name")` is its time |
| The moment a word is spoken | `self.on("word")` holds until then | `word("Beat", "word")` is its time |
| A phrase, or the second occurrence | `self.on("real users")`, `self.on("the", nth=2)` | `word("Beat", "real users")`, `word("Beat", "the", 2)` |
| So many seconds into a beat | `self.at(1.2)` | `cue("Name") + 1.2` |
| Time left before a word or the next beat | `self.room("word", most=0.5)`, `self.left()` | `word(...) - t` |
| Now | `self.now` (section seconds) | `t` (section seconds) |
| End the segment | `self.finish()` (`clear=True` fades to the stage) | the composition's length is set for you |

`on()` ends 0.12 s before the word (`lead`), so the move that follows lands on it. Pass `lead=0`
for an instant change, or a longer lead for a slow move that should finish on the word.

## Manim: `from xkit import *`

That one import is the whole Manim namespace with the house style over it.

### Theme (`xkit/theme.py`)

| | |
|---|---|
| Colours | `WHITE BLACK GREY_A GREY_B GREY_C GREY_D GREY_E BLUE BLUE_LIGHT BLUE_DEEP TEAL TEAL_DEEP GREEN YELLOW GOLD ORANGE RED PINK PURPLE`, `RAMP`, `role("focus")` |
| Type sizes | `HERO TITLE HEADING LABEL BODY SMALL TINY` |
| Strokes | `W_HAIR W_THIN W_SHAPE W_HERO W_ARROW W_BACK` |
| Lengths (units) | `MARGIN_X MARGIN_Y GAP SPACE CLEARANCE RADIUS FRAME_W FRAME_H`, `px(pixels)` |
| Durations | `MOVE FAST TRANSFORM CAMERA LAG LEAD` |
| Fills | `tint(color, amount=0.18)`: a solid tint over the stage. `ramp_color(p)` for a value |

### Text (`xkit/text.py`)

| | |
|---|---|
| `T(text, size=BODY, color=WHITE, weight="regular", italic=False)` | One line. Typewriter quotes become typographic ones |
| `sans(text, ...)`, `mono(text, ...)` | Interface text; code (leading spaces kept, `\n` makes a block) |
| `paragraph(text, width, ...)` | Wrapped text that is content |
| `eq(expr, colors={"w": BLUE})` | Typst math; name parts with `{{ ... : w }}`, fetch them with `.select("w")` |
| `num(value, "{:,.0f}")` | A formatted number with a true minus sign |
| `baseline(m)`, `align_baseline(m, to)`, `baseline_row(a, b, c)` | Words on one line |
| `backstroke(m)` | A stage-coloured outline behind text that sits on lines or fills |

### Motion (`xkit/motion.py`)

`write rise pop fade_in draw build grow pop_list stagger` · `morph from_copy recolor glow dim undim`
· `leave sink undraw` · `later(delay, anim)` `span(anim, start, end)` · `glide(m, end, via)`
`travel(path)` `flip(old, new)` · `smooth ease_out ease_in`

`leave()` returns a list: `self.play(*leave(a, b), rise(c))`.

### Shapes (`xkit/shapes.py`)

`box disc ring dot panel rule` · `token chip badge` · `arrow thin_arrow arc_arrow link` ·
`highlight_box underline strike cross_out check cross brace_label` · `axes axis_label` ·
`bar_list bracket_vector progress_bar set_progress`

- `bar_list(rows)` returns `.rows`, `.words`, `.bars`, `.numbers`. `relative=False` colours a bar
  by its value itself, so a list of equally unsure guesses stays pale.
- `token()` and `chip()` are as tall as a full line of text, so rows of them line up.

### Pictograms (`xkit/pictograms.py`)

`person team crowd robot` · `page pages code_bars folder clipboard` · `app_window browser terminal
phone laptop chat_bubble` · `server database cloud chip_cpu gear` · `dial turn_dial turn_dials
dial_panel neural_net` · `clock magnifier padlock key bolt star lightbulb envelope globe warning
coin eye line_chart`

- `dial_panel()` is a model; `.dials` are its numbers; `turn_dials(model.dials, values)` animates
  them (never in the same `play` as moving the panel).
- `neural_net()` has `.layers` and `.edges`.

### Numbers that run (`xkit/counter.py`)

```python
steps = ValueTracker(0)
readout = counter(self, steps, "{:,.0f}", HEADING, anchor=RIGHT, at=[4, 1, 0])
self.add(readout)
self.play(steps.animate(rate_func=linear).set_value(5000), run_time=3)
readout.clear_updaters()
```

A live number cannot fade in (its shape changes every frame): bring in `still_number(...)` with
`rise()`, then `self.remove(still); self.add(readout)` in the same place.

### Layout (`xkit/layout.py`)

| | |
|---|---|
| `check_layout(a, b, c)` | Raises if anything leaves the safe area or two things overlap. Call it on a composed frame before playing it |
| `parts_of(group)` | These pieces are one object: the audit never compares them with each other |
| `allow_overlap(m)`, `watch_again(m)` | A crossing that is meant (a signal entering a box) |
| `frames(box, target)` | `box` is a frame around `target` |
| `named(m, "name")` | A name for audit messages |

### Scenes (`xkit/scene.py`)

- `Segment`: 2D, with `self.zoom_to(m)` and `self.zoom_out()` for a dive into a detail.
- `Segment3D`: for spatial ideas. The overlap audit is off; check 3D shots on the sheets.
- `self.live(update)`: an object rebuilt every frame. `self.regroup(group)`: after a build that
  brought a group's parts in one by one, make the scene hold the group as one object.
- `X_OVERLAP=error` stops a render at the first overlap; `X_OVERLAP=off` disables the audit
  (debugging only).

## Remotion: `import { ... } from "@kit"`

### Theme (`kit/remotion/theme.ts`)

`P` (palette: `P.blue`, `P.blueLight`, `P.yellow`, `P.greyB` ...), `TYPE` (px), `STROKE` (px),
`RADIUS`, `FONT`, `MOTION`, `LAYOUT`, `tint(color, amount, stage)`, `mix`, `alpha`, `rampColor`,
`px(x, y)` (Manim coordinates to canvas pixels).

### Time (`kit/remotion/time.ts`)

| | |
|---|---|
| `ramp(t, start, dur, ease=smooth)` | Eased 0..1 progress of a move |
| `hold(t, start, end)` | 1 between two times, eased in and out |
| `track(t, [[t0, v0], [t1, v1], ...])` | A value that follows keyframes |
| `smooth`, `easeOut`, `easeIn`, `linear`, `lerp`, `clamp01` | |

### Components

| | |
|---|---|
| `<Enter at out kind="rise\|pop\|fade\|slide">` | Arrives at `at`, leaves at `out`. Position it with `style` |
| `<Write text at />` | A word arriving glyph by glyph |
| `typed(text, t, at, dur)` | Text that types itself |
| `cascade(start, count, lag)` | Start times for a list |
| `<Code code lang roles lineAt active span band numberColor />` | An editor's contents: lines type in on cues, a band steps through them. `roles` gives identifiers the video's colours |
| `<Panel x y w h color fill>` | A rounded frame with a solid tint |
| `<Txt size color family weight>`, `<Num value decimals />` | One line of text; a formatted number |
| `<ProgressBar value w />`, `<Chip>`, `<Token>` | |
| `<Arrow from to progress />`, `<HighlightBox x y w h progress />` | SVG, drawn on by `progress` |
| `<Window>`, `<Bubble side>` | A product window; a chat message |
| `useStage()` | The stage colour, for tints |

A segment component is exported under the name `segments` gives it, from a file of the same name
in the section folder. `./x sync` (run by every render) registers it as the composition
`<video>-<section>-<Component>`; `./x studio` opens Remotion Studio to scrub it.

## Adding to a kit

1. Build it in the section first.
2. When a second section needs it, move it into the kit, with a one-line docstring saying what it
   stands for.
3. Add it to `tools/specimens.py`, run `./x specimens` and look at it.
4. If it exists in both engines, add it to the parity card and run `./x parity`.
