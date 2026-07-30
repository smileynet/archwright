#!/usr/bin/env node
/**
 * tools/report/playwright-check.js — Reusable report visual verification harness.
 *
 * Usage:
 *   node tools/report/playwright-check.js [path-to-report.html] [--screenshots dir]
 *
 * Defaults:
 *   report path: first argument, or auto-detects from design/report/report.html in cwd
 *   screenshots: --screenshots <dir> (optional, saves PNGs)
 *
 * Exit: 0 = all pass, 1 = failures found
 * Output: structured pass/fail report to stdout
 *
 * Requires: playwright installed (npm install playwright in the project or globally)
 */

const { chromium } = require('playwright');
const path = require('path');
const fs = require('fs');

// === ARGS ===
const args = process.argv.slice(2);
let reportPath = null;
let screenshotDir = null;

for (let i = 0; i < args.length; i++) {
  if (args[i] === '--screenshots' && args[i + 1]) { screenshotDir = args[++i]; }
  else if (!args[i].startsWith('-')) { reportPath = args[i]; }
}

if (!reportPath) {
  // Auto-detect
  const candidates = ['design/report/report.html', '../design/report/report.html'];
  for (const c of candidates) { if (fs.existsSync(c)) { reportPath = c; break; } }
}
if (!reportPath || !fs.existsSync(reportPath)) {
  console.error('Usage: node playwright-check.js <report.html> [--screenshots dir]');
  console.error('  No report file found at: ' + (reportPath || '(none)'));
  process.exit(2);
}

reportPath = path.resolve(reportPath);
if (screenshotDir) fs.mkdirSync(screenshotDir, { recursive: true });

// === MAIN ===
(async () => {
  const browser = await chromium.launch();
  let pass = 0, fail = 0;
  const findings = [];

  function check(category, name, condition, detail) {
    if (condition) { pass++; findings.push({ status: 'pass', category, name }); }
    else { fail++; findings.push({ status: 'FAIL', category, name, detail }); }
  }

  // === Light mode ===
  const page = await browser.newPage({ viewport: { width: 1280, height: 900 } });
  await page.goto(`file:///${reportPath}`, { waitUntil: 'networkidle' });
  await page.waitForTimeout(3000);

  // Structure
  const structure = await page.evaluate(() => {
    return {
      hasHeader: !!document.querySelector('header h1'),
      hasVerdict: !!document.querySelector('.verdict'),
      hasDiagram: !!document.querySelector('#diagram-top') || !!document.querySelector('#diagram'),
      hasSvgOrMermaid: !!document.querySelector('svg') || !!document.querySelector('.mermaid'),
      posture: document.body.dataset.posture || null,
      cardCount: document.querySelectorAll('.card').length,
      h2Count: document.querySelectorAll('h2').length,
    };
  });
  check('structure', 'Header present', structure.hasHeader);
  check('structure', 'Verdict line present', structure.hasVerdict);
  check('structure', 'Diagram section present', structure.hasDiagram);
  check('structure', 'SVG or Mermaid diagram rendered', structure.hasSvgOrMermaid);
  check('structure', 'Posture attribute set', !!structure.posture, 'body[data-posture] missing');
  check('structure', 'Section headers present', structure.h2Count >= 1);

  // Visual hierarchy
  const visual = await page.evaluate(() => {
    const verdict = document.querySelector('.verdict');
    const card = document.querySelector('.card');
    return {
      verdictSize: verdict ? getComputedStyle(verdict).fontSize : null,
      cardShadow: card ? getComputedStyle(card).boxShadow : null,
    };
  });
  check('visual', 'Verdict font size >= 20px', visual.verdictSize && parseInt(visual.verdictSize) >= 20, visual.verdictSize);
  check('visual', 'Cards have box-shadow', visual.cardShadow && visual.cardShadow !== 'none');

  // Responsiveness
  await page.setViewportSize({ width: 375, height: 812 });
  await page.waitForTimeout(300);
  const mobile = await page.evaluate(() => ({
    overflow: document.body.scrollWidth > document.body.clientWidth
  }));
  check('responsive', 'No horizontal overflow at 375px', !mobile.overflow);
  await page.setViewportSize({ width: 1280, height: 900 });

  // Dark mode
  await page.emulateMedia({ colorScheme: 'dark' });
  await page.waitForTimeout(300);
  const dark = await page.evaluate(() => {
    const bg = getComputedStyle(document.body).backgroundColor;
    return { isDark: bg.includes('13, 17, 23') || bg.includes('0d1117') || bg.includes('22, 27, 34') };
  });
  check('theme', 'Dark mode activates', dark.isDark);
  await page.emulateMedia({ colorScheme: 'light' });

  // Screenshots
  if (screenshotDir) {
    await page.screenshot({ path: path.join(screenshotDir, 'light.png'), fullPage: false });
    await page.emulateMedia({ colorScheme: 'dark' });
    await page.waitForTimeout(200);
    await page.screenshot({ path: path.join(screenshotDir, 'dark.png'), fullPage: false });
    await page.emulateMedia({ colorScheme: 'light' });
    await page.setViewportSize({ width: 375, height: 812 });
    await page.waitForTimeout(200);
    await page.screenshot({ path: path.join(screenshotDir, 'mobile.png'), fullPage: false });
  }

  await browser.close();

  // === REPORT ===
  console.log('');
  for (const f of findings) {
    const icon = f.status === 'pass' ? '  ✓' : '  ✗';
    console.log(`${icon} [${f.category}] ${f.name}${f.detail ? ': ' + f.detail : ''}`);
  }
  console.log(`\n  ${pass} passed, ${fail} failed`);
  if (screenshotDir) console.log(`  Screenshots: ${screenshotDir}/`);

  process.exit(fail > 0 ? 1 : 0);
})();
