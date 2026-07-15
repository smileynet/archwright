---
name: archwright-audit
description: "Audit project documentation for truth — surface contradictions between docs and code, stale references, missing coverage, and terminology drift. Use when docs feel untrustworthy, when onboarding, after major refactors, or during archwright survey intake. Trigger: audit docs, reveal the lies, what's stale, doc drift, truth check, are these docs accurate."
metadata:
  type: protocol
  invocation: both
  practice: null
---

# Archwright Audit

Surface contradictions between documentation and implementation. Docs rot faster than code — this skill finds where they've diverged.

**Core principle:** Documentation that contradicts the code is worse than no documentation. A developer who trusts a lie builds the wrong thing. This skill makes the lies visible so they can be fixed.

## When to Use

- First time archwright runs on a project (initial audit during survey)
- After major refactors (code changed, docs didn't)
- When onboarding a new team member (they'll find the lies anyway — find them first)
- Periodic health check (monthly/quarterly)
- When someone says "I think our docs are wrong"

## What It Detects

| Category | Pattern | Example |
|----------|---------|---------|
| **Lies** | Docs claim X, code does Y | "GLoot addon as foundation" but no GLoot in codebase |
| **Stale references** | Docs mention things that don't exist | "CollisionTransform" in AGENTS.md but class is `CustomTransform` |
| **Missing coverage** | Code features undocumented | Object placement system exists but isn't in any doc |
| **Terminology drift** | Docs and code use different names | Doc says "ItemData", code uses "ObjectData" |
| **Architecture drift** | Diagrams don't match file structure | Player3D shown inside framework but lives in game/ |
| **Planned-as-current** | Aspirational features described as implemented | "Nested containers" documented as working but listed as deferred |

## Process

### 1. Identify documentation sources

Read the project structure and collect all documentation:
- AGENTS.md (project conventions)
- README (project overview)
- `docs/` directory (all subdirectories)
- `.memory/CONTEXT.md` (glossary)
- Framework/API docs
- Architecture diagrams
- Design documents (mechanics, scenarios)

### 2. Identify code sources

Map documentation to the code it describes:
- Framework docs → framework source files
- Architecture docs → actual directory structure
- Mechanic docs → implementing classes
- Glossary terms → class_name declarations

### 3. Extract claims from each doc

For each documentation file, identify concrete claims:
- "Class X exists" → verifiable
- "X does Y" → verifiable
- "X uses addon Z" → verifiable
- "The structure is [tree]" → verifiable against `ls`
- "Feature F is implemented" → verifiable against code

Skip subjective/aspirational content (goals, philosophy, future plans marked as such).

### 4. Verify claims against code

For each claim:

| Claim type | Verification method |
|------------|-------------------|
| Class/node exists | `grep -r "class_name X"` or check file exists |
| Method exists on class | Read the file, check method list |
| Signal exists | `grep "signal X"` in the class file |
| Data flow described | Trace the actual connection in code |
| File structure | Compare against `ls` / directory listing |
| Addon dependency | Check `project.godot` or addon directory |
| Feature status | Check if code exists vs. only design docs |

### 5. Classify findings

For each contradiction:

**Severity:**
- **HIGH** — actively misleading. A developer following this doc would make incorrect assumptions, build against a non-existent API, or misunderstand system boundaries.
- **MEDIUM** — confusing. Takes time to discover the truth. Creates friction during development.
- **LOW** — cosmetic. Outdated detail that doesn't affect decision-making.

**Fix type:**
- **doc-fix** — the code is right, update the doc
- **code-fix** — the doc describes the intended behavior, fix the code
- **both** — the intended state is neither (need a decision)
- **remove** — the doc section should be deleted (describes removed feature)

### 6. Generate fix tickets

One ticket per finding:

```markdown
### [CATEGORY]-[NUM]: Brief title

**Source:** `path/to/doc.md` line N
**Claim:** "What the doc says"
**Truth:** What the code actually does
**Evidence:** `path/to/code.gd` line M — [what it shows]
**Severity:** HIGH | MEDIUM | LOW
**Fix type:** doc-fix | code-fix | both | remove
**Proposed action:** One sentence describing the fix
**Effort:** trivial | small | medium | large
```

### 7. Produce the report

```markdown
# Doc-Drift Audit — [project] — [date]

## Summary
- Documents scanned: N
- Claims verified: M
- Contradictions found: K (X high, Y medium, Z low)

## Lies (docs claim what code doesn't do)
| # | File:Line | Claim | Truth | Severity | Fix |
|---|-----------|-------|-------|----------|-----|

## Stale References (names/paths that don't exist)
| # | File:Line | Reference | Status | Fix |
|---|-----------|-----------|--------|-----|

## Missing Coverage (code features without docs)
| # | Code Location | Feature | Impact | Fix |
|---|---------------|---------|--------|-----|

## Terminology Drift
| # | Doc Term | Code Term | Files Affected | Fix |
|---|----------|-----------|----------------|-----|

## Architecture Drift
| # | Doc Structure | Actual Structure | Impact | Fix |
|---|---------------|-----------------|--------|-----|

## Planned-as-Current
| # | File:Line | Described As | Actual Status | Fix |
|---|-----------|-------------|---------------|-----|
```

### 8. Route findings

- **HIGH severity** → immediate fix tickets (block further doc consumption)
- **MEDIUM severity** → batch into a cleanup PR
- **LOW severity** → log, fix opportunistically
- **Planned-as-current** → add "[Planned]" or "[Post-MLP]" markers to doc claims

## Subagent Dispatch (at scale)

For projects with 15+ doc files, dispatch subagents per doc group:

| Group | Scope | What to check |
|-------|-------|---------------|
| Framework docs | `docs/framework/*.md` | Claims about framework code match actual classes |
| Design docs | `docs/design/*.md` | Feature status claims match implementation plan |
| Architecture | AGENTS.md + architecture.md | Structure claims match actual directories |
| Glossary | `.memory/CONTEXT.md` | Terms match actual class_name/signal names |

Per `subagent-reliability` steering: each subagent reads specific doc files + corresponding code files. Small prompts ("read X.md, read Y.gd, find contradictions"). Synthesis (dedup, severity) done directly.

## Integration with Pipeline

| Pipeline phase | How audit integrates |
|----------------|---------------------|
| **Survey** | Run audit as part of initial project intake. Contradictions may reveal unnamed tensions. |
| **Check (periodic)** | Run audit on docs touching recently-changed code. Catch new drift. |
| **After formalize/derive** | Run audit on NEW design artifacts vs existing project docs. Do patterns contradict project documentation? |
| **Onboarding** | Run full audit. Fix HIGH findings before new developer starts. |

## Does NOT

- Check code against specs (that's `archwright-review`)
- Fix documentation (generates tickets; human decides and acts)
- Validate spec schema/links (that's `archwright-check --structural`)
- Run on every PR (too expensive; periodic or event-triggered)
- Judge documentation quality/style (only truth — is it accurate?)

## Relationship to Other Skills

```
archwright-survey  → may trigger audit during initial intake
archwright-review  → checks CODE against SPECS (alignment)
archwright-audit   → checks DOCS against CODE (truth)
archwright-check   → runs structural/behavioral verification
```

`archwright-review` asks: "Does the code honor the design?"
`archwright-audit` asks: "Do the docs describe reality?"
