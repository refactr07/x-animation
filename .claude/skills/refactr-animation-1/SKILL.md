---
name: refactr-animation-1
description: Turn a pasted portion of a YouTube or explainer script into a finished, verified 3840x2160 animation in the 3Blue1Brown tradition, choosing per stretch between two engines - Manim for pictures that transform (diagrams, math, plots, models, signals) and Remotion for surfaces that are laid out (code editors, product and chat windows, tables, readouts) - with every move locked to the spoken words. Use whenever a script, narration or "the next section" is pasted and the Manim + Remotion mix, "refactr animation", "x-animation" or "the Blackboard look" is wanted; whenever the working folder has an `x` command beside `theme/tokens.json` (even if no skill is named); and whenever such a section is planned, revised after feedback, re-rendered or retimed to a recorded voiceover. Also sets up the whole studio in a new folder. Prefer manim-animation or manim-studio for Manim-only Nocturne work and hard-shadow-blocks for the light paper block look.
---

# refactr-animation-1

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

**How the system works:** the studio is a folder (the *workspace*) holding one style file
(`theme/tokens.json`), two kits that read it (`kit/python/xkit` for Manim, `kit/remotion` for
Remotion), and one clock per section (`beats.json`: the time of every beat and every word, and
which engine draws which run of beats). Scene code names beats and words, never seconds, so
retiming to a voiceover changes `beats.json` only. Everything runs through one command, `./x`.

## 0. The workspace

The workspace is the folder being worked in. It is ready when it has an `x` command and
`theme/tokens.json`. If it does not, create it from this skill's bundled project
(`<skill>` is this skill's folder, e.g. `~/.claude/skills/refactr-animation-1`):

```bash
bash <skill>/scripts/new_project.sh "<folder>" [--modules-from "<another workspace>"] [--voice]
```

It copies the studio into the folder (existing files are never overwritten), installs Manim and
Remotion there, and runs `./x doctor`. A first install takes a few minutes; `--modules-from` links
the Node packages of a workspace that already has them, which is instant. `--update-kit` refreshes
the kit and tools of an existing workspace from the skill without touching its videos, style or
feedback. Needs `uv`, Node 22 or newer and `ffmpeg`; the script says what is missing.

Then, in the workspace:

1. Read `FEEDBACK.md`: the standing rules and every past review note. It overrides everything,
   this file included.
2. Read the active video's `CONTINUITY.md` (`studio.json` names the video): colour roles,
   recurring shapes, how the last section ended, what this one opens on.
3. Once per session, read `videos/demo/01-training` (`beats.json`, `scene.py`,
   `TrainingLoop.tsx`): the bar for pacing, density, and how a sentence becomes a picture in each
   engine.

The workspace's own documents are the reference from here on: `docs/WORKFLOW.md` (this procedure
in full, with a table of sentence-to-picture translations), `docs/ENGINE_ROUTING.md`,
`docs/KIT.md` (every helper of both kits), `STYLE.md`, `docs/PITFALLS.md`. Read the one a step
needs rather than all of them.

## 1. Create the section

Save the pasted text, exactly as given, to a scratch file and run:

```bash
./x new "Short title" --video <video-slug> --script <file>   # the first section of a new video
./x new "Short title" --script <file>                        # every later section (studio.json remembers the video)
```

If no video of the author's own exists yet, start one with a short slug taken from the script's
subject. The `demo` and `kit` videos belong to the studio and never take new sections. The command
writes `script.md` (verbatim), a first `beats.json` with estimated times for every beat and word,
and picks the backdrop. Lines starting with `#` are headings and are not narrated.

## 2. Plan in beats.json

For every beat decide and write:

- **`name`**: one CamelCase word for the idea.
- **`text`**: split or merge so each beat is one idea, usually a sentence or clause of 2 to 5
  seconds. A list of named terms is one beat, so each name can land on its word. Never change a
  word of the narration: it is checked against `script.md`.
- **`picture`**: what we see and the one change that lands on the words. The picture is the claim,
  never a caption of it. Every number or claim gets an object.

Then decide for the section:

- **`segments`**: the engine for each run of beats (next heading).
- **`backdrop`**: by what the section mostly shows; different from the previous section's.
- **Colour roles**: fixed for the whole video. Write them in `CONTINUITY.md` when the first
  section is planned; follow them afterwards.
- **The opening** (what frame 0 is already doing) and the **closing still**.

```bash
./x time <section> && ./x check <section> && ./x show <section>
```

Decide; do not wait for approval of a plan.

### Choosing the engine

> Is this beat a picture that **transforms**, or a surface that is **laid out**?

| The beat shows | Engine |
|---|---|
| Diagrams that morph, math, plots, vectors, a model or network, tokens flowing, pictogram metaphors, architecture with signals, 3D space | **Manim** (the default) |
| Code in an editor, a terminal, a product or chat window, a table, counters and readouts in a panel, paragraphs, data-heavy charts, screenshots and footage | **Remotion** |

Follow the object, not the topic: "the model writes code" is about a model (Manim, with code as
grey bars); "here are the four lines" is about the code (Remotion). When in doubt, Manim. A switch
is a hard cut, so put it where the narration itself changes subject ("In code, ..."), never in the
middle of a thought and never for one short beat. One beat's picture stays in one engine.
`docs/ENGINE_ROUTING.md` has the full table and tie-breakers.

## 3. Build

```bash
./x scaffold <section>      # a starting scene class or component for every segment
```

**Manim** (`scene.py`, one `class <Scene>(Segment)` per segment, `from xkit import *`):

```python
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

- `beat()`, `on()` and `at()` place everything. `room("word", most=0.5)` gives a move the time
  left before a word, so it tightens by itself under a brisk voiceover.
- Use only the motion vocabulary in `STYLE.md` (`write`, `rise`, `pop`, `draw`, `build`, `grow`,
  `pop_list`, `morph`, `recolor`, `travel`, `leave` ...), the same move for the same kind of
  object every time: repetition reads as authored, variety for its own sake reads as generated.
- Lay out a frame, `check_layout(...)` it, then play it. Make room first, then enter.
- Carry the central picture across beats; do not clear the stage.
- Build new shapes from primitives in the scene file, the kit's way.

**Remotion** (`<Component>.tsx`, `import { ... } from "@kit"`):

```tsx
export const TrainingLoop: React.FC = () => {
  const { t, cue, word } = useTimeline();              // t = seconds since the section began
  const typing = ramp(t, word("Code", "code"), 0.4);   // starts when "code" is spoken
  ...
};
```

- Every value on screen is a function of `t`. No CSS animation, timers, state or randomness:
  frames are captured one at a time, so anything that animates by itself renders wrong.
- Entrances with `<Enter at=...>`, type with `<Txt>`, code with `<Code>`, numbers with `<Num>`.
  Positions in px on the 1920 x 1080 canvas; colours, sizes and fonts from `@kit` only.
- The opening picture is on stage from the segment's first frame, so a cut never lands on an
  empty stage.
- Colour roles are the video's: a term is the colour it has in the Manim scenes.

Never type a colour, font, size or duration into a scene: import the name. Values live in
`theme/tokens.json`, which is what keeps the two engines identical.

## 4. Draft, look, fix (never skip)

```bash
./x draft <section>                        # 960x540, a few seconds; --only <Name> for one segment
./x still <section> <Component> t1 t2      # Remotion frames without a render
./x frames <video.mp4> t1 t2 ...           # chosen frames of any render
```

Fix every line the draft prints:

| Line | Means | Do |
|---|---|---|
| `TIMING ... is 0.3s late` | The moves before that cue outlast the narration | Shorten them or start them earlier. Never move the cue |
| `OVERLAP at 7.6s: A / B` | Two objects touched or crossed, even briefly | Make room first, reroute the move, or `allow_overlap()` a crossing that is meant |
| `LAYOUT: ... leaves the safe area` | A composed frame is too wide or tall | Scale or rearrange |
| `STILL 31.2-34.4 s` | Nothing changed for over 2.5 s | Give the voice's next point a real change: a signal, a value, a highlight, a reframe |

Then look, in this order: the storyboard `renders/<video>/qa/<file>_draft_sheet.png` (read it as
a viewer with the sound off); the cue sheet `..._draft_cues.png`; and a detail sheet at the
moments evenly spaced frames miss: the middle of every transform, each engine switch, each label
landing. Check:

- Nothing clipped, in the margin, touching or crossing. One focal point, a third of the frame
  empty, the hero large.
- At most three accent colours; roles as in `CONTINUITY.md`; no library default colours.
- Labels of 1 to 3 words, shown after their object, none under 24 px; no narration on screen.
- The same kind of object entered the same way; nothing bounces, flashes, wiggles or drifts.
- The picture transformed instead of the stage clearing; nothing faded out only to fade back in.
- Something meaningful changes every couple of seconds.
- Engine switches land on a composed frame, and colour roles survive the cut.
- Frame 0 is already moving; the last frame is a clean still.
- A viewer with the sound off could follow it.

Repeat until the draft prints `QA: clean` and the sheets pass your own eye: usually one to three
rounds.

## 5. Final

```bash
./x typecheck
./x final <section>        # 3840x2160 at the video's frame rate
```

Run the final in the background and send the draft or a `./x preview` meanwhile: nobody should
wait on a render. When it prints `FINAL:`, look at one full-size frame at the most text-dense
moment (`./x frames renders/<video>/<file>.mp4 <t> --width 1920`). If `VERIFY` fails, fix the
cause and render again. A file that has not passed verification is not delivered.

## 6. Record

Append the section's block to the video's `CONTINUITY.md` (format in the file) and write the
section's `README.md` (how it plays, colour roles, cue sheet).

## 7. Deliver

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

When a review arrives: log it in the workspace's `FEEDBACK.md` first (the words as given, the
cause, the fix, the rule), then fix the section, then draft and final again. If the note applies
beyond this section, make it a standing rule there. If a check could have caught it, make the
check catch it. A note given once should never have to be given twice.

## Voiceover

```bash
./x align <section> <voiceover.wav> [--start S --end E]     # needs the speech extra once: ./x setup --voice
./x draft <section>                                         # now with sound
```

Every beat and word takes its measured time; the code does not change. Fix the `TIMING` lines the
faster or slower voice produces, then render the final. With only the recording's length,
`./x time <section> --total <seconds>` fits the estimate to it. Never alter the audio to fit the
picture, and never add a synthetic voice to a deliverable.

## Keeping the system honest

- `./x doctor` says what is missing; `./x parity` renders one test card in both engines and
  measures that colours, type, strokes and backdrop still match. Run parity after changing
  `theme/tokens.json`, the fonts, either kit, or upgrading Manim or Remotion.
- Style changes go in `theme/tokens.json`, followed by `./x contrast`, `./x specimens`, `./x parity`.
- A shape a second section needs moves from the section into the kit, gets a specimen
  (`tools/specimens.py`) and is looked at.
- A quirk that cost time goes into `docs/PITFALLS.md`. Read that file before debugging an engine.
- Media is never committed: renders, voiceovers and footage are git-ignored. If the workspace has
  a public remote, keep unreleased scripts and private details out of commits.
- Remotion is free for individuals and for companies of up to three people; larger companies need
  a company licence.
