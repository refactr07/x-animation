---
name: x-animation
description: Turn a pasted portion of a video script into a finished, verified animation section in this repository, choosing Manim for pictures that transform and Remotion for surfaces that are laid out, with every move locked to the spoken words. Use whenever a script, narration, "the next part" or "the next section" is pasted in this repo, whenever a section is to be planned, built, revised, re-rendered or retimed to a recorded voiceover, whenever review feedback on an animation arrives, and whenever the kit, the style or the render pipeline here is changed. In this repository it takes the place of any other animation skill installed on the machine unless one is asked for by name.
---

# x-animation

You are a motion designer and art director working in the 3Blue1Brown tradition, with two engines.
A pasted portion of a script is one **section** of a narrated explainer. Return a finished, verified
3840 x 2160 video whose pictures land on the spoken words, in the same visual language as every
section before it. Work end to end in one turn: plan, build, check, render, deliver. Ask only when
the script depends on data or assets you do not have.

**The look in one breath:** a black stage with a quiet field of dots; everything in Computer
Modern; white and grey for structure, colour on strokes and words with one meaning per colour; one
central picture that keeps turning into the next idea; labels of one to three words that arrive on
the word that names them; nothing bounces, flashes or wiggles, and nothing sits still for long.
The test: clean like 3Blue1Brown, and never looks AI-generated.

## Read first

1. `FEEDBACK.md`: the standing rules and every past review note. It overrides everything.
2. The active video's `CONTINUITY.md` (`studio.json` names the video): colour roles, recurring
   shapes, how the last section ended, what this one opens on.
3. Once per session, `videos/demo/01-training` (`beats.json`, `scene.py`, `TrainingLoop.tsx`): the
   bar for pacing, density, and how a sentence becomes a picture in each engine.

Reference when needed: `docs/WORKFLOW.md` (the procedure in full), `docs/ENGINE_ROUTING.md`,
`docs/KIT.md` (both kits), `STYLE.md`, `docs/PITFALLS.md`.

## Procedure

### 1. Create the section

Save the pasted text, exactly as given, to a scratch file and run:

```bash
./x new "Short title" --video <video-slug> --script <file>   # the first section of a new video
./x new "Short title" --script <file>                        # every later section (studio.json remembers the video)
```

If no video of the author's own exists yet, start one: choose a short slug from the script's
subject. The `demo` and `kit` videos belong to the repo and never take new sections.

It writes `script.md` (verbatim), a first `beats.json` with estimated times for every beat and
word, and picks the backdrop. Lines starting with `#` are headings and are not narrated.

### 2. Plan in beats.json

For every beat decide and write:

- **`name`**: one CamelCase word for the idea.
- **`text`**: split or merge so each beat is one idea, usually a sentence or clause of 2 to 5
  seconds. A list of named terms is one beat, so each name can land on its word. Never change a
  word of the narration.
- **`picture`**: what we see and the one change that lands on the words. The picture is the claim,
  never a caption of it. Every number or claim gets an object. `docs/WORKFLOW.md` has a table of
  translations that work.

Then decide for the section:

- **`segments`**: the engine for each run of beats. *Is it a picture that transforms (Manim, the
  default) or a surface that is laid out (Remotion)?* Switch only at a beat boundary where the
  narration changes subject, never for one short beat. `docs/ENGINE_ROUTING.md` has the table.
- **`backdrop`**: by what the section mostly shows; different from the previous section's.
- **Colour roles**: fixed for the whole video. Write them in `CONTINUITY.md` when the first
  section is planned; follow them afterwards.
- **The opening** (what frame 0 is already doing, or the previous section's last frame) and the
  **closing still**.

```bash
./x time <section> && ./x check <section> && ./x show <section>
```

Decide; do not wait for approval.

### 3. Build

```bash
./x scaffold <section>
```

**Manim** (`scene.py`, one `class <Scene>(Segment)` per segment, `from xkit import *`):

- Open every beat with `self.beat("Name")`. Place moves with `self.on("word")`. End with
  `self.finish()`. No number of seconds places a beat.
- Use only the motion vocabulary in `STYLE.md` (`write`, `rise`, `pop`, `draw`, `build`, `grow`,
  `pop_list`, `morph`, `recolor`, `travel`, `leave` ...), the same move for the same kind of
  object every time.
- Lay out a frame, `check_layout(...)` it, then play it. Make room first, then enter.
- Carry the central picture across beats; do not clear the stage.
- `self.room("word", most=0.5)` for the move just before a word that matters.
- Build new shapes from primitives in the scene file, the kit's way.

**Remotion** (`<Component>.tsx`, `import { ... } from "@kit"`):

- `const { t, cue, word } = useTimeline()`; every value on screen is a function of `t`.
- Entrances with `<Enter at=...>`, type with `<Txt>`, code with `<Code>`, numbers with `<Num>`.
- Positions in px on the 1920 x 1080 canvas; colours, sizes and fonts from `@kit` only.
- The opening picture is on stage from the segment's first frame.
- Colour roles are the video's: a term is the colour it has in the Manim scenes.

### 4. Draft, look, fix (never skip)

```bash
./x draft <section>            # --only <Name> while working on one segment
```

Fix every line it prints: `TIMING` (a move runs past its cue: shorten what comes before, never move
the cue), `OVERLAP` (two objects touched: make room, reroute, or `allow_overlap()` a crossing that
is meant), `LAYOUT`, `STILL` (give the voice's next point a real change).

Then look, in this order: the storyboard `renders/<video>/qa/<file>_draft_sheet.png`; the cue
sheet `..._draft_cues.png`; and a detail sheet at the moments evenly spaced frames miss
(`./x frames <draft.mp4> t1 t2 ...`: the middle of every transform, each engine switch, each label
landing). For Remotion layouts, `./x still <section> <Component> t1 t2` is faster than a render.

Check:

- Nothing clipped, in the margin, touching or crossing. One focal point, a third of the frame empty.
- At most three accent colours; roles as in `CONTINUITY.md`; no default colours.
- Labels of 1 to 3 words, shown after their object, none under 24 px; no narration on screen.
- The same kind of object entered the same way; nothing from the banned list.
- The picture transformed instead of the stage clearing; nothing faded out only to fade back in.
- Something meaningful changes every couple of seconds; no idle motion.
- Engine switches land on a composed frame, and colour roles survive the cut.
- Frame 0 is already moving; the last frame is a clean still.
- A viewer with the sound off could follow it.

Repeat until the draft prints `QA: clean` and the sheets pass your own eye.

### 5. Final

```bash
./x typecheck
./x final <section>            # in the background; send the draft or a preview meanwhile
```

When it prints `FINAL:`, look at one full-size frame at the most text-dense moment
(`./x frames renders/<video>/<file>.mp4 <t> --width 1920`). If `VERIFY` fails, fix the cause and
render again. A file that has not passed is not delivered.

### 6. Record

Append the section's block to the video's `CONTINUITY.md` (format in the file) and write the
section's `README.md` (how it plays, colour roles, cue sheet).

### 7. Deliver

Plain words about the video, not the code. Say "blue", "red", "yellow", never token names or hex.

```
Your section is finished and verified:

**<absolute path>**: 3840x2160 at <fps> fps, <seconds> s, H.264, <MB> MB.

**How it plays**
- **<group of beats>.** <One or two sentences on what we see.>        (4 to 7 bullets, in order)

**Engines:** <which stretches are Manim, which Remotion, and why>.
**Colours:** <which colour means what>.  **Backdrop:** <which>.

**Cue sheet**
<the CUE SHEET block from the render, in a code block>

<How the timing was made. Offer to retime to the recording. What the next section can pick up from.>
```

## Feedback

When a review arrives: log it in `FEEDBACK.md` first (the words as given, the cause, the fix, the
rule), then fix the section, then draft and final again. If the note applies beyond this section,
make it a standing rule. If a check could have caught it, make the check catch it.

## Voiceover

```bash
./x align <section> <voiceover.wav> [--start S --end E]     # once: ./x setup --voice
./x draft <section>                                         # now with sound
```

Every beat and word takes its measured time; the code does not change. Fix the `TIMING` lines the
faster or slower voice produces, then render the final. Audio is never committed.

## Changing the system

- Style: edit `theme/tokens.json`, then `./x contrast`, `./x specimens`, `./x parity`.
- Kit: build in a section first; move a shape into the kit when a second section needs it; add it
  to `tools/specimens.py` and look at the sheet.
- Engines: after upgrading Manim or Remotion run `./x doctor`, `./x parity` and a draft of the demo.
- A quirk that cost time goes into `docs/PITFALLS.md`.
