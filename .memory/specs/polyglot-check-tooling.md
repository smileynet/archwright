# Spec: Polyglot Check Tooling

**Covers:** Phase 5 (Polyglot + Agent-Native Check Tool)
**Goal:** archwright-check.py becomes a real polyglot tool that any archwright-enabled project can use: executes checks from specs, produces structured JSON (MCP-compatible + SARIF), supports baseline ratchet, works across languages (GDScript, TypeScript, Rust, Python).
**Status:** Design complete (.scratch/check-tool-design.md). Implementation not started.

**Audit reconciliation (2026-07-16, see `.memory/audit/tools.md` + `audit-plan.md`):**
- This spec **absorbs** audit-plan.md **B4** (tiered check routing + grep hardening): CK-05 (ripgrep backend), CK-11–13 (ast-grep), CK-06 (`target_status: pending`). B4's remaining delta — comment false-positive hardening for Tier 1 and erroring on unknown `expect:` values (A1/F3 silent false-pass) — is folded into CK-05's acceptance below.
- This spec **absorbs** audit-plan.md **C1** (contrast pairs → CK-10) and most of **C2** (provenance/routing → CK-09, structured output → CK-03). C2's ★★ `escalate` flag: add to CK-09.
- A1 findings that adjust tickets: current `--json` drops violations/provenance the tool already computes (CK-03 is partly re-plumbing, not greenfield); unknown `expect:` values silently pass (fix in CK-05); Alloy jar path is hardcoded to `~/code/archwright/.references/` (fix opportunistically in CK-04's error handling).
- Naming: success criterion 1 says `--structural` — today's flag is `--static`, and skills/steering were just corrected to `--static` (A2). If Phase 5 introduces `--structural` as a NEW mode (schema+links), update skills/steering/AGENTS.md in CK-17 as a breaking rename, not silently.

**CK-05 acceptance additions (from B4):** a constraint keyword appearing only in a comment does not match (comment-stripping or rg pattern guidance per language); `expect:` values outside `absent|present|only-in` are a tool error (exit 2), not a silent pass.
**CK-09 acceptance addition (from C2):** violations on ★★ specs carry `escalate: true`.

---

## Success Criteria

1. `archwright-check --structural design/` validates all spec YAML + resolves all `kind:id` links — exit 0 if valid, exit 1 if broken
2. `archwright-check --static design/specs/ --project ~/code/catalyst-mono/game/` executes grep/ast-grep checks and reports pass/fail per spec with evidence
3. Output conforms to structured JSON schema (violations carry `spec_id`, `from_pattern`, `from_force`, `suggested_route`, `contrast_pair`)
4. `--baseline design/.archwright-baseline.json` suppresses known violations; only new violations fail
5. `--output sarif` produces valid SARIF 2.1.0 consumable by GitHub Code Scanning
6. GDScript structural checks work via ast-grep with tree-sitter-gdscript grammar
7. Total check time < 2s for 30 specs (catalyst-mono scale) on static mode

---

## Research Topics

| ID | Topic | Question | Method | Blocking? |
|----|-------|----------|--------|-----------|
| R30 | ast-grep GDScript integration | Can ast-grep load tree-sitter-gdscript as custom language? What's the compilation + registration process on Windows? | Spike: compile grammar, write test pattern | Yes (Phase 5c) |
| R31 | SARIF schema compliance | What's the minimum viable SARIF output that GitHub Code Scanning accepts? Do we need `partialFingerprints`? | Read SARIF spec + test upload | No (Phase 5d) |
| R32 | Baseline fingerprinting | How should violations be fingerprinted for stable dedup across runs? (file+line is fragile; content hash?) | Study ArchUnit FreezingArchRule + semgrep fingerprint | Yes (Phase 5b) |
| R33 | MCP tool exposure | Can archwright-check be exposed as an MCP server tool for agents that support MCP? What's the effort? | Read MCP spec, build minimal server | No (future enhancement) |

---

## Spikes

| ID | Question | Method | Success | Failure | Blocking? |
|----|----------|--------|---------|---------|-----------|
| S20 | Does ast-grep parse GDScript with custom grammar on Windows? | Compile tree-sitter-gdscript.dll, register in sgconfig.yml, run pattern match | Pattern matches GDScript function declarations | Falls back to ripgrep-only (Tier 1) for GDScript | Yes (Phase 5c) |
| S21 | Does ripgrep --json give enough structure for violation reporting? | Run ripgrep --json against a catalyst-mono constraint check | JSON output includes file, line, match text — sufficient for evidence field | Need to wrap ripgrep output in post-processing | No (already known to work) |
| S22 | Can GitHub Code Scanning ingest our SARIF? | Generate minimal SARIF from one check result, upload via API | Alert appears in Security tab with correct location | Adjust schema fields until accepted | No (Phase 5d) |

---

## Tickets

### Phase 5a: Structural Validation (foundation)

| ID | Title | Description | Effort | Depends |
|----|-------|-------------|--------|---------|
| CK-01 | Spec YAML schema validation | archwright-check --structural validates all specs against spec-schema.yaml + contract template. Reports malformed specs with file+line+error. | Small | None |
| CK-02 | Link resolution check | Walk all specs, extract `kind:id` references from `links:`, `from_patterns:`, `resolves_into:`. Verify each target exists as a file in design/. Report orphan references. | Small | CK-01 |
| CK-03 | Structured JSON output contract | Define and implement the output JSON schema. All modes produce conforming output. Include `status`, `scope`, `violations[]`, `remaining_delta`, `coverage`. | Medium | CK-01 |
| CK-04 | Exit code contract | Exit 0 = pass, 1 = violations, 2 = tool error. Wire through all modes. | Trivial | CK-03 |

### Phase 5b: Static Checks + Baseline (core value)

| ID | Title | Description | Effort | Depends |
|----|-------|-------------|--------|---------|
| CK-05 | Grep backend | For each constraint spec with `check.method: grep`, invoke ripgrep with `check.pattern` against `check.target`. Map ripgrep JSON output to violations[]. Handle `expect: present` vs `expect: absent`. | Medium | CK-03 |
| CK-06 | target_status: pending handling | Specs with `check.target_status: pending` reported as coverage.pending, not as pass or fail. | Small | CK-05 |
| CK-07 | Baseline file implementation | Read `.archwright-baseline.json`. Fingerprint each violation (spec_id + normalized evidence hash). Suppress baselined violations (report as warning, not error). New violations = error. | Medium | CK-05, R32 |
| CK-08 | Baseline ratchet enforcement | On `--update-baseline`: remove entries whose violations no longer reproduce. Never add new entries automatically (human decision). Count can only decrease. | Small | CK-07 |
| CK-09 | Provenance in violation output | Each violation carries `from_pattern` and `from_force` extracted from the spec's `from_patterns:` field. Add `suggested_route` based on heuristic (grep fail on existing code = fix-implementation; missing target = fix-check). | Small | CK-05 |
| CK-10 | Contrast pair generation | For constraint violations, generate `contrast_pair: {expected, actual}` from the spec's Rule section (expected) + actual grep/ast-grep finding (actual). | Small | CK-09 |

### Phase 5c: ast-grep + GDScript (structural checks)

| ID | Title | Description | Effort | Depends |
|----|-------|-------------|--------|---------|
| CK-11 | ast-grep backend | For specs with `check.method: ast-grep`, invoke ast-grep CLI with --json. Parse output into violations[]. Support meta-variables in patterns. | Medium | CK-05, S20 |
| CK-12 | Compile tree-sitter-gdscript | Compile PrestonKnopp/tree-sitter-gdscript into .so/.dll. Document build process for Windows/Mac/Linux. Register as custom language in sgconfig.yml. | Medium | S20 |
| CK-13 | GDScript pattern library | Write 5-10 common ast-grep patterns for GDScript checks (class_name detection, signal declaration, export property, extends clause). Validate against catalyst-mono code. | Small | CK-12 |

### Phase 5d: SARIF Output (ecosystem integration)

| ID | Title | Description | Effort | Depends |
|----|-------|-------------|--------|---------|
| CK-14 | SARIF output mode | `--output sarif` produces valid SARIF 2.1.0 JSON. Map: spec → rule, violation → result, file+line → location, severity → level. | Medium | CK-03, R31 |
| CK-15 | GitHub Actions workflow | Create `.github/workflows/archwright.yml` template that runs structural + static checks on PR and uploads SARIF. Document setup for target projects. | Small | CK-14 |
| CK-16 | Fingerprinting for SARIF dedup | Generate stable `partialFingerprints` from spec_id + pattern + target region. GitHub uses these for alert dedup across commits. | Small | CK-14, R32 |

### Phase 5e: Agent Interface (skill integration)

| ID | Title | Description | Effort | Depends |
|----|-------|-------------|--------|---------|
| CK-17 | Update archwright-check skill | Rewrite skill's "Run structural checks" section to invoke the real tool. Document the full invocation contract (input args, output schema, exit codes). | Small | CK-03 |
| CK-18 | remaining_delta convergence tracking | After the skill invokes a fix → re-check cycle, track whether `remaining_delta` shrinks. If stagnant after 3 iterations, escalate to human. | Small | CK-17 |
| CK-19 | Scope selection from git diff | `archwright-check --changed-only --base origin/main` determines affected specs from git diff (changed code file → specs whose check.target overlaps). Only checks affected specs. | Medium | CK-05 |

---

## Work Order (dependency graph)

```
Phase 5a: Foundation
CK-01 ── CK-02
  │
  └── CK-03 ── CK-04
        │
        ▼
Phase 5b: Core Value
CK-05 ── CK-06
  │
  ├── CK-07 ── CK-08    (depends on R32)
  │
  └── CK-09 ── CK-10
        │
        ▼
Phase 5c: GDScript (parallel with 5d after S20)
S20 ── CK-12 ── CK-11 ── CK-13

Phase 5d: SARIF (parallel with 5c)
R31 ── CK-14 ── CK-15
         │
         └── CK-16    (depends on R32)

Phase 5e: Agent Integration (after 5b)
CK-17 ── CK-18
  │
  └── CK-19
```

### Parallel tracks after Phase 5a:
- **5b** (static + baseline) — core value, do first
- **5c** (ast-grep + GDScript) — parallel if S20 passes
- **5d** (SARIF) — parallel, independent
- **5e** (agent interface) — after 5b, needs working tool

### Critical path:
```
CK-01 → CK-03 → CK-05 → CK-07 → CK-17 → CK-19
```

---

## Technology Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Primary language | Python 3.10+ | Existing tool is Python. Rich YAML/JSON ecosystem. |
| Grep backend | ripgrep (subprocess) | Fast, cross-platform, JSON output, installed everywhere |
| AST backend | ast-grep (subprocess) | Polyglot, custom language support, JSON output, fast |
| GDScript grammar | PrestonKnopp/tree-sitter-gdscript | Production-ready, 348 commits, used by GDCode |
| Output format | Custom JSON (primary) + SARIF 2.1.0 (optional) | JSON for agent consumption, SARIF for GitHub |
| Baseline format | JSON file in design/ directory | Versionable, diffable, auto-shrinks |
| CI integration | GitHub Actions + exit codes | Universal. SARIF upload for persistent tracking. |

---

## Out of Scope (for this spec)

- Alloy integration (already exists as archwright-compile-alloy.py; behavior dispatch in archwright-check.py — note: there is NO `--model` flag; verified `.memory/audit/tools.md`)
- Trace validation (working implementation is `archwright-check.py --trace`; `archwright-trace-validate.{sh,mjs}` are BROKEN — schema fork + TS syntax, see `.memory/audit/tools.md` F2 — repair/deletion tracked as audit-plan.md B7)
- MCP server (future enhancement, tracked as R33)
- Auto-fix capabilities (tool reports, agent/human decides fix)
- Custom rule DSL (specs ARE the rules — no separate language needed)
