// SECTION demo/01-training, segment TrainingLoop (beats Code and Loop), drawn by Remotion.
//
// Why Remotion: the picture is an editor. Type on a baseline grid, syntax colour, a band stepping
// through lines and two running readouts are layout and typography, which is what React is for.
// The Manim segments on either side draw the same idea as a picture (scene.py).
//
// Colour roles are the video's: `loss` is red and `model` is teal here because they are red and teal
// in the Manim scenes. No time below is a number of seconds from the start: cue() and word() read
// beats.json, so retiming to a voiceover moves everything with it.
import { clamp01, Code, codeHeight, Enter, lerp, Num, P, Panel, ProgressBar, ramp, smooth, track, Txt, TYPE, useTimeline } from "@kit";
import React from "react";

const CODE = `for step in range(5000):
    loss = model(batch)
    loss.backward()
    optimizer.step()`;

const ROLES = { loss: P.red, model: P.teal, batch: P.blueLight };
const STEPS = 5000;

// The editor panel: centred while the code is written, then it makes room for the readouts.
const SIZE = TYPE.label;
const PANEL = { w: 1040, h: 520, y: 280, xCentred: 440, xLeft: 130 };
const READOUT_X = 1290;

export const TrainingLoop: React.FC = () => {
  const { t, cue, word } = useTimeline();
  const loop = cue("Loop");

  // Code: "In code, that whole idea is four lines." One line per phrase, then the four are counted.
  const lineAt = [word("Code", "code"), word("Code", "that"), word("Code", "whole") + 0.15, word("Code", "idea") + 0.2];
  const counted = word("Code", "four");
  const makeRoom = loop - 0.4;

  // Loop: "Run them a few thousand times," Two passes you can follow, then the count races away.
  const pass1 = loop + 0.1;
  const pass2 = pass1 + 0.48;
  const race = pass2 + 0.52;
  const done = word("Loop", "times") + 0.35;
  const q = clamp01((t - race) / (done - race));

  const panelX = lerp(PANEL.xCentred, PANEL.xLeft, ramp(t, makeRoom, 0.5));
  const active = track(t, [
    [pass1, 1], [pass1 + 0.16, 2], [pass1 + 0.32, 3], [pass2, 3],
    [pass2 + 0.08, 1], [pass2 + 0.18, 2], [pass2 + 0.28, 3], [pass2 + 0.38, 3], [race, 1],
  ]);
  const span = lerp(1, 3, ramp(t, pass2 + 0.38, race - pass2 - 0.38));
  const band = ramp(t, pass1 - 0.05, 0.15) * lerp(1, 0.7, q);

  const step = t < pass2 ? (t < pass2 - 0.02 ? 0 : 1) : t < race ? (t < pass2 + 0.36 ? 1 : 2) : Math.round(lerp(2, STEPS, smooth(q)));
  const loss =
    t < race
      ? track(t, [[pass2 - 0.02, 2.31], [pass2 + 0.12, 2.24], [pass2 + 0.36, 2.24], [pass2 + 0.5, 2.17]])
      : lerp(2.17, 0.04, 1 - Math.pow(1 - q, 3));

  const inner = (PANEL.h - codeHeight(4, SIZE)) / 2;
  const readoutAt = loop - 0.1;

  return (
    <>
      {/* The editor is on stage from the first frame: a cut between engines never lands on an empty stage. */}
      <Panel x={panelX} y={PANEL.y} w={PANEL.w} h={PANEL.h} color={P.greyB} fill={0.1}>
        <Code
          code={CODE}
          lang="python"
          roles={ROLES}
          size={SIZE}
          lineAt={(i) => lineAt[i]}
          typeDur={0.4}
          active={t >= pass1 - 0.05 ? active : null}
          span={span}
          band={band}
          numberColor={(i) => (t >= counted + i * 0.09 && t < makeRoom ? P.yellow : undefined)}
          style={{ position: "absolute", left: 84, top: inner }}
        />
      </Panel>

      <Enter at={readoutAt} kind="rise" dur={0.4} style={{ position: "absolute", left: READOUT_X, top: 349 }}>
        <Txt size={TYPE.small} color={P.greyB}>step</Txt>
      </Enter>
      <Enter at={readoutAt + 0.06} kind="rise" dur={0.4} style={{ position: "absolute", left: READOUT_X, top: 390 }}>
        <Num value={step} size={TYPE.title} />
      </Enter>
      <Enter at={readoutAt + 0.12} kind="fade" dur={0.4} style={{ position: "absolute", left: READOUT_X, top: 513 }}>
        <ProgressBar value={step / STEPS} w={520} color={P.greyA} />
      </Enter>
      <Enter at={readoutAt + 0.18} kind="rise" dur={0.4} style={{ position: "absolute", left: READOUT_X, top: 593 }}>
        <Txt size={TYPE.small} color={P.red}>loss</Txt>
      </Enter>
      <Enter at={readoutAt + 0.24} kind="rise" dur={0.4} style={{ position: "absolute", left: READOUT_X, top: 634 }}>
        <Num value={loss} decimals={2} size={TYPE.title} color={P.red} />
      </Enter>
    </>
  );
};
