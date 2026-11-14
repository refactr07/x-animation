// Easing and progress helpers. Everything works in seconds, like beats.json: no magic frame numbers.

export type Ease = (x: number) => number;

export const clamp01 = (x: number): number => Math.min(1, Math.max(0, x));

export const lerp = (a: number, b: number, p: number): number => a + (b - a) * p;

/** Smootherstep, 6t^5 - 15t^4 + 10t^3: the house curve, identical to xkit.motion.smooth. */
export const smooth: Ease = (t) => {
  const x = clamp01(t);
  return x * x * x * (10 - 15 * x + 6 * x * x);
};

/** Arrivals that should settle quickly: fast start, soft landing. */
export const easeOut: Ease = (t) => 1 - Math.pow(1 - clamp01(t), 5);

/** Departures: slow start, fast finish. */
export const easeIn: Ease = (t) => Math.pow(clamp01(t), 3);

export const linear: Ease = (t) => clamp01(t);

/** Eased 0..1 progress of a move that starts at `start` seconds and lasts `dur` seconds. */
export const ramp = (t: number, start: number, dur: number, ease: Ease = smooth): number =>
  dur <= 0 ? (t >= start ? 1 : 0) : ease((t - start) / dur);

/** 1 while t is between start and end, eased up over fadeIn and down over fadeOut (which ends at `end`). */
export const hold = (t: number, start: number, end: number, fadeIn = 0.3, fadeOut = 0.25): number =>
  Math.min(ramp(t, start, fadeIn, easeOut), 1 - ramp(t, end - fadeOut, fadeOut, easeIn));

/** Start time of item i in a run of like things that arrive one after another. */
export const staggered = (start: number, i: number, lag: number): number => start + i * lag;

/** A value that follows keyframes [[time, value], ...] with one ease between each pair. */
export const track = (t: number, keys: ReadonlyArray<readonly [number, number]>, ease: Ease = smooth): number => {
  if (t <= keys[0][0]) return keys[0][1];
  for (let i = 1; i < keys.length; i++) {
    const [t1, v1] = keys[i];
    if (t <= t1) {
      const [t0, v0] = keys[i - 1];
      return lerp(v0, v1, ease((t - t0) / Math.max(t1 - t0, 1e-9)));
    }
  }
  return keys[keys.length - 1][1];
};
