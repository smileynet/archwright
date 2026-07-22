#!/usr/bin/env node
// capture.mjs — deterministic per-section screenshots of a report page (ticket 044).
//
// Usage: node tools/report/capture.mjs <report.html> [-o <outdir>]
//
// Regions: named selectors (header h1, .verdict, #response-bar when visible) plus
// h2-delimited sections named by slugified heading. Crops are pre-resized to the
// analysis budget (long edge <= 1568 px, floor >= 200 px) by re-rendering at a
// scaled deviceScaleFactor — never post-processed. Two runs: light + dark.
//
// Output: <outdir>/<scheme>/<region>.png + fullpage.png + manifest.json
// Exit: 0 = captured, 2 = error (incl. playwright missing — callers decide SKIP).

import { fileURLToPath } from "node:url";
import { mkdirSync, writeFileSync, readFileSync } from "node:fs";
import { resolve, dirname, join } from "node:path";

const MAX_EDGE = 1568;
const MIN_EDGE = 200;

function pngSize(file) {
  const b = readFileSync(file);
  return { w: b.readUInt32BE(16), h: b.readUInt32BE(20) };
}

function slug(s) {
  return s.toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/^-|-$/g, "").slice(0, 40);
}

async function main() {
  const args = process.argv.slice(2);
  const htmlArg = args.find((a) => !a.startsWith("-"));
  if (!htmlArg) {
    console.error("Usage: capture.mjs <report.html> [-o <outdir>]");
    process.exit(2);
  }
  const oIdx = args.indexOf("-o");
  const outdir = resolve(oIdx >= 0 ? args[oIdx + 1] : join(dirname(resolve(htmlArg)), "visual"));

  let chromium;
  try {
    ({ chromium } = await import("playwright"));
  } catch {
    console.error("ERROR: playwright not installed (npm install; node_modules/.bin/playwright install chromium)");
    process.exit(2);
  }

  const url = "file://" + resolve(htmlArg);
  const browser = await chromium.launch();
  const manifest = { source: resolve(htmlArg), captured_at: new Date().toISOString(), schemes: {} };

  try {
    for (const colorScheme of ["light", "dark"]) {
      const dir = join(outdir, colorScheme);
      mkdirSync(dir, { recursive: true });
      const entries = [];

      // Pass 1 at dsf 1: discover regions and their boxes.
      const boxes = await withPage(browser, url, colorScheme, 1, (page) => regionBoxes(page));

      for (const region of boxes) {
        const longEdge = Math.max(region.box.width, region.box.height);
        let dsf = 1;
        if (longEdge > MAX_EDGE) dsf = MAX_EDGE / longEdge;
        const file = join(dir, `${region.name}.png`);
        await withPage(browser, url, colorScheme, dsf, async (page) => {
          const fresh = (await regionBoxes(page)).find((r) => r.name === region.name);
          if (!fresh) throw new Error(`region ${region.name} vanished at dsf ${dsf}`);
          // Floor rule: a crop under MIN_EDGE on either axis gets PADDED with
          // surrounding page context (never upscaled — extreme-aspect strips are
          // the documented hallucination-risk shape).
          const clip = padToFloor(fresh.box, await pageBounds(page));
          await page.screenshot({ path: file, clip, animations: "disabled" });
        });
        const size = pngSize(file);
        entries.push({ region: region.name, file, ...size, dsf: Number(dsf.toFixed(3)) });
      }

      const fullFile = join(dir, "fullpage.png");
      await withPage(browser, url, colorScheme, 1, (page) =>
        page.screenshot({ path: fullFile, fullPage: true, animations: "disabled" })
      );
      entries.push({ region: "fullpage", file: fullFile, ...pngSize(fullFile), dsf: 1, overview_only: true });
      manifest.schemes[colorScheme] = entries;
    }
  } finally {
    await browser.close();
  }

  const manifestFile = join(outdir, "manifest.json");
  writeFileSync(manifestFile, JSON.stringify(manifest, null, 2));
  console.log(`captured ${Object.values(manifest.schemes).flat().length} images -> ${outdir}`);
  console.log(manifestFile);
}

function padToFloor(box, bounds) {
  const clip = { ...box };
  for (const [axis, size, limit] of [["x", "width", bounds.width], ["y", "height", bounds.height]]) {
    if (clip[size] < MIN_EDGE) {
      const target = Math.min(MIN_EDGE, limit);
      // Center the padded window, then shift it back inside the page bounds.
      clip[axis] = Math.max(0, Math.min(clip[axis] - (target - clip[size]) / 2, limit - target));
      clip[size] = target;
    }
  }
  return clip;
}

function pageBounds(page) {
  return page.evaluate(() => ({
    width: document.documentElement.clientWidth,
    height: document.documentElement.scrollHeight,
  }));
}

async function withPage(browser, url, colorScheme, deviceScaleFactor, fn) {
  const ctx = await browser.newContext({
    viewport: { width: 1280, height: 900 },
    deviceScaleFactor,
    colorScheme,
    reducedMotion: "reduce",
  });
  const page = await ctx.newPage();
  try {
    await page.goto(url, { waitUntil: "load" });
    await page.evaluate(() => document.fonts.ready);
    // Clip screenshots clamp to the viewport surface — grow the viewport to the
    // document height (capped) so document-space clips capture fully.
    const docH = await page.evaluate(() => document.documentElement.scrollHeight);
    if (docH > 900) await page.setViewportSize({ width: 1280, height: Math.min(docH, 6000) });
    await page.mouse.move(0, 0);
    return await fn(page);
  } finally {
    await ctx.close();
  }
}

// Region discovery: named selectors + h2-delimited spans (heading to next heading).
async function regionBoxes(page) {
  return page.evaluate(() => {
    const out = [];
    const push = (name, rect) => {
      if (rect && rect.width > 4 && rect.height > 4)
        out.push({ name, box: { x: Math.max(0, rect.x), y: Math.max(0, rect.y),
                                width: Math.ceil(rect.width), height: Math.ceil(rect.height) } });
    };
    const abs = (el) => {
      const r = el.getBoundingClientRect();
      return { x: r.x + scrollX, y: r.y + scrollY, width: r.width, height: r.height };
    };
    const h1 = document.querySelector("h1");
    if (h1) push("header", abs(h1));
    const verdict = document.querySelector(".verdict");
    if (verdict) push("verdict", abs(verdict));
    const bar = document.querySelector("#response-bar");
    if (bar && getComputedStyle(bar).display !== "none") push("response-bar", abs(bar));

    const h2s = [...document.querySelectorAll("h2")];
    const docEnd = document.documentElement.scrollHeight;
    h2s.forEach((h, i) => {
      const start = abs(h);
      const next = h2s[i + 1];
      const end = next ? abs(next).y : docEnd;
      const name = h.textContent.toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/^-|-$/g, "").slice(0, 40);
      push("section-" + name, { x: 0, y: start.y, width: document.documentElement.clientWidth,
                                height: end - start.y });
    });
    return out;
  });
}

main().catch((e) => {
  console.error("ERROR:", e.message);
  process.exit(2);
});
