# A checker proven only on passing cases may be vacuous

One-line: the transition bug was invisible until a deliberately-violating spec unexpectedly PASSED.

**Date:** 2026-07-17 · **Source:** Alloy wiring session (recurred same day: comment-truncation false-pass)

Wiring a checker end-to-end proves nothing until a known-bad input FAILs.
Codified: Extension Protocol rule 4 requires a violating scenario in every
conformance corpus; the suite's feature tests and fixture canaries model the
pattern. Corollary (from the second occurrence): verify a checker's fix with an
independent tool before trusting its verdict.
