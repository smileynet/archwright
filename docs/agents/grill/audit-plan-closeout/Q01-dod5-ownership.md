# Q01 — DoD-5 ownership: how does "check output carries the brief-promised shape" get satisfied?

**Status:** DECIDED — Option C′ (execute the Phase 5 slice, as Phase 5)
**Date:** 2026-07-17

## Question

Audit-plan DoD item 5 (check output carries provenance chain, fix direction, contrast pair, escalation flag) is owned by Phase 5 tickets CK-03/09/10 — design complete, implementation not started, no executor. Block, amend, or execute?

## Research

- DoD status verified: 1–4, 7 done; 5 = Phase 5; 6 = C4+C5.
- Phase 5 spec: "Implementation not started"; full scope 8–12h; DoD-5 chain (CK-03→04→05→09→10) ≈ 5–7h; CK-03 partly re-plumbing (A1: tool computes provenance that `--json` drops).
- Commit history since 2026-07-15: no second active agent. The "other agent may claim Phase 5" fog is unsupported — Phase 5 has no executor.
- A4: contrast pairs / correction routing / escalation = spike-only or aspirational — DoD-5 is the audit's headline finding.

## Options

- **A. Block on Phase 5** — rejected: no executor → open indefinitely.
- **B. Amend DoD-5 to "specified & handed off"** — rejected as primary (deferral dressed as delegation; mails the headline finding to an empty desk). Remains the cheap fallback if the chain stalls.
- **C. Pull minimal CK-03/09/10 into audit plan** — rejected: two specs for one tool; reverses the 2026-07-16 reconciliation.
- **C′. Execute the chain under the Phase 5 spec** — CHOSEN. DoD-5 stays literal; CK-03→04→05→09→10 runs next with this line of work as named executor; audit plan records "in execution via Phase 5a/5b chain." Plus `archwright-passup` skill (Q02) as consumer, sequenced with CK-17.

## Decision

C′. Initially recommended B; the operator's "why not C?" challenge exposed that B rested on the phantom second-agent assumption. With one actor, executing the slice under its rightful spec has C's substance without its ownership cost.

## Implications

- Next major execution block: CK-03 → CK-04 → CK-05 → CK-09 → CK-10 (+ passup skill) ≈ 7–9h total
- Audit plan closes when: this chain lands (DoD-5) + C4/C5 resolved (DoD-6)
- Phase 5 executor fog is resolved: this line of work
- Fallback: option B is a one-paragraph amendment if priorities shift
