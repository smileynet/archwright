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

2. **Run checks by kind:**
   - `behavior` → compile to Alloy → bounded model check → counterexamples
   - `contract` → validate types/fields against implementation
   - `constraint` → execute `check` field from frontmatter (grep/semgrep/script)
   - `dependency` → run import/call analysis from `allowed`/`forbidden`

3. **Interpret results:**
   - `pass` → record as evidence toward confidence promotion
   - `fail` → route violation via provenance (step 4)
   - `error` → fix the check itself, not the spec

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

## Commands

```bash
python tools/install-alloy.py             # install the pinned, hash-verified Alloy runtime
archwright-validate <file>           # Schema validation
archwright-validate --links design/  # Link graph check
archwright-check <spec>              # Full verification
archwright-check --all design/specs/ # Check everything
```

## Report Generation (interim ownership — ticket 041)

After a check run, project the results into the human-facing report bundle:

```bash
python tools/archwright-check.py --static design/specs/ --target . --json > check.json
python tools/report/generate.py --check-json check.json [--design design/] [--out <dir>] [--project <name>]
```

Output: `design/report/` (gitignored) — `report.html` (interactive surface),
`REPORT.md` (mirror), `report.json` (canonical doc + `model_view`/`asks` blocks).
Exit 0 = bundle written (posture printed); exit 2 = input error OR an
untranslated vocabulary term (add the surface phrase to the token table —
never bypass). `ARCHWRIGHT_AUTO_APPROVE` (off|code-fixes|all, mise.local.toml)
collapses APPROVALS only — decisions/suggestions are structurally exempt.

**Consuming a response file** (`design/report/responses.json`, contract:response-file):
per-ask staleness — a response applies iff its ask_id exists in the LATEST run's
asks block, else drop as moot; newest `responded_at` supersedes whole-file for
the same run identity (never merge); `run.dirty: true` = advisory only.
Acknowledge every consumed-or-moot response in the next span digest.

## Evidence Staleness (commit-binding, ADR 0009 / ticket 018)

Every check `--json` document and evidence-ledger event carries `code_state: {commit, dirty}`. Staleness is judged at CONSUMPTION, by affectedness — never at append time:

- Evidence recorded at commit C is FRESH iff the spec file and its `check.target` are unchanged since C (CK-19's affectedness predicate with `--base C`)
- `dirty: true` = unverifiable for signoff-grade claims — treat as advisory
- Git absent = null fields with a reason (a coverage note, never a crash)
- Stale events are never deleted (append-only); pass streaks survive unrelated commits by design — hard EDA-style invalidation was rejected

## Does NOT Cover

- Writing patterns or specs (use `archwright-formalize` / `archwright-derive`)
- Implementation testing (use your project's test framework)
- Code review (this checks architectural properties, not style)
