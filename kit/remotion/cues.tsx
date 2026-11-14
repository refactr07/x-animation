// The timing model for Remotion: the same beats.json the Manim kit reads (kit/python/xcore/beats.py).
//
// A segment component never contains a number of seconds that places a beat. It asks the timeline:
//
//   const { t, cue, word } = useTimeline();
//   const lineIn = ramp(t, word("Code", "code"), 0.4);     // starts when "code" is spoken
//   if (t >= cue("Loop")) { ... }                          // from the Loop beat on
//
// `t` is seconds since the start of the SECTION, so cue times mean the same thing in every segment
// and in the Manim scenes. Retiming to a voiceover changes beats.json and nothing here.
import React, { createContext, useContext, useMemo } from "react";
import { useCurrentFrame, useVideoConfig } from "remotion";

export type WordJson = [string, number, number];
export type BeatJson = { name: string; text: string; start: number; end: number; words?: WordJson[]; picture?: string };
export type SegmentJson = { engine: "manim" | "remotion"; scene?: string; component?: string; from: string; to: string };
export type BeatsJson = {
  section: string;
  title?: string;
  file?: string;
  backdrop?: string;
  fps?: number;
  tail?: number;
  beats: BeatJson[];
  segments: SegmentJson[];
};

export const END = "END";

/** The frame a time falls on. Half frames round up: the same rule as xcore.beats.frame_of. */
export const frameOf = (seconds: number, fps: number): number => Math.floor(seconds * fps + 0.5 + 1e-9);

/** How words are compared: lower case, letters and digits only ("Don't," -> "dont"). */
export const norm = (w: string): string => w.toLowerCase().replace(/[^a-z0-9]/g, "");

export type SegmentInfo = { index: number; engine: string; name: string; start: number; end: number };

export class Section {
  readonly beats: BeatJson[];
  readonly duration: number;
  readonly backdrop: string;
  readonly segments: SegmentInfo[];

  constructor(readonly json: BeatsJson) {
    this.beats = json.beats;
    const last = this.beats[this.beats.length - 1];
    this.duration = Math.round(((last ? last.end : 0) + (json.tail ?? 0.8)) * 1e4) / 1e4;
    this.backdrop = json.backdrop ?? "dots";
    this.segments = json.segments.map((s, index) => ({
      index,
      engine: s.engine,
      name: s.scene ?? s.component ?? `segment${index}`,
      start: this.cue(s.from),
      end: this.cue(s.to),
    }));
  }

  beat(name: string): BeatJson {
    const b = this.beats.find((x) => x.name === name);
    if (!b) throw new Error(`no beat named "${name}"; beats are: ${this.beats.map((x) => x.name).join(", ")}`);
    return b;
  }

  /** Start of a beat in section seconds. END is the end of the section. */
  cue(name: string): number {
    return name === END ? this.duration : this.beat(name).start;
  }

  /** When the nth occurrence of `phrase` (one word or several) starts being spoken in a beat. */
  word(beat: string, phrase: string, nth = 1): number {
    const b = this.beat(beat);
    const want = phrase.split(/\s+/).map(norm).filter(Boolean);
    const have = (b.words ?? []).map((w) => norm(w[0]));
    let seen = 0;
    for (let i = 0; i + want.length <= have.length; i++) {
      if (want.every((w, k) => have[i + k] === w) && ++seen === nth) return (b.words as WordJson[])[i][1];
    }
    throw new Error(`beat ${beat}: "${phrase}" (occurrence ${nth}) is not in its narration: "${b.text}"`);
  }

  segment(name: string): SegmentInfo {
    const s = this.segments.find((x) => x.name === name);
    if (!s) throw new Error(`no segment named "${name}"`);
    return s;
  }

  /** Frames a segment owns. From frame indices on the section's grid, as in xcore: segments sum to the section. */
  segmentFrames(s: SegmentInfo, fps: number): number {
    return frameOf(s.end, fps) - frameOf(s.start, fps);
  }
}

type Ctx = { section: Section; segment: SegmentInfo };
const TimelineContext = createContext<Ctx | null>(null);

export const TimelineProvider: React.FC<{ section: Section; segment: SegmentInfo; children: React.ReactNode }> = ({
  section,
  segment,
  children,
}) => {
  const value = useMemo(() => ({ section, segment }), [section, segment]);
  return <TimelineContext.Provider value={value}>{children}</TimelineContext.Provider>;
};

export type Timeline = {
  /** Seconds since the start of the section. */
  t: number;
  fps: number;
  /** Start of a beat, snapped to the frame it lands on. */
  cue: (name: string) => number;
  /** When a word is spoken: word("Code", "four"). */
  word: (beat: string, phrase: string, nth?: number) => number;
  /** Where this segment starts and ends, in section seconds. */
  start: number;
  end: number;
  section: Section;
};

/** The clock of the segment a component is drawn in. Call it in the smallest component that animates. */
export const useTimeline = (): Timeline => {
  const ctx = useContext(TimelineContext);
  if (!ctx) throw new Error("useTimeline() needs a <TimelineProvider>: render the component through its segment composition");
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  return useMemo(() => {
    const { section, segment } = ctx;
    const first = frameOf(segment.start, fps);
    return {
      t: (frame + first) / fps,
      fps,
      cue: (name: string) => frameOf(section.cue(name), fps) / fps,
      word: (beat: string, phrase: string, nth = 1) => section.word(beat, phrase, nth),
      start: first / fps,
      end: frameOf(segment.end, fps) / fps,
      section,
    };
  }, [ctx, frame, fps]);
};
