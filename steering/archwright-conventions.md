# Archwright Conventions

Applies when working on archwright methodology, archwright skills, or running archwright pipeline phases against any target project.

## Pipeline Phase Discipline

The archwright pipeline (`survey → forces → tensions → resolve → formalize → model → contract → derive → check`) is a sequence of **discrete phases with human checkpoints between them**.

**Rules:**
1. Each skill invocation = one phase. Produce its artifact, present it, STOP.
2. After presenting the phase output, ask whether to proceed to the next phase — never auto-advance.
3. "Proceed" after orientation means "run the current phase" (the one named in Next Steps[1]), not "run all phases."
4. The survey skill explicitly does NOT write patterns, specs, or resolve tensions. It produces an intake outline and dispatch queue.
5. Phases that require human input (resolve, grill) are HITL gates — they cannot be skipped even if prior decisions exist.
6. A skill's "Does NOT" section is a hard boundary, not a suggestion.

**Why:** Each phase produces an artifact the human should review before it feeds the next. Pattern quality depends on force quality. Spec quality depends on pattern quality. Skipping review compounds errors silently.

## Autonomy Within Phases

Once inside a single phase, execute sub-steps without pausing unless:
- A sub-step failed and needs user input
- A decision point not covered by the skill arises
- The action is high-risk per safety guardrails

Do not ask "shall I proceed?" between sub-steps of one phase. DO stop and present results at the end of the phase.

**"Proceed" disambiguation:** When the user says "proceed" after an orientation report or phase completion summary, it means "execute the NEXT SINGLE PHASE" — not "execute all remaining phases." If the next phase has sub-steps, those sub-steps are one unit. Multiple phases are not.

## Target Project Artifacts

When archwright operates on a target project, it produces:
```
target-project/
  design/
    patterns/          # Markdown+frontmatter (forces, tensions, resolutions)
    models/            # YAML (machine-readable) + MD (human-readable with Mermaid diagrams)
    specs/             # Behavior/contract: YAML. Constraint/dependency: Markdown+frontmatter.
```

These directories are the archwright output. The `.memory/` directory in the target project contains the project's own internal knowledge (grills, ADRs, specs-as-requirements) — archwright reads from `.memory/` and writes to `design/`.

## Pattern Quality Gates

Before committing a pattern:
- Forces section: polarity is clear, each force is one sentence, no solutions disguised as forces
- Evidence section: ≥70% of the pattern body, cited, not "it's standard practice"
- Therefore section: specific enough that two developers would implement the same architecture
- Verification section: names a mechanical check (★★) or heuristic check (★)

## Spec Quality Gates

Before committing a spec:
- `from_patterns` traces to at least one formalized pattern
- Constraint specs: `check` section has a runnable method (grep/semgrep/script) with correct target path
- Behavior specs: states, transitions, and invariants map to observable system behavior
- All specs pass `archwright-check --static` before commit
