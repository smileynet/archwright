---
id: 017
title: "Evidence ledger (ADR 0009): auto-appended confidence events in archwright-check"
status: open
blocked_by: []
---

# Evidence ledger (ADR 0009)

## Context

ADR 0009 (`.memory/adr/0009-confidence-evidence-lifecycle.md`) ratified split
storage by author: machine evidence events go to a tool-owned ledger
(`design/.archwright-evidence.json`); human ratifications go to the artifact's
`confidence` field + Evidence line. The design was accepted 2026-07-17 with
implementation deferred to the CK-07 plumbing timeframe. That plumbing now
exists (`_fingerprint_base`, `find_baseline`, aw/v1 — shipped 2026-07-18); the
ledger does not. Until it does, evidence events remain session-ephemeral
(accepted gap, now closable).

## What to build

In `tools/archwright-check.py`:

1. **Ledger discovery** — activation by existence, mirroring the baseline
   precedent: explicit `--evidence <file>` wins (create-if-missing — the flag
   states intent); otherwise walk up from spec dirs for an existing
   `.archwright-evidence.json` (same walk as `find_baseline`, stop at git
   root). No file found and no flag = no ledger writes (the ADR's
   "session-ephemeral until the ledger exists"). This keeps repo fixtures
   (`tests/fixtures/*/design/`) clean and matches "never silently created."
   Bootstrap per project: `echo '{}' > design/.archwright-evidence.json`.
2. **Event append rules** (tool auto-appends; humans never edit):
   - `demotion-candidate`: FAIL on a ★★ or ★ spec/invariant (counterexample
     found). Baselined violations emit NO event — the baseline entry is the
     human adjudication already. `—` fails emit nothing (no confidence claim
     to demote).
   - `promotion-candidate`: pass streak reached (`config.promotion_streak`,
     default 5, per (key, invariant); fail resets, error/skip neither counts
     nor resets — proves nothing), or a deeper-tier check passes on a ★/—
     invariant (assurance `bounded`, i.e. Alloy mechanical). ★★ is never a
     promotion candidate (top tier).
   - Events keyed `kind:id` (per ADR), carry invariant, confidence,
     timestamp, assurance, fingerprints (when available), provenance
     (from_pattern/from_force), reason (promotion only).
   - **Dedup**: an event is appended only if no existing event matches
     (event, key, invariant, confidence, reason, fingerprints). New evidence
     (new fingerprints) or a changed confidence = new event; identical
     re-observation = silence. Append-only otherwise.
3. **Trace mode**: `--trace` runs feed the same ledger (pass streaks per
   checked invariant; demotion-candidates for ★★/★ violations, including
   structural transition/guard/protocol violations at spec-level confidence).
   **Fog resolution**: trace events carry `fingerprints: []` — aw/v1
   fingerprints hash static path+content, which traces don't have (deliberate
   CK-07 scope cut, upheld); identity falls back to (key, invariant,
   confidence). Not a new decision — follows from the ratified scheme.
4. **Failure discipline**: malformed ledger JSON = tool error exit 2 (matches
   baseline); ledger write failure after checks ran = stderr warning, exit
   code unchanged. Contract/pattern "pass" results are not evidence (schema-
   only) and never feed the ledger.
5. **Output**: `--json` doc gains optional `evidence_ledger: {path,
   events_appended}`; non-JSON mode prints one summary line (like baseline).
   Exit codes unchanged (CK-04).

## Acceptance criteria

- [ ] No ledger file + no flag → check runs write nothing, create nothing
- [ ] `--evidence <tmp>` + ★★ FAIL → demotion-candidate with aw/v1 fingerprints
- [ ] Re-run appends nothing (dedup)
- [ ] Baselined violation → no demotion event
- [ ] `—` confidence FAIL → no demotion event
- [ ] Pass streak (threshold via `config.promotion_streak`) → one
      promotion-candidate, emitted once; FAIL resets the streak
- [ ] Trace FAIL on ★★ invariant → demotion-candidate, `fingerprints: []`
- [ ] Trace PASS increments streaks for checked invariants
- [ ] Malformed ledger → exit 2
- [ ] (Alloy-gated) ★ invariant passing bounded check → promotion-candidate
      with deeper-check reason
- [ ] All wired into `tools/run-fixture-tests.sh`; suite green
- [ ] Docs updated: check-output-schema.yaml, check skill (invocation
      contract per CK-17), AGENTS.md flags note + count row, PLAN.md,
      glossary (`Evidence ledger`), ADR 0009 status line

## Out of scope

- The report command joining ledger + artifacts (pending-candidates listing)
  — separate ticket when demanded; passup already receives escalations.
- Trace-mode fingerprints (upheld scope cut, see fog resolution above).
