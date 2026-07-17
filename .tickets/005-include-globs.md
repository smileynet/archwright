---
id: 005
title: include glob support for python-grep checks
status: done
blocked_by: []
created: 2026-07-17
---

# `include:` glob support for python-grep checks

Resolution (2026-07-17): implemented + verified. Suite green at **26/0/0** (two new conformance canaries: `no-shell-exec` for include filtering, `endpoint-pinned` for positional comment handling). ExposeAR `tls-only` scoped to `*.cs`: 897 noise matches → 2 honest ★★ violations (MP3Player.cs:14, SpeechRecognitionTest.cs:54). BONUS FIX: comment stripping truncated lines at the first comment token, which false-passed any pattern containing the token (`http://` contains `//`) — replaced with positional matching. Derive skill + constraint template documented; skills deployed.

## Why

Field need from ExposeAR (handoff task 3): `tls-only` matched 897 lines repo-wide (SVGs, .gitattributes, docs). Constraint specs need `check.include: ["*.cs"]` to scope declarative grep checks to relevant file types. Upstream added comment-stripping but not include filtering (verified 2026-07-17).

## What to build

- `_python_grep`: `include` param — list of globs; basename match (`*.cs`), or relative-posix-path match when the glob contains `/`.
- `_check_grep`: read `check.include` (string or list); pass through. `include:` combined with `command:` mode is a loud tool error (it only applies to declarative target+pattern checks).
- Fixture conformance spec (Extension Protocol rule 4): a constraint that would FAIL unscoped but PASSes with `include:` — proves filtering works. Update expected suite counts (22 → 23) in fixture README, AGENTS.md, mise.toml comment, check skill.
- Document in derive skill check-method guidance + `tools/templates/spec-constraint.md`; deploy skills.
- Verify on ExposeAR: add `include: ["*.cs"]` to `tls-only.md`, rerun, record honest result.

## Acceptance criteria

- [ ] `mise run test` green with new count (23/0/0)
- [ ] ExposeAR tls-only produces scoped, honest matches (expected: a handful in APIManager.cs / SpeechRecognitionTest.cs)
- [ ] Derive skill + template document `include:`; skills deployed
