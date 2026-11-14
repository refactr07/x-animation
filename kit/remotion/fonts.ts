// Latin Modern (the OpenType Computer Modern) from public/fonts: the very files the Manim kit hands to
// Typst, so type is identical on both sides of an engine switch. loadFont() holds the render until
// each face is ready, so no frame is ever drawn in a fallback font.
import { loadFont } from "@remotion/fonts";
import { staticFile } from "remotion";
import { FONT, FONT_FILES } from "./theme";

type Faces = Record<string, string>;

const faces = (family: string, files: Faces) =>
  Object.entries(files).map(([key, file]) =>
    loadFont({
      family,
      url: staticFile(`fonts/${file}`),
      weight: key.replace("i", ""),
      style: key.endsWith("i") ? "italic" : "normal",
      display: "block",
    }),
  );

let loading: Promise<unknown> | null = null;

export const loadKitFonts = (): Promise<unknown> => {
  loading ??= Promise.all([
    ...faces(FONT.serif, FONT_FILES.serif),
    ...faces(FONT.mono, FONT_FILES.mono),
    ...faces(FONT.sans, FONT_FILES.sans),
  ]);
  return loading;
};
