# Run the fixture suite after ANY check/validate change

One-line: a path-format change silently broke only-in substring filters; only the suite caught it.

**Date:** 2026-07-16 · **Source:** DemoAR pipeline run

The python-grep rewrite emitted absolute Windows paths, breaking `only-in`
matching (its filters compare raw substrings — output format is a contract).
Fixed: project-relative POSIX paths. `mise run test` is the regression net;
trust AGENTS.md for the current green count.
