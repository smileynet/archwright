# A check runner must fail loud when its own tooling is missing

One-line: absent `grep` made command-mode checks return empty stdout → false PASS on expect:absent.

**Date:** 2026-07-16 · **Source:** ExposeAR pipeline run (Windows)

The check tool trusted missing binaries: `grep` absent → empty output → "no
matches" → PASS. Fixed: pure-Python grep for target+pattern mode, Git-bash for
command mode, and rc>1 / "not recognized" / "command not found" → status error.
`fail-loud-at-source` applies to the checker itself, not just the checked code.
