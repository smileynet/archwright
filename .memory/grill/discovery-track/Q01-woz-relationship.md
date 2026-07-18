# Q1: wizard_of_oz relationship

**Status:** Decided 2026-07-18
**Decision:** Option A — standalone + import/export.

## Question

Does wizard_of_oz stay a standalone product (archwright imports its patterns, consumes its session exports), get absorbed as archwright's game-discovery instance, or get forked?

## Research

- wizard_of_oz has independent product identity: user-facing (solo indie devs), release plan (v0.1.0 → internal GitLab `woz-game-planner`), two field sessions, own maintenance loop (release gates, session lint).
- Its design corpus is already archwright-format — patterns import with citations, zero conversion.
- Dual-track research: the risk is ownership handoffs, not code location. Orchestration research: don't merge/split without a boundary crossing.
- Fork option loses provenance (evidence cites wizard_of_oz sessions/commits) and recreates the silent-staleness failure mode observed with claude/codex skill copies.

## Options Considered

| Option | Verdict |
|---|---|
| A. Standalone + import/export | **Chosen** — one-way dependency, no vocabulary fork, both evolve independently |
| B. Absorb | Rejected — kills a shipped product's release path; archwright inherits unrelated maintenance; violates rule-of-two |
| C. Fork + sever | Rejected — loses provenance, staleness risk |

## Implications

- Imports are **snapshots with citation**, refreshed deliberately — not auto-synced (default accepted; no stronger sync mechanism requested).
- ADR 0011 Decision 9 ratified as written.
- Task T1 (facilitation-stance reference distilling 4 wizard_of_oz patterns) proceeds with provenance citations back to `wizard_of_oz/design/patterns/`.
- Task T7 (woz-session-export) treats wizard_of_oz session format as an external contract — exporter validates against it, doesn't own it.
