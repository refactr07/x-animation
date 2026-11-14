import React from "react";
import { AbsoluteFill, Img, staticFile } from "remotion";
import { BACKDROP_VERSION, BACKDROPS, type BackdropId, FONT, LAYOUT, P } from "../theme";

const StageContext = React.createContext<string>(P.bg);

/** The colour of the stage a component is drawn on. Tints mix over it: tint(P.blue, 0.18, useStage()). */
export const useStage = (): string => React.useContext(StageContext);

/**
 * The stage: the section's backdrop, painted from the same PNG Manim uses as its camera background
 * (public/backdrops, drawn by tools/backdrops.py). `outputWidth` is the width of the file being
 * rendered (960, 1920 or 3840), so the image maps onto the output pixel for pixel.
 */
export const Stage: React.FC<{ backdrop: string; outputWidth?: number; children?: React.ReactNode }> = ({
  backdrop,
  outputWidth = LAYOUT.width,
  children,
}) => {
  const spec = BACKDROPS[backdrop as BackdropId];
  if (!spec) throw new Error(`backdrop "${backdrop}" is not in theme/backdrops.json`);
  const h = Math.round((outputWidth * LAYOUT.height) / LAYOUT.width);
  const file = `backdrops/${backdrop}_${outputWidth}x${h}_v${BACKDROP_VERSION}.png`;
  return (
    <StageContext.Provider value={spec.bg}>
      <AbsoluteFill style={{ backgroundColor: spec.bg, color: P.white, fontFamily: FONT.serif }}>
        {spec.pattern ? (
          <Img src={staticFile(file)} style={{ position: "absolute", left: 0, top: 0, width: LAYOUT.width, height: LAYOUT.height }} />
        ) : null}
        {children}
      </AbsoluteFill>
    </StageContext.Provider>
  );
};
