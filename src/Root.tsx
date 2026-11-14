// One composition per Remotion segment of every section, named "<video>-<section>-<Component>".
// The list of sections is generated: run ./x sync after adding a section or a component.
import { compositionId, loadKitFonts, makeSegment, remotionSegments, segmentMetadata } from "@kit";
import React from "react";
import { Composition, Folder } from "remotion";
import { SECTIONS } from "./sections.generated";

loadKitFonts();

export const RemotionRoot: React.FC = () => (
  <>
    {SECTIONS.map((entry) => (
      <Folder key={entry.key} name={entry.key.replace(/[^A-Za-z0-9]+/g, "-")}>
        {remotionSegments(entry).map((component) => (
          <Composition
            key={component}
            id={compositionId(entry, component)}
            component={makeSegment(entry, component)}
            calculateMetadata={segmentMetadata(entry, component)}
            defaultProps={{}}
          />
        ))}
      </Folder>
    ))}
  </>
);
