import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import { resolve } from "node:path";
import test from "node:test";

const root = resolve(import.meta.dirname, "..");
const home = await readFile(resolve(root, "index.html"), "utf8");

test("homepage includes every required section", () => {
  for (const id of ["hero-title", "review", "services", "process", "proof", "faq", "contact"]) {
    assert.match(home, new RegExp(`id="${id}"`));
  }
});

test("homepage contains eight connected services and four process steps", () => {
  assert.equal((home.match(/class="service-card"/g) ?? []).length, 8);
  assert.equal((home.match(/<li><span>0[1-4]<\/span><h3>/g) ?? []).length, 4);
});

test("contact is honest and email-based", () => {
  assert.doesNotMatch(home, /<form\b/i);
  assert.match(home, /Email is the active contact method\./);
  assert.match(home, /No web form or scheduling system is connected\./);
  assert.ok((home.match(/mailto:rafanielloandrew@gmail\.com/g) ?? []).length >= 3);
});

test("private launch controls are present", async () => {
  assert.match(home, /noindex, nofollow, noarchive, nosnippet/);
  const robots = await readFile(resolve(root, "robots.txt"), "utf8");
  assert.match(robots, /Disallow: \//);
});

test("social and favicon assets are wired", () => {
  assert.match(home, /<meta property="og:image" content="https:\/\/missionstack\.us\/og\.png">/);
  assert.match(home, /<link rel="icon" href="\/favicon\.svg"/);
  assert.match(home, /<link rel="manifest" href="\/site\.webmanifest">/);
});
