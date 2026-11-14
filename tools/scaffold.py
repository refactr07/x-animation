#!/usr/bin/env python3
"""Write a starting point for every segment of a section, from its beats.json.

    ./x scaffold <section>

For each Manim segment it adds a scene class to scene.py; for each Remotion segment it writes
<Component>.tsx. Each starts with the beats it owns, their narration and their planned picture, so
the work that is left is the pictures themselves. Nothing that exists is overwritten: a class or a
file that is already there is left alone. Run ./x sync afterwards (the render does it for you).
"""

from __future__ import annotations

import re
import sys

from xcore.beats import Beats
from xcore.paths import ROOT

SCENE_HEAD = '''from xkit import *

# SECTION {key}, "{title}"
#
# Colour roles: <concept = COLOUR, ... fixed for the whole video: see CONTINUITY.md>
# Central picture: <the one thing that persists and keeps transforming>
#
# No number of seconds below places a beat: beat() and on() follow the narration in beats.json.
'''

SCENE_CLASS = '''

class {name}(Segment):
    def construct(self):
{beats}
        self.finish()
'''

SCENE_BEAT = '''        # ---------------------------------------------------------------- {name}
        # "{text}"
        # picture: {picture}
        self.beat("{name}")
        # self.on("<a word from the line above>")   then   self.play(...)
'''

COMPONENT = '''// SECTION {key}, segment {name} ({beat_list}), drawn by Remotion.
//
// Why Remotion: <what makes this stretch layout, type, UI or data rather than a picture that transforms>
//
// No time below is a number of seconds from the start: cue() and word() read beats.json.
import {{ Enter, P, ramp, Txt, TYPE, useTimeline }} from "@kit";
import React from "react";

export const {name}: React.FC = () => {{
  const {{ t, cue, word }} = useTimeline();
{cues}
  void t;
  void word;
  void ramp;

  return (
    <>
      {{/* Whatever opens the segment is on stage from its first frame: a cut never lands on an empty stage. */}}
      <Enter at={{{first}}} kind="rise" style={{{{ position: "absolute", left: 200, top: 480 }}}}>
        <Txt size={{TYPE.label}} color={{P.white}}>{name}</Txt>
      </Enter>
    </>
  );
}};
'''


def var(name: str) -> str:
    return name[0].lower() + name[1:]


def main() -> None:
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    beats = Beats.load(sys.argv[1])
    section = beats.dir
    key = f"{section.parent.name}/{section.name}"

    scene = section / "scene.py"
    text = scene.read_text() if scene.exists() else SCENE_HEAD.format(key=key, title=beats.data.get("title", section.name))
    added = []
    for seg in beats.segments:
        own = beats.beats_in(seg)
        if seg.engine == "manim":
            if re.search(rf"^class {seg.name}\(", text, flags=re.M):
                continue
            body = "\n".join(
                SCENE_BEAT.format(name=b.name, text=b.text.replace('"', "'"), picture=b.picture or "<what we see, and the one change that lands on the words>")
                for b in own
            )
            text += SCENE_CLASS.format(name=seg.name, beats=body.rstrip("\n"))
            added.append(f"scene.py: class {seg.name}")
        else:
            path = section / f"{seg.name}.tsx"
            if path.exists():
                continue
            cues = "\n".join(f'  const {var(b.name)} = cue("{b.name}"); // "{b.text}"' for b in own)
            path.write_text(COMPONENT.format(key=key, name=seg.name, beat_list=", ".join(b.name for b in own),
                                             cues=cues, first=var(own[0].name)))
            added.append(f"{path.name}")
    if any(s.engine == "manim" for s in beats.segments) and (not scene.exists() or scene.read_text() != text):
        scene.write_text(text)
    print(("SCAFFOLD: wrote " + ", ".join(added)) if added else "SCAFFOLD: nothing to add, every segment already has its code")
    print(f"  in {section.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
