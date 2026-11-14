# FEEDBACK.md: standing rules and review log

Read this before planning or changing any animation. Every piece of feedback is logged here **in the
same turn it is given**: the words as given, what was wrong, what changed, and the rule that keeps it
from happening again. Standing rules override [`STYLE.md`](STYLE.md) and everything else in this
repo.

## Standing rules

These are the author's standing taste, carried over from earlier projects where each was given as
review feedback. They apply from the first section. Confirm, change or drop them as reviews of this
repo's own videos come in.

### The picture

- **R1. Dark theme.** Every video plays on a dark stage unless asked otherwise. Never a warm or
  reddish background.
- **R2. Clean like 3Blue1Brown, and never looks AI-generated.** Authored, consistent, calm. Build
  original pictures in that language; never use 3Blue1Brown's own characters, logo or shots, or
  any real brand's logo.
- **R3. Clean and minimalist.** One picture per beat with generous empty space; about five object
  groups and three accent colours on screen at most; thin strokes; nothing that carries no meaning
  (window chrome for its own sake, filler boxes, ornaments).
- **R4. No overlapping objects, ever**, in any frame, mid-move included, unless one deliberately
  contains the other. Plan every move's path and every entry's slot so the space is free first:
  make room, then enter. (Enforced by the overlap audit in every Manim render.)
- **R5. Minimal text.** Labels are 1 to 3 words, beside what they name, at least 24 px at 1080p.
  No narration captions, bullet lists or titles across the top. Numbers and shapes beat words.
  Text that is the subject (a prompt, a sentence, code) is content and is welcome.
- **R6. Every element is clearly visible against its background**: text at 4.5:1 or better,
  strokes and shapes at 3:1 or better, on every backdrop. (`./x contrast`.)
- **R7. Colour is meaning.** A concept keeps its colour for the whole video; at most three accents
  in a frame; never a library's default colours.

### The motion

- **R8. Dynamic, for retention.** Something meaningful changes on screen at least every two seconds
  or so; no still stretch longer than 2.5 s. Each beat opens with motion on its cue, and the kind
  of motion varies from beat to beat (transform, reframe onto the named detail and back, swap,
  pour, count, travelling signal, build). Motion is always purposeful. (Enforced by the stillness
  check in every render.)
- **R9. No decoration in motion.** No idle pulsing, wiggles, flashes, bounces or overshoot,
  shaking, or aimlessly drifting cameras.
- **R10. One motion vocabulary.** The same kind of object always enters the same way.
- **R11. Continuity.** Transform the central picture into the next idea instead of clearing the
  stage. Frame 0 is already moving; the last frame is a clean still.
- **R12. On the word.** Every visual lands on the word it illustrates. The audio is never altered
  to fit the picture.

### The production

- **R13. The best engine for each stretch.** Manim for pictures that transform, Remotion for
  surfaces that are laid out; switch only at beat boundaries. ([`docs/ENGINE_ROUTING.md`](docs/ENGINE_ROUTING.md).)
- **R14. One backdrop per pasted script portion**, for its whole length. The next portion uses a
  different one, chosen by its content. Never change it inside a portion.
- **R15. Deliver verified masters only**: 3840 x 2160 at the video's frame rate (60 fps unless the
  video says otherwise), H.264. A file that has not passed verification is not delivered.
- **R16. Never make the author wait on a render.** Send the draft or the preview first; run the 4K
  in the background.
- **R17. Narration is verbatim.** The script is saved exactly as pasted, typos and all, and the
  beats must say exactly what it says. Never add a synthetic voice to a deliverable.
- **R18. Work end to end in one turn**: plan, build, check, render, deliver. Ask only when the
  script depends on data or assets that are not available.

## Review log

| # | Date | Section / version | Feedback (verbatim) | What was wrong | Fix | Rule |
|---|---|---|---|---|---|---|
| | | | | | | |

### How to add an entry

1. Add a row: the next number, the date, the section and version, the feedback quoted exactly, the
   root cause in one line, the fix, and the rule it produced or confirmed.
2. If the lesson applies beyond that one section, add or amend a standing rule above and name it
   in the row.
3. If it changes the look, change `theme/tokens.json` or `STYLE.md` in the same turn, and run
   `./x contrast`, `./x specimens` and `./x parity`.
4. If a check could have caught it, make the check catch it.
