import { cp, mkdir, rm } from "node:fs/promises";
import { resolve } from "node:path";

const root = resolve(import.meta.dirname, "..");
const out = resolve(root, "dist");
const entries = [
  "index.html",
  "favicon.svg",
  "site.webmanifest",
  "og.png",
  "robots.txt",
  "sitemap.xml",
  "en",
  "auditoria",
  "insights",
];

await rm(out, { recursive: true, force: true });
await mkdir(out, { recursive: true });
for (const entry of entries) {
  await cp(resolve(root, entry), resolve(out, entry), { recursive: true });
}
console.log(`Build complete: ${entries.length} public entries copied to dist/.`);
