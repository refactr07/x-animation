// The Blackboard style for Remotion, read from theme/tokens.json: the same file the Manim kit reads.
// Never write a colour, a font or a duration into a component: import it from here.
import backdrops from "../../theme/backdrops.json";
import tokens from "../../theme/tokens.json";

const c = tokens.color;

/** The palette. Colour is meaning: a role keeps its colour for the whole video. */
export const P = {
  bg: c.bg,
  white: c.text,
  black: "#000000",
  greyA: c.grey.a, // arrows, light strokes
  greyB: c.grey.b, // outlines of neutral things
  greyC: c.grey.c, // secondary labels, inactive words
  greyD: c.grey.d, // guides, empty slots
  greyE: c.grey.e, // faint fills
  blue: c.blue,
  blueLight: c.blue_light, // blue words
  blueDeep: c.blue_deep,
  teal: c.teal,
  tealDeep: c.teal_deep,
  green: c.green,
  yellow: c.yellow,
  gold: c.gold,
  orange: c.orange,
  red: c.red,
  pink: c.pink,
  purple: c.purple,
} as const;

export const RAMP: readonly string[] = c.ramp;

/** Em sizes in px on the 1920x1080 canvas. Nothing is ever smaller than TYPE.min. */
export const TYPE = tokens.type;
/** Stroke widths in px on the 1920x1080 canvas. */
export const STROKE = tokens.stroke;
export const RADIUS = tokens.radius;
export const FONT = { serif: tokens.font.serif, mono: tokens.font.mono, sans: tokens.font.sans } as const;
export const FONT_FILES = tokens.font.files;
/** Durations in seconds. */
export const MOTION = tokens.motion;
export const LAYOUT = tokens.layout;
/** Frames per second when neither the section nor its video sets one. */
export const DEFAULT_FPS: number = tokens.render.fps;
/** Pixels per Manim unit: a point (x, y) in a Manim scene is at px(x, y) here. */
export const UNIT = LAYOUT.unit_px;

/** Manim coordinates (origin at the centre, y up) to canvas pixels (origin top left, y down). */
export const px = (x: number, y: number): { x: number; y: number } => ({
  x: LAYOUT.width / 2 + x * UNIT,
  y: LAYOUT.height / 2 - y * UNIT,
});

const channel = (hex: string, i: number) => parseInt(hex.replace("#", "").slice(i * 2, i * 2 + 2), 16);
const hex2 = (v: number) => Math.max(0, Math.min(255, Math.round(v))).toString(16).padStart(2, "0").toUpperCase();

/** `top` laid over `base` at `amount` (0..1) in sRGB. The Manim kit mixes the same way (xcore.tokens.mix). */
export const mix = (base: string, top: string, amount: number): string =>
  "#" + [0, 1, 2].map((i) => hex2(channel(base, i) + (channel(top, i) - channel(base, i)) * amount)).join("");

/** A colour with an alpha, for the few places that need one (never for fills that sit over lines). */
export const alpha = (hex: string, a: number): string =>
  `rgba(${channel(hex, 0)}, ${channel(hex, 1)}, ${channel(hex, 2)}, ${a})`;

export type Pattern =
  | { kind: "grid"; color: string; width_px: number; spacing_px: number }
  | { kind: "dots"; color: string; radius_px: number; spacing_px: number };

export type BackdropSpec = { name: string; bg: string; pattern: Pattern | null; mood: string; use_for: string };
export type BackdropId = keyof typeof backdrops.styles;
export const BACKDROPS = backdrops.styles as unknown as Record<BackdropId, BackdropSpec>;
/** Bump together with xcore/backdrop.py VERSION. */
export const BACKDROP_VERSION = 1;

/** The fill of every shape that carries a colour role: a SOLID tint of the hue over the stage. */
export const tint = (color: string, amount: number = tokens.tint.fill, stage: string = P.bg): string =>
  mix(stage, color, amount);

/** Colour for a value in 0..1: pale yellow (low) through green to teal (high). */
export const rampColor = (p: number): string => {
  const x = Math.min(Math.max(p, 0), 1) * (RAMP.length - 1);
  const i = Math.min(Math.floor(x), RAMP.length - 2);
  return mix(RAMP[i], RAMP[i + 1], x - i);
};
