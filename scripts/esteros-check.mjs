import { access, readFile } from "node:fs/promises";
import { resolve } from "node:path";

const root = resolve(import.meta.dirname, "..");
const concepts = ["costa-108", "mesa-surquillo", "pacifico-34"];
const forbidden = [/lorem ipsum/i, /placeholder/i, /stock photo/i, /fake/i];

for (const concept of concepts) {
  const file = resolve(root, "esteros", concept, "index.html");
  const html = await readFile(file, "utf8");
  if (!/^<!doctype html>/i.test(html.trim())) throw new Error(`${concept}: missing doctype`);
  if (!/<meta name="viewport"/i.test(html)) throw new Error(`${concept}: missing viewport`);
  for (const pattern of forbidden) if (pattern.test(html)) throw new Error(`${concept}: forbidden copy ${pattern}`);
  const ids = new Set([...html.matchAll(/id="([^"]+)"/g)].map((match) => match[1]));
  for (const match of html.matchAll(/href="#([^"]+)"/g)) if (!ids.has(match[1])) throw new Error(`${concept}: broken anchor ${match[1]}`);
  const sources = [...html.matchAll(/src="([^"]+\.jpg)"/g)].map((match) => match[1].replaceAll("%20", " "));
  for (const source of sources) await access(resolve(root, "esteros", concept, source));
  console.log(`PASS ${concept}: page, anchors, copy, and ${sources.length} real photos checked`);
}

