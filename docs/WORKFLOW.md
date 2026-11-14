# From a pasted script to a verified video

One pasted portion of a script is one **section**: a folder under `videos/<video>/` with its
narration, its timing, its code and nothing else. This is the whole path, in order. Every command
is `./x <something>`; `./x help` lists them.

```
script ──▶ beats.json ──▶ pictures + engines ──▶ scene.py / Component.tsx ──▶ draft ──▶ final
           (the clock)     (the plan)             (the build)                 (QA)      (the master)
```

## 0. Before planning

- Read [`FEEDBACK.md`](../FEEDBACK.md): the standing rules, and every past review note.
- Read the video's `CONTINUITY.md`: colour roles, recurring shapes, how the last section ended and
  what this one should open on.
- Read `videos/demo/01-training` (`beats.json`, `scene.py`, `TrainingLoop.tsx`) once per session.
  It is the bar for pacing, density and how a sentence becomes a picture.

## 1. Create the section

```bash
./x new "Hook" --video my-video --script pasted.txt     # the first section of a new video
./x new "The problem" --script pasted.txt               # every later section of that video
```

This saves the script verbatim as `script.md`, splits it into beats (one per sentence; long
sentences at a clause; runs of very short sentences together, so each name in a list can land on
its word), estimates every beat and word time at the video's pace, picks the next backdrop, and
prints the beats with a first guess at the engine. `--video <slug>` starts a video (or switches to
one) and makes it the active video in `studio.json`; without it the section joins the active video.
The `demo` and `kit` videos belong to the repo and never take new sections. The script can also be
piped in instead of `--script`.

Narration is verbatim. Lines starting with `#` in the script are headings and are not narrated.

## 2. Plan it in beats.json

Open the section's `beats.json` and decide, for every beat:

- **Its name**: one CamelCase word for the idea (`Noise`, `Guess`, `Downhill`).
- **Its boundaries**: split or merge by editing the `text` fields. One idea per beat, usually a
  sentence or a clause; a beat is typically 2 to 5 seconds.
- **Its picture** (`"picture"`): what we see, and the one change that lands on the words. The
  picture is the claim, never a caption of it. Translations that work:

  | The narration says | The picture |
  |---|---|
  | A big number | The thing as a pictogram beside a counter that runs to the number |
  | A span of time | A timeline with one segment per unit |
  | None, zero, "not one" | A large 0 where the number would be, then the thing it denies |
  | A contrast ("meanwhile, most of us...") | Their picture shrinks to a corner; ours builds in the space it left |
  | A question | Everything leaves but the subject, which centres; a `?` rises |
  | "It was not X" | X draws around the subject, then is struck out |
  | "It was Y" | The struck X becomes Y, and Y takes the focus colour |
  | Several names that sound alike | Identical tags first, then each name on its spoken word |
  | A metaphor | The subject morphs into the metaphor's pictogram and keeps its colour |
  | A list of examples | One framed glyph per example, left to right on the words |
  | A process | A signal travels the diagram, lighting each stage on its word |
  | "In code" / "in the app" / "on the dashboard" | Cut to that surface, built in Remotion |
  | An aside with no picture of its own | The picture tidies itself into the layout the next beat needs |

- **The engine for each run of beats** (`"segments"`), by [`ENGINE_ROUTING.md`](ENGINE_ROUTING.md).
- **The backdrop**, by what the section mostly shows ([`STYLE.md`](../STYLE.md), Backdrops).
- **Colour roles**, fixed for the whole video and written in `CONTINUITY.md`.

Then:

```bash
./x time  <section>      # recompute beat and word times from the edited text
./x check <section>      # contiguous beats and segments, verbatim narration, backdrop rule
./x show  <section>      # the plan on one screen
```

Decide and build. Do not stop to ask for approval of a plan.

## 3. Build

```bash
./x scaffold <section>   # a starting scene class or component for every segment
```

**Manim segments** are classes in `scene.py`, named as in `segments`:

```python
from xkit import *

class Learn(Segment):
    def construct(self):
        self.beat("Noise")                       # starts on its cue
        model = dial_panel(2, 3).scale(2)
        self.play(build(model.frame), stagger([pop(d) for d in model.dials], 0.12))
        self.on("noise")                         # holds until the word is spoken
        self.play(turn_dials(model.dials, RANDOM))
        self.beat("Guess")                       # the rest of Noise becomes a hold
        ...
        self.finish()                            # ends on the segment's last frame
```

- `beat()`, `on()` and `at()` place everything. No number of seconds places a beat.
- `room("word", most=0.5)` gives a move the time left before a word, so it tightens by itself
  when a voiceover is brisker than the estimate.
- Lay a frame out, call `check_layout(...)` on it, then play it.
- Carry the central picture from beat to beat with `morph`, `.animate` and `recolor`.
- New shapes are built in the scene file from primitives, the kit's way. A shape a second section
  needs moves into `kit/python/xkit/pictograms.py`.

**Remotion segments** are components in `<Component>.tsx`:

```tsx
export const TrainingLoop: React.FC = () => {
  const { t, cue, word } = useTimeline();
  const typed = ramp(t, word("Code", "code"), 0.4);      // starts when "code" is spoken
  ...
};
```

- `t` is seconds since the start of the section; `cue()` and `word()` read `beats.json`.
- Every value on screen is a function of `t`. No CSS animation, no timers, no state, no randomness.
- Positions are px on the 1920 x 1080 canvas. Colours, sizes and fonts come from `@kit`.
- The opening picture is on stage from the segment's first frame.

Reference for both kits: [`KIT.md`](KIT.md). Quirks that cost time once: [`PITFALLS.md`](PITFALLS.md).

## 4. Draft, look, fix

```bash
./x draft <section>                 # 960x540 at 30 fps, a few seconds
./x draft <section> --only Learn    # one segment while you work on it
./x still <section> TrainingLoop 12.9 14.3   # Remotion frames without rendering
```

The draft prints, for every segment, anything that is wrong:

| Line | Means | Do |
|---|---|---|
| `TIMING beat X is 0.3s late` | The moves before that cue take longer than the narration | Shorten them or start them earlier. Never move the cue |
| `OVERLAP at 7.6s: A / B` | Two objects touched or crossed, even briefly | Make room first, reroute the move, or `allow_overlap()` a crossing that is meant |
| `LAYOUT: item 2 leaves the safe area` | A composed frame is too wide or tall | Scale or rearrange |
| `STILL 31.2-34.4 s` | Nothing changed for over 2.5 s | Give the voice's next point a real change: a signal, a value, a highlight, a reframe |
| `VERIFY FAIL` | The file is not what was asked for | Fix the cause; the file is not to be delivered |

Then **look**, in this order:

1. `renders/<video>/qa/<file>_draft_sheet.png`: the storyboard. Read it as a viewer with the sound
   off. Does each beat have one clear picture? Does the picture carry from beat to beat?
2. `renders/<video>/qa/<file>_draft_cues.png`: the frame at each cue and 0.4 s later.
3. `./x frames <draft.mp4> t1 t2 ...`: the middle of every transform, each engine switch, and the
   frame each label lands on. Evenly spaced frames land on holds and miss these.

Check against this list:

- Nothing clipped, nothing inside the margin, no label touching another or crossing a line.
- One focal point; at most three accent colours; colour roles as in `CONTINUITY.md`.
- About five words of labelling at most, all at least 24 px at 1080p. No default colours.
- The same kind of object entered the same way every time. Nothing from the banned list.
- The central picture transformed instead of the stage clearing.
- Every number or claim in the narration has an object. A muted viewer could follow it.
- Engine switches land on a composed frame; colour roles survive the cut.
- Frame 0 is already moving; the last frame is a clean still.

Fix and draft again until the draft says `QA: clean` and the sheets pass your own eye: usually one
to three rounds.

## 5. Final

```bash
./x final <section>        # 3840x2160 at the video's frame rate; run it in the background
```

It renders every segment at full size, joins them, verifies resolution, frame rate, exact frame
count, codec and colour tags, runs the stillness check and writes the QA sheets. A 23 second
section takes about a minute on an M4. When it prints `FINAL:`, look at one full-size frame at the
most text-dense moment (`./x frames renders/<video>/<file>.mp4 <t> --width 1920`): type crispness
and stroke weight only show at full size. `./x preview` gives a 1080p file in the meantime.

A file that has not passed verification is not delivered.

## 6. Record what happened

- Append the section's block to the video's `CONTINUITY.md`: engines and why, backdrop, what it
  introduced, the exact final frame, what the next section should open on, and any promise the
  narration made to the viewer.
- Write the section's `README.md`: how it plays, colour roles, the cue sheet.

## 7. Deliver

Reply in plain words, about the video rather than the code. Say "blue", "red" and "yellow", never
token names or hex codes.

```
Your section is finished and verified:

**<absolute path>**: 3840x2160 at 60 fps, <seconds> s, H.264, <MB> MB.

**How it plays**
- **<group of beats>.** <One or two sentences on what we see.>          (4 to 7 bullets, in order)

**Engines:** <which stretches are Manim, which Remotion, and why>.
**Colours:** <which colour means what>.  **Backdrop:** <which>.

**Cue sheet**
<the CUE SHEET block, in a code block>

<How the timing was made (estimate at N wpm, or a voiceover). Offer to retime to the recording.
Say what the next section can pick up from.>
```

## When the voiceover exists

```bash
./x align <section> voiceover.wav                       # this section's narration
./x align <section> full-video.wav --start 83.2 --end 121.0    # its part of a longer file
./x draft <section>                                     # now with sound
```

`align` listens to the recording, matches it to the narration word by word and writes the measured
time of every beat and word into `beats.json`. Scene code names beats and words, so nothing else
changes: the draft now plays against the real voice, and prints a `TIMING` line for any move that
is too long for it. Fix those, then `./x final`.

With only the recording's length, `./x time <section> --total <seconds>` fits the estimate to it.

Needs the speech extra once: `./x setup --voice`. Audio files are never committed.

## Feedback

When a review comes back, write it into `FEEDBACK.md` in the same turn: the words as given, what
was wrong, the fix, and the rule it produced. A rule that applies beyond one section becomes a
standing rule. A mistake that is logged there is not made twice.
