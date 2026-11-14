// The Remotion kit on one stage: every component, arriving the way it arrives in a video.
// `./x still kit/01-remotion-kit KitSheet 0.9 4.5` shows it mid-entrance and settled.
// Look at it after changing kit/remotion or theme/tokens.json.
import {
  Arrow, Bubble, cascade, Chip, Code, Enter, HighlightBox, Num, P, Panel, ProgressBar, ramp, Token, Txt, TYPE, typed,
  useTimeline, Window, Write,
} from "@kit";
import React from "react";

const CODE = `def answer(question):
    return model(question)  # one call`;

export const KitSheet: React.FC = () => {
  const { t, cue } = useTimeline();
  const t0 = cue("Sheet");
  const rows = cascade(t0 + 0.6, 3);
  const p = ramp(t, t0 + 0.5, 1.2);
  return (
    <>
      {/* type */}
      <div style={{ position: "absolute", left: 110, top: 84 }}>
        <Txt size={TYPE.heading}>
          <Write text="Words write on" at={t0 + 0.2} />
        </Txt>
      </div>
      <Enter at={t0 + 0.3} kind="rise" style={{ position: "absolute", left: 110, top: 190 }}>
        <Txt size={TYPE.body} color={P.blueLight}>a label rises</Txt>
      </Enter>
      <Enter at={t0 + 0.4} kind="pop" style={{ position: "absolute", left: 470, top: 186 }}>
        <Chip color={P.yellow}>A Chip Pops</Chip>
      </Enter>
      <Enter at={t0 + 0.5} kind="pop" style={{ position: "absolute", left: 720, top: 184 }}>
        <Token color={P.blue}>token</Token>
      </Enter>
      <Enter at={t0 + 0.55} kind="pop" style={{ position: "absolute", left: 850, top: 184 }}>
        <Token color={P.yellow}>next</Token>
      </Enter>
      <div style={{ position: "absolute", left: 110, top: 270 }}>
        <Txt size={TYPE.small} color={P.greyB} family="mono">{typed("$ text types itself, a character at a time", t, t0 + 0.3, 1.4)}</Txt>
      </div>

      {/* a list */}
      {["rows land", "top to bottom", "a beat apart"].map((row, i) => (
        <Enter key={row} at={rows[i]} kind="slide" style={{ position: "absolute", left: 110, top: 350 + i * 58 }}>
          <Txt size={TYPE.small}>{row}</Txt>
        </Enter>
      ))}

      {/* arrows and highlights */}
      <Arrow from={[470, 400]} to={[760, 400]} progress={p} />
      <Arrow from={[470, 470]} to={[760, 470]} progress={p} color={P.greyB} width={5} head={26} />
      <div style={{ position: "absolute", left: 830, top: 372 }}>
        <Txt size={TYPE.body}>look here</Txt>
      </div>
      <HighlightBox x={812} y={362} w={236} h={72} progress={p} />

      {/* numbers */}
      <div style={{ position: "absolute", left: 110, top: 560 }}>
        <Txt size={TYPE.small} color={P.greyB}>step</Txt>
      </div>
      <div style={{ position: "absolute", left: 110, top: 600 }}>
        <Num value={Math.round(5000 * p)} size={TYPE.title} />
      </div>
      <ProgressBar value={p} w={420} style={{ position: "absolute", left: 110, top: 720 }} />
      <div style={{ position: "absolute", left: 590, top: 600 }}>
        <Num value={2.31 - 2.27 * p} decimals={2} size={TYPE.title} color={P.red} />
      </div>

      {/* code in a panel */}
      <Panel x={110} y={800} w={940} h={200}>
        <Code code={CODE} roles={{ model: P.teal, question: P.blueLight }} size={TYPE.small} active={1} band={p} style={{ position: "absolute", left: 60, top: 42 }} />
      </Panel>

      {/* a product */}
      <Window x={1140} y={84} w={670} h={916} title="assistant">
        <Enter at={t0 + 0.4} kind="rise" style={{ position: "absolute", inset: 0 }}>
          <Bubble x={170} y={60} w={460} side="right">What is the capital of France?</Bubble>
        </Enter>
        <Enter at={t0 + 0.9} kind="rise" style={{ position: "absolute", inset: 0 }}>
          <Bubble x={40} y={240} w={420} side="left">Paris.</Bubble>
        </Enter>
        <Enter at={t0 + 1.3} kind="fade" style={{ position: "absolute", left: 40, top: 400 }}>
          <Panel x={0} y={0} w={590} h={150} color={P.teal} fill={0.18}>
            <div style={{ position: "absolute", left: 36, top: 44 }}>
              <Txt size={TYPE.body} color={P.teal}>a tinted panel</Txt>
            </div>
          </Panel>
        </Enter>
      </Window>
    </>
  );
};
