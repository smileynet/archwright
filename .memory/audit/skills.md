# A2 — Skill Consistency Audit (2026-07-16)

Method: structured extraction from all 12 SKILL.md files + 2 steering files (3 parallel subagents, raw output in `.scratch/audit-a2/`), claims spot-verified against tool source (`.memory/audit/tools.md`), fixes applied where classification = fix-now. One subagent claim rejected on verification: `archwright-check --all` DOES exist (check.py line 624) — the check skill's usage is correct.

## Classification Legend
- **FIXED** — corrected in this session (commit refs below)
- **TICKET** — routed to audit-plan.md ticket
- **ACCEPT** — noted, no action needed

## Findings

### Nonexistent tool flags (Damn Lies — agent follows instruction, command fails)

| # | Location | Claim | Truth | Status |
|---|----------|-------|-------|--------|
| 1 | steering/archwright-conventions.md:10 | `archwright-check --structural` validates schema/links | No such flag; schema/links = `archwright-validate.py` | **FIXED** |
| 2 | steering/archwright-conventions.md:13 | `archwright-check --design` for design audits | No such flag exists | **FIXED** (routed to archwright-review) |
| 3 | skills/archwright-derive:217 | `archwright-check --structural` before commit | Flag is `--static` | **FIXED** |
| 4 | skills/archwright-audit:183 | Does-NOT: "that's `archwright-check --structural`" | `archwright-validate.py` | **FIXED** |
| 5 | skills/archwright-review (3 places) | invokes `archwright-trace-validate` | Broken tool (A1/F2); working path is `archwright-check.py --trace` | **FIXED** |

### Structural inconsistencies

| # | Finding | Severity | Status |
|---|---------|----------|--------|
| 6 | Survey "Route to the Right Skill" table listed only 7 of 12 skills — `archwright-model` is declared MANDATORY ("ALWAYS — never skip") yet was unreachable via routing; contract/audit/review/diagram also missing | HIGH | **FIXED** |
| 7 | `steering/subagent-reliability.md` claimed by AGENTS.md but absent from repo — only the deployed `~/.kiro/steering/` copy existed (source-of-truth inversion; deploy-skills syncs repo→global) | HIGH | **FIXED** (copied back; note: its `references/tool-limitations.md` link resolves only post-deploy) |
| 8 | Contract vs derive contradiction: contract groups event payloads per system (`<system>-events.yaml`); derive mandates "one spec per file — no exceptions" | MEDIUM | **TICKET** → fold into A3 dry-run observation + resolve in C-work (needs a decision, not a mechanical fix) |
| 9 | Contract-spec ownership triple-claimed: derive says "produced by contract phase, not duplicated here" but retains a full contract-derivation subsection; model Step 10 also emits contract specs | MEDIUM | **TICKET** → same decision as #8 |
| 10 | formalize not contract/model-phase-aware: says derive "creates the specs" directly from `resolves_into`; no mention of the two intermediate phases | MEDIUM | **TICKET** (A3 will confirm real impact) |
| 11 | derive requires `protects_experience` + `user_story` on ALL specs; contract's templates lack both fields | MEDIUM | **TICKET** → B2 (field flexibility) |
| 12 | formalize validation requires `serves` link but its own embedded template frontmatter has no `serves` field (repo template `tools/templates/pattern.md` HAS it) | MEDIUM | **TICKET** → B-class fix |
| 13 | Pipeline strings: 9-phase string consistent where present (survey, resolve, model, contract, conventions, AGENTS.md). No stale 7-phase string found. | — | **ACCEPT** (verified clean) |

### Vocabulary drift

| # | Finding | Severity | Status |
|---|---------|----------|--------|
| 14 | Confidence semantics fragmented: survey/resolve = escalate/propose/auto-adjust; check = error/warning/info; conventions mentions only ★★/★ (omits —); forces uses L1–L5 with no mapping to stars; review/audit use HIGH/MED/LOW | MEDIUM | **TICKET** → new: unify confidence vocabulary (glossary as anchor) |
| 15 | Resolve uses header "Does NOT Cover" vs the "Does NOT" convention AGENTS.md rule 6 depends on | LOW | **TICKET** (batch with #14) |
| 16 | Scales vocabulary appears only in formalize (game-only set) — consistent with tool hardcoding (A1/F7) | — | **ACCEPT** → already B1 scope |
| 17 | Subagent temp path: forces uses `.scratch/archwright-raw/`, steering uses `.scratch/subagent-raw/` | LOW | **TICKET** (batch) |
| 18 | audit skill verification methods are Godot-specific (`class_name`, `project.godot`, `.gd`) in a generic skill | LOW | **TICKET** → B1-adjacent (domain overlay for audit methods) |

### Internal skill defects (single-file)

| # | Finding | Status |
|---|---------|--------|
| 19 | forces: duplicate "### 4." step numbering; "Workaround Detection" (reads code hacks) contradicts own "Does NOT read implementation code" | **TICKET** (batch cleanup) |
| 20 | tensions: no output path specified for tension map; formalization enum 4 values vs table 3 | **TICKET** (batch cleanup) |
| 21 | resolve: step-3 header says "For fully-resolved tensions: Research and present options" contradicting its own routing (fully-resolved → confirm + formalize) | **TICKET** (batch cleanup) |
| 22 | model: process steps skip number 2; invokes `merman-cli`/`smcat` (absent from AGENTS.md Commands, availability unverified) | **TICKET** (batch cleanup; verify tools in A3) |
| 23 | diagram: recommends note blocks for invariants, then forbids note blocks in Rendering Hygiene; Does-NOT forbids binary images while hygiene mandates render-to-PNG | **TICKET** (batch cleanup) |
| 24 | model/contract embed LBP-specific worked examples (BallStateService, Godot) — fine as examples, but unlabeled as domain-specific | **ACCEPT** |

## Recommended new tickets for audit-plan.md

1. **B5 — Skill cleanup batch:** items 15, 17, 19–23 (one PR, ~2h).
2. **B6 — Unify confidence vocabulary:** item 14 — single definition in glossary; skills reference it (~1.5h).
3. **C7 — Contract/derive/model spec-ownership decision:** items 8–10 — who produces contract specs, and does one-per-file bend for event groups? Needs human decision (resolve-style), then edits (~2h).

Item 11 folds into existing B2. Item 18 folds into B1.

## Fixes Applied This Session
- conventions steering: real invocations for the 4 "check is continuous" bullets
- derive/audit skills: `--structural` → working commands
- review skill: 3× `archwright-trace-validate` → `archwright-check.py --trace`
- survey: routing table now lists all 12 skills
- steering/subagent-reliability.md restored to repo
