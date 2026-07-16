# PLAN: Archwright Audit & Intent-Alignment Proposal

**Goal:** Deep-dive the current functionality, verify it against the original intent (docs/brief.md), close the gap between what the docs claim and what the tools do, and land the improvements identified in real-world pipeline runs.

**Status:** Proposed — initial findings gathered 2026-07-16.
**Prior plan:** [.memory/PLAN.md](.memory/PLAN.md) (live design checking for lacrosse-bosse-platform) — complete, with three loose ends inherited here (C4, C5).

---

## Initial Findings (basis for the tickets)

1. **Docs drift confirmed.** AGENTS.md documents `tools/domains/{game,general}` — the directory does not exist. The AGENTS.md skill list omits `archwright-diagram`; the tools list omits `archwright-trace-validate`, `archwright-check-compile`, `run-fixture-tests`, `trace-schema.ts`.
2. **Session findings partially landed.** Of the 8 items in `.scratch/2026-07-14-session-findings.md`, commit `9ec9ca3` landed #2 (model mandatory), #3 (ast-grep guidance), #4 (`resolution_source`), #5/#6 (discipline notes). Pending: #1 (domain overlays), #7 (`protects_experience` flexibility), #8 (source quality assessment).
3. **Brief claims unverified as tool behavior.** The brief promises contrast pairs ("the diff is the diagnosis"), correction routing with fix direction and ★★ escalation, and confidence promotion/demotion. These exist in docs/spikes but their presence in actual tool output is unaudited.
4. **Prior-plan loose ends.** T7 (GDScript trace emitter) never started — Definition of Done item 6 ("new language = ~20 lines of emitter") is unproven. R18 growth rules drafted but not validated. S15 selective re-checking deferred.
5. **Open questions backlog is live.** 8 active questions in docs/open-questions.md; the lift contract (#1) and abstraction gap (#7) directly affect check-output quality.

---

## Task Graph

```
Workstream A: AUDIT (establish ground truth)
├── A1  Tool functional audit
├── A2  Skill consistency audit
├── A3  End-to-end pipeline dry run on fixture
├── A4  Claims audit (brief/README vs reality)
└── A5  Test coverage audit

Workstream B: KNOWN IMPROVEMENTS (from session findings — depends on A2 for placement)
├── B1  Domain overlays / adaptive scale vocabulary
├── B2  protects_experience flexibility
├── B3  Source quality assessment in survey
└── B4  Grep false-positive hardening in archwright-check (tooling, not just guidance)

Workstream C: INTENT GAPS (original brief → fuller realization — depends on A4)
├── C1  Contrast pairs in check output
├── C2  Correction routing as first-class output
├── C3  Confidence lifecycle tooling (promote/demote)
├── C4  T7 GDScript trace emitter (close out or descope)
└── C5  Growth rules validation (R18/S15 trigger criteria)

Workstream D: HYGIENE (independent — can run immediately)
├── D1  Fix AGENTS.md / README drift
├── D2  Archive prior plan, activate this one
└── D3  Promote session findings, clean .scratch
```

**Order:** D (immediate) ∥ A (audit first) → B (quick wins) → C (deeper work, informed by A3/A4).

---

## Workstream A: Audit — Establish Ground Truth

### A1 — Tool functional audit
**Problem:** 7 tools exist (`archwright-validate`, `-check`, `-check-compile`, `-compile-alloy`, `-trace-validate`, `run-fixture-tests`, `deploy-skills`); their actual behavior vs documented behavior has never been systematically compared.
**Action:** Run each tool against `tests/fixtures/lacrosse-bosse` (and a synthetic bad input). Record: invocation, output shape, exit codes, JSON conformance to check-results spec, failure modes.
**Acceptance:** Audit report (`.memory/audit/tools.md`) with one section per tool: verified capabilities, gaps, bugs found. Every claim backed by captured output.
**Effort:** 2h · **Priority:** P1

### A2 — Skill consistency audit
**Problem:** 10 skills evolved incrementally; vocabulary (confidence stars, phase names, artifact paths), cross-references (references/ files), and "Does NOT" boundaries may have drifted apart.
**Action:** Walk all 10 SKILL.md files. Check: dispatch table consistency (survey's routing vs actual skill names), shared vocabulary matches glossary, quality gates in steering match gates stated in skills, reference files resolve.
**Acceptance:** Report (`.memory/audit/skills.md`) listing inconsistencies with file:line; each classified fix-now / ticket / accept.
**Effort:** 1.5h · **Priority:** P1

### A3 — End-to-end pipeline dry run
**Problem:** The pipeline has been run against external projects but never end-to-end against the in-repo fixture; the prior plan's Definition of Done was validated piecemeal.
**Action:** Run survey → forces → tensions → resolve → formalize → model → derive → check against `tests/fixtures/lacrosse-bosse`. Time each phase. Verify the 6 Definition-of-Done items from the prior plan still hold.
**Acceptance:** Dry-run log with per-phase timing, friction points, and DoD item status (pass/fail/blocked). Item 6 expected to fail (no emitter) — feeds C4.
**Effort:** 3h · **Priority:** P1 · **Depends:** A1

### A4 — Claims audit (brief/README vs reality)
**Problem:** docs/brief.md and README make specific capability claims (contrast pairs, provenance routing with fix direction, ★★ escalation, 94ms counterexamples, confidence promotion). Some are spike-validated but not shipped in tools.
**Action:** For each claim in brief.md §"What archwright CAN do" and §"Key Ideas": label **shipped** (tool does it, cite output), **spike-only** (validated in .memory but not in tools), or **aspirational** (docs only).
**Acceptance:** Claims matrix (`.memory/audit/claims.md`). Spike-only and aspirational items map to C-tickets or explicit doc corrections.
**Effort:** 1.5h · **Priority:** P1

### A5 — Test coverage audit
**Problem:** `run-fixture-tests` exists but what it exercises is undocumented; most tools likely have zero automated coverage.
**Action:** Read `run-fixture-tests`, enumerate covered vs uncovered tools/paths. Propose a minimal fixture-test matrix (each tool × happy path × one failure path).
**Acceptance:** Coverage table + proposed test additions with effort estimates.
**Effort:** 1h · **Priority:** P2

---

## Workstream B: Known Improvements (session findings, pending)

### B1 — Domain overlays / adaptive scale vocabulary
**Source:** Finding #1 (High impact — blocks non-game projects).
**Problem:** Scale names (`premise`/`loops-systems`/`verbs-interactions`/`feel-finish`) are game-specific; web/platform runs had to improvise. AGENTS.md already documents `tools/domains/` as if it existed.
**Action:** Create `tools/domains/{game,general,web}/scales.yaml`; add auto-detection (project type inference from manifest files) with explicit override; update forces/tensions/model skills to load the overlay. Implementation plan exists in the AwsTcEverything session's grill output (`.memory/grill/archwright-tensions-resolution/Q05-adaptive-scale-selection.md` in that target repo — copy relevant content in).
**Acceptance:** Pipeline run against a web fixture uses web-scale vocabulary without manual mapping; game fixture unchanged. AGENTS.md layout becomes true.
**Effort:** 4h · **Priority:** P1

### B2 — `protects_experience` flexibility
**Source:** Finding #7.
**Problem:** archwright-derive requires `protects_experience` linking to a modeled experience; when the experience lives at product-force level the field is forced.
**Action:** Update derive skill + spec-schema: field accepts modeled-experience ID (preferred) or product-force ID (acceptable); `archwright-validate` warns (not errors) when absent.
**Acceptance:** Validator accepts both reference kinds; missing field produces a warning with guidance, not a failure.
**Effort:** 1h · **Priority:** P2

### B3 — Source quality assessment in survey
**Source:** Finding #8.
**Problem:** Survey doesn't assess source-material richness upfront, so users can't predict whether a run is a formalization exercise or a grilling exercise.
**Action:** Add "Source Quality Assessment" table to survey step 1 (ADRs / tenets / vision / feature specs / conventions / README — present? richness?) with the resulting mode prediction.
**Acceptance:** Survey skill emits the table; intake outline template includes it.
**Effort:** 45m · **Priority:** P2

### B4 — Grep false-positive hardening (tooling)
**Source:** Finding #3 — guidance landed in 9ec9ca3, but the tool itself still executes naive patterns.
**Problem:** Comments explaining a rule trigger the rule's grep; `import type` triggers runtime-import checks.
**Action:** In `archwright-check --static`: support an optional `check.engine: ast-grep` per constraint spec; for plain grep, apply comment-stripping preprocessing for known languages (`//`, `#`) before matching. Add fixture tests for both false-positive cases.
**Acceptance:** A constraint spec whose keyword appears only in a comment passes; `import type` does not trip import constraints. Fixture tests prove both.
**Effort:** 3h · **Priority:** P1 · **Depends:** A1

---

## Workstream C: Intent Gaps (fuller realization of the brief)

### C1 — Contrast pairs in check output
**Source:** Brief Key Idea #5 ("the diff is the diagnosis"); spike-validated per README.
**Problem:** Check failures likely report raw violations without the nearest-valid-alternative contrast the brief promises. (Confirm via A4.)
**Action:** If unshipped: add contrast-pair section to violation output — for constraint violations, show the allowed pattern from the spec next to the offending line; for behavior violations, show the nearest legal transition next to the illegal one.
**Acceptance:** A constraint failure and a trace failure each render `violation / nearest-valid` side by side, sourced from the spec.
**Effort:** 3h · **Priority:** P2 · **Depends:** A4

### C2 — Correction routing as first-class output
**Source:** Brief Step 5 — violation → invariant → pattern → force, with fix direction and ★★ escalation.
**Problem:** Provenance exists in specs; whether check output actually renders the full route (FROM pattern → force, FIX DIRECTION, escalation flag) is unverified.
**Action:** After A4: make check output include the full provenance chain and a `fix_direction` (sourced from spec/pattern), plus an `escalate: true` flag for ★★ violations. Wire into JSON schema (check-results spec).
**Acceptance:** A ★★ violation output contains pattern ID, force ID, fix direction, and escalation flag; matches the brief's Step 5 example shape.
**Effort:** 3h · **Priority:** P1 · **Depends:** A4

### C3 — Confidence lifecycle tooling
**Source:** Brief §Confidence System — "promoted (evidence accumulates) or demoted (counterexample found)."
**Problem:** Promotion/demotion is documented methodology with no mechanical support; nothing records evidence accumulation.
**Action:** Design first (small ADR): where evidence lives (spec frontmatter `evidence:` log?), what triggers promotion review, whether the check tool auto-appends counterexample events. Then minimal implementation: check failures append a demotion-candidate event; a report command lists promotion/demotion candidates.
**Acceptance:** ADR accepted; `archwright-check` records counterexample events against spec confidence; a listing surfaces candidates for human review.
**Effort:** 4h (1h ADR + 3h impl) · **Priority:** P2

### C4 — T7 GDScript trace emitter: close out or descope
**Source:** Prior plan Phase 3; DoD item 6 unproven.
**Problem:** The "~20 lines per language" portability claim has never been demonstrated — the trace validator exists but no real emitter feeds it.
**Action:** Either write the GDScript emitter against the trace schema and run S14-style conformance end-to-end, or explicitly descope with a doc correction (brief + prior plan DoD).
**Acceptance:** Working emitter + passing conformance run, or a committed descope note. No unproven claim remains in docs.
**Effort:** 2h · **Priority:** P2 · **Depends:** A3

### C5 — Growth rules validation (R18 → operational)
**Source:** Prior plan "Outstanding Research"; drafted in `.memory/specs/growth-rules.md` and referenced by archwright-resolve.
**Problem:** The 6 growth rules are drafted but never validated against a real change sequence; S15 (selective re-checking) was deferred with a "when checks exceed 5s" trigger nobody monitors.
**Action:** Run a change scenario against the fixture (modify a pattern → verify the rules identify exactly which specs need updates). Record check wall-time in A3 to make the S15 trigger observable.
**Acceptance:** One validated change-propagation walkthrough documented; growth-rules reference updated with corrections; S15 trigger criterion stated where it will be seen (check output or conventions).
**Effort:** 2h · **Priority:** P3 · **Depends:** A3

---

## Workstream D: Hygiene (immediate)

### D1 — Fix AGENTS.md / README drift
**Problem:** AGENTS.md documents nonexistent `tools/domains/`; skill list omits `archwright-diagram`; tools list omits 4 tools; `.memory` layout section is stale.
**Action:** Correct AGENTS.md project layout + skill/tool lists to match reality (or annotate `tools/domains/` as "planned — B1"). Sync README status section.
**Acceptance:** Every path in AGENTS.md layout exists; every skill/tool in the repo appears in the lists.
**Effort:** 30m · **Priority:** P1

### D2 — Archive prior plan, activate this one
**Action:** Add a "COMPLETE — superseded by /plan.md" header to `.memory/PLAN.md`. This file (`/plan.md`) is the active plan.
**Acceptance:** No ambiguity about which plan is live.
**Effort:** 10m · **Priority:** P1

### D3 — Promote session findings, clean .scratch
**Action:** `.scratch/2026-07-14-session-findings.md` is now fully represented by tickets B1–B4 (+ landed items). Note the ticket mapping at the top of the file, then delete it once B-tickets are underway (scratch policy: promote or delete).
**Acceptance:** No orphaned scratch; findings traceable to tickets.
**Effort:** 10m · **Priority:** P3

---

## Ticket Summary

| ID | Title | Priority | Effort | Depends |
|----|-------|:--------:|:------:|---------|
| A1 | Tool functional audit | P1 | 2h | — |
| A2 | Skill consistency audit | P1 | 1.5h | — |
| A3 | End-to-end pipeline dry run | P1 | 3h | A1 |
| A4 | Claims audit | P1 | 1.5h | — |
| A5 | Test coverage audit | P2 | 1h | — |
| B1 | Domain overlays / adaptive scales | P1 | 4h | — |
| B2 | protects_experience flexibility | P2 | 1h | — |
| B3 | Source quality assessment in survey | P2 | 45m | — |
| B4 | Grep false-positive hardening | P1 | 3h | A1 |
| C1 | Contrast pairs in check output | P2 | 3h | A4 |
| C2 | Correction routing first-class | P1 | 3h | A4 |
| C3 | Confidence lifecycle tooling | P2 | 4h | — |
| C4 | Trace emitter close-out/descope | P2 | 2h | A3 |
| C5 | Growth rules validation | P3 | 2h | A3 |
| D1 | Fix AGENTS.md/README drift | P1 | 30m | — |
| D2 | Archive prior plan | P1 | 10m | — |
| D3 | Clean .scratch findings | P3 | 10m | B1–B4 started |

**Total:** ~32h. **Recommended first batch (one session):** D1 + D2 + A1 + A2 + A4 (~6h) — establishes ground truth and fixes drift before any behavior changes.

---

## Definition of Done (plan level)

1. Every capability claim in docs/brief.md is labeled shipped / spike-only / aspirational, and no aspirational claim is presented as shipped.
2. AGENTS.md layout matches the repository exactly.
3. All 8 session findings are landed, descoped with rationale, or ticketed with owner.
4. The pipeline runs end-to-end on the in-repo fixture with per-phase timing recorded.
5. Check output carries the full brief-promised shape: provenance chain, fix direction, contrast pair, escalation flag.
6. Prior-plan loose ends (T7, R18, S15) are closed or explicitly descoped.
