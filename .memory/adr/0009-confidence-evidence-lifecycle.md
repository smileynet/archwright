# ADR 0009: Confidence Evidence Lifecycle — Split Storage by Author

**Status:** Accepted (2026-07-17); ledger IMPLEMENTED 2026-07-18 (ticket 017 — `archwright-check.py` `--evidence` / activation-by-existence; 11 conformance checks in the fixture suite). The report command (joining ledger + artifacts) remains future work.
**Closes:** Audit ticket C3 (as re-scoped by grill Q04, `.memory/grill/audit-plan-closeout/Q04-evidence-storage.md`).
**Relates to:** ADR 0007 (★★ transitions are HITL), ADR 0010 (research-first ★★ disposition), growth rule 7 (promotion = deeper checking + recorded evidence).

## Context

Confidence (★★/★/—) is a stated belief that a resolution names a true invariant. That belief is supposed to MOVE: promotion when evidence accumulates (pass streaks, deeper checks passing), demotion when a counterexample lands (brief:142, growth-rules.md rule 7). But the evidence events driving those moves have no home:

- Check runs produce FAILs with provenance and contrast pairs (CK-03 output contract, `tools/check-output-schema.yaml`) — then the structured record evaporates after the session.
- Pass streaks aren't recorded anywhere, so promotion candidates can't be surfaced mechanically.
- When a human DOES ratify a confidence change, nothing requires the artifact to cite why.

Three candidate homes were considered: (A) spec/pattern frontmatter that tools append to, (B) a separate tool-owned ledger, (C) derive-from-history (recompute from check logs on demand).

Precedents already in the system:

- CK-07/CK-08 (Phase 5): `design/.archwright-baseline.json` is a fingerprinted, tool-read, human-gated violation ledger — entries are "never added automatically" (CK-08).
- Force template: `evidence_level` + a prose Evidence section live in the human-authored artifact.

## Decision

**Split storage by author. Tools write tool-owned files; humans write human-owned files.**

### Machine events → ledger

`design/.archwright-evidence.json` — append-only, keyed by `kind:id`, fingerprinted (same plumbing family as the CK-07 baseline; shared fingerprint scheme pending R32).

The check tool auto-appends:

| Event | Emitted when |
|-------|--------------|
| `demotion-candidate` | FAIL on a ★★ or ★ spec (counterexample found) |
| `promotion-candidate` | Pass streak reached, or a deeper-tier check passes (e.g., a ★ spec passing a mechanical check) |

Events cite the CK-03 structured output (spec id, provenance, contrast pair reference) — which is why implementation sequences after CK-03 (now done) and alongside CK-07 (shared ledger/fingerprint plumbing; R32 fingerprinting research still open).

### Human ratifications → artifact

A confidence change is applied by editing the artifact itself: the `confidence` field is updated AND one line is added to the pattern/spec's Evidence section citing the ledger events that justified the move. ★★ transitions (assignment, promotion to, demotion from) always block for HITL — ADR 0007, reinforced by the CK-08 "never add automatically" precedent. ADR 0010's research gate shapes HOW demotion candidates are presented, not whether they block.

### Joining the two

- A report command joins ledger + artifacts and lists pending candidates (promotion candidates not yet ratified, demotion candidates not yet addressed).
- `archwright-passup` surfaces ★★ demotion candidates as escalations (grill Q02 ownership: check emits, passup lifts and routes).

## Consequences

- Confidence stops being write-once: the promotion path of growth rule 7 becomes mechanically supportable (candidates surfaced from real events) while staying human-ratified.
- Diffs stay honest: human-authored files change only by human decision; tool noise is confined to a tool-owned JSON file.
- Two ledgers (`.archwright-baseline.json`, `.archwright-evidence.json`) share fingerprint plumbing — implement together in the CK-07 timeframe to avoid divergent schemes.
- Until the ledger exists, evidence events remain session-ephemeral — an accepted gap; the ADR unblocks the design, CK-07 unblocks the mechanics.
- The Evidence-line convention means an artifact's confidence value is auditable back to concrete events (provenance for beliefs, not just for structure).

## Rejected Alternatives

- **(A) Tools append to spec/pattern frontmatter:** noisy diffs on human-authored files; a check that edits what it checks is a self-review smell; merge conflicts between lanes multiply.
- **(C) Derive-from-history (recompute on demand):** ephemeral — contradicts growth rule 7's "record evidence"; check logs aren't durable artifacts; recomputation can't distinguish "no evidence" from "evidence lost."
