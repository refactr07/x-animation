// How a section's Remotion segments become compositions.
//
// tools/registry.py scans videos/*/*/beats.json and writes src/sections.generated.tsx, which lists
// every section with its beats and its components. For each Remotion segment that file registers one
// composition, "<video>-<section>-<Component>", whose length and frame rate come from beats.json.
// tools/render.py renders those compositions; `npm run studio` shows them for scrubbing.
import React from "react";
import { type CalculateMetadataFunction } from "remotion";
import { Stage } from "./components/Stage";
import { type BeatsJson, Section, TimelineProvider } from "./cues";
import { DEFAULT_FPS, LAYOUT } from "./theme";

export type SectionEntry = {
  /** "<video>/<section>" */
  key: string;
  beats: BeatsJson;
  /** frames per second of the video this section belongs to (video.json), if it sets one */
  fps?: number;
  components: Record<string, React.FC>;
};

export type SegmentProps = {
  /** Frame rate to render at. Drafts pass 30; otherwise the video's own rate is used. */
  fps?: number;
  /** Width in px of the file being rendered (960, 1920, 3840): picks the matching backdrop PNG. */
  outputWidth?: number;
};

const sections = new Map<string, Section>();
const sectionOf = (entry: SectionEntry): Section => {
  let s = sections.get(entry.key);
  if (!s) {
    s = new Section(entry.beats);
    sections.set(entry.key, s);
  }
  return s;
};

export const fpsOf = (entry: SectionEntry, props?: SegmentProps): number =>
  props?.fps ?? entry.beats.fps ?? entry.fps ?? DEFAULT_FPS;

export const compositionId = (entry: SectionEntry, component: string): string =>
  `${entry.key.replace(/[^A-Za-z0-9]+/g, "-")}-${component}`;

/** Length and frame rate of a segment's composition, from beats.json and the render's props. */
export const segmentMetadata =
  (entry: SectionEntry, component: string): CalculateMetadataFunction<SegmentProps> =>
  ({ props }) => {
    const section = sectionOf(entry);
    const fps = fpsOf(entry, props);
    return {
      fps,
      durationInFrames: Math.max(1, section.segmentFrames(section.segment(component), fps)),
      width: LAYOUT.width,
      height: LAYOUT.height,
    };
  };

/** A segment on its stage, with its clock. This is what a segment composition renders. */
export const makeSegment = (entry: SectionEntry, component: string): React.FC<SegmentProps> => {
  const Inner = entry.components[component];
  if (!Inner) throw new Error(`${entry.key}: beats.json names the component "${component}" but the section does not export it`);
  const Host: React.FC<SegmentProps> = ({ outputWidth }) => {
    const section = sectionOf(entry);
    return (
      <Stage backdrop={section.backdrop} outputWidth={outputWidth}>
        <TimelineProvider section={section} segment={section.segment(component)}>
          <Inner />
        </TimelineProvider>
      </Stage>
    );
  };
  Host.displayName = `Segment(${component})`;
  return Host;
};

export const remotionSegments = (entry: SectionEntry): string[] =>
  entry.beats.segments.filter((s) => s.engine === "remotion" && s.component).map((s) => s.component as string);
