---
id: "042"
title: "Adopt tkt natively: prefer it when on PATH, align ticket conventions regardless"
status: done
blocked_by: []
---

# Adopt tkt natively: prefer it when on PATH, align ticket conventions regardless

Cross-repo counterpart of crew-research ticket 41 (tkt rollout). tkt is the git-native
ticket CLI at crew-research `tools/tkt`, built against the shared frontmatter contract
both repos already satisfy (archwright's 40 tickets verified: parse clean, frontier
computes correctly, round-trips are byte-identical — 2026-07-21).

## Why

Operator directive 2026-07-21: "archwright will need to rebase to prefer tkt native
approach when available, and that it aligns regardless." Two collision incidents here
(005 double-implementation, 009/010 id race) are the motivating evidence; tkt's claim
loop (fetch → scan local+origin → create → commit → push, bounded renumber-retry) is the
mechanical fix. This ticket was itself allocated by `tkt new` from this repo — the
archwright-side birth run.

## What to build

1. **Prefer tkt when on PATH.** Wherever this repo's guidance describes ticket work
   (AGENTS.md, PLAN.md conventions, any concurrent-sessions guard notes), route to tkt
   commands first — `tkt ready` / `tkt new` / `tkt claim` / `tkt close` / `tkt validate` —
   with the manual protocol retained as explicit fallback-when-absent. Install note:
   `uv tool install <crew-research>/tools/tkt` (interim: `PYTHONPATH=<crew>/tools/tkt
   python3 -m tkt.cli`).
2. **Align regardless.** Document the shared contract as THIS repo's ticket convention,
   independent of the tool being installed: status vocabulary `open | in_progress | done`
   (in_progress = claimed WIP, new here — today only claim commits mark WIP), quoted-or-
   unquoted text ids matching filename prefix, `blocked_by` done-gating, claim-before-
   allocate via fetch+rescan+push. Hand-done ticket work follows the same shapes tkt
   would produce.
3. **Wire validation.** `tkt validate` (or its exit-code contract) added to a mise task /
   the fixture-suite runway so contract drift and decay findings (25 current unchecked-AC
   warnings) surface mechanically. Decide whether warnings stay advisory here.
4. **PLAN.md seam note.** PLAN.md remains the authoritative status narrative (its own
   rule); record that ticket frontmatter is the machine-readable layer tkt computes from,
   and that a future drift-check (crew ticket 41's sync-plan) may watch the seam.

## Acceptance criteria

- [x] AGENTS.md (or the conventions doc it points to) prefers tkt commands with manual
      fallback; install/interim invocation documented
- [x] Shared contract documented as repo convention (incl. in_progress adoption)
- [x] `tkt validate` runs green here via a mise task (warnings advisory unless decided
      otherwise)
- [x] Existing tickets remain valid unchanged (zero migration)

## Out of scope

- tkt feature work (renumber, sync-plan, batch create — crew ticket 41)
- Fixing this repo's 25 unchecked-AC decay warnings (separate cleanup if wanted)

## Resolution (2026-07-22)

- AGENTS.md §Tickets added: shared contract as repo convention (text ids, `open | in_progress | done`, blocked_by gating, unknown-field preservation, claim-before-allocate), tkt command table with install + interim invocation, manual fallback, `tk` warning. Layout row + mise task list updated (`validate:tickets`, `ship`).
- `mise run validate:tickets` (f69f23d, pre-existing) verified green: exit 0, 27 unchecked-AC warnings — kept advisory (decay cleanup stays out of scope).
- Zero migration confirmed: `tkt validate` status=pass over all existing tickets; `tkt ready` frontier matches manual scan.
- PLAN.md seam note recorded (frontmatter = machine layer tkt computes from; sync-plan may watch the seam); stale NEXT UP refreshed.
- `.memory/lessons/concurrent-sessions.md` allocation guard routed to tkt.
- R11/R12 workaround audit (directive rider): R11 still live — 039 open, both check.py:384 and validate.py:63 still substring-split on `---`. R12 item 1 marked OBSOLETE (040 shipped exclude); items 2–3 stand.
- This ticket was itself worked end-to-end via tkt (new → claim → close) — the birth run doubles as acceptance evidence.
