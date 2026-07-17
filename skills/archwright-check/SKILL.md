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

4. **Route violations** — read `from_pattern` + `from_force` from violated invariant. Severity from confidence (★★=error, ★=warning, —=info). Present contrast pair if available. See `archwright-resolve` skill [references/pass-up.md](../archwright-resolve/references/pass-up.md).

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
| `semgrep` (optional) | `constraint` kind: AST checks | `pipx install semgrep` — grep fallback runs without it |

The tool locates the jar via `ARCHWRIGHT_ALLOY_JAR` env var, then `.references/alloy6.jar` relative to the tools dir, then the legacy `~/code/archwright/` path. After rehydrating, re-run the skipped specs — and in the archwright repo, `mise run test` (green = 22/0/0, behavior fixture active).

## Commands

```bash
archwright-validate <file>           # Schema validation
archwright-validate --links design/  # Link graph check
archwright-check <spec>              # Full verification
archwright-check --all design/specs/ # Check everything
```

## Does NOT Cover

- Writing patterns or specs (use `archwright-formalize` / `archwright-derive`)
- Implementation testing (use your project's test framework)
- Code review (this checks architectural properties, not style)
