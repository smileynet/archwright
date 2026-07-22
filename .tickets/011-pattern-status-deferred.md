---
id: 011
title: "Pattern status vocabulary: add deferred/gated (fog is being repurposed)"
status: done
blocked_by: []
created: 2026-07-17
---

# Pattern status vocabulary: add `deferred`/`gated` status

Field-driven (DemoVR phase-1 review 2026-07-17): DemoAR pattern
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
- [x] validate rejects `deferred` without `gated_on:`
- [x] fog definition unchanged; fixture suite gains one pass + one violating case

## Close-out (2026-07-18)

Ratified name: **`gated`** (operator, 2026-07-18) — "deferred" reads like a
punt; "gated" states the semantics and pairs with the required `gated_on:`.
Shipped: enum + gated_on requirement in `archwright-validate.py` (also rejects
`gated_on:` on non-gated status, and now enforces the status enum at all —
previously unvalidated); pattern-schema.yaml; pattern template; formalize
skeleton; glossary + CONTEXT.md. Suite: gated-with-gated_on PASSes,
gated-without-gated_on rejected. Fog definition unchanged. **AC 1 (DemoAR
`persistent-room-with-reset` re-status) defers to that lane** — the edit is:
`status: gated` + `gated_on: "Unity 6 migration"` + delete the disclaimer
paragraph.
