# YAML 1.1 parses the key `on:` as boolean True

One-line: the Alloy compiler generated transition-less models for months; every behavior check passed vacuously.

**Date:** 2026-07-17 · **Source:** Alloy wiring session

PyYAML coerces unquoted on/off/yes/no — including as KEYS. The trace validator
carried the workaround inline; the compiler didn't. Fixes: shared
`tools/archwright_common.py::state_events()` (all tools MUST use it — the
second inline copy is where the bug hides), and templates/fixtures write
`"on":` quoted. Rule: when one tool works around a parsing quirk, grep every
other tool for the same raw access.
