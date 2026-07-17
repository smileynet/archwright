---
id: 011
title: "Pattern status vocabulary: add deferred/gated (fog is being repurposed)"
status: open
blocked_by: []
created: 2026-07-17
---

# Pattern status vocabulary: add `deferred`/`gated` status

Field-driven (AwsArchVR phase-1 review 2026-07-17): ExposeAR pattern
`persistent-room-with-reset` carries `status: fog` for a gate-CONFIRMED scope
deferral (anchor mechanism deferred to Unity 6), with an in-file disclaimer that
this is NOT an unresolved tension. Fog means "unknown forces / unresolved tension
encountered mid-span" — repurposing it for a ratified deferral corrupts the
signal both for humans and for any tooling that treats fog as a HITL-blocking
condition.

## What to build

- Add a status value (`deferred` or `gated`) to the pattern schema meaning:
  resolution ratified, activation gated on a named future event (e.g. a spike
  verdict, an engine migration).
- Require a `gated_on:` field naming the unblocking event when that status is used.
- Update: pattern schema in archwright-validate.py, formalize skill, glossary.

## Acceptance criteria

- [ ] persistent-room-with-reset re-statused without its disclaimer paragraph
- [ ] validate rejects `deferred` without `gated_on:`
- [ ] fog definition unchanged; fixture suite gains one pass + one violating case
