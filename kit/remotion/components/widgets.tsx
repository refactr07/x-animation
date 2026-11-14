// Themed building blocks for Remotion segments: the counterparts of xkit.shapes.
// Everything is positioned in px on the 1920x1080 canvas; use theme.px() to place something exactly
// where a Manim scene has it.
import React from "react";
import { FONT, P, RADIUS, STROKE, tint, TYPE } from "../theme";
import { clamp01 } from "../time";
import { useStage } from "./Stage";

type Box = { x: number; y: number; w: number; h: number };

/** Absolutely positioned box, the layout primitive of a segment. */
export const At: React.FC<Partial<Box> & { anchor?: "top-left" | "center"; style?: React.CSSProperties; children?: React.ReactNode }> = ({
  x = 0,
  y = 0,
  w,
  h,
  anchor = "top-left",
  style,
  children,
}) => (
  <div
    style={{
      position: "absolute",
      left: x,
      top: y,
      width: w,
      height: h,
      translate: anchor === "center" ? "-50% -50%" : undefined,
      ...style,
    }}
  >
    {children}
  </div>
);

/** A rounded panel: stroke in `color`, solid tint of it inside. The frame of an editor, a card, a readout. */
export const Panel: React.FC<Box & { color?: string; fill?: number; stroke?: number; radius?: number; style?: React.CSSProperties; children?: React.ReactNode }> = ({
  x,
  y,
  w,
  h,
  color = P.greyB,
  fill = 0.1,
  stroke = STROKE.thin,
  radius = RADIUS.panel,
  style,
  children,
}) => {
  const stage = useStage();
  return (
    <div
      style={{
        position: "absolute",
        left: x,
        top: y,
        width: w,
        height: h,
        boxSizing: "border-box",
        borderRadius: radius,
        outline: `${stroke}px solid ${color}`,
        outlineOffset: -stroke,
        backgroundColor: tint(color, fill, stage),
        ...style,
      }}
    >
      {children}
    </div>
  );
};

/** One line of text. `size` is a TYPE token. Lines are never wrapped: a label is 1-3 words. */
export const Txt: React.FC<{
  children: React.ReactNode;
  size?: number;
  color?: string;
  family?: keyof typeof FONT;
  weight?: 400 | 700;
  italic?: boolean;
  style?: React.CSSProperties;
}> = ({ children, size = TYPE.body, color = P.white, family = "serif", weight = 400, italic = false, style }) => (
  <span
    style={{
      fontFamily: FONT[family],
      fontSize: size,
      fontWeight: weight,
      fontStyle: italic ? "italic" : undefined,
      color,
      lineHeight: 1.15,
      whiteSpace: "pre",
      ...style,
    }}
  >
    {children}
  </span>
);

/** A formatted number: thousands separators, a true minus sign, digits that never jitter. */
export const formatNumber = (value: number, decimals = 0): string =>
  value
    .toLocaleString("en-US", { minimumFractionDigits: decimals, maximumFractionDigits: decimals })
    .replace("-", "−");

export const Num: React.FC<{ value: number; decimals?: number; size?: number; color?: string; prefix?: string; suffix?: string; style?: React.CSSProperties }> = ({
  value,
  decimals = 0,
  size = TYPE.heading,
  color = P.white,
  prefix = "",
  suffix = "",
  style,
}) => (
  <Txt size={size} color={color} style={{ fontVariantNumeric: "tabular-nums lining-nums", ...style }}>
    {prefix + formatNumber(value, decimals) + suffix}
  </Txt>
);

/** A track with a fill. */
export const ProgressBar: React.FC<{ value: number; w: number; h?: number; color?: string; style?: React.CSSProperties }> = ({
  value,
  w,
  h = 20,
  color = P.blue,
  style,
}) => (
  <div style={{ width: w, height: h, borderRadius: h / 2, backgroundColor: P.greyD, overflow: "hidden", ...style }}>
    <div style={{ width: Math.max(h, w * clamp01(value)), height: h, borderRadius: h / 2, backgroundColor: color, opacity: value > 0 ? 1 : 0 }} />
  </div>
);

/** A solid pill with dark text: a name tag for the thing it sits beside. Title Case, 1-3 words. */
export const Chip: React.FC<{ children: React.ReactNode; color?: string; size?: number; style?: React.CSSProperties }> = ({
  children,
  color = P.yellow,
  size = TYPE.small,
  style,
}) => (
  <span
    style={{
      display: "inline-block",
      fontFamily: FONT.serif,
      fontSize: size,
      lineHeight: 1,
      color: P.black,
      backgroundColor: color,
      borderRadius: RADIUS.chip,
      padding: `${size * 0.3}px ${size * 0.62}px ${size * 0.34}px`,
      whiteSpace: "pre",
      ...style,
    }}
  >
    {children}
  </span>
);

/** A word in a thin coloured box with a tint of the same hue: a token, a tag, an option. */
export const Token: React.FC<{ children: React.ReactNode; color?: string; size?: number; family?: keyof typeof FONT; style?: React.CSSProperties }> = ({
  children,
  color = P.blue,
  size = TYPE.small,
  family = "serif",
  style,
}) => {
  const stage = useStage();
  return (
    <span
      style={{
        display: "inline-block",
        fontFamily: FONT[family],
        fontSize: size,
        lineHeight: 1.1,
        color: P.white,
        backgroundColor: tint(color, 0.22, stage),
        outline: `${STROKE.thin}px solid ${color}`,
        outlineOffset: -STROKE.thin,
        borderRadius: 8,
        padding: `${size * 0.22}px ${size * 0.44}px ${size * 0.28}px`,
        whiteSpace: "pre",
        ...style,
      }}
    >
      {children}
    </span>
  );
};

/** The house arrow, drawn in SVG: it grows from its tail as `progress` goes 0..1. */
export const Arrow: React.FC<{ from: [number, number]; to: [number, number]; progress?: number; color?: string; width?: number; head?: number }> = ({
  from,
  to,
  progress = 1,
  color = P.greyA,
  width = STROKE.arrow,
  head = 40,
}) => {
  const p = clamp01(progress);
  if (p <= 0) return null;
  const [x1, y1] = from;
  const dx = to[0] - x1;
  const dy = to[1] - y1;
  const len = Math.hypot(dx, dy) || 1;
  const ux = dx / len;
  const uy = dy / len;
  const reach = len * p;
  const hl = Math.min(head, reach);
  const tipX = x1 + ux * reach;
  const tipY = y1 + uy * reach;
  const baseX = tipX - ux * hl;
  const baseY = tipY - uy * hl;
  const half = hl * 0.48;
  const points = `${tipX},${tipY} ${baseX - uy * half},${baseY + ux * half} ${baseX + uy * half},${baseY - ux * half}`;
  return (
    <svg style={{ position: "absolute", left: 0, top: 0, overflow: "visible" }} width={1} height={1}>
      <line x1={x1} y1={y1} x2={baseX + ux * 2} y2={baseY + uy * 2} stroke={color} strokeWidth={width} />
      <polygon points={points} fill={color} />
    </svg>
  );
};

/** The rectangle that says "look here": its outline draws on as `progress` goes 0..1. */
export const HighlightBox: React.FC<Box & { progress?: number; color?: string; fill?: number; radius?: number }> = ({
  x,
  y,
  w,
  h,
  progress = 1,
  color = P.yellow,
  fill = 0,
  radius = 8,
}) => {
  const stage = useStage();
  const p = clamp01(progress);
  if (p <= 0) return null;
  return (
    <svg style={{ position: "absolute", left: 0, top: 0, overflow: "visible" }} width={1} height={1}>
      <rect
        x={x}
        y={y}
        width={w}
        height={h}
        rx={radius}
        fill={fill ? tint(color, fill * p, stage) : "none"}
        stroke={color}
        strokeWidth={STROKE.thin}
        pathLength={1}
        strokeDasharray={1}
        strokeDashoffset={1 - p}
      />
    </svg>
  );
};

/** A product window: a rounded frame, a top bar and three dots. For UI beats; keep what is inside it sparse. */
export const Window: React.FC<Box & { color?: string; title?: string; children?: React.ReactNode }> = ({ x, y, w, h, color = P.greyB, title, children }) => {
  const stage = useStage();
  const bar = 56;
  return (
    <div
      style={{
        position: "absolute",
        left: x,
        top: y,
        width: w,
        height: h,
        boxSizing: "border-box",
        borderRadius: RADIUS.panel,
        outline: `${STROKE.shape}px solid ${color}`,
        outlineOffset: -STROKE.shape,
        backgroundColor: tint(color, 0.1, stage),
        overflow: "hidden",
      }}
    >
      <div style={{ height: bar, display: "flex", alignItems: "center", gap: 12, paddingLeft: 26, boxShadow: `inset 0 -${STROKE.thin}px 0 ${color}` }}>
        {[0, 1, 2].map((i) => (
          <div key={i} style={{ width: 12, height: 12, borderRadius: 6, backgroundColor: color }} />
        ))}
        {title ? <Txt size={TYPE.tiny} color={P.greyB} family="sans" style={{ marginLeft: 18 }}>{title}</Txt> : null}
      </div>
      <div style={{ position: "absolute", left: 0, right: 0, top: bar, bottom: 0 }}>{children}</div>
    </div>
  );
};

/** A chat message. side="right" is the person asking (blue), side="left" the other party (grey). */
export const Bubble: React.FC<{ x: number; y: number; w: number; side?: "left" | "right"; color?: string; size?: number; children: React.ReactNode }> = ({
  x,
  y,
  w,
  side = "left",
  color,
  size = TYPE.small,
  children,
}) => {
  const stage = useStage();
  const c = color ?? (side === "right" ? P.blue : P.greyB);
  return (
    <div
      style={{
        position: "absolute",
        left: x,
        top: y,
        width: w,
        boxSizing: "border-box",
        padding: `${size * 0.5}px ${size * 0.7}px`,
        borderRadius: side === "right" ? "26px 26px 6px 26px" : "26px 26px 26px 6px",
        outline: `${STROKE.thin}px solid ${c}`,
        outlineOffset: -STROKE.thin,
        backgroundColor: tint(c, 0.16, stage),
        fontFamily: FONT.serif,
        fontSize: size,
        lineHeight: 1.3,
        color: side === "right" ? P.blueLight : P.white,
      }}
    >
      {children}
    </div>
  );
};
