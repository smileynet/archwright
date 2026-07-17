# Archwright Conventions

Applies when working on archwright methodology, archwright skills, or running archwright pipeline phases against any target project.

## Pipeline Phase Discipline

The archwright pipeline (`survey → forces → tensions → resolve → formalize → model → contract → derive → check`) is a sequence of **discrete phases with human checkpoints between them**.

**Check is continuous, not terminal:**
- After contract/derive: run `python3 tools/archwright-validate.py <specs>... && python3 tools/archwright-validate.py --links design/` (spec schema, link resolution)
- After any code change: run `python3 tools/archwright-check.py --static design/specs/` (verify constraint specs against code)
- After test suite runs: run `python3 tools/archwright-check.py --trace <spec.yaml> <trace.json>` (verify behavior specs against execution traces)
- Design audits: AI-assisted via `archwright-review` (no dedicated tool flag exists)

**Rules (ADR 0007 — gates block only where human input is needed):**
1. Each skill invocation = one phase. Produce its artifact, validate it, log it to the span digest.
2. **HITL-blocking gates** — always stop and wait for the human:
   - `resolve` (decisions; pre-resolved tensions = ONE batched confirmation, still presented)
   - Inferred product-desire validation (L4/L5) inside `forces`
   - Any ★★ event: violation found, ★★ assigned beyond what resolve ratified, or demotion proposed
   - Fog: unknown forces / unresolved tension encountered mid-span
   - End of span: present the full digest for acceptance
3. **Flow-through gates** — auto-advance WITHOUT stopping, but only when ALL hold:
   - The human pre-authorized a span (e.g., "run forces through derive"); never advance past the span boundary
   - The phase's artifacts pass `archwright-validate.py` (schema + links); validation failure = stop
   - The digest entry is written
   - No span authorized → fall back to stop-after-each-phase
4. The survey skill explicitly does NOT write patterns, specs, or resolve tensions. It produces an intake outline and dispatch queue.
5. A skill's "Does NOT" section is a hard boundary, not a suggestion.
6. "Proceed" after orientation authorizes the NEXT phase (or the span the agent proposed and the human accepted) — never "run everything silently to completion" without a digest gate at the end.

**Why:** Human checkpoints are for decisions, not ceremony. Mechanical phases are protected by validation gates + the end-of-span digest (batched review), while decision points, ★★ events, and fog still hard-block. Evidence: `.memory/audit/pipeline-dryrun.md` findings 2 and 4; full rationale in `.memory/adr/0007-hitl-only-gates.md`.

## Autonomy Within Phases and Spans

Once inside a single phase, execute sub-steps without pausing unless:
- A sub-step failed and needs user input
- A decision point not covered by the skill arises
- The action is high-risk per safety guardrails

Do not ask "shall I proceed?" between sub-steps of one phase. At phase end: if inside a pre-authorized span and the flow-through conditions hold (ADR 0007), advance; otherwise stop and present.

**"Proceed" disambiguation:** When the user says "proceed" after an orientation report or phase summary, it authorizes the NEXT SINGLE PHASE — unless the agent proposed a span (e.g., "I'll run forces through derive, then present the digest") and the human accepted it, in which case "proceed" authorizes that span. It never means "run all remaining phases" without an end-of-span digest gate.

## Target Project Artifacts

When archwright operates on a target project, it produces:
```
target-project/
  design/
    forces/            # Markdown+frontmatter, one file per force (kind: force) — root of provenance
    patterns/          # Markdown+frontmatter (tensions, resolutions; serves: links to forces)
    models/            # YAML (machine-readable) + MD (human-readable with Mermaid diagrams)
    specs/             # Behavior/contract: YAML. Constraint/dependency: Markdown+frontmatter.
```

These directories are the archwright output. The `.memory/` directory in the target project contains the project's own internal knowledge (grills, ADRs, specs-as-requirements) — archwright reads from `.memory/` and writes to `design/`.

## Pattern Quality Gates

Before committing a pattern:
- Forces section: polarity is clear, each force is one sentence, no solutions disguised as forces
- Evidence section: ≥70% of the pattern body, cited, not "it's standard practice"
- Therefore section: specific enough that two developers would implement the same architecture
- Verification section: names a mechanical check (★★), a heuristic check (★), or — for advisory patterns — states explicitly why no check exists (— is a legitimate confidence, not a missing field; vocabulary map in the deployed `archwright-survey/references/glossary.md`)

## Spec Quality Gates

Before committing a spec:
- `from_patterns` traces to at least one formalized pattern
- Constraint specs: `check` section has a runnable method (grep/semgrep/script) with correct target path
- Behavior specs: states, transitions, and invariants map to observable system behavior
- All specs pass `archwright-check --static` before commit
