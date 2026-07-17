// Rasterize the architecture presentation SVGs to high-DPI PNG using the frontend's
// sharp install. Run from assets/architecture/:  node build_arch_raster.mjs
import { readFileSync, writeFileSync } from "node:fs";
import { createRequire } from "node:module";

const require = createRequire("file://" + process.cwd() + "/../../frontend/");
const sharp = require("sharp");

const SCALE = 2; // 1712x940 -> 3424x1880
const jobs = [
  ["arch-dark.svg", "arch-dark.png"],
  ["arch-light.svg", "arch-light.png"],
];

for (const [src, out] of jobs) {
  const svg = readFileSync(src);
  const png = await sharp(svg, { density: 72 * SCALE })
    .png()
    .toBuffer();
  writeFileSync(out, png);
  console.log(`wrote ${out}`);
}
