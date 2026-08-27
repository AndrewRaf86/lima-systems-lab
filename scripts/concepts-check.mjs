import { access, readFile } from "node:fs/promises";
import { resolve } from "node:path";

const root = resolve(import.meta.dirname, "..");
const pages = [
  ["concepts", "index.html"],
  ["concepts/mar-abierto", "index.html"],
  ["concepts/mar-abierto", "carta.html"],
  ["concepts/mar-abierto", "visita.html"],
  ["concepts/mesa-surquillo", "index.html"],
  ["concepts/mesa-surquillo", "carta.html"],
  ["concepts/mesa-surquillo", "visita.html"],
  ["concepts/sabor-pacifico", "index.html"],
  ["concepts/sabor-pacifico", "carta.html"],
  ["concepts/sabor-pacifico", "visita.html"],
];
const forbidden = [/lorem ipsum/i, /placeholder/i, /experience gastronomica inolvidable/i];

for (const [folder, page] of pages) {
  const file = resolve(root, folder, page);
  const html = await readFile(file, "utf8");
  if (!/^<!doctype html>/i.test(html.trim())) throw new Error(`${folder}/${page}: missing doctype`);
  if (!/<meta name="viewport"/i.test(html)) throw new Error(`${folder}/${page}: missing viewport`);
  if (!/<meta name="robots" content="noindex, nofollow"/i.test(html)) throw new Error(`${folder}/${page}: private review page must be noindex`);
  for (const pattern of forbidden) if (pattern.test(html)) throw new Error(`${folder}/${page}: forbidden copy ${pattern}`);
  const ids = new Set([...html.matchAll(/id="([^"]+)"/g)].map((match) => match[1]));
  for (const match of html.matchAll(/href="#([^"]+)"/g)) if (!ids.has(match[1])) throw new Error(`${folder}/${page}: broken anchor ${match[1]}`);
  const sources = [...html.matchAll(/src="([^"]+\.jpg)"/g)].map((match) => match[1].replaceAll("%20", " "));
  for (const source of sources) await access(resolve(root, folder, source));
  console.log(`PASS ${folder}/${page}: semantic shell, noindex, anchors, and ${sources.length} real photos checked`);
}

