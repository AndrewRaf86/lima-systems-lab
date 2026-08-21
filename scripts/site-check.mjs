import { readFile } from "node:fs/promises";
import { resolve } from "node:path";

const root = resolve(import.meta.dirname, "..");
const routes = new Map([
  ["/", "index.html"],
  ["/en/", "en/index.html"],
  ["/auditoria/", "auditoria/index.html"],
  ["/en/audit/", "en/audit/index.html"],
  ["/insights/ai-slop-founder-voice.html", "insights/ai-slop-founder-voice.html"],
]);
const forbidden = [
  /Lima Systems/i,
  /Private concept/i,
  /concept comparison/i,
  /design score/i,
  /compare all five/i,
  /lorem ipsum/i,
  /placeholder/i,
];

function assert(condition, message) {
  if (!condition) throw new Error(message);
}

async function read(relativePath) {
  return readFile(resolve(root, relativePath), "utf8");
}

async function lint() {
  const files = [...routes.values()];
  for (const file of files) {
    const html = await read(file);
    assert(/^<!doctype html>/i.test(html.trim()), `${file}: missing doctype`);
    assert(/<html\b[^>]*lang=/i.test(html), `${file}: missing document language`);
    assert(/<meta\b[^>]*name="viewport"/i.test(html), `${file}: missing viewport metadata`);
    assert(/<title>[^<]+<\/title>/i.test(html), `${file}: missing title`);
    if (file === "index.html") {
      assert(/<meta\b[^>]*name="robots"[^>]*index, follow/i.test(html), `${file}: homepage must allow indexing`);
      assert(!/<meta\b[^>]*name="robots"[^>]*noindex/i.test(html), `${file}: homepage still contains noindex`);
    } else {
      assert(/<meta\b[^>]*name="robots"[^>]*noindex/i.test(html), `${file}: legacy redirect must remain noindex`);
    }
    for (const pattern of forbidden) assert(!pattern.test(html), `${file}: forbidden text ${pattern}`);
  }

  const home = await read("index.html");
  const ids = new Set([...home.matchAll(/\bid="([^"]+)"/g)].map((match) => match[1]));
  for (const match of home.matchAll(/href="#([^"]+)"/g)) {
    assert(ids.has(match[1]), `index.html: broken anchor #${match[1]}`);
  }
  assert(!/<form\b/i.test(home), "index.html: form found without a verified delivery integration");
  assert(/mailto:rafanielloandrew@gmail\.com/i.test(home), "index.html: active email CTA missing");
  assert(/tel:\+13475206792/i.test(home), "index.html: active phone CTA missing");
  assert(/Illustrative demonstration \/ Not a case study/i.test(home), "index.html: demonstration label missing");
  assert(/prefers-reduced-motion/i.test(home), "index.html: reduced-motion support missing");
  assert(/<script type="application\/ld\+json">/i.test(home), "index.html: structured data missing");
  JSON.parse((await read("site.webmanifest")));
  console.log(`Lint passed: ${files.length} HTML files and site metadata checked.`);
}

async function checkRoutes() {
  for (const [route, file] of routes) {
    const html = await read(file);
    assert(html.length > 100, `${route}: route file is unexpectedly empty`);
    console.log(`PASS ${route} -> ${file}`);
  }
  const robots = await read("robots.txt");
  assert(/User-agent:\s*\*/i.test(robots) && /Allow:\s*\//i.test(robots), "robots.txt does not allow homepage crawling");
  assert(!/Disallow:\s*\//i.test(robots), "robots.txt still blocks the production site");
  const sitemap = await read("sitemap.xml");
  assert(/<loc>https:\/\/missionstack\.us\/<\/loc>/i.test(sitemap), "production homepage missing from sitemap");
  console.log("Route checks passed: legacy routes resolve and production indexing is enabled.");
}

const command = process.argv[2];
if (command === "lint") await lint();
else if (command === "routes") await checkRoutes();
else throw new Error("Use: node scripts/site-check.mjs <lint|routes>");
