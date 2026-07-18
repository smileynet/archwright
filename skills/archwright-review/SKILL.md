---
name: archwright-review
description: "Review implementation code for design alignment against archwright specs and models. Checks whether code honors architectural commitments made in patterns, models, and specs. Use when reviewing PRs, auditing drift, or validating that implementation matches design intent. Trigger: review code against specs, check design alignment, does this code match the architecture, design review, drift check."
metadata:
  type: protocol
  invocation: both
  practice: null
---

# Archwright Review

Review implementation for design alignment — does the code honor the architectural commitments declared in the project's specs, model, and experiences?

**Core principle:** Specs declare WHAT must be true. Code implements HOW. This skill checks that the HOW doesn't violate the WHAT. It operates at three layers: structural (deterministic, CI-able), behavioral (trace-based, CI-able with instrumentation), and semantic (AI-assisted, periodic).

## When to Use

- PR review: "Does this change violate any design specs?"
- Periodic audit: "Has the codebase drifted from its stated architecture?"
- Post-implementation: "We just built X — does it align with the model?"
- Onboarding: "Show me where the architecture is honored and where it's drifted"

## Three Checking Layers

| Layer | Method | Tool | CI-able? | What it catches |
|-------|--------|------|----------|----------------|
| **Structural** | AST pattern matching | semgrep + grep | ✅ Yes | Import violations, silent catches, mutation in observers, plaintext secrets |
| **Behavioral** | Trace validation | archwright-check.py --trace | ✅ Yes (with instrumented tests) | Wrong state transitions, skipped phases, invalid targets |
| **Semantic** | AI-assisted review | Subagent dispatch | ⚠️ Periodic (non-deterministic) | Intent drift, edge case reasoning, experience degradation |

## Process

### 1. Determine scope

What triggered this review?

| Trigger | Scope | Layers to run |
|---------|-------|---------------|
| PR/code change | `--changed-only --base <ref>` (CK-19 — mechanical: spec changed, or changed/untracked file under a `check.target`; don't eyeball path overlap) | Structural + Semantic |
| Periodic audit | All specs | All three layers |
| Specific concern | Named spec(s) | All three layers |
| New implementation | Specs from the model's relevant actors | Semantic (primary) + Structural |

### 2. Run structural checks (Layer 1)

Execute deterministic checks:

```bash
# grep/semgrep checks from constraint specs
archwright-check --static design/ --target .

# PR review: only specs the diff affects (base = the PR's merge target)
archwright-check --static design/ --target . --changed-only --base origin/main

# Semgrep rules (if design/specs/semgrep-rules.yaml exists)
semgrep --config design/specs/semgrep-rules.yaml src/
```

**Output:** Pass/fail per spec. Violations cite specific files and lines.

**Escalation:** If structural checks fail, fix before proceeding to deeper layers.

### 3. Run behavioral checks (Layer 2)

If the project has instrumented tests that emit traces:

```bash
# Run tests that produce trace files
npm test  # traces land in design/specs/traces/

# Validate each trace against its behavior spec
python3 <archwright-repo>/tools/archwright-check.py --trace design/specs/<behavior-spec>.yaml design/specs/traces/<trace>.json

# When the review will route violations through archwright-passup, add --json:
# emits the CK-03 document (severity, escalate, contrast_pair, provenance) —
# trace violations route uniformly with static ones (ticket 016)
python3 <archwright-repo>/tools/archwright-check.py --trace design/specs/<behavior-spec>.yaml design/specs/traces/<trace>.json --json
```

**Output:** Pass/fail per trace. Violations show which event violated which transition; untranslatable predicates/guards are reported as skips (coverage statements), never silent passes.

**Prerequisite:** Tests must emit trace JSON files. Instrumentation cost: ~5 lines per state machine.

### 4. Run semantic review (Layer 3)

Dispatch AI review per-spec for deeper alignment checking:

**For each constraint/behavior spec:**
1. Read the spec (frontmatter + content)
2. Identify the source files to review (from `check.target` or `source_files`)
3. Dispatch review with the protocol below

#### Review Prompt Protocol

```
You are reviewing code for DESIGN ALIGNMENT — whether the implementation
honors the architectural commitments in the project's design specs.

Spec being verified:
  [spec frontmatter YAML]

User story: [user_story field]

Invariants to check:
  [numbered list of invariants from the spec]

Source file under review: [file path]
  [source content — focused section, not entire file]

For each invariant, assess:
- ALIGNED: code actively enforces the invariant (cite the line)
- DRIFT: code has a path that could violate (cite the line, explain how)
- GAP: code doesn't address the invariant (may be handled elsewhere)

Output as YAML:
  review:
    spec: "<spec_id>"
    file: "<file_path>"
    findings:
      - invariant: "<which>"
        status: aligned | drift | gap
        location: "line N-M"
        evidence: "What the code does"
        reasoning: "Why this aligns/drifts"
        recommendation: "What to change (drift/gap only)"
        severity: error | warning | info

RULES:
- ONLY flag violations of the STATED invariants. Do not invent new rules.
- A "drift" must cite a specific code path — not hypothetical.
- Consider error paths, edge cases, and concurrent access.
```

**Output:** YAML findings per spec per file.

### 5. Compile report

Merge results from all three layers:

```markdown
# Design Alignment Report — [date]

## Summary
- Structural: X/Y specs pass
- Behavioral: N traces validated, M violations
- Semantic: P findings across Q files

## Violations

### [spec-id] — [protects_experience]
**User story:** "..."
| Layer | File | Line | Issue | Severity |
|-------|------|------|-------|----------|
| structural | src/x.ts | 42 | silent catch | error |
| semantic | src/y.ts | 108 | logs credential-bearing object | warning |

## Drift Risks (semantic findings)
...

## Coverage Gaps
- Specs without matching source files: [list]
- Actors without specs: [list]
```

### 6. Route corrections

For each violation, read `from_pattern` + `from_force`:
- **Structural violation** → fix the code (it's a bug)
- **Behavioral violation** → either code is wrong OR spec is wrong (investigate)
- **Semantic drift** → discussion item (may need spec update or code fix)

## Quality Gates

| Gate | Criterion | Action if failed |
|------|-----------|-----------------|
| Structural checks | 100% pass | Block merge / fix immediately |
| Behavioral traces | 100% pass | Investigate: code bug or spec drift |
| Semantic findings (error) | 0 error-severity drift | Discuss before merge |
| Semantic findings (warning) | Track, don't block | Log as tech debt |

## Sizing Guidance

| Project size | Structural | Behavioral | Semantic |
|-------------|-----------|------------|----------|
| < 20 specs | All, every PR | If instrumented | On-demand |
| 20-50 specs | All, every PR | If instrumented | Weekly |
| 50+ specs | `--changed-only` per PR; full sweep weekly | Critical paths | Sprint boundary |

## Tool Requirements

| Tool | Purpose | Install |
|------|---------|---------|
| `archwright-check` | Structural (grep) checks | In archwright/tools/ |
| `semgrep` | Structural (AST) checks | `pip install semgrep` or `pipx install semgrep` |
| `archwright-check.py --trace` | Behavioral trace validation | In archwright/tools/ |
| `archwright-check-compile` | Generate checks from intents | In archwright/tools/ — invocation + the six intent patterns documented in `archwright-derive` §Check Method Guidance |

## Does NOT

- Replace unit/integration tests (those test behavior, this tests alignment)
- Write or modify specs (use `archwright-derive` for that)
- Auto-fix violations (reports findings, human decides the fix)
- Run continuously (periodic or event-triggered, not a daemon)
- Block CI on semantic findings (only structural/behavioral are gateable)
- Check docs against code (that's `archwright-audit` — truth verification)

## Relationship to Other Skills

```
archwright-derive → produces specs
archwright-check  → runs structural checks (subset of Layer 1)
archwright-review → runs ALL layers, produces alignment report
```

`archwright-review` is a superset of `archwright-check --static`. It adds behavioral validation and semantic review on top.

## Anti-Patterns

- ❌ Running semantic review on every PR (too expensive, non-deterministic)
- ❌ Treating semantic findings as hard failures (they're signals, not gates)
- ❌ Reviewing files without knowing which spec they should align with (unfocused = hallucinated rules)
- ❌ Skipping structural checks because "AI will catch it" (AI is slower and less reliable for deterministic rules)
- ❌ Writing semgrep rules for things grep can check (unnecessary complexity)
