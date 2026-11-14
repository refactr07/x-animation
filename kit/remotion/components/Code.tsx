import React from "react";
import { useTimeline } from "../cues";
import { type Lang, sliceTokens, tokenize } from "../highlight";
import { FONT, P, RADIUS, STROKE, tint, TYPE } from "../theme";
import { clamp01, ramp } from "../time";
import { useStage } from "./Stage";

type CodeProps = {
  code: string;
  lang?: Lang;
  /** Identifiers that carry one of the video's colour roles: { loss: P.red, model: P.teal }. */
  roles?: Record<string, string>;
  /** Section time at which each line starts typing. Omit for code that is simply there. */
  lineAt?: (line: number) => number;
  /** Seconds a line takes to type. */
  typeDur?: number;
  /** The line the highlight band sits on: a fraction slides it between lines. Omit for no band. */
  active?: number | null;
  /** Colour of the band and of the active line's number. */
  accent?: string;
  /** 0..1 strength of the band, to bring it in and out. */
  band?: number;
  /** How many lines the band covers, starting at `active` (a fraction grows it smoothly). */
  span?: number;
  size?: number;
  lineHeight?: number;
  numbers?: boolean;
  /** Colour of one line's number, e.g. to count lines on a spoken number. */
  numberColor?: (line: number) => string | undefined;
  style?: React.CSSProperties;
};

/**
 * Code in Computer Modern Typewriter, coloured from the house palette. Lines can type themselves in
 * on their cues and a band can step through them. No window chrome: a panel holds it (see Panel).
 */
export const Code: React.FC<CodeProps> = ({
  code,
  lang = "python",
  roles,
  lineAt,
  typeDur = 0.4,
  active = null,
  accent = P.yellow,
  band = 1,
  span = 1,
  size = TYPE.body,
  lineHeight = 1.6,
  numbers = true,
  numberColor,
  style,
}) => {
  const { t } = useTimeline();
  const stage = useStage();
  const lines = code.replace(/\n$/, "").split("\n");
  const row = size * lineHeight;
  const gutter = numbers ? size * 1.5 : 0;
  return (
    <div style={{ position: "relative", fontFamily: FONT.mono, fontSize: size, lineHeight: `${row}px`, whiteSpace: "pre", ...style }}>
      {active !== null && band > 0 ? (
        <div
          style={{
            position: "absolute",
            left: -size * 0.45,
            right: -size * 0.45,
            top: active * row,
            height: row * span,
            borderRadius: RADIUS.shape * 0.6,
            backgroundColor: tint(accent, 0.2 * band, stage),
            boxShadow: `inset ${STROKE.shape}px 0 0 ${tint(accent, band, stage)}`,
          }}
        />
      ) : null}
      {lines.map((line, i) => {
        const tokens = tokenize(line, lang, roles);
        const start = lineAt ? lineAt(i) : -Infinity;
        const shown = lineAt ? Math.floor(clamp01((t - start) / typeDur) * Array.from(line).length + 1e-6) : Infinity;
        const visible = lineAt ? sliceTokens(tokens, shown) : tokens;
        const isActive = active !== null && band > 0.5 && i >= Math.round(active) && i < Math.round(active + span);
        return (
          <div key={i} style={{ position: "relative", height: row, display: "flex" }}>
            {numbers ? (
              <span
                style={{
                  width: gutter,
                  flex: "none",
                  color: numberColor?.(i) ?? (isActive ? accent : P.greyC),
                  opacity: lineAt ? ramp(t, start, 0.2) : 1,
                  fontSize: size * 0.78,
                }}
              >
                {i + 1}
              </span>
            ) : null}
            <span>
              {visible.map((tok, k) => (
                <span key={k} style={{ color: tok.color, fontStyle: tok.italic ? "italic" : undefined }}>
                  {tok.text}
                </span>
              ))}
            </span>
          </div>
        );
      })}
    </div>
  );
};

/** Height in px of a block of `lines` lines, to lay a panel out around it. */
export const codeHeight = (lines: number, size: number = TYPE.body, lineHeight = 1.6): number => lines * size * lineHeight;
