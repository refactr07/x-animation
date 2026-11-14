// Render defaults for every composition. tools/render.py overrides them per quality with CLI flags.
import path from "node:path";
import { Config } from "@remotion/cli/config";

Config.setEntryPoint("./src/index.ts");
Config.setVideoImageFormat("png"); // lossless frames: JPEG rings around thin bright lines on black
Config.setCodec("h264");
Config.setPixelFormat("yuv420p");
Config.setColorSpace("bt709");
Config.setCrf(12); // segment clips are intermediates: tools/render.py makes the delivery encode
Config.setConcurrency(4); // 4K frames are large: four browser tabs is a safe ceiling on 16 GB
Config.setOverwriteOutput(true);

// `import { ... } from "@kit"` in any section resolves to kit/remotion (tsconfig.json has the same alias).
Config.overrideWebpackConfig((current) => ({
  ...current,
  resolve: {
    ...current.resolve,
    alias: { ...(current.resolve?.alias ?? {}), "@kit": path.join(process.cwd(), "kit", "remotion", "index.ts") },
  },
}));
