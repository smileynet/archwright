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
   - `fail` with `baselined: true` (baseline active, CK-07) → known accepted debt: warning severity, doesn't gate the run. Still no evidence FOR the design — and a baselined ★★ keeps its escalate flag (see §Baseline)
   - `error` → fix the check itself, not the spec
   - `pending` (`coverage.pending`, CK-06) → `check.target_status: pending` — the target isn't built yet; the check activates when it exists. Neither pass nor fail; human output labels it `○ PENDING`
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
python3 <archwright-repo>/tools/archwright-check.py --trace <spec.yaml> <trace.json> [--json]  # Behavior vs execution trace
python3 <archwright-repo>/tools/archwright-check.py --probe <behavior-spec.yaml>      # Non-vacuity probe (false invariant must FAIL)
python3 <archwright-repo>/tools/archwright-check.py ... --baseline <file>         # Explicit baseline (else auto-discovered)
python3 <archwright-repo>/tools/archwright-check.py ... --update-baseline         # Ratchet: drop resolved entries (never adds)
```

Exit codes: 0 = pass, 1 = violations, 2 = tool error. `--json` emits the output contract (status, scope, violations w/ provenance + contrast pairs, skips w/ reasons, coverage, remaining_delta) — the payload `archwright-passup` consumes. This includes trace mode (ticket 016): `--trace ... --json` emits the same CK-03 document (trace violations route uniformly; untranslatable predicates/guards land in `skips[]`), while without `--json` trace mode keeps its bespoke replay shape (`trace-schema.ts`).

### Output fields to interpret (CK-03 document)

- **`violations[].fingerprints`** + doc-level `fingerprint_algo: aw/v1` — stable identity per evidence item (spec_id + invariant + path + normalized content; line numbers never hashed, so line shifts don't churn identity). Aligned 1:1 with `evidence[]`. These are the keys for baseline entries and for recognizing "same violation recurring across runs".
- **`coverage`** — disjoint buckets summing to `checked`: `passed / failed / skipped / errors / pending`. `pending` = specs with `check.target_status: pending` (target not built yet — CK-06); human output labels these `○ PENDING`. Neither a pass nor a fail nor evidence in either direction; reason surfaces in `skips[]`. `failed` counts raw outcomes — it can be non-zero on a passing run when everything failed is baselined.
- **`remaining_delta`** — violations AFTER baseline suppression: the number a fix loop drives to zero. No baseline active = all violations.
- **`baseline`** (present when a baseline is active) — `{path, entries, suppressed}`.

### Baseline (known-debt suppression, CK-07/CK-08)

`.archwright-baseline.json` (auto-discovered walking up from the spec dirs to the git root, or `--baseline <file>`) lets a project adopt archwright with pre-existing violations frozen as debt:

- A constraint/dependency violation whose fingerprints ALL match baseline entries is **suppressed**: `severity` drops to `warning`, `baselined: true`, and it no longer fails the run. Suppression is all-or-nothing per violation — one new match alongside baselined debt = the whole violation fails.
- **A baselined ★★ keeps `escalate: true`** — the baseline gates CI exit codes, not human routing; there is no back door around ★★-routes-to-a-human.
- **Behavior and trace violations are never suppressible** — they're design violations, not adoptable debt.
- **Entries are created by humans, never by the tool.** Copy the `fingerprints` values from `--json` output into `{"entries": [{"fingerprint": "...", "algo": "aw/v1", "note": "why this debt is accepted"}]}`. `--update-baseline` only ever REMOVES entries that no longer reproduce (refuses on errored runs and when no baseline exists).

### Debugging a behavior FAIL

When an Alloy counterexample is surprising, inspect the generated model directly: `python3 <archwright-repo>/tools/archwright-compile-alloy.py <spec.yaml>` prints the Alloy 6 source the checker ran (states, transitions, compiled guards, invariant predicates). A transition-less or guard-less model means the spec didn't compile the way you think it reads — fix the spec (or ticket the compiler gap), don't argue with the counterexample.

## Does NOT

- Write patterns or specs (use `archwright-formalize` / `archwright-derive`)
- Route or fix violations (use `archwright-passup` — this skill produces the payload, passup consumes it)
- Implementation testing (use your project's test framework)
- Code review (this checks architectural properties, not style)
