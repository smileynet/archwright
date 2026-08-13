---
id: "003"
title: Fixture suite green via mise (incl. Alloy behavior check)
status: done
blocked_by: ["002"]
created: 2026-07-17
---

# Fixture suite green via mise (incl. Alloy behavior check)

Resolution (2026-07-17): `mise run rehydrate-alloy` fetched the 6.2.0 dist jar (20 MB, smoke-tested via `java -jar ... help`). `mise run test` → **22 passed / 0 failed / 0 skipped** — behavior check active, no pyshim, no manual env. Evidence in session log.

## What to build

- `mise run rehydrate-alloy` → `.references/alloy6.jar` present (Alloy 6.2.0 dist jar — `exec` CLI added in 6.2.0).
- `mise run test` runs `tools/run-fixture-tests.sh` with mise-managed python3 + java on PATH — NO `/tmp/pyshim` hack, no manual `PYTHONIOENCODING`.
- Upstream 410623c claims 22/0/0 with the jar; verify on this machine.

## Acceptance criteria

- [x] `mise run test` → 22 passed / 0 failed / 0 skipped (behavior check active, not SKIP)
- [x] Works from a plain shell with no manual env setup

## Gotchas (lessons.md)

- #1: any tools/ change ⇒ fixture suite before commit
- #6: `only-in` compares raw substrings — output format is a contract
