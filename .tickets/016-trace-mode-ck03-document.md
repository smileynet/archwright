---
id: 016
title: "Trace mode ignores --json and emits a bespoke shape — wire into the CK-03 document"
status: open
blocked_by: []
created: 2026-07-18
---

# Trace mode ignores `--json` and emits a bespoke shape

## Problem

`archwright-check.py --trace` prints its own result shape (`TraceValidationResult`
in `tools/trace-schema.ts`) and ignores the `--json` flag entirely — it never
routes through `build_document`. But `tools/check-output-schema.yaml` lists
`trace` in the CK-03 `scope.mode` enum, implying trace results participate in
the document contract. Consequences:

- `archwright-passup` consumes the CK-03 contract; trace FAILs arrive in a
  different shape with no `severity`/`escalate`/`suggested_route`/`contrast_pair`
  fields — trace violations can't be routed uniformly with static ones.
- The schema enum advertises a mode that no producer emits.

Discovered during the ticket-015 close-out (2026-07-18) when documenting the
trace skip fields.

## What to build

Either (decide at implementation, prefer A):

**A. Wire trace mode into CK-03.** `--trace --json` emits the document shape:
the trace violation becomes a `violations[]` entry (confidence from the
violated invariant, severity derived, `escalate` on ★★, `contrast_pair` =
{expected: invariant predicate/description, actual: event+state at failure},
provenance from the invariant's `from_pattern`/`from_force`);
`invariants_skipped`/`guards_skipped` map into `skips[]`; coverage counts the
invariants. Keep the bespoke shape as the non-`--json` output (it carries
replay detail the document doesn't need). Update trace-schema.ts and both
golden-check sections.

**B. Correct the schema.** Remove `trace` from the mode enum and document that
trace output is a separate contract (trace-schema.ts). Cheaper, but leaves
passup unable to route trace violations.

## Acceptance criteria

- [ ] `--trace <spec> <trace> --json` on a violating trace emits a CK-03
      document with all 10 violation fields (or the schema no longer claims
      trace mode, option B)
- [ ] Skips map into the document's `skips[]` with reasons
- [ ] Fixture suite gains golden checks for the chosen behavior (incl. a
      violating case)
- [ ] check-output-schema.yaml, trace-schema.ts, and the passup skill's Input
      section agree with whichever option ships

## Context

- Tickets 015 (trace skip fields) and 012 (`skips[]` in CK-03)
- `skills/archwright-passup/SKILL.md` Input section — the intended consumer
