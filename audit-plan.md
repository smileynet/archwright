# AUDIT PLAN: Archwright Functionality & Intent-Alignment

**Scope:** Standalone audit plan — separate from mainline feature planning (`.memory/PLAN.md`, which remains the historical record of the lacrosse-bosse live-checking work).

**Goal:** Deep-dive the current functionality, verify it against the original intent (docs/brief.md), close the gap between what the docs claim and what the tools do, and land the improvements identified in real-world pipeline runs.

**Status:** Proposed — initial findings gathered 2026-07-16; re-baselined same day against origin/main (`82c5d30`), which added the `archwright-audit` skill, `archwright-contract` phase, `tools/domains/game/predicates.yaml`, tool file-extension renames, and open questions #9–#13.
**Prior plan:** [.memory/PLAN.md](.memory/PLAN.md) — complete, with three loose ends inherited here (C4, C5).

---

## Initial Findings (basis for the tickets)

1. **Docs drift — reduced but persists.** Upstream updated AGENTS.md, but verified remaining drift: `tools/domains/general/` documented but missing; `domains/game/` claims "predicates + scales" but has no scales; the skill list omits `archwright-diagram` (12 skills exist, 11 listed); the Commands table uses pre-rename tool names (`archwright-validate` vs `archwright-validate.py`); the layout omits all 8 tool scripts.
2. **Session findings mostly landed.** Of the 8 items in `.scratch/2026-07-14-session-findings.md`: #2–#6 landed in `9ec9ca3`; #1 (domain overlays) is now partially started upstream (`domains/game/predicates.yaml`, 13 predicates) but scales + auto-detection remain; #7 (`protects_experience` flexibility) and #8 (source quality assessment) verified still absent from derive/survey skills.
3. **Brief claims unverified as tool behavior.** The brief promises contrast pairs ("the diff is the diagnosis"), correction routing with fix direction and ★★ escalation, and confidence promotion/demotion. These exist in docs/spikes but their presence in actual tool output is unaudited.
4. **Prior-plan loose ends.** T7 (GDScript trace emitter) never started — Definition of Done item 6 ("new language = ~20 lines of emitter") is unproven. R18 growth rules drafted but not validated. S15 selective re-checking deferred.
5. **Open questions backlog is live.** Now 13 active questions; the lift contract (#1) and abstraction gap (#7) affect check-output quality; new #13 (tiered check tooling) directly re-scopes ticket B4.
6. **New audit capability to dogfood.** `archwright-audit` (doc-truth auditing with Lies/Damn-Lies classification and ticket format) is exactly the methodology tickets A4/D1 describe — this plan should use it on the archwright repo itself.

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
└── B4  Tiered check routing + grep false-positive hardening (open question #13)

Workstream C: INTENT GAPS (original brief → fuller realization — depends on A4)
├── C1  Contrast pairs in check output
├── C2  Correction routing as first-class output
├── C3  Confidence lifecycle tooling (promote/demote)
├── C4  T7 GDScript trace emitter (close out or descope)
├── C5  Growth rules validation (R18/S15 trigger criteria)
└── C6  Re-evaluate phase gates: block only where human input is needed

Workstream D: HYGIENE (independent — can run immediately)
├── D1  Fix AGENTS.md / README drift
├── D2  Archive prior plan, activate this one
└── D3  Promote session findings, clean .scratch
```

**Order:** D (immediate) ∥ A (audit first) → B (quick wins) → C (deeper work, informed by A3/A4).

---

## Workstream A: Audit — Establish Ground Truth

### A1 — Tool functional audit
**Problem:** 8 tool scripts exist (`archwright-validate.py`, `archwright-check.py`, `archwright-check-compile.mjs`, `archwright-compile-alloy.py`, `archwright-trace-validate.{sh,mjs}`, `run-fixture-tests.sh`, `deploy-skills.sh`); their actual behavior vs documented behavior has never been systematically compared. Recent rename (extensions added, `6cb54f3`) may have broken PATH invocations documented elsewhere.
**Action:** Run each tool against `tests/fixtures/lacrosse-bosse` (and a synthetic bad input). Record: invocation (verify documented command names still resolve post-rename), output shape, exit codes, JSON conformance to check-results spec, failure modes. Verify the `--static` → `--structural` flag rename is consistent between tool and docs.
**Acceptance:** Audit report (`.memory/audit/tools.md`) with one section per tool: verified capabilities, gaps, bugs found. Every claim backed by captured output.
**Effort:** 2h · **Priority:** P1

### A2 — Skill consistency audit
**Problem:** 12 skills evolved incrementally (audit + contract added upstream 2026-07-15); vocabulary (confidence stars, phase names, artifact paths), cross-references, and "Does NOT" boundaries may have drifted. Known risks: the 9-phase pipeline string (`survey → … → model → contract → derive → check`) was updated in survey but may be stale in other skills/steering/docs; survey's routing table may not include audit/contract/diagram; `--static` vs `--structural` naming split.
**Action:** Walk all 12 SKILL.md files + both steering files. Check: dispatch table completeness (survey routing vs actual skill set), pipeline string consistency everywhere it appears, shared vocabulary matches glossary, quality gates in steering match gates stated in skills, reference files resolve.
**Acceptance:** Report (`.memory/audit/skills.md`) listing inconsistencies with file:line; each classified fix-now / ticket / accept.
**Effort:** 2h · **Priority:** P1

### A3 — End-to-end pipeline dry run
**Problem:** The pipeline has been run against external projects but never end-to-end against the in-repo fixture; the prior plan's Definition of Done was validated piecemeal; the new contract phase has never run against the fixture at all.
**Action:** Run all 9 phases — survey → forces → tensions → resolve → formalize → model → contract → derive → check — against `tests/fixtures/lacrosse-bosse`. Time each phase. Verify the 6 Definition-of-Done items from the prior plan still hold. Exercise survey's new auto-triggered audit step (1b) and derive's contract cross-referencing rules.
**Acceptance:** Dry-run log with per-phase timing, friction points, and DoD item status (pass/fail/blocked). Item 6 expected to fail (no emitter) — feeds C4.
**Effort:** 3.5h · **Priority:** P1 · **Depends:** A1

### A4 — Claims audit via archwright-audit (dogfood)
**Problem:** docs/brief.md and README make specific capability claims (contrast pairs, provenance routing with fix direction, ★★ escalation, 94ms counterexamples, confidence promotion). Some are spike-validated but not shipped in tools. The repo now ships `archwright-audit` — a doc-truth methodology that has never been run on archwright itself.
**Action:** Run `archwright-audit` on the archwright repo (brief, README, AGENTS.md, glossary vs skills/tools). Classify per the skill: Lies / Damn Lies / planned-as-current / terminology drift. Extend with the capability-claims lens: label each brief claim **shipped** (tool does it, cite output), **spike-only**, or **aspirational**.
**Acceptance:** Audit report in the skill's own ticket format (`.memory/audit/claims.md`). Spike-only and aspirational items map to C-tickets or explicit doc corrections. Doubles as a dogfood test of the audit skill — friction findings feed A2.
**Effort:** 2h · **Priority:** P1

### A5 — Test coverage audit
**Problem:** `run-fixture-tests` exists but what it exercises is undocumented; most tools likely have zero automated coverage.
**Action:** Read `run-fixture-tests`, enumerate covered vs uncovered tools/paths. Propose a minimal fixture-test matrix (each tool × happy path × one failure path).
**Acceptance:** Coverage table + proposed test additions with effort estimates.
**Effort:** 1h · **Priority:** P2

---

## Workstream B: Known Improvements (session findings, pending)

### B1 — Domain overlays / adaptive scale vocabulary
**Source:** Finding #1 (High impact — blocks non-game projects). Partially started upstream: `tools/domains/game/predicates.yaml` (13 predicates) + `research-sources.md` exist; scales, `general/`, and auto-detection do not.
**Problem:** Scale names (`premise`/`loops-systems`/`verbs-interactions`/`feel-finish`) are game-specific; web/platform runs had to improvise. AGENTS.md documents `domains/{game,general}` with "predicates + scales" — only game predicates exist.
**Action:** Add `scales.yaml` to `tools/domains/game/`; create `tools/domains/{general,web}/` overlays; add auto-detection (project type inference from manifest files) with explicit override; update forces/tensions/model skills to load the overlay. Coordinate with open question #9 (predicate library growth) so overlay structure serves both scales and predicates. Implementation plan exists in the AwsTcEverything session's grill output (`.memory/grill/archwright-tensions-resolution/Q05-adaptive-scale-selection.md` in that target repo — copy relevant content in).
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

### B4 — Tiered check routing + grep false-positive hardening → **ABSORBED by Phase 5 (2026-07-16)**
Upstream added Phase 5 "Polyglot + Agent-Native Check Tool" (`.memory/specs/polyglot-check-tooling.md`) covering this ticket's full scope: CK-05 (ripgrep backend), CK-11–13 (ast-grep + tree-sitter-gdscript), CK-06 (`target_status: pending`). B4's unique deltas were folded into the Phase 5 spec as CK-05 acceptance additions (comment false-positive hardening; error on unknown `expect:` values per A1/F3). No separate work remains here — execute via Phase 5.

---

## Workstream C: Intent Gaps (fuller realization of the brief)

### C1 — Contrast pairs in check output → **ABSORBED by Phase 5 CK-10 (2026-07-16)**
A4/P2 confirmed the gap (trace output has the `valid_events` primitive; no contrast rendering; constraint checks have none). Phase 5 ticket CK-10 implements `contrast_pair: {expected, actual}` — exactly this scope. Execute via Phase 5.

### C2 — Correction routing as first-class output → **ABSORBED by Phase 5 CK-03/CK-09 (2026-07-16)**
A4/L3 confirmed the gap with evidence (constraint FAIL shows invariant+★★ only; trace FAIL has `from_pattern` but `from_force: null`; no fix direction; no escalation flag; `--json` drops data the tool computes). Phase 5 CK-03 (structured output: `spec_id`, `from_pattern`, `from_force`, `suggested_route`) + CK-09 (provenance + suggested_route) cover it; the ★★ `escalate: true` flag was added to CK-09's acceptance in the spec. Execute via Phase 5.

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

### C6 — Re-evaluate phase gates: block only where human input is needed
**Source:** Operator feedback 2026-07-16. Current pipeline discipline (steering/archwright-conventions.md, AGENTS.md, survey skill) mandates a hard STOP after **every** phase — "present the phase output, ask whether to proceed — never auto-advance."
**Problem:** Universal stops treat all checkpoints as equal, but only some phases genuinely require a human: resolve (decisions), grilling (unknown forces), ★★ escalations, and final acceptance. For AFK phases (forces, tensions clustering, formalize, model, contract, derive, check) the stop is review-availability, not review-necessity — it adds turnaround latency on every run without adding decision quality.
**Action:** Classify every gate in the 9-phase pipeline as **HITL-blocking** (human decision/input/review is required to proceed correctly) or **flow-through** (artifact is produced and reviewable, but the pipeline may auto-advance when the human has pre-authorized a run span). Draft an ADR — this reverses a deliberate documented decision, so it must engage the original rationale ("skipping review compounds errors silently"). Candidate mitigations for that rationale: auto-advance only when the prior phase's artifact passes mechanical validation (`archwright-validate`); confidence-gating (any — or ★★-touching output forces a stop); an end-of-span digest listing every artifact produced for batched review. Then update: steering/archwright-conventions.md, AGENTS.md §Pipeline Phase Discipline, survey skill's STOP instructions, and any per-skill "present and STOP" language. A3's dry run should record where stops added value vs. pure latency — use that as evidence.
**Acceptance:** ADR accepted with an explicit gate classification table (phase → blocking? → why). Conventions/skills updated consistently: HITL gates (resolve, grill, ★★ escalation, final acceptance) still hard-block; flow-through phases chain within a pre-authorized span and emit a review digest. A pipeline run on the fixture completes survey→check with exactly the HITL stops and no others.
**Effort:** 3h (1h ADR + 2h edits) · **Priority:** P1 · **Depends:** A3 (gate-friction evidence)

---

## Workstream D: Hygiene (immediate)

### D1 — Fix AGENTS.md / README residual drift
**Problem:** Verified remaining drift post-upstream-update: `tools/domains/general/` documented but missing; `domains/game/` described as "predicates + scales" (no scales); skill list omits `archwright-diagram`; Commands table uses pre-rename tool names (no `.py`/`.sh` extensions); layout omits the 8 tool scripts and stale `.memory` entries.
**Action:** Correct AGENTS.md layout + skill/tool lists + Commands table to match reality (annotate `tools/domains/general` as "planned — B1" if kept). Sync README status section.
**Acceptance:** Every path in AGENTS.md layout exists (or is marked planned with a ticket ref); every skill/tool in the repo appears in the lists; Commands table invocations actually run.
**Effort:** 45m · **Priority:** P1

### D2 — Mark prior plan complete, cross-link audit plan
**Action:** Add a "COMPLETE" status header to `.memory/PLAN.md` noting its loose ends (T7, R18, S15) are tracked in `/audit-plan.md` (C4, C5). This file remains a standalone audit plan, not a replacement for mainline planning.
**Acceptance:** Prior plan clearly marked complete; loose-end tracking is unambiguous.
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
| A2 | Skill consistency audit (12 skills) | P1 | 2h | — |
| A3 | End-to-end pipeline dry run (9 phases) | P1 | 3.5h | A1 |
| A4 | Claims audit via archwright-audit (dogfood) | P1 | 2h | — |
| A5 | Test coverage audit | P2 | 1h | — |
| B1 | Domain overlays / adaptive scales | P1 | 4h | — |
| B2 | protects_experience flexibility | P2 | 1h | — |
| B3 | Source quality assessment in survey | P2 | 45m | — |
| B4 | Tiered check routing + grep hardening | — | — | ABSORBED → Phase 5 (CK-05/06/11–13) |
| C1 | Contrast pairs in check output | — | — | ABSORBED → Phase 5 (CK-10) |
| C2 | Correction routing first-class | — | — | ABSORBED → Phase 5 (CK-03/09) |
| C3 | Confidence lifecycle tooling | P2 | 4h | — |
| C4 | Trace emitter close-out/descope | P2 | 2h | A3 |
| C5 | Growth rules validation | P3 | 2h | A3 |
| C6 | Phase gates: block only on HITL need | P1 | 3h | A3 |
| D1 | Fix AGENTS.md/README residual drift | P1 | 45m | — |
| D2 | Archive prior plan | P1 | 10m | — |
| D3 | Clean .scratch findings | P3 | 10m | B1–B4 started |

**Total:** ~38h base + ~7h discovered (B5–B7, C7). **First batch executed 2026-07-16** — see Progress below.

### Discovered during execution (sources: A1/A2/A4 reports in `.memory/audit/`)

| ID | Title | Priority | Effort | Source |
|----|-------|:--------:|:------:|--------|
| B5 | Skill cleanup batch (numbering, headers, enum counts, temp paths, diagram contradictions) | P2 | 2h | A2 items 15,17,19–23 |
| B6 | Unify confidence vocabulary across skills (glossary as anchor; map L1–L5, error/warn/info, HIGH/MED/LOW to ★★/★/—) | P2 | 1.5h | A2 item 14 |
| B7 | Restore fixture `design/` artifacts + repair `run-fixture-tests.sh` + resolve trace-validate fork (delete or fix `.sh`/`.mjs`) | P1 | 3h | A1 F1/F2, A4 DL1 — **blocks A3** |
| C7 | Contract/derive/model spec-ownership decision (who emits contract specs; does one-per-file bend for event groups?) | P2 | 2h | A2 items 8–10 (HITL) |

## Progress

**Batch 1 (2026-07-16):** D2 ✅ · A1 ✅ (`.memory/audit/tools.md`) · D1 ✅ · A2 ✅ (`.memory/audit/skills.md`, fix-now edits landed) · A4 ✅ (`.memory/audit/claims.md`, dogfood of archwright-audit).
Key outcomes: 5 dead-flag/broken-tool references fixed in skills/steering; survey routing completed to 12 skills; `subagent-reliability.md` source-of-truth restored; AGENTS.md/README now match verified reality; claims matrix: 6 shipped, 3 spike-only, 4 aspirational.

**Phase 5 reconciliation (2026-07-16):** Upstream's Phase 5 (polyglot check tooling, `.memory/specs/polyglot-check-tooling.md`) absorbs B4, C1, C2. Their unique deltas were folded into that spec (CK-05: comment false-positives + `expect:` typo → exit 2; CK-09: ★★ `escalate: true`); the spec's two false premises were corrected against A1 evidence (trace-validate.sh is broken, `--model` flag doesn't exist). Remaining independent audit work: B7 → A3 + A5, B1–B3, B5, B6, C3–C7, D3.
**B7 ✅ (2026-07-16):** Fixture `design/` restored (3 patterns + 5 specs written, joining upstream's contract spec); `run-fixture-tests.sh` repaired (set-e find death, stale extensionless paths) and extended (behavior-spec section); broken `archwright-trace-validate.{sh,mjs}` deleted (canonical: `archwright-check.py --trace`). Verified: 16 passed / 0 failed / 1 skipped (Alloy jar); negative test — injected `ball_holder = self` violation caught by both ★★ specs with file:line, then reverted to green. A4/DL1 doc lie corrected in fixture README. **A3 is now unblocked.**
**A3 + A5 ✅ (2026-07-16):** Pipeline dry run (`.memory/audit/pipeline-dryrun.md`): 0.79s full check suite (DoD-5 pass); prior-plan DoD re-verified — 2 pass, 2 external, 1 partial-fail (provenance), 1 fail (emitter → C4). Top findings: forces have no artifact (provenance roots are hollow ID strings → new ticket **C8**); quality gates are honor-system (no tool checks them); model mandate lacks artifact enforcement (→ C7 scope); resolve-gate-on-pre-resolved = concrete C6 evidence. Coverage audit (`.memory/audit/test-coverage.md`): 4/9 tool modes covered, 0 automated failure paths → propose Phase 5 **CK-20** (fixture test hardening, ~2.5h: violation overlay, bad-spec fixtures, trace fixtures).

| ID | Title | Priority | Effort | Source |
|----|-------|:--------:|:------:|--------|
| C8 | Forces as first-class artifact: define `design/forces/` format; extend link validation to `serves:`/`from_force:`; backfill fixture | P1 | 3h | A3 finding 1 — core-promise gap |
| CK-20 | Fixture test hardening (violation overlay + bad-spec + trace fixtures) — execute under Phase 5a | P2 | 2.5h | A5 |

**C6 ✅ (2026-07-16):** ADR 0007 accepted (`.memory/adr/0007-hitl-only-gates.md`) with the gate classification table. HITL-blocking: resolve (batched confirmation when pre-resolved), L4/L5 desire validation, ★★ events, fog, end-of-span digest. Flow-through: everything else, guarded by pre-authorized span + `archwright-validate.py` pass + digest entry. Updated: conventions steering (rules + "proceed" semantics), AGENTS.md §Pipeline Phase Discipline, survey step 5 (now proposes a span). Residual per-skill "present and STOP" phrasing → B5. DoD item 7 satisfied.
**C8 ✅ (2026-07-16):** Forces are first-class. Per-force files in `design/forces/` (decision: per-file, not single inventory); `force` kind added to `archwright-validate.py` (polarity/hardness/evidence_level rules, desires-can't-serve check); `--links` now resolves `serves:` + nested `from_force:` against the force inventory (enforcement activates when the first force file exists — older projects unaffected); template added; fixture backfilled with 5 forces; suite now 21 passed / 0 failed / 1 skipped, dangling-force-ref detection verified. Forces skill outputs per-force files; AGENTS.md/conventions/fixture README updated.

**C7 research ✅ (2026-07-16):** 3 subagent tracks (ownership, granularity, addressability) → `.memory/research-contract-ownership.md`. Evidence-backed recommendation: **R1** contract phase solely owns contract specs (model emits contract-*candidates*; derive's contract subsection deleted) — no surveyed methodology puts contracts in modeling; duplication avoided by direction, not dedup. **R2** one-spec-per-file stands; unit = independently-evolving contract; default one spec per event type, sanctioned protobuf-style exception for a single-producer protocol cluster (fixture's `ball-possession-events.yaml` is legal); per-system `<system>-events.yaml` dumping grounds prohibited. **Awaiting ratification (HITL)** — then 4 skill/template edits listed in the synthesis.
**Next:** C7 ratification → edits · B-workstream (B1–B3, B5, B6) · C3/C4 · D3. Phase 5 execution under `.memory/PLAN.md`.

---

## Out of Scope (tracked, not ticketed here)

New open questions #10–#12 from the upstream catalyst run are proposal material for mainline planning, not this audit:
- **#10 Audit findings as force input** — natural follow-on once A4 produces real findings; revisit after Workstream A.
- **#11 Code generation from contract specs** — feature work, belongs in a future feature plan.
- **#12 Architecture-as-documentation** — would ultimately eliminate the doc-drift class this plan audits; strategic, not audit-scoped.

---

## Definition of Done (plan level)

1. Every capability claim in docs/brief.md is labeled shipped / spike-only / aspirational, and no aspirational claim is presented as shipped.
2. AGENTS.md layout matches the repository exactly.
3. All 8 session findings are landed, descoped with rationale, or ticketed with owner.
4. The pipeline runs end-to-end on the in-repo fixture with per-phase timing recorded.
5. Check output carries the full brief-promised shape: provenance chain, fix direction, contrast pair, escalation flag.
6. Prior-plan loose ends (T7, R18, S15) are closed or explicitly descoped.
7. Every pipeline gate is classified HITL-blocking or flow-through, and the pipeline stops only at HITL gates.
