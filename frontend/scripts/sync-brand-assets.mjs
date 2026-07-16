import { copyFile, mkdir } from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";

const scriptDirectory = path.dirname(fileURLToPath(import.meta.url));
const frontendDirectory = path.resolve(scriptDirectory, "..");
const source = path.resolve(frontendDirectory, "..", "assets", "brand", "drift-banner-dark.svg");
const destinationDirectory = path.join(frontendDirectory, "public", "brand");
const destination = path.join(destinationDirectory, "drift-banner-dark.svg");

await mkdir(destinationDirectory, { recursive: true });
await copyFile(source, destination);
console.log("Synced canonical DRIFT brand asset for the frontend build.");
