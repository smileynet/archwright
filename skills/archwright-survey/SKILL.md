---
name: archwright-survey
description: "Survey a project's design state. Reads grills, ADRs, specs, and code to produce an intake outline mapping forces, tensions, patterns, and spec coverage. Dispatches specialists to fill gaps. Use when starting design work on a project, doing a full state review, or asking 'what forces exist?', 'what's not covered?', 'do a design audit'. Trigger: survey, full state review, design audit, what's covered, what's missing, intake."
metadata:
  type: protocol
  invocation: both
  practice: null
---

# Archwright Survey

The entry point for archwright. Routes to the right specialist, or maps a project's full design state and dispatches work.

## The Pipeline

```
survey → forces → tensions → resolve → formalize → model → contract → derive → check
```

## Route to the Right Skill

| You want to... | Use |
|----------------|-----|
| Full state review of a project | This skill (full mode below) |
| Audit docs for truth (contradictions, drift) | `archwright-audit` |
| Name the forces in an area | `archwright-forces` |
| Find what tensions exist | `archwright-tensions` |
| Resolve a design tension (make a decision) | `archwright-resolve` |
| Capture a decision as a pattern | `archwright-formalize` |
| Map domains, actors, state machines | `archwright-model` |
| Derive typed data contracts from the model | `archwright-contract` |
| Generate specs from a pattern + model | `archwright-derive` |
| Verify specs against implementation | `archwright-check` |
| Review code for design alignment | `archwright-review` |
| Render models/patterns as diagrams | `archwright-diagram` |

## Core Principles

- **Forces stay first-class.** Every architectural commitment traces back to a force that demanded it.
- **No pattern without a tension.** If forces don't conflict, there's nothing to resolve.
- **"Resolves into" not "compiles to."** Resolution is creative + verified, not mechanical.
- **Confidence gates autonomy.** ★★ = escalate violations. ★ = propose fix. — = auto-adjust.
- **Provenance is the routing table.** Pass-up follows the same links hands-down laid.

---

## Full Mode: Project Survey

Triggered by: "Do a full state review" / "What's covered?" / "Design audit"

### 1. Read the project

**Detect the domain FIRST.** Apply the manifest rules in `references/domains/detect.yaml` (deployed with this skill; source: `tools/domains/` in the archwright repo) — game / web / general. An explicit `domain:` in the target's `design/domain.yaml`, or the human stating it, overrides detection. Record the domain and what triggered it in the intake outline; downstream phases (forces, tensions, formalize, model) load `references/domains/<domain>/{scales,predicates}.yaml` (via `../archwright-survey/` from their own skill dirs) for vocabulary and prior art. Detection reads the architecture, not the theme — a game-themed project on an express backend is `web`.

**Detect the stack alongside the domain.** Match the target's manifests against the `detect:` globs in `references/stacks/REGISTRY.yaml` (deployed with this skill; source: `tools/stacks/REGISTRY.yaml`). Stack and domain are orthogonal axes — a TypeScript game backend is `web` domain + `typescript` stack. Record in the intake outline: the detected stack(s) and each adapter's registry status (trace_emitter / ast_grammar / check_patterns). `pending` adapters mean downstream checks of that kind will SKIP with reason — flag this as expected coverage limits, not as gaps to fix now. A stack with no registry entry at all is an Extension Protocol gap: record it pending-with-reason in the outline (what's missing, what it unblocks) per `steering/archwright-conventions.md` § Extension Protocol.

**Scope the run by size (grill Q06).** Default: full project, all areas, one pipeline run. **Large projects and monorepos** (workspace layouts like `apps/`+`packages/`, multiple deployable units, or a source corpus far beyond the subagent sizing guidance) are the exception: propose AREA PARTITION in the intake outline — per-area pipeline runs followed by an all-up **reconciliation pass** (dedupe forces across areas, surface cross-area tensions, unify models). Name the proposed areas and their run order (most invariant-dense first). Design artifacts commit to the CURRENT project branch unless the human specifies otherwise — no special design branches.

**Start with purpose.** Before reading architectural decisions, establish WHY the project exists and WHO it serves.

Product-level sources (read FIRST — these establish the generative desires):
- Project README — what the product does and who it's for
- GitHub issues (user stories, closed features, milestones) — what users want to accomplish
- Product backlog / roadmap — what's valued and prioritized
- Domain conventions (sport rules, coaching norms) — what's given by the world

Then read architectural sources:
- `design/patterns/` — existing formalized patterns
- `design/specs/` — existing checkable specs
- `.memory/grills/` — design decisions made in grill sessions
- `.memory/adr/` — binding architectural decisions
- `.memory/specs/` — internal spec system (requirements, subspecs)
- `AGENTS.md` — project conventions and structure
- `.memory/CONTEXT.md` — domain glossary

Do NOT read implementation code at this stage. Forces live in decisions, not in functions.

**Source Quality Assessment (emit this table before proceeding):** Assess the richness of what you found, so the human can predict what kind of run this will be BEFORE dispatching work.

| Source | Present? | Richness |
|--------|----------|----------|
| README / product purpose | ✓/✗ | rich / thin / absent |
| Vision or roadmap | ✓/✗ | rich / thin / absent |
| Tenets / design principles | ✓/✗ | rich / thin / absent |
| ADRs | ✓/✗ | rich (rationale + alternatives) / thin (decision only) / absent |
| Grills / decision records | ✓/✗ | rich / thin / absent |
| Feature specs / requirements | ✓/✗ | rich / thin / absent |
| Conventions (AGENTS.md, glossary) | ✓/✗ | rich / thin / absent |

**Mode prediction (state it explicitly):**
- Mostly rich → **formalization run** — forces are latent in the sources; extraction is reading, not asking. Expect few HITL stops.
- Mixed → **hybrid run** — some areas extract cleanly, others need grilling. Flag which areas fall on which side.
- Mostly thin/absent → **grilling run** — forces live in humans' heads, not documents. Expect heavy HITL; propose grill sessions before dispatching `archwright-forces`.

**At scale (>15 source files):** Dispatch subagents per area/session. See `subagent-reliability` steering for sizing and failure handling. Report coverage before proceeding:
```
## Source Coverage
- ✅ Fully read: [areas]
- ⚠️ Partial: [areas, reason]
- ❌ Not read: [areas, reason, remediation plan]
```

### 1b. Audit existing documentation (auto-triggered)

Before classifying design state, run `archwright-audit` on the project's docs to establish a baseline of known contradictions. Doc lies may surface unnamed tensions — a doc that claims X while code does Y indicates a decision was made but never propagated.

Include the audit summary in the survey output under a "Known Contradictions" section. HIGH-severity findings may block force extraction (you can't extract forces from docs that lie about the system).

### 2. Classify each area

For each capability/domain area in the project, assess:

| Question | Status |
|----------|--------|
| Are forces named? | ✓ named / ○ implicit in grills / ✗ unknown |
| Are tensions articulated? | ✓ explicit / ○ inferrable / ✗ not yet |
| Is there a resolution? | ✓ decided (grill/ADR) / ○ partial / ✗ open |
| Is it formalized as a pattern? | ✓ in design/patterns/ / ✗ missing |
| Are specs derived? | ✓ checkable specs exist / ○ partial / ✗ missing |
| Are specs verified? | ✓ checks pass / ○ checks exist but not wired / ✗ no checks |
| Is there a domain model? | ✓ in design/models/ / ✗ missing |
| Are data contracts derived? | ✓ contract specs exist / ○ partial / ✗ missing |
| Do docs match code? | ✓ audited / ○ untested / ✗ known contradictions |

### 3. Produce the intake outline

Write to `.memory/archwright-survey.md`:

```markdown
# Archwright Survey: <project-name>

## Domain
<game | web | general> — detected via <trigger> (or: overridden by <source>)

## Stack
<stack(s)> — adapter status per references/stacks/REGISTRY.yaml (trace_emitter / ast_grammar / check_patterns: ★★ / ★ / pending). Unregistered stack → Extension Protocol gap, pending-with-reason.

## Run Scope
<full-project (default) | area-partitioned: [areas, run order] + reconciliation pass> — artifacts commit to the current branch

## Destination
<what "fully covered" looks like for this project>

## Source Quality
<the assessment table from step 1 + the mode prediction (formalization / hybrid / grilling run)>

## Coverage Map
| Area | Forces | Tensions | Patterns | Specs | Status |
|------|--------|----------|----------|-------|--------|
| ... | | | | | |

## Dispatch Queue
<ordered list of specialist invocations needed>

## Already Complete
<areas with full coverage — formalized pattern + passing specs>

## Fog (cannot yet specify)
<areas where forces are unknown — need grilling before extraction>
```

### 4. Dispatch specialists

Route each gap to the appropriate specialist:

| Gap | Dispatch to | Mode |
|-----|-------------|------|
| Forces unknown | Human grill session needed first | HITL |
| Forces implicit in grills | `archwright-forces` | AFK |
| Tensions not clustered | `archwright-tensions` | AFK |
| Tension unresolved | `archwright-resolve` | HITL |
| Tension resolved but no pattern | `archwright-formalize` | AFK |
| Pattern exists but no model | `archwright-model` (ALWAYS — never skip) | AFK |
| Model exists but no data contracts | `archwright-contract` | AFK |
| Model exists but specs missing | `archwright-derive` | AFK |
| Specs exist but not verified | `archwright-check` | AFK |
| Docs may contradict code | `archwright-audit` | AFK |
| Code may violate specs | `archwright-review` | AFK |

### 5. Present the outline, propose a span, and STOP

Show the human:
1. What's already complete (celebrate coverage)
2. What can be done without them (AFK dispatch queue)
3. What needs their input (HITL items — unresolved tensions, unexplored areas, L4/L5 desires to validate)
4. Recommended order (dependency-aware — forces before tensions before patterns before specs)
5. **A proposed span** — the contiguous flow-through phases you recommend running unattended (e.g., "forces through derive"), with the HITL gates inside it called out (resolve confirmation, any expected ★★ events)

**STOP HERE** — survey always ends with this gate. If the human accepts the proposed span, run it under ADR 0007 flow-through rules: auto-advance only while `archwright-validate.py` passes each phase's artifacts, write a digest entry per phase, hard-stop at resolve / ★★ events / fog, and present the full digest at span end. If no span is accepted, run one phase per "proceed."

---

## Quick Reference

- Growth rules: see `archwright-resolve` [references/growth-rules.md]
- Context assembly: see `archwright-resolve` [references/context-assembly.md]
- Findings (stable theory): `docs/findings.md` in the archwright repo
- Glossary: `references/glossary.md` (deployed with this skill; source: `docs/glossary.md` in the archwright repo)

## Does NOT

- Write patterns (dispatch `archwright-formalize`)
- Write specs (dispatch `archwright-derive`)
- Resolve tensions (dispatch `archwright-resolve`)
- Extract forces (dispatch `archwright-forces`)
- Check specs (dispatch `archwright-check`)
- Read implementation code (forces live in decisions, not functions)
