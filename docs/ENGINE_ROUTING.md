# Choosing the engine

Every run of beats is drawn by the engine that suits it. The choice is made per beat, from what the
beat **shows**, not from what it says, and written into `beats.json → segments`.

## The one question

> Is this beat a picture that **transforms**, or a surface that is **laid out**?

A picture that transforms is geometry: shapes that become other shapes, things placed by coordinates,
math. That is Manim. A surface that is laid out is type and boxes on a grid: an interface, an
editor, a table, a document. That is Remotion.

## The table

| The beat shows | Engine | Why |
|---|---|---|
| A diagram whose parts move, merge, split or become something else | **Manim** | Any shape interpolates into any other |
| Math: equations, terms that move between lines, anything typeset | **Manim** | `eq()` with named parts |
| Graphs and plots, curves, slopes, a point moving on a curve | **Manim** | Axes and coordinates |
| Vectors, matrices, embeddings, probability lists | **Manim** | `bracket_vector`, `bar_list` |
| A model, a network, tokens flowing through a machine | **Manim** | `dial_panel`, `neural_net`, `token`, `travel` |
| A metaphor or concept drawn as a pictogram scene | **Manim** | Line pictograms that morph |
| Architecture and flow: boxes, arrows, signals travelling | **Manim** | Morphing and paths |
| A spatial idea: vector spaces, surfaces, stacked layers | **Manim** (`Segment3D`) | A real 3D camera |
| Code in an editor: syntax colour, typing, a highlight stepping through lines, a diff | **Remotion** | Type on a baseline grid |
| A terminal session, logs scrolling, a command and its output | **Remotion** | Monospace layout |
| A product: chat window, app, browser, dashboard, settings page, a form | **Remotion** | It is literally a web page |
| A table, a comparison grid, a pricing sheet, a leaderboard | **Remotion** | Rows and columns that align |
| Counters and readouts, progress, a clock or timer in a panel | **Remotion** | Numbers in a layout |
| Paragraphs: a document, an email, a search result, a long prompt and reply | **Remotion** | Text that wraps |
| Data-driven charts with many marks (hundreds of points or bars) | **Remotion** | SVG from data |
| Screenshots, photographs, footage, screen recordings | **Remotion** | Images and video |
| 3D with lit materials, or a Lottie animation | **Remotion** (add `@remotion/three` or `@remotion/lottie`) | Not what Manim renders |

## Tie-breakers

1. **When in doubt, Manim.** It is the house language. Reach for Remotion when the beat is plainly
   a surface.
2. **Follow the object, not the topic.** "The model writes code" is about a model: Manim, with code
   as grey bars (`code_bars`). "Here are the four lines" is about the code: Remotion.
3. **Does a shape have to become another shape?** Then Manim, even if text is involved.
4. **Does text have to wrap, align in columns or look like a real interface?** Then Remotion, even
   if a diagram would be nicer.
5. **Keep one beat's picture in one engine.** There is no layering of one engine over the other.
6. **Do not switch for one beat.** A segment needs to be on screen long enough to be worth a cut:
   at least a full sentence, and never under a second (`./x check` refuses that). If a lone beat
   wants the other engine, draw a simpler version of it in the engine around it.
7. **Switch where the picture changes subject anyway.** A switch is a hard cut. Put it where the
   narration turns ("In code, ...", "Here is what that looks like in the app"), not in the middle
   of a thought.
8. **Expect one to three switches a minute at most.** Most sections are mostly one engine.

## Making a switch invisible

See "Engine switches" in [`STYLE.md`](../STYLE.md). In short: the incoming picture is on stage from
its first frame, colour roles carry across the cut, and anything that appears on both sides keeps
its place and size.

## Worked example

`videos/demo/01-training` is 23 seconds across both engines:

| Beats | Narration | Engine | Reason |
|---|---|---|---|
| Noise, Guess | "Every AI model starts out as noise. Ask it a question, and it guesses." | Manim | A model as a box of dials; a question flows in, guesses come out |
| Wrong, Downhill | "Training measures how wrong that guess is, and nudges every number ... downhill." | Manim | A point descending a curve while the dials turn |
| Code, Loop | "In code, that whole idea is four lines. Run them a few thousand times," | **Remotion** | An editor: four lines typed in, a band stepping through them, two readouts counting |
| Works | "and the noise turns into something that knows the answer." | Manim | Back to the model: its dials settle, one bar answers |

The switches fall on "In code," and on "and the noise", where the narration itself changes subject.
`loss` is red and `model` is teal in the code because they are red and teal in the picture.

## How it is written down

```json
"segments": [
  { "engine": "manim",    "scene": "Learn",            "from": "Noise", "to": "Code" },
  { "engine": "remotion", "component": "TrainingLoop", "from": "Code",  "to": "Works" },
  { "engine": "manim",    "scene": "Answer",           "from": "Works", "to": "END" }
]
```

A Manim segment names a scene class in the section's `scene.py`. A Remotion segment names a
component exported from `<Component>.tsx` in the section folder. Segments must cover the section
without gaps: the first starts on the first beat, each starts where the last one stopped, and the
last runs to `END`.

`./x new` prints a first guess beside each beat (`remotion? (code)`). It only looks at words; the
choice is yours.
