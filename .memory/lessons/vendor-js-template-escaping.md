# Lesson: Vendor JS + Python string.Template

**Session:** 2026-07-30 (report visual overhaul)
**Incident:** Mermaid.js (3.4MB, ~10K `$` signs) corrupted when passed through Python `string.Template`. Rendered as black rectangles / broken CSS in browser.

## Rule

Never pass third-party vendor JS through `string.Template` substitution. The `$` characters in template literals, jQuery-style code, and minified variable names conflict with Template's `$identifier` syntax.

**Pattern:** Use a placeholder string in the template (`/* __PLACEHOLDER__ */`), let Template process everything else, then do a final `.replace("/* __PLACEHOLDER__ */", vendor_content)` after substitution.

**Confirmed cases:** Mermaid.js (3.4MB, ~10K `$`), ELK.js (1.4MB, `$` in minified variable names). Same `__PLACEHOLDER__` trick works for both.

## Also

- Always test inlined vendor JS with Playwright (headless browser) before claiming it works. `python -c "import ..."` doesn't catch DOM-dependent failures.
- Cytoscape.js renders to `<canvas>`, not DOM — CSS custom properties (`var(--x)`) don't work in its stylesheets. Compute colors via `getComputedStyle()` at runtime and pass literal values.
- `cytoscape-elk` extension only uses ELK for **node positions**. It discards ELK's edge routing entirely. For actual obstacle-avoidance routing, call ELK.js directly and render the computed bend points as SVG paths yourself.
- On Windows, npm-installed tools (smcat, mmdc) have extensionless binaries that Python `subprocess.run()` can't resolve. Use `shell=True` or append `.cmd`.
