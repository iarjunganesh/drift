// Rasterize the DRIFT banner SVGs to high-DPI PNG using the frontend's sharp
// install. Run from assets/brand/:  node build_banner_raster.mjs
// The API serves the SVGs; the PNGs are convenience exports for decks/video.
import { readFileSync, writeFileSync } from "node:fs";
import { createRequire } from "node:module";

const require = createRequire("file://" + process.cwd() + "/../../frontend/");
const sharp = require("sharp");

const SCALE = 2; // 1600x520 -> 3200x1040
const jobs = [
  ["drift-banner-dark.svg", "drift-banner-dark.png"],
  ["drift-banner-light.svg", "drift-banner-light.png"],
];

for (const [src, out] of jobs) {
  const svg = readFileSync(src);
  const png = await sharp(svg, { density: 72 * SCALE }).png().toBuffer();
  writeFileSync(out, png);
  console.log(`wrote ${out}`);
}
