# 01 · How a model learns

The reference section: 22.8 seconds, three segments, two engines. Read `beats.json`, `scene.py`
and `TrainingLoop.tsx` before building a section; this is the bar for pacing and density.

```bash
./x draft demo/01-training      # a few seconds
./x final demo/01-training      # 3840x2160 at 60 fps, about a minute
```

## How it plays

- **Noise.** A grey box of six dials draws on in the centre and is named "model". On "noise" every
  needle swings to a random setting.
- **Guess.** The model settles a little to the left as a question is written beside it: "The
  capital of France is" and a yellow blank. An arrow feeds it, a signal runs in, and four equally
  unsure guesses pop out on the right.
- **Wrong.** A red box draws round the guesses and a red "loss 2.31" rises under it. Then the stage
  rearranges: the question leaves, the model moves left, and a curve draws with a red point high
  on it; the loss number takes its place above the axis.
- **Downhill.** Four nudges, each on its word: the point steps down the curve, the dials turn a
  little, and the loss falls to 0.21.
- **Code** (Remotion). A cut to an editor on the same stage. Four lines type in, one per phrase;
  on "four" their line numbers count up in yellow.
- **Loop** (Remotion). The editor makes room, a band steps through the loop twice, then covers it
  as a step counter races to 5,000 and the loss readout falls to 0.04.
- **Works.** A cut back to the model: its needles swing into agreement, the same question goes in,
  and one long bar answers. "Paris 97%" is boxed in yellow and written into the blank.

## Colours

Light blue is the question, teal the model's settings, red the loss, yellow the answer. `loss` and
`model` are red and teal in the code because they are red and teal in the picture.

## Cue sheet (estimated at 150 words a minute)

```
00:00.00  Noise
00:02.74  Guess
00:05.58  Wrong
00:08.37  Downhill
00:12.61  Code       <- Remotion from here
00:15.79  Loop
00:17.99  Works      <- Manim again
00:22.80  END
```
