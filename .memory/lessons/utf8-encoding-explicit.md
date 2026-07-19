# Always pass encoding="utf-8" to read_text/write_text

One-line: Windows cp1252 default silently broke ★-confidence parsing.

**Date:** 2026-07-16 · **Source:** DemoAR pipeline run (Windows)

`read_text()` without an encoding uses the platform default; on Windows that's
cp1252, which mangles ★/— glyphs and broke confidence parsing in
validate/check/compile-alloy. Fixed everywhere — always pass `encoding="utf-8"`.
`mise.toml` `[env]` also sets `PYTHONIOENCODING=utf-8` for console output.
