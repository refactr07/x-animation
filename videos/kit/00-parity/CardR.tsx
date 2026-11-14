// The Remotion half of the engine parity card. scene.py draws the same card from the same card.json;
// `./x parity` measures the two against each other.
import { FONT, P, STROKE, tint, TYPE } from "@kit";
import React from "react";
import tokens from "../../../theme/tokens.json";
import card from "./card.json";

const hex = (name: string): string => {
  let node: unknown = tokens.color;
  for (const part of name.split(".")) node = (node as Record<string, unknown>)[part];
  return node as string;
};

const SIZES = TYPE as unknown as Record<string, number>;
const WIDTHS = STROKE as unknown as Record<string, number>;
const FAMILIES: Record<string, string> = FONT;

export const CardR: React.FC = () => (
  <>
    {card.colors.map((name, k) => (
      <React.Fragment key={name}>
        <div style={{ position: "absolute", left: card.patch.x0 + k * card.patch.dx, top: card.patch.y, width: card.patch.w, height: card.patch.h, backgroundColor: hex(name) }} />
        <div style={{ position: "absolute", left: card.tint.x0 + k * card.tint.dx, top: card.tint.y, width: card.tint.w, height: card.tint.h, backgroundColor: tint(hex(name), card.tint.amount, P.bg) }} />
      </React.Fragment>
    ))}
    <svg width={1920} height={1080} style={{ position: "absolute", left: 0, top: 0 }}>
      {card.text.map((item, k) => (
        <text key={k} x={item.x} y={item.y} fill={P.white} fontFamily={FAMILIES[item.family]} fontSize={SIZES[item.size]}>
          {item.text}
        </text>
      ))}
      {card.strokes.map((item) => (
        <line key={item.name} x1={item.x1} y1={item.y} x2={item.x2} y2={item.y} stroke={P.white} strokeWidth={WIDTHS[item.name]} />
      ))}
    </svg>
  </>
);
