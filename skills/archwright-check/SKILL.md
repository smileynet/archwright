---
name: archwright-check
description: "Verification loop for archwright specs. Checks specs against invariants, reports violations with provenance, routes corrections. Use when checking design consistency, verifying architecture, finding violations, or after implementation changes. Trigger: check specs, verify architecture, are there violations, what broke, run archwright checks."
metadata:
  type: protocol
  invocation: both
  practice: null
---

# Archwright Check

Verify specs against their stated invariants. Report violations with provenance. Route corrections to the responsible pattern.

## Process

1. **Select scope** — what to check:
   - New spec → that spec only
   - Pattern modified → all specs in its `resolves_into`
   - Code changed → specs whose `check.target` overlaps changed files
   - Full audit → all specs in `design/specs/`

2. **Run checks by kind** (consult `tools/stacks/REGISTRY.yaml` for the target's stack first — a check whose adapter is `pending` SKIPs with the registry's stated reason; it never fails and never silently passes):
   - `behavior` → compile to Alloy → bounded model check → counterexamples. Trace validation additionally needs the stack's `trace_emitter` adapter (★ or better).
   - `contract` → validate types/fields against implementation
   - `constraint` → execute `check` field from frontmatter (grep/semgrep/script). Structural (ast-grep) checks need the stack's `ast_grammar` adapter; grep fallback runs regardless.
   - `dependency` → run import/call analysis from `allowed`/`forbidden`

3. **Interpret results:**
   - `pass` → record as evidence toward confidence promotion
   - `fail` → route violation via provenance (step 4)
   - `error` → fix the check itself, not the spec
   - `skip` → adapter/backend unavailable (pending registry row, missing Alloy jar). Report the declared reason. A skip is a coverage statement, not a pass — it counts as no evidence in either direction.

4. **Hand off violations** — run with `--json` and hand the structured violations (provenance, severity, escalate flags, contrast pairs) to `archwright-passup`, which lifts each to its owning level and routes per confidence. This skill verifies; it does not route.

## Assurance Levels

Check results report what level of assurance they provide:
- `bounded` — no counterexample within scope N, K steps (Alloy). Not proof.
- `proven` — mathematically proven for all cases (Lean). Genuine ★★.
- `conformance` — codebase matches stated rule (grep/AST). As reliable as the check pattern.
- `empirical` — no violation observed in N playtests/runs. Statistical, not exhaustive.

## Checking Layers

| Layer | When | Method | Speed |
|-------|------|--------|-------|
| Quick | Design iteration | Schema + link validation | <100ms |
| Standard | Spec stable | Alloy bounded + codebase checks | <1s |
| Deep | ★★ promotion | Large scope / unbounded | seconds-minutes |
| Full | Periodic audit | All specs, all layers | project-dependent |

## Link Validation

Beyond individual specs, validate the graph:
- All `resolves_into` targets exist
- All `from_patterns` sources exist
- All `links[].target` references resolve
- No orphan specs (without parent pattern)

## Backend Prerequisites (rehydration)

Behavior checks need the Alloy jar, which is NOT in the repo (`.references/` is gitignored). Before reporting SKIPs on behavior specs, offer to rehydrate.

**With mise** (preferred — the archwright repo has a `mise.toml`): `mise install && mise run rehydrate-alloy` provisions java + the jar and sets `ARCHWRIGHT_ALLOY_JAR` automatically.

**Manual fallback:**

| Backend | Needed for | Rehydrate |
|---------|-----------|-----------|
| `alloy6.jar` (Alloy ≥ 6.2.0 — `exec` CLI added in 6.2.0) | `behavior` kind: bounded model check | `curl -L -o <archwright-repo>/.references/alloy6.jar https://github.com/AlloyTools/org.alloytools.alloy/releases/download/v6.2.0/org.alloytools.alloy.dist.jar` |
| Java (`java` on PATH) | running the jar | `winget install EclipseAdoptium.Temurin.21.JRE` / `brew install temurin` / `apt-get install default-jre` |
| `semgrep` (optional) | `constraint` kind: `method: semgrep` specs | `pipx install semgrep` — NOTE: `archwright-check.py`'s semgrep runner is a stub today; `method: semgrep` specs SKIP with "not yet implemented" regardless of the binary. Prefer `method: grep` with `include:` scoping until a spec genuinely needs AST matching (rule-of-two) |

The tool locates the jar via `ARCHWRIGHT_ALLOY_JAR` env var, then `.references/alloy6.jar` relative to the tools dir, then the legacy `~/code/archwright/` path. After rehydrating, re-run the skipped specs — and in the archwright repo, `mise run test` (green = 31/0/0, behavior fixture active).

## Commands

```bash
python3 tools/archwright-validate.py [--json] <file>     # Schema validation
python3 tools/archwright-validate.py [--json] --links design/  # Link graph check
python3 tools/archwright-check.py <spec>... [--json]     # Full verification
python3 tools/archwright-check.py --all design/specs/    # Check everything
python3 tools/archwright-check.py --static design/specs/ [--target <root>]  # Constraint/dependency only
```

Exit codes: 0 = pass, 1 = violations, 2 = tool error. `--json` emits the output contract (status, scope, violations w/ provenance + contrast pairs, coverage, remaining_delta) — the payload `archwright-passup` consumes.

## Does NOT

- Write patterns or specs (use `archwright-formalize` / `archwright-derive`)
- Route or fix violations (use `archwright-passup` — this skill produces the payload, passup consumes it)
- Implementation testing (use your project's test framework)
- Code review (this checks architectural properties, not style)
