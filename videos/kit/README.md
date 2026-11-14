# kit: self-tests

Not a video. Sections here exist to test the system itself.

- `00-parity`: the same test card drawn by Manim and by Remotion. `./x parity` renders both through
  the normal pipeline and measures how far apart they are in colour, type size, stroke width and
  backdrop. Run it after changing `theme/tokens.json`, the fonts, either kit, or upgrading Manim or
  Remotion.
