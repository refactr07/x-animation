// The motion vocabulary for Remotion: the same moves as xkit.motion, driven by the section clock.
// One move per kind of object, used the same way every time. Nothing bounces, flashes or wiggles.
import React from "react";
import { useTimeline } from "../cues";
import { MOTION } from "../theme";
import { clamp01, type Ease, easeIn, easeOut, ramp, smooth } from "../time";

export type EnterKind = "rise" | "pop" | "fade" | "slide";

type EnterProps = {
  /** Section time at which it arrives. */
  at: number;
  /** Section time at which it leaves (it fades, shorter than it came in). Omit to stay. */
  out?: number;
  /** rise: labels and numbers. pop: dots, chips, badges. fade: panels and pictures. slide: list rows. */
  kind?: EnterKind;
  dur?: number;
  /** Travel in px for rise and slide. */
  distance?: number;
  ease?: Ease;
  style?: React.CSSProperties;
  children?: React.ReactNode;
};

const DEFAULT_DUR: Record<EnterKind, number> = { rise: 0.6, pop: 0.5, fade: 0.8, slide: MOTION.list_item };

/** An element that arrives at `at` and (optionally) leaves at `out`. Position it with `style`. */
export const Enter: React.FC<EnterProps> = ({ at, out, kind = "rise", dur, distance, ease = smooth, style, children }) => {
  const { t } = useTimeline();
  const d = dur ?? DEFAULT_DUR[kind];
  const p = ramp(t, at, d, ease);
  const q = out === undefined ? 0 : ramp(t, out, MOTION.fast, easeIn);
  if (p <= 0 || q >= 1) return null;
  const travel = (1 - p) * (distance ?? (kind === "slide" ? 20 : 34));
  return (
    <div
      style={{
        ...style,
        opacity: clamp01(p * 1.6) * (1 - q),
        translate: kind === "rise" ? `0px ${travel}px` : kind === "slide" ? `${-travel}px 0px` : undefined,
        scale: kind === "pop" ? String(0.6 + 0.4 * p) : undefined,
      }}
    >
      {children}
    </div>
  );
};

/** Start times for a run of like things arriving one after another. */
export const cascade = (start: number, count: number, lag: number = MOTION.list_lag): number[] =>
  Array.from({ length: count }, (_, i) => start + i * lag);

type WriteProps = {
  text: string;
  at: number;
  /** Seconds per glyph. The whole word takes about glyphs x this, as in xkit.motion.write. */
  perGlyph?: number;
  color?: string;
  style?: React.CSSProperties;
};

/**
 * Words arriving letter by letter: each glyph shows as an outline first, then fills. The Remotion
 * counterpart of Manim's Write, for a word or a short line.
 */
export const Write: React.FC<WriteProps> = ({ text, at, perGlyph = MOTION.write_per_glyph, color = "currentColor", style }) => {
  const { t } = useTimeline();
  const glyphs = Array.from(text);
  const inked = glyphs.filter((g) => g.trim()).length;
  const total = Math.min(MOTION.write_max, Math.max(MOTION.write_min, perGlyph * inked + 0.3));
  const each = Math.min(0.45, total * 0.5);
  const lag = inked > 1 ? (total - each) / (inked - 1) : 0;
  if (t < at) return <span style={{ ...style, visibility: "hidden" }}>{text}</span>;
  let k = 0;
  return (
    <span style={{ ...style, whiteSpace: "pre" }}>
      {glyphs.map((g, i) => {
        if (!g.trim()) return <span key={i}>{g}</span>;
        const p = clamp01((t - at - k++ * lag) / each);
        const outline = p < 0.5 ? easeOut(p * 2) : 1 - smooth((p - 0.5) * 2);
        const fill = smooth((p - 0.35) / 0.65);
        return (
          <span
            key={i}
            style={{
              // the fill and the outline fade separately; `color` itself is left alone so that
              // "currentColor" keeps meaning the colour of the text around it
              WebkitTextFillColor: withAlpha(color, fill),
              WebkitTextStroke: `1.5px ${withAlpha(color, outline)}`,
            }}
          >
            {g}
          </span>
        );
      })}
    </span>
  );
};

const withAlpha = (color: string, a: number): string => {
  if (color.startsWith("#") && color.length === 7) {
    const n = parseInt(color.slice(1), 16);
    return `rgba(${(n >> 16) & 255}, ${(n >> 8) & 255}, ${n & 255}, ${clamp01(a)})`;
  }
  return `color-mix(in srgb, ${color} ${Math.round(clamp01(a) * 100)}%, transparent)`;
};

/** Text that types itself, a character at a time: prompts, commands, code. */
export const typed = (text: string, t: number, at: number, dur: number): string => {
  if (dur <= 0) return t >= at ? text : "";
  const n = Math.floor(clamp01((t - at) / dur) * Array.from(text).length + 1e-6);
  return Array.from(text).slice(0, n).join("");
};
