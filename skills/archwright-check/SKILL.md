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
   - `skip` → coverage statement, not a pass — counts as no evidence in either direction. Report the declared reason. Skip kinds and their remedies:
     - *adapter/backend unavailable* (pending registry row, missing Alloy jar) → rehydrate or Extension Protocol
     - *untranslatable predicate* (trace mode, ticket 015: `invariants_skipped`/`guards_skipped` list which invariants/guards were NOT evaluated, with reason) → rewrite the predicate into the translatable subset (enum ==/!=, numeric comparisons, in-set, and/or/not/implies) or ticket the translator gap
     - *vacuous absence claim* (static mode, ticket 012: `expect: absent`/`only-in` scanned 0 files) → fix the target path or include glob; if the target genuinely doesn't exist yet, use `check.target_status: pending` instead
   - **Changed verdicts are unverified until independently reproduced.** A verdict that flips after a tooling or spec change (fail→pass especially), or a fix whose first verification is the tool that was just fixed, must be confirmed by an independent method (a different grep, manual inspection, a second tool) before being recorded. Field basis: a comment-stripping bug once flipped a check to a false PASS over 2 real violations — caught only by an independent grep; the rule has since caught wrong-token spec noise three times in one field run.

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

The tool locates the jar via `ARCHWRIGHT_ALLOY_JAR` env var, then `.references/alloy6.jar` relative to the tools dir, then the legacy `~/code/archwright/` path. After rehydrating, re-run the skipped specs — and in the archwright repo, `mise run test` (suite green, 0 failed, 0 skipped — current count in the repo's AGENTS.md §Commands).

## Commands

`<archwright-repo>` = the archwright checkout (skills deploy globally; the tools do not). Locate it: `ls ~/code/archwright` is the conventional path; otherwise ask the human or check `ARCHWRIGHT_ALLOY_JAR`'s parent. Inside the repo, prefer `mise run <task>` (test, validate, check-static, deploy-skills).

```bash
python3 <archwright-repo>/tools/archwright-validate.py [--json] <file>     # Schema validation
python3 <archwright-repo>/tools/archwright-validate.py [--json] --links design/  # Link graph check
python3 <archwright-repo>/tools/archwright-check.py <spec>... [--json]     # Full verification
python3 <archwright-repo>/tools/archwright-check.py --all design/specs/    # Check everything
python3 <archwright-repo>/tools/archwright-check.py --static design/specs/ [--target <root>]  # Constraint/dependency only
python3 <archwright-repo>/tools/archwright-check.py --trace <spec.yaml> <trace.json>  # Behavior vs execution trace
python3 <archwright-repo>/tools/archwright-check.py --probe <behavior-spec.yaml>      # Non-vacuity probe (false invariant must FAIL)
```

Exit codes: 0 = pass, 1 = violations, 2 = tool error. `--json` emits the output contract (status, scope, violations w/ provenance + contrast pairs, skips w/ reasons, coverage, remaining_delta) — the payload `archwright-passup` consumes.

## Does NOT

- Write patterns or specs (use `archwright-formalize` / `archwright-derive`)
- Route or fix violations (use `archwright-passup` — this skill produces the payload, passup consumes it)
- Implementation testing (use your project's test framework)
- Code review (this checks architectural properties, not style)
