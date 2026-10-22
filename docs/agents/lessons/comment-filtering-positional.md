# When filtering by comment token, never mutate the haystack

One-line: truncating lines at `//` false-passed TLS checks — `http://` contains the token.

**Date:** 2026-07-17 · **Source:** include-glob session (DemoAR lane)

Comment-aware matching must be positional (a match counts iff it starts before
the comment token), never truncation — patterns may legitimately contain the
token. Related include-glob design: bare glob matches file NAME, glob with `/`
matches project-relative path; explicitly-named single-file targets are never
filtered (GNU grep `--include` silently filters those — a field false-pass).
Fixture canaries: `no-shell-exec`, `endpoint-pinned`.
