# A4 — Claims Audit (Doc-Drift + Capability Claims) — archwright — 2026-07-16

Dogfood run of `archwright-audit` on archwright's own docs, extended with the capability-claims lens (**shipped** = tool does it, cited; **spike-only** = validated in .memory but not in tools; **aspirational** = docs only). Evidence base: `.memory/audit/tools.md` (A1, all tool behavior verified this session), `.memory/audit/skills.md` (A2).

## Summary
- Documents scanned: 4 (docs/brief.md, README.md, AGENTS.md, tests/fixtures/fieldball-coach/README.md) + .memory/PLAN.md (historical)
- Claims verified: 18
- Contradictions: 2 damn lies, 3 lies, 3 planned-as-current
- AGENTS.md: clean post-D1 (fixed this session, commit 41a0ebd)

## Damn Lies (wrong AND following them wastes hours)

| # | File:Line | Claim | Truth | Harm if followed | Fix |
|---|-----------|-------|-------|-----------------|-----|
| DL1 | tests/fixtures/fieldball-coach/README.md | Documents `design/` with 3 patterns + 6 specs; "Running: ./tools/run-fixture-tests.sh — All 14 checks should pass" | No `design/` dir exists in the fixture; script dies silently exit 1 (A1/F1) | Developer trusts fixture as reference implementation of the artifact layout; debugging the silent script death costs real time | **code-fix**: restore fixture design/ artifacts + repair script (new ticket B7) |
| DL2 | skills + steering (5 locations, pre-A2) | `archwright-check --structural` / `--design` invocations | Flags don't exist (A1/F8) | Agent-facing instructions that fail when followed | **FIXED** (A2, commit 0751144) |

## Lies (wrong but truth discoverable in minutes)

| # | File:Line | Claim | Truth | Fix |
|---|-----------|-------|-------|-----|
| L1 | docs/brief.md §Step 4 | `$ archwright-check ball-state-lifecycle.yaml → ✓ at-most-one-holder: PASS` | Behavior checks SKIP (exit 0) without `.references/alloy6.jar` (not in repo, path hardcoded, A1/F6); bare command not on PATH | doc-fix: show real invocation + jar prerequisite |
| L2 | .memory/PLAN.md §Three-Layer | "Tool: archwright-check --model (existing)" | No `--model` flag exists | accept (historical doc, marked COMPLETE) — annotate if touched |
| L3 | docs/brief.md §Step 5 example | Violation report shows FROM pattern→force chain + FIX DIRECTION + "★★ = must escalate" | Actual output: constraint FAIL shows `invariant + ★★` only; trace FAIL has `from_pattern` but `from_force: null`; no fix direction; no escalation flag (A1/F5) | code-fix → ticket C2 (already scoped) |

## Planned-as-Current

| # | File:Line | Described As | Actual Status | Fix |
|---|-----------|-------------|---------------|-----|
| P1 | docs/brief.md §Confidence | "Confidence can be promoted (evidence accumulates) or demoted (counterexample found)" | Methodology prose only; zero tooling, no evidence log | ticket C3 (scoped); doc: mark as methodology-not-tooling |
| P2 | docs/brief.md §Key Ideas 5 | "Contrast pairs over raw errors... the diff is the diagnosis" | Primitive exists: trace violations include `valid_events` next to the offending event (A1 verified). No side-by-side contrast rendering; constraint checks have none | ticket C1 (scoped) |
| P3 | docs/brief.md §CAN do | "Verify codebase conformance to stated rules (grep/AST checks)" | grep shipped + verified; AST path (semgrep method) declared in check.py dispatch but unexercised; no ast-grep support | ticket B4 (scoped) |

## Capability Claims Matrix

| Claim (source) | Classification | Evidence |
|----------------|:--------------:|----------|
| Constraint checks against real code, file:line output (brief §Step 4) | **SHIPPED** | A1: FAIL with path:line:content on fixture; `only-in` PASS; exit codes correct |
| Trace validation with violation position + message (brief §Step 4/5) | **SHIPPED** | A1: `--trace` JSON incl. type, position, clock, valid_events |
| Batch static checking (`--static`) | **SHIPPED** | A1 verified |
| Behavior spec → Alloy compilation | **SHIPPED** | A1: `.als` generated |
| Schema + link validation | **SHIPPED** | A1: multi-error reporting, broken-link detection |
| Skills-as-methodology, 12-skill pipeline | **SHIPPED** | deploy verified to project dir (A1) |
| Alloy counterexamples <500ms / "94ms" (README) | **SPIKE-ONLY** | `.memory/validation-spikes.md`; not reproducible in-repo (no jar) |
| "Static checks block commits" (README status) | **SPIKE-ONLY / EXTERNAL** | S13 PROVEN in FBC target repo; nothing in this repo demonstrates it |
| Contrast pair generation (README spike list) | **SPIKE-ONLY** | `valid_events` primitive shipped; rendering not (P2) |
| Full provenance routing violation→pattern→force (brief §Step 5) | **ASPIRATIONAL** | `from_force: null` in actual output; no fix direction; no escalate flag (L3) |
| Confidence promote/demote (brief) | **ASPIRATIONAL** | No tooling (P1) |
| "★★ violations escalate to human" as mechanical behavior | **ASPIRATIONAL** | Confidence rendered in output but no escalation mechanism; skills treat it as agent-behavioral rule |
| AST-based conformance checks | **ASPIRATIONAL** | P3 |

## Routing

- **HIGH:** DL1 → new ticket **B7** (restore fixture design/ + repair run-fixture-tests.sh + fix trace-validate fork or delete). This also unblocks A3 (dry run needs the fixture).
- Already-scoped tickets confirmed with evidence: C1 (P2), C2 (L3), C3 (P1), B4 (P3), B1 (scales, A1/F7).
- **Doc corrections (small batch):** brief §Step 4 invocation + jar prerequisite (L1); brief §Confidence "tooling planned" qualifier (P1); README "94ms" → "94ms in spike (S-series, 2026-06)" attribution.
- AGENTS.md needs no action (fixed in D1).

## Honest-Claims Note
brief.md §"Limitations & Honest Claims" holds up well — its CANNOT list (state explosion, model≠implementation, playtesting) matches observed tool reality. The gap is concentrated in the Step 5 correction-routing narrative and the confidence lifecycle, both presented in present tense but partially aspirational.
